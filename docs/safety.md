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
