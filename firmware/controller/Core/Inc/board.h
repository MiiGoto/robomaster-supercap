#ifndef BOARD_H
#define BOARD_H
#include "bq76942.h"
#include "rev_a.h"
#include "stm32g4xx_hal.h"
extern ADC_HandleTypeDef hadc1, hadc2;
extern DMA_HandleTypeDef hdma1, hdma2;
extern HRTIM_HandleTypeDef hhrtim1;
extern FDCAN_HandleTypeDef hfdcan1;
extern UART_HandleTypeDef huart2;
extern SPI_HandleTypeDef hspi2;
extern IWDG_HandleTypeDef hiwdg;
extern app_t app;
extern volatile uint32_t pending_faults;
void board_safe_gpio(void);
void board_init(void);
void board_apply_outputs(const app_t *a);
void board_emergency_off(void);
bool board_spi_transfer(void *context, const uint8_t tx[3], uint8_t rx[3]);
void board_delay_us(void *context, uint32_t us);
void board_snapshot(sensors_t *s);
void board_foreground_io(uint32_t now);
void board_heartbeat(uint32_t now);
void board_adc_irq_budget(uint32_t cycles);
uint32_t board_reset_cause(void);
void Error_Handler(void);
#endif
