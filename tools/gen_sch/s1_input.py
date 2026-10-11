"""Sheet 1: power input - fuse, TVS, series PMOS (back-feed block), input shunt, ISNS offset sink, input caps, INA240."""
import sys
from kisch2 import Sheet2
from parts import *

s = Sheet2("Rev B control board - 1/4 power input", paper="A4", path=sys.argv[2], ref_base=0, global_nets=GLOBALS)
r, c, gnd, v33 = mk(s)
Y = 55.88  # main power rail

s.text(15, 15, "1/4  Power input  (PM chassis output 22-26 V)", 2.5, bold=True)
s.text(15, 20.5, "Q1 blocks back-feed from converter/bank into the PM output (body diode conducts input -> board only). "
                 "Q1 stays OFF unless PMOS_EN is high.", 1.27)
s.text(15, 23.5, "R4 = LM5176 input shunt (ISNS limit 50 mV -> 4.2 A). Kelvin-route ISNS+ (VIN_C), ISNS- (via R5) and "
                 "the INA240 inputs from the R4 pads.", 1.27)

# ---------- input connector, fuse, TVS
J1 = s.add(CON2, 17.78, Y, "XT30", {"1": "VIN_RAW", "2": "GND"}, mirror="y",
           props={"Footprint": FP_XT30, "Note": "from PM chassis output"}, text="left")
F1 = s.add(F, 38.1, Y, "10A", {"1": "VIN_RAW", "2": "VIN_F"}, rot=90,
           props={"Footprint": "Fuse:Fuse_2920_7451Metric", "Note": "part TBD (fast, >=10A, 32V)"}, text="above")
s.wire(J1[1], F1[1])
gx = J1[2][0] + 2.54
s.wire(J1[2], (gx, J1[2][1]), (gx, J1[2][1] + 5.08))
gnd((gx, J1[2][1] + 5.08))

xd = 50.8
D1 = s.add(DZ, xd, Y + 7.62, "SMDJ30A", {"1": "VIN_F", "2": "GND"}, rot=270, props={"Footprint": "Diode_SMD:D_SMC"})
gnd(D1[2])

# ---------- series PMOS Q1 (D = input side, S = converter side)
Q1 = s.add(PMOS, 68.58, Y + 2.54, "AOD409", {"1": "PG", "2": "VIN_F", "3": "VIN_C"}, rot=90,
           props={"Footprint": "Package_TO_SOT_SMD:TO-252-2", "LCSC": "C36220"}, text="above")
s.wire(F1[2], Q1[2])
s.wire((xd, Y), D1[1])
s.wire((xd, Y), (xd, Y - 7.62))
s.label("VIN_F", (xd, Y - 7.62), "U")

xs, yg = 83.82, Y + 15.24       # source-gate network column, gate node
R1 = s.add(R, xs, Y + 7.62, "100k", {"1": "VIN_C", "2": "PG"}, props={"Footprint": R06})
D2 = s.add(DZ, xs + 12.7, Y + 7.62, "12V", {"1": "VIN_C", "2": "PG"}, rot=270,
           props={"Footprint": "Diode_SMD:D_SOD-123", "Note": "Vgs clamp"})
x4 = 116.84
s.wire(Q1[3], (x4 - 3.81, Y))
s.wire((xs, Y), R1[1])
s.wire((xs + 12.7, Y), D2[1])
s.wire(R1[2], (xs, yg))
s.wire(D2[2], (xs + 12.7, yg))
s.wire(Q1[1], (Q1[1][0], yg), (xs + 12.7, yg))
R2 = s.add(R, Q1[1][0], yg + 7.62, "10k", {"1": "PG", "2": "PG_PULL"}, props={"Footprint": R06})
s.wire((Q1[1][0], yg), R2[1])
Q2 = s.add(NMOS, Q1[1][0] - 2.54, yg + 20.32, "2N7002", {"1": "PMOS_EN", "2": "GND", "3": "PG_PULL"},
           props={"Footprint": SOT23})
s.wire(R2[2], Q2[3])
gnd(Q2[2])
xr3 = Q2[1][0] - 7.62
R3 = s.add(R, xr3, Q2[1][1] + 5.08, "100k", {"1": "PMOS_EN", "2": "GND"}, props={"Footprint": R06}, text="left")
s.wire(Q2[1], (xr3, Q2[1][1]), R3[1])
gnd(R3[2])
s.wire((xr3, Q2[1][1]), (xr3 - 10.16, Q2[1][1]))
s.label("PMOS_EN", (xr3 - 10.16, Q2[1][1]), "L")
s.text(15, yg + 37, "PMOS_EN (sheet 4) = MCU EN_PMOS AND no input OV.  R3 keeps Q1 off at power-up.", 1.27)

# ---------- input shunt R4 (VIN_C -> VIN_P)
R4 = s.add(R, x4, Y, "12m 2512", {"1": "VIN_C", "2": "VIN_P"}, rot=90,
           props={"Footprint": R25, "Note": "Kelvin to ISNS+/- and INA240"}, text="above")
s.wire((x4 - 7.62, Y), (x4 - 7.62, Y - 7.62))
s.label("VIN_C", (x4 - 7.62, Y - 7.62), "U")

# ---------- input caps on VIN_P
xc0, dxc = 137.16, 12.7
xe = xc0 + 6 * dxc + 12.7
s.wire(R4[2], (xe, Y))
for i in range(6):
    cx = xc0 + i * dxc
    k = c(cx, Y + 7.62, "4.7u", "VIN_P", "GND", fp=C12)
    s.wire((cx, Y), k[1])
    gnd(k[2])
