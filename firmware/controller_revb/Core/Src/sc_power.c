#include "sc_power.h"

#include <math.h>
#include <string.h>

#include "sc_config.h"

static float clampf(float v, float lo, float hi)
{
    return v < lo ? lo : (v > hi ? hi : v);
}

void sc_power_init(sc_power_t *p)
{
    memset(p, 0, sizeof(*p));
    p->ton_eoc_ms = SC_EOC_PERIOD_MS;
    p->ton_ms = SC_EOC_PERIOD_MS;
    p->i_min_hw = sc_limit_min_hw(3.3f);
}

void sc_power_target(const sc_referee_data_t *ref, bool can_fresh, float can_limit_w, uint32_t now_ms,
                     sc_target_t *out)
{
    bool st_fresh = ref->have_status && (uint32_t)(now_ms - ref->t_status_ms) < SC_SRC_TIMEOUT_MS;
    bool pw_fresh = ref->have_power && (uint32_t)(now_ms - ref->t_power_ms) < SC_SRC_TIMEOUT_MS;
    float limit;
    out->chassis_off = false;
    if (st_fresh) {
        out->src = SC_SRC_REFEREE;
        limit = (float)ref->chassis_power_limit;
        out->chassis_off = !ref->chassis_output_on;
    } else if (can_fresh) {
        out->src = SC_SRC_CAN;
        limit = can_limit_w;
    } else {
        out->src = SC_SRC_DEFAULT;
        limit = SC_P_DEFAULT_W;
    }
    float p = limit - SC_P_MARGIN_W;
    if (st_fresh && pw_fresh && (float)ref->buffer_energy < SC_BUF_REF_J) {
        p -= SC_K_BUF_W_PER_J * (SC_BUF_REF_J - (float)ref->buffer_energy);
    }
    if (out->chassis_off) {
        p = 0.0f;
    }
    out->p_target = clampf(p, 0.0f, SC_P_MAX_W);
}

float sc_dac_volts_for_limit(float i_lim_a)
{
    float ofs_v = SC_ISNS_TH_V - i_lim_a * SC_R_SHUNT_IN;     /* offset needed across R5 */
    if (ofs_v <= 0.0f) {
        return 0.0f;                                         /* Q3 off, full hardware limit */
    }
    float i_ofs = ofs_v / SC_R_ISNS;
    float v_b = SC_VBE + i_ofs * SC_R_OFS_E;
    return v_b + (v_b / SC_R_OFS_BPD + i_ofs / 100.0f) * SC_R_OFS_B;   /* hFE ~100 */
}

float sc_limit_min_hw(float vdda)
{
    float v_dac = vdda * SC_DAC_VMAX_FRAC;
    float v_b = v_dac / (1.0f + SC_R_OFS_B / SC_R_OFS_BPD);
    float i_ofs = (v_b - SC_VBE) / SC_R_OFS_E;
    float i = (SC_ISNS_TH_V - i_ofs * SC_R_ISNS) / SC_R_SHUNT_IN;
    return i > 0.0f ? i : 0.0f;
}

static void gate_step(sc_power_t *p, bool running, float icap, float vnode, uint32_t dt_ms)
{
    if (!running) {
        p->phase_ms = 0u;
        p->ton_eoc_ms = SC_EOC_PERIOD_MS;
        p->icap_acc = 0.0f;
        p->icap_n = 0u;
        p->eoc = false;
        p->gate = false;
        return;
    }
    p->eoc = vnode >= SC_V_EOC;
    if (p->phase_ms == 0u) {
        /* start of a period: choose the on-time */
        uint32_t ton_low = SC_EOC_PERIOD_MS;
        if (p->i_cmd < p->i_min_hw && p->i_min_hw > 0.0f) {
            float f = clampf(p->i_cmd / p->i_min_hw, 0.0f, 1.0f);
            ton_low = (uint32_t)lrintf(f * (float)SC_EOC_PERIOD_MS);
        }
        uint32_t ton = p->eoc ? p->ton_eoc_ms : SC_EOC_PERIOD_MS;
        p->ton_ms = ton < ton_low ? ton : ton_low;
    }
    p->gate = p->phase_ms < p->ton_ms;
    p->icap_acc += icap;
    p->icap_n++;
    p->phase_ms += dt_ms;
    if (p->phase_ms >= SC_EOC_PERIOD_MS) {
        /* end of a period: adapt the end-of-charge on-time to the measured bank current */
        float iavg = p->icap_n ? p->icap_acc / (float)p->icap_n : 0.0f;
        if (p->eoc) {
            float k = (iavg > 0.05f) ? SC_I_EOC_A / iavg : 1.5f;
            k = clampf(k, 0.5f, 1.5f);
            float t = clampf((float)p->ton_eoc_ms * k, (float)SC_EOC_TON_MIN_MS, (float)SC_EOC_PERIOD_MS);
            p->ton_eoc_ms = (uint32_t)lrintf(t);
        } else {
            p->ton_eoc_ms = SC_EOC_PERIOD_MS;
        }
        p->phase_ms = 0u;
        p->icap_acc = 0.0f;
        p->icap_n = 0u;
    }
}

void sc_power_step(sc_power_t *p, const sc_target_t *t, bool running, float vin, float pin, float icap,
                   float vnode, float vdda, uint32_t dt_ms)
{
    const float dt = (float)dt_ms / 1000.0f;
    p->i_min_hw = sc_limit_min_hw(vdda);
    if (!running) {
        p->p_ramp = 0.0f;
        p->trim_a = 0.0f;
    } else {
        float step = SC_P_RAMP_W_PER_S * dt;
        p->p_ramp = clampf(t->p_target, p->p_ramp - step, p->p_ramp + step);
    }
    float v = vin > 5.0f ? vin : 5.0f;
    /* closed-loop trim only with continuous conduction (no on/off gating in this period) */
    if (running && p->gate && p->ton_ms >= SC_EOC_PERIOD_MS) {
        /* the converter is current limited while the bank is below the end-of-charge voltage,
           or when the measured power already reaches the target */
        if (vnode < SC_V_EOC || pin > p->p_ramp - 2.0f) {
            p->trim_a += SC_TRIM_KI * ((p->p_ramp - pin) / v) * dt;
        } else {
            /* below the target (bank nearly full or load small): let the trim decay */
            float leak = SC_TRIM_LEAK_A_PER_S * dt;
            p->trim_a = (p->trim_a > leak) ? p->trim_a - leak : (p->trim_a < -leak ? p->trim_a + leak : 0.0f);
        }
        p->trim_a = clampf(p->trim_a, -SC_TRIM_MAX_A, SC_TRIM_MAX_A);
    }
    p->i_cmd = clampf(p->p_ramp / v + p->trim_a, 0.0f, SC_ILIM_HW_MAX_A);
    float i_for_dac = p->i_cmd > p->i_min_hw ? p->i_cmd : p->i_min_hw;
    p->dac_v = running ? sc_dac_volts_for_limit(i_for_dac) : sc_dac_volts_for_limit(p->i_min_hw);
    float vmax = vdda * SC_DAC_VMAX_FRAC;
    if (p->dac_v > vmax) {
        p->dac_v = vmax;
    }
    float code = (vdda > 1.0f) ? p->dac_v / vdda * 4095.0f : 0.0f;
    p->dac_code = (uint16_t)clampf(code, 0.0f, 4095.0f);
    gate_step(p, running, icap, vnode, dt_ms);
}
