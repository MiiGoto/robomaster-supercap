"""Shared symbols and footprints for the Rev B control board schematic (kisch2 style)."""
from kisch2 import LibSym, PowerSym, Box

R = LibSym("R", "Device.kicad_sym", "R", "R")
C = LibSym("C", "Device.kicad_sym", "C", "C")
CP = LibSym("CP", "Device.kicad_sym", "C_Polarized", "C")
L = LibSym("L", "Device.kicad_sym", "L", "L")
DZ = LibSym("DZ", "Device.kicad_sym", "D_Zener", "D")
DS = LibSym("DS", "Device.kicad_sym", "D_Schottky", "D")
LED = LibSym("LED", "Device.kicad_sym", "LED", "D")
F = LibSym("FUSE", "Device.kicad_sym", "Fuse", "F")
NMOS = LibSym("NMOS", "Device.kicad_sym", "Q_NMOS_GSD", "Q")        # SOT-23: 1=G 2=S 3=D
PMOS = LibSym("PMOS", "Device.kicad_sym", "Q_PMOS_GDS", "Q")        # TO-252: 1=G 2=D(tab) 3=S
NPN = LibSym("NPN", "Device.kicad_sym", "Q_NPN_BEC", "Q")           # SOT-23: 1=B 2=E 3=C
PFET = LibSym("TDSON8", "Transistor_FET.kicad_sym", "BSC028N06LS3", "Q")  # 1-3=S 4=G 5-8=D
XTAL = LibSym("XTAL", "Device.kicad_sym", "Crystal", "Y")
NTC = LibSym("NTC", "Device.kicad_sym", "Thermistor_NTC", "TH")
CON2 = LibSym("CON2", "Connector_Generic.kicad_sym", "Conn_01x02", "J")
CON3 = LibSym("CON3", "Connector_Generic.kicad_sym", "Conn_01x03", "J")
CON4 = LibSym("CON4", "Connector_Generic.kicad_sym", "Conn_01x04", "J")
CON5 = LibSym("CON5", "Connector_Generic.kicad_sym", "Conn_01x05", "J")
TP = LibSym("TP", "Connector.kicad_sym", "TestPoint", "TP")
MCU = LibSym("STM32G431", "MCU_ST_STM32G4.kicad_sym", "STM32G431CBTx", "U")
AP = LibSym("AP63203", "Regulator_Switching.kicad_sym", "AP63203WU", "U")
INA = LibSym("INA240A1", "Amplifier_Current.kicad_sym", "INA240A1PW", "U")
CMP = LibSym("LM393", "Comparator.kicad_sym", "LM393", "U")
REF = LibSym("TL431", "Reference_Voltage.kicad_sym", "TL431DBZ", "U")
CAN = LibSym("HVD230", "Interface_CAN_LIN.kicad_sym", "SN65HVD230", "U")

GND = PowerSym("GND")
V33 = PowerSym("+3V3")
FLAG = PowerSym("PWR_FLAG")

_p = "passive"
def _rows(spec, n):
    out = [None] * n
    for row, num, name in spec:
        out[row] = (num, name, _p)
    return out


LM5176 = Box("rev:LM5176", "U", _rows([
    (0, "2", "VIN"), (1, "3", "VISNS"), (3, "14", "ISNS+"), (4, "13", "ISNS-"), (6, "1", "EN/UVLO"),
    (9, "4", "MODE"), (12, "5", "DITH"), (15, "6", "RT/SYNC"), (19, "7", "SLOPE"), (23, "8", "SS"),
    (27, "9", "COMP"), (32, "12", "VOSNS"), (35, "11", "FB")], 36), _rows([
    (0, "24", "BIAS"), (2, "23", "VCC"), (6, "17", "PGOOD"), (9, "27", "HDRV1"), (11, "26", "BOOT1"),
    (14, "28", "SW1"), (16, "25", "LDRV1"), (20, "19", "HDRV2"), (22, "20", "BOOT2"), (25, "18", "SW2"),
    (27, "21", "LDRV2"), (30, "16", "CS"), (31, "15", "CSG"), (33, "10", "AGND"), (34, "22", "PGND"),
    (35, "29", "EP")], 36), width=25.4)

R06 = "Resistor_SMD:R_0603_1608Metric"
C06 = "Capacitor_SMD:C_0603_1608Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"
C12 = "Capacitor_SMD:C_1210_3225Metric"
R25 = "Resistor_SMD:R_2512_6332Metric"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_XT30 = "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"
FP_FET = "Package_TO_SOT_SMD:TDSON-8-1"

GLOBALS = {"VIN_F", "VIN_C", "VIN_P", "ISNS_N", "NODE", "CHG_INH", "PMOS_EN", "PGOOD", "IIN_S", "ICAP_S",
           "ILIM_DAC", "EN_CHG", "EN_PMOS", "NODE_OK", "VNODE_S", "VINC_S", "TEMP_S"}


def mk(s):
    """helpers bound to a sheet"""
    def r(x, y, val, a, b, rot=0, fp=R06, **p):
        p["Footprint"] = fp
        return s.add(R, x, y, val, {"1": a, "2": b}, rot=rot, props=p)

    def c(x, y, val, a, b, rot=0, fp=C06, **p):
        p["Footprint"] = fp
        return s.add(C, x, y, val, {"1": a, "2": b}, rot=rot, props=p)

    def gnd(pt):
        s.power(GND, pt)

    def v33(pt):
        s.power(V33, pt)

    return r, c, gnd, v33
