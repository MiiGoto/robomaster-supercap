#include "bq76942.h"
#include <math.h>
#include <string.h>
/* SLUUBY1B sections3.1/9.3: 24-clock SPI mode0, delayed response, polynomial0x07.
 * Bounded foreground transactions only. Never call from an ISR. */
bool bq_byte(bq_t *b, uint8_t address, bool write, uint8_t *value) {
    uint8_t tx[3], rx[3], dummy[3] = {0, 0, 0};
    unsigned attempt;
    tx[0] = (uint8_t)((address & 0x7fu) | (write ? 0x80u : 0));
    tx[1] = write ? *value : 0;
    tx[2] = crc8(tx, 2);
    for (attempt = 0; attempt < 3; attempt++) {
        if (!b->io.transfer(b->io.context, tx, rx)) {
            b->communication_fault = BQ_CONFIG;
            return false;
        }
        b->io.delay_us(b->io.context, 250u);
        if (!b->io.transfer(b->io.context, dummy, rx)) {
            b->communication_fault = BQ_CONFIG;
            return false;
        }
        b->io.delay_us(b->io.context, 250u);
        if (rx[0] == 0xff && rx[1] == 0xff) {
            if (rx[2] == 0xaa) {
                b->communication_fault = BQ_CRC;
                return false;
            }
            b->io.delay_us(b->io.context, 5000u);
            continue;
        }
        if (crc8(rx, 2) != rx[2]) {
            b->communication_fault = BQ_CRC;
            return false;
        }
        if (rx[0] != tx[0] || (write && rx[1] != *value)) {
            b->communication_fault = BQ_CONFIG;
            return false;
        }
        if (!write)
            *value = rx[1];
        return true;
    }
    b->communication_fault = BQ_CONFIG;
    return false;
}
static bool word(bq_t *b, uint8_t address, bool write, uint16_t *value) {
    uint8_t lo = (uint8_t)*value, hi = (uint8_t)(*value >> 8);
    if (!bq_byte(b, address, write, &lo) || !bq_byte(b, (uint8_t)(address + 1u), write, &hi))
        return false;
    if (!write)
        *value = (uint16_t)((uint16_t)lo | ((uint16_t)hi << 8));
    return true;
}
static bool command_only(bq_t *b, uint16_t cmd) {
    /* Strict allowlist. No OTP, sealing, reset, shutdown, chemical-fuse or FET-test APIs. */
    if (cmd != 0x0090u && cmd != 0x0092u && cmd != 0x009au && cmd != 0x0096u && cmd != 0x0022u)
        return false;
    if (!word(b, 0x3eu, true, &cmd))
        return false;
    b->io.delay_us(b->io.context, 2000u);
    return true;
}
bool bq_subcommand(bq_t *b, uint16_t cmd, uint8_t *buffer, size_t *length) {
    uint16_t echo;
    uint8_t len = 0, check = 0, sum;
    unsigned i, tries;
    if (cmd != 0x0001u && cmd != 0x0057u && cmd != 0x0083u)
        return false;
    if (!word(b, 0x3eu, true, &cmd))
        return false;
    for (tries = 0; tries < 3; tries++) {
        b->io.delay_us(b->io.context, 2000u);
        echo = 0;
        if (!word(b, 0x3eu, false, &echo))
            return false;
        if (echo == cmd)
            break;
    }
    if (echo != cmd || !bq_byte(b, 0x61u, false, &len) || len < 4u || len > 36u ||
        (size_t)(len - 4u) > *length)
        return false;
    sum = (uint8_t)((uint8_t)cmd + (uint8_t)(cmd >> 8));
    for (i = 0; i < (unsigned)(len - 4u); i++) {
        if (!bq_byte(b, (uint8_t)(0x40u + i), false, buffer + i))
            return false;
        sum = (uint8_t)(sum + buffer[i]);
    }
    if (!bq_byte(b, 0x60u, false, &check) || check != (uint8_t)(0xffu - sum)) {
        b->communication_fault = BQ_CRC;
        return false;
    }
    *length = (size_t)(len - 4u);
    return true;
}
bool bq_profile_readback(bq_t *b, const bq_profile_entry_t *e, bool write) {
    uint16_t addr = e->address, echo;
    uint8_t v, check, len, sum;
    unsigned i;
    if (e->width < 1 || e->width > 2 || addr < 0x9200u || addr > 0x9400u)
        return false;
    if (!word(b, 0x3eu, true, &addr))
        return false;
    b->io.delay_us(b->io.context, 2000u);
    if (write) {
        sum = (uint8_t)((uint8_t)addr + (uint8_t)(addr >> 8));
        for (i = 0; i < e->width; i++) {
            v = e->bytes[i];
            sum = (uint8_t)(sum + v);
            if (!bq_byte(b, (uint8_t)(0x40u + i), true, &v))
                return false;
        }
        v = (uint8_t)(0xffu - sum);
        if (!bq_byte(b, 0x60u, true, &v))
            return false;
        v = (uint8_t)(e->width + 4u);
        if (!bq_byte(b, 0x61u, true, &v))
            return false;
        b->io.delay_us(b->io.context, 2000u);
        addr = e->address;
        if (!word(b, 0x3eu, true, &addr))
            return false;
        b->io.delay_us(b->io.context, 2000u);
    }
    echo = 0;
    if (!word(b, 0x3eu, false, &echo) || echo != e->address || !bq_byte(b, 0x61u, false, &len) ||
        len < e->width + 4u || len > 36u)
        return false;
    sum = (uint8_t)((uint8_t)addr + (uint8_t)(addr >> 8));
    for (i = 0; i < (unsigned)(len - 4u); i++) {
        if (!bq_byte(b, (uint8_t)(0x40u + i), false, &v))
            return false;
        sum = (uint8_t)(sum + v);
        if (i < e->width && v != e->bytes[i]) {
            b->communication_fault = BQ_CONFIG;
            return false;
        }
    }
    if (!bq_byte(b, 0x60u, false, &check) || check != (uint8_t)(0xffu - sum)) {
        b->communication_fault = BQ_CRC;
        return false;
    }
    return true;
}
void bq_init(bq_t *b, const bq_transport_t *io, uint32_t now) {
    memset(b, 0, sizeof(*b));
    b->io = *io;
    b->phase = BQ_IDENTITY;
    b->entered_ms = now;
    b->balance_logical = -1;
}
static bool scan(bq_t *b, uint32_t now) {
    unsigned i;
    uint16_t mv = 0;
    uint8_t v = 0;
    bool valid = true;
    for (i = 0; i < CELL_COUNT; i++) {
        /* Direct cell1 at0x14;
               channel9=0x24 deliberately skipped, channel10=0x26. */
        if (!word(b, (uint8_t)(0x14u + 2u * (i == 8u ? 9u : i)), false, &mv))
            return false;
        b->monitor.cell_v[i] = (float)(int16_t)mv / 1000.0f;
        if ((int16_t)mv < 0 || mv > 2700u)
            valid = false;
    }
    if (!bq_byte(b, 0x03u, false, &v))
        return false;
    b->monitor.safety_a = v;
    if (!bq_byte(b, 0x05u, false, &v))
        return false;
    b->monitor.safety_b = v;
    if (!bq_byte(b, 0x07u, false, &v))
        return false;
    b->monitor.safety_c = v;
    if (!bq_byte(b, 0x7fu, false, &v))
        return false;
    b->monitor.fet_status = v;
    /* PIN bits express asserted fault (TRM12.2.20), not an auxiliary contact.
     * Healthy physical HIGH under0xA6 must be confirmed with simulator/PA12. */
    b->monitor.permissions_healthy = (v & 0x30u) == 0 && b->monitor.safety_a == 0 &&
                                     b->monitor.safety_b == 0 && b->monitor.safety_c == 0;
    b->monitor.measurements_valid = valid;
    b->monitor.timestamp_ms = now;
    b->last_scan_ms = now;
    if (b->monitor.safety_a & 8u)
        b->monitor.faults |= CELL_OV;
    if (b->monitor.safety_a & 4u)
        b->monitor.faults |= CELL_UV;
    if (b->monitor.safety_b || b->monitor.safety_c)
        b->monitor.faults |= MONITOR_ALERT;
    return valid;
}
static bool balance_write(bq_t *b, uint16_t mask) {
    uint16_t cmd = 0x0083u;
    uint8_t data[2] = {(uint8_t)mask, (uint8_t)(mask >> 8)};
    uint8_t c =
        (uint8_t)(0xffu - (uint8_t)((uint8_t)cmd + (uint8_t)(cmd >> 8) + data[0] + data[1]));
    uint8_t len = 6;
    size_t n = 2;
    uint8_t readback[2];
    if (mask && mask != balance_physical_mask(b->balance_logical))
        return false;
    if (!word(b, 0x3e, true, &cmd) || !bq_byte(b, 0x40, true, data) ||
        !bq_byte(b, 0x41, true, data + 1) || !bq_byte(b, 0x60, true, &c) ||
        !bq_byte(b, 0x61, true, &len))
        return false;
    b->io.delay_us(b->io.context, 2000u);
    return bq_subcommand(b, cmd, readback, &n) && n == 2 && readback[0] == (uint8_t)mask &&
           readback[1] == (uint8_t)(mask >> 8);
}
void bq_tick(bq_t *b, uint32_t now, float temp, bool off, bool sensors_valid) {
    uint16_t status = 0;
    uint8_t data[4] = {0};
    size_t n = sizeof(data);
    uint16_t mfg;
    bool ok = true;
    if (b->phase == BQ_FAILED)
        return;
    switch (b->phase) {
    case BQ_IDENTITY:
        ok = bq_subcommand(b, 0x0001u, data, &n) && n == 2 && data[0] == 0x94 && data[1] == 0x76;
        if (ok)
            b->phase = BQ_ENTER;
        break;
    case BQ_ENTER:
        ok = command_only(b, 0x0090u) && word(b, 0x12u, false, &status) && (status & 1u) != 0;
        if (ok)
            b->phase = BQ_WRITE_PROFILE;
        break;
    case BQ_WRITE_PROFILE:
        ok = bq_profile_readback(b, &bq_profile[b->entry], true);
        if (ok && ++b->entry == bq_profile_count)
            b->phase = BQ_EXIT;
        break;
    case BQ_EXIT:
        ok = command_only(b, 0x0092u) && command_only(b, 0x009au) &&
             word(b, 0x12u, false, &status) && (status & 0xb817u) == 0;
        if (ok) {
            b->phase = BQ_WAIT_SCAN;
            b->entered_ms = now;
            b->initial_por = (status & 8u) != 0;
        }
        break;
    case BQ_WAIT_SCAN:
        ok = word(b, 0x12u, false, &status);
        b->monitor.battery_status = status;
        if (status & 0x20u)
            b->cow_seen = true;
        if (b->cow_seen && (status & 0x20u) == 0)
            b->cow_completed = true;
        if ((status & 0xb817u) != 0)
            ok = false;
        if (ok && now - b->last_scan_ms >= 100u)
            ok = scan(b, now);
        if (ok && b->cow_completed && now - b->entered_ms >= 1500u &&
            b->monitor.measurements_valid && sensors_valid && isfinite(temp)) {
            unsigned i;
            for (i = 0; i < CELL_COUNT; i++)
                if (b->monitor.cell_v[i] < 1.2144f || b->monitor.cell_v[i] > 2.45f)
                    ok = false;
            if (ok) {
                b->monitor.open_wire_observed = true;
                b->phase = BQ_RELEASE;
            }
        }
        if (now - b->entered_ms > 7000u)
            ok = false;
        break;
    case BQ_RELEASE:
        /* Read-before-toggle;
               no blind FET_ENABLE. Refuse test/OTP/PF bits. */
        ok = bq_subcommand(b, 0x0057u, data, &n) && n >= 2;
        mfg = (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
        if (ok && (mfg & 0x00e7u) != 0)
            ok = false;
        if (ok && (mfg & 0x10u) == 0) {
            ok = command_only(b, 0x0022u);
            n = sizeof(data);
            ok = ok && bq_subcommand(b, 0x0057u, data, &n) && (data[0] & 0xf7u) == 0x10u;
        }
        ok = ok && command_only(b, 0x0096u) && scan(b, now) && b->monitor.permissions_healthy;
        if (ok) {
            b->monitor.config_valid = true;
            b->phase = BQ_READY;
        }
        break;
    case BQ_READY:
        ok = word(b, 0x12u, false, &status);
        b->monitor.battery_status = status;
        if ((status & 0xb817u) != 0 || ((status & 8u) != 0) != b->initial_por)
            ok = false;
        if (b->balance_mask) {
            b->monitor.settling = true;
            b->monitor.measurements_valid = false;
            if (!off || !sensors_valid || !isfinite(temp) || temp < 0 || temp > 40 ||
                now - b->balance_started_ms >= 1000u) {
                ok = ok && balance_write(b, 0);
                b->balance_mask = 0;
                b->balance_stop_ms = now;
                if (!off || !sensors_valid || !isfinite(temp) || temp < 0 || temp > 40)
                    b->balance_logical = -1;
            }
        } else if (now - b->balance_stop_ms < 250u) {
            b->monitor.settling = true;
            b->monitor.measurements_valid = false;
        } else {
            b->monitor.settling = false;
            if (ok && now - b->last_scan_ms >= 100u) {
                ok = scan(b, now) && b->monitor.permissions_healthy &&
                     bq_profile_readback(b, &bq_profile[b->entry % bq_profile_count], false);
                b->entry++;
            }
            if (off && sensors_valid && b->monitor.measurements_valid) {
                b->balance_logical = balance_select(&b->monitor, temp, off, b->balance_logical);
                if (b->balance_logical >= 0) {
                    b->balance_mask = balance_physical_mask(b->balance_logical);
                    ok = ok && balance_write(b, b->balance_mask);
                    b->balance_started_ms = now;
                    b->monitor.settling = true;
                    b->monitor.measurements_valid = false;
                }
            }
        }
        break;
    default:
        ok = false;
        break;
    }
    if (!ok || b->monitor.faults) {
        b->monitor.config_valid = false;
        b->monitor.permissions_healthy = false;
        b->monitor.faults |= b->communication_fault ? b->communication_fault : BQ_CONFIG;
        b->phase = BQ_FAILED;
    }
}
