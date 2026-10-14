/*
 * Compile-check only: hand-written equivalent of what CubeMX generates from SupercapRevB.ioc
 * (main.c, stm32g4xx_hal_msp.c, stm32g4xx_it.c).  It lets the application be built and linked
 * against the real ST HAL without STM32CubeIDE.  In the real project these files come from CubeMX.
 */
#include "main.h"
#include "sc_app.h"

ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;
DMA_HandleTypeDef hdma_adc1;
DMA_HandleTypeDef hdma_adc2;
DAC_HandleTypeDef hdac1;
FDCAN_HandleTypeDef hfdcan1;
IWDG_HandleTypeDef hiwdg;
TIM_HandleTypeDef htim6;
UART_HandleTypeDef huart3;
DMA_HandleTypeDef hdma_usart3_rx;

void Error_Handler(void)
{
    __disable_irq();
    while (1) {
    }
}

static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};
    HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST);
    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE | RCC_OSCILLATORTYPE_LSI;
    osc.HSEState = RCC_HSE_ON;
    osc.LSIState = RCC_LSI_ON;
    osc.PLL.PLLState = RCC_PLL_ON;
    osc.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLM = RCC_PLLM_DIV2;
    osc.PLL.PLLN = 85;
    osc.PLL.PLLP = RCC_PLLP_DIV2;
    osc.PLL.PLLQ = RCC_PLLQ_DIV2;
    osc.PLL.PLLR = RCC_PLLR_DIV2;
    if (HAL_RCC_OscConfig(&osc) != HAL_OK) {
        Error_Handler();
    }
    clk.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV1;
    clk.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_4) != HAL_OK) {
        Error_Handler();
    }
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_GPIOF_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    HAL_GPIO_WritePin(GPIOB, EN_CHG_Pin | EN_PMOS_Pin | LED1_Pin | LED2_Pin, GPIO_PIN_RESET);
    g.Pin = EN_CHG_Pin | EN_PMOS_Pin | LED1_Pin | LED2_Pin;
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &g);
    g.Pin = PGOOD_Pin | NODE_OK_Pin | PMOS_EN_RB_Pin;
    g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOB, &g);
}

static void MX_DMA_Init(void)
{
    __HAL_RCC_DMAMUX1_CLK_ENABLE();
    __HAL_RCC_DMA1_CLK_ENABLE();
    HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 3, 0);
    HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);
    HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 3, 0);
    HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);
    HAL_NVIC_SetPriority(DMA1_Channel3_IRQn, 3, 0);
    HAL_NVIC_EnableIRQ(DMA1_Channel3_IRQn);
}

static void adc_common(ADC_HandleTypeDef *h, ADC_TypeDef *inst, uint32_t n, uint32_t scan)
{
    h->Instance = inst;
    h->Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    h->Init.Resolution = ADC_RESOLUTION_12B;
    h->Init.DataAlign = ADC_DATAALIGN_RIGHT;
    h->Init.GainCompensation = 0;
    h->Init.ScanConvMode = scan;
    h->Init.EOCSelection = (n > 1u) ? ADC_EOC_SEQ_CONV : ADC_EOC_SINGLE_CONV;
    h->Init.LowPowerAutoWait = DISABLE;
    h->Init.ContinuousConvMode = ENABLE;
    h->Init.NbrOfConversion = n;
    h->Init.DiscontinuousConvMode = DISABLE;
    h->Init.ExternalTrigConv = ADC_SOFTWARE_START;
    h->Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    h->Init.DMAContinuousRequests = ENABLE;
    h->Init.Overrun = ADC_OVR_DATA_OVERWRITTEN;
    h->Init.OversamplingMode = ENABLE;
    h->Init.Oversampling.Ratio = ADC_OVERSAMPLING_RATIO_16;
    h->Init.Oversampling.RightBitShift = ADC_RIGHTBITSHIFT_4;
    h->Init.Oversampling.TriggeredMode = ADC_TRIGGEREDMODE_SINGLE_TRIGGER;
    h->Init.Oversampling.OversamplingStopReset = ADC_REGOVERSAMPLING_CONTINUED_MODE;
    if (HAL_ADC_Init(h) != HAL_OK) {
        Error_Handler();
    }
}

