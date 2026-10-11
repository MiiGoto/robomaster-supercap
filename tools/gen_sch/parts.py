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

R06 = "Resistor_SMD:R_0402_1005Metric"   # default small passives are 0402 (JLCPCB basic)
C06 = "Capacitor_SMD:C_0402_1005Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"
C12 = "Capacitor_SMD:C_1206_3216Metric"   # 50V MLCCs are 1206 (JLCPCB basic)
R25 = "Resistor_SMD:R_2512_6332Metric"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_XT30 = "Connector_AMASS:AMASS_XT30UPB-M_1x02_P5.0mm_Vertical"
FP_FET = "Package_TO_SOT_SMD:TDSON-8-1"   # onsemi SO-8FL is pin/land compatible: verify

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


# JLCPCB / LCSC part numbers (checked 2026-10-11 on jlcpcb.com: stock-sorted, Basic/Preferred where possible)
import kisch2 as _k
_k.LCSC_MAP.update({
    ("R", "100k"): "C25803", ("R", "10k"): "C25804", ("R", "1k"): "C21190", ("R", "100R"): "C22775",
    ("R", "10R"): "C22859", ("R", "2R2"): "C22939", ("R", "200k"): "C25811", ("R", "33k"): "C4216",
    ("R", "560R"): "C23204", ("R", "1M"): "C22935", ("R", "20k"): "C4184", ("R", "4.7k"): "C23162",
    ("R", "6.8k"): "C23212", ("R", "220k"): "C22961", ("R", "15k"): "C22809", ("R", "150k"): "C22807",
    ("R", "1.5M"): "C4172", ("R", "47k"): "C25819", ("R", "120R DNP"): "C22787",
    ("R", "12m 2512"): "C49164692", ("R", "2m 2512"): "C7420017",
    ("C", "100n"): "C14663", ("C", "1n"): "C1588", ("C", "220p"): "C1603", ("C", "470p"): "C1620",
    ("C", "33n"): "C21117", ("C", "33p"): "C1663", ("C", "1u"): "C15849", ("C", "4.7u 25V"): "C1779",
    ("C", "4.7u"): "C29823", ("C", "10u 50V"): "C13585", ("C", "22u 25V"): "C45783",
    ("NMOS", "2N7002"): "C8545", ("NPN", "MMBT5551"): "C2145", ("DZ", "SMBJ30A"): "C19077584",
    ("DZ", "SMAJ28A"): "C19077545", ("DZ", "12V"): "C19077426", ("DS", "SS34"): "C8678",
    ("LM393", "LM393"): "C7955", ("TL431", "TL431 (2.495 V)"): "C181103", ("INA240A1", "INA240A1PW"): "C93965",
    ("HVD230", "SN65HVD230"): "C12084", ("AP63203", "AP63203WU"): "C780769", ("NTC", "NTC 10k B3380"): "C13564",
    ("LED", "green"): "C12624", ("LED", "red"): "C2286", ("CON2", "XT30"): "C428721",
    ("CP", "100u"): "C3151829", ("CON2", "XT30 chassis"): "C428721", ("CON2", "XT30 to CM01/bank"): "C428721",
})

# 0402 versions (default footprint); entries absent here fall back to 0603 (see FORCE_0603)
_k.LCSC_MAP_0402.update({
    ("R", "100k"): "C25741", ("R", "10k"): "C25744", ("R", "1k"): "C11702", ("R", "100R"): "C25076",
    ("R", "10R"): "C25077", ("R", "200k"): "C25764", ("R", "33k"): "C25779", ("R", "1M"): "C26083",
    ("R", "20k"): "C25765", ("R", "4.7k"): "C25900", ("R", "6.8k"): "C25917", ("R", "220k"): "C25767",
    ("R", "15k"): "C25756", ("R", "150k"): "C25755", ("R", "47k"): "C25792", ("R", "120R DNP"): "C25079",
    ("C", "100n"): "C1525", ("C", "1n"): "C1523", ("C", "220p"): "C1530", ("C", "470p"): "C1537",
    ("C", "33p"): "C1562", ("C", "1u"): "C52923",
})
_k.FORCE_0603.update({("R", "2R2"), ("R", "560R"), ("R", "1.5M"), ("C", "33n"), ("C", "100n 50V")})
_k.LCSC_MAP[("C", "100n 50V")] = "C14663"
