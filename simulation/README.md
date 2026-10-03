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
