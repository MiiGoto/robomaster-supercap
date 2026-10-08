# Rev A firmware architecture — 2026-10-08

Project-authored C11, HAL peripheral adapters, no RTOS or runtime allocation. Hardware remains unchanged. Routing-complete base: `f38ec4f`. Board U11 pin/net assignments were read from the native KiCad netlist; PC5 REFEREE_PERMIT is additionally implemented. Exact package pins are in `pinout.md`; board GPIO grouping and ADC rank lists are in `Core/Src/board.c`.

## Ownership / scheduling

|Layer|Responsibility|
|---|---|
|External protection + HRTIM FLT1|Asynchronous inactive PWM before ISR; cannot be overridden by a command|
|ADC2 DMA ISR|Latest signed IL, independent software instantaneous guard, PI/duty update; no SPI/CAN/printf/heap|
|ADC1 DMA ISR|Publish latest six-channel scan; foreground conversion|
|Main loop|BQ SPI, conversion, supervisor, CAN parser/telemetry, UART, log, watchdog heartbeat|
|Board safety adapter|Second runtime output veto and default-safe GPIO; short critical sections publish ISR demand/snapshots|

HSI16 PLL gives170 MHz CPU/HRTIM; ADC42.5 MHz. HRTIM master period27200 at×32 gives200 kHz, A/B complementary outputs with provisional deadtime34 fDTG ticks, preload and inactive fault levels. ADC trigger compare6800 is adjustable. ADC1 ranks: CH1 BUS_V,CH2 CAP_V,CH6 TEMP_FET,CH7 TEMP_L,CH8 TEMP_BANK,CH9 BUS_RAW. ADC2 ranks: CH3 IL,CH17 BUS_I,CH13 CAP_I,CH5 CAP_RAW. HAL rank enums are explicit, not assumed arithmetically contiguous. ADC1 circular96 halfword buffer reduces callback rate; ADC2 circular8 halfwords supplies one four-channel frame per half/full callback. Buffers reside in contiguous SRAM, not CCM.

SPI2 mode0/CRC uses~664 kHz; USART2 115200/8N1 interrupt RX/TX; FDCAN1 Classic500 kbit/s. HRTIM timers/ADC triggers may run for sensing in SAFE, but PWM pins remain GPIO LOW and waveform output start is not reachable. Startup sets output latches LOW before configuring output modes. CS and CAN standby start HIGH. CAN standby later becomes LOW for diagnostics.

External heartbeat toggles PB1 only after a completed foreground iteration, about50 ms; IWDG timeout is~1 s nominal LSI. No timer perpetually feeds the watchdog while foreground is stalled. Reset cause is recorded; reset never resumes a power session. HardFault/error handlers stop requests and await watchdog reset. Debug halt is not a safe operating state.

## Allowed transitions

All states may enter FAULT_LATCHED on a fault. Other unlisted transitions are rejected.

|From|To|Gate / condition|
|---|---|---|
|BOOT_SAFE|MONITOR_INIT|All actuators OFF|
|MONITOR_INIT|SELF_TEST|Profile configured/readback, healthy measurements; timeout fails|
|SELF_TEST|DISARMED|Self-test PASS; never auto-ARM|
|DISARMED|PRECHARGE|Explicit ARM + reviewed mode/calibration/tuning/permissions|
|DISARMED|SELF_TEST / SERVICE|Explicit reviewed command/path; dump default forbidden|
|PRECHARGE|READY|BothlinkΔV<1 V stable, bypass settles, resistor paths removed within3 s|
|PRECHARGE|SHUTDOWN|DISARM/SHUTDOWN|
|READY / STANDBY|CHARGE / ASSIST / STANDBY / SHUTDOWN|Fresh command and hardware/sensor permissions|
|CHARGE / ASSIST|STANDBY / SHUTDOWN|No direct direction reversal|
|SHUTDOWN|DISARMED / COOLDOWN / SERVICE|Gate OFF first; bounded zero-current observation; outputs OFF|
|COOLDOWN / FAULT_LATCHED|SELF_TEST|Cause absent, cooled, explicit REARM; then fresh ARM|
|SERVICE|DISARMED|Explicit exit; meter confirmation independent of software|

