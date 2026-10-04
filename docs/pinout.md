# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A physical pinout

2026-10-03. STM32G474RET6/LQFP64. Pin numbers and AF functions checked against ST DS12288 Table12/13 and manufacturer package data. This is a schematic allocation, not firmware or PCB completion. VDD3.3V; analog0..3.3V only. HSI clock provisional. **PB8 is also BOOT0: nSWBOOT0/nBOOT0 option-bit policy must force flash boot before use; CAN idle HIGH cannot serve as a LOW boot strap.** PG10 option must enable NRST. Option programming is not implemented.

| Physical pin | Pad / schematic pin name | Signal | Function / AF | Default / note |
|---|---|---|---|---|
| 1 | VBAT | V3V3 | supply | see interface/power sequencing |
| 2 | PC13 | PRE_CAP_FB | GPIO | input / no drive |
| 3 | PC14 | NC spare | unused | see interface/power sequencing |
| 4 | PC15 | NC spare | unused | see interface/power sequencing |
| 5 | PF0 | NC spare | unused | see interface/power sequencing |
| 6 | PF1 | NC spare | unused | see interface/power sequencing |
| 7 | PG10 | NRST | reset | see interface/power sequencing |
| 8 | PC0 | TEMP_FET_ADC | ADC12_IN6 | input / no drive |
| 9 | PC1 | TEMP_L_ADC | ADC12_IN7 | input / no drive |
| 10 | PC2 | TEMP_BANK_ADC | ADC12_IN8 | input / no drive |
| 11 | PC3 | BUS_RAW_ADC | ADC12_IN9 | input / no drive |
| 12 | PA0 | BUS_V_ADC | ADC12_IN1 | input / no drive |
| 13 | PA1 | CAP_V_ADC | ADC12_IN2 | input / no drive |
| 14 | PA2 | UART_TX | AF7 USART2_TX | see interface/power sequencing |
| 15 | VSS | GND | supply | see interface/power sequencing |
| 16 | VDD | V3V3 | supply | see interface/power sequencing |
| 17 | PA3 | UART_RX | AF7 USART2_RX | see interface/power sequencing |
| 18 | PA4 | BUS_I_ADC | ADC2_IN17 | input / no drive |
| 19 | PA5 | CAP_I_ADC | ADC2_IN13 | input / no drive |
| 20 | PA6 | IL_I_ADC | ADC2_IN3 | input / no drive |
| 21 | PA7 | NC spare | unused | see interface/power sequencing |
| 22 | PC4 | CAP_RAW_ADC | ADC2_IN5 | input / no drive |
| 23 | PC5 | REFEREE_PERMIT | GPIO | see interface/power sequencing |
| 24 | PB0 | ARM_PULSE | GPIO | LOW / disabled |
| 25 | PB1 | WD_HEARTBEAT | GPIO | LOW / disabled |
| 26 | PB2 | MCU_GATE_REQUEST | GPIO | LOW / disabled |
| 27 | VSSA | GND | supply | see interface/power sequencing |
| 28 | VREF+ | VREF_ADC | supply | see interface/power sequencing |
| 29 | VDDA | VDDA | supply | see interface/power sequencing |
| 30 | PB10 | PRE_BUS_REQUEST | GPIO | LOW / disabled |
| 31 | VSS | GND | supply | see interface/power sequencing |
| 32 | VDD | V3V3 | supply | see interface/power sequencing |
| 33 | PB11 | BYP_BUS_REQUEST | GPIO | LOW / disabled |
| 34 | PB12 | MON_CS_HOST | GPIO | see interface/power sequencing |
| 35 | PB13 | MON_SCLK_HOST | AF5 SPI2_SCK | see interface/power sequencing |
| 36 | PB14 | MON_MISO_HOST | AF5 SPI2_MISO | see interface/power sequencing |
| 37 | PB15 | MON_MOSI_HOST | AF5 SPI2_MOSI | see interface/power sequencing |
| 38 | PC6 | BUS_ISO_REQUEST | GPIO | LOW / disabled |
| 39 | PC7 | CAP_ISO_REQUEST | GPIO | LOW / disabled |
| 40 | PC8 | PRE_CAP_REQUEST | GPIO | LOW / disabled |
| 41 | PC9 | BYP_CAP_REQUEST | GPIO | LOW / disabled |
| 42 | PA8 | PWM_AH | AF13 HRTIM_CHA1 | LOW / disabled |
| 43 | PA9 | PWM_AL | AF13 HRTIM_CHA2 | LOW / disabled |
| 44 | PA10 | PWM_BH | AF13 HRTIM_CHB1 | LOW / disabled |
| 45 | PA11 | PWM_BL | AF13 HRTIM_CHB2 | LOW / disabled |
| 46 | PA12 | HW_FAULT_N | AF13 HRTIM_FLT1 active LOW | see interface/power sequencing |
| 47 | VSS | GND | supply | see interface/power sequencing |
| 48 | VDD | V3V3 | supply | see interface/power sequencing |
| 49 | PA13 | SWDIO | AF0 SWDIO | see interface/power sequencing |
| 50 | PA14 | SWCLK | AF0 SWCLK | see interface/power sequencing |
| 51 | PA15 | PRE_BUS_FB | GPIO | input / no drive |
| 52 | PC10 | DUMP_REQUEST | GPIO | LOW / disabled |
| 53 | PC11 | MON_ALERT_HOST | GPIO | see interface/power sequencing |
| 54 | PC12 | CAN_STANDBY | GPIO | see interface/power sequencing |
| 55 | PD2 | MON_CONFIG_VALID | GPIO | LOW / disabled |
| 56 | PB3 | SWO | AF0 SWO | see interface/power sequencing |
| 57 | PB4 | BUS_ISO_FB | GPIO | input / no drive |
| 58 | PB5 | CAP_ISO_FB | GPIO | input / no drive |
| 59 | PB6 | BYP_BUS_FB | GPIO | input / no drive |
| 60 | PB7 | BYP_CAP_FB | GPIO | input / no drive |
| 61 | PB8 | CAN_RX | AF9 FDCAN1_RX | see interface/power sequencing |
| 62 | PB9 | CAN_TX | AF9 FDCAN1_TX | see interface/power sequencing |
| 63 | VSS | GND | supply | see interface/power sequencing |
| 64 | VDD | V3V3 | supply | see interface/power sequencing |

