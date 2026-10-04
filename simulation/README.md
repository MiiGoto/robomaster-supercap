# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](../docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Task 2 calculation model

Python standard library only。power_budget.py冒頭のBank/BUS_V/power変数で3 scenariosを変更可能。C/F、V、Ω、A、W、J、sのSI単位。ηはconverterのみ、ESRを別計算。

```text
python simulation/power_budget.py --write-report
python -m unittest discover -s test -p "test_*.py"
```

results.mdは公開用の自作計算結果。runtimeは電流clippingを含みpeak ratingではない。aux/leakage/temperature/loop/transient/thermalモデルを含まず楽観値。SPICE/firmware実装ではない。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Simulation scope

Task 1ではモデル実装なし。将来の検証: bus/cap電圧の上下関係、ESR損失、cellばらつき、precharge、shutdown放電、fault時のbody-diode電流経路。
control-loop compensation、switching frequency最適化は別Task。
