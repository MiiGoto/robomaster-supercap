#include "sc_referee.h"

#include <string.h>

/* CRC8: DJI referee (Maxim/Dallas, reflected poly 0x8C, init 0xFF) */
uint8_t sc_crc8(const uint8_t *p, uint32_t n)
{
    uint8_t crc = 0xFFu;
    while (n--) {
        crc ^= *p++;
        for (int i = 0; i < 8; i++) {
            crc = (crc & 1u) ? (uint8_t)((crc >> 1) ^ 0x8Cu) : (uint8_t)(crc >> 1);
        }
    }
    return crc;
}

/* CRC16: DJI referee (reflected poly 0x8408, init 0xFFFF, no final xor), sent low byte first */
uint16_t sc_crc16(const uint8_t *p, uint32_t n)
{
    uint16_t crc = 0xFFFFu;
    while (n--) {
        crc ^= *p++;
        for (int i = 0; i < 8; i++) {
            crc = (crc & 1u) ? (uint16_t)((crc >> 1) ^ 0x8408u) : (uint16_t)(crc >> 1);
        }
    }
    return crc;
}

void sc_referee_init(sc_referee_t *r)
{
    memset(r, 0, sizeof(*r));
}

static uint16_t rd16(const uint8_t *p)
{
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}

static void handle(sc_referee_t *r, uint16_t cmd, const uint8_t *d, uint16_t len, uint32_t now)
{
    if (cmd == 0x0201u && len >= 13u) {
        r->data.chassis_power_limit = rd16(&d[10]);
        r->data.chassis_output_on = (d[12] & 0x02u) != 0u;
        r->data.t_status_ms = now;
        r->data.have_status = true;
    } else if (cmd == 0x0202u && len >= 10u) {
        r->data.buffer_energy = rd16(&d[8]);
        r->data.t_power_ms = now;
        r->data.have_power = true;
    }
}

/* drop the first byte and restart at the next 0xA5 already in the buffer */
static void resync(sc_referee_t *r)
{
    uint16_t i = 1u;
    while (i < r->idx && r->buf[i] != 0xA5u) {
        i++;
    }
    uint16_t n = (uint16_t)(r->idx - i);
    memmove(r->buf, &r->buf[i], n);
    r->idx = n;
    r->need = 0u;
}

/* header check once 5 bytes are present; returns false (and resyncs) on a bad header */
static bool header_ok(sc_referee_t *r)
{
    while (r->idx >= 5u && r->need == 0u) {
        uint16_t len = rd16(&r->buf[1]);
        if (sc_crc8(r->buf, 4u) == r->buf[4] && len <= SC_REF_MAX_DATA) {
            r->need = (uint16_t)(5u + 2u + len + 2u);
            return true;
        }
        r->data.crc_errors++;
        resync(r);
    }
    return r->need != 0u;
}

uint16_t sc_referee_feed(sc_referee_t *r, uint8_t b, uint32_t now_ms)
{
    if (r->idx == 0u && b != 0xA5u) {
        return 0u;
    }
    if (r->idx >= sizeof(r->buf)) {
        r->idx = 0u;
        r->need = 0u;
        return 0u;
    }
    r->buf[r->idx++] = b;
    if (!header_ok(r) || r->idx < r->need) {
        return 0u;
    }
    uint16_t n = r->need;
    uint16_t crc = sc_crc16(r->buf, (uint32_t)n - 2u);
    if (crc != rd16(&r->buf[n - 2u])) {
        r->data.crc_errors++;
        resync(r);
        (void)header_ok(r);
        return 0u;
    }
    uint16_t cmd = rd16(&r->buf[5]);
    handle(r, cmd, &r->buf[7], (uint16_t)(n - 9u), now_ms);
    r->data.frames_ok++;
    r->idx = 0u;
    r->need = 0u;
    return cmd;
}
