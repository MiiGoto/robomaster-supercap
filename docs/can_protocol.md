# Rev A CAN protocol v1

Implementation: `firmware/controller/App/protocol.c`; FDCAN1 in Classic CAN, standard 11-bit IDs, 8 data bytes, 500 kbit/s, nominal sample point 80%. This is a project protocol, not a claimed RoboMaster referee protocol. Robot integration and bus ID allocation require review.

All frames: byte0 protocol version=1; byte1 sequence; byte7 CRC-8 polynomial 0x07, init0, no reflection/XOR, over bytes0–6. Multi-byte integers are little-endian. Receive filters accept command ID **0x501**. Extended IDs, RTR, FD frames and wrong lengths are rejected by the board layer/parser.

Command: byte2 opcode, byte3=0, bytes4–5 unsigned power in 0.1 W, byte6=0. Non-power commands require zero power. Accepted sequence advances by 1..127 modulo256; duplicate/backward/ambiguous sequences are rejected. A rejected command does not renew permission.

| Opcode | Meaning | Conditions |
|---|---|---|
|0|STATUS / keepalive|Read-only; valid accepted frame renews lease|
|1|ARM|DISARMED, valid calibration/tuning, commissioning permission, hardware/referee/monitor/sensor checks; unavailable in SAFE|
|2|DISARM|Controlled shutdown; never directly enables anything|
|3|CHARGE|READY/STANDBY; 0..40 W; positive IL / bus-to-bank|
|4|ASSIST|READY/STANDBY; 0..120 W request; negative IL / bank-to-bus; current/thermal/energy limits override|
|5|SHUTDOWN|Gate OFF then bounded zero-current isolation sequence|
|6|REARM|Cause gone, hardware/referee healthy, cooled; self-test then DISARMED; fresh ARM still required|
|7|STANDBY|Stop conversion; change direction through STANDBY|
|8|SERVICE|DISARMED only; default dump authorization remains false|

Send a fresh STATUS frame at least every100 ms while a power session is active. Lease expiry at250 ms disables CHARGE/ASSIST, gate/arm and latches CAN_TIMEOUT. Receiving communication again does not rearm. No CAN command overrides the external latch, calibration or build mode. Sequence resynchronization after a sender restart requires a reviewed disarmed restart/session procedure; do not disable sequence checking in operation.

Telemetry IDs **0x601 + page** (pages0..12), emitted cyclically. Byte0/1/7 follow the common header. Signed quantities below are int16; invalid/nonfinite=-32768, finite values saturate at±32767. Energy and SOE are nonnegative but use the same signed encoding. Values derived from factory calibration are estimates: inspect page3 byte6 before treating them as calibrated.

|Page|bytes2–3|bytes4–5|byte6|
|---|---|---|---|
|0|byte2 state enum; byte3 build mode|byte4 major=0; byte5 minor=1|patch=0|
|1|fault mask bytes2–5 uint32|continuation|reset cause mask|
|2|VBUS mV|VCAP mV|ADC validity|
|3|bus current mA|cap current mA|calibration validity|
|4|IL mA|bus power 0.1 W|BQ config validity|
|5|cap power 0.1 W|bank stored energy 0.1 J|BQ measurement validity|
|6|usable energy 0.1 J|SOE 0.01%|reserved0|
|7|min cell mV|max cell mV|reserved0|
|8|cell delta mV|FET temperature 0.01 C|reserved0|
|9|inductor temperature 0.01 C|bank temperature 0.01 C|reserved0|
|10|BQ Battery Status uint16|byte4 FET Status; byte5 Safety A|Safety B|
|11|byte2 output bits; byte3 precharge phase|byte4 reject-count low8; byte5 observed COW cycle|self-test pass|
|12|byte2 reserved feedback bits; byte3 ALERT asserted|maximum ADC2 IRQ cycles uint16 saturated|REFEREE_PERMIT|

Output bits0..7: pre_bus,pre_cap,iso_bus,iso_cap,bypass_bus,bypass_cap,gate,dump. These are safe-filtered requests, **not verified contact positions**. Reserved feedback inputs are not contactor auxiliary contacts.

Positive bus current means bus→converter. Positive cap current means bank→converter; positive IL means SW_A→SW_B / charging. Cap power is negative while charging. Stored energy uses CAP_RAW and nominal5.5556 F; SOE uses12–22.05 V useful range. It is not battery SOC.

State enum0..12: BOOT_SAFE,MONITOR_INIT,SELF_TEST,DISARMED,PRECHARGE,READY,CHARGE,STANDBY,ASSIST,SHUTDOWN,COOLDOWN,FAULT_LATCHED,SERVICE. Build modes0/1/2: SAFE_MONITOR_ONLY/LOW_ENERGY_COMMISSIONING/POWER_STAGE_CONTROL.

Fault bits0..23: HW_OC,HW_FAULT,BQ_CONFIG,BQ_CRC,CELL_OV,CELL_UV,CELL_IMBALANCE,TEMP_FET,TEMP_INDUCTOR,TEMP_BANK,TEMP_SENSOR_INVALID,BUS_OV,BUS_UV,CAP_OV,CAP_UV,CAN_TIMEOUT,WATCHDOG,PRECHARGE_TIMEOUT,SENSOR_INVALID,CONTACT_SEQUENCE,MONITOR_ALERT,ADC_STALE,CONTROL_TRACKING,DISCHARGE_TIMEOUT. PA12 reports shared HW_FAULT; it does not identify OC cause by itself. Reset cause bits0..5: BOR/POR-compatible cause,PIN,software,IWDG,WWDG,low-power; hardware does not separately expose every possible POR/BOR history.

All IDs, rate, scales and enum values are protocol v1. Do not deploy two devices with the same IDs without a protocol/address update and host tests.

Reserved feedback page12 bits0..5: PRE_CAP_FB,PRE_BUS_FB,BUS_ISO_FB,CAP_ISO_FB,BYP_BUS_FB,BYP_CAP_FB. Diagnostic levels are not contact-position evidence.

Reviewed SERVICE dump also requires a fresh CAN lease; DISARM exits SERVICE and stops dump. A provisional40 min timeout above1 V latches DISCHARGE_TIMEOUT; this is a stop budget, not a guaranteed discharge time.

Freshness is measured from the MCU receive-ISR timestamp, not when the main loop eventually parses a queued frame. Queue age>250 ms is rejected before command execution.
