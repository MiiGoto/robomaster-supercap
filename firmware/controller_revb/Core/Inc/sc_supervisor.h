/*
 * Charger state machine and software protections.
 * Hardware protections (input/node over-voltage comparators, default-off enables) work
 * without the MCU; this layer adds sequencing, temperature, over-current and retries.
 */
#ifndef SC_SUPERVISOR_H
#define SC_SUPERVISOR_H

#include <stdbool.h>
#include <stdint.h>

#include "sc_sensing.h"

typedef enum {
    SC_ST_BOOT = 0,
    SC_ST_IDLE = 1,     /* charger off, waiting for input / permission */
    SC_ST_START = 2,    /* PMOS on, checking the readback */
    SC_ST_CHARGE = 3,   /* converter enabled (EN_CHG may still be gated by sc_power) */
    SC_ST_FAULT = 4,
} sc_state_t;

/* fault bits (0x212 byte 1) */
#define SC_F_IN_OV      0x01u   /* input over-voltage (comparator pulled PMOS_EN low, or VIN high) */
#define SC_F_NODE_OV    0x02u   /* node over-voltage (NODE_OK low or VNODE high) */
#define SC_F_OVERTEMP   0x04u
#define SC_F_IN_OC      0x08u   /* input over-current - latched until reset */
#define SC_F_SENSOR     0x10u   /* VDDA or NTC implausible */
#define SC_F_START      0x20u   /* PMOS_EN readback did not follow EN_PMOS */
#define SC_F_SHORT      0x40u   /* node did not rise while charging (short); latched after SC_SHORT_MAX_TRIPS */
#define SC_F_LATCHED    (SC_F_IN_OC)

typedef struct {
    bool pmos_en_rb;    /* PB13: PMOS_EN net after the comparator wired-AND */
    bool node_ok;       /* PB12 */
    bool pgood;         /* PB2 (telemetry only) */
    bool chg_on;        /* EN_CHG pin state of the previous tick (after sc_power gating) */
} sc_inputs_t;

typedef struct {
    sc_state_t state;
    uint8_t    faults;      /* currently active or latched */
    uint8_t    last_fault;  /* most recent fault cause, for display */
    uint32_t   t_state_ms;  /* time in the current state */
    uint32_t   vin_ok_ms;
    uint32_t   oc_ms;
    uint32_t   now_ms;
    bool       hot;         /* over-temperature hysteresis */
    uint32_t   short_win_ms;  /* switching time accumulated in the current check window */
    float      short_v0;      /* node voltage at the start of the window */
    uint8_t    short_trips;   /* consecutive short trips */
    bool       short_latched;
    /* outputs */
    bool       en_pmos;
    bool       en_chg;      /* before gating by sc_power */
} sc_super_t;

void sc_super_init(sc_super_t *s);
void sc_super_step(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, float p_target, uint32_t dt_ms);
bool sc_super_running(const sc_super_t *s);

#endif
