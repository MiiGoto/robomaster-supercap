#include "rev_a.h"
#include <math.h>
#include <string.h>
const char *state_name(fw_state_t s) {
    static const char *const names[] = {
        "BOOT_SAFE", "MONITOR_INIT", "SELF_TEST", "DISARMED", "PRECHARGE",     "READY",  "CHARGE",
        "STANDBY",   "ASSIST",       "SHUTDOWN",  "COOLDOWN", "FAULT_LATCHED", "SERVICE"};
    return (unsigned)s < sizeof(names) / sizeof(names[0]) ? names[s] : "INVALID";
}
static bool energized_state(fw_state_t s) {
    return s == PRECHARGE || s == READY || s == CHARGE || s == ASSIST || s == STANDBY;
}
static bool cooled(const app_t *a) {
    unsigned i;
    for (i = 0; i < 3; i++)
        if (!isfinite(a->sensors.value[TEMP_FET_CH + i]) ||
            a->sensors.value[TEMP_FET_CH + i] >= a->config.temp_rearm[i])
            return false;
    return true;
}
bool app_transition(app_t *a, fw_state_t next, uint32_t now) {
    bool ok = false;
    if (next == FAULT_LATCHED)
        ok = true;
    else
        switch (a->state) {
        case BOOT_SAFE:
            ok = next == MONITOR_INIT;
            break;
        case MONITOR_INIT:
            ok = next == SELF_TEST;
            break;
        case SELF_TEST:
            ok = next == DISARMED && a->self_test_pass;
            break;
        case DISARMED:
            ok = next == PRECHARGE || next == SERVICE || next == SELF_TEST;
            break;
        case PRECHARGE:
            ok = next == READY || next == SHUTDOWN;
            break;
        case READY:
        case STANDBY:
            ok = next == CHARGE || next == ASSIST || next == SHUTDOWN || next == STANDBY;
            break;
        case CHARGE:
        case ASSIST:
            ok = next == STANDBY || next == SHUTDOWN;
            break;
        case SHUTDOWN:
            ok = next == DISARMED || next == COOLDOWN || next == SERVICE;
            break;
        case COOLDOWN:
            ok = next == SELF_TEST && a->rearm_pending && cooled(a);
            break;
        case FAULT_LATCHED:
            ok = next == SELF_TEST && a->rearm_pending && cooled(a);
            break;
        case SERVICE:
            ok = next == DISARMED;
            break;
        default:
            break;
        }
    if (!ok)
        return false;
    if (a->state == ASSIST && next != ASSIST && a->peak_active) {
        a->peak_active = false;
        a->last_peak_ms = now;
    }
    a->state = next;
    a->entered_ms = now;
    a->control_ms = now;
    a->integrator = 0;
    a->current_reference = 0;
    a->outputs.gate = false;
    a->outputs.arm = false;
    if (next == PRECHARGE) {
        a->precharge_phase = 0;
        a->phase_ms = now;
        a->previous_bus_v = a->sensors.value[BUS_V];
        a->previous_cap_v = a->sensors.value[CAP_V];
    }
    if (next == DISARMED || next == FAULT_LATCHED || next == SERVICE || next == COOLDOWN) {
        memset(&a->outputs, 0, sizeof(a->outputs));
        a->power_session = false;
    }
    return true;
}
void app_init(app_t *a, const fw_config_t *config, uint32_t now) {
    memset(a, 0, sizeof(*a));
    a->state = BOOT_SAFE;
    a->config = *config;
    a->entered_ms = now;
    calibration_defaults(&a->calibration);
}
void app_fault(app_t *a, uint32_t cause, uint32_t now) {
    if (!cause)
        return;
    if (a->first_fault == 0) {
        a->first_fault = cause & (~cause + 1u);
        a->first_fault_ms = now;
        a->first_fault_state = a->state;
        a->first_fault_snapshot = a->sensors;
    }
    a->faults |= cause;
    a->outputs.gate = false;
    a->outputs.arm = false;
    a->request_w = 0;
    a->peak_active = false;
    (void)app_transition(a, FAULT_LATCHED, now);
    /* Include first-fault snapshot, then freeze the preceding RAM history. */
    if (!a->log_frozen) {
        log_entry_t *l = &a->log[a->log_head];
        l->timestamp_ms = now;
        l->faults = a->faults;
        l->state = a->first_fault_state;
        l->sensors = a->sensors;
        a->log_head = (uint16_t)((a->log_head + 1u) % LOG_DEPTH);
        if (a->log_count < LOG_DEPTH)
            a->log_count++;
        a->log_frozen = true;
    }
}
uint32_t app_live_faults(const app_t *a, uint32_t now) {
    uint32_t f = 0;
    unsigned i;
    float lo = 100, hi = 0, sum = 0;
    if (!a->monitor.config_valid)
        f |= BQ_CONFIG;
    f |= a->monitor.faults;
    bool settling_allowed = a->monitor.settling && !a->power_session &&
                            (a->state == DISARMED || a->state == SERVICE) &&
                            now - a->monitor.timestamp_ms <= 1500u;
    if ((!a->monitor.measurements_valid && !settling_allowed) ||
        now - a->monitor.timestamp_ms > (settling_allowed ? 1500u : 500u))
        f |= SENSOR_INVALID;
    if (!a->sensors.valid)
        f |= SENSOR_INVALID;
    if (now - a->sensors.timestamp_ms > a->config.sensor_timeout_ms)
        f |= ADC_STALE;
    for (i = 0; i < CELL_COUNT; i++) {
        float v = a->monitor.cell_v[i];
        if (!isfinite(v) || v < 0 || v > 3)
            f |= SENSOR_INVALID;
        if (v > 2.45f)
            f |= CELL_OV;
        if (v < 1.2144f)
            f |= CELL_UV;
        if (v < lo)
            lo = v;
        if (v > hi)
            hi = v;
        sum += v;
    }
    if (hi - lo > 0.150f)
        f |= CELL_IMBALANCE;
    /* Prototype software stop;
    not balancing start threshold. */
    if (a->monitor.measurements_valid && fabsf(sum - a->sensors.value[CAP_RAW]) > 1.0f)
        f |= SENSOR_INVALID;
    for (i = 0; i < 3; i++) {
        float t = a->sensors.value[TEMP_FET_CH + i];
        if (!isfinite(t))
            f |= TEMP_SENSOR_INVALID;
        else if (t >= a->config.temp_stop[i])
            f |= (TEMP_FET << i);
    }
    if (a->sensors.value[BUS_RAW] > a->config.bus_max)
        f |= BUS_OV;
    if (a->sensors.value[CAP_RAW] > a->config.cap_max + 0.10f)
        f |= CAP_OV;
    if (a->state == SERVICE && FW_MODE != SAFE_MONITOR_ONLY && a->config.commissioning_authorized &&
        a->config.service_dump_authorized) {
        if (!a->command_seen || now - a->command_ms > a->config.can_timeout_ms)
            f |= CAN_TIMEOUT;
        if (now - a->entered_ms > a->config.discharge_timeout_ms &&
            a->sensors.value[CAP_RAW] >= 1.0f)
            f |= DISCHARGE_TIMEOUT;
    }
    if (a->power_session) {
        if (!a->hw_fault_clear || !a->referee_permit)
            f |= HW_FAULT;
        if (a->sensors.value[BUS_RAW] < a->config.bus_min)
            f |= BUS_UV;
        if (a->sensors.value[CAP_RAW] < a->config.cap_min)
            f |= CAP_UV;
        if (!a->command_seen || now - a->command_ms > a->config.can_timeout_ms)
            f |= CAN_TIMEOUT;
        if (fabsf(a->sensors.value[CAP_I]) > a->config.cap_limit_a + 0.25f ||
            fabsf(a->sensors.value[IL_I]) > a->config.fast_trip_a ||
            fabsf(a->sensors.value[BUS_I]) > 7.5f)
            f |= HW_OC;
    }
    return f;
}
static bool ready_guard(const app_t *a, uint32_t now) {
    return FW_MODE != SAFE_MONITOR_ONLY && a->config.commissioning_authorized &&
           a->config.tuning_verified && calibration_valid(&a->calibration) && a->self_test_pass &&
           a->faults == 0 && a->hw_fault_clear && a->referee_permit &&
           a->monitor.open_wire_observed && a->monitor.permissions_healthy &&
           app_live_faults(a, now) == 0 && a->sensors.value[BUS_RAW] >= a->config.bus_min &&
           a->sensors.value[CAP_RAW] >= a->config.cap_min &&
           a->sensors.value[CAP_RAW] <= a->config.cap_max;
}
bool app_command(app_t *a, command_t cmd, float watts, uint32_t now) {
    if (!isfinite(watts) || watts < 0)
        return false;
    switch (cmd) {
    case CMD_STATUS:
        return true;
    case CMD_ARM:
        if (a->state != DISARMED || !ready_guard(a, now))
            return false;
        a->power_session = true;
        return app_transition(a, PRECHARGE, now);
    case CMD_DISARM:
    case CMD_SHUTDOWN:
        a->request_w = 0;
        a->outputs.gate = false;
        a->outputs.arm = false;
        if (a->state == SERVICE)
            return app_transition(a, DISARMED, now);
        if (energized_state(a->state))
            return app_transition(a, SHUTDOWN, now);
        return a->state == DISARMED || a->state == FAULT_LATCHED || a->state == SERVICE;
    case CMD_REARM:
        if (a->state != FAULT_LATCHED && a->state != COOLDOWN)
            return false;
        if (app_live_faults(a, now) != 0 || !cooled(a) || !a->hw_fault_clear || !a->referee_permit)
            return false;
        a->rearm_pending = true;
        a->faults = 0;
        a->self_test_pass = false;
        return app_transition(a, SELF_TEST, now);
    case CMD_CHARGE:
    case CMD_ASSIST:
        if (!ready_guard(a, now) || !a->power_session ||
            watts > (cmd == CMD_CHARGE ? a->config.charge_w : a->config.peak_w))
            return false;
        if (a->state != READY && a->state != STANDBY)
            return false;
        if (fabsf(a->sensors.value[IL_I]) > 0.25f)
            return false;
        a->request_w = watts;
        return app_transition(a, cmd == CMD_CHARGE ? CHARGE : ASSIST, now);
    case CMD_STANDBY:
        a->request_w = 0;
        return app_transition(a, STANDBY, now);
    case CMD_SERVICE:
        /* Only diagnostic SERVICE label;
               never certifies independent-meter safety. */
        if (a->state != DISARMED)
            return false;
        return app_transition(a, SERVICE, now);
    default:
        return false;
    }
}
void app_step(app_t *a, uint32_t now) {
    uint32_t f;
    uint32_t elapsed = now - a->entered_ms;
    a->outputs.monitor_valid = a->monitor.config_valid && a->monitor.measurements_valid &&
                               a->monitor.open_wire_observed && a->monitor.permissions_healthy &&
                               a->monitor.faults == 0;
    if (a->state == BOOT_SAFE) {
        (void)app_transition(a, MONITOR_INIT, now);
        return;
    }
    if (a->state == MONITOR_INIT) {
        if (a->monitor.faults) {
            app_fault(a, a->monitor.faults, now);
            return;
        }
        if (a->outputs.monitor_valid)
            (void)app_transition(a, SELF_TEST, now);
        else if (elapsed > 10000u)
            app_fault(a, BQ_CONFIG, now);
        return;
    }
    f = app_live_faults(a, now);
    if (f && a->state != FAULT_LATCHED) {
        app_fault(a, f, now);
        return;
    }
    if (a->state == SELF_TEST) {
        a->self_test_pass = f == 0 && a->outputs.monitor_valid;
        if (a->self_test_pass) {
            a->rearm_pending = false;
            (void)app_transition(a, DISARMED, now);
        }
        return;
    }
    if (a->state == FAULT_LATCHED) {
        /* A healthy monitor may clear the hardware cause while all power outputs
         * remain disabled. Explicit REARM and new self-test are still required. */
        return;
    }
    if (a->state == PRECHARGE) {
        if (elapsed > a->config.precharge_ms) {
            app_fault(a, PRECHARGE_TIMEOUT, now);
            return;
        }
        a->outputs.iso_bus = true;
        a->outputs.iso_cap = true;
        a->outputs.pre_bus = true;
        a->outputs.pre_cap = true;
        if (a->sensors.value[BUS_V] > a->sensors.value[BUS_RAW] + 0.5f ||
            a->sensors.value[CAP_V] > a->sensors.value[CAP_RAW] + 0.5f ||
            fabsf(a->sensors.value[BUS_I]) > 0.5f || fabsf(a->sensors.value[CAP_I]) > 0.5f ||
            a->sensors.value[BUS_V] + 0.5f < a->previous_bus_v ||
            a->sensors.value[CAP_V] + 0.5f < a->previous_cap_v) {
            app_fault(a, CONTACT_SEQUENCE, now);
            return;
        }
        a->previous_bus_v = a->sensors.value[BUS_V];
        a->previous_cap_v = a->sensors.value[CAP_V];
        if (fabsf(a->sensors.value[BUS_RAW] - a->sensors.value[BUS_V]) < 1.0f &&
            fabsf(a->sensors.value[CAP_RAW] - a->sensors.value[CAP_V]) < 1.0f &&
            elapsed >= a->config.settle_ms) {
            if (a->precharge_phase == 0) {
                a->precharge_phase = 1;
                a->phase_ms = now;
            } else if (now - a->phase_ms >= a->config.settle_ms) {
                a->outputs.bypass_bus = true;
                a->outputs.bypass_cap = true;
                if (a->precharge_phase == 1) {
                    a->precharge_phase = 2;
                    a->phase_ms = now;
                } else if (now - a->phase_ms >= a->config.settle_ms) {
                    a->outputs.pre_bus = false;
                    a->outputs.pre_cap = false;
                    (void)app_transition(a, READY, now);
                }
            }
        }
    }
    if (a->state == SHUTDOWN) {
        a->outputs.gate = false;
        a->outputs.arm = false;
        /* Stop switching first;
               contacts open after zero-current observation or bounded timeout. */
        if (fabsf(a->sensors.value[IL_I]) < 0.25f && elapsed >= a->config.settle_ms) {
            memset(&a->outputs, 0, sizeof(a->outputs));
            (void)app_transition(a, cooled(a) ? DISARMED : COOLDOWN, now);
        } else if (elapsed > 500u)
            app_fault(a, CONTACT_SEQUENCE, now);
    }
    control_slow(a, now);
    if (!a->log_frozen) {
        log_entry_t *l = &a->log[a->log_head];
        l->timestamp_ms = now;
        l->faults = a->faults;
        l->state = a->state;
        l->sensors = a->sensors;
        a->log_head = (uint16_t)((a->log_head + 1u) % LOG_DEPTH);
        if (a->log_count < LOG_DEPTH)
            a->log_count++;
    }
}
outputs_t app_safe_outputs(const app_t *a) {
    outputs_t o = a->outputs;
    o.monitor_valid = o.monitor_valid && a->monitor.config_valid && a->monitor.measurements_valid &&
                      a->monitor.permissions_healthy;
    if (FW_MODE == SAFE_MONITOR_ONLY || !a->config.commissioning_authorized ||
        !a->config.tuning_verified || !calibration_valid(&a->calibration) || a->faults ||
        !a->monitor.config_valid || !a->monitor.measurements_valid ||
        !a->monitor.permissions_healthy || !a->sensors.valid || !a->hw_fault_clear ||
        !a->referee_permit) {
        memset(&o, 0, sizeof(o));
        o.monitor_valid = a->outputs.monitor_valid && a->monitor.config_valid &&
                          a->monitor.measurements_valid && a->monitor.permissions_healthy;
    }
    if (!a->power_session || !energized_state(a->state)) {
        o.gate = false;
        o.arm = false;
        o.pre_bus = false;
        o.pre_cap = false;
        o.iso_bus = false;
        o.iso_cap = false;
        o.bypass_bus = false;
        o.bypass_cap = false;
    }
    /* Explicit SERVICE plus a separately reviewed build policy. No dump on fault/overheat.
     * BQ UV may stop this path early; an independent service tool is still required. */
    o.dump = FW_MODE != SAFE_MONITOR_ONLY && a->state == SERVICE &&
             a->config.commissioning_authorized && a->config.service_dump_authorized &&
             a->config.tuning_verified && a->monitor.config_valid &&
             a->monitor.measurements_valid && a->monitor.permissions_healthy && a->hw_fault_clear &&
             a->referee_permit && calibration_valid(&a->calibration) && a->sensors.valid &&
             a->faults == 0 && cooled(a) && a->sensors.value[CAP_RAW] >= 1.0f;
    return o;
}
