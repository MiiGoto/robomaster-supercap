#include "sc_canproto.h"

#include <math.h>

static uint16_t u16_sat(float v)
{
    if (!(v > 0.0f)) {
        return 0u;
    }
    if (v > 65535.0f) {
        return 65535u;
    }
    return (uint16_t)lrintf(v);
}

static int16_t i16_sat(float v)
{
    if (isnan(v)) {
        return INT16_MIN;
    }
    if (v > 32767.0f) {
        return 32767;
    }
    if (v < -32767.0f) {
        return -32767;
    }
    return (int16_t)lrintf(v);
}

static void w16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

void sc_can_pack_status(const sc_can_status_t *s, uint8_t out[8])
{
    w16(&out[0], u16_sat(s->vin * 100.0f));
    w16(&out[2], u16_sat(s->vcap * 100.0f));
    w16(&out[4], u16_sat(s->iin * 100.0f));
    w16(&out[6], u16_sat(s->p_target * 100.0f));
}

void sc_can_pack_ext(const sc_can_ext_t *s, uint8_t out[8])
{
    out[0] = s->state;
    out[1] = s->faults;
    w16(&out[2], (uint16_t)i16_sat(s->icap * 100.0f));
    w16(&out[4], (uint16_t)i16_sat(s->temp_c * 10.0f));
    out[6] = s->energy_pct;
    out[7] = s->flags;
}

bool sc_can_parse_cmd(const uint8_t *d, uint8_t len, float *p_limit_w)
{
    if (len < 2u) {
        return false;
    }
    uint16_t raw = (uint16_t)(d[0] | ((uint16_t)d[1] << 8));
    *p_limit_w = (float)raw / 100.0f;
    return true;
}
