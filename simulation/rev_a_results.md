# Prototype Rev A selected-candidate calculations

ASSUMPTION — MUST VERIFY ON PROTOTYPE. CSD18540Q5B, XAL1510-223MED22uH,
WSK25123L000FEA3mR; 180/200kHz. CSD18563Q5A /15uH alternatives remain in component_results.md.
Same eta0.9, ESR0.18ohm, L tolerance0.8*bias0.8, hotRDS factor1.6, winding80C, tr+tf40ns.
Driver12V; Qg53nC measured at10V reused as a LOWER-FIDELITY assumption, not a12V bound.
Subtotal excludes core/Coss/Qrr/deadtime/aux/connector and bank ESR; no efficiency guarantee.
Model is single-active-leg CCM; overlap/equal-rail modulation, startup and fault not modeled.

| fs kHz | bus / rest cap V | request W | delivered W | cap A | bus A | IL RMS / peak A | ripple App | loss subtotal W |
|---|---|---|---|---|---|---|---|---|
| 180 | 22/12 | 80 | 76.032 | 8.000 | 3.456 | 8.024/9.083 | 2.167 | 3.852 |
| 180 | 22/12 | 120 | 106.272 | 12.000 | 4.831 | 12.016/13.073 | 2.146 | 7.120 |
| 180 | 22/22.05 | 80 | 80.000 | 4.173 | 3.636 | 4.174/4.307 | 0.268 | 1.725 |
| 180 | 22/22.05 | 120 | 120.000 | 6.379 | 5.455 | 6.380/6.585 | 0.412 | 2.880 |
| 180 | 26/12 | 80 | 76.032 | 8.000 | 2.924 | 8.032/9.237 | 2.474 | 4.076 |
| 180 | 26/12 | 120 | 106.272 | 12.000 | 4.087 | 12.020/13.207 | 2.413 | 7.449 |
| 180 | 26/22.05 | 80 | 80.000 | 4.173 | 3.077 | 4.196/4.933 | 1.520 | 1.839 |
| 180 | 26/22.05 | 120 | 120.000 | 6.379 | 4.615 | 6.396/7.188 | 1.617 | 3.045 |
| 200 | 22/12 | 80 | 76.032 | 8.000 | 3.456 | 8.020/8.975 | 1.950 | 4.042 |
| 200 | 22/12 | 120 | 106.272 | 12.000 | 4.831 | 12.013/12.966 | 1.931 | 7.380 |
| 200 | 22/22.05 | 80 | 80.000 | 4.173 | 3.636 | 4.174/4.294 | 0.241 | 1.849 |
| 200 | 22/22.05 | 120 | 120.000 | 6.379 | 5.455 | 6.380/6.564 | 0.371 | 3.044 |
| 200 | 26/12 | 80 | 76.032 | 8.000 | 2.924 | 8.026/9.113 | 2.227 | 4.291 |
| 200 | 26/12 | 120 | 106.272 | 12.000 | 4.087 | 12.016/13.086 | 2.172 | 7.746 |
| 200 | 26/22.05 | 80 | 80.000 | 4.173 | 3.077 | 4.192/4.857 | 1.368 | 1.976 |
| 200 | 26/22.05 | 120 | 120.000 | 6.379 | 4.615 | 6.393/7.107 | 1.455 | 3.227 |

## 40W charge-input corner calculation

| Bus / rest cap V | Actual input W | Bus A | Signed cap A | Stored W | ESR W | Converter W |
|---|---|---|---|---|---|---|
| 22/12 | 40.000 | 1.818 | -2.876 | 34.511 | 1.489 | 4.000 |
| 22/22.05 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 26/12 | 40.000 | 1.538 | -2.876 | 34.511 | 1.489 | 4.000 |
| 26/22.05 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

At22.05V rest ceiling this model stops charge; cell limits can stop earlier. Power conservation checked in W, signed capacitor charging current is negative.


## Sanity checks and proposed setting arithmetic

- Local-link precharge100R/470uF/26V: I0=0.260A, P0=6.760W, resistor energy=0.15886J, t95=0.14080s. Loads ignored.
- Dump100R, +30%C: initial=4.862W, energy to1V=1752.120J, ideal time=2234.1s.1V is only proposed inspection/service investigation target.
- Permanent10k bleed +30%C: initial=0.04862W, time to1V=62.06h; OFF is not safe.
- Available nominal ideal useful energy950.5625J; +30%C1235.73125J. Stored total at22.05V1350.5625J nominal. External dump thermally rated separately.
- 12A cell-bank ESR loss=25.92W initially; 2x aging51.84W.1s/30s pulse-only mean=0.864/1.728W, excludes normal current and all other losses.
- WSK2512 1W70C rating is board/ambient dependent.3mR at12A=0.432W; modeled IL RMS≈12.02A gives≈0.433W. Pulse/derating are not yet accepted.
- IL comparator nominal threshold3.3*10k/(29.4k+10k)=0.83756V -> 13.9594A with gain20/3mR. Not coordinated maximum fault current.
- Port INA293A1/TLV3202 thresholds: BUS3.3*10/68.7/0.06=8.006A; CAP3.3*10/39.4/0.06=13.959A. Tolerance/offset/delay/overshoot unbudgeted; INA301 rejected for40V absmax versus45.4V TVS clamp.
- Independent TLV4311.24V reference: bus OV221k/10k ->28.644V; bus UV154k/10k ->20.336V; bank OV172k/10k ->22.568V nominal. These are hardware backup proposals, distinct from operating window.
- Loaded voltage dividers including100k ADC drain: bus36V->2.46555V; cap24.3V->2.13798V. Clamp2.7V plus diode drop/mux3.6V need transient test.2uA off-leakage *100k=0.2V proposed bound.
- Current midscale1.65V: BUSgain50 +-8A->0.45..2.85V; CAP/ILgain20 +-20A->0.45..2.85V; ideal12-bit steps5.37/13.43mA. Actual clamp/swing can reduce range.
- Approximate beta NTC trip including100k ADC load: FET/L->69.47C; BANK->53.67C. Mux OFF removes this load, so threshold is state-dependent; manufacturer R/T calibration and partial-power tests mandatory.
- Fast IL shutdown estimate must include INA293 dynamic response, comparator, logic, latch/AND, driver/gate and Lmin. No guaranteed max latency is inferred from bandwidth or typical delays.
- For a fault: excursion roughly Vfault/Lmin*tclear. At26V/14.08uH, 1us adds1.847A. This is NOT an accepted1us clearing time, and saturation worsens it.
- Qg53nC / bootstrap effective200nF =0.265V charge droop before leakage/bias.470nF nominal needs DC-bias capacitance, duty/refresh and UVLO verification.
- Aux Type3 ripple:12V300kHz, RA1M/CA1nF gives~20mV at24V;3.3V~301kHz, RA475k/CA1nF gives~20mV. CA exceeds10/(fs*RFB_parallel); CB100pF permits provisional settling >=270/52.5us. Datasheet equations only; stability not simulated.
- Peak duration and repetition are adjustable assumptions; existing runtime calculations are not permission for those pulses.
