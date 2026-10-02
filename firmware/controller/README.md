# Controller firmware placeholder

実装なし。STM32G4 / F334を比較中。型番・pinout・toolchain projectはTBD。
将来: boot self-test → precharge → charge/standby/assist → fault/shutdown。
PWM同期ADC、current loop、hardware fault inputs、watchdog、CAN timeout、telemetry、calibration管理を分離する。
起動・reset・crashでenable OFF。ISR時間予算と通信処理の分離を検証する。
SWD halt時のPWM継続も危険として扱う。デバッグで保護を無効化しない。
