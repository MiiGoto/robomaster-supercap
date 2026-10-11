"""Sheet 2: LM5176 4-switch buck-boost charger, power stage, output node, connectors, cap-port current."""
import sys
from kisch2 import Sheet2
from parts import *

s = Sheet2("Rev B control board - 2/4 buck-boost charger", paper="A3", path=sys.argv[2], ref_base=100,
           global_nets=GLOBALS)
r, c, gnd, v33 = mk(s)

s.text(15, 15, "2/4  LM5176 4-switch buck-boost charger  (VIN_P 22-26 V -> NODE 0-26.2 V, ~100 W)", 2.5, bold=True)
s.text(15, 20.5, "NODE = chassis output and capacitor bank (via CM01).  fsw ~248 kHz (RT 33k), Vout 26.2 V (634k/20k), "
                 "UVLO ~19 V, CCM, hiccup off (MODE 200k: confirm in datasheet).", 1.27)
s.text(15, 23.5, "Power FETs: 60 V class (input TVS clamps up to ~48 V).  Gate nets HG1/LG1/HG2/LG2 and SW1/SW2 are "
                 "local labels; keep gate loops short in layout.", 1.27)

U = s.add(LM5176, 118.11, 100.33, "LM5176PWPR", {
    "1": "EN", "2": "VIN_P", "3": "VIN_P", "4": "MODE", "5": "GND", "6": "RT", "7": "SLOPE", "8": "SS",
    "9": "COMP", "10": "GND", "11": "FB", "12": "NODE", "13": "ISNS_N", "14": "VIN_C", "29": "GND",
    "15": "GND", "16": "CS_N", "17": "PGOOD", "18": "SW2", "19": "HDRV2", "20": "BOOT2", "21": "LDRV2",
    "22": "GND", "23": "VCC_LM", "24": "NODE", "25": "LDRV1", "26": "BOOT1", "27": "HDRV1", "28": "SW1"},
    props={"LCSC": "C442493", "Footprint": "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm"}, text="box")

# ---------------- left side
# VIN / VISNS
xa = U["2"][0] - 5.08
s.wire(U["2"], (xa, U["2"][1]))
s.wire(U["3"], (xa, U["3"][1]), (xa, U["2"][1]))
s.wire((xa, U["2"][1]), (xa - 5.08, U["2"][1]))
s.label("VIN_P", (xa - 5.08, U["2"][1]), "L")
for pin in ("14", "13"):
    s.stub_label(U, pin, length=5.08)

# EN / UVLO divider + inhibit FET
yen = U["1"][1]
xen = 60.96
RUV2 = r(xen, yen - 3.81, "249k", "VIN_C", "EN")
RUV1 = r(xen, yen + 3.81, "17.4k", "EN", "GND")
s.wire(RUV2[1], (xen, RUV2[1][1] - 2.54))
s.label("VIN_C", (xen, RUV2[1][1] - 2.54), "U")
gnd(RUV1[2])
Qi = s.add(NMOS, 45.72, yen + 5.08, "2N7002", {"1": "CHG_INH", "2": "GND", "3": "EN"}, props={"Footprint": SOT23})
s.wire(U["1"], Qi[3])
gnd(Qi[2])
Rinh = r(35.56, Qi[1][1] - 3.81, "100k", "3V3", "CHG_INH", text="left")
v33(Rinh[1])
s.wire(Qi[1], (25.4, Qi[1][1]))
s.label("CHG_INH", (25.4, Qi[1][1]), "L")
s.text(20, yen + 20, "CHG_INH high (default, pulled to 3V3)\n= converter held off.  Sheet 4 pulls it low.", 1.27)

# settings: horizontal parts from pin to a common AGND rail at x = xr
xr = 71.12
xp = 86.36  # part centre column
rows = [("4", R, "200k", "MODE"), ("6", R, "33k", "RT"), ("7", C, "220p", "SLOPE"), ("8", C, "100n", "SS"),
        ("9", C, "560p", "COMP")]
for pin, sym, val, net in rows:
    y = U[pin][1]
    k = s.add(sym, xp, y, val, {"1": "GND", "2": net}, rot=90, text="above",
              props={"Footprint": R06 if sym is R else C06})
    s.wire(U[pin], k[2])
    s.wire(k[1], (xr, y))
