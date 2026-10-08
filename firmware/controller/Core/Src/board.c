#include "board.h"
#include <math.h>
#include <string.h>
ADC_HandleTypeDef hadc1, hadc2;

DMA_HandleTypeDef hdma1, hdma2;

HRTIM_HandleTypeDef hhrtim1;

FDCAN_HandleTypeDef hfdcan1;

UART_HandleTypeDef huart2;

SPI_HandleTypeDef hspi2;

IWDG_HandleTypeDef hiwdg;

volatile uint32_t pending_faults;

static uint16_t adc1_dma[96] __attribute__((aligned(4)));
static uint16_t adc2_dma[8] __attribute__((aligned(4)));
static uint32_t pwm_period;

static volatile uint16_t latest[ADC_COUNT];

static volatile uint32_t adc1_ms, adc2_ms;

static uint8_t uart_rx_byte;

static uint8_t uart_ring[128];

static volatile uint16_t uart_head, uart_tail;

typedef struct {
    uint16_t id;
    uint8_t data[8];
    uint32_t received_ms;
} can_rx_t;

static can_rx_t can_ring[16];

static volatile uint8_t can_head, can_tail;

static volatile bool outputs_started, arm_was_high, fast_enabled, session_active;
static app_t
    fast_context; /* ISR owns its PI accumulator; foreground publishes only scalar setpoint. */
static volatile float fast_duty_a, fast_duty_b;
volatile uint32_t control_isr_max_cycles;
static volatile bool uart_tx_busy;

