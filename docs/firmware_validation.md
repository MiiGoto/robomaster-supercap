# Firmware validation — 2026-10-08 JST

Scope: code/build/PC tests only, routing-complete hardware base `f38ec4f`; branch `feature/stm32-firmware-rev-a`. No flash, option-byte write, energizing, actual PWM, contactor actuation, bank/robot connection or physical testing.

## Confirmed software evidence

|Check|Result|
|---|---|
|ARM GCC12.3.1 / CubeIDE1.15.1; CMake3.25 / Ninja|All three modes build; project -Wall/-Wextra/-Werror; compiler/linker warnings0|
|SAFE_MONITOR_ONLY size|text34168,data100,bss12324 bytes; Flash/RAM fit linker512 KiB/96 KiB|
|LOW_ENERGY_COMMISSIONING size|text36736,data100,bss18004 bytes|
|POWER_STAGE_CONTROL size|text36736,data100,bss18004 bytes|
|SAFE linked symbol inspection|No HAL_HRTIM_WaveformOutputStart, malloc, free or _sbrk symbol; GPIO LOW and runtime veto also reviewed|
|Host GCC11.4 / WSL Ubuntu22.04|SAFE339 assertions; LOW363; POWER363; CTest3/3 PASS|
|ASan+UBSan non-PIE host build|3/3 PASS; -fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie, linker-no-pie; no sanitizer finding|
|Cppcheck warning/performance/portability C11, App/config|0 findings|
|BQ profile generator --check|39 entries match JSON; widths/addresses/LE values/cell mask/policy checks PASS|
|Profile corruption/schema tests|6 checks PASS, including wrong part, value, length, duplicate address, OTP policy rejection|
|Native KiCad netlist contract|47 U11 physical pin/net assignments PASS; AF/ADC rank sentinels present|
|Hardware preservation|PCB SHA256 unchanged; pre-existing dirty kicad_pro SHA256 unchanged; no schematic/PCB edits staged|

Host tests cover legal/illegal transitions, fault latching/rearm, command CRC/ranges/replay/wrap/timeouts, mapping, SOE, NTC/scaling/calibration CRC, precharge total timeout, cooldown, peak transition bookkeeping, balance selection/settling eligibility, telemetry/CLI, and behavioral BQ initialization/CRC/readback/loss. Mock BQ behavior is an explicit model, not actual IC verification. Test-only calibration/tuning permissions do not alter production defaults.

ASan+UBSan PIE build first passed all modes, but a subsequent run stalled/repeated DEADLYSIGNAL without a useful code-location report. That run was stopped; root cause is not established. The separate non-PIE configuration above completed all modes. Do not report universal sanitizer/platform stability. CTest now has10 s per-test timeout. Existing WSL configuration warning `boot.generateResolvConf` was observed; no WSL/system settings were changed.

Local full build/test logs and external sources remain ignored. This public summary omits absolute user paths and does not include binaries, manufacturer PDFs, private netlist exports or third-party source files. Reproduction commands are in `firmware/controller/README.md`; pinned external licenses/commits are in its `Drivers/README.md`.

## Review observations / remaining measurements

- Hardware async PA12 fault precedes software; software error also clears gate/ARM/contact requests. Shared hardware input cannot uniquely identify OC; SW current guards and generic fault flags are distinguished in documentation.
- Exact ADC channel ranks, shunt signs and divider/100 kOhm drain loading follow the actual schematic. ISR/foreground ownership uses short critical sections; nested pending fault updates cannot lose bitmask changes. CPU timing and calibration accuracy remain unmeasured.
- Startup LOW precedes output-mode setup; default SAFE cannot assert actuators. Other modes still require reviewed calibration/tuning/commissioning flags. CAN alone cannot grant these flags.
- BQ RAM readback/CRC and mapping are implemented. DCHG/DDSG polarity, ALERT cause behavior, reset/status interpretation, open-wire tap coverage and SPI timing require a cell simulator. COW cycle observation is not proof of every tap connection. No OTP/FET test commands; FET_EN toggle is guarded by readback.
- Precharge has one3 s budget across phases; voltages/current/time determine acceptance. Reserved feedback levels do not establish contact position. Physical contactor delays, stuck/welded failure, resistor pulses and isolation/fuse coordination remain untested.
- Signed IL PI and power-demand framework are implemented, but initial gains, feedforward, efficiency, sample phase, deadtime, ripple, measured power accuracy and200 kHz IRQ budget are **PROTOTYPE_TUNING_REQUIRED**.
- Charge40 W/assist80 W/peak120 W are requests, not demonstrated power. Initial cap/IL9.5 A limits and thermal thresholds are conservative software targets, not verified operating boundaries. Peak1 s/30 s and thermal lag/ambient/cooling require review and measurement.
- Service dump is separately gated/default forbidden; BQ/hardware UV may stop it before discharge completes. Independent service discharge/meter and2 min rebound observation are necessary. No claim of guaranteed discharge time or energy isolation.

Before first flash: review pinout/options/SWD/backfeed, SAFE artifact/hash, dependency revisions and GPIO/peripheral setup. Before first energizing: complete commissioning phases and approve external protections, waveform/timing, calibrated sensors, surge/OC/fuse/contactors, thermal and service measurements. No hardware permission is implied by passing these software tests.

CAN queue entries carry ISR receive timestamps. Expired queued commands cannot become fresh through delayed foreground processing; accepted leases retain their receive timestamp. Additional boundary tests cover this behavior.