`app_transition` checks graph legality; `app_command`, `app_live_faults` and `app_safe_outputs` apply permissions/limits. Reserved PRE/BYP/ISO feedbacks are diagnostic samples only; voltage/current/time are used for sequence acceptance. Requests are not measured contact positions.

## BQ7694204

`firmware/config/bq76942_rev_a.json` generates39 RAM entries through `tools/generate_bq_profile.py`; check mode detects stale data. CRC-8 SPI transport verifies replies/echoes with bounded retries, data-memory checksum/length and full readback. Startup confirms device0x7694, enters CONFIG_UPDATE, programs RAM, verifies every entry, exits configuration, observes measurements and periodic open-wire check, checks safety/FET permissions, and publishes MON_CONFIG_VALID last. No OTP or FET test commands exist. Manufacturing FET_EN is read before any conditional toggle, verified after; ALL_FETS_ON follows configuration/safety checks as the existing profile requires.

Logical cells0..8 map to physical channels1..8,10 (mask0x02FF), not channel9. DCHG/DDSG logical fault bits and their physical polarity must be tested with a cell simulator. COW_CHK reports a running open-wire check, not a separate proof that all taps passed. Startup observes a cycle and evaluates measurements/safety; actual tap-disconnect coverage requires bench verification. POR is sticky and not a reliable new-reset counter; mode/status, rotated readback and physical permission loss provide additional detection. BQ failure clears config validity and inhibits power; no blind automatic recovery.

Host balancing: converter OFF, valid cells, bank0–40 C, cells≥2.3 V, startΔ20 mV/stopΔ10 mV policy, one cell, ≤1 s pulse,250 ms settle then remeasure. Measurement validity/PD2 drop during a pulse/settle; this is permitted only in disarmed/service, never a powered session. Independent OV remains active; balancing is not protection.

## Control / faults / calibration

Inner signed IL PI has feedforward duty and anti-windup. Slow power-to-current supervisor applies cell/voltage/thermal/current/peak limits. Initial gains and assumed efficiency are unvalidated; current PI and measured power behavior need bench tuning. Software cap target9.5 A does not replace external~12 A OC. Fault timestamp, first state/sensor snapshot, additional bitmask and frozen64-entry RAM history are retained until reset. No high-frequency Flash logging.

Default calibration gains reflect actual divider/shunt/NTC loading but validity=false; version/CRC detects corruption, not measurement accuracy. Factory defaults plus explicit reviewed flags are used; no in-field flash storage/update. ISR owns its PI context; foreground publishes demands in short interrupt-masked sections, and ISR publishes raw samples/fault flags. Maximum IRQ cycles are tracked, with a secondary period-overrun guard. Timing, sampling and filter delay remain bench items.

Sources: [TI BQ76942 TRM SLUUBY1B](https://www.ti.com/lit/ug/sluuby1b/sluuby1b.pdf), [ST RM0440](https://www.st.com/resource/en/reference_manual/dm00355726.pdf), [ST HAL/LL UM2570](https://www.st.com/resource/en/user_manual/um2570-description-of-stm32g4-hal-and-lowlayer-drivers--stmicroelectronics.pdf). Vendor source versions/licenses are in `firmware/controller/Drivers/README.md`.

ALERT PC11 is polled to request immediate cause-register scanning; an ALERT level alone is not classified as a specific fault. Six reserved feedback levels and ALERT/referee/IRQ-cycle diagnostics are available on telemetry page12. SERVICE dump requires the same monitor/hardware permissions, freshness and a provisional40 min timeout; DISARM exits SERVICE.
