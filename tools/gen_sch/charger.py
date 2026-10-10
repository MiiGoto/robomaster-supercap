"""Rev B control board - block 1: input protection + PMOS + LM5176 power stage (plan Y).

Provisional design. Values come from docs/revb/plan_y_charger_sizing.md.
"""
import sys
from kisch import Sheet, Sym

OUT = sys.argv[1] if len(sys.argv) > 1 else "charger.kicad_sch"

R = Sym("rev:R", "R", [("1", "1", "L", "passive"), ("2", "2", "R", "passive")], small=True)
C = Sym("rev:C", "C", [("1", "1", "L", "passive"), ("2", "2", "R", "passive")], small=True)
L = Sym("rev:L", "L", [("1", "1", "L", "passive"), ("2", "2", "R", "passive")], small=True)
D = Sym("rev:D", "D", [("1", "A", "L", "passive"), ("2", "K", "R", "passive")], small=True)
F = Sym("rev:FUSE", "F", [("1", "1", "L", "passive"), ("2", "2", "R", "passive")], small=True)
FET = [("1", "G", "L", "passive"), ("2", "D", "R", "passive"), ("3", "S", "R", "passive")]
NMOS = Sym("rev:NMOS", "Q", FET, width=10.16)
PMOS = Sym("rev:PMOS", "QP", FET, width=10.16)
TP = Sym("rev:TP", "TP", [("1", "1", "R", "passive")], small=True)
XT30 = Sym("rev:XT30", "J", [("1", "+", "R", "passive"), ("2", "-", "R", "passive")], width=10.16)
LM5176 = Sym("rev:LM5176", "U", [
    ("1", "EN/UVLO", "L", "passive"), ("2", "VIN", "L", "passive"), ("3", "VISNS", "L", "passive"),
    ("4", "MODE", "L", "passive"), ("5", "DITH", "L", "passive"), ("6", "RT/SYNC", "L", "passive"),
    ("7", "SLOPE", "L", "passive"), ("8", "SS", "L", "passive"), ("9", "COMP", "L", "passive"),
    ("10", "AGND", "L", "passive"), ("11", "FB", "L", "passive"), ("12", "VOSNS", "L", "passive"),
    ("13", "ISNS-", "L", "passive"), ("14", "ISNS+", "L", "passive"), ("29", "EP", "L", "passive"),
    ("15", "CSG", "R", "passive"), ("16", "CS", "R", "passive"), ("17", "PGOOD", "R", "passive"),
    ("18", "SW2", "R", "passive"), ("19", "HDRV2", "R", "passive"), ("20", "BOOT2", "R", "passive"),
    ("21", "LDRV2", "R", "passive"), ("22", "PGND", "R", "passive"), ("23", "VCC", "R", "passive"),
    ("24", "BIAS", "R", "passive"), ("25", "LDRV1", "R", "passive"), ("26", "BOOT1", "R", "passive"),
    ("27", "HDRV1", "R", "passive"), ("28", "SW1", "R", "passive"),
], width=22.86)

s = Sheet("Rev B control board - charger block (plan Y, provisional)", "A1")

R06 = "Resistor_SMD:R_0603_1608Metric"
C06 = "Capacitor_SMD:C_0603_1608Metric"
C12 = "Capacitor_SMD:C_1210_3225Metric"
R25 = "Resistor_SMD:R_2512_6332Metric"


def r(x, y, val, a, b, **p):
    p.setdefault("Footprint", R06)
    return s.place(R, x, y, val, {"1": a, "2": b}, props=p)


def c(x, y, val, a, b, fp=C06, **p):
    p["Footprint"] = fp
    return s.place(C, x, y, val, {"1": a, "2": b}, props=p)


def g(x0, y0, col, row, dx=45, dy=24):
    return x0 + col * dx, y0 + row * dy


FP_XT30 = "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"

s.text(20, 17, "Rev B control board: block 1 / charger (input protection, series PMOS, LM5176 4-switch buck-boost)  -  plan Y, PROVISIONAL", 3.0)
s.text(20, 25, "Values: docs/revb/plan_y_charger_sizing.md. Connectivity by net labels. Verify against the original datasheet: ISNS+/- polarity, MODE (hiccup), BIAS=NODE, UVLO values, FET/inductor footprints.", 1.6)