static void adc_ch(ADC_HandleTypeDef *h, uint32_t ch, uint32_t rank, uint32_t st)
{
    ADC_ChannelConfTypeDef c = {0};
    c.Channel = ch;
    c.Rank = rank;
    c.SamplingTime = st;
    c.SingleDiff = ADC_SINGLE_ENDED;
    c.OffsetNumber = ADC_OFFSET_NONE;
    c.Offset = 0;
    if (HAL_ADC_ConfigChannel(h, &c) != HAL_OK) {
        Error_Handler();
    }
}

static void MX_ADC1_Init(void)
{
    ADC_MultiModeTypeDef mm = {0};
    adc_common(&hadc1, ADC1, 5, ADC_SCAN_ENABLE);
    mm.Mode = ADC_MODE_INDEPENDENT;
    if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &mm) != HAL_OK) {
        Error_Handler();
    }
    adc_ch(&hadc1, ADC_CHANNEL_1, ADC_REGULAR_RANK_1, ADC_SAMPLETIME_47CYCLES_5);
    adc_ch(&hadc1, ADC_CHANNEL_2, ADC_REGULAR_RANK_2, ADC_SAMPLETIME_47CYCLES_5);
    adc_ch(&hadc1, ADC_CHANNEL_3, ADC_REGULAR_RANK_3, ADC_SAMPLETIME_47CYCLES_5);
    adc_ch(&hadc1, ADC_CHANNEL_4, ADC_REGULAR_RANK_4, ADC_SAMPLETIME_47CYCLES_5);
    adc_ch(&hadc1, ADC_CHANNEL_VREFINT, ADC_REGULAR_RANK_5, ADC_SAMPLETIME_247CYCLES_5);
}

static void MX_ADC2_Init(void)
{
    adc_common(&hadc2, ADC2, 1, ADC_SCAN_DISABLE);
    adc_ch(&hadc2, ADC_CHANNEL_3, ADC_REGULAR_RANK_1, ADC_SAMPLETIME_47CYCLES_5);
}

static void MX_DAC1_Init(void)
{
    DAC_ChannelConfTypeDef c = {0};
    hdac1.Instance = DAC1;
    if (HAL_DAC_Init(&hdac1) != HAL_OK) {
        Error_Handler();
    }
    c.DAC_HighFrequency = DAC_HIGH_FREQUENCY_INTERFACE_MODE_ABOVE_160MHZ;
    c.DAC_DMADoubleDataMode = DISABLE;
    c.DAC_SignedFormat = DISABLE;
    c.DAC_SampleAndHold = DAC_SAMPLEANDHOLD_DISABLE;
    c.DAC_Trigger = DAC_TRIGGER_NONE;
    c.DAC_Trigger2 = DAC_TRIGGER_NONE;
    c.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    c.DAC_ConnectOnChipPeripheral = DAC_CHIPCONNECT_EXTERNAL;
    c.DAC_UserTrimming = DAC_TRIMMING_FACTORY;
    if (HAL_DAC_ConfigChannel(&hdac1, &c, DAC_CHANNEL_1) != HAL_OK) {
        Error_Handler();
    }
}

static void MX_FDCAN1_Init(void)
{
    hfdcan1.Instance = FDCAN1;
    hfdcan1.Init.ClockDivider = FDCAN_CLOCK_DIV1;
    hfdcan1.Init.FrameFormat = FDCAN_FRAME_CLASSIC;
    hfdcan1.Init.Mode = FDCAN_MODE_NORMAL;
    hfdcan1.Init.AutoRetransmission = ENABLE;
    hfdcan1.Init.TransmitPause = DISABLE;
    hfdcan1.Init.ProtocolException = DISABLE;
    hfdcan1.Init.NominalPrescaler = 10;     /* 170 MHz / 10 = 17 MHz, 17 tq -> 1 Mbit/s, SP 82 % */
    hfdcan1.Init.NominalSyncJumpWidth = 3;
    hfdcan1.Init.NominalTimeSeg1 = 13;
    hfdcan1.Init.NominalTimeSeg2 = 3;
    hfdcan1.Init.DataPrescaler = 1;
    hfdcan1.Init.DataSyncJumpWidth = 1;
    hfdcan1.Init.DataTimeSeg1 = 1;
    hfdcan1.Init.DataTimeSeg2 = 1;
    hfdcan1.Init.StdFiltersNbr = 1;
    hfdcan1.Init.ExtFiltersNbr = 0;
    hfdcan1.Init.TxFifoQueueMode = FDCAN_TX_FIFO_OPERATION;
    if (HAL_FDCAN_Init(&hfdcan1) != HAL_OK) {
        Error_Handler();
    }
}

