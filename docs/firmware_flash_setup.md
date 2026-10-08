# Rev A programming setup — 2026-10-08

Status: procedure only. No probe connection, flash write or option-byte write was performed. First flash requires human review of the exact PCB, firmware ELF, power isolation and this checklist.

1. Disconnect robot, capacitor bank and external contactor power. Independently verify absence of stored energy. A programmer can backfeed the 3.3 V rail; review probe supply/target-sense wiring first.
2. Review `docs/pinout.md`, U11 STM32G474RET6/LQFP64 and SWD connector orientation. Use SWDIO PA13, SWCLK PA14, NRST, GND and target voltage sense. Do not assume connector pin numbers from another board.
3. Read and archive existing option bytes with STM32CubeProgrammer. Do not run an automated option-byte script. PB8 is FDCAN RX and can idle HIGH; it must not select system boot.
4. Human-check `nSWBOOT0=0`, `nBOOT0=1` (software-controlled BOOT0 LOW / main Flash boot). Read the installed tool's decoded descriptions against STM32G474 RM0440; do not paste an undocumented packed register value.
5. Keep PG10 as reset input/output: `NRST_MODE=3`. Do not repurpose the physical NRST pin as GPIO. Preserve unrelated RDP, WRP, BOR and boot settings; separately review any required change.
6. Select the **SAFE_MONITOR_ONLY** artifact. Review map, vector table at 0x08000000, 512 KiB Flash, contiguous 96 KiB SRAM, defaults `verified=false`, `tuning_verified=false`, `commissioning_authorized=false`.
7. Only after explicit human approval, program and verify Flash. Reset initially with actuator/bank power physically disconnected. Record firmware revision, artifact hash and option-byte readback.

Debug halt is not energy isolation. Firmware contains no automatic option-byte programming or flash calibration writes. Do not disable external protection/watchdogs to make a debug session continue.

Sources: [STM32G4 RM0440](https://www.st.com/resource/en/reference_manual/dm00355726.pdf), [STM32G474 product documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html). Exact board pin nets remain authoritative.
