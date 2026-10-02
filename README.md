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
