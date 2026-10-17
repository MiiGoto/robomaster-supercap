/*
 * HAL glue for the Rev B supercap control board.
 * Peripheral setup comes from SupercapRevB.ioc (CubeMX). Handles used here:
 *   hadc1 (PA0 VNODE, PA1 VIN, PA2 TEMP, PA3 IIN, VREFINT; DMA circular, oversampling x16)
 *   hadc2 (PA6 ICAP; DMA circular, oversampling x16)
 *   hdac1 (PA4 ILIM_DAC, buffered)
 *   hfdcan1 (PA11 RX / PA12 TX, classic 1 Mbit/s)
 *   huart3 (PB10 TX / PB11 RX, 115200 8N1, RX DMA circular) - referee
 *   htim6 (1 kHz update interrupt)
 *   hiwdg (~200 ms)
 * GPIO labels: EN_CHG PB0, EN_PMOS PB1, PGOOD PB2, NODE_OK PB12, PMOS_EN_RB PB13, LED1 PB5, LED2 PB6.
 */
#include "sc_app.h"

#include <string.h>

#include "main.h"
#include "sc_canproto.h"
#include "sc_config.h"
#include "sc_referee.h"

extern ADC_HandleTypeDef hadc1;
extern ADC_HandleTypeDef hadc2;
extern DAC_HandleTypeDef hdac1;
extern FDCAN_HandleTypeDef hfdcan1;
extern UART_HandleTypeDef huart3;
extern TIM_HandleTypeDef htim6;
extern IWDG_HandleTypeDef hiwdg;

/* ---------------- buffers */
#define ADC1_CH     5u
#define ADC1_SCANS  8u
#define ADC2_N      16u
#define UART_RX_N   256u

static uint16_t adc1_buf[ADC1_CH * ADC1_SCANS];
static uint16_t adc2_buf[ADC2_N];
static uint8_t  uart_rx[UART_RX_N];
static uint32_t uart_rd;

/* ---------------- state */
static sc_cal_t     cal;
static sc_super_t   sup;
static sc_power_t   pwr;
static sc_referee_t ref_parser;               /* main loop only */
static sc_referee_data_t ref_shared;          /* written by the main loop with IRQs off, read by the tick */
static volatile float    can_limit_w;         /* written by the FDCAN RX interrupt */
static volatile uint32_t can_limit_ms;
static volatile uint8_t  can_have_limit;
static volatile uint32_t tick_ms;
static bool              chg_on_prev;         /* EN_CHG as driven in the previous tick */
static uint16_t vrefint_cal;
static sc_telemetry_t tel;                    /* written by the tick */

static void set_outputs(bool en_pmos, bool en_chg)
{
    HAL_GPIO_WritePin(EN_PMOS_GPIO_Port, EN_PMOS_Pin, en_pmos ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(EN_CHG_GPIO_Port, EN_CHG_Pin, en_chg ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void can_filter_start(void)
{
    FDCAN_FilterTypeDef f = {0};
    f.IdType = FDCAN_STANDARD_ID;
    f.FilterIndex = 0;
    f.FilterType = FDCAN_FILTER_MASK;
    f.FilterConfig = FDCAN_FILTER_TO_RXFIFO0;
    f.FilterID1 = SC_CAN_ID_CMD;
    f.FilterID2 = 0x7FFu;
    (void)HAL_FDCAN_ConfigFilter(&hfdcan1, &f);
    (void)HAL_FDCAN_ConfigGlobalFilter(&hfdcan1, FDCAN_REJECT, FDCAN_REJECT, FDCAN_REJECT_REMOTE, FDCAN_REJECT_REMOTE);
    (void)HAL_FDCAN_ActivateNotification(&hfdcan1, FDCAN_IT_RX_FIFO0_NEW_MESSAGE, 0);
    (void)HAL_FDCAN_Start(&hfdcan1);
}

static void can_send(uint32_t id, const uint8_t d[8])
{
    if (HAL_FDCAN_GetTxFifoFreeLevel(&hfdcan1) == 0u) {
        return;     /* bus off / no ACK: drop, never block the loop */
    }
    FDCAN_TxHeaderTypeDef h = {0};
    h.Identifier = id;
    h.IdType = FDCAN_STANDARD_ID;
    h.TxFrameType = FDCAN_DATA_FRAME;
    h.DataLength = FDCAN_DLC_BYTES_8;
    h.ErrorStateIndicator = FDCAN_ESI_ACTIVE;
    h.BitRateSwitch = FDCAN_BRS_OFF;
    h.FDFormat = FDCAN_CLASSIC_CAN;
    h.TxEventFifoControl = FDCAN_NO_TX_EVENTS;
    h.MessageMarker = 0;
    (void)HAL_FDCAN_AddMessageToTxFifoQ(&hfdcan1, &h, (uint8_t *)d);
}

void sc_app_init(void)
{
    set_outputs(false, false);
    HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LED2_GPIO_Port, LED2_Pin, GPIO_PIN_RESET);

#if SC_DEBUG_FREEZE_IWDG
    __HAL_DBGMCU_FREEZE_IWDG();
#endif
    sc_cal_default(&cal);
    sc_super_init(&sup);
    sc_power_init(&pwr);
    sc_referee_init(&ref_parser);
    memset(&ref_shared, 0, sizeof(ref_shared));
    vrefint_cal = *VREFINT_CAL_ADDR;

    /* DAC first, at the lowest current limit, before anything can enable the charger */
    (void)HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 0u);
    (void)HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);

    (void)HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);
    (void)HAL_ADCEx_Calibration_Start(&hadc2, ADC_SINGLE_ENDED);
    (void)HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc1_buf, ADC1_CH * ADC1_SCANS);
    (void)HAL_ADC_Start_DMA(&hadc2, (uint32_t *)adc2_buf, ADC2_N);

    (void)HAL_UART_Receive_DMA(&huart3, uart_rx, UART_RX_N);
    uart_rd = 0u;

    can_filter_start();
    (void)HAL_TIM_Base_Start_IT(&htim6);
}