ADC uses HRTIM-triggered conversions away from edges;12-bit nominal resolution is not effective accuracy. Multiple ADC/DMA scheduling and INA240 settling at200kHz must be tested. External comparator path drives FLT1; internal MCU comparators are unassigned expansion, not primary protection. Five unused GPIO pads are PC14/PC15/PF0/PF1/PA7. Debug power pin is a voltage reference only.

## Major component pin → datasheet terminal → footprint pad

Original box symbols are maintained in tools/rev_a_parts.py; numbers are physical except the explicitly grouped MOSFET aliases below. Installed candidate footprints were checked for pad-set equivalence, not certified land geometry.

| Component | Symbol pin:function / datasheet equivalent | Candidate footprint |
|---|---|---|
| Q_NPN | 1:B, 2:E, 3:C | Package_TO_SOT_SMD:SOT-23 |
| Q_PNP | 1:B, 2:E, 3:C | Package_TO_SOT_SMD:SOT-23 |
| FUSE | 1:A, 2:B | external / TBD |
| CSD18540Q5B | 1:S_DS1_2_3, 2:G_DS4, 3:D_DS5_6_7_8 | Package_SON:VSONP-8-1EP_5x6_P1.27mm |
| UCC27282DRCR | 1:VDD, 2:NC, 3:HB, 4:HO, 5:HS, 6:EN, 7:HI, 8:LI, 9:VSS, 10:LO, 11:EP | Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm |
| INA240A1D | 1:INM, 2:GND, 3:REF2, 4:NC, 5:OUT, 6:VS, 7:REF1, 8:INP | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm |
| INA240A2D | 1:INM, 2:GND, 3:REF2, 4:NC, 5:OUT, 6:VS, 7:REF1, 8:INP | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm |
| WSK25123L000FEA | 1:I_P, 2:K_P, 3:K_M, 4:I_M | Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T2.21mm |
| INA293A1DBVR | 1:OUT, 2:GND, 3:INP, 4:INM, 5:VS | Package_TO_SOT_SMD:SOT-23-5 |
| INA301A1DGKR | 1:VS, 2:OUT, 3:LIMIT, 4:GND, 5:RESET, 6:ALERT_N, 7:INM, 8:INP | Package_SO:VSSOP-8_3x3mm_P0.65mm |
| TLV3202DGKR | 1:OUT1, 2:INM1, 3:INP1, 4:GND, 5:INP2, 6:INM2, 7:OUT2, 8:VCC | Package_SO:VSSOP-8_3x3mm_P0.65mm |
| SN74LVC1G74DCUR | 1:CLK, 2:D, 3:QN, 4:GND, 5:Q, 6:CLR_N, 7:PRE_N, 8:VCC | Package_SO:VSSOP-8_2.3x2mm_P0.5mm |
| SN74LVC2G08DCUR | 1:A1, 2:B1, 3:Y2, 4:GND, 5:A2, 6:B2, 7:Y1, 8:VCC | Package_SO:VSSOP-8_2.3x2mm_P0.5mm |
| TPS3431SDRBR | 1:VDD, 2:CWD, 3:EN, 4:GND, 5:SET1, 6:WDI, 7:WDO_N, 8:ENOUT, 9:EP | Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm |
| TPS3839K33DBZR | 1:GND, 2:RESET_N, 3:VDD | Package_TO_SOT_SMD:SOT-23 |
| LM5164DDAR | 1:GND, 2:VIN, 3:EN, 4:RON, 5:FB, 6:PGOOD, 7:BST, 8:SW, 9:EP | Package_SO:TI_SO-PowerPAD-8 |
| TMUX1511PWR | 1:SEL1, 2:S1, 3:D1, 4:SEL2, 5:S2, 6:D2, 7:GND, 8:D3, 9:S3, 10:SEL3, 11:D4, 12:S4, 13:SEL4, 14:VDD | Package_SO:TSSOP-14_4.4x5mm_P0.65mm |
| TLV431AIDBZR | 1:REF, 2:K, 3:A | Package_TO_SOT_SMD:SOT-23 |
| SN65HVD230DR | 1:D, 2:GND, 3:VCC, 4:R, 5:VREF, 6:CANL, 7:CANH, 8:RS | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm |
| SN74LV1T34DBVR | 1:NC, 2:A, 3:GND, 4:Y, 5:VCC | Package_TO_SOT_SMD:SOT-23-5 |
| BQ7694204PFBR | 1:NC, 2:VC9, 3:NC, 4:VC8, 5:NC, 6:VC7, 7:NC, 8:VC6, 9:NC, 10:VC5, 11:NC, 12:VC4, 13:VC3, 14:VC2, 15:VC1, 16:VC0, 17:VSS, 18:SRP, 19:NC, 20:SRN, 21:TS1, 22:TS2, 23:TS3, 24:REG18, 25:ALERT, 26:SCLK, 27:MISO, 28:MOSI, 29:CS_N, 30:DFETOFF, 31:DCHG, 32:DDSG, 33:RST_SHUT, 34:REG2, 35:REG1, 36:REGIN, 37:BREG, 38:FUSE, 39:PDSG, 40:PCHG, 41:LD, 42:PACK, 43:DSG, 44:NC, 45:CHG, 46:CP1, 47:BAT, 48:VC10 | Package_QFP:TQFP-48_7x7mm_P0.5mm |
| CONTACT | 1:COM, 2:NO, 3:COIL_P, 4:COIL_M | external / TBD |

