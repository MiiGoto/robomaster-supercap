"""Rev B control board - block 2: aux power, MCU, sensing, protection/enable logic, interfaces (plan Y).

Provisional. Cross-sheet nets are global labels (see GLOBALS). Part numbers marked 'stock unchecked'
were not verified on JLCPCB yet.
"""
import sys
from kisch import Sheet, LibSym

PATH = sys.argv[2] if len(sys.argv) > 2 else "/"
GLOBALS = {"GND", "NODE", "NODE_CAP", "VIN_F", "VIN_C", "VIN_P", "CHG_INH", "PMOS_EN", "PGOOD", "3V3"}

R = LibSym("R", "Device.kicad_sym", "R", "R")
C = LibSym("C", "Device.kicad_sym", "C", "C")
CP = LibSym("CP", "Device.kicad_sym", "C_Polarized", "C")
L = LibSym("L", "Device.kicad_sym", "L", "L")
DZ = LibSym("DZ", "Device.kicad_sym", "D_Zener", "D")
DS = LibSym("DS", "Device.kicad_sym", "D_Schottky", "D")
LED = LibSym("LED", "Device.kicad_sym", "LED", "D")
NMOS = LibSym("NMOS", "Device.kicad_sym", "Q_NMOS_GDS", "Q")
XTAL = LibSym("XTAL", "Device.kicad_sym", "Crystal", "Y")
NTC = LibSym("NTC", "Device.kicad_sym", "Thermistor_NTC", "TH")
CON3 = LibSym("CON3", "Connector_Generic.kicad_sym", "Conn_01x03", "J")
CON4 = LibSym("CON4", "Connector_Generic.kicad_sym", "Conn_01x04", "J")
CON5 = LibSym("CON5", "Connector_Generic.kicad_sym", "Conn_01x05", "J")
PF = LibSym("PWRFLAG", "power.kicad_sym", "PWR_FLAG", "FLG")
MCU = LibSym("STM32G431", "MCU_ST_STM32G4.kicad_sym", "STM32G431CBTx", "U")
AP = LibSym("AP63203", "Regulator_Switching.kicad_sym", "AP63203WU", "U")
INA = LibSym("INA240A1", "Amplifier_Current.kicad_sym", "INA240A1PW", "U")
CMP = LibSym("LM393", "Comparator.kicad_sym", "LM393", "U")
REF = LibSym("TL431", "Reference_Voltage.kicad_sym", "TL431DBZ", "U")
CAN = LibSym("HVD230", "Interface_CAN_LIN.kicad_sym", "SN65HVD230", "U")

s = Sheet("Rev B control board - control block (plan Y, provisional)", "A1", path=PATH, ref_base=100, global_nets=GLOBALS)

R06 = "Resistor_SMD:R_0603_1608Metric"
C06 = "Capacitor_SMD:C_0603_1608Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"
C12 = "Capacitor_SMD:C_1210_3225Metric"


def r(x, y, val, a, b, **p):
    p.setdefault("Footprint", R06)
    return s.place(R, x, y, val, {"1": a, "2": b}, props=p)


def c(x, y, val, a, b, fp=C06, **p):
    p["Footprint"] = fp
    return s.place(C, x, y, val, {"1": a, "2": b}, props=p)


def g(x0, y0, col, row, dx=45, dy=24):
    return x0 + col * dx, y0 + row * dy


s.text(20, 17, "Rev B control board: block 2 / control (aux power, MCU, sensing, protection and enable logic, interfaces)  -  plan Y, PROVISIONAL", 3.0)
s.text(20, 25, "Cross-sheet nets are global labels. Parts marked 'stock unchecked' are not verified on JLCPCB. Verify pin mapping of INA240/AP63203 symbols (KiCad library) against datasheets.", 1.6)

# ---------------- A. aux power
s.frame(20, 35, 320, 155, "A. Aux power 3.3V", "AUX_IN = diode-OR of PM input and node. AP63203 (3.8-32V, 3.3V). Stock unchecked.")
x0, y0 = 40, 68
s.place(DS, *g(x0, y0, 0, 0), "Schottky (SS34)", {"1": "AUX_IN", "2": "VIN_F"}, props={"Footprint": "Diode_SMD:D_SMA"})
s.place(DS, *g(x0, y0, 1, 0), "Schottky (SS34)", {"1": "AUX_IN", "2": "NODE"}, props={"Footprint": "Diode_SMD:D_SMA"})
s.place(DZ, *g(x0, y0, 2, 0), "TVS SMAJ28A (unidirectional)", {"1": "AUX_IN", "2": "GND"}, props={"Footprint": "Diode_SMD:D_SMA"})
s.place(PF, *g(x0, y0, 3, 0), "PWR_FLAG", {"1": "AUX_IN"})
c(*g(x0, y0, 0, 1), "10u/50V X7R", "AUX_IN", "GND", fp=C12)
c(*g(x0, y0, 1, 1), "10u/50V X7R", "AUX_IN", "GND", fp=C12)
s.place(AP, 270, 115, "AP63203WU", {"1": "3V3", "2": "AUX_IN", "3": "AUX_IN", "4": "GND", "5": "AUX_SW", "6": "AUX_BST"},
        props={"Footprint": "Package_TO_SOT_SMD:TSOT-23-6", "Note": "EN tied to IN: verify"})
