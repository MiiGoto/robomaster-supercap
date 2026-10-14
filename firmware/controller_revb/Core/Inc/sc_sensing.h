/* Raw ADC counts -> physical values (portable, no HAL). */
#ifndef SC_SENSING_H
#define SC_SENSING_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint16_t vnode;     /* PA0 ADC1_IN1 */
    uint16_t vin;       /* PA1 ADC1_IN2 (VIN_C) */
    uint16_t temp;      /* PA2 ADC1_IN3 */
    uint16_t iin;       /* PA3 ADC1_IN4 */
    uint16_t vrefint;   /* ADC1 VREFINT */
    uint16_t icap;      /* PA6 ADC2_IN3 */
} sc_adc_raw_t;         /* 12-bit averages */

typedef struct {
    float vdda;         /* V */
    float vnode;        /* V, bank / chassis node */
    float vin;          /* V, input after the series PMOS */
    float iin;          /* A, input current (>= 0) */
    float icap;         /* A, + = into the bank */
    float temp_c;       /* C, NTC near the power stage */
    float pin;          /* W, vin * iin */
    bool  valid;        /* VDDA and temperature plausible */
} sc_meas_t;

typedef struct {
    float icap_zero_v;  /* INA240 bidirectional offset; 0 = use VDDA/2 */
    float vnode_gain;   /* calibration multipliers (1.0 = nominal) */
    float vin_gain;
    float iin_gain;
    float icap_gain;
} sc_cal_t;

void  sc_cal_default(sc_cal_t *cal);
void  sc_sensing_convert(const sc_adc_raw_t *raw, uint16_t vrefint_cal, const sc_cal_t *cal, sc_meas_t *out);
float sc_ntc_celsius(float v_adc, float vdda);

#endif
