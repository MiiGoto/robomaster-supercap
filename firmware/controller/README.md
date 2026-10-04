# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../../docs/rev_a_schematic_review.md)と[pinout](../../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。



## Historical records (preserved)

# Controller firmware placeholder

実装なし。STM32G4 / F334を比較中。型番・pinout・toolchain projectはTBD。
将来: boot self-test → precharge → charge/standby/assist → fault/shutdown。
PWM同期ADC、current loop、hardware fault inputs、watchdog、CAN timeout、telemetry、calibration管理を分離する。
起動・reset・crashでenable OFF。ISR時間予算と通信処理の分離を検証する。
SWD halt時のPWM継続も危険として扱う。デバッグで保護を無効化しない。