# ---------------- A. input
s.frame(20, 35, 165, 55, "A. Input / protection", "PM chassis output 22-26V. Fuse + TVS (SMDJ30A).")
x0, y0 = 40, 67
s.place(XT30, *g(x0, y0, 0, 0), "XT30 input (PM chassis out)", {"1": "VIN_RAW", "2": "GND"}, props={"Footprint": FP_XT30})
s.place(F, *g(x0, y0, 1, 0), "Fuse 10A", {"1": "VIN_RAW", "2": "VIN_F"}, props={"Footprint": "Fuse:Fuse_1206_3216Metric", "Note": "type undecided"})
s.place(D, *g(x0, y0, 2, 0), "TVS SMDJ30A", {"1": "GND", "2": "VIN_F"}, props={"Footprint": "Diode_SMD:D_SMC"})

# ---------------- B. series PMOS
s.frame(200, 35, 175, 85, "B. Series PMOS (R2/R3 back-feed block)", "Default OFF. ON only when PMOS_EN=1 (Zener limits Vgs to 12V).")
x0, y0 = 220, 67
s.place(PMOS, *g(x0, y0, 0, 0), "AOD409 60V P-ch", {"1": "PG_GATE", "2": "VIN_F", "3": "VIN_C"}, props={"LCSC": "C36220", "Footprint": "Package_TO_SOT_SMD:TO-252-2"})
r(*g(x0, y0, 1, 0), "100k", "PG_GATE", "VIN_C")
s.place(D, *g(x0, y0, 2, 0), "Zener 12V", {"1": "PG_GATE", "2": "VIN_C"}, props={"Footprint": "Diode_SMD:D_SOD-123"})
r(*g(x0, y0, 0, 1), "10k", "PG_GATE", "PG_PULL")
s.place(NMOS, *g(x0, y0, 1, 1), "2N7002", {"1": "PMOS_EN", "2": "PG_PULL", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(*g(x0, y0, 2, 1), "100k (default off)", "PMOS_EN", "GND")

# ---------------- C. input current sense + input caps
s.frame(390, 35, 175, 105, "C. Input current sense / input capacitors", "ISNS average limit 50mV/12mR = 4.2A (input power cap). Kelvin to ISNS+/-.")
x0, y0 = 410, 67
r(*g(x0, y0, 0, 0), "12mR 2512 (ISNS)", "VIN_C", "VIN_P", Footprint=R25, Note="Kelvin to ISNS+/-")
for i in range(6):
    c(*g(x0, y0, i % 3, 1 + i // 3), "4.7u/50V X7R", "VIN_P", "GND", fp=C12)
c(*g(x0, y0, 1, 0), "100u/35V polymer", "VIN_P", "GND", fp="Capacitor_SMD:CP_Elec_8x10", Note="part undecided")

# ---------------- G. output
s.frame(580, 35, 175, 80, "D. Output node (chassis + capacitor bank)", "Chassis and bank share this node. Bank via CM01.")
x0, y0 = 600, 67
s.place(XT30, *g(x0, y0, 0, 0), "XT30 chassis", {"1": "NODE", "2": "GND"}, props={"Footprint": FP_XT30})
s.place(XT30, *g(x0, y0, 0, 1), "XT30 capacitor (to CM01)", {"1": "NODE", "2": "GND"}, props={"Footprint": FP_XT30})
for i in range(4):
    c(*g(x0, y0, 1 + i % 2, i // 2), "10u/35V X7R", "NODE", "GND", fp=C12)

# ---------------- E. LM5176 peripherals
s.frame(20, 155, 165, 150, "E. LM5176 settings", "UVLO ~19V, no hiccup, 248kHz, Vout 26.2V.")
x0, y0 = 40, 188
r(*g(x0, y0, 0, 0), "249k (RUV2)", "VIN_C", "EN")
r(*g(x0, y0, 1, 0), "17.4k (RUV1)", "EN", "GND", Note="UVLO about 19V (provisional)")
s.place(NMOS, *g(x0, y0, 2, 0), "2N7002 (inhibit)", {"1": "CHG_INH", "2": "EN", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(*g(x0, y0, 0, 1), "100k (default inhibit)", "CHG_INH", "VCC_LM")
r(*g(x0, y0, 1, 1), "200k (MODE, no hiccup)", "MODE", "GND", Note="93.1k = hiccup enabled; undecided")
r(*g(x0, y0, 2, 1), "33k (RT, ~248kHz)", "RT", "GND")
c(*g(x0, y0, 0, 2), "220p (SLOPE)", "SLOPE", "GND")
c(*g(x0, y0, 1, 2), "0.1u (SS)", "SS", "GND")
c(*g(x0, y0, 2, 2), "4.7u (VCC)", "VCC_LM", "GND", fp="Capacitor_SMD:C_0805_2012Metric")
r(*g(x0, y0, 0, 3), "10k (Rc1)", "COMP", "COMP_RC")
c(*g(x0, y0, 1, 3), "33n (Cc1)", "COMP_RC", "GND")
c(*g(x0, y0, 2, 3), "560p (Cc2)", "COMP", "GND")
r(*g(x0, y0, 0, 4), "634k (RFB2, 26.2V)", "NODE", "FB")
r(*g(x0, y0, 1, 4), "20k (RFB1)", "FB", "GND")

# ---------------- F. LM5176 IC
s.frame(200, 155, 200, 150, "F. LM5176 controller", "HTSSOP-28. Buck side = SW1/HDRV1/LDRV1, boost side = SW2/HDRV2/LDRV2.")
U = s.place(LM5176, 305, 235, "LM5176PWPR", {
    "1": "EN", "2": "VIN_P", "3": "VIN_P", "4": "MODE", "5": "GND", "6": "RT", "7": "SLOPE", "8": "SS",
    "9": "COMP", "10": "GND", "11": "FB", "12": "NODE", "13": "VIN_P", "14": "VIN_C", "29": "GND",
    "15": "GND", "16": "CS_N", "17": "PGOOD", "18": "SW2", "19": "HG2_R", "20": "BOOT2", "21": "LG2_R",
    "22": "GND", "23": "VCC_LM", "24": "NODE", "25": "LG1_R", "26": "BOOT1", "27": "HG1_R", "28": "SW1",
}, props={"LCSC": "C442493", "Footprint": "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm"})
s.place(TP, 375, 185, "TP PGOOD", {"1": "PGOOD"}, props={"Footprint": "TestPoint:TestPoint_Pad_D1.0mm"})

# ---------------- gate resistors and bootstrap
s.frame(415, 155, 135, 150, "G. Gate drive", "Gate resistors and bootstrap capacitors.")
x0, y0 = 435, 188
r(*g(x0, y0, 0, 0), "2R2", "HG1_R", "HG1")
r(*g(x0, y0, 0, 1), "2R2", "LG1_R", "LG1")
r(*g(x0, y0, 0, 2), "2R2", "HG2_R", "HG2")
r(*g(x0, y0, 0, 3), "2R2", "LG2_R", "LG2")
c(*g(x0, y0, 1, 0), "0.22u (BOOT1)", "BOOT1", "SW1")
c(*g(x0, y0, 1, 2), "0.22u (BOOT2)", "BOOT2", "SW2")

# ---------------- power stage
s.frame(565, 155, 250, 120, "H. Power stage", "Q1,Q2 = buck leg; Q3,Q4 = boost leg; one Rcs for both low sides (CS/CSG Kelvin).")
x0, y0 = 590, 192
fp_fet = "Package_TO_SOT_SMD:Infineon_PG-TDSON-8_5.15x5.9mm"
s.place(NMOS, *g(x0, y0, 0, 0, 55, 36), "BSC059N04LS6 (Q1 HS buck)", {"1": "HG1", "2": "VIN_P", "3": "SW1"}, props={"LCSC": "C534356", "Footprint": fp_fet, "Note": "footprint to confirm"})
s.place(NMOS, *g(x0, y0, 0, 1, 55, 36), "BSC059N04LS6 (Q2 LS buck)", {"1": "LG1", "2": "SW1", "3": "CS_N"}, props={"LCSC": "C534356", "Footprint": fp_fet})
s.place(NMOS, *g(x0, y0, 1, 0, 55, 36), "BSC059N04LS6 (Q3 HS boost)", {"1": "HG2", "2": "NODE", "3": "SW2"}, props={"LCSC": "C534356", "Footprint": fp_fet})
s.place(NMOS, *g(x0, y0, 1, 1, 55, 36), "BSC059N04LS6 (Q4 LS boost)", {"1": "LG2", "2": "SW2", "3": "CS_N"}, props={"LCSC": "C534356", "Footprint": fp_fet})
s.place(L, *g(x0, y0, 2, 0, 55, 36), "10uH MDA1360-100M", {"1": "SW1", "2": "SW2"}, props={"LCSC": "C6916222", "Footprint": "Inductor_SMD:L_Bourns_SRP1245A", "Note": "footprint to confirm"})
r(*g(x0, y0, 2, 1, 55, 36), "10mR 2512 (Rcs)", "CS_N", "GND", Footprint=R25, LCSC="C2930473", Note="Kelvin to CS and CSG")

s.write(OUT)
s.write_lib(OUT.replace("charger.kicad_sch", "rev.kicad_sym"))
with open(OUT.replace(".kicad_sch", "_bom.csv"), "w", encoding="utf-8") as fh:
    fh.write("Ref,Value,LCSC,Footprint,Symbol\n")
    for row in s.bom:
        fh.write(",".join('"%s"' % x for x in row) + "\n")
print("wrote", OUT, len(s.bom), "parts")
