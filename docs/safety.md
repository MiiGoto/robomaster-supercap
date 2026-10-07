# PCB routing complete — 2026-10-07

**Current: Prototype Rev A CAD routing complete.** KiCad10.0.6の正式PCBでnative未接続0、全DRC0 errors/0 warnings、schematic parity0、ERC0 errors/0 warningsを確認した。全331ネット／1524 net-assigned pad recordsの物理接続と、設計manifestの1478 pad/net assignmentsを照合済み。これはCAD接続・規則検証であり、製造リリース、通電許可、120 W性能、競技適合の承認ではない。

一般銅箔間隔0.20 mm、承認済み39 ICの同一部品内Pad/Pad0.15 mmを維持した。新たなDRC除外・No ERC・規則緩和はない。未コミットの`.kicad_pro`設定展開は保持し、functional commitに含めない。詳細は[配線完了記録](pcb_routing_completion.md)を現在の情報源とする。以下は過去時点の記録として保存する。

## Historical records (preserved)

# PCB engineering authorized — 2026-10-04

ユーザーがsurge・OC遮断時間・fuse/接触器協調・熱・放電時間の実測前にPCB配置/配線へ進むことを明示承認した。[現行PCB記録](pcb_rev_a.md)を優先する。未実測の項目はPrototype Assumptionとして保持し、製造/通電/性能保証にはしない。以下の「PCB未承認/開始しない」は過去時点の記録として残す。

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A current unresolved safety release conditions

Independent OC comparator→async latch→PWM AND/driver EN/HRTIM fault exists in the schematic; do not replace with ADC polling. Mandatory G–S pull-downs, UVLO/window, supervisor, watchdog and default-low arm remain. Active dump is thermally qualified, never automatic on overheat. Sources and bank require independent DC interruption because shorted FET/contact cannot be cleared with PWM.

Unapproved: actual surge/regen/source Z, end-to-end shutdown/overshoot and shoot-through bypassing sense, cell profile defaults/readback/OTP, cell tap source protection, gate/partial-power behavior, shared reference/shunt faults, aux/actuator supply, welded contacts/fuse breaking, discharge residual/rebound, continuous and repeated peak temperature. 60V FET, TVS name and ERC0 are not proof of fault containment. Service voltage investigation1V is not a safe-service certification.


## Historical records (preserved)

# Task 3 safety review — circuit unimplemented

[採用承認と未確定条件](task3_review_gate.md)・[部品比較](task3_component_review.md)を優先する。Task 2の8/12 A平均目標承認は瞬時current・熱・保護性能の確認ではない。

- OCはcomparator/front-end maximum delay、latch、input clamp、driver propagation、gate turnoff、寄生Lとfault voltageを合計し、I_peak + V_fault/L_min × t_clearが部品・module制約内か評価。典型値だけでtripを確定しない。
- UCC27282 EN停止typ1.5µsだけを高速tripとしない。HI/LI clamp + timer faultと独立EN inhibitを候補にする。signal/supplyの共通故障とstuck driverにはsource/bank DC interruptが必要。
- L toleranceとbias低下でripple目標を超え得る。cap平均12 A、ILpeak、module端瞬時15 Aは別量で、DC-linkのripple吸収とerror/latencyを含むcoordinationが未完了。
- bank ESR初期12 A時25.92 W、aging2倍時51.84 W。120 W要求の計算runtimeをpeak許可秒数として使用しない。actual pulse/interval/ambient/cooling・cell熱定格の確認まで実機運転禁止。
- precharge/dumpはRC感度計算だけ。抵抗製品のpulse overload、bypass weld、thermal fault時dump inhibit、single-port適合、安全閾値/時間はTBD。

---

# Task 2 safety architecture (unimplemented)

[architecture proposal](task2_decisions.md)のexternal OC/OV/cell monitoring、watchdog/latch、normally-OFF isolation、default OFF、precharge feedback、bleed/controlled/service dischargeを基準とする。software-only高速保護は禁止。gate killとsource/bank disconnectは別action、PWM OFFはshort FETやbody diodeを遮断できない。

- ref Chassis cut→assist即inhibit。bank/aux/通信線から監視・遮断を迂回しない。
- cell OVはbank sum正常でもcharge停止。per-cell UVは最弱cell逆転防止、balancingは保護代用不可。
- current clamp8/12 A、cell2.45 V、FS±20 A等はAssumption。15 A rule以下を瞬時ripple/誤差/latency込みで検証。
- external supervisor/latched faultはreset/crash/debug/aux loss/floatでOFF。driver supply UVLO、GPIO bias、power sequence、fault-input lossを検証。
- short/MOSFET stuck-highには独立DC interruptとfault energy coordinationが必要、実装/定格TBD。
- no hot unplug、reverse polarity/connector arc/PCB hotspot/temperature sensor lagをFMEA対象とする。
- permanent bleed + controlled dump + service tool + independent voltage indicationを提案。熱fault時dump禁止。single-port/検査energy測定との共存を人間確認。
- OFFはSafeではない。Vsafe/Esafe/rebound/timeがTBDの間はSafe確認を宣言しない。

