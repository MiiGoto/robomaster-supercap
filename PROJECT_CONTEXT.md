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