/* ---------------- 1 kHz control tick (TIM6 interrupt) */
static void read_adc(sc_adc_raw_t *raw)
{
    uint32_t acc[ADC1_CH] = {0};
    for (uint32_t s = 0; s < ADC1_SCANS; s++) {
        for (uint32_t c = 0; c < ADC1_CH; c++) {
            acc[c] += adc1_buf[s * ADC1_CH + c];
        }
    }
    raw->vnode = (uint16_t)(acc[0] / ADC1_SCANS);
    raw->vin = (uint16_t)(acc[1] / ADC1_SCANS);
    raw->temp = (uint16_t)(acc[2] / ADC1_SCANS);
    raw->iin = (uint16_t)(acc[3] / ADC1_SCANS);
    raw->vrefint = (uint16_t)(acc[4] / ADC1_SCANS);
    uint32_t a2 = 0;
    for (uint32_t i = 0; i < ADC2_N; i++) {
        a2 += adc2_buf[i];
    }
    raw->icap = (uint16_t)(a2 / ADC2_N);
}

void sc_app_tick_1khz(void)
{
    uint32_t now = ++tick_ms;
    sc_adc_raw_t raw;
    sc_meas_t m;
    sc_inputs_t in;
    read_adc(&raw);
    sc_sensing_convert(&raw, vrefint_cal, &cal, &m);
    in.pmos_en_rb = HAL_GPIO_ReadPin(PMOS_EN_RB_GPIO_Port, PMOS_EN_RB_Pin) == GPIO_PIN_SET;
    in.node_ok = HAL_GPIO_ReadPin(NODE_OK_GPIO_Port, NODE_OK_Pin) == GPIO_PIN_SET;
    in.pgood = HAL_GPIO_ReadPin(PGOOD_GPIO_Port, PGOOD_Pin) == GPIO_PIN_SET;
    in.chg_on = chg_on_prev;

    bool can_fresh = can_have_limit && (uint32_t)(now - can_limit_ms) < SC_SRC_TIMEOUT_MS;
    sc_target_t tgt;
    sc_power_target(&ref_shared, can_fresh, can_limit_w, now, &tgt);

    sc_super_step(&sup, &m, &in, tgt.p_target, 1u);
    bool running = sc_super_running(&sup);
    sc_power_step(&pwr, &tgt, running, m.vin, m.pin, m.icap, m.vnode, m.vdda, 1u);

    (void)HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, pwr.dac_code);
    set_outputs(sup.en_pmos, sup.en_chg && pwr.gate);
    chg_on_prev = sup.en_chg && pwr.gate;

    uint8_t flags = 0u;
    flags |= (tgt.src == SC_SRC_REFEREE) ? SC_FLAG_REFEREE_OK : 0u;
    flags |= can_fresh ? SC_FLAG_CANCMD_OK : 0u;
    flags |= pwr.eoc ? SC_FLAG_EOC : 0u;
    flags |= in.pgood ? SC_FLAG_PGOOD : 0u;
    flags |= in.pmos_en_rb ? SC_FLAG_PMOS_EN : 0u;
    flags |= in.node_ok ? SC_FLAG_NODE_OK : 0u;
    flags |= (sup.en_chg && pwr.gate) ? SC_FLAG_CHG_ON : 0u;

    tel.meas = m;
    tel.in = in;
    tel.target = tgt;
    tel.state = sup.state;
    tel.faults = sup.faults;
    tel.last_fault = sup.last_fault;
    tel.p_ramp = pwr.p_ramp;
    tel.i_cmd = pwr.i_cmd;
    tel.dac_code = pwr.dac_code;
    tel.flags = flags;
    tel.tick = now;
}

