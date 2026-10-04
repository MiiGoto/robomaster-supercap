# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A gate before energizing

1. Independent schematic/package/land review; inspect selected exact passives/lands,source-side tap assembly,external power/fuses/contacts and required interruption tests against rev_a_design_freeze.md.
2. BQ supercap profile/readback/power-cycle/protection mapping and MCU BOOT0/reset options review. No gate arm with unprovisioned monitor.
3. Approve current-limited containment plan and independent bank/service isolation; OFF/LED dark never prove discharged.
4. Only after approval: staged auxiliary/low-energy fault tests, analog off-injection, bootstrap/ringing, actual trip latency/current excursion, precharge/dump and thermal characterization. Then review measured full-power/duty/competition envelope separately.

No tests in this list were physically performed. ERC/netlist/calculation results are not energizing authorization.


## Historical records (preserved)

# Task 4 measurement access plan — no energization

scope protective-earth ground clipをhigh-side gate/source、SW_NODE、bankのfloating pointへ無確認で接続しない。scopeのearthを外してfloating測定しない。rated differential probeまたは適切にisolatedされたmeasurement systemを使用し、differential/common-mode電圧、transient、bandwidth、probe spacingを確認する。VGSはgateとそのsource間で測定する。

bank未接続・低energyでfixture/ground/probe接続を確認し、原則deenergized状態でprobeを固定、独立meterで残留電圧とreboundを確認する。loopを短くするためのprobe padも指やground clipでshortしにくくする。[PCB方針](task4_pcb_strategy.md)のtestpointは未配置。現在回路/placement gate未通過につき通電許可ではない。

---

# Task 2 validation plan

今回通電なし。Task3承認後、current-limited/low-energy sourceでsensor calibration、ADC/PWM窓/latency、external comparator/kill、reset/boot/debug halt、cell OV/open-wire、precharge welded/open、referee cutoff、CAN stale、dump thermal/断線/reboundを段階検証する。
公式module peak15 Aのscopeとwaveform、fault interruption/energy let-throughを測定。cap公差/ESR/thermal/lifetimeと実usable energyを測定。実prototype結果なしにsafe/working/validatedと表現しない。
計算5 checksはunit/analytic runtime/both-direction power balance/current clamp/energy conservationを対象、circuit approvalではない。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Future bringup gates

Task 1で実機試験なし。この手順は将来計画で、通電許可ではない。

1. 適用規則・robot envelope・capacitor datasheet・全limitを人間承認。schematic pin/rating/thermal/ERC、PCB DRCをreview。
2. bank未接続・power stage無効でauxだけをcurrent-limited sourceから起動。enable float/reset/brownout/debug haltがOFFであることを測定。
3. ADC/reference/calibrationを既知signalで確認。sensor open/short/stuckと独立tripをenergyなしで検証。
4. small-energy代替loadでprechargeとshutdown、timeout、CAN loss、fault latch、explicit rearmを確認。
5. approved limits下でconverter directionを個別確認。differential probeと測定器common groundによる短絡を防ぐ。
6. fault actionが証明された後にbank/energy/currentを段階的に増加。各段階でthermal、ripple、trip energyを記録。
7. robot統合は公式module接続・計測点・rule complianceの確認後。service dischargeとreboundを毎回確認。

合格条件の数値・probe rating・test fixture・緊急遮断・放電toolはTBD。
unresolved limit、failed trip、sensor不整合、未確認residual voltageがあれば次段階へ進まない。
