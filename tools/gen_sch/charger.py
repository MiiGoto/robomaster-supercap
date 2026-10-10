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


def gx(col, row, x0=30, y0=30):
    return x0 + col * 34, y0 + row * 20


s.text(20, 12, "Rev B control board: block 1 (input protection, series PMOS, LM5176 4-switch buck-boost)\\n"
       "PROVISIONAL (plan Y). Values: docs/revb/plan_y_charger_sizing.md. Connectivity by net labels.\\n"
       "ISNS+/- polarity, MODE (hiccup), BIAS=NODE, UVLO values, FET footprints: verify against the original datasheet.", 2.2)

# --- connectors
s.place(XT30, *gx(0, 1), "XT30 input (PM chassis out)", {"1": "VIN_RAW", "2": "GND"}, props={"Footprint": "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"})
s.place(XT30, *gx(0, 3), "XT30 chassis", {"1": "NODE", "2": "GND"}, props={"Footprint": "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"})
s.place(XT30, *gx(0, 5), "XT30 capacitor (to CM01)", {"1": "NODE", "2": "GND"}, props={"Footprint": "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"})

# --- input protection
s.place(F, *gx(1, 1), "Fuse 10A", {"1": "VIN_RAW", "2": "VIN_F"}, props={"Footprint": "Fuse:Fuse_1206_3216Metric", "Note": "type undecided"})
s.place(D, *gx(2, 1), "TVS SMDJ30A", {"1": "GND", "2": "VIN_F"}, props={"Footprint": "Diode_SMD:D_SMC"})