c(*g(x0, y0, 0, 2), "0.1u (BST)", "AUX_BST", "AUX_SW")
s.place(L, *g(x0, y0, 1, 2), "6.8uH", {"1": "AUX_SW", "2": "3V3"}, props={"Footprint": "Inductor_SMD:L_Bourns_SRP5030TA", "Note": "part undecided"})
c(*g(x0, y0, 2, 2), "22u/10V", "3V3", "GND", fp=C08)
c(*g(x0, y0, 3, 2), "22u/10V", "3V3", "GND", fp=C08)
s.place(PF, *g(x0, y0, 4, 2), "PWR_FLAG", {"1": "3V3"})
s.place(PF, *g(x0, y0, 5, 2), "PWR_FLAG", {"1": "GND"})

# ---------------- B. MCU
s.frame(350, 35, 275, 340, "B. MCU STM32G431CBT6", "Slow outer loop only. 8MHz crystal for FDCAN. SWD header. Stock: C529355 (checked earlier).")
mcu_named = {
    "PA0": "VNODE_S", "PA1": "VINC_S", "PA2": "TEMP_S", "PA3": "IIN_S", "PA4": "ICAP_S",
    "PB0": "EN_CHG", "PB1": "EN_PMOS", "PB2": "PGOOD", "PB12": "NODE_OK", "PB13": "PMOS_EN",
    "PA11": "CAN_RX", "PA12": "CAN_TX", "PB10": "USART3_TX", "PB11": "USART3_RX",
    "PB5": "LED1", "PB6": "LED2", "PA13": "SWDIO", "PA14": "SWCLK", "PG10": "NRST",
    "PF0": "OSC_IN", "PF1": "OSC_OUT", "PB8": "BOOT0",
    "VDD": "3V3", "VDDA": "3V3", "VREF+": "3V3", "VBAT": "3V3", "VSS": "GND", "VSSA": "GND",
}
s.place(MCU, 480, 165, "STM32G431CBT6", {}, props={"LCSC": "C529355", "Footprint": "Package_QFP:LQFP-48_7x7mm_P0.5mm"}, named=mcu_named)
x0, y0 = 370, 262
for i in range(4):
    c(*g(x0, y0, i, 0, 40), "0.1u", "3V3", "GND")
c(*g(x0, y0, 4, 0, 40), "1u (VDDA)", "3V3", "GND")
c(*g(x0, y0, 0, 1, 40), "4.7u", "3V3", "GND", fp=C08)
c(*g(x0, y0, 1, 1, 40), "0.1u (NRST)", "NRST", "GND")
r(*g(x0, y0, 2, 1, 40), "10k (BOOT0)", "BOOT0", "GND")
s.place(XTAL, *g(x0, y0, 0, 2, 40), "8MHz", {"1": "OSC_IN", "2": "OSC_OUT"}, props={"Footprint": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "Note": "part undecided"})
c(*g(x0, y0, 1, 2, 40), "15p", "OSC_IN", "GND")
c(*g(x0, y0, 2, 2, 40), "15p", "OSC_OUT", "GND")
s.place(CON5, 585, 100, "SWD (3V3, SWDIO, SWCLK, NRST, GND)", {"1": "3V3", "2": "SWDIO", "3": "SWCLK", "4": "NRST", "5": "GND"}, props={"Footprint": "Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical"})

# ---------------- C. sensing
s.frame(640, 35, 190, 340, "C. Sensing", "Dividers 100k/10k (27V -> 2.45V). INA240A1 (G=20). Stock unchecked.")
x0, y0 = 665, 68
r(*g(x0, y0, 0, 0), "100k", "NODE", "VNODE_S")
r(*g(x0, y0, 1, 0), "10k", "VNODE_S", "GND")
c(*g(x0, y0, 2, 0), "0.1u", "VNODE_S", "GND")
r(*g(x0, y0, 0, 1), "100k", "VIN_C", "VINC_S")
r(*g(x0, y0, 1, 1), "10k", "VINC_S", "GND")
c(*g(x0, y0, 2, 1), "0.1u", "VINC_S", "GND")
s.place(NTC, *g(x0, y0, 0, 2), "NTC 10k", {"1": "3V3", "2": "TEMP_S"}, props={"Footprint": "Resistor_SMD:R_0603_1608Metric", "Note": "place near inductor/FETs"})
r(*g(x0, y0, 1, 2), "10k", "TEMP_S", "GND")
c(*g(x0, y0, 2, 2), "0.1u", "TEMP_S", "GND")
s.place(INA, 700, 185, "INA240A1PW (input current)", {"1": "GND", "2": "VIN_C", "3": "VIN_P", "4": "GND", "5": "3V3", "6": "GND", "7": "GND", "8": "IIN_RAW"},
        props={"Footprint": "Package_SO:TSSOP-8_4.4x3mm_P0.65mm"})
