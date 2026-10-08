"""Read-only audit against a native KiCad S-expression netlist export.

Usage: python -B check_hardware_contract.py path/to/rev_a.net
Export is local-only: it may contain private absolute paths and is not committed.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from read_kicad import parse, child, children

# Physical LQFP64 pad, GPIO, electrical net; reviewed from U11 and datasheet.
CONTRACT = """
24 PB0 ARM_PULSE
25 PB1 WD_HEARTBEAT
26 PB2 MCU_GATE_REQUEST
30 PB10 PRE_BUS_REQUEST
33 PB11 BYP_BUS_REQUEST
38 PC6 BUS_ISO_REQUEST
39 PC7 CAP_ISO_REQUEST
40 PC8 PRE_CAP_REQUEST
41 PC9 BYP_CAP_REQUEST
52 PC10 DUMP_REQUEST
55 PD2 MON_CONFIG_VALID
42 PA8 PWM_AH
43 PA9 PWM_AL
44 PA10 PWM_BH
45 PA11 PWM_BL
46 PA12 HW_FAULT_N
8 PC0 TEMP_FET_ADC
9 PC1 TEMP_L_ADC
10 PC2 TEMP_BANK_ADC
11 PC3 BUS_RAW_ADC
12 PA0 BUS_V_ADC
13 PA1 CAP_V_ADC
18 PA4 BUS_I_ADC
19 PA5 CAP_I_ADC
20 PA6 IL_I_ADC
22 PC4 CAP_RAW_ADC
34 PB12 MON_CS_HOST
35 PB13 MON_SCLK_HOST
36 PB14 MON_MISO_HOST
37 PB15 MON_MOSI_HOST
53 PC11 MON_ALERT_HOST
61 PB8 CAN_RX
62 PB9 CAN_TX
54 PC12 CAN_STANDBY
14 PA2 UART_TX
17 PA3 UART_RX
49 PA13 SWDIO
50 PA14 SWCLK
56 PB3 SWO
2 PC13 PRE_CAP_FB
51 PA15 PRE_BUS_FB
57 PB4 BUS_ISO_FB
58 PB5 CAP_ISO_FB
59 PB6 BYP_BUS_FB
60 PB7 BYP_CAP_FB
23 PC5 REFEREE_PERMIT
7 PG10 NRST
"""

def check(path):
    native = parse(path.read_text(encoding="utf-8"))
    actual = {}
    for net in children(child(native, "nets"), "net"):
        for node in children(net, "node"):
            if child(node, "ref")[1] == "U11":
                actual[child(node, "pin")[1]] = (
                    child(node, "pinfunction")[1].split("_")[0], child(net, "name")[1])
    count = 0
    for row in CONTRACT.splitlines():
        if row.strip():
            pad, pin, name = row.split()
            assert actual.get(pad) == (pin, name), (pad, pin, name, actual.get(pad))
            count += 1
    board = (ROOT / "firmware/controller/Core/Src/board.c").read_text(encoding="utf-8")
    for token in ("GPIO_AF13_HRTIM1", "GPIO_AF5_SPI2", "GPIO_AF9_FDCAN1",
                  "ADC_CHANNEL_17", "ADC_CHANNEL_13", "ADC_REGULAR_RANK_6"):
        assert token in board, token
    print(f"PASS {count} U11 physical pin/net assignments; AF/ADC rank sentinels present")

if __name__ == "__main__":
    check(Path(sys.argv[1]))
