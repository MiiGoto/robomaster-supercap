# Clearance approval update — 2026-10-04

39対象ICの内部fine-pitchパッド間0.15 mmをユーザー承認に基づき許容し、その他の銅箔間隔は0.20 mm以上を維持した。DRCの寸法・間隔違反0/0、未接続935本。[検証記録](pcb_rev_a_validation.md)を現状として優先する。以下は変更前の経緯を含む。

# PCB engineering authorized — 2026-10-04

ユーザーがsurge・OC遮断時間・fuse/接触器協調・熱・放電時間の実測前にPCB配置/配線へ進むことを明示承認した。[現行PCB記録](pcb_rev_a.md)を優先する。未実測の項目はPrototype Assumptionとして保持し、製造/通電/性能保証にはしない。以下の「PCB未承認/開始しない」は過去時点の記録として残す。

## PCB-specific residual risks — 2026-10-04

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| Power copper overheating |Provisional necks/inner SW routing/via concentration |Loss,open circuit or damaged laminate |Layer/width audit,IR and temperature testing later |Current clamp and thermal shutdown retained |Partial routes are not accepted for current capacity;manual power routing required |
| Sensing/kill noise coupling |Kelvin paths on reference layer,return cuts,large switching loops |Incorrect current estimate,spurious fault or delayed kill |Close-up route review;later low-energy waveform tests |Independent fault latch/default-OFF logic retained |935 native unconnected edges prevent functional PCB claims |
| Harness misconnection |Unkeyed solder wire lands and external assemblies |Reverse polarity,tap fault or protection bypass |Named-net assembly map,independent continuity/polarity inspection |External tap resistors,fuses and manual disconnect retained |No assembled harness or fabrication release;fixture strain relief required |
| Fine-pitch fabrication defect |0.15 mm library gaps versus0.20 mm project hard minimum |Copper bridge or unreliable assembly |218 retained DRC clearance errors;fabricator/package review |No DRC exclusions or minimum reduction applied |Explicit process/rule decision unresolved |

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A FMEA additions (current architecture)

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| Cell OV / imbalance |leakage/mismatch/config wrong|cell damage|BQ per-cell/ADC bank|autonomous configured DCHG/DDSG + latch|RAM profile selected but not programmed/read back;slow trim |
| Cell open-wire |tap break/short|false cell reading/short energy|BQ open-wire + plausibility|charge inhibit/tap series|source/onboard1k tap resistors selected;harness shorts/open-wire settling must be tested |
| Overcurrent / L saturation |short/load/control error|rapid heating/current rise|INA293 pairs/TLV3202|latch/PWM AND/EN/FLT1|trip~12A with±7% planning allowance;required0.5us clearing/saturation unverified |
| MOSFET short |surge/heat/shoot-through|diode/short reverse path|port/current/rail faults|external disconnect/fuse candidates|DC breaking coordination not approved |
| MOSFET open |bond/gate failure|diode stress/loss of control|command-current mismatch|latched inhibit|firmware absent, residual IL energy |
| Driver failure |bias/glitch/stuck output|uncommanded FET|rail window/OC|EN+input kill+external isolation|stuck output ignores logic; actual ringing |
| Sensor failure |shared shunt/reference/open input|false safe current/temp|independent fast front end + plausibility|hardware windows/latch|shared-element failures, firmware absent |
| MCU crash / CAN loss |software/link failure|stale assist request|external watchdog/lease|default-off reset/latch|unconditional heartbeat defeats watchdog; lease unimplemented |
| Thermal fault |bank ESR/core/poor cooling|cell/FET/L overheating|three NTC + hardware windows|disable/contact release|probe lag, thresholds assumed, enclosure unknown |
| Precharge failure |welded bypass/open resistor|inrush/failed start|raw/link ΔV + feedback/timeout|NO paths/upstream isolate|firmware interlock/pulse test absent |
| Discharge failure |aux loss/open dump/short Q|energy remains or prolonged heat|meter/time/NTC/LED|permanent bleed + service tool|LED dark misleading,62h bleed, tool/rebound unverified |
| Auxiliary failure |UV/OV/sequencing|logic/gate unsafe/dump unavailable|PG/supervisor/driver window|latch clear and default-off coils|external actuator rail unresolved, partial-power injection |

Fault taxonomy proposal: WARNING (approach thermal/energy boundary), RECOVERABLE (startup/precharge refused with sources safe), LATCHED (OC/OV/UV/temp/CAN lease), CRITICAL (suspected FET/contact short, failed discharge/monitor provisioning). Clear/rearm requires supervised reason; no automatic restart. Categories are architecture requirements, not implemented firmware.


## Historical records (preserved)

# Task 4 prospective PCB risks — no placement yet

次表は配置前のrisk register。Protectionは未実装要求、配置によって実際に発生した不具合ではない。

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| MOSFET overheating | narrow thermal path/airflow loss | short/fire | hot junction estimate + thermal validation | copper/thermal strategy + derate/trip | boardtemp≠junction |
| inductor overheating | core/Cu loss/hotbias | L低下→OC | winding/core temperature/ripple | Lhot margin/airflow/OC | coreloss未算入 |
| shunt local heating | pulse/RMS/bottleneck | drift/open | Kelvin error/temp | ratedpulse/thermalspread | nearbyamp tempdrift |
| connector heating | contact/cable/retention | arc/melt | temperature/drop/inspection | keying/retention/derating | vibration/aging |
| copper bottleneck | neck/via/pad current crowding | localburn | rule/thermal/currentpath review | area/return/via sharing検証 | RMS/peak不明 |
| misleading NTC position | heat lag/remote sensor | delayedtrip | thermal mapping/fault tests | representative hotspot placement | unmonitored hotspot |
| sensing noise | SW/L/return coupling | control/fault誤動作 | synchronized sample/noise test | Kelvin/analog zone/reference continuity | common reference fault |
| gate ringing | long gate/return loop | falseON/shootthrough | differentialVGS measurement | drivernearFET/localreturn/deadtime | parasitic transient未検証 |