r(780, 185, "1k", "IIN_RAW", "IIN_S")
c(780, 209, "1n", "IIN_S", "GND")
c(740, 215, "0.1u", "3V3", "GND")
s.place(INA, 700, 275, "INA240A1PW (cap-port current, bidirectional)", {"1": "GND", "2": "NODE", "3": "NODE_CAP", "4": "GND", "5": "3V3", "6": "GND", "7": "3V3", "8": "ICAP_RAW"},
        props={"Footprint": "Package_SO:TSSOP-8_4.4x3mm_P0.65mm"})
r(780, 275, "1k", "ICAP_RAW", "ICAP_S")
c(780, 299, "1n", "ICAP_S", "GND")
c(740, 305, "0.1u", "3V3", "GND")

# ---------------- D. protection / enable logic
s.frame(20, 205, 320, 175, "D. Protection and enable logic", "Converter runs only if: PMOS_EN (no input OV) AND NODE_OK (no node OV) AND EN_CHG (MCU). Default off.")
x0, y0 = 40, 238
r(*g(x0, y0, 0, 0), "560R (ref bias)", "3V3", "V25")
s.place(REF, *g(x0, y0, 1, 0), "TL431 (2.495V)", {"1": "V25", "2": "V25", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(*g(x0, y0, 2, 0), "10k", "V25", "V125")
r(*g(x0, y0, 3, 0), "10k", "V125", "GND")
c(*g(x0, y0, 4, 0), "0.1u", "V125", "GND")
r(*g(x0, y0, 0, 1), "100k", "VIN_C", "VOV_A")
r(*g(x0, y0, 1, 1), "4.53k (OV 28.8V)", "VOV_A", "GND")
r(*g(x0, y0, 2, 1), "100k", "NODE", "VOV_B")
r(*g(x0, y0, 3, 1), "4.75k (OV 27.5V)", "VOV_B", "GND")
UCMP = s.place(CMP, 60, 310, "LM393", {"1": "PMOS_EN", "2": "VOV_A", "3": "V125"}, unit=1, props={"Footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"})
s.place(CMP, 140, 310, "LM393", {"7": "NODE_OK", "6": "VOV_B", "5": "V125"}, unit=2, ref=UCMP)
s.place(CMP, 220, 310, "LM393", {"8": "3V3", "4": "GND"}, unit=3, ref=UCMP)
c(260, 330, "0.1u", "3V3", "GND")
r(*g(x0, y0, 4, 1), "10k (NODE_OK pull-up)", "NODE_OK", "3V3")
s.place(NMOS, 60, 350, "2N7002 (Qa)", {"1": "PMOS_EN", "2": "CHG_INH", "3": "MID1"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
s.place(NMOS, 120, 350, "2N7002 (Qb)", {"1": "NODE_OK", "2": "MID1", "3": "MID2"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
s.place(NMOS, 180, 350, "2N7002 (Qc)", {"1": "EN_CHG_G", "2": "MID2", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(230, 350, "1k", "EN_CHG", "EN_CHG_G")
r(275, 350, "100k", "EN_CHG_G", "GND")
r(*g(x0, y0, 5, 0), "1k", "EN_PMOS", "PMOS_EN")
r(*g(x0, y0, 5, 1), "100k (PGOOD pull-up)", "PGOOD", "3V3")

# ---------------- E. interfaces
s.frame(20, 395, 810, 165, "E. Interfaces", "Robot CAN (SN65HVD230), referee UART (3.3V level: verify), status LEDs.")
x0, y0 = 40, 450
s.place(CAN, 90, 460, "SN65HVD230", {"1": "CAN_TX", "2": "GND", "3": "3V3", "4": "CAN_RX", "6": "CANL", "7": "CANH", "8": "GND"},
        props={"Footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "Note": "Vref (5) unconnected"})
c(150, 500, "0.1u", "3V3", "GND")
s.place(CON4, 230, 460, "CAN (5V NC, GND, CANH, CANL)", {"2": "GND", "3": "CANH", "4": "CANL"}, props={"Footprint": "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"})
r(330, 470, "100R", "USART3_TX", "REF_TXO")
r(330, 494, "100R", "USART3_RX", "REF_RXI")
s.place(CON3, 420, 460, "Referee UART (TX, RX, GND)", {"1": "REF_TXO", "2": "REF_RXI", "3": "GND"}, props={"Footprint": "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal"})
r(520, 470, "1k", "LED1", "LED1_A")
s.place(LED, 570, 470, "LED status", {"1": "GND", "2": "LED1_A"}, props={"Footprint": "LED_SMD:LED_0603_1608Metric"})
r(520, 494, "1k", "LED2", "LED2_A")
s.place(LED, 570, 494, "LED fault", {"1": "GND", "2": "LED2_A"}, props={"Footprint": "LED_SMD:LED_0603_1608Metric"})

s.write(sys.argv[1])
with open(sys.argv[1].replace(".kicad_sch", "_bom.csv"), "w", encoding="utf-8") as fh:
    fh.write("Ref,Value,LCSC,Footprint,Symbol\n")
    for row in s.bom:
        fh.write(",".join('"%s"' % x for x in row) + "\n")
print("wrote", sys.argv[1], len(s.bom), "parts")
