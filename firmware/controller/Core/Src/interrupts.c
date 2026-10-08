#include "board.h"
void SysTick_Handler(void) { HAL_IncTick(); }
void DMA1_Channel1_IRQHandler(void) { HAL_DMA_IRQHandler(&hdma1); }
void DMA1_Channel2_IRQHandler(void) {
    uint32_t started = DWT->CYCCNT;
    HAL_DMA_IRQHandler(&hdma2);
    board_adc_irq_budget(DWT->CYCCNT - started);
}
void HRTIM1_FLT_IRQHandler(void) { HAL_HRTIM_IRQHandler(&hhrtim1, HRTIM_TIMERINDEX_COMMON); }
void USART2_IRQHandler(void) { HAL_UART_IRQHandler(&huart2); }
void FDCAN1_IT0_IRQHandler(void) { HAL_FDCAN_IRQHandler(&hfdcan1); }
void NMI_Handler(void) { Error_Handler(); }
void HardFault_Handler(void) { Error_Handler(); }
void MemManage_Handler(void) { Error_Handler(); }
void BusFault_Handler(void) { Error_Handler(); }
void UsageFault_Handler(void) { Error_Handler(); }