安全marginの配賦はtask2_decisions参照。保護threshold/error/response time/common cause/残留energyをTask3前に承認し、後日低energy fault injectionで検証する。今回実機試験なし。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Safety concept and unresolved risks

Task 1のConfirmed要求。保護回路・閾値・遮断能力・試験はTBD。安全性検証完了ではない。

## Fail-safe philosophy

enableはfloating、reset、firmware crash、aux supply loss、communication lossでONにならない。
外部biasとsupervisor、driver UVLO、independent fault latch、watchdog inhibit候補を検討する。
MCU pin初期値だけで安全を保証せず、電源sequence・bootloader・SWD haltも対象とする。
保護入力はnormal operationの通信やsoftware commandより優先する。
CAN復帰・reset完了だけでautomatic re-armしない。故障原因除去・明示操作・self-testが必要。

PWM停止は電気的隔離ではない。MOSFET body diode、短絡FET、bankからの逆給電を追跡する。
bus側とbank側のどちらもenergy source。DC遮断・fuse clearing・isolationの能力は双方のworst caseで検証する。
通常のsoftware current loopより速いshort circuitには独立hardware tripを要求する。
同じsensor/ADC reference/aux supplyを共有すれば独立software判定でもcommon-cause failureが残る。

## Hazard controls

| Hazard | Required prevention / detection / response | Open risk / decision |
|---|---|---|
| bank overvoltage | bank V sense + independent OV candidate、charge inhibit / isolation | OV threshold、sensor independence |
| individual cell OV | cell monitor、imbalance診断、charge停止 | bank V正常でもOV可能、balanceは単独保護不可 |
| excessive charge current | signed current、fast trip、soft start | sensor/filter delay、trip latency |
| excessive discharge current | bank/inductor current上限、UV derating、fast trip | low Vcapでcurrent増大 |
| short circuit | fault energy path別のisolation/fuse候補 | PWM OFFでshort FETを止められない、DC interrupt/arc |
| MOSFET short | independent disconnect / fault current limitation | body diode経路、共通mode故障、energy let-through |
| MOSFET open | current tracking、voltage/power異常、stop | 他FET/diodeへ負担集中 |
| gate driver failure | UVLO、enable OFF bias、fault latch、deadtime | stuck-highはPWM停止だけでは不十分 |
| MCU crash/reset | external watchdog/supervisor候補、hardware trip | timerがPWMを出し続ける場合、clock共通故障 |
| current sensor failure | plausibility、open/stuck/range診断、independent protection | 同一shunt/reference共通故障 |
| voltage sensor failure | cell/bank sum相関、reference診断、range検査 | divider openによる偽低電圧 |
| overtemperature | hotspot monitoring、derating/trip、sensor fault診断 | thermal lag、未監視箇所 |
| reverse current | signed sense、mode/zero-current guard、blocking候補 | OFF body-diode逆流、robot source吸収可否 |
| connector disconnect under load | load停止→zero確認→service lockout、touch/arc防護 | 操作ミス・接触不良・arc、hot unplug禁止方針 |
| residual energy after OFF | bleed/service discharge、独立電圧測定、rebound再確認 | aux消失、bleed断線、表示故障 |
| reverse polarity | keyed connector、polarity検出、blocking候補 | capacitor逆電圧、短絡FETで保護喪失 |
| PCB overheating | current/thermal budget、Kelvin、短いloops、cooling | connector/via局所hotspot、aging |
| bank/cell undervoltage | per-cell UV、assist停止、weak cell逆転防止 | bank sumだけでは不十分 |
| precharge bypass fault | ΔV/current/time監視、main接続feedback | welded bypass、未検知inrush |

## Stored-energy-safe definition

G Shutdownは制御transfer停止。H Stored-energy-safeは全危険domainのvoltage/energyが承認閾値以下で、隔離・再上昇・cell状態を測定して確認した状態。
safe threshold、discharge time、indicator、service測定点、放電素子のpulse/continuous/energy定格はTBD。
OFF/LED消灯/一定待ち時間のみをH判定にしない。故障で放電できない場合はFに保持し、energy残留を明示する。
電圧計の動作を既知sourceで前後確認し、service tool接続もinrush/arcを評価する。
温度異常中にbleedをONすると熱を増やす場合がある。controlled discharge許可条件をfault別に設計する。

## Review and verification gate

限界値はrequirementsとPROJECT_CONTEXTのhuman gateを守る。maker datasheet、official rules、robot envelope、capacitor候補をそろえる。
全safety機能について「検出範囲 / latency / action / common cause / residual risk / test」を記録する。
FMEAを更新し、低energy/current-limited条件からfault injectionを行う。今回通電・保護解除・実機試験は行わない。