static void MX_USART3_UART_Init(void)
{
    huart3.Instance = USART3;
    huart3.Init.BaudRate = 115200;
    huart3.Init.WordLength = UART_WORDLENGTH_8B;
    huart3.Init.StopBits = UART_STOPBITS_1;
    huart3.Init.Parity = UART_PARITY_NONE;
    huart3.Init.Mode = UART_MODE_TX_RX;
    huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart3.Init.OverSampling = UART_OVERSAMPLING_16;
    huart3.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
    huart3.Init.ClockPrescaler = UART_PRESCALER_DIV1;
    huart3.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
    if (HAL_UART_Init(&huart3) != HAL_OK) {
        Error_Handler();
    }
}

static void MX_TIM6_Init(void)
{
    TIM_MasterConfigTypeDef m = {0};
    htim6.Instance = TIM6;
    htim6.Init.Prescaler = 169;
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = 999;
    htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim6) != HAL_OK) {
        Error_Handler();
    }
    m.MasterOutputTrigger = TIM_TRGO_RESET;
    m.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    (void)HAL_TIMEx_MasterConfigSynchronization(&htim6, &m);
}

static void MX_IWDG_Init(void)
{
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_32;
    hiwdg.Init.Window = 4095;
    hiwdg.Init.Reload = 200;
    if (HAL_IWDG_Init(&hiwdg) != HAL_OK) {
        Error_Handler();
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_ADC1_Init();
    MX_ADC2_Init();
    MX_DAC1_Init();
    MX_FDCAN1_Init();
    MX_USART3_UART_Init();
    MX_TIM6_Init();
    MX_IWDG_Init();
    sc_app_init();
    while (1) {
        sc_app_loop();
    }
}

/* ---------------- MSP (stm32g4xx_hal_msp.c equivalent) */
void HAL_MspInit(void)
{
    __HAL_RCC_SYSCFG_CLK_ENABLE();
    __HAL_RCC_PWR_CLK_ENABLE();
    HAL_PWREx_DisableUCPDDeadBattery();
}

static void dma_cfg(DMA_HandleTypeDef *d, DMA_Channel_TypeDef *ch, uint32_t req, uint32_t align_p, uint32_t align_m)
{
    d->Instance = ch;
    d->Init.Request = req;
    d->Init.Direction = DMA_PERIPH_TO_MEMORY;
    d->Init.PeriphInc = DMA_PINC_DISABLE;
    d->Init.MemInc = DMA_MINC_ENABLE;
    d->Init.PeriphDataAlignment = align_p;
    d->Init.MemDataAlignment = align_m;
    d->Init.Mode = DMA_CIRCULAR;
    d->Init.Priority = DMA_PRIORITY_HIGH;
    if (HAL_DMA_Init(d) != HAL_OK) {
        Error_Handler();
    }
}

void HAL_ADC_MspInit(ADC_HandleTypeDef *h)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_ADC12_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    g.Mode = GPIO_MODE_ANALOG;
    g.Pull = GPIO_NOPULL;
    if (h->Instance == ADC1) {
        g.Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3;
        HAL_GPIO_Init(GPIOA, &g);
        dma_cfg(&hdma_adc1, DMA1_Channel1, DMA_REQUEST_ADC1, DMA_PDATAALIGN_HALFWORD, DMA_MDATAALIGN_HALFWORD);
        __HAL_LINKDMA(h, DMA_Handle, hdma_adc1);
    } else if (h->Instance == ADC2) {
        g.Pin = GPIO_PIN_6;
        HAL_GPIO_Init(GPIOA, &g);
        dma_cfg(&hdma_adc2, DMA1_Channel2, DMA_REQUEST_ADC2, DMA_PDATAALIGN_HALFWORD, DMA_MDATAALIGN_HALFWORD);
        __HAL_LINKDMA(h, DMA_Handle, hdma_adc2);
    }
}

