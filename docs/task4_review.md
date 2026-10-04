# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Current milestone correction

Earlier Task4 label describes a placement review, not completed PCB work. Current new branch implements Rev A schematic. PCB is still empty and unchanged; fabrication/placement gate remains CLOSED pending schematic/assembly/protection review. Historical audit findings below are preserved; resolved schematic absence is superseded, physical safety evidence is still missing.


## Historical records (preserved)

# Task 4 independent review — placement gate not passed

2026-10-03 JST。baseはTask 3 feature/power-stage-schematic /428ad10。詳細回路が完成しているというTask 4の前提は満たされていない。添付Task 4 §1に従いPCB placementへ進まない。Task 2構成承認は有効だが、実bus/surge、peak秒数/間隔、ambient/coolingについて直近ユーザー回答は「不明」。同じ採用承認を再要求しない。

## Gate review

| Item | Evidence / current state | Decision |
|---|---|---|
| VBUS max | 22–26 Vは計算scenario、実converter端surge不明 | blocking TBD |
| VCAP / bank | 承認済9S50 F/cell、12–22.05 V、cell ceiling2.45 V | 構成Confirmed、cell OV/UV実装・熱定格TBD |
| current / power | 承認済平均8/12 A、要求80/120 W、charge入力40 W | ripple/latency、peak duty/thermal未確認 |
| topology / MCU | 承認済4-switch bidirectional、G474RE/LQFP64 | 詳細net/AF/pin照合未実装 |
| MOSFET / L | CSD18540Q5B / XAL1510-223MEDは候補 | VDS実peak、hot saturation、SOA/thermal未承認 |
| driver supply | UCC27282DRCR候補、12 V案 | regulator・sequence・bootstrap・deadtimeTBD |
| current sense | high-side signed shunts承認、3 mΩ/gain20/50計算候補 | shunt製品/保証swing/range/error/fault未確定 |
| hardware OC | comparator/latch/kill要求のみ | threshold/max latency/parts未確定、blocking TBD |

## Independent block review

各行は回路で確認できた動作ではなく、現存conceptと不足実装を突き合わせた要求レビュー。全blockの電気的net・保護動作は未検証。

| Block / function | Normal | Startup | Shutdown | Fault | Power OFF / missing evidence |
|---|---|---|---|---|---|
| POWER_INPUT / source boundary | 公式計測点から供給 | polarity/ΔV確認 | source disconnect | fuse/DC interrupt | bank逆流阻止回路なし |
| AUXILIARY_POWER / rails | driver/3.3 V供給 | supervisor arm inhibit | gate kill先行 | UVLO/OV kill | regulator/backfeed回路なし |
| CONTROLLER / control | signed current loop/telemetry | resetでOFF | zero current/disable | external watchdog | MCU pin/rail/AF/clock回路なし |
| GATE_DRIVER / two legs | complementary control | bootstrap charge/refresh | HI/LI/EN LOW | latch kill | supplyOFF/float確認回路なし |
| POWER_STAGE / reversible conversion | charge/assist | limited energy | current decay then isolate | short時独立interrupt | bodydiode path未実装・追跡不可 |
| INDUCTOR / energy transfer | CCM/current ripple | zero-current start | decay path | saturation→OC | L製品定格freezeなし |
| CURRENT_SENSING / signed bus/cap/IL | range/settling/calibration | reference validity | continue fault sensing | open/short/stuck diagnosis | amp/shunt/comparator回路なし |
| VOLTAGE_SENSING / bus/cap/cells | limits/energy | OV/UV/open-wire確認 | independent residual check | divider失敗時independent OV | unpoweredADC injection未設計 |
| TEMPERATURE_SENSING / hot spots | derate | open/short check | hot dump禁止 | latch/isolate | NTC値・位置・tripTBD |
| PRECHARGE / inrush | bypass aftervalidΔV | R path/time/I確認 | bypassOFF | welded/open inhibit | R/bypass/isolation未実装 |
| SUPERCAP_BANK / storage | per-celllimits/balance | weakest cell確認 | residualenergy管理 | cellOV/UV independent action | monitoring/tap protection未実装 |
| SAFE_DISCHARGE / residual energy | standbybleed | voltagecheck | controlled/service discharge | hot/stuck診断 | auxOFF表示/放電保証なし |
| CAN / integration | fresh telemetry/requests | no stale arm | inhibit message | timeout/busoff | transceiver/backfeed/terminationなし |
| SAFETY / independent inhibit | all permits valid | defaultOFF | latch/isolate | HW OC/OV/temp/watchdog | comparator/latch/interrupt回路なし |

## Abnormal-state review

以下の危険pathは詳細回路がないため排除できていない。Protection列は未実装要求。

| State | Potential uncontrolled path / effect | Required protection / verification |
|---|---|---|
| A busOFF bankfull | bodydiode/auxからrobot逆流 | 両側source isolation、公式cutoff尊重 |
| B busON MCUOFF | gateinputfloat/ADC injection | biasOFF/supervisor/no backpower |
| C MCUreset | retained PWM/boot alternatefunction | independent kill/reset/startup tests |
| D driverOFF | bodydiode transfer残留 | gateOFFとisolationを分離 |
| E driverstuckON | oneleg短絡/相手FETshootthrough | 独立DC interrupt/fuse coordination |
| F MOSFETshort | bus/bank短絡供給 | both-source interruption/let-through |
| G MOSFETopen | bodydiode過熱/no transfer | command-current mismatch停止 |
| H Lsaturation | di/dt急増 | hot Lmin/OC totaldelay確認 |
| I currentsensor断線 | falsezero/excess current | independent sensing/OC、no rearm |
| J busdividerfailure | falsebus/ADCdamage | independent OV/range/ADCprotection |
| K capdividerfailure | chargeOV/energy誤表示 | cellOV + independent bankOV |
| L prechargeONstuck | insertioninrush | separate source isolation/feedback |
| M prechargeOFFstuck | startup失敗/timeout | bypassinhibit、explicitfault |
| N dumpONstuck | resistor/PCB過熱 | independent thermal/interrupt |
| O dumpOFFstuck | storedenergy残留 | 独立meter/service path/rebound |
| P CANdisconnect | stalepower/officialcutoff迂回 | timeout/inhibit/explicitrearm |

## Corrections and remaining work

「Task 3詳細回路完了」「ERC0だから回路安全」「unconnected0だから配線完了」という解釈をstatus文書で訂正。回路自体の修正は行わない。candidate pin/footprint assignmentは存在しないため、全主要部品の最終照合はNot performed。

実bus/surge・peak duty・thermal条件を確認し、Task 3詳細回路、cell監視/aux/OC/隔離、部品定格、symbol/land-pattern照合を完了・人間レビュー後に本Task 4 placementを再開する。routing/Task 5への許可ではない。

**Confirmed:** Task 3 base保持、詳細回路不存在、構成承認。
**Assumption:** 既存simulationの電圧/eta/bias/temperature条件、将来4-layer案。
**TBD:** 全blocking limits・詳細回路・footprint・board size・placement・最終rules・thermal/mechanical verification。