CSD18540 functional1=S physical package leads1/2/3; functional2=G lead4; functional3=D leads5/6/7/8 and drain metal. KiCad VSONP footprint groups these as1/2/3; **not literal manufacturer 8-pin numbering**. WSK2512 grouped1=I+,2=Kelvin+,3=Kelvin−,4=I−; inspect terminal view and PCB current direction before routing. UCC27282 EP11 and LM5164 EP9 are ground; thermal-pad solder and vias need PCB review. BQ76942 physical48=VC10,2=VC9; VC9/VC8 short is deliberate unused-channel handling, not a missing ninth cell.

## External selected-module physical pin supplement

| Module | Manufacturer terminal mapping | PCB land |
|---|---|---|
| AQZ202G |1 LED−,2 LED+,3/4 AC/DC load|External,no PCB footprint|
| DDR-60L-12 |1/2 −Vo,3/4 +Vo,5 +Vin,6 −Vin|External DIN module|

PRE_BUS_FB/ PRE_CAP_FB are reserved inputs pulled LOW;SSR conduction is inferred from raw/link voltage progression,not an invented auxiliary contact. Existing64-pin MCU allocation is unchanged.

AEV14012 main-contact FB headers are also reserved diagnostic inputs,default LOW;the selected contactor has no intrinsic auxiliary feedback. Firmware must not interpret an unconnected pin as closed-contact proof. Raw/link ADC progression,current response and independently inspected isolation establish behavior;welded-contact fault tests remain required.
