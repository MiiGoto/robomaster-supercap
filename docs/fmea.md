# Preliminary FMEA

2026-10-03。定性分析のみ。Protectionは要求/候補で、実装済みではない。
Severity/occurrence/detectionの数値RPNは故障率・試験根拠がなく未採点(TBD)。閾値・反応時間・遮断能力もTBD。

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| control MCU failure | crash、clock、brownout、stuck PWM、debug halt | uncontrolled current / charge | external watchdog、fault inputs、heartbeat | default OFF、independent hardware trip/latch | watchdog前のenergy、shared supply |
| gate driver failure | UVLO、supply OV、stuck output | gate loss、shoot-through、unwanted conduction | rail/fault monitoring、current trip | enable bias OFF、UVLO、isolation candidate | stuck-high / FET短絡はPWMで停止不可 |
| MOSFET short | overvoltage、thermal、shoot-through | bus↔bank直結またはground短絡 | fast current / voltage異常 | source/bank側energy isolationとfuse候補 | fault clearing energy、DC arc、diode path |
| MOSFET open | bond failure、solder、driver断線 | transfer喪失、他素子過負荷 | current command対feedback不一致 | stop・fault latch | diode熱、局所hotspot |
| current sensor failure | shunt/amp/reference断線、飽和、stuck | incorrect feedback、overcurrent | range/rate/plausibility、independent comparator | inhibit、separate fast trip candidate | shared shunt/reference common failure |
| voltage sensor failure | divider open/short、ADC、reference mismatch | 偽低電圧で過充電 | cell sum/bank相関、range、reference診断 | independent OV、charge inhibit | plausible stuck-low |
| capacitor imbalance | C/leakage/temperature差、balance failure | cell OV/UV/reversal | per-cell min/max/delta | charge inhibit、balance、UV assist stop | monitor tap共通故障、balancer不足 |
| bank overvoltage | loop error、regeneration、sense誤差 | cell損傷・vent | bank/cell sense、independent threshold | charge stop、isolation/energy sink候補 | sink許容power不明、transient overshoot |
| overcurrent | short、bad command、low Vcap、control instability | FET/L/PCB熱、connector arc | fast current、cycle trip候補 | independent inhibit、fuse/isolation | trip前stress、fuse coordination |
| overtemperature | airflow loss、ESR、connector resistance | aging、short/open、火災 | selected hotspot sensors、derating trend | derate→trip、sensor fault診断 | thermal lag、unmonitored hotspot |
| CAN loss | bus-off、disconnect、stale frames | uncontrolled/stale assist budget | timestamp/counter/timeout | inhibit、latched safe mode、explicit rearm | timeout内energy、robot integration影響 |
| input power loss | battery disconnect、brownout | aux loss、cap backfeed、reboot | bus UV、reset cause | gate OFF、reverse flow対策、service discharge | cap側auxが意図せず継続、bleed不能 |
| shorted bank wiring | abrasion、tool、tap short | large discharge、arc | current trip、inspection | bank-sidefault interruption、tap current制限、enclosure | bank内部短絡は外部fuseで止まらない |
| reverse polarity | miswire / connector error | reverse cell stress、FET diode conduction | polarity sensing、mechanical key | blocking候補、禁止connection | failed blocking device |
| precharge failure | bypass welded/open、resistor open、wrong sequence | inrush / no startup | ΔV/current/time、main feedback | timeout latch、bypass inhibit | contact状態の診断限界 |
| bleed/discharge failure | resistor open、switch stuck OFF、aux loss | OFF後energy残留 | independent voltage measurement、rebound check | alternate service discharge、lockout | tool/測定ミス、cell残留 |
| discharge stuck ON | switch short、firmware fault | unnecessary熱 / cell UV | voltage fall/current/temp | limit thermal energy、cell UV監視 | aux不要のpassive pathは遮断困難 |
| temperature sensor failure | NTC断線/短絡、ADC故障 | 偽低温で運転継続 | open/short/range診断 | fault inhibit / conservative derating | 同一ADC common failure |
| reverse current | FPWM、body diode、source collapse | robot/batteryへの逆給電 | signed current / bus state | zero-current guard、blocking/isolation候補 | PWM OFFでdiode conduction |
| connector opens under load | vibration、manual removal | arc、bus transient、contact heating | continuity/voltage異常、inspection | strain relief、load OFF手順、arc防護 | sudden mechanical failure |
| PCB overheating | via不足、bad solder、return loop、aging | delamination / short / fire | thermal test、current and hotspot | thermal/current derating、layout review | 隠れたcontact hotspot |

最大riskはstored energyの短絡供給、single cell過電圧、shorted switchの遮断不能、sensor共通故障、shutdown後残留。
各riskは検出不能ケースを含めTask 2 gateでレビューし、未解決を消さない。
