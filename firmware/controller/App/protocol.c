#include "rev_a.h"
#include <math.h>
#include <string.h>
#define COMMAND_ID 0x501u
static void u16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
}
static int16_t scaled(float f, float k) {
    if (!isfinite(f))
        return INT16_MIN;
    return (int16_t)clampf(f * k, -32767, 32767);
}
bool app_can_receive(app_t *a, uint16_t id, const uint8_t *d, size_t n, uint32_t now) {
    uint8_t delta;
    command_t cmd;
    float watts;
    bool accepted;
    if (id != COMMAND_ID || n != 8 || d[0] != 1 || crc8(d, 7) != d[7] || d[3] != 0 || d[6] != 0 ||
        d[2] > CMD_SERVICE) {
        a->command_rejects++;
        return false;
    }
    delta = (uint8_t)(d[1] - a->sequence);
    if (a->command_seen && (delta == 0 || delta > 127)) {
        a->command_rejects++;
        return false;
    }
    cmd = (command_t)d[2];
    watts = (float)((uint16_t)d[4] | ((uint16_t)d[5] << 8)) / 10.0f;
    if ((cmd != CMD_CHARGE && cmd != CMD_ASSIST && watts != 0) ||
        (cmd == CMD_CHARGE && watts > a->config.charge_w) ||
        (cmd == CMD_ASSIST && watts > a->config.peak_w)) {
        a->command_rejects++;
        return false;
    }
    accepted = app_command(a, cmd, watts, now);
    if (!accepted) {
        a->command_rejects++;
        return false;
    }
    a->sequence = d[1];
    a->command_ms = now;
    a->command_seen = true;
    return true;
}
bool app_can_receive_at(app_t *a, uint16_t id, const uint8_t *data, size_t size,
                        uint32_t received_ms, uint32_t now) {
    if (now - received_ms > a->config.can_timeout_ms) {
        a->command_rejects++;
        return false;
    }
    if (!app_can_receive(a, id, data, size, now))
        return false;
    /* Lease starts at ISR receipt, never at delayed foreground processing. */
    a->command_ms = received_ms;
    return true;
}
void telemetry_pack(const app_t *a, uint8_t page, uint8_t seq, uint8_t d[8]) {
    float lo = 100, hi = 0;
    unsigned i;
    memset(d, 0, 8);
    d[0] = 1;
    d[1] = seq;
    for (i = 0; i < CELL_COUNT; i++) {
        lo = fminf(lo, a->monitor.cell_v[i]);
        hi = fmaxf(hi, a->monitor.cell_v[i]);
    }
    switch (page) {
    case 0:
        d[2] = (uint8_t)a->state;
        d[3] = (uint8_t)FW_MODE;
        d[4] = 0;
        d[5] = 1;
        d[6] = 0;
        break;
    case 1:
        d[2] = (uint8_t)a->faults;
        d[3] = (uint8_t)(a->faults >> 8);
        d[4] = (uint8_t)(a->faults >> 16);
        d[5] = (uint8_t)(a->faults >> 24);
        d[6] = (uint8_t)a->reset_cause;
        break;
    case 2:
        u16(d + 2, (uint16_t)scaled(a->sensors.value[BUS_V], 1000));
        u16(d + 4, (uint16_t)scaled(a->sensors.value[CAP_V], 1000));
        d[6] = a->sensors.valid ? 1 : 0;
        break;
    case 3:
        u16(d + 2, (uint16_t)scaled(a->sensors.value[BUS_I], 1000));
        u16(d + 4, (uint16_t)scaled(a->sensors.value[CAP_I], 1000));
        d[6] = calibration_valid(&a->calibration) ? 1 : 0;
        break;
    case 4:
        u16(d + 2, (uint16_t)scaled(a->sensors.value[IL_I], 1000));
        u16(d + 4, (uint16_t)scaled(a->sensors.value[BUS_V] * a->sensors.value[BUS_I], 10));
        d[6] = a->monitor.config_valid ? 1 : 0;
        break;
    case 5:
        u16(d + 2, (uint16_t)scaled(a->sensors.value[CAP_V] * a->sensors.value[CAP_I], 10));
        u16(d + 4, (uint16_t)scaled(stored_energy_j(a->sensors.value[CAP_RAW]), 10));
        d[6] = a->monitor.measurements_valid ? 1 : 0;
        break;
    case 6:
        u16(d + 2, (uint16_t)scaled(usable_energy_j(a->sensors.value[CAP_RAW]), 10));
        u16(d + 4, (uint16_t)scaled(soe_percent(a->sensors.value[CAP_RAW]), 100));
        break;
    case 7:
        u16(d + 2, (uint16_t)scaled(lo, 1000));
        u16(d + 4, (uint16_t)scaled(hi, 1000));
        break;
    case 8:
        u16(d + 2, (uint16_t)scaled(hi - lo, 1000));
        u16(d + 4, (uint16_t)scaled(a->sensors.value[TEMP_FET_CH], 100));
        break;
    case 9:
        u16(d + 2, (uint16_t)scaled(a->sensors.value[TEMP_L_CH], 100));
        u16(d + 4, (uint16_t)scaled(a->sensors.value[TEMP_BANK_CH], 100));
        break;
    case 10:
        u16(d + 2, a->monitor.battery_status);
        d[4] = a->monitor.fet_status;
        d[5] = (uint8_t)a->monitor.safety_a;
        d[6] = (uint8_t)a->monitor.safety_b;
        break;
    case 11: {
        outputs_t o = app_safe_outputs(a);
        d[2] = (uint8_t)(o.pre_bus | (o.pre_cap << 1) | (o.iso_bus << 2) | (o.iso_cap << 3) |
                         (o.bypass_bus << 4) | (o.bypass_cap << 5) | (o.gate << 6) | (o.dump << 7));
        d[3] = a->precharge_phase;
        d[4] = (uint8_t)a->command_rejects;
        d[5] = a->monitor.open_wire_observed;
        d[6] = a->self_test_pass;
        break;
    }
    case 12:
        d[2] = a->reserved_feedback;
        d[3] = a->monitor_alert_asserted;
        u16(d + 4,
            (uint16_t)(a->control_isr_max_cycles > 65535u ? 65535u : a->control_isr_max_cycles));
        d[6] = a->referee_permit;
        break;
    default:
        d[6] = 0xff;
        break;
    }
    d[7] = crc8(d, 7);
}

