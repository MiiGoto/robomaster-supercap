# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](../docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Firmware status — Prototype Rev A

No firmware implementation. Adopted STM32G474RE/LQFP64 pin allocation and default-off protections are in [pinout](../docs/pinout.md) and [schematic review](../docs/rev_a_schematic_review.md). Future work: HRTIM timing/ADC synchronization, BQ supercap provisioning/readback, watchdog health/CAN lease, control loops, precharge/dump/contact interlocks and fault state machine. BOOT0/NRST options and cell monitor profile must be reviewed before any energizing. Hardware latch protection is not optional. Historical firmware requirements remain in [controller README](controller/README.md).

Cell monitor RAM profile now exists in config/bq76942_rev_a.json;check_cell_profile.py is offline arithmetic only. Firmware has not been implemented or flashed.