/* Nested fault/ADC/CAN interrupts must not lose read-modify-write bits. */
static void fault_pending(uint32_t bits) {
    uint32_t key = __get_PRIMASK();
    __disable_irq();
    pending_faults |= bits;
    __set_PRIMASK(key);
}
static void check(HAL_StatusTypeDef r) {
    if (r != HAL_OK)
        Error_Handler();
}
static void gpio(GPIO_TypeDef *port, uint32_t pins, uint32_t mode, uint32_t pull, uint32_t af) {
    GPIO_InitTypeDef g = {0};
    g.Pin = pins;
    g.Mode = mode;
    g.Pull = pull;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    g.Alternate = af;
    HAL_GPIO_Init(port, &g);
}
void board_safe_gpio(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOF_CLK_ENABLE();
    /* ODR latches BEFORE output/AF mode. Hardware pull-downs cover reset/pre-C startup. */
    GPIOA->BSRR = (GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11) << 16;
    GPIOB->BSRR = (GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_10 | GPIO_PIN_11) << 16;
    GPIOC->BSRR = (GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10) << 16;
    GPIOD->BSRR = GPIO_PIN_2 << 16;
    GPIOB->BSRR = GPIO_PIN_12;
    GPIOC->BSRR = GPIO_PIN_12;
    /* CS idle;
    CAN standby */
    gpio(GPIOA, GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11, GPIO_MODE_OUTPUT_PP,
         GPIO_PULLDOWN, 0);
    gpio(GPIOB, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12,
         GPIO_MODE_OUTPUT_PP, GPIO_PULLDOWN, 0);
    gpio(GPIOC, GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_12,
         GPIO_MODE_OUTPUT_PP, GPIO_PULLDOWN, 0);
    gpio(GPIOD, GPIO_PIN_2, GPIO_MODE_OUTPUT_PP, GPIO_PULLDOWN, 0);
    gpio(GPIOC, GPIO_PIN_5 | GPIO_PIN_13, GPIO_MODE_INPUT, GPIO_PULLDOWN, 0);
    gpio(GPIOB, GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7, GPIO_MODE_INPUT, GPIO_PULLDOWN,
         0);
    gpio(GPIOA, GPIO_PIN_15, GPIO_MODE_INPUT, GPIO_PULLDOWN, 0);
    gpio(GPIOC, GPIO_PIN_11, GPIO_MODE_INPUT, GPIO_NOPULL, 0);
    /* external pull-up, active-low alert */
    gpio(GPIOA, GPIO_PIN_12, GPIO_MODE_AF_PP, GPIO_PULLDOWN, GPIO_AF13_HRTIM1);
    gpio(GPIOA, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7,
         GPIO_MODE_ANALOG, GPIO_NOPULL, 0);
    gpio(GPIOC,
         GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_4 | GPIO_PIN_14 | GPIO_PIN_15,
         GPIO_MODE_ANALOG, GPIO_NOPULL, 0);
    gpio(GPIOF, GPIO_PIN_0 | GPIO_PIN_1, GPIO_MODE_ANALOG, GPIO_NOPULL, 0);
    /* PA13/14 SWD and PB3 SWO preserved;
        PG10 must remain NRST by option bytes. */
}
static void clock_init(void) {
    RCC_OscInitTypeDef o = {0};
    RCC_ClkInitTypeDef c = {0};
    RCC_PeriphCLKInitTypeDef p = {0};
    __HAL_RCC_SYSCFG_CLK_ENABLE();
    __HAL_RCC_PWR_CLK_ENABLE();
    check(HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST));
    o.OscillatorType = RCC_OSCILLATORTYPE_HSI | RCC_OSCILLATORTYPE_LSI;
    o.HSIState = RCC_HSI_ON;
    o.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    o.LSIState = RCC_LSI_ON;
    o.PLL.PLLState = RCC_PLL_ON;
    o.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    o.PLL.PLLM = RCC_PLLM_DIV4;
    o.PLL.PLLN = 85;
    o.PLL.PLLP = RCC_PLLP_DIV2;
    o.PLL.PLLQ = RCC_PLLQ_DIV2;
    o.PLL.PLLR = RCC_PLLR_DIV2;
    check(HAL_RCC_OscConfig(&o));
    c.ClockType =
        RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    c.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    c.AHBCLKDivider = RCC_SYSCLK_DIV1;
    c.APB1CLKDivider = RCC_HCLK_DIV1;
    c.APB2CLKDivider = RCC_HCLK_DIV1;
    check(HAL_RCC_ClockConfig(&c, FLASH_LATENCY_4));
    p.PeriphClockSelection = RCC_PERIPHCLK_ADC12 | RCC_PERIPHCLK_FDCAN | RCC_PERIPHCLK_USART2;
    p.Adc12ClockSelection = RCC_ADC12CLKSOURCE_PLL;
    p.FdcanClockSelection = RCC_FDCANCLKSOURCE_PLL;
    p.Usart2ClockSelection = RCC_USART2CLKSOURCE_PCLK1;
    check(HAL_RCCEx_PeriphCLKConfig(&p));
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}
static void adc_init(ADC_HandleTypeDef *a, DMA_HandleTypeDef *d, ADC_TypeDef *instance,
                     DMA_Channel_TypeDef *dma, const uint32_t *channels, unsigned n,
                     uint32_t request) {
    unsigned i;
    static const uint32_t ranks[] = {ADC_REGULAR_RANK_1, ADC_REGULAR_RANK_2, ADC_REGULAR_RANK_3,
                                     ADC_REGULAR_RANK_4, ADC_REGULAR_RANK_5, ADC_REGULAR_RANK_6};
    ADC_ChannelConfTypeDef ch = {0};
    a->Instance = instance;
    a->Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV4;
    /* 170/4=42.5MHz */
    a->Init.Resolution = ADC_RESOLUTION_12B;
    a->Init.DataAlign = ADC_DATAALIGN_RIGHT;
    a->Init.ScanConvMode = ADC_SCAN_ENABLE;
    a->Init.EOCSelection = ADC_EOC_SEQ_CONV;
    a->Init.NbrOfConversion = n;
    a->Init.ExternalTrigConv = ADC_EXTERNALTRIG_HRTIM_TRG1;
    a->Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
    a->Init.DMAContinuousRequests = ENABLE;
    a->Init.Overrun = ADC_OVR_DATA_OVERWRITTEN;
    check(HAL_ADC_Init(a));
    for (i = 0; i < n; i++) {
        ch.Channel = channels[i];
        ch.Rank = ranks[i]; /* HAL/LL encodings are not consecutive integers. */
        ch.SamplingTime = ADC_SAMPLETIME_12CYCLES_5;
        ch.SingleDiff = ADC_SINGLE_ENDED;
        ch.OffsetNumber = ADC_OFFSET_NONE;
        check(HAL_ADC_ConfigChannel(a, &ch));
    }
    d->Instance = dma;
    d->Init.Request = request;
    d->Init.Direction = DMA_PERIPH_TO_MEMORY;
    d->Init.PeriphInc = DMA_PINC_DISABLE;
    d->Init.MemInc = DMA_MINC_ENABLE;
    d->Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    d->Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    d->Init.Mode = DMA_CIRCULAR;
    d->Init.Priority = DMA_PRIORITY_VERY_HIGH;
    check(HAL_DMA_Init(d));
    __HAL_LINKDMA(a, DMA_Handle, *d);
    check(HAL_ADCEx_Calibration_Start(a, ADC_SINGLE_ENDED));
}
static void hrtim_init(void) {
    HRTIM_TimeBaseCfgTypeDef base = {0};
    HRTIM_TimerCfgTypeDef timer = {0};
    HRTIM_OutputCfgTypeDef out = {0};
    HRTIM_CompareCfgTypeDef cmp = {0};
    HRTIM_DeadTimeCfgTypeDef dead = {0};
    HRTIM_FaultCfgTypeDef fault = {0};
    HRTIM_ADCTriggerCfgTypeDef trigger = {0};
    unsigned i;
    __HAL_RCC_HRTIM1_CLK_ENABLE();
    hhrtim1.Instance = HRTIM1;
    hhrtim1.Init.HRTIMInterruptRequests = HRTIM_IT_FLT1;
    hhrtim1.Init.SyncOptions = HRTIM_SYNCOPTION_NONE;
    check(HAL_HRTIM_Init(&hhrtim1));
    check(HAL_HRTIM_DLLCalibrationStart(&hhrtim1, HRTIM_CALIBRATIONRATE_3));
    check(HAL_HRTIM_PollForDLLCalibration(&hhrtim1, 20));
    pwm_period = (uint32_t)((uint64_t)SystemCoreClock * 32u / rev_a_config.pwm_hz);
    if (pwm_period >= 65535u || rev_a_config.adc_phase_ticks >= pwm_period ||
        rev_a_config.deadtime_ticks > 511u)
        Error_Handler();
    base.Period = pwm_period;
    base.RepetitionCounter = 0;
    base.PrescalerRatio = HRTIM_PRESCALERRATIO_MUL32;
    base.Mode = HRTIM_MODE_CONTINUOUS;
    check(HAL_HRTIM_TimeBaseConfig(&hhrtim1, HRTIM_TIMERINDEX_MASTER, &base));
    timer.PreloadEnable = HRTIM_PRELOAD_ENABLED;
    timer.UpdateGating = HRTIM_UPDATEGATING_INDEPENDENT;
    check(HAL_HRTIM_WaveformTimerConfig(&hhrtim1, HRTIM_TIMERINDEX_MASTER, &timer));
    timer.FaultEnable = HRTIM_TIMFAULTENABLE_FAULT1;
    timer.FaultLock = HRTIM_TIMFAULTLOCK_READONLY;
    timer.DeadTimeInsertion = HRTIM_TIMDEADTIMEINSERTION_ENABLED;
    timer.UpdateTrigger = HRTIM_TIMUPDATETRIGGER_MASTER;
    timer.ResetTrigger = HRTIM_TIMRESETTRIGGER_MASTER_PER;
    timer.ResetUpdate = HRTIM_TIMUPDATEONRESET_ENABLED;
    out.Polarity = HRTIM_OUTPUTPOLARITY_HIGH;
    out.IdleMode = HRTIM_OUTPUTIDLEMODE_IDLE;
    out.IdleLevel = HRTIM_OUTPUTIDLELEVEL_INACTIVE;
    out.FaultLevel = HRTIM_OUTPUTFAULTLEVEL_INACTIVE;
    out.SetSource = HRTIM_OUTPUTSET_TIMPER;
    out.ResetSource = HRTIM_OUTPUTRESET_TIMCMP1;
    dead.Prescaler = HRTIM_TIMDEADTIME_PRESCALERRATIO_DIV1;
    dead.RisingValue = rev_a_config.deadtime_ticks;
    dead.FallingValue = rev_a_config.deadtime_ticks;
    dead.RisingSign = HRTIM_TIMDEADTIME_RISINGSIGN_POSITIVE;
    dead.FallingSign = HRTIM_TIMDEADTIME_FALLINGSIGN_POSITIVE;
    for (i = 0; i < 2; i++) {
        check(HAL_HRTIM_TimeBaseConfig(&hhrtim1, i, &base));
        check(HAL_HRTIM_WaveformTimerConfig(&hhrtim1, i, &timer));
        cmp.CompareValue = 13600;
        check(HAL_HRTIM_WaveformCompareConfig(&hhrtim1, i, HRTIM_COMPAREUNIT_1, &cmp));
        check(HAL_HRTIM_DeadTimeConfig(&hhrtim1, i, &dead));
        check(HAL_HRTIM_WaveformOutputConfig(&hhrtim1, i,
                                             i == 0 ? HRTIM_OUTPUT_TA1 : HRTIM_OUTPUT_TB1, &out));
        /* Deadtime mode drives output2 from complementary output1;
               no independent set/reset. */
        out.SetSource = HRTIM_OUTPUTSET_NONE;
        out.ResetSource = HRTIM_OUTPUTRESET_NONE;
        check(HAL_HRTIM_WaveformOutputConfig(&hhrtim1, i,
                                             i == 0 ? HRTIM_OUTPUT_TA2 : HRTIM_OUTPUT_TB2, &out));
        out.SetSource = HRTIM_OUTPUTSET_TIMPER;
        out.ResetSource = HRTIM_OUTPUTRESET_TIMCMP1;
    }
    fault.Source = HRTIM_FAULTSOURCE_DIGITALINPUT;
    fault.Polarity = HRTIM_FAULTPOLARITY_LOW;
    fault.Filter = HRTIM_FAULTFILTER_NONE;
    fault.Lock = HRTIM_FAULTLOCK_READONLY;
    check(HAL_HRTIM_FaultConfig(&hhrtim1, HRTIM_FAULT_1, &fault));
    HAL_HRTIM_FaultModeCtl(&hhrtim1, HRTIM_FAULT_1, HRTIM_FAULTMODECTL_ENABLED);
    cmp.CompareValue = rev_a_config.adc_phase_ticks;
    check(HAL_HRTIM_WaveformCompareConfig(&hhrtim1, HRTIM_TIMERINDEX_MASTER, HRTIM_COMPAREUNIT_2,
                                          &cmp));
    trigger.UpdateSource = HRTIM_ADCTRIGGERUPDATE_MASTER;
    trigger.Trigger = HRTIM_ADCTRIGGEREVENT13_MASTER_CMP2;
    check(HAL_HRTIM_ADCTriggerConfig(&hhrtim1, HRTIM_ADCTRIGGER_1, &trigger));
    /* Counter/ADC triggering is allowed in monitor mode;
        output enable is not. */
    HRTIM1->sCommonRegs.ODISR =
        HRTIM_OUTPUT_TA1 | HRTIM_OUTPUT_TA2 | HRTIM_OUTPUT_TB1 | HRTIM_OUTPUT_TB2;
    HAL_NVIC_SetPriority(HRTIM1_FLT_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(HRTIM1_FLT_IRQn);
}
void board_init(void) {
    static const uint32_t ch1[] = {ADC_CHANNEL_1, ADC_CHANNEL_2, ADC_CHANNEL_6,
                                   ADC_CHANNEL_7, ADC_CHANNEL_8, ADC_CHANNEL_9};
    static const uint32_t ch2[] = {ADC_CHANNEL_3, ADC_CHANNEL_17, ADC_CHANNEL_13, ADC_CHANNEL_5};
    FDCAN_FilterTypeDef filter = {0};
    board_safe_gpio();
    check(HAL_Init());
    clock_init();
    fast_context.config = app.config;
    fast_context.calibration = app.calibration;
    __HAL_RCC_DMA1_CLK_ENABLE();
    __HAL_RCC_DMAMUX1_CLK_ENABLE();
    __HAL_RCC_ADC12_CLK_ENABLE();
    adc_init(&hadc1, &hdma1, ADC1, DMA1_Channel1, ch1, 6, DMA_REQUEST_ADC1);
    adc_init(&hadc2, &hdma2, ADC2, DMA1_Channel2, ch2, 4, DMA_REQUEST_ADC2);
    HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 3, 0);
    HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);
    HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);
    hrtim_init();
    if (FW_MODE != SAFE_MONITOR_ONLY)
        gpio(GPIOA, GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11, GPIO_MODE_AF_PP,
             GPIO_PULLDOWN, GPIO_AF13_HRTIM1);
    __HAL_RCC_SPI2_CLK_ENABLE();
    gpio(GPIOB, GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15, GPIO_MODE_AF_PP, GPIO_NOPULL,
         GPIO_AF5_SPI2);
    hspi2.Instance = SPI2;
    hspi2.Init.Mode = SPI_MODE_MASTER;
    hspi2.Init.Direction = SPI_DIRECTION_2LINES;
    hspi2.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi2.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi2.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi2.Init.NSS = SPI_NSS_SOFT;
    hspi2.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_256;
    /* 664kHz */
    hspi2.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi2.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
    check(HAL_SPI_Init(&hspi2));
    __HAL_RCC_USART2_CLK_ENABLE();
    gpio(GPIOA, GPIO_PIN_2 | GPIO_PIN_3, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART2);
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    check(HAL_UART_Init(&huart2));
    HAL_NVIC_SetPriority(USART2_IRQn, 7, 0);
    HAL_NVIC_EnableIRQ(USART2_IRQn);
    check(HAL_UART_Receive_IT(&huart2, &uart_rx_byte, 1));
    __HAL_RCC_FDCAN_CLK_ENABLE();
    gpio(GPIOB, GPIO_PIN_8 | GPIO_PIN_9, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_AF9_FDCAN1);
    hfdcan1.Instance = FDCAN1;
    hfdcan1.Init.ClockDivider = FDCAN_CLOCK_DIV1;
    hfdcan1.Init.FrameFormat = FDCAN_FRAME_CLASSIC;
    hfdcan1.Init.Mode = FDCAN_MODE_NORMAL;
    hfdcan1.Init.AutoRetransmission = ENABLE;
    hfdcan1.Init.NominalPrescaler = 17;
    hfdcan1.Init.NominalSyncJumpWidth = 2;
    hfdcan1.Init.NominalTimeSeg1 = 15;
    hfdcan1.Init.NominalTimeSeg2 = 4;
    /* 170MHz/17/20=500kbps, 80% */
    hfdcan1.Init.DataPrescaler = 17;
    hfdcan1.Init.DataSyncJumpWidth = 2;
    hfdcan1.Init.DataTimeSeg1 = 15;
    hfdcan1.Init.DataTimeSeg2 = 4;
    hfdcan1.Init.StdFiltersNbr = 1;
    hfdcan1.Init.TxFifoQueueMode = FDCAN_TX_FIFO_OPERATION;
    check(HAL_FDCAN_Init(&hfdcan1));
    filter.IdType = FDCAN_STANDARD_ID;
    filter.FilterIndex = 0;
    filter.FilterType = FDCAN_FILTER_MASK;
    filter.FilterConfig = FDCAN_FILTER_TO_RXFIFO0;
    filter.FilterID1 = 0x501;
    filter.FilterID2 = 0x7ff;
    check(HAL_FDCAN_ConfigFilter(&hfdcan1, &filter));
    check(HAL_FDCAN_ConfigGlobalFilter(&hfdcan1, FDCAN_REJECT, FDCAN_REJECT, FDCAN_REJECT_REMOTE,
                                       FDCAN_REJECT_REMOTE));
    check(HAL_FDCAN_ActivateNotification(&hfdcan1, FDCAN_IT_RX_FIFO0_NEW_MESSAGE | FDCAN_IT_BUS_OFF,
                                         0));
    HAL_NVIC_SetPriority(FDCAN1_IT0_IRQn, 6, 0);
    HAL_NVIC_EnableIRQ(FDCAN1_IT0_IRQn);
    check(HAL_FDCAN_Start(&hfdcan1));
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_12, GPIO_PIN_RESET);
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_32;
    hiwdg.Init.Reload = 999;
    hiwdg.Init.Window = IWDG_WINDOW_DISABLE;
    check(HAL_IWDG_Init(&hiwdg));
    /* ~1s at nominal32kHz;
    actual LSI variation must be reviewed. */
    check(HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc1_dma, 96));
    check(HAL_ADC_Start_DMA(&hadc2, (uint32_t *)adc2_dma, 8));
    check(HAL_HRTIM_WaveformCounterStart(&hhrtim1, HRTIM_TIMERID_MASTER | HRTIM_TIMERID_TIMER_A |
                                                       HRTIM_TIMERID_TIMER_B));
}
void board_emergency_off(void) {
    GPIOB->BSRR = (GPIO_PIN_0 | GPIO_PIN_2 | GPIO_PIN_10 | GPIO_PIN_11) << 16;
    GPIOC->BSRR = (GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10) << 16;
    if (hhrtim1.Instance)
        HRTIM1->sCommonRegs.ODISR =
            HRTIM_OUTPUT_TA1 | HRTIM_OUTPUT_TA2 | HRTIM_OUTPUT_TB1 | HRTIM_OUTPUT_TB2;
    outputs_started = false;
    arm_was_high = false;
    fast_enabled = false;
}
void board_apply_outputs(const app_t *a) {
    outputs_t o = app_safe_outputs(a);
    uint32_t key = __get_PRIMASK();
    __disable_irq();
    if (pending_faults || HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_12) == GPIO_PIN_RESET) {
        o.gate = false;
        o.arm = false;
        o.iso_bus = false;
        o.iso_cap = false;
        o.pre_bus = false;
        o.pre_cap = false;
        o.bypass_bus = false;
        o.bypass_cap = false;
        o.dump = false;
    }
    session_active = a->power_session;
    fast_context.current_reference = a->current_reference;
    fast_context.outputs.gate = o.gate;
    if (!o.gate)
        fast_context.integrator = 0;
    fast_enabled = o.gate && !pending_faults;
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_2, o.monitor_valid ? GPIO_PIN_SET : GPIO_PIN_RESET);
    if (FW_MODE == SAFE_MONITOR_ONLY) {
        board_emergency_off();
    } else {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_10, o.pre_bus ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_11, o.bypass_bus ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_6, o.iso_bus ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, o.iso_cap ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, o.pre_cap ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_9, o.bypass_cap ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_10, o.dump ? GPIO_PIN_SET : GPIO_PIN_RESET);
        if (o.gate && !outputs_started) {
            /* Balanced feedforward before first output enable; no 50%/50% step. */
            float bus = a->sensors.value[BUS_V], cap = a->sensors.value[CAP_V];
            float maxv = fmaxf(bus, cap);
            fast_context.duty_a = 0.9f * cap / maxv;
            fast_context.duty_b = 0.9f * bus / maxv;
            fast_duty_a = fast_context.duty_a;
            fast_duty_b = fast_context.duty_b;
            __HAL_HRTIM_SETCOMPARE(&hhrtim1, HRTIM_TIMERINDEX_TIMER_A, HRTIM_COMPAREUNIT_1,
                                   (uint32_t)(fast_duty_a * (float)pwm_period));
            __HAL_HRTIM_SETCOMPARE(&hhrtim1, HRTIM_TIMERINDEX_TIMER_B, HRTIM_COMPAREUNIT_1,
                                   (uint32_t)(fast_duty_b * (float)pwm_period));
            /* Preload committed together while driver request is still LOW. */
            check(HAL_HRTIM_SoftwareUpdate(&hhrtim1, HRTIM_TIMERUPDATE_A | HRTIM_TIMERUPDATE_B));
            if (HAL_HRTIM_WaveformOutputStart(&hhrtim1, HRTIM_OUTPUT_TA1 | HRTIM_OUTPUT_TA2 |
                                                            HRTIM_OUTPUT_TB1 | HRTIM_OUTPUT_TB2) !=
                HAL_OK) {
                fault_pending(HW_FAULT);
                board_emergency_off();
            } else
                outputs_started = true;
        }
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2,
                          o.gate && outputs_started ? GPIO_PIN_SET : GPIO_PIN_RESET);
        /* Rising-edge arm lasts one foreground cycle, no timer ISR can keep arming. */
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0,
                          o.arm && !arm_was_high && outputs_started ? GPIO_PIN_SET
                                                                    : GPIO_PIN_RESET);
        arm_was_high = o.arm;
        if (!o.gate) {
            GPIOB->BSRR = (GPIO_PIN_0 | GPIO_PIN_2) << 16;
            HRTIM1->sCommonRegs.ODISR =
                HRTIM_OUTPUT_TA1 | HRTIM_OUTPUT_TA2 | HRTIM_OUTPUT_TB1 | HRTIM_OUTPUT_TB2;
            outputs_started = false;
            arm_was_high = false;
        }
    }
    __set_PRIMASK(key);
}
bool board_spi_transfer(void *context, const uint8_t tx[3], uint8_t rx[3]) {
    HAL_StatusTypeDef r;
    (void)context;
    GPIOB->BSRR = GPIO_PIN_12 << 16;
    r = HAL_SPI_TransmitReceive(&hspi2, (uint8_t *)tx, rx, 3, 2);
    GPIOB->BSRR = GPIO_PIN_12;
    return r == HAL_OK;
}
void board_delay_us(void *context, uint32_t us) {
    uint32_t start = DWT->CYCCNT, ticks = us * (SystemCoreClock / 1000000u);
    (void)context;
    while (DWT->CYCCNT - start < ticks) {
        __NOP();
    }
}
void board_snapshot(sensors_t *s) {
    uint32_t key = __get_PRIMASK();
    unsigned i;
    __disable_irq();
    for (i = 0; i < ADC_COUNT; i++)
        s->raw[i] = latest[i];
    s->timestamp_ms = (int32_t)(adc1_ms - adc2_ms) < 0 ? adc1_ms : adc2_ms;
    app.duty_a = fast_duty_a;
    app.duty_b = fast_duty_b;
    __set_PRIMASK(key);
}
static void adc_frame(ADC_HandleTypeDef *a, unsigned half) {
    unsigned i;
    if (a->Instance == ADC1) {
        static const unsigned map[] = {BUS_V, CAP_V, TEMP_FET_CH, TEMP_L_CH, TEMP_BANK_CH, BUS_RAW};
        for (i = 0; i < 6; i++)
            latest[map[i]] = adc1_dma[half * 48u + 42u + i];
        adc1_ms = HAL_GetTick();
    } else {
        static const unsigned map[] = {IL_I, BUS_I, CAP_I, CAP_RAW};
        float il;
        for (i = 0; i < 4; i++)
            latest[map[i]] = adc2_dma[half * 4u + i];
        adc2_ms = HAL_GetTick();
        if (fast_enabled && FW_MODE != SAFE_MONITOR_ONLY) {
            uint32_t began = DWT->CYCCNT;
            il = ((float)latest[IL_I] * fast_context.calibration.adc_reference_v / 4095.0f +
                  fast_context.calibration.offset[IL_I]) *
                 fast_context.calibration.gain[IL_I];
            float bus = (float)latest[BUS_V] * fast_context.calibration.adc_reference_v / 4095.0f *
                        fast_context.calibration.gain[BUS_V];
            float cap = (float)latest[CAP_V] * fast_context.calibration.adc_reference_v / 4095.0f *
                        fast_context.calibration.gain[CAP_V];
            if (!isfinite(il) || fabsf(il) > fast_context.config.fast_trip_a) {
                fault_pending(HW_OC);
                board_emergency_off();
            } else {
                control_fast(&fast_context, il, bus, cap);
                fast_duty_a = fast_context.duty_a;
                fast_duty_b = fast_context.duty_b;
                __HAL_HRTIM_SETCOMPARE(&hhrtim1, HRTIM_TIMERINDEX_TIMER_A, HRTIM_COMPAREUNIT_1,
                                       (uint32_t)(fast_duty_a * (float)pwm_period));
                __HAL_HRTIM_SETCOMPARE(&hhrtim1, HRTIM_TIMERINDEX_TIMER_B, HRTIM_COMPAREUNIT_1,
                                       (uint32_t)(fast_duty_b * (float)pwm_period));
            }
            uint32_t cycles = DWT->CYCCNT - began;
            if (cycles >= SystemCoreClock / rev_a_config.pwm_hz) {
                fault_pending(CONTROL_TRACKING);
                board_emergency_off();
            }
        }
    }
}
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *a) { adc_frame(a, 0); }
void board_adc_irq_budget(uint32_t cycles) {
    if (cycles > control_isr_max_cycles)
        control_isr_max_cycles = cycles;
    if (fast_enabled && cycles >= SystemCoreClock / rev_a_config.pwm_hz) {
        fault_pending(CONTROL_TRACKING);
        board_emergency_off();
    }
}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *a) { adc_frame(a, 1); }
void HAL_ADC_ErrorCallback(ADC_HandleTypeDef *a) {
    (void)a;
    fault_pending(ADC_STALE);
    board_emergency_off();
}
void HAL_HRTIM_Fault1Callback(HRTIM_HandleTypeDef *h) {
    (void)h;
    board_emergency_off();
    /* Low is expected while monitor provisioning/referee permission are absent.
     * Hardware always inhibits;
        software latches any assertion during a power session. */
    if (session_active)
        fault_pending(HW_FAULT);
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *u) {
    uint16_t next = (uint16_t)((uart_head + 1u) % sizeof(uart_ring));
    if (u->Instance == USART2) {
        if (next != uart_tail) {
            uart_ring[uart_head] = uart_rx_byte;
            __DMB();
            uart_head = next;
        }
        (void)HAL_UART_Receive_IT(u, &uart_rx_byte, 1);
    }
}
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *u) {
    if (u->Instance == USART2)
        uart_tx_busy = false;
}
void HAL_UART_ErrorCallback(UART_HandleTypeDef *u) {
    __HAL_UART_CLEAR_OREFLAG(u);
    (void)HAL_UART_Receive_IT(u, &uart_rx_byte, 1);
}
void HAL_FDCAN_RxFifo0Callback(FDCAN_HandleTypeDef *h, uint32_t flags) {
    FDCAN_RxHeaderTypeDef r;
    uint8_t data[8], next = (uint8_t)((can_head + 1u) % 16u);
    (void)flags;
    if (HAL_FDCAN_GetRxMessage(h, FDCAN_RX_FIFO0, &r, data) == HAL_OK &&
        r.IdType == FDCAN_STANDARD_ID && r.RxFrameType == FDCAN_DATA_FRAME &&
        r.DataLength == FDCAN_DLC_BYTES_8 && r.FDFormat == FDCAN_CLASSIC_CAN) {
        if (next != can_tail) {
            can_ring[can_head].id = (uint16_t)r.Identifier;
            can_ring[can_head].received_ms = HAL_GetTick();
            memcpy(can_ring[can_head].data, data, 8);
            __DMB();
            can_head = next;
        } else {
            fault_pending(CAN_TIMEOUT);
            board_emergency_off();
        }
    }
}
void HAL_FDCAN_ErrorStatusCallback(FDCAN_HandleTypeDef *h, uint32_t flags) {
    (void)h;
    if (flags & FDCAN_IT_BUS_OFF) {
        fault_pending(CAN_TIMEOUT);
        board_emergency_off();
    }
}
void board_foreground_io(uint32_t now) {
    app.control_isr_max_cycles = control_isr_max_cycles;
    app.reserved_feedback =
        (uint8_t)((HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_SET) |
                  ((HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_15) == GPIO_PIN_SET) << 1) |
                  ((HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_4) == GPIO_PIN_SET) << 2) |
                  ((HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_5) == GPIO_PIN_SET) << 3) |
                  ((HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_6) == GPIO_PIN_SET) << 4) |
                  ((HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_7) == GPIO_PIN_SET) << 5));
    static char line[64], reply[320];
    static unsigned pos;
    static uint32_t telemetry_ms;
    static uint8_t page, seq;
    while (can_tail != can_head) {
        can_rx_t r = can_ring[can_tail];
        __DMB();
        can_tail = (uint8_t)((can_tail + 1u) % 16u);
        (void)app_can_receive_at(&app, r.id, r.data, 8, r.received_ms, now);
    }
    while (uart_tail != uart_head) {
        char c = (char)uart_ring[uart_tail];
        uart_tail = (uint16_t)((uart_tail + 1u) % sizeof(uart_ring));
        if (c == '\r' || c == '\n') {
            if (pos) {
                line[pos] = 0;
                if (!uart_tx_busy) {
                    cli_reply(&app, line, reply, sizeof(reply));
                    uart_tx_busy = true;
                    if (HAL_UART_Transmit_IT(&huart2, (uint8_t *)reply, (uint16_t)strlen(reply)) !=
                        HAL_OK)
                        uart_tx_busy = false;
                }
                pos = 0;
            }
        } else if (c >= 32 && c < 127) {
            if (pos < sizeof(line) - 1u)
                line[pos++] = c;
            else
                pos = 0;
        }
    }
    if (now - telemetry_ms >= 10u && HAL_FDCAN_GetTxFifoFreeLevel(&hfdcan1) > 0) {
        FDCAN_TxHeaderTypeDef h = {0};
        uint8_t data[8];
        h.Identifier = 0x601u + page;
        h.IdType = FDCAN_STANDARD_ID;
        h.TxFrameType = FDCAN_DATA_FRAME;
        h.DataLength = FDCAN_DLC_BYTES_8;
        h.ErrorStateIndicator = FDCAN_ESI_ACTIVE;
        h.BitRateSwitch = FDCAN_BRS_OFF;
        h.FDFormat = FDCAN_CLASSIC_CAN;
        h.TxEventFifoControl = FDCAN_NO_TX_EVENTS;
        telemetry_pack(&app, page, seq, data);
        (void)HAL_FDCAN_AddMessageToTxFifoQ(&hfdcan1, &h, data);
        page = (uint8_t)((page + 1u) % 13u);
        if (page == 0)
            seq++;
        telemetry_ms = now;
    }
}
void board_heartbeat(uint32_t now) {
    static uint32_t previous;
    if (now - previous >= 50u) {
        HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_1);
        previous = now;
    }
    check(HAL_IWDG_Refresh(&hiwdg));
}
uint32_t board_reset_cause(void) {
    uint32_t flags = RCC->CSR, result = 0;
    if (flags & RCC_CSR_BORRSTF)
        result |= 1u;
    if (flags & RCC_CSR_PINRSTF)
        result |= 2u;
    if (flags & RCC_CSR_SFTRSTF)
        result |= 4u;
    if (flags & RCC_CSR_IWDGRSTF)
        result |= 8u;
    if (flags & RCC_CSR_WWDGRSTF)
        result |= 16u;
    if (flags & RCC_CSR_LPWRRSTF)
        result |= 32u;
    __HAL_RCC_CLEAR_RESET_FLAGS();
    return result;
    /* G4 exposes BOR;
    POR not separately reliable here. */
}
void Error_Handler(void) {
    board_emergency_off();
    GPIOD->BSRR = GPIO_PIN_2 << 16;
    __disable_irq();
    for (;;) {
        __NOP();
    }
}
