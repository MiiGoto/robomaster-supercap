/* Compile-check only: project-authored HAL configuration matching SupercapRevB.ioc.
 * In STM32CubeIDE, CubeMX generates its own Core/Inc/stm32g4xx_hal_conf.h. */
#ifndef STM32G4xx_HAL_CONF_H
#define STM32G4xx_HAL_CONF_H
#define HAL_MODULE_ENABLED
#define HAL_ADC_MODULE_ENABLED
#define HAL_CORTEX_MODULE_ENABLED
#define HAL_DAC_MODULE_ENABLED
#define HAL_DMA_MODULE_ENABLED
#define HAL_EXTI_MODULE_ENABLED
#define HAL_FDCAN_MODULE_ENABLED
#define HAL_FLASH_MODULE_ENABLED
#define HAL_GPIO_MODULE_ENABLED
#define HAL_IWDG_MODULE_ENABLED
#define HAL_PWR_MODULE_ENABLED
#define HAL_RCC_MODULE_ENABLED
#define HAL_TIM_MODULE_ENABLED
#define HAL_UART_MODULE_ENABLED
#define HSE_VALUE 8000000u
#define HSE_STARTUP_TIMEOUT 100u
#define HSI_VALUE 16000000u
#define HSI48_VALUE 48000000u
#define LSI_VALUE 32000u
#define LSE_VALUE 32768u
#define LSE_STARTUP_TIMEOUT 5000u
#define EXTERNAL_CLOCK_VALUE 12288000u
#define VDD_VALUE 3300u
#define TICK_INT_PRIORITY 15u
#define USE_RTOS 0u
#define PREFETCH_ENABLE 0u
#define INSTRUCTION_CACHE_ENABLE 1u
#define DATA_CACHE_ENABLE 1u
#define USE_HAL_ADC_REGISTER_CALLBACKS 0u
#define USE_HAL_DAC_REGISTER_CALLBACKS 0u
#define USE_HAL_FDCAN_REGISTER_CALLBACKS 0u
#define USE_HAL_TIM_REGISTER_CALLBACKS 0u
#define USE_HAL_UART_REGISTER_CALLBACKS 0u
#define assert_param(expr) ((void)0u)
#include "stm32g4xx_hal_rcc.h"
#include "stm32g4xx_hal_gpio.h"
#include "stm32g4xx_hal_dma.h"
#include "stm32g4xx_hal_adc.h"
#include "stm32g4xx_hal_cortex.h"
#include "stm32g4xx_hal_dac.h"
#include "stm32g4xx_hal_exti.h"
#include "stm32g4xx_hal_fdcan.h"
#include "stm32g4xx_hal_flash.h"
#include "stm32g4xx_hal_iwdg.h"
#include "stm32g4xx_hal_pwr.h"
#include "stm32g4xx_hal_tim.h"
#include "stm32g4xx_hal_uart.h"
#endif
