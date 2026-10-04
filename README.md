# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](docs/rev_a_schematic_review.md)と[pinout](docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。



[Validation record](docs/rev_a_validation.md): ERC0/0 baseline; current counts in validation record. External assembly and cell-monitor RAM profile are selected;hardware programming/qualification remain unperformed.

## Historical records (preserved)

# Task 4 current status — placement gate未通過

2026-10-03 JST。Task 3 base428ad10を保持。重大TBDと詳細回路未実装のため添付Task 4 §1に従いplacement/outline/footprint/routingは行わない。[独立review](docs/task4_review.md)が現在status、[PCB方針](docs/task4_pcb_strategy.md)は提案、[検査結果](docs/task4_baseline.md)は既存skeleton限定。Task 5へ進まない。以下は過去Task記録。

---

# Task 3 current status

2026-10-03 JST。Task 2案はユーザー採用承認済み。実bus/surge・peak継続/間隔・ambient/coolingは未確定（ユーザー回答：不明）。承認範囲と詳細回路gateは[Task 3 review gate](docs/task3_review_gate.md)を優先する。Task 3は候補評価まで進行中、詳細回路未実装。以下のTask 2承認待ち表示は承認範囲についてhistorical record。

---

# robomaster-supercap — Task 2

2026 RMUL用energy bufferの設計検討。英雄・歩兵・哨兵の競技assistが対象、EngineerはS5搭載許可対象外。Task1成果を保ち、Task2 architecture proposal・simulation・9-page KiCad conceptを追加。完成/検証済み回路ではない。

- [Requirements/status](requirements.md)
- [Architecture and 11 modes](docs/architecture.md)
- [Evidence and selected proposals](docs/task2_decisions.md)
- [Calculation results](simulation/results.md)
- [Safety](docs/safety.md) / [FMEA](docs/fmea.md)

第一案は9S 50F、4-switch bidirectional buck-boost、G474RE/LQFP64、signed high-side shunts、independent fault latch。全選定案はAssumptionとしてhuman review待ち、robot実bus/power/thermalはTBD。stored energyはOFF後も残る。
Roadmap: Task1完了→Task2 reviewable proposal→人間承認→別途Task3 component selection。mainへ自動mergeしない。詳細回路・routing・firmware・hardware testingなし。第三者PDF等は公開対象外、引用linkと出典のみ。

---

## Task 1 record (historical; Task 2 above takes precedence)

# robomaster-supercap

RoboMaster向けスーパーキャパシタ電源システムの要求・安全設計と開発基盤。
robot busの余剰energyを蓄え、必要時にassistし、状態監視とCAN通信を行う。

## Architecture

Robot Power Bus ⇄ Input Protection ⇄ Bidirectional Power Converter ⇄ Supercapacitor Bank。
MCUはbus/bank voltage、current、temperature、faultを監視する。独立保護がgate enableを拒否できる構成を要求する。
競技用の公式管理モジュール・検査経路を含む実接続は適用規則確認後に決める。

## Repository structure

```text
README.md / AGENTS.md / PROJECT_CONTEXT.md
requirements.md / references.md
hardware/kicad/        block-level project skeleton
firmware/controller/  future firmware requirements
simulation/           future model scope
docs/                 architecture, comparison, safety, FMEA, bringup
test/                 verification plan and publication audit
```

## Safety notice

蓄積energyは電源OFF後も残る。短絡・cell過電圧・逆流・熱暴走・connector arcを設計要件として扱う。
このrepositoryは通電可能な完成回路、製造データ、検証済みシステムを提供しない。
KiCad ERCが通っても、部品・netがないskeletonの安全性や動作は証明しない。

## Current status

Task 1文書とKiCad skeleton。詳細power stage、PCB layout、firmware、prototypeは未着手。
Confirmed / Assumption / TBDはPROJECT_CONTEXTとrequirementsに明示。
環境確認は [environment](docs/environment.md)、調査は [comparison](docs/reference_comparison.md)。

## Reference policy

外部設計は設計意図を比較し、[references.md](references.md)へ記録する。
外部回路図・PCB・PDF・画像・コードは取り込まない。ライセンスの衝突・不明点も記録する。
本プロジェクトの公開ライセンス選択はTBD。PUBLICであることだけで再利用許諾とはしない。

## Roadmap

1. Task 1: environment / repository / research / requirements / safety / KiCad skeleton。
2. 人間レビュー: 競技適用、robot仕様、capacitor候補、限界値、topology。
3. 承認後の別Task: 詳細回路、独立保護の検証、制御設計。
4. その後: PCB / firmware / 段階的bringup / fault injection / robot統合。

Task 2は自動開始しない。
