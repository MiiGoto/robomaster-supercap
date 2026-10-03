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