y5 = U["5"][1]
s.wire(U["5"], (xr, y5))           # DITH -> AGND (dither off)
# COMP series branch
yc = U["9"][1] + 5.08
xj = 96.52
s.wire((xj, U["9"][1]), (xj, yc))
Rc1 = s.add(R, xj - 6.35, yc, "10k", {"1": "COMP_RC", "2": "COMP"}, rot=90, text="above", props={"Footprint": R06})
Cc1 = s.add(C, xj - 19.05, yc, "33n", {"1": "GND", "2": "COMP_RC"}, rot=90, text="above", props={"Footprint": C06})
s.wire((xj, yc), Rc1[2])
s.wire(Rc1[1], Cc1[2])
s.wire(Cc1[1], (xr, yc))
s.wire((xr, U["4"][1]), (xr, yc + 5.08))
gnd((xr, yc + 5.08))
s.text(xr - 2, U["4"][1] - 6, "MODE: 200k = CCM, hiccup off (TBC)", 1.1)

# VOSNS / FB divider
yv, yf = U["12"][1], U["11"][1]
xv = 96.52
s.wire(U["12"], (xv, yv))
s.wire((xv, yv), (xv - 7.62, yv))
s.label("NODE", (xv - 7.62, yv), "L")
RFB2 = r(xv, (yv + yf) / 2, "634k 0.1%", "NODE", "FB")
s.wire(U["11"], RFB2[2])
RFB1 = r(xv, yf + 3.81, "20k 0.1%", "FB", "GND")
gnd(RFB1[2])
s.text(60, yf + 10, "Vout = 0.8 V x (1 + 634k/20k) = 26.2 V", 1.27)

# ---------------- right side
xR = U["24"][0]
s.stub_label(U, "24", "NODE", length=5.08)
CV = c(160.02, U["23"][1] + 3.81, "4.7u 16V", "VCC_LM", "GND", fp=C08)
s.wire(U["23"], CV[1])
gnd(CV[2])
s.stub_label(U, "17", "PGOOD", length=5.08)

# gate resistors -> local labels; bootstrap caps between BOOT and SW
for hd, bt, sw, ld, hl, ll, swn in (("27", "26", "28", "25", "HG1", "LG1", "SW1"),
                                     ("19", "20", "18", "21", "HG2", "LG2", "SW2")):
    for pin, lab in ((hd, hl), (ld, ll)):
        y = U[pin][1]
        rg = s.add(R, 148.59, y, "2R2", {"1": f"{lab}_R", "2": lab}, rot=90, text="above", props={"Footprint": R06})
        s.wire(U[pin], rg[1])
        s.wire(rg[2], (160.02, y))
        s.label(lab, (160.02, y), "R")
        rg.nets = {"1": U.nets[pin], "2": lab}
    yb, ys = U[bt][1], U[sw][1]
    cb = c(175.26, (yb + ys) / 2 + 0.0, "100n 50V", f"BOOT{swn[-1]}", swn, fp=C06)
    s.wire(U[bt], (175.26, yb), cb[1])
    s.wire(U[sw], cb[2])
    s.wire(cb[2], (182.88, ys))
    s.label(swn, (182.88, ys), "R")

# CS (Kelvin to Rcs), grounds
s.stub_label(U, "16", "CS_N", length=5.08)
xg = U["15"][0] + 5.08
for pin in ("15", "10", "22", "29"):
    s.wire(U[pin], (xg, U[pin][1]))
s.wire((xg, U["15"][1]), (xg, U["29"][1] + 2.54))
gnd((xg, U["29"][1] + 2.54))
s.text(xg + 3, U["10"][1] - 1, "AGND/PGND/EP: star at the EP, Kelvin\nCS/CSG to Rcs pads", 1.1)

# ---------------- power stage
s.frame(195, 32, 100, 135, "Power stage")
yt = 45.72                      # top rails
xb, xo = 215.9, 271.78          # buck leg / boost leg FET x (centre)
Q1 = s.add(PFET, xb, 66.04, "60V N-MOS 5x6", {"1": "SW1", "2": "SW1", "3": "SW1", "4": "HG1", "5": "VIN_P",
                                               "6": "VIN_P", "7": "VIN_P", "8": "VIN_P", "9": "VIN_P"} if "9" in PFET.geom else
           {"1": "SW1", "2": "SW1", "3": "SW1", "4": "HG1", "5": "VIN_P", "6": "VIN_P", "7": "VIN_P", "8": "VIN_P"},
           props={"Footprint": FP_FET, "Note": "60V, Qg<=25nC, e.g. BSC028N06LS3 / TBD"})