void sc_app_get_telemetry(sc_telemetry_t *out)
{
    __disable_irq();
    *out = tel;
    __enable_irq();
}

/* ---------------- interrupts */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM6) {
        sc_app_tick_1khz();
    }
}

void HAL_FDCAN_RxFifo0Callback(FDCAN_HandleTypeDef *hfdcan, uint32_t RxFifo0ITs)
{
    if ((RxFifo0ITs & FDCAN_IT_RX_FIFO0_NEW_MESSAGE) == 0u) {
        return;
    }
    FDCAN_RxHeaderTypeDef h;
    uint8_t d[8];
    while (HAL_FDCAN_GetRxFifoFillLevel(hfdcan, FDCAN_RX_FIFO0) > 0u) {
        if (HAL_FDCAN_GetRxMessage(hfdcan, FDCAN_RX_FIFO0, &h, d) != HAL_OK) {
            break;
        }
        float w;
        uint8_t len = (h.DataLength <= 8u) ? (uint8_t)h.DataLength : 8u;
        if (h.IdType == FDCAN_STANDARD_ID && h.Identifier == SC_CAN_ID_CMD && sc_can_parse_cmd(d, len, &w)) {
            can_limit_w = w;
            can_limit_ms = tick_ms;
            can_have_limit = 1u;
        }
    }
}

/* ---------------- main loop */
static void referee_poll(void)
{
    uint32_t wr = UART_RX_N - __HAL_DMA_GET_COUNTER(huart3.hdmarx);
    uint32_t now = tick_ms;
    while (uart_rd != wr) {
        uint16_t cmd = sc_referee_feed(&ref_parser, uart_rx[uart_rd], now);
        uart_rd = (uart_rd + 1u) % UART_RX_N;
        if (cmd == 0x0201u || cmd == 0x0202u) {
            __disable_irq();
            ref_shared = ref_parser.data;
            __enable_irq();
        }
    }
    /* a UART error stops the DMA in HAL: restart it */
    if (huart3.RxState == HAL_UART_STATE_READY) {
        (void)HAL_UART_Receive_DMA(&huart3, uart_rx, UART_RX_N);
        uart_rd = 0u;
    }
}

static uint8_t energy_pct(float v)
{
    /* usable energy between SC_V_EMPTY and SC_V_FULL, E ~ V^2 */
    float e0 = SC_V_EMPTY * SC_V_EMPTY, e1 = SC_V_FULL * SC_V_FULL;
    float f = (v * v - e0) / (e1 - e0);
    if (f < 0.0f) {
        f = 0.0f;
    }
    if (f > 1.0f) {
        f = 1.0f;
    }
    return (uint8_t)(f * 100.0f + 0.5f);
}

static void leds(const sc_telemetry_t *t)
{
    uint32_t ms = t->tick;
    bool g = false, r = false;
    switch (t->state) {
    case SC_ST_IDLE:
        g = (ms % 1000u) < 100u;                          /* short blink: alive, not charging */
        break;
    case SC_ST_START:
    case SC_ST_CHARGE:
        g = (t->flags & SC_FLAG_EOC) ? ((ms % 250u) < 125u) : true;
        break;
    case SC_ST_FAULT: {
        /* red: blink (bit index + 1) times every 2 s */
        uint8_t n = 0u;
        for (uint8_t b = t->last_fault; b; b >>= 1) {
            n++;
        }
        uint32_t ph = ms % 2000u;
        r = (ph / 200u) < n && (ph % 200u) < 100u;
        break;
    }
    default:
        break;
    }
    HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, g ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LED2_GPIO_Port, LED2_Pin, r ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

void sc_app_loop(void)
{
    static uint32_t last_tick, t_status, t_ext;
    referee_poll();

    sc_telemetry_t t;
    sc_app_get_telemetry(&t);
    uint32_t now = t.tick;

    if ((uint32_t)(now - t_status) >= SC_TICK_HZ / SC_CAN_STATUS_HZ) {
        t_status = now;
        sc_can_status_t s = {t.meas.vin, t.meas.vnode, t.meas.iin, t.p_ramp};
        uint8_t d[8];
        sc_can_pack_status(&s, d);
        can_send(SC_CAN_ID_STATUS, d);
    }
    if ((uint32_t)(now - t_ext) >= SC_TICK_HZ / SC_CAN_EXT_HZ) {
        t_ext = now;
        sc_can_ext_t e = {(uint8_t)t.state, t.faults, t.meas.icap, t.meas.temp_c, energy_pct(t.meas.vnode), t.flags};
        uint8_t d[8];
        sc_can_pack_ext(&e, d);
        can_send(SC_CAN_ID_EXT, d);
    }
    leds(&t);

    /* watchdog: refresh only while the 1 kHz tick is running */
    if (now != last_tick) {
        last_tick = now;
        (void)HAL_IWDG_Refresh(&hiwdg);
    }
}
