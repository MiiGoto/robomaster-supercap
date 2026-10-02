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