Q2 = s.add(PFET, xb, 99.06, "60V N-MOS 5x6", {**{k: "SW1" for k in Q1.geom if Q1.nets[k] == "VIN_P"},
                                               **{k: "CS_N" for k in Q1.geom if Q1.nets[k] == "SW1"}, "4": "LG1"},
           props={"Footprint": FP_FET})
Q3 = s.add(PFET, xo, 66.04, "60V N-MOS 5x6", {**{k: "NODE" for k in Q1.geom if Q1.nets[k] == "VIN_P"},
                                               **{k: "SW2" for k in Q1.geom if Q1.nets[k] == "SW1"}, "4": "HG2"},
           props={"Footprint": FP_FET})
Q4 = s.add(PFET, xo, 99.06, "60V N-MOS 5x6", {**{k: "SW2" for k in Q1.geom if Q1.nets[k] == "VIN_P"},
                                               **{k: "CS_N" for k in Q1.geom if Q1.nets[k] == "SW1"}, "4": "LG2"},
           props={"Footprint": FP_FET})
D, S, Gt = "5", "1", "4"
s.wire((Q1[D][0] - 15.24, yt), (Q1[D][0], yt), Q1[D])
s.label("VIN_P", (Q1[D][0] - 15.24, yt), "L")
s.wire(Q3[D], (Q3[D][0], yt))
ysw = (Q1[S][1] + Q2[D][1]) / 2
s.wire(Q1[S], Q2[D])
s.wire(Q3[S], Q4[D])
Lm = s.add(L, (Q1[S][0] + Q3[S][0]) / 2, ysw, "10uH", {"1": "SW1", "2": "SW2"}, rot=90, text="above",
           props={"Footprint": "Inductor_SMD:L_12x12mm_H8mm", "LCSC": "C6916222",
                  "Note": "MDA1360-100M, Isat >= 12 A, footprint to confirm"})
s.wire((Q1[S][0], ysw), Lm[1])
s.wire(Lm[2], (Q3[S][0], ysw))
s.wire((Q1[S][0], ysw), (Q1[S][0] - 7.62, ysw))
s.label("SW1", (Q1[S][0] - 7.62, ysw), "L")
s.wire((Q3[S][0], ysw), (Q3[S][0] + 7.62, ysw))
s.label("SW2", (Q3[S][0] + 7.62, ysw), "R")
for q, lab in ((Q1, "HG1"), (Q2, "LG1"), (Q3, "HG2"), (Q4, "LG2")):
    s.stub_label(q, Gt, lab, length=5.08)
ycs = Q2[S][1] + 7.62
s.wire(Q2[S], (Q2[S][0], ycs), (Q4[S][0], ycs), Q4[S])
xcs = (Q2[S][0] + Q4[S][0]) / 2
Rcs = s.add(R, xcs, ycs + 6.35, "10m 2512", {"1": "CS_N", "2": "GND"},
            props={"Footprint": R25, "LCSC": "C2930473", "Note": "Kelvin to CS/CSG"})
s.wire((xcs, ycs), Rcs[1])
gnd(Rcs[2])
s.wire((xcs, ycs), (xcs + 10.16, ycs))
s.label("CS_N", (xcs + 10.16, ycs), "R")
s.text(198, 150, "Valley/peak current limits: buck 80 mV, boost 120 mV typ\nover 10 mR  -> ~8 A / ~12 A inductor current.", 1.27)

# ---------------- output node
fx = 300
s.frame(fx, 32, 107, 135, "Output node  NODE  (chassis + bank)")
yn = yt
xc = fx + 12.7
s.wire((Q3[D][0], yt), (fx + 81.28, yn))
s.label("NODE", (fx + 2.54, yn), "U")
for i in range(5):
    k = c(xc + i * 10.16, yn + 7.62, "4.7u", "NODE", "GND", fp=C12)
    s.wire((xc + i * 10.16, yn), k[1])
    gnd(k[2])
cpo = s.add(CP, xc + 50.8, yn + 7.62, "100u", {"1": "NODE", "2": "GND"},
            props={"Footprint": "Capacitor_SMD:CP_Elec_10x10.5", "Note": "50V hybrid polymer, part TBD"})
