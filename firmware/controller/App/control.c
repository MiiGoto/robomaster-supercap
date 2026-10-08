#include "rev_a.h"
#include <math.h>
void control_slow(app_t *a, uint32_t now) {
    unsigned i;
    float derate = 1, hi = 0, lo = 100, p, il;
    if (a->state != CHARGE && a->state != ASSIST) {
        a->current_reference = 0;
        a->outputs.gate = false;
        a->outputs.arm = false;
        return;
    }
    if (app_live_faults(a, now) || a->faults || !calibration_valid(&a->calibration) ||
        !a->config.tuning_verified || !a->config.commissioning_authorized ||
        FW_MODE == SAFE_MONITOR_ONLY) {
        a->current_reference = 0;
        a->outputs.gate = false;
        a->outputs.arm = false;
        return;
    }
    for (i = 0; i < 3; i++) {
        float t = a->sensors.value[TEMP_FET_CH + i];
        derate = fminf(derate, clampf((a->config.temp_stop[i] - t) /
                                          (a->config.temp_stop[i] - a->config.temp_warn[i]),
                                      0, 1));
    }
    for (i = 0; i < CELL_COUNT; i++) {
        hi = fmaxf(hi, a->monitor.cell_v[i]);
        lo = fminf(lo, a->monitor.cell_v[i]);
    }
    p = a->request_w;
    if (a->state == CHARGE) {
        p = fminf(p, a->config.charge_w) * derate * clampf((2.45f - hi) / 0.05f, 0, 1);
        il = p / (fmaxf(a->sensors.value[BUS_V], 1.0f) * fmaxf(a->duty_a, 0.45f));
    } else {
        if (p > a->config.assist_w) {
            if (!a->peak_active) {
                if (!a->peak_seen || now - a->last_peak_ms >= a->config.repetition_ms) {
                    a->peak_active = true;
                    a->peak_seen = true;
                    a->peak_started_ms = now;
                } else
                    p = a->config.assist_w;
            }
            if (a->peak_active && now - a->peak_started_ms >= a->config.peak_ms) {
                a->peak_active = false;
                a->last_peak_ms = now;
                p = a->config.assist_w;
            }
        } else if (a->peak_active) {
            a->peak_active = false;
            a->last_peak_ms = now;
        }
        p *= derate * clampf((a->sensors.value[CAP_V] - a->config.cap_min) / 0.5f, 0, 1) *
             clampf((lo - 1.30f) / 0.10f, 0, 1);
        il = -p /
             (a->config.efficiency * fmaxf(a->sensors.value[CAP_V], 1) * fmaxf(a->duty_b, 0.45f));
    }
    /* IL limit is deliberately below hardware trip, separately enforce cap-average target. */
    il = clampf(il, -a->config.il_limit_a, a->config.il_limit_a);
    il = clampf(il, -a->config.cap_limit_a / fmaxf(a->duty_b, 0.45f),
                a->config.cap_limit_a / fmaxf(a->duty_b, 0.45f));
    float slew = 100.0f * fminf((float)(now - a->control_ms) / 1000.0f, 0.05f);
    a->control_ms = now;
    a->current_reference += clampf(il - a->current_reference, -slew, slew);
    a->outputs.gate = fabsf(a->current_reference) > 0.01f;
    a->outputs.arm = a->outputs.gate;
}
void control_fast(app_t *a, float il, float bus, float cap) {
    float e, u, trial, maxv, da, db, correction;
    if (!isfinite(il) || !isfinite(bus) || !isfinite(cap) || bus < 1 || cap < 1 || a->faults ||
        !a->outputs.gate || FW_MODE == SAFE_MONITOR_ONLY) {
        a->integrator = 0;
        return;
    }
    maxv = fmaxf(bus, cap);
    da = 0.90f * cap / maxv;
    db = 0.90f * bus / maxv;
    e = a->current_reference - il;
    trial = a->integrator + a->calibration.ki * e / (float)a->config.pwm_hz;
    /* PI commands inductor voltage, not arbitrary duty. V_L = dA*VBUS-dB*VCAP. */
    u = clampf(a->calibration.kp * e + trial, -0.1f * maxv, 0.1f * maxv);
    correction = a->calibration.kp * e + trial;
    if (fabsf(correction - u) < 0.0001f || e * correction < 0)
        a->integrator = trial;
    a->duty_a = clampf(da + u / (2.0f * bus), 0.05f, 0.95f);
    a->duty_b = clampf(db - u / (2.0f * cap), 0.05f, 0.95f);
}
