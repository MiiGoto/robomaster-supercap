#include "sc_sensing.h"

#include <math.h>

#include "sc_config.h"

void sc_cal_default(sc_cal_t *cal)
{
    cal->icap_zero_v = 0.0f;
    cal->vnode_gain = 1.0f;
    cal->vin_gain = 1.0f;
    cal->iin_gain = 1.0f;
    cal->icap_gain = 1.0f;
}

float sc_ntc_celsius(float v_adc, float vdda)
{
    /* NTC from 3V3 (= VDDA) to the node, RFIX from the node to GND */
    if (v_adc <= 0.001f || v_adc >= vdda - 0.001f) {
        return NAN;
    }
    float r_ntc = SC_NTC_RFIX * (vdda / v_adc - 1.0f);
    float inv_t = 1.0f / 298.15f + logf(r_ntc / SC_NTC_R25) / SC_NTC_B;
    return 1.0f / inv_t - 273.15f;
}

void sc_sensing_convert(const sc_adc_raw_t *raw, uint16_t vrefint_cal, const sc_cal_t *cal, sc_meas_t *out)
{
    float vdda = 0.0f;
    if (raw->vrefint > 0u) {
        vdda = (SC_VREFINT_CAL_MV / 1000.0f) * (float)vrefint_cal / (float)raw->vrefint;
    }
    const float lsb = vdda / 4095.0f;
    out->vdda = vdda;
    out->vnode = (float)raw->vnode * lsb * SC_DIV_VNODE * cal->vnode_gain;
    out->vin = (float)raw->vin * lsb * SC_DIV_VIN * cal->vin_gain;
    out->iin = (float)raw->iin * lsb / SC_IIN_V_PER_A * cal->iin_gain;
    float zero = (cal->icap_zero_v > 0.0f) ? cal->icap_zero_v : 0.5f * vdda;
    out->icap = ((float)raw->icap * lsb - zero) / SC_ICAP_V_PER_A * cal->icap_gain;
    out->temp_c = sc_ntc_celsius((float)raw->temp * lsb, vdda);
    out->pin = out->vin * out->iin;
    bool vdda_ok = (vdda >= SC_VDDA_MIN) && (vdda <= SC_VDDA_MAX);
    bool t_ok = !isnan(out->temp_c) && out->temp_c > SC_T_SENSOR_MIN_C && out->temp_c < SC_T_SENSOR_MAX_C;
    out->valid = vdda_ok && t_ok;
}