cpx = xc0 + 6 * dxc
CPa = s.add(CP, cpx, Y + 7.62, "100u", {"1": "VIN_P", "2": "GND"},
            props={"Footprint": "Capacitor_SMD:CP_Elec_10x10.5", "Note": "hybrid polymer, part TBD"})
s.wire((cpx, Y), CPa[1])
gnd(CPa[2])
s.label("VIN_P", (xe, Y), "R")
s.text(xc0 - 2, Y + 20, "C1-C6: 4.7u 50V X7R 1210.  C7: 100u 50V hybrid polymer.  Place at the buck leg (Q101/Q102).", 1.27)

# ---------- ISNS offset sink (dynamic input-power limit)
fx, fy = 120.65, 95.25
s.frame(fx, fy, 78.74, 63.5, "ISNS offset = adjustable input-power limit")
yo = fy + 15.24
R5 = s.add(R, fx + 17.78, yo, "100R", {"1": "VIN_P", "2": "ISNS_N"}, rot=90, props={"Footprint": R06}, text="above")
s.wire(R5[1], (R5[1][0] - 5.08, yo))
s.label("VIN_P", (R5[1][0] - 5.08, yo), "L")
xq = fx + 40.64
Q3 = s.add(NPN, xq, yo + 12.7, "MMBT5551", {"1": "OFS_B", "2": "OFS_E", "3": "ISNS_N"}, props={"Footprint": SOT23})
xc5 = Q3[3][0] + 12.7
s.wire(R5[2], (xc5 + 10.16, yo))
s.label("ISNS_N", (xc5 + 10.16, yo), "R")
C8 = c(xc5, yo + 7.62, "100n", "ISNS_N", "VIN_C")
s.wire((xc5, yo), C8[1])
s.wire(C8[2], (xc5, C8[2][1] + 3.81))
s.label("VIN_C", (xc5, C8[2][1] + 3.81), "D")
s.wire((Q3[3][0], yo), Q3[3])
R7 = r(Q3[2][0], Q3[2][1] + 7.62, "6.8k", "OFS_E", "GND")
s.wire(Q3[2], R7[1])
gnd(R7[2])
R6 = r(Q3[1][0] - 10.16, Q3[1][1], "1k", "ILIM_DAC", "OFS_B", rot=90, text="above")
s.wire(R6[2], Q3[1])
xr8 = Q3[1][0] - 3.81
R8 = r(xr8, Q3[1][1] + 7.62, "100k", "OFS_B", "GND", text="left")
s.wire((xr8, Q3[1][1]), R8[1])
gnd(R8[2])
s.wire(R6[1], (fx + 7.62, R6[1][1]))
s.label("ILIM_DAC", (fx + 7.62, R6[1][1]), "L")
s.text(fx + 2, fy + 52, f"I_ofs = (V_DAC - 0.65 V)/{R7.ref}, max ~0.4 mA -> +40 mV on ISNS\n"
                        f"=> limit 4.2 A ... ~0.8 A.  MCU closes the loop with IIN_S.", 1.27)

# ---------- INA240 input current
gx0, gy0 = 205.74, 95.25
s.frame(gx0, gy0, 76.2, 63.5, "Input current  (INA240A1, G=20 -> 0.24 V/A)")
U1 = s.add(INA, gx0 + 33.02, gy0 + 30.48, "INA240A1PW",
           {"1": "GND", "2": "VIN_C", "3": "VIN_P", "4": "GND", "5": "3V3", "6": "GND", "7": "GND", "8": "IIN_RAW"},
           props={"Footprint": "Package_SO:TSSOP-8_4.4x3mm_P0.65mm"}, text="box")
for pin, net in (("2", "VIN_C"), ("3", "VIN_P")):
    a = U1[pin]
    s.wire(a, (gx0 + 10.16, a[1]))
    s.label(net, (gx0 + 10.16, a[1]), "L")
yb = U1["1"][1] + 3.81
s.wire(U1["1"], (U1["1"][0], yb))
s.wire(U1["6"], (U1["6"][0], yb))
s.wire(U1["7"], (U1["7"][0], yb))
s.wire((U1["1"][0], yb), (U1["7"][0], yb))
gnd((U1["1"][0], yb))
yt = U1["5"][1] - 7.62
s.wire(U1["5"], (U1["5"][0], yt))
v33((U1["5"][0], yt))
C9 = c(U1["5"][0] + 10.16, yt + 5.08, "100n", "3V3", "GND")
s.wire((U1["5"][0], yt), (C9[1][0], yt), C9[1])
gnd(C9[2])
R9 = r(U1["8"][0] + 10.16, U1["8"][1], "1k", "IIN_RAW", "IIN_S", rot=90, text="above")
s.wire(U1["8"], R9[1])
C10 = c(R9[2][0] + 5.08, U1["8"][1] + 7.62, "1n", "IIN_S", "GND")
s.wire(R9[2], (R9[2][0] + 12.7, R9[2][1]))
s.wire((C10[1][0], R9[2][1]), C10[1])
gnd(C10[2])
s.label("IIN_S", (R9[2][0] + 12.7, R9[2][1]), "R")

# ---------- power flags (input nets are driven from a connector)
s.power(FLAG, F1[1])
s.wire((gx, J1[2][1] + 2.54), (gx + 5.08, J1[2][1] + 2.54))
s.power(FLAG, (gx + 5.08, J1[2][1] + 2.54))

s.write(sys.argv[1])
print("wrote", sys.argv[1], len(s.bom))
