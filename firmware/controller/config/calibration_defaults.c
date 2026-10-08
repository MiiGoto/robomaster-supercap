#include "rev_a.h"
#include <string.h>
/* Rev A schematic-derived factory coefficients. UNVERIFIED until bench calibration. */
void calibration_defaults(calibration_t *c) {
    unsigned i;
    float bus_bottom = 1.0f / (1.0f / 5100.0f + 1.0f / 100000.0f);
    float cap_bottom = 1.0f / (1.0f / 6800.0f + 1.0f / 100000.0f);
    memset(c, 0, sizeof(*c));
    c->version = 1;
    c->adc_reference_v = 3.3f;
    for (i = 0; i < ADC_COUNT; i++)
        c->gain[i] = 1;
    c->gain[BUS_V] = c->gain[BUS_RAW] = (66000.0f + bus_bottom) / bus_bottom;
    c->gain[CAP_V] = c->gain[CAP_RAW] = (66000.0f + cap_bottom) / cap_bottom;
    /* INA240A2 bus gain50, A1 cap/IL gain20, 3mohm;
        100R/100k loading. */
    c->gain[BUS_I] = 1.001f / 0.15f;
    c->gain[CAP_I] = c->gain[IL_I] = 1.001f / 0.06f;
    c->offset[BUS_I] = c->offset[CAP_I] = c->offset[IL_I] = -1.65f / 1.001f;
    c->ntc_beta = 3977.0f;
    c->ntc_r25 = 10000.0f;
    /* PROVISIONAL CONTROL GAINS — BENCH TUNING REQUIRED.
     * Voltage-command PI: Kp=L*2*pi*1kHz, Ki=Kp*2*pi*100Hz;
        not stability proof. */
    c->kp = 0.13823f;
    c->ki = 86.85f;
    c->verified = false;
    c->crc = crc32(c, offsetof(calibration_t, crc));
}
