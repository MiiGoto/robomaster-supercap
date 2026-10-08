# Firmware implementation — 2026-10-08

Current: Rev A STM32G474RET6 firmware source implemented; default SAFE_MONITOR_ONLY. Host logic tests and ARM builds are recorded in docs/firmware_validation.md. No flash, option-byte write, real PWM/contact actuation or energizing was performed. Hardware/CAD is unchanged. Calibration, control gains, timing, BQ physical behavior and power limits require bench measurement and human review before first flash/energizing.

Current guides: [firmware architecture](../docs/firmware_architecture.md), [operation](../docs/supercap_user_guide.md), [commissioning](../docs/firmware_commissioning.md), [CAN protocol](../docs/can_protocol.md), [tuning](../docs/control_tuning.md), [flash setup](../docs/firmware_flash_setup.md).

## Historical records (preserved)

# PCB routing complete — 2026-10-07

**Current: Prototype Rev A CAD routing complete.** KiCad10.0.6の正式PCBでnative未接続0、全DRC0 errors/0 warnings、schematic parity0、ERC0 errors/0 warningsを確認した。全331ネット／1524 net-assigned pad recordsの物理接続と、設計manifestの1478 pad/net assignmentsを照合済み。これはCAD接続・規則検証であり、製造リリース、通電許可、120 W性能、競技適合の承認ではない。

一般銅箔間隔0.20 mm、承認済み39 ICの同一部品内Pad/Pad0.15 mmを維持した。新たなDRC除外・No ERC・規則緩和はない。未コミットの`.kicad_pro`設定展開は保持し、functional commitに含めない。詳細は[配線完了記録](../docs/pcb_routing_completion.md)を現在の情報源とする。以下は過去時点の記録として保存する。

## Historical records (preserved)

# PCB engineering authorized — 2026-10-04

ユーザーがsurge・OC遮断時間・fuse/接触器協調・熱・放電時間の実測前にPCB配置/配線へ進むことを明示承認した。[現行PCB記録](../docs/pcb_rev_a.md)を優先する。未実測の項目はPrototype Assumptionとして保持し、製造/通電/性能保証にはしない。以下の「PCB未承認/開始しない」は過去時点の記録として残す。

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](../docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Firmware status — Prototype Rev A

No firmware implementation. Adopted STM32G474RE/LQFP64 pin allocation and default-off protections are in [pinout](../docs/pinout.md) and [schematic review](../docs/rev_a_schematic_review.md). Future work: HRTIM timing/ADC synchronization, BQ supercap provisioning/readback, watchdog health/CAN lease, control loops, precharge/dump/contact interlocks and fault state machine. BOOT0/NRST options and cell monitor profile must be reviewed before any energizing. Hardware latch protection is not optional. Historical firmware requirements remain in [controller README](controller/README.md).

Cell monitor RAM profile now exists in config/bq76942_rev_a.json;check_cell_profile.py is offline arithmetic only. Firmware has not been implemented or flashed.
