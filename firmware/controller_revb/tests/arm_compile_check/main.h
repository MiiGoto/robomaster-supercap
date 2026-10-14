/* Compile-check only: the pin macros CubeMX generates from the GPIO labels in SupercapRevB.ioc. */
#ifndef MAIN_H
#define MAIN_H
#include "stm32g4xx_hal.h"
void Error_Handler(void);
#define EN_CHG_Pin GPIO_PIN_0
#define EN_CHG_GPIO_Port GPIOB
#define EN_PMOS_Pin GPIO_PIN_1
#define EN_PMOS_GPIO_Port GPIOB
#define PGOOD_Pin GPIO_PIN_2
#define PGOOD_GPIO_Port GPIOB
#define NODE_OK_Pin GPIO_PIN_12
#define NODE_OK_GPIO_Port GPIOB
#define PMOS_EN_RB_Pin GPIO_PIN_13
#define PMOS_EN_RB_GPIO_Port GPIOB
#define LED1_Pin GPIO_PIN_5
#define LED1_GPIO_Port GPIOB
#define LED2_Pin GPIO_PIN_6
#define LED2_GPIO_Port GPIOB
#endif