# --- series PMOS (R2/R3)
s.place(PMOS, *gx(1, 3), "AOD409 60V P-ch", {"1": "PG_GATE", "2": "VIN_F", "3": "VIN_C"}, props={"LCSC": "C36220", "Footprint": "Package_TO_SOT_SMD:TO-252-2"})
r(*gx(2, 3), "100k", "PG_GATE", "VIN_C")
s.place(D, *gx(2, 4), "Zener 12V", {"1": "PG_GATE", "2": "VIN_C"}, props={"Footprint": "Diode_SMD:D_SOD-123"})
r(*gx(3, 3), "10k", "PG_GATE", "PG_PULL")
s.place(NMOS, *gx(3, 4), "2N7002", {"1": "PMOS_EN", "2": "PG_PULL", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(*gx(4, 4), "100k (default off)", "PMOS_EN", "GND")

# --- sense resistor (input average current) and input caps
r(*gx(1, 5), "12mR 2512 (ISNS)", "VIN_C", "VIN_P", Footprint=R25, Note="Kelvin to ISNS+/-")
for i in range(6):
    c(*gx(2 + i % 3, 6 + i // 3), "4.7u/50V X7R", "VIN_P", "GND", fp=C12)
c(*gx(5, 6), "100u/35V polymer", "VIN_P", "GND", fp="Capacitor_SMD:CP_Elec_8x10", Note="part undecided")

# --- LM5176
U = s.place(LM5176, 400, 190, "LM5176PWPR", {
    "1": "EN", "2": "VIN_P", "3": "VIN_P", "4": "MODE", "5": "GND", "6": "RT", "7": "SLOPE", "8": "SS",
    "9": "COMP", "10": "GND", "11": "FB", "12": "NODE", "13": "VIN_P", "14": "VIN_C", "29": "GND",
    "15": "GND", "16": "CS_N", "17": "PGOOD", "18": "SW2", "19": "HG2_R", "20": "BOOT2", "21": "LG2_R",
    "22": "GND", "23": "VCC_LM", "24": "NODE", "25": "LG1_R", "26": "BOOT1", "27": "HG1_R", "28": "SW1",
}, props={"LCSC": "C442493", "Footprint": "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm"})

# LM5176 external parts (left column)
bx, by = 190, 130
r(bx, by + 0, "249k (RUV2)", "VIN_C", "EN")
r(bx + 34, by + 0, "17.4k (RUV1)", "EN", "GND", Note="UVLO about 19V (provisional)")
s.place(NMOS, bx + 68, by + 0, "2N7002 (inhibit)", {"1": "CHG_INH", "2": "EN", "3": "GND"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23"})
r(bx + 102, by + 0, "100k (default inhibit)", "CHG_INH", "VCC_LM")
r(bx, by + 20, "200k (MODE, no hiccup)", "MODE", "GND", Note="93.1k = hiccup enabled; undecided")
r(bx + 34, by + 20, "33k (RT, ~248kHz)", "RT", "GND")
c(bx, by + 40, "220p (SLOPE)", "SLOPE", "GND")
c(bx + 34, by + 40, "0.1u (SS)", "SS", "GND")
r(bx, by + 60, "10k (Rc1)", "COMP", "COMP_RC")
c(bx + 34, by + 60, "33n (Cc1)", "COMP_RC", "GND")
c(bx + 68, by + 60, "560p (Cc2)", "COMP", "GND")
r(bx, by + 80, "634k (RFB2, 26.2V)", "NODE", "FB")
r(bx + 34, by + 80, "20k (RFB1)", "FB", "GND")
c(bx, by + 100, "4.7u (VCC)", "VCC_LM", "GND", fp="Capacitor_SMD:C_0805_2012Metric")

# gate resistors, bootstraps (right column)
rx, ry = 460, 130
r(rx, ry + 0, "2R2", "HG1_R", "HG1")
r(rx, ry + 20, "2R2", "LG1_R", "LG1")
r(rx, ry + 40, "2R2", "HG2_R", "HG2")
r(rx, ry + 60, "2R2", "LG2_R", "LG2")
c(rx + 34, ry + 0, "0.22u (BOOT1)", "BOOT1", "SW1")
c(rx + 34, ry + 40, "0.22u (BOOT2)", "BOOT2", "SW2")

s.place(TP, 440, 100, "TP PGOOD", {"1": "PGOOD"}, props={"Footprint": "TestPoint:TestPoint_Pad_D1.0mm"})

# --- power stage
px, py = 540, 130
s.place(NMOS, px, py, "BSC059N04LS6 (Q1 HS buck)", {"1": "HG1", "2": "VIN_P", "3": "SW1"}, props={"LCSC": "C534356", "Footprint": "Package_TO_SOT_SMD:Infineon_PG-TDSON-8_5.15x5.9mm", "Note": "footprint to confirm"})
s.place(NMOS, px, py + 26, "BSC059N04LS6 (Q2 LS buck)", {"1": "LG1", "2": "SW1", "3": "CS_N"}, props={"LCSC": "C534356"})
s.place(NMOS, px + 40, py, "BSC059N04LS6 (Q3 HS boost)", {"1": "HG2", "2": "NODE", "3": "SW2"}, props={"LCSC": "C534356"})
s.place(NMOS, px + 40, py + 26, "BSC059N04LS6 (Q4 LS boost)", {"1": "LG2", "2": "SW2", "3": "CS_N"}, props={"LCSC": "C534356"})
s.place(L, px + 20, py + 56, "10uH MDA1360-100M", {"1": "SW1", "2": "SW2"}, props={"LCSC": "C6916222", "Footprint": "Inductor_SMD:L_Bourns_SRP1245A", "Note": "footprint to confirm"})
r(px + 20, py + 76, "10mR 2512 (Rcs)", "CS_N", "GND", Footprint=R25, LCSC="C2930473", Note="Kelvin to CS and CSG")
for i in range(4):
    c(px + (i % 2) * 34, py + 96 + (i // 2) * 20, "10u/35V X7R", "NODE", "GND", fp=C12)

s.write(OUT)
s.write_lib(OUT.replace("charger.kicad_sch", "rev.kicad_sym"))
with open(OUT.replace(".kicad_sch", "_bom.csv"), "w", encoding="utf-8") as fh:
    fh.write("Ref,Value,LCSC,Footprint,Symbol\n")
    for row in s.bom:
        fh.write(",".join('"%s"' % x for x in row) + "\n")
print("wrote", OUT, len(s.bom), "parts")
