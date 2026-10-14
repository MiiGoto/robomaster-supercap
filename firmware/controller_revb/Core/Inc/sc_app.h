/*
 * Rev B supercap control board application (STM32G431CBT6, STM32CubeIDE / HAL).
 *
 * main.c (CubeMX generated) only needs:
 *   USER CODE BEGIN Includes : #include "sc_app.h"
 *   USER CODE BEGIN 2        : sc_app_init();
 *   USER CODE BEGIN 3        : sc_app_loop();      (inside while(1))
 * The HAL callbacks (TIM6 1 kHz tick, FDCAN RX) are defined in sc_app.c.
 */
#ifndef SC_APP_H
#define SC_APP_H

#include <stdint.h>

#include "sc_power.h"
#include "sc_sensing.h"
#include "sc_supervisor.h"

typedef struct {
    sc_meas_t  meas;
    sc_inputs_t in;
    sc_target_t target;
    sc_state_t state;
    uint8_t    faults;
    uint8_t    last_fault;
    float      p_ramp;
    float      i_cmd;
    uint16_t   dac_code;
    uint8_t    flags;       /* SC_FLAG_* (sc_canproto.h) */
    uint32_t   tick;
} sc_telemetry_t;

void sc_app_init(void);
void sc_app_loop(void);
void sc_app_tick_1khz(void);                     /* called from the TIM6 interrupt */
void sc_app_get_telemetry(sc_telemetry_t *out);  /* for debugging (Live Expressions) */

#endif
