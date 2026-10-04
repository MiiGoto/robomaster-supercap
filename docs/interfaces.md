# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A concrete interfaces

| Signal | Direction | Domain/type | Fail-safe default |
|---|---|---|---|
| PWM_AH/AL/BH/BL |MCU→AND→driver|3.3V digital|pulled LOW / GATE_PERMIT veto |
| GATE_PERMIT |latch+fault chain→EN/AND|3.3V digital|LOW, no automatic rearm |
| HW_FAULT_N |hardware→PA12 FLT1|3.3V active LOW|fault on missing permit |
| ARM_PULSE / MCU_GATE_REQUEST |MCU→safety|3.3V digital|LOW |
| BUS/CAP/IL_I_ADC |INA240→RC→TMUX→MCU|0..3.3V analog|off isolated/100k drain |
| BUS/CAP_V_ADC and RAW_ADC |divider/clamp→TMUX→MCU|0..3.3V analog|off isolated; loaded gain |
| TEMP_FET/L/BANK |NTC→window+TMUX→MCU|3.3V analog|open/short inhibit |
| MON_DCHG/DDSG |BQ→safety|REG1 3.3V permission|pull-down, provisioning required |
| MON_CONFIG_VALID |MCU→safety|3.3V digital|LOW until verified profile |
| SPI2 / MON_ALERT |MCU↔BQ|3.3V digital, initial1.8V MISO shifted|disconnect when either rail absent |
| PRE/BYP/ISO requests and feedback |MCU↔external actuators|3.3V control, separate12V coils|requests LOW / NO contacts |
| DUMP_REQUEST |MCU→thermal qualification→gate|3.3V request /12V gate|OFF; bleed remains |
| CAN TX/RX/RS |MCU↔transceiver|3.3V digital|TX HIGH, RS standby |

Exact physical pins/AFs: [pinout](pinout.md). Shared GND, source-return integrity and power-off injection remain review gates; no galvanic isolation claim.


## Historical records (preserved)

# Task 2 block interface contract

logic3.3 V/ADC reference3.3 VはAssumption。pin/connector、protection、absolute ratingsはTBD。interface名はblock仕様、KiCad net未実装。

| Signal | Direction | Domain / analog-digital | Fail-safe default |
|---|---|---|---|
| PWM_A1/A2/B1/B2 | MCU→driver | 3.3 V digital | driver killed、all gates OFF |
| MCU_GATE_ENABLE | MCU→safety AND driver | 3.3 V digital request | external bias OFF、float不可 |
| DRIVER_KILL | latch→drivers | driver logic compatible / digital TBD | asserted at reset/aux loss/fault |
| POWER_STAGE_FAULT | latch→MCU HRTIM/interrupt | 3.3 V digital, polarity TBD | missing safety supply treated fault |
| OC_TRIP / BANK_OV / CELL_OV | protection→latch | comparator/monitor domain TBD | active fault priority、MCU override不可 |
| BUS_V_SENSE / CAP_V_SENSE | front-end→ADC | protected analog0.2..3.1 V proposal | invalid/saturation→inhibit |
| BUS_I / CAP_I / INDUCTOR_I | amplifier→ADC | signed analog centered reference | invalid→inhibit、fast OC separate |
| CELL_SPI + CELL_ALERT | MCU↔monitor / monitor→latch | 3.3 V interface、cell side rated separately | open-wire/stale/fault→charge禁止 |
| TEMP_FET / TEMP_L / TEMP_BANK | NTC front-end→ADC | protected analog | open/short→fault |
| PRECHARGE_REQUEST / MAIN_CLOSE / CAP_CONNECT | MCU→interlock | 3.3 V digital→power domain | normal OFF、feedback必要 |
| MAIN_FEEDBACK / PRECHARGE_DV | isolation/sense→MCU | digital / protected analog | unknown→no arm |
| DISCHARGE_REQUEST | MCU→thermal interlock→dump | 3.3 V digital | OFF、permanent bleed independent |
| WATCHDOG_HEARTBEAT | MCU→external supervisor | 3.3 V digital | absent/stuck→kill |
| FDCAN_TX/RX | MCU↔transceiver | 3.3 V digital | transceiver recessive、stale→inhibit |
| CANH/L/reference | transceiver↔robot | CAN physical domain TBD | no command permits no transfer |
| Official module CAN | module↔referee CAN1 | official interface | offline inhibits competition operation |
| SWD/UART | debugger↔MCU | 3.3 V reference | debugger halt inhibits stage |

Initial telemetry: Vbus/Vbank/cell min/max/delta、signed bus/cap/inductor current、bus instantaneous power、stored/usable energy/SOEとcalibration validity、FET/L/bank temperatures、mode、fault class/flags/latched cause、precharge/disconnect feedback、reset cause。ID/bit layout/bitrate/update rate/timeoutはTBD。SOE=usable energy fraction、battery SOCとは異なる。
commandsはfresh counter付きlimits/enable/shutdown/rearm request。classic CAN互換を提案、CAN-FDをrobot側へ仮定しない。hardware latchはcommandでは解除不可、再armは原因消去+self-test+明示承認。

---

## Task 1 record (historical; Task 2 above takes precedence)

# Interfaces

物理connector、pin番号、定格、termination、isolated/nonisolatedはTBD。Task 1はsignal契約のみ。

| Interface | Required candidate signals / behavior | Unresolved |
|---|---|---|
| Robot power | bus+/return、polarity確認、inrush / backfeed制限 | voltage/current/connector、公式計測点 |
| Bank | bank+/return、cell monitor、service-safe手段 | single power port規則、tap保護、cell数 |
| MCU ↔ driver | PWM、enable(default OFF)、fault、UVLO状態 | polarity、timing、deadtime、pull network |
| Independent safety | fast OC、cell/bank OV、latched trip、explicit clear | channels、common cause、閾値 |
| Sensing | bus/bank V、signed current、selected temperature | ranges、ADC reference、calibration |
| CAN | external transceiver、CANH/L/reference、ESD、termination管理 | ID/bitrate/pinout/update/timeout |
| Debug | SWDIO/SWCLK/NRST/VTref/GND、UART | connector、levels、halt shutdown |

## Telemetry candidates

bus voltage、bank voltage、cell min/max/imbalance、signed bus/bank current、stored energy estimate、usable energy estimate、温度とsensor location、fault bitmask/latched cause、operating mode、enable state、precharge/discharge state、sensor validity、uptime/reset cause、protocol/calibration version。

Energy estimateはCとVの不確かさ・ESR・温度・劣化を伴う。未校正時にverified値として送らない。
commandsはenable request、charge/assist limit、shutdown、explicit fault reset候補。CAN commandはhardware safetyをoverride不可。
freshness counter/timeout、range validation、bus-off、起動直後のstale frameを扱う。期限切れはinhibit、復帰だけで再armしない。
FDCAN peripheral採用でもClassic CAN互換frameを選べる。CAN-FD対応をrobot側に仮定しない。
公式management module CANと独自controller telemetryは別interfaceとして、最新版規則の接続要求を確認する。
