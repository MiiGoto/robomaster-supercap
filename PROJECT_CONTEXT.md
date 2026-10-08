# Firmware implementation — 2026-10-08

Current: Rev A STM32G474RET6 firmware source implemented; default SAFE_MONITOR_ONLY. Host logic tests and ARM builds are recorded in docs/firmware_validation.md. No flash, option-byte write, real PWM/contact actuation or energizing was performed. Hardware/CAD is unchanged. Calibration, control gains, timing, BQ physical behavior and power limits require bench measurement and human review before first flash/energizing.

Current guides: [firmware architecture](docs/firmware_architecture.md), [operation](docs/supercap_user_guide.md), [commissioning](docs/firmware_commissioning.md), [CAN protocol](docs/can_protocol.md), [tuning](docs/control_tuning.md), [flash setup](docs/firmware_flash_setup.md).

## Historical records (preserved)

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



[Validation record](docs/rev_a_validation.md): ERC0/0;467 actual components; PCB unchanged. External interruption assembly and supercap monitor configuration remain unfinished.

## Historical records (preserved)

# Task 4 current status — placement gate未通過

2026-10-03 JST。Task 3 base428ad10を保持。重大TBDと詳細回路未実装のため添付Task 4 §1に従いplacement/outline/footprint/routingは行わない。[独立review](docs/task4_review.md)が現在status、[PCB方針](docs/task4_pcb_strategy.md)は提案、[検査結果](docs/task4_baseline.md)は既存skeleton限定。Task 5へ進まない。以下は過去Task記録。

---

# Task 3 current status

2026-10-03 JST。Task 2案はユーザー採用承認済み。実bus/surge・peak継続/間隔・ambient/coolingは未確定（ユーザー回答：不明）。承認範囲と詳細回路gateは[Task 3 review gate](docs/task3_review_gate.md)を優先する。Task 3は候補評価まで進行中、詳細回路未実装。以下のTask 2承認待ち表示は承認範囲についてhistorical record。

---

# Project context — Task 2

2026-10-03 JST。2026 RMUL、哨兵・歩兵・英雄・エンジニアをユーザー指定。S5によりEngineerへの競技底盤supercap assistは対象外。開催地/種目、battery/robot実bus/assist requirementはTBD。
Task1はmainの077fd5fまで、Task2はfeature/system-architecture。今回要求refinement、根拠付きproposal、energy/power計算、sensing/MCU/safety、同一KiCad project更新まで。詳細power stage/PCB/firmware/通電なし。
[requirements freeze](requirements.md)と[proposal](docs/task2_decisions.md)を最優先に読む。人間レビュー前の採用案はAssumption。cell数/Vcap/max current/peak power/topology/MCU/sensing/prechargeと全component定格を承認してから詳細回路へ進む。Task3自動開始禁止。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Project context

更新: 2026-10-03 (Asia/Tokyo)。Task 1: 調査・要求・安全・構成・KiCad skeletonのみ。

RoboMasterロボット用スーパーキャパシタのエネルギーバッファを自作する。robot power busから充電し、必要時にrobotへ供給する。capacitor stateを監視し、charge/dischargeを制御し、CAN等でrobot controllerと通信し、安全状態を維持する。

## Evidence status

- **Confirmed**: ユーザーが要求した目的・Task 1 scope・人間レビューgate。これは検証済みハードウェア性能を意味しない。
- **Assumption**: 非絶縁の双方向power flow、STM32によるデジタル制御を比較の出発点とする。採用決定ではない。
- **TBD**: 対象大会・年・地域・ロボット種別、適用規則最新版、robot bus仕様、capacitor候補、全定格、topology、実装・試験。

要求は [requirements.md](requirements.md)、危険分析は [safety](docs/safety.md) と [FMEA](docs/fmea.md)。公式規則は版・条項・適用範囲を確認し、過年度値や他チームの実績値を本仕様に移さない。

## Human review gate

maximum bus voltage、capacitor maximum voltage、cell count、maximum charge/discharge current、maximum output power、converter topology、MOSFET定格、inductor定格、fuse定格、connector定格は人間レビューなしに確定しない。

Task 1で詳細MOSFET選定、gate driver回路、inductor sizing、switching frequency最適化、補償、PCB routing、高電流銅箔設計、firmware実装、物理prototype試験を行わない。Task 2へ自動移行しない。
