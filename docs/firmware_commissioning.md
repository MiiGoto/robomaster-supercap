# Rev A commissioning checklist

All phases below are **NOT EXECUTED**. A FAIL or missing evidence prevents the next phase. Review exact hardware revision, firmware commit/hash, mode, calibrated instruments, supply limits and independent disconnect before each energized phase. Firmware tests alone do not authorize energizing.

|Phase|Checklist / PASS|FAIL / stop condition|
|---|---|---|
|0 no power review|[ ] CAD/BOM/pinout, polarity, body-diode paths, fuse/contactors, safe defaults, firmware build and tests reviewed; bank/links independently discharged|Any unexplained connection, rating or software discrepancy|
|1 programming/options|[ ] Human-approved SAFE artifact; SWD wiring; nSWBOOT0/nBOOT0/NRST_MODE readback; no actuator supply|Unexpected options/boot, probe backfeed, outputs asserted|
|2 3.3 V auxiliary only|[ ] Rail/startup/reset current and all requests/PWM LOW; no bank/contact power|Rail fault, reset loop, unexpected output|
|3 BQ/sensors|[ ] Cell simulator mapping1..8+10;39 entries readback/CRC; tap disconnect tests; DCHG/DDSG polarity; ADC/NTC ranges/invalid detection; calibration documented|CRC/config error, any tap fault not inhibited, wrong scaling/sign|
|4 CAN/UART|[ ] v1 parsing/scales/freshness; read-only CLI; timeout/replay/rearm tests|Unauthorized command, stale lease accepted, raw dangerous CLI|
|5 hardware fault without energy|[ ] PA12 forces PWM inactive before ISR; latch/rail/watchdog/reset tests; heartbeat stops on main stall|Software-only shutdown or unwanted restart|
|6 precharge low energy|[ ] Current-limited source; bothlink voltage/current behavior;ΔV<1 V stable;3 s timeout; stuck bypass/contact faults tested|Inrush, backfeed, reserved FB wrongly assumed contact position|
|7 gate waveforms without high-energy bank|[ ] Reviewed non-SAFE permissions; polarity/deadtime/bootstrap/ADC phase; fault response; ISR budget measured|Shoot-through, edge sampling, timing overrun, unexpected arm|
|8 low-voltage converter|[ ] External limited energy/current; signed IL loop bothdirections; conservative gains; body-diode/isolation behavior|Instability, current/sign fault, failed disconnect|
|9 gradual current increase|[ ] Logged ramp steps, current ripple, shunt/connector temperatures, externalOC response and fuse coordination|Trip threshold/delay uncertain, component stress, overrun|
|10 thermal validation|[ ] Worst ambient/airflow/pulse/repetition measured; thermal lag/derating/cooldown verified; discharge/rebound independently measured|Any limit not met or residual-energy indication unreliable|
|11 full envelope review|[ ] Human signs measured surge, OC delay, fuse/contactors, thermal/current/power, shutdown/service evidence and robot/rules compatibility|Unmeasured assumptions or legal/interface mismatch|

Do not begin at22 V/fullbank/120 W. External hardware protection and meter/disconnect remain required throughout. AEV14012 feedback inputs are reserved diagnostics, not proof of contact opening. Flash/update/debug instructions are in `firmware_flash_setup.md`; future authorization is required before performing them.
