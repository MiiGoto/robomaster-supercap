# Task 3 component sensitivity — not an approved rating

Inputs: eta90% (Task 2), cap12–22.05 V, bus22/26 V, request80/120 W,
cap clamps8/12 A, hot RDS factor1.6, winding80°C, tr+tf40 ns.
L effective = nominal ×0.8 tolerance ×0.8 assumed DC bias.
Neither temperature nor bias factor is predicted or guaranteed.

| FET / L / fs | Bus / cap open / request | Output W | Cap A | IL rms / peak A | Ripple A pp | FET conduction / overlap / gate W | L Cu / shunts W | Subtotal W |
|---|---|---|---|---|---|---|---|---|
| CSD18540Q5B / 22 uH / 100 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.176 / 4.415 | 0.482 | 0.123 / 0.367 / 0.212 | 0.339 / 0.144 | 1.186 |
| CSD18540Q5B / 22 uH / 100 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.383 / 6.750 | 0.741 | 0.287 / 0.561 / 0.212 | 0.793 / 0.334 | 2.186 |
| CSD18540Q5B / 22 uH / 100 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.103 / 10.227 | 4.454 | 0.462 / 0.832 / 0.212 | 1.278 / 0.415 | 3.198 |
| CSD18540Q5B / 22 uH / 100 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.065 / 14.172 | 4.344 | 1.025 / 1.248 / 0.212 | 2.833 / 0.919 | 6.236 |
| CSD18540Q5B / 22 uH / 200 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.174 / 4.294 | 0.241 | 0.123 / 0.735 / 0.424 | 0.339 / 0.144 | 1.764 |
| CSD18540Q5B / 22 uH / 200 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.380 / 6.564 | 0.371 | 0.287 / 1.123 / 0.424 | 0.792 / 0.333 | 2.959 |
| CSD18540Q5B / 22 uH / 200 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.026 / 9.113 | 2.227 | 0.453 / 1.664 / 0.424 | 1.253 / 0.411 | 4.206 |
| CSD18540Q5B / 22 uH / 200 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.016 / 13.086 | 2.172 | 1.017 / 2.496 / 0.424 | 2.810 / 0.915 | 7.661 |
| CSD18540Q5B / 15 uH / 100 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.178 / 4.527 | 0.707 | 0.123 / 0.367 / 0.212 | 0.263 / 0.144 | 1.110 |
| CSD18540Q5B / 15 uH / 100 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.387 / 6.922 | 1.087 | 0.287 / 0.561 / 0.212 | 0.615 / 0.334 | 2.009 |
| CSD18540Q5B / 15 uH / 100 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.219 / 11.266 | 6.532 | 0.476 / 0.832 / 0.212 | 1.019 / 0.420 | 2.959 |
| CSD18540Q5B / 15 uH / 100 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.140 / 15.185 | 6.371 | 1.038 / 1.248 / 0.212 | 2.223 / 0.924 | 5.644 |
| CSD18540Q5B / 15 uH / 200 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.175 / 4.350 | 0.354 | 0.123 / 0.735 / 0.424 | 0.263 / 0.144 | 1.688 |
| CSD18540Q5B / 15 uH / 200 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.381 / 6.651 | 0.543 | 0.287 / 1.123 / 0.424 | 0.614 / 0.333 | 2.781 |
| CSD18540Q5B / 15 uH / 200 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.055 / 9.633 | 3.266 | 0.457 / 1.664 / 0.424 | 0.979 / 0.412 | 3.936 |
| CSD18540Q5B / 15 uH / 200 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.035 / 13.593 | 3.185 | 1.020 / 2.496 / 0.424 | 2.184 / 0.917 | 7.041 |
| CSD18563Q5A / 22 uH / 100 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.176 / 4.415 | 0.482 | 0.379 / 0.367 / 0.080 | 0.339 / 0.144 | 1.310 |
| CSD18563Q5A / 22 uH / 100 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.383 / 6.750 | 0.741 | 0.886 / 0.561 / 0.080 | 0.793 / 0.334 | 2.654 |
| CSD18563Q5A / 22 uH / 100 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.103 / 10.227 | 4.454 | 1.429 / 0.832 / 0.080 | 1.278 / 0.415 | 4.033 |
| CSD18563Q5A / 22 uH / 100 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.065 / 14.172 | 4.344 | 3.168 / 1.248 / 0.080 | 2.833 / 0.919 | 8.247 |
| CSD18563Q5A / 22 uH / 200 kHz | 22 / 22.05 / 80 | 80.000 | 4.173 | 4.174 / 4.294 | 0.241 | 0.379 / 0.735 / 0.160 | 0.339 / 0.144 | 1.757 |
| CSD18563Q5A / 22 uH / 200 kHz | 22 / 22.05 / 120 | 120.000 | 6.379 | 6.380 / 6.564 | 0.371 | 0.886 / 1.123 / 0.160 | 0.792 / 0.333 | 3.294 |
| CSD18563Q5A / 22 uH / 200 kHz | 26 / 12 / 80 | 76.032 | 8.000 | 8.026 / 9.113 | 2.227 | 1.402 / 1.664 / 0.160 | 1.253 / 0.411 | 4.890 |
| CSD18563Q5A / 22 uH / 200 kHz | 26 / 12 / 120 | 106.272 | 12.000 | 12.016 / 13.086 | 2.172 | 3.142 / 2.496 / 0.160 | 2.810 / 0.915 | 9.523 |

Subtotal excludes core/Coss/Qrr/deadtime/connector/aux losses.
Partial efficiency is an optimistic accounting result, not a converter target.
Near-equal rail switching and startup/regen/short are outside this CCM model.
Inductor ripple is not directly the capacitor-module port ripple; DC-link and PWM require separate validation.
12 V / 120 W request is clipped to106.272 W before component loss assessment.

## RC scenarios (Assumption, not component values)

- Empty local470 uF link,26 V,R=47 ohm: I0=0.553 A, P0=14.383 W,Eres=0.1589 J, t95=0.0662 s. Loads/parasitics/fault pulse not modeled.
- Empty local470 uF link,26 V,R=100 ohm: I0=0.260 A, P0=6.760 W,Eres=0.1589 J, t95=0.1408 s. Loads/parasitics/fault pulse not modeled.
- Bank22.05→1 V,R=100 ohm: P0=4.862 W, E=1347.785 J,t=1718.5 s. 1 V is inspection reference, not approved service-safe threshold.
- Bank22.05→1 V,R=1000 ohm: P0=0.486 W, E=1347.785 J,t=17185.1 s. 1 V is inspection reference, not approved service-safe threshold.
