# Task 3 current status

2026-10-03 JST。Task 2案はユーザー採用承認済み。実bus/surge・peak継続/間隔・ambient/coolingは未入力。承認範囲と詳細回路gateは[Task 3 review gate](docs/task3_review_gate.md)を優先する。Task 3は候補評価まで進行中、詳細回路未実装。以下のTask 2承認待ち表示は承認範囲についてhistorical record。

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
