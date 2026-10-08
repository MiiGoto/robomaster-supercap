# Firmware implementation — 2026-10-08

Current: Rev A STM32G474RET6 firmware source implemented; default SAFE_MONITOR_ONLY. Host logic tests and ARM builds are recorded in docs/firmware_validation.md. No flash, option-byte write, real PWM/contact actuation or energizing was performed. Hardware/CAD is unchanged. Calibration, control gains, timing, BQ physical behavior and power limits require bench measurement and human review before first flash/energizing.

Current guides: [firmware architecture](../../docs/firmware_architecture.md), [operation](../../docs/supercap_user_guide.md), [commissioning](../../docs/firmware_commissioning.md), [CAN protocol](../../docs/can_protocol.md), [tuning](../../docs/control_tuning.md), [flash setup](../../docs/firmware_flash_setup.md).

## Build and tests

Project-authored source: Core (HAL adapters), App (portable logic), config (reviewed defaults/profile), tests (host emulator). External unmodified HAL/device/CMSIS versions and licenses: Drivers/README.md. No automatic downloads, installs, flash or hardware operations exist in build targets.

Host (Linux/WSL GCC or another supported C11 GCC/Clang installation):

```sh
cmake -S firmware/controller -B build/firmware-host
cmake --build build/firmware-host -j 4
ctest --test-dir build/firmware-host --output-on-failure
python -B firmware/controller/tools/generate_bq_profile.py --check
python -B firmware/controller/tools/test_profile.py
```

ARM (set external paths to the pinned sources; Ninja optional):

```sh
cmake -S firmware/controller -B build/firmware-arm -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=cmake/arm-gcc.cmake \
  -DARM_TOOLCHAIN_BIN=/path/to/arm-tools/bin \
  -DHAL_ROOT=/path/to/hal -DDEVICE_ROOT=/path/to/device -DCMSIS_ROOT=/path/to/cmsis \
  -DFW_MODE=SAFE_MONITOR_ONLY
cmake --build build/firmware-arm -j 4
```

Windows: use `tools/build_windows.ps1` with explicit `-CMake`, `-Ninja`, `-ArmTools`, `-HalRoot`, `-DeviceRoot`, `-CmsisRoot` paths. It uses temporary ASCII junctions because the tested Ninja cannot resolve the Unicode checkout path. It never removes/replaces an existing alias and never moves the checkout. `-Mode` defaults SAFE_MONITOR_ONLY; select a new `-AliasRoot` if an existing alias belongs to another checkout. Output is ELF/HEX/map under the alias build directory, not programmed into a board.

Project code uses -Wall/-Wextra/-Werror; vendor code is separately compiled without -Werror. Host builds execute all three modes with mocked hardware permissions; those test fixtures do not change production default permissions. Optional host sanitizer configuration (tested WSL non-PIE executable, add `-DCMAKE_EXE_LINKER_FLAGS=-no-pie`): `-DCMAKE_C_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie"`.

Native connectivity audit: export a local-only KiCad S-expression netlist, then `python -B firmware/controller/tools/check_hardware_contract.py path/to/export.net`. Do not commit native exports containing absolute local paths. The audit checks47 U11 physical assignments plus ADC/AF sentinels; it is not a hardware timing test.

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](../../docs/rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../../docs/rev_a_schematic_review.md)と[pinout](../../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。



## Historical records (preserved)

# Controller firmware placeholder

実装なし。STM32G4 / F334を比較中。型番・pinout・toolchain projectはTBD。
将来: boot self-test → precharge → charge/standby/assist → fault/shutdown。
PWM同期ADC、current loop、hardware fault inputs、watchdog、CAN timeout、telemetry、calibration管理を分離する。
起動・reset・crashでenable OFF。ISR時間予算と通信処理の分離を検証する。
SWD halt時のPWM継続も危険として扱う。デバッグで保護を無効化しない。