typedef struct {
    char *out;
    size_t size, used;
} text_writer_t;
static void text(text_writer_t *w, const char *s) {
    while (*s && w->used + 1u < w->size)
        w->out[w->used++] = *s++;
    if (w->size)
        w->out[w->used] = 0;
}
static void number(text_writer_t *w, uint32_t value, unsigned base) {
    char digits[32];
    unsigned n = 0;
    do {
        digits[n++] = "0123456789abcdef"[value % base];
        value /= base;
    } while (value);
    while (n) {
        char s[2] = {digits[--n], 0};
        text(w, s);
    }
}
static void value(text_writer_t *w, const char *label, float f, unsigned scale) {
    uint32_t magnitude;
    text(w, label);
    if (!isfinite(f) || fabsf(f) > 100000.0f) {
        text(w, "INVALID ");
        return;
    }
    if (f < 0) {
        text(w, "-");
        f = -f;
    }
    magnitude = (uint32_t)(f * (float)scale + 0.5f);
    number(w, magnitude, 10);
    text(w, " ");
}
void cli_reply(const app_t *a, const char *line, char *out, size_t size) {
    text_writer_t w = {out, size, 0};
    unsigned i;
    if (size)
        out[0] = 0;
    if (strcmp(line, "version") == 0) {
        text(&w, FW_VERSION " mode=");
        number(&w, FW_MODE, 10);
    } else if (strcmp(line, "status") == 0) {
        text(&w, "state=");
        text(&w, state_name(a->state));
        text(&w, " faults=0x");
        number(&w, a->faults, 16);
        text(&w, calibration_valid(&a->calibration) ? " cal=verified" : " cal=UNVERIFIED");
        text(&w, " reset=0x");
        number(&w, a->reset_cause, 16);
        text(&w, " max_adc_irq_cycles=");
        number(&w, a->control_isr_max_cycles, 10);
    } else if (strcmp(line, "sensors") == 0) {
        text(&w, "mV/mA (UNVERIFIED until calibrated): ");
        value(&w, "VB=", a->sensors.value[BUS_V], 1000);
        value(&w, "VC=", a->sensors.value[CAP_V], 1000);
        value(&w, "IB=", a->sensors.value[BUS_I], 1000);
        value(&w, "IC=", a->sensors.value[CAP_I], 1000);
        value(&w, "IL=", a->sensors.value[IL_I], 1000);
        value(&w, "rawVB=", a->sensors.value[BUS_RAW], 1000);
        value(&w, "rawVC=", a->sensors.value[CAP_RAW], 1000);
    } else if (strcmp(line, "cells") == 0) {
        text(&w, "mV logical1..9 (physical1..8,10): ");
        for (i = 0; i < CELL_COUNT; i++)
            value(&w, "", a->monitor.cell_v[i], 1000);
    } else if (strcmp(line, "temps") == 0) {
        text(&w, "centi-degC (offset/lag unverified): ");
        value(&w, "FET=", a->sensors.value[TEMP_FET_CH], 100);
        value(&w, "L=", a->sensors.value[TEMP_L_CH], 100);
        value(&w, "bank=", a->sensors.value[TEMP_BANK_CH], 100);
    } else if (strcmp(line, "faults") == 0) {
        text(&w, "latched=0x");
        number(&w, a->faults, 16);
        text(&w, " first=0x");
        number(&w, a->first_fault, 16);
        text(&w, " at_ms=");
        number(&w, a->first_fault_ms, 10);
        text(&w, " state=");
        text(&w, state_name(a->first_fault_state));
        text(&w, " log_entries=");
        number(&w, a->log_count, 10);
        text(&w, a->log_frozen ? " frozen" : " recording");
    } else if (strcmp(line, "bq status") == 0) {
        text(&w, "config=");
        number(&w, a->monitor.config_valid, 10);
        text(&w, " measurements=");
        number(&w, a->monitor.measurements_valid, 10);
        text(&w, " openwire-cycle-observed=");
        number(&w, a->monitor.open_wire_observed, 10);
        text(&w, " permits=");
        number(&w, a->monitor.permissions_healthy, 10);
        text(&w, " status=0x");
        number(&w, a->monitor.battery_status, 16);
        text(&w, " fet=0x");
        number(&w, a->monitor.fet_status, 16);
    } else if (strcmp(line, "can status") == 0) {
        text(&w, "protocol=1 seq=");
        number(&w, a->sequence, 10);
        text(&w, " lease_ms=");
        number(&w, a->command_ms, 10);
        text(&w, " rejects=");
        number(&w, a->command_rejects, 10);
    } else
        text(&w, "read-only: status sensors cells temps faults bq status can status version");
    text(&w, "\r\n");
}
