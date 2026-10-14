/*
 * Input power limiting.
 *
 * The LM5176 limits its average input current at ISNS = 50 mV (R4 12 mOhm -> 4.17 A).
 * The MCU lowers that limit by sinking an offset current through R5 (DAC -> Q3), see
 * sheet 1 "ISNS offset".  The power target comes from the referee chassis power limit
 * and buffer energy (UART), or from the robot over CAN 0x210, or a safe default.
 *
 * Two gates can switch EN_CHG on/off inside a 100 ms period:
 *  - low power: the DAC can only lower the limit to ~1.2 A; below that the on-time is scaled.
 *  - end of charge: above SC_V_EOC the bank charge current is held at SC_I_EOC_A on average,
 *    because the per-cell clamps on the bank board can bypass only ~0.6 A.
 */
#ifndef SC_POWER_H
#define SC_POWER_H

#include <stdbool.h>
#include <stdint.h>

#include "sc_referee.h"

typedef enum { SC_SRC_DEFAULT = 0, SC_SRC_REFEREE = 1, SC_SRC_CAN = 2 } sc_src_t;

typedef struct {
    float    p_target;      /* W, before ramp */
    sc_src_t src;
    bool     chassis_off;   /* referee says the PM chassis port is off */
} sc_target_t;

typedef struct {
    float    p_ramp;        /* W, ramped target actually commanded */
    float    trim_a;        /* integral trim on the current limit */
    float    i_cmd;         /* A, commanded input current limit */
    float    i_min_hw;      /* A, lowest limit the DAC can reach (depends on VDDA) */
    float    dac_v;         /* V at PA4 */
    uint16_t dac_code;
    /* gate */
    uint32_t phase_ms;
    uint32_t ton_eoc_ms;
    uint32_t ton_ms;        /* on-time of the current period */
    float    icap_acc;
    uint32_t icap_n;
    bool     eoc;
    bool     gate;          /* EN_CHG allowed in this tick */
} sc_power_t;

void  sc_power_init(sc_power_t *p);
void  sc_power_target(const sc_referee_data_t *ref, bool can_fresh, float can_limit_w, uint32_t now_ms,
                      sc_target_t *out);
/* running: the supervisor has the charger enabled.  dt in ms (normally 1). */
void  sc_power_step(sc_power_t *p, const sc_target_t *t, bool running, float vin, float pin, float icap,
                    float vnode, float vdda, uint32_t dt_ms);
/* exposed for tests */
float sc_dac_volts_for_limit(float i_lim_a);
float sc_limit_min_hw(float vdda);

#endif
