#include "sc_supervisor.h"

#include <string.h>

#include "sc_config.h"

void sc_super_init(sc_super_t *s)
{
    memset(s, 0, sizeof(*s));
    s->state = SC_ST_BOOT;
}

bool sc_super_running(const sc_super_t *s)
{
    return s->state == SC_ST_CHARGE;
}

static void enter(sc_super_t *s, sc_state_t st)
{
    s->state = st;
    s->t_state_ms = 0u;
}

static void fault(sc_super_t *s, uint8_t f)
{
    s->faults |= f;
    s->last_fault = f;
    enter(s, SC_ST_FAULT);
}

/* conditions that must hold while the converter runs; returns fault bits */
static uint8_t check_run(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, uint32_t dt_ms)
{
    uint8_t f = 0u;
    if (!m->valid) {
        f |= SC_F_SENSOR;
    }
    if (m->vin > SC_VIN_MAX) {
        f |= SC_F_IN_OV;
    }
    if (!in->node_ok || m->vnode > SC_VNODE_SW_OV) {
        f |= SC_F_NODE_OV;
    }
    if (m->temp_c > SC_T_MAX_C) {
        f |= SC_F_OVERTEMP;
        s->hot = true;
    }
    if (m->iin > SC_IIN_OC_A) {
        s->oc_ms += dt_ms;
        if (s->oc_ms >= SC_IIN_OC_MS) {
            f |= SC_F_IN_OC;
        }
    } else {
        s->oc_ms = 0u;
    }
    return f;
}

/* short / stall: while the node is low, each SC_SHORT_WIN_MS of switching must raise it */
static uint8_t check_short(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, uint32_t dt_ms)
{
    if (m->vnode >= SC_SHORT_V_CHECK) {
        s->short_win_ms = 0u;
        s->short_trips = 0u;          /* the node came up: earlier trips were not a hard short */
        return 0u;
    }
    if (!in->chg_on) {
        return 0u;                    /* gated off by sc_power: pause the window */
    }
    if (s->short_win_ms == 0u) {
        s->short_v0 = m->vnode;
    }
    s->short_win_ms += dt_ms;
    if (s->short_win_ms < SC_SHORT_WIN_MS) {
        return 0u;
    }
    s->short_win_ms = 0u;
    if (m->vnode - s->short_v0 >= SC_SHORT_DV_MIN) {
        return 0u;
    }
    if (s->short_trips < 255u) {
        s->short_trips++;
    }
    if (s->short_trips >= SC_SHORT_MAX_TRIPS) {
        s->short_latched = true;
    }
    return SC_F_SHORT;
}

/* conditions that keep a fault active (except latched ones) */
static uint8_t still_bad(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in)
{
    uint8_t f = s->faults & SC_F_LATCHED;
    if (s->short_latched) {
        f |= SC_F_SHORT;
    }
    if (!m->valid) {
        f |= SC_F_SENSOR;
    }
    if (m->vin > SC_VIN_MAX) {
        f |= SC_F_IN_OV;
    }
    if (!in->node_ok || m->vnode > SC_VNODE_SW_OV_CLEAR) {
        f |= (s->faults & SC_F_NODE_OV) ? SC_F_NODE_OV : 0u;
    }
    if (s->hot && m->temp_c > SC_T_RESUME_C) {
        f |= SC_F_OVERTEMP;
    } else {
        s->hot = false;
    }
    return f;
}

void sc_super_step(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, float p_target, uint32_t dt_ms)
{
    s->now_ms += dt_ms;
    s->t_state_ms += dt_ms;
    bool vin_in_range = m->vin >= SC_VIN_START_MIN && m->vin <= SC_VIN_MAX;
    s->vin_ok_ms = vin_in_range ? s->vin_ok_ms + dt_ms : 0u;

    switch (s->state) {
    case SC_ST_BOOT:
        if (s->t_state_ms >= SC_BOOT_MS) {
            enter(s, SC_ST_IDLE);
        }
        break;

    case SC_ST_IDLE: {
        uint8_t f = check_run(s, m, in, 0u) & (uint8_t)~SC_F_IN_OC;
        if (f) {
            fault(s, f);
            break;
        }
        bool permit = s->vin_ok_ms >= SC_VIN_OK_MS && p_target >= SC_P_MIN_RUN_W && !s->hot &&
                      m->vnode < SC_VNODE_SW_OV_CLEAR;
        if (permit) {
            enter(s, SC_ST_START);
        }
        break;
    }

    case SC_ST_START:
        if (s->t_state_ms >= SC_START_CHECK_MS) {
            if (!in->pmos_en_rb) {
                fault(s, SC_F_START);
            } else {
                s->oc_ms = 0u;
                s->short_win_ms = 0u;
                enter(s, SC_ST_CHARGE);
            }
        }
        break;

    case SC_ST_CHARGE: {
        uint8_t f = check_run(s, m, in, dt_ms);
        if (!in->pmos_en_rb) {
            f |= SC_F_IN_OV;   /* comparator A pulled PMOS_EN low */
        }
        f |= check_short(s, m, in, dt_ms);
        if (f) {
            fault(s, f);
            break;
        }
        if (m->vin < SC_VIN_RUN_MIN || p_target < SC_P_MIN_RUN_W - 1.0f) {
            enter(s, SC_ST_IDLE);   /* input gone or no permission: normal stop */
        }
        break;
    }

    case SC_ST_FAULT: {
        uint8_t f = still_bad(s, m, in);
        s->faults = f | (s->faults & SC_F_LATCHED);
        uint32_t retry = (s->last_fault & SC_F_SHORT) ? SC_SHORT_RETRY_MS : SC_RETRY_MS;
        if (s->faults == 0u && s->t_state_ms >= retry) {
            enter(s, SC_ST_IDLE);
        } else if (f) {
            s->t_state_ms = 0u;     /* retry delay restarts while the cause persists */
        }
        break;
    }
    }

    s->en_pmos = (s->state == SC_ST_START) || (s->state == SC_ST_CHARGE);
    s->en_chg = (s->state == SC_ST_CHARGE);
}
