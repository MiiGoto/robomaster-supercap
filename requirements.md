# Task 3 current status

2026-10-03 JST。Task 2案はユーザー採用承認済み。実bus/surge・peak継続/間隔・ambient/coolingは未入力。承認範囲と詳細回路gateは[Task 3 review gate](docs/task3_review_gate.md)を優先する。Task 3は候補評価まで進行中、詳細回路未実装。以下のTask 2承認待ち表示は承認範囲についてhistorical record。

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