---

# Task 3 candidate review FMEA additions

Protection列は未実装要求。各故障はTask 2表と併せて扱い、回路ERCや保護検証の完了を意味しない。

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| slow OC clearing | EN-only kill/amp settling/blanking | I上昇、15 A port超過/半導体stress | measured end-to-end delay/current | independent comparator→latch→input clamp+timer fault、EN backup | maxdelay/source impedance/Ttrip未確定 |
| shunt open / short | solder/crack/bridge | power interruption/amp overstress or hidden current | redundant port/IL consistency、diagnostic range | no rearm、independent source interruption | 共用shuntのsingle-point blind fault |
| sense amplifier stuck / rail | aux/reference/CM transient | false current limit | range/command consistency/reference check | separate fast front-end要求 | amp共用ならOCも失敗 |
| divider open / short | resistor/ADC clamp damage | false lowV/ADC overvoltage | independent OV/cell sum/range | charge inhibit/ADC injection protection | divider/OV共通reference |
| precharge bypass stuck ON | FETshort/contact weld | insertion inrush | isolation/ΔV/current feedback | separate disconnect、arm interlock | unexpected bank/bodydiode backfeed |
| dump switch stuck ON / OFF | gate/solder/short | resistor overheat / stored energy | V decay/temperature/current | thermal cutoff、independent meter/service path | auxOFF/indicatorOFFでもenergy残留 |
| aux regulator fail | surge/short/startup | unsafe driver or MCU state | rail supervisor/UVLO | default OFF、independent kill、reverse blocking | common supply lossで保護も停止 |
| L saturation | tolerance/bias/hot | ripple/di-dt増大 | external fast OC + validated L curve | threshold/latency/Isat coordination | typ25°C Isatでは保証不能 |

---

# Task 2 FMEA update

qualitative、未実装、RPN/Ttrip/clear energyはTBD。Protectionは要求。各faultはfault latch→killと必要な両側disconnectを使う。normal recoverableでもautomatic rearm禁止。

| Failure mode | Cause | Effect | Detection | Protection | Residual risk |
|---|---|---|---|---|---|
| capacitor overvoltage [LATCHED] | control/regen/divider fault | cell vent | bank independent OV + cell monitor | charge inhibit / isolate | threshold/latency、dump thermal |
| cell imbalance [WARNING→LATCHED] | C/leak/temp/shunt fault | cell OV/UV/reversal | per-cell min/max/open-wire | switched passive balance、OV kill/UV stop | tap/monitor common failure |
| overcurrent [LATCHED→CRITICAL] | short/control/lowV | energy into PCB/FET | external fast comparator + port sensing | latch/kill、DC disconnect/fuse coordination | clearing前stress、same shunt fault |
| MOSFET short [CRITICAL] | thermal/avalanche/shootthrough | bus-bank uncontrolled conduction | current/ΔV abnormal、isolation feedback | both-source independent interrupt | failed disconnect/body diode/internal bank short |
| MOSFET open [LATCHED] | bond/driver/solder | diode overload/no transfer | command-current mismatch | kill/log/inspect | local hotspot before detection |
| gate driver failure [LATCHED→CRITICAL] | UVLO/stuck output | shootthrough/unwanted gate | rail/fault/current | EN default OFF + independent disconnect | stuck-high not solved by PWM OFF |
| inductor saturation [CRITICAL] | overload/hot/dc bias | rapidly rising current | fast OC / current slope | kill and latch、Isat/Ttrip coordination | delay di/dt、core damage |
| sensor failure [LATCHED] | amp/reference/tap/open/stuck | false safe feedback | rails/range/cell sum/reference/open-wire | no arm、external protection | common reference/shunt/supply failure |
| MCU crash [LATCHED] | clock/hardfault/debug/watchdog | retained PWM | external heartbeat supervisor | hardware kill + timer fault | reaction time/clock shared causes |
| CAN loss [RECOVERABLE] | cable/busoff/stale | stale power request | counter/timeout/busoff | inhibit + explicit rearm | timeout energy、official module offline |
| thermal fault [WARNING→LATCHED/CRITICAL] | ESR/airflow/contact/core | degradation/fire | 3 representative NTC + validation thermography | derate/trip、no hot dump | unmonitored hotspot/lag |
| precharge failure [LATCHED] | resistor open/bypass welded | inrush/no startup | ΔV/I/time/feedback | bypass interlock/isolation | contact feedback ambiguous |
| discharge-path failure [LATCHED] | bleed open/dump fail/aux loss | residual bank energy | independent meter/rebound/indicator selfcheck | lockout + service discharge | service error/indicator failure |
| input loss [RECOVERABLE→LATCHED] | ref cutoff/battery disconnect | cap backfeed/reboot | bus UV/ref enable/supervisor | assist inhibit / source isolation | diode conduction、aux collapse |
| disconnect failure [CRITICAL] | welded/short switch | continuing fault current | feedback/current after kill | alternate interrupt/fuse | DC arc、fault coordinationTBD |

Fault thresholds、latency、primary/secondary sensor独立性、pulse熱、single bank port合規、Safe判定は未解決。詳細回路へ進む前にレビューする。

---

## Task 1 record (historical; Task 2 above takes precedence)

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