void HAL_DAC_MspInit(DAC_HandleTypeDef *h)
{
    GPIO_InitTypeDef g = {0};
    (void)h;
    __HAL_RCC_DAC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    g.Pin = GPIO_PIN_4;
    g.Mode = GPIO_MODE_ANALOG;
    g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &g);
}

void HAL_FDCAN_MspInit(FDCAN_HandleTypeDef *h)
{
    GPIO_InitTypeDef g = {0};
    RCC_PeriphCLKInitTypeDef pc = {0};
    (void)h;
    pc.PeriphClockSelection = RCC_PERIPHCLK_FDCAN;
    pc.FdcanClockSelection = RCC_FDCANCLKSOURCE_PCLK1;
    if (HAL_RCCEx_PeriphCLKConfig(&pc) != HAL_OK) {
        Error_Handler();
    }
    __HAL_RCC_FDCAN_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    g.Pin = GPIO_PIN_11 | GPIO_PIN_12;
    g.Mode = GPIO_MODE_AF_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    g.Alternate = GPIO_AF9_FDCAN1;
    HAL_GPIO_Init(GPIOA, &g);
    HAL_NVIC_SetPriority(FDCAN1_IT0_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(FDCAN1_IT0_IRQn);
}

void HAL_UART_MspInit(UART_HandleTypeDef *h)
{
    GPIO_InitTypeDef g = {0};
    RCC_PeriphCLKInitTypeDef pc = {0};
    pc.PeriphClockSelection = RCC_PERIPHCLK_USART3;
    pc.Usart3ClockSelection = RCC_USART3CLKSOURCE_PCLK1;
    if (HAL_RCCEx_PeriphCLKConfig(&pc) != HAL_OK) {
        Error_Handler();
    }
    __HAL_RCC_USART3_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    g.Pin = GPIO_PIN_10 | GPIO_PIN_11;
    g.Mode = GPIO_MODE_AF_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    g.Alternate = GPIO_AF7_USART3;
    HAL_GPIO_Init(GPIOB, &g);
    dma_cfg(&hdma_usart3_rx, DMA1_Channel3, DMA_REQUEST_USART3_RX, DMA_PDATAALIGN_BYTE, DMA_MDATAALIGN_BYTE);
    __HAL_LINKDMA(h, hdmarx, hdma_usart3_rx);
    HAL_NVIC_SetPriority(USART3_IRQn, 3, 0);
    HAL_NVIC_EnableIRQ(USART3_IRQn);
}

void HAL_TIM_Base_MspInit(TIM_HandleTypeDef *h)
{
    if (h->Instance == TIM6) {
        __HAL_RCC_TIM6_CLK_ENABLE();
        HAL_NVIC_SetPriority(TIM6_DAC_IRQn, 1, 0);
        HAL_NVIC_EnableIRQ(TIM6_DAC_IRQn);
    }
}

/* ---------------- interrupt handlers (stm32g4xx_it.c equivalent) */
void SysTick_Handler(void) { HAL_IncTick(); }
void DMA1_Channel1_IRQHandler(void) { HAL_DMA_IRQHandler(&hdma_adc1); }
void DMA1_Channel2_IRQHandler(void) { HAL_DMA_IRQHandler(&hdma_adc2); }
void DMA1_Channel3_IRQHandler(void) { HAL_DMA_IRQHandler(&hdma_usart3_rx); }
void FDCAN1_IT0_IRQHandler(void) { HAL_FDCAN_IRQHandler(&hfdcan1); }
void USART3_IRQHandler(void) { HAL_UART_IRQHandler(&huart3); }
void TIM6_DAC_IRQHandler(void)
{
    HAL_DAC_IRQHandler(&hdac1);
    HAL_TIM_IRQHandler(&htim6);
}
void HardFault_Handler(void) { while (1) { } }
