# PCB routing complete — 2026-10-07

**Current: Prototype Rev A CAD routing complete.** KiCad10.0.6の正式PCBでnative未接続0、全DRC0 errors/0 warnings、schematic parity0、ERC0 errors/0 warningsを確認した。全331ネット／1524 net-assigned pad recordsの物理接続と、設計manifestの1478 pad/net assignmentsを照合済み。これはCAD接続・規則検証であり、製造リリース、通電許可、120 W性能、競技適合の承認ではない。

一般銅箔間隔0.20 mm、承認済み39 ICの同一部品内Pad/Pad0.15 mmを維持した。新たなDRC除外・No ERC・規則緩和はない。未コミットの`.kicad_pro`設定展開は保持し、functional commitに含めない。詳細は[配線完了記録](docs/pcb_routing_completion.md)を現在の情報源とする。以下は過去時点の記録として保存する。

## Historical records (preserved)

# PCB engineering authorized — 2026-10-04

ユーザーがsurge・OC遮断時間・fuse/接触器協調・熱・放電時間の実測前にPCB配置/配線へ進むことを明示承認した。[現行PCB記録](docs/pcb_rev_a.md)を優先する。未実測の項目はPrototype Assumptionとして保持し、製造/通電/性能保証にはしない。以下の「PCB未承認/開始しない」は過去時点の記録として残す。

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](docs/rev_a_schematic_review.md)と[pinout](docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A current requirements register

| Item | Current decision | Status |
|---|---|---|
| Rules |2026 RMUL,prior source editions;event supplement applicability remains open |Confirmed target / eligibility TBD|
| Bank |9S SCCV40B506SRB50F;Ceq5.5556F;rest12–22.05V;cell normal2.45V,COV2.530V |Adopted goals / Prototype selection|
| Bus |22–26V;surge investigation36V,measured VDS<=48V and reviewed SOA |Prototype Assumption / waveform TBD|
| Power/current |40W charge,80/120W assist requests;normal8A,initial peak-average9.5A;12A future goal |Adopted goals / capability TBD|
| Converter/MCU |Four-switch bidirectional buck-boost,G474RE/LQFP64,200kHz/22uH |Approved architecture / schematic only|
| Sensing/OC |Three3mR WSK2512 Kelvin,INA240 signed,INA293/TLV3202;cap/IL~12A;0.5us clearing required |Concrete schematic / actual response TBD|
| Cell monitor |BQ7694204,39-entryRAM profile,SPI CRC,9S0x02FF,COV/CUV,active-low-fault permits,host-only trim |Selected configuration / NOT programmed|
| Link/precharge |Each6×EEUFR1J471,100R HS25+AQZ202G,NO AEV bypass,3s timeout |Prototype selection / inrush test TBD|
| Discharge |10k bleed,100R HS25 dump/service;40min to1V target pluscell/rebound/energy checks |Procedure target / measured time TBD|
| External isolation |FourAEV14012,DDR-60L-12,MINI99758V fuses+0FHM holders;manual disconnect |Bench assembly selected / interruption coordination test TBD|

Confirmed means adopted target or checked fact; **does not mean demonstrated capability**. Full-power gates remain surge/regen/source impedance, duty, heat, OC clearing, residual energy and isolation fault capability. Current MCU allocation is docs/pinout.md, overriding historical spare-count/pin plans.


## Historical records (preserved)

# Task 4 current status — placement gate未通過

2026-10-03 JST。Task 3 base428ad10を保持。重大TBDと詳細回路未実装のため添付Task 4 §1に従いplacement/outline/footprint/routingは行わない。[独立review](docs/task4_review.md)が現在status、[PCB方針](docs/task4_pcb_strategy.md)は提案、[検査結果](docs/task4_baseline.md)は既存skeleton限定。Task 5へ進まない。以下は過去Task記録。

---

# Task 3 current status

2026-10-03 JST。Task 2案はユーザー採用承認済み。実bus/surge・peak継続/間隔・ambient/coolingは未確定（ユーザー回答：不明）。承認範囲と詳細回路gateは[Task 3 review gate](docs/task3_review_gate.md)を優先する。Task 3は候補評価まで進行中、詳細回路未実装。以下のTask 2承認待ち表示は承認範囲についてhistorical record。

---

# Task 2 requirements freeze — proposal, not construction approval

2026-10-03 JST。[採用理由・一次根拠・margin](docs/task2_decisions.md)、[計算](simulation/results.md)。Confirmedは実装完了を意味しない。Assumptionは人間レビュー待ち。

| Item | Current value / decision | Status | Remaining evidence |
|---|---|---|---|
| Ruleset | 2026 RMUL、哨兵/歩兵/英雄/エンジニアの要求 | Confirmed | 開催地/種目/補足TBD |
| Rule editions | RMUL CN V1.2.0 / 制作CN V1.3.0、公式RMULアーカイブ掲載最新版 | Confirmed | 会場答疑確認 |
| Eligibility | 底盤assist bankは英雄/歩兵/哨兵のみ、Engineer対象外(S5) | Confirmed | Engineerへの別用途は許可を推測しない |
| Supply maximum | 対象4種30 V、power management input22–26 V | Confirmed | converter実端のdroop/surgeはTBD |
| Vbus range | 計算22/24/26 V; 実operating min/nom/max | Assumption / TBD | battery型番、Chassis端波形、regen |
| Rule energy | nominal2000 J / measured2200 J | Confirmed | capacityはrated voltageで計算、実測検査 |
| Power constraint | 3V3 Hero/Sentry100 W, Infantry90/75 W; Infantry Match120 W | Confirmed | 種目/型選択、referee計測点の統合 |
| Cell count / product | SCCV40B506SRB、9S第一案; alternatives7S HV60 /4S HV100 | Assumption | thermal/stock/mount/人間承認 |
| Capacitance | cell50 F, Ceq5.5556 F nominal、tol−10/+30% | Assumption | 製品採用・実測・aging |
| Vcap range | useful12..22.05 V; nominal比較18 V; cell normal2.45 V | Assumption | 精度/balance/overshoot配賦の実証 |
| Cell rating | 選定候補datasheet2.7 V/cell, rated sum24.3 V | Confirmed (candidate) | normal定格と混同しない |
| Energy | A usable950.5625 J nominal; rated1640.25 J; +30%2132.325 J | Confirmed calculation under Assumption | 実効C/セル差/検査測定 |
| Charge current / power | bus input40 W scenario、normal cap clamp8 A | Assumption | 実charge max/TBD、referee負荷budget |
| Discharge current | normal8 A / peak12 A scenario; module peak/continuous15 A rule | Assumption / Confirmed rule | ripple/error/trip overshoot、熱定格TBD |
| Nominal / peak power | request80 /120 W、current/thermal/UVでderate | Assumption | 実max、peak duration、robot要求TBD |
| Converter | 4-switch non-inverting bidirectional synchronous buck-boost | Assumption selected proposal | 重なり電圧・制御・loss・人間承認 |
| Switching / L | 100–200 kHz; exploration11–22 µH, ΔI3 A p-p | Assumption | 全corner/duty/部品/温度で再算出 |
| MCU | STM32G474RE LQFP64; alternative G431RB | Assumption selected proposal | package AF conflict、errata、承認 |
| Current sensing | bus/cap high-side signed shunts + separate inductor sense | Assumption selected proposal | amplifier settling/共通故障/承認 |
| Voltage sensing | bus/bank ADC + differential per-cell monitor、独立OV | Confirmed requirement / Assumption method | tap protection/range/error |
| Temperature | MOSFET群/inductor/bank各代表1点NTC | Assumption | hotspot測定、thresholdsTBD |
| Balancing | IC-based switched passive、MCU非依存OV inhibit | Assumption selected proposal | IC/精度/損失/供給断時動作 |
| Precharge | resistor path + normally-OFF bypass、ΔV/current/time確認 | Assumption selected proposal | R/Clink/energy/start time/approval |
| Discharge | permanent bleed + controlled dump + service tool +独立表示 | Assumption selected proposal | Vsafe/Esafe/time/公式検査との共存TBD |
| Hardware protection | external OC/OV/latch/watchdog/kill、reset/float OFF | Confirmed requirement | clearing時間/回路/故障遮断能力TBD |
| CAN | telemetry使用、official module→CAN1、Classic CAN互換を想定 | Confirmed requirement / Assumption format | bitrate/ID/period/timeout/TBD |
| Mechanical / cooling | port1つ、検査lead≥100 mm、mount/冷却/絶縁 | Confirmed rule / TBD dimensions | robot envelope/thermal approval |
| Debug / test / firmware | SWD/UART、ADC同期、state machine、fault injection計画 | Confirmed requirement | implementation、試験は今回なし |
| Expansion | spare GPIO4、cell monitor interface | Assumption | pin plan/area |

Task 3へ進む前のhuman review: cell数/Vcap、max current/peak power、topology、MCU、sensing、prechargeと全power component定格。実robot仕様不明のため最終数値freezeではなく、証拠付きproposal freeze。Task 3自動開始禁止。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Requirements register

2026-10-03 JST。Confirmed = 依頼から確定した要求または直接確認した資料の内容。
Assumption = 比較に使う仮定。TBD = 未決定。要求のConfirmedは実装・検証の完了を意味しない。

## Competition constraints: current applicability is TBD

公式 [Rules/Resources Hub](https://bbs.robomaster.com/wiki/20204847) と [downloads](https://www.robomaster.com/zh-CN/resource/download/competition) を確認。
取得できた一次資料は **2026制作規則 V1.3.0 (2026-02-09)**。以下はその版の内容としてConfirmed。
現在適用する最新版・大会・地域・robot種別はTBDであり、下記数値を本設計の確定限界値にしない。

[公式V1.3.0 PDF](https://bbs-web-static.robomaster.com/715e2519e5384666a5d13edda17c6b831770696773838/RoboMaster%202026%20%E6%9C%BA%E7%94%B2%E5%A4%A7%E5%B8%88%E9%AB%98%E6%A0%A1%E7%B3%BB%E5%88%97%E8%B5%9B%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%88%B6%E4%BD%9C%E8%A7%84%E8%8C%83%E6%89%8B%E5%86%8CV1.3.0%EF%BC%8820260209%EF%BC%89.pdf)

| 条項 / 印刷page | 確認した版での内容 | 本projectへの適用 |
|---|---|---|
| S5 / 14 | Hero / Infantry / Sentryのみ、各robot最大1組 | TBD |
| S6 / 14 | nominal energy合計 ≤2000 J、measured energy合計 ≤2200 J。nominal計算は耐圧と容量による1/2 C U² | TBD、動作電圧でnominalを過小評価しない |
| S7 / 14 | Chassisに接続し底盤powerに寄与しないcapacitorのnominal容量合計 ≤10 mF | TBD、通常bus decouplingも分類確認 |
| 3.12 / 97–98 | bankと自作power control boardの間に公式管理module、module CANはpower management CAN1へ | TBD、独自telemetry CANと混同しない |
| S184 / 98 | 公式moduleのXT30接口はpeak / continuousとも ≤15 A | TBD、bus側current限界とは同義でない |
| S185–189 / 98 | 検査時bankを満充電から1 V未満まで測定、検査lead ≥100 mm、moduleにアクセス可能、bank power接口は1つ | TBD、1 Vを一般のservice-safe閾値としない |

第三者indexにはV2.0.0制作規則(2026-06-26)とV2.2.0競技規則(2026-08-07)、2027先行資料への案内があった。
一次資料としての最新版取得・版照合はできず、第三者PDF linkは404。探索はここで停止した。
対象大会を決め、公式hubから最新版と補足を取得し、上表の変更差分・接続図・chassis power計測点を人間レビューする。
最大bus電圧・許容powerは今回一次資料で対象robotに対して確定できていない。過去の24 V / 240 W等を流用しない。

## Requirements

| ID | Category | Requirement | Status | Acceptance / next evidence |
|---|---|---|---|---|
| COMP-01 | Competition constraints | 大会・年・地域・robot種別・最新規則・裁判systemを特定 | TBD | 版/date/条項/適用範囲をレビュー署名 |
| COMP-02 | Competition constraints | 公式管理module・検査path・single bank接口を満たす | TBD | 適用図面と接続を照合 |
| IN-01 | Electrical input | bus min/nominal/max、surge、source impedance、regen吸収能力 | TBD | robot power仕様と測定 |
| IN-02 | Electrical input | reverse polarity、inrush、busへの逆流を制限 | Confirmed | approved limitsでfault test |
| OUT-01 | Electrical output | assist power/current/duration、ripple、response time | TBD | robot load profile / competition制約 |
| ES-01 | Energy storage | cell数/製品/C/ESR/voltage/usable energy/agingを決定 | TBD | maker datasheetとworst case計算 |
| ES-02 | Energy storage | series cell imbalanceを検出し弱いcellを保護 | Confirmed | bank正常でもcell OVならcharge inhibit |
| CHG-01 | Charge control | current/power/voltage上限を守りsoft startする | Confirmed | 上限値TBD、independent trip検証 |
| CHG-02 | Charge control | referee計測点でpower budgetを守る | TBD | power budget loss/delay余裕を承認 |
| DIS-01 | Discharge control | bus電圧、bank/cell UV、熱、currentからassistを制限 | Confirmed | approved envelope外はinhibit |
| DIS-02 | Discharge control | charge↔assistはzero-current確認を経由 | Confirmed | reversal transientを検証 |
| VS-01 | Voltage sensing | busとbankを測定、ADC open/short/saturation/stuck診断 | Confirmed | calibrated測定とfault injection |
| VS-02 | Voltage sensing | per-cell監視方式とindependent OV path | TBD | 共通原因故障をレビュー |
| CS-01 | Current sensing | signed bus/bank/inductor電流の必要測定点を決定 | TBD | topologyとloop帯域から選択 |
| CS-02 | Current sensing | calibrationと独立fast overcurrent trip | Confirmed | sensor故障でも危険電流を止める |
| TS-01 | Temperature sensing | MOSFET/inductor/bankのriskから測定点選定 | Confirmed | hotspot熱測定、断線診断 |
| TS-02 | Temperature sensing | sensor数、derating/trip温度と応答 | TBD | datasheetとthermal model |
| COM-01 | Communication | CANによるmode/fault/voltage/current/energy/temp telemetry | Confirmed | protocol/ID/bitrate/periodはTBD |
| COM-02 | Communication | timeout、bus-off、stale commandはassist/chargeを無効化 | Confirmed | CAN lossと復帰時再arm検証 |
| SAF-01 | Safety | float/reset/crash/aux lossのdefault enable OFF | Confirmed | MCU不要のhardware inhibit確認 |
| SAF-02 | Safety | MOSFET短絡でもenergy fault pathを遮断/制限 | Confirmed | PWM OFFだけで合格しない |
| SAF-03 | Safety | OV/OC/UV/thermal、precharge timeout、reverse current保護 | Confirmed | thresholds / trip latency TBD |
| SAF-04 | Safety | shutdown後の放電、独立電圧確認、再上昇確認 | Confirmed | safe voltage/energy/time TBD |
| MECH-01 | Mechanical | vibration/impact、cell retention、絶縁、touch/arc防護 | Confirmed | enclosure/interfaceレビュー |
| MECH-02 | Mechanical | size/mass、mount、connector、serviceアクセス | TBD | robot envelopeと規則 |
| COOL-01 | Cooling | ESR/semiconductor/inductor/PCB損失の熱経路確保 | Confirmed | ambient/airflow/limits TBD |
| DBG-01 | Debug | SWD/UARTとfault log、halt時に安全停止 | Confirmed | debugger halt fault test |
| TEST-01 | Testability | sense/fault/enable測定点、current-limited初期試験 | Confirmed | bringup checklist |
| FW-01 | Firmware | 明示state machine、watchdog、latched fault、再arm | Confirmed | implementationは別Task |
| FW-02 | Firmware | ADC/PWM同期、ISR予算、calibration integrity | Confirmed | timing / checksum試験 |
| EXP-01 | Future expansion | balancing・telemetry拡張余地を比較 | Assumption | pin/area/cost予算承認 |

## Values requiring human approval

maximum bus voltage、capacitor maximum voltage、cell count、charge/discharge current、output power、topology、MOSFET/inductor/fuse/connector定格は全てTBD。
安全要求の存在は確定していても、数値・回路実現・検証は未確定。