s.wire((xc + 50.8, yn), cpo[1])
gnd(cpo[2])
Dn = s.add(DZ, xc + 63.5, yn + 7.62, "SMDJ30A", {"1": "NODE", "2": "GND"}, rot=270, props={"Footprint": "Diode_SMD:D_SMC"})
s.wire((xc + 63.5, yn), Dn[1])
gnd(Dn[2])
s.text(fx + 3, yn + 22, "C: 4.7u 50V X7R 1210 at the boost leg.\nD: clamps regen spikes if the bank is cut off.", 1.27)
# connectors
xj = fx + 81.28
J2 = s.add(CON2, xj + 5.08, yn, "XT30 chassis", {"1": "NODE", "2": "GND"}, props={"Footprint": FP_XT30}, text="right")
s.wire(J2[2], (J2[2][0] - 2.54, J2[2][1]), (J2[2][0] - 2.54, J2[2][1] + 5.08))
gnd((J2[2][0] - 2.54, J2[2][1] + 5.08))
# cap-port shunt and connector
ycp = yn + 40.64
Rsh = s.add(R, fx + 55.88, ycp, "2m 2512", {"1": "NODE", "2": "NODE_CAP"}, rot=90, text="above",
            props={"Footprint": R25, "Note": "Kelvin to U102"})
s.wire(Rsh[1], (fx + 38.1, ycp))
s.label("NODE", (fx + 38.1, ycp), "L")
J3 = s.add(CON2, fx + 81.28 + 5.08, ycp, "XT30 to CM01/bank", {"1": "NODE_CAP", "2": "GND"},
           props={"Footprint": FP_XT30}, text="right")
s.wire(Rsh[2], J3[1])
s.wire(J3[2], (J3[2][0] - 2.54, J3[2][1]), (J3[2][0] - 2.54, J3[2][1] + 5.08))
gnd((J3[2][0] - 2.54, J3[2][1] + 5.08))
# INA240 on the cap port (bidirectional, mid-supply reference)
U2 = s.add(INA, fx + 33.02, ycp + 33.02, "INA240A1PW",
           {"1": "GND", "2": "NODE", "3": "NODE_CAP", "4": "GND", "5": "3V3", "6": "GND", "7": "3V3", "8": "ICAP_RAW"},
           props={"Footprint": "Package_SO:TSSOP-8_4.4x3mm_P0.65mm"}, text="box")
s.wire(U2["2"], (U2["2"][0] - 7.62, U2["2"][1]))
s.label("NODE", (U2["2"][0] - 7.62, U2["2"][1]), "L")
xk = Rsh[2][0] + 5.08
s.wire(U2["3"], (U2["3"][0] - 3.81, U2["3"][1]), (U2["3"][0] - 3.81, U2["3"][1] + 0))
s.wire((U2["3"][0] - 3.81, U2["3"][1]), (U2["3"][0] - 3.81, ycp + 7.62), (xk, ycp + 7.62), (xk, ycp))
yb = U2["1"][1] + 3.81
s.wire(U2["1"], (U2["1"][0], yb))
s.wire(U2["6"], (U2["6"][0], yb))
s.wire((U2["1"][0], yb), (U2["6"][0], yb))
gnd((U2["1"][0], yb))
s.wire(U2["7"], (U2["7"][0], yb + 2.54), (U2["7"][0] + 7.62, yb + 2.54))
v33((U2["7"][0] + 7.62, yb + 2.54))
ytt = U2["5"][1] - 7.62
s.wire(U2["5"], (U2["5"][0], ytt))
v33((U2["5"][0], ytt))
C9 = c(U2["5"][0] + 10.16, ytt + 5.08, "100n", "3V3", "GND")
s.wire((U2["5"][0], ytt), (C9[1][0], ytt), C9[1])
gnd(C9[2])
R9 = r(U2["8"][0] + 10.16, U2["8"][1], "1k", "ICAP_RAW", "ICAP_S", rot=90, text="above")
s.wire(U2["8"], R9[1])
C10 = c(R9[2][0] + 5.08, U2["8"][1] + 7.62, "1n", "ICAP_S", "GND")
s.wire(R9[2], (R9[2][0] + 12.7, R9[2][1]))
s.wire((C10[1][0], R9[2][1]), C10[1])
gnd(C10[2])
s.label("ICAP_S", (R9[2][0] + 12.7, R9[2][1]), "R")
s.text(fx + 3, ycp + 52, "ICAP_S = 1.65 V + 40 mV/A (+ = charging bank), +-40 A range", 1.27)

s.write(sys.argv[1])
print("wrote", sys.argv[1], len(s.bom))
