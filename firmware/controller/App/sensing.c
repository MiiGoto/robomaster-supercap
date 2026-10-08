#include "rev_a.h"
#include <math.h>
#include <string.h>
float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }
uint8_t crc8(const uint8_t *data, size_t n) {
    uint8_t c = 0;
    size_t i;
    unsigned b;
    for (i = 0; i < n; i++) {
        c ^= data[i];
        for (b = 0; b < 8; b++)
            c = (uint8_t)((c & 0x80u) ? ((unsigned)c << 1) ^ 7u : (unsigned)c << 1);
    }
    return c;
}
uint32_t crc32(const void *data, size_t n) {
    const uint8_t *p = data;
    uint32_t c = 0xffffffffu;
    size_t i;
    unsigned j;
    for (i = 0; i < n; i++) {
        c ^= p[i];
        for (j = 0; j < 8; j++)
            c = (c >> 1) ^ ((c & 1u) ? 0xedb88320u : 0u);
    }
    return ~c;
}
bool calibration_valid(const calibration_t *c) {
    unsigned i;
    if (c->version != 1u || !c->verified || c->crc != crc32(c, offsetof(calibration_t, crc)) ||
        !isfinite(c->adc_reference_v) || c->adc_reference_v < 3.0f || c->adc_reference_v > 3.6f ||
        !isfinite(c->kp) || !isfinite(c->ki) || c->kp <= 0 || c->ki <= 0 || c->kp > 2 ||
        c->ki > 1000 || !isfinite(c->ntc_beta) || c->ntc_beta < 3000 || c->ntc_beta > 5000 ||
        !isfinite(c->ntc_r25) || c->ntc_r25 < 5000 || c->ntc_r25 > 20000)
        return false;
    for (i = 0; i < ADC_COUNT; i++)
        if (!isfinite(c->gain[i]) || c->gain[i] <= 0 || c->gain[i] > 100 || !isfinite(c->offset[i]))
            return false;
    return true;
}
float sensors_ntc_c(uint16_t code, const calibration_t *c) {
    float ratio, r;
    if (code <= 16u || code >= 4000u)
        return NAN;
    ratio = (float)code / 4095.0f;
    /* 10k pullup, NTC ||100k ADC drain. Remove the parallel loading first. */
    r = 10000.0f * ratio / (1.0f - ratio);
    if (r >= 100000.0f)
        return NAN;
    r = 1.0f / (1.0f / r - 1.0f / 100000.0f);
    return 1.0f / (1.0f / 298.15f + logf(r / c->ntc_r25) / c->ntc_beta) - 273.15f;
}
void sensors_convert(sensors_t *s, const calibration_t *c) {
    unsigned i;
    s->valid = true;
    for (i = 0; i < ADC_COUNT; i++) {
        if (s->raw[i] > 4095u)
            s->valid = false;
        if (i >= TEMP_FET_CH && i <= TEMP_BANK_CH)
            s->value[i] = sensors_ntc_c(s->raw[i], c) * c->gain[i] + c->offset[i];
        else
            s->value[i] =
                ((float)s->raw[i] * c->adc_reference_v / 4095.0f + c->offset[i]) * c->gain[i];
        if (!isfinite(s->value[i]))
            s->valid = false;
    }
    for (i = BUS_I; i <= IL_I; i++)
        if (s->raw[i] < 32u || s->raw[i] > 4063u)
            s->valid = false;
}
float stored_energy_j(float v) { return isfinite(v) && v > 0 ? 0.5f * (50.0f / 9.0f) * v * v : 0; }
float usable_energy_j(float v) {
    return clampf(stored_energy_j(v) - stored_energy_j(12), 0, 950.5625f);
}
float soe_percent(float v) { return 100.0f * usable_energy_j(v) / 950.5625f; }
uint16_t balance_physical_mask(int logical) {
    return logical >= 0 && logical < 9 ? (uint16_t)(1u << (logical == 8 ? 9 : logical)) : 0u;
}
int balance_select(const monitor_t *m, float t, bool off, int previous) {
    unsigned i, high = 0;
    float lo = 100, hi = 0;
    if (!off || !m->config_valid || !m->measurements_valid || !isfinite(t) || t < 0 || t > 40)
        return -1;
    for (i = 0; i < CELL_COUNT; i++) {
        float v = m->cell_v[i];
        if (!isfinite(v) || v < 2.3f || v > 2.45f)
            return -1;
        if (v < lo)
            lo = v;
        if (v > hi) {
            hi = v;
            high = i;
        }
    }
    if (previous >= 0 ? hi - lo <= 0.010001f : hi - lo < 0.019999f)
        return -1;
    return (int)high;
}
