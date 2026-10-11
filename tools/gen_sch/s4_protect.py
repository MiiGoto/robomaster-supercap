"""Sheet 4: sensing dividers, 1.25 V reference, hardware over-voltage comparators, converter enable logic."""
import sys
from kisch2 import Sheet2
from parts import *

s = Sheet2("Rev B control board - 4/4 sensing and protection", paper="A3", path=sys.argv[2], ref_base=300,
           global_nets=GLOBALS)
r, c, gnd, v33 = mk(s)

s.text(15, 15, "4/4  Sensing, hardware over-voltage protection, converter enable logic", 2.5, bold=True)
s.text(15, 20.5, "The converter runs only if  PMOS_EN (MCU EN_PMOS and no input OV)  AND  NODE_OK (no node OV)  AND  EN_CHG (MCU).  "
                 "Everything defaults to OFF.  The comparators work without the MCU.", 1.27)

# ================= A. dividers
s.frame(15, 30, 150, 75, "Voltage / temperature sensing (ADC)")
for i, (src, out, note) in enumerate((("NODE", "VNODE_S", "27 V -> 2.45 V"), ("VIN_C", "VINC_S", "26 V -> 2.36 V"))):
    x = 35 + i * 45
    ra = r(x, 52.07, "100k", src, out)
    rb = r(x, 67.31, "10k", out, "GND")
    s.wire(ra[1], (x, ra[1][1] - 3.81))
    s.label(src, (x, ra[1][1] - 3.81), "U")
    s.wire(ra[2], rb[1])
    ym = (ra[2][1] + rb[1][1]) / 2
    ck = c(x + 10.16, ym + 5.08, "100n", out, "GND")
    s.wire((x, ym), (x + 20.32, ym))
    s.wire((x + 10.16, ym), ck[1])
    gnd(ck[2])
    gnd(rb[2])
    s.label(out, (x + 20.32, ym), "R")
    s.text(x - 5, 85, note, 1.27)
x = 125
nt = s.add(NTC, x, 52.07, "NTC 10k B3380", {"1": "3V3", "2": "TEMP_S"},
           props={"Footprint": R06, "Note": "place at L101 / power FETs"})
rb = r(x, 67.31, "10k", "TEMP_S", "GND")
v33(nt[1])
s.wire(nt[2], rb[1])
ym = (nt[2][1] + rb[1][1]) / 2
ck = c(x + 10.16, ym + 5.08, "100n", "TEMP_S", "GND")
s.wire((x, ym), (x + 20.32, ym))
s.wire((x + 10.16, ym), ck[1])
gnd(ck[2])
gnd(rb[2])
s.label("TEMP_S", (x + 20.32, ym), "R")

# ================= B. reference
s.frame(175, 30, 95, 75, "1.25 V comparator reference")
xr = 195.58
Rr = r(xr, 50.8, "560R", "3V3", "V25")
v33(Rr[1])
TL = s.add(REF, xr, 63.5, "TL431 (2.495 V)", {"1": "V25", "2": "V25", "3": "GND"}, rot=90,
           props={"Footprint": SOT23, "Note": "K and REF tied, pin order varies by vendor"},
           tpos=((xr + 3.81, 66.04), (xr + 3.81, 68.58)))
s.wire(Rr[2], TL["1"])
gnd(TL["3"])
s.wire(TL["2"], (TL["2"][0] - 2.54, TL["2"][1]), (TL["2"][0] - 2.54, Rr[2][1]), Rr[2])
yv = Rr[2][1]
s.wire(Rr[2], (xr + 22.86, yv))
R1 = r(xr + 22.86, yv + 3.81, "10k", "V25", "V125")
R2 = r(xr + 22.86, yv + 19.05, "10k", "V125", "GND")
s.wire(R1[2], R2[1])
y125 = R1[2][1] + 3.81
gnd(R2[2])
Cr = c(xr + 35.56, y125 + 3.81, "100n", "V125", "GND")
s.wire((xr + 22.86, y125), (xr + 50.8, y125))
s.wire((xr + 35.56, y125), Cr[1])
gnd(Cr[2])
s.label("V125", (xr + 50.8, y125), "R", glob=False)
s.text(178, 97, "1.2475 V: below the LM393 input range limit (Vcc - 1.5 V).", 1.27)

# ================= C. over-voltage comparators (with hysteresis)
s.frame(15, 115, 255, 110, "Hardware over-voltage comparators (LM393, open collector)")
specs = (
    ("VIN_C", "6.8k", "VOV_A", "VR_A", "PMOS_EN", "Input OV 28.8 V -> PMOS_EN low (Q1 off, converter off)", 1),
    ("NODE", "4.7k", "VOV_B", "VR_B", "NODE_OK", "Node OV 27.8 V -> NODE_OK low (converter off)", 2),
)
UC = None
for i, (src, rlo, vov, vr, outn, note, unit) in enumerate(specs):
    y0 = 140 + i * 45
    U = s.add(CMP, 120, y0, "LM393", {"1": outn, "2": vov, "3": vr} if unit == 1 else {"7": outn, "6": vov, "5": vr},
              unit=unit, ref=UC, props={"Footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"}, text="box")
    UC = U.ref
    pin_m, pin_p, pin_o = ("2", "3", "1") if unit == 1 else ("6", "5", "7")
    # divider to the inverting input
    xd = 60
    ra = r(xd, U[pin_m][1] - 6.35, "150k" if unit == 1 else "100k", src, vov)
    rb = r(xd, U[pin_m][1] + 10.16, rlo, vov, "GND")
    s.wire(ra[1], (xd, ra[1][1] - 2.54))
    s.label(src, (xd, ra[1][1] - 2.54), "U")
    s.wire(ra[2], (xd, U[pin_m][1]), rb[1])
    s.wire((xd, U[pin_m][1]), U[pin_m])
    gnd(rb[2])
    cf = c(xd + 17.78, U[pin_m][1] + 10.16, "1n", vov, "GND")
    s.wire((xd + 17.78, U[pin_m][1]), cf[1])
    gnd(cf[2])
    # reference + hysteresis on the non-inverting input
    yp = U[pin_p][1]
    xv = 100.33
    rref = r(xv, yp - 3.81, "10k", "V125", vr)
    s.wire(rref[1], (xv, rref[1][1] - 2.54))
    s.label("V125", (xv, rref[1][1] - 2.54), "U", glob=False)
    s.wire(rref[2], U[pin_p])
    xh = 106.68
    xo = U[pin_o][0] + 7.62
    rh = s.add(R, (xh + xo) / 2, yp - 12.7, "1M", {"1": vr, "2": outn}, rot=90, text="above", props={"Footprint": R06})
    s.wire((xh, yp), (xh, yp - 12.7), rh[1])
    s.wire(rh[2], (xo, yp - 12.7), (xo, U[pin_o][1]))
    s.wire(U[pin_o], (xo + 20.32, U[pin_o][1]))
    s.label(outn, (xo + 20.32, U[pin_o][1]), "R")
    if unit == 2:
        Rpu = r(xo + 10.16, U[pin_o][1] - 6.35, "10k", "3V3", "NODE_OK")
        s.wire(Rpu[1], (Rpu[1][0], Rpu[1][1] - 1.27))
        v33((Rpu[1][0], Rpu[1][1] - 1.27))
        s.wire(Rpu[2], (Rpu[2][0], U[pin_o][1]))
    s.text(140, y0 + 10, note, 1.27)
# power unit
Up = s.add(CMP, 230, 160, "LM393", {"8": "3V3", "4": "GND"}, unit=3, ref=UC, text="right",
           props={"Footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"})
s.wire(Up["8"], (Up["8"][0], Up["8"][1] - 2.54))
v33((Up["8"][0], Up["8"][1] - 2.54))
gnd(Up["4"])
Cp = c(245, Up["8"][1] + 1.27, "100n", "3V3", "GND")
s.wire((Up["8"][0], Up["8"][1] - 2.54), (245, Up["8"][1] - 2.54), Cp[1])
gnd(Cp[2])
s.text(18, 214, "Hysteresis: 10k/1M on the + input, about 0.7 V at the monitored rail.  1n filters on the dividers.", 1.27)

# ================= D. enable logic
s.frame(280, 30, 125, 195, "Converter enable logic (default OFF)")
# PMOS_EN driven by MCU through 4.7k, wired-AND with comparator A
Re = s.add(R, 320, 55.88, "4.7k", {"1": "EN_PMOS", "2": "PMOS_EN"}, rot=90, text="above", props={"Footprint": R06})
s.wire(Re[1], (300, 55.88))
s.label("EN_PMOS", (300, 55.88), "L")
s.wire(Re[2], (345, 55.88))
s.label("PMOS_EN", (345, 55.88), "R")
s.text(285, 62, "MCU sources PMOS_EN through 4.7k; comparator A sinks it on input OV.\n"
                "100k pull-down at Q2 (sheet 1) keeps it low at reset.", 1.27)
# PGOOD pull-up
Rpg = r(370, 85, "100k", "3V3", "PGOOD")
v33(Rpg[1])
s.wire(Rpg[2], (370, Rpg[2][1] + 2.54))
s.label("PGOOD", (370, Rpg[2][1] + 2.54), "D")
s.text(376, 92, "LM5176 PGOOD\n(open drain)", 1.27)
# series NMOS chain on CHG_INH
xq = 340
Qa = s.add(NMOS, xq, 110, "2N7002", {"1": "PMOS_EN", "2": "MID1", "3": "CHG_INH"}, props={"Footprint": SOT23})
Qb = s.add(NMOS, xq, 130, "2N7002", {"1": "NODE_OK", "2": "MID2", "3": "MID1"}, props={"Footprint": SOT23})
Qc = s.add(NMOS, xq, 150, "2N7002", {"1": "EN_CHG_G", "2": "GND", "3": "MID2"}, props={"Footprint": SOT23})
s.wire(Qa["2"], Qb["3"])
s.wire(Qb["2"], Qc["3"])
gnd(Qc["2"])
s.wire(Qa["3"], (Qa["3"][0], Qa["3"][1] - 7.62))
s.label("CHG_INH", (Qa["3"][0], Qa["3"][1] - 7.62), "U")
for q, lab in ((Qa, "PMOS_EN"), (Qb, "NODE_OK")):
    s.wire(q["1"], (q["1"][0] - 12.7, q["1"][1]))
    s.label(lab, (q["1"][0] - 12.7, q["1"][1]), "L")
Rg = s.add(R, Qc["1"][0] - 15.24, Qc["1"][1], "1k", {"1": "EN_CHG", "2": "EN_CHG_G"}, rot=90, text="above",
           props={"Footprint": R06})
s.wire(Rg[2], Qc["1"])
Rpd = r(Qc["1"][0] - 6.35, Qc["1"][1] + 5.08, "100k", "EN_CHG_G", "GND", text="left")
s.wire((Rpd[1][0], Qc["1"][1]), Rpd[1])
gnd(Rpd[2])
s.wire(Rg[1], (Rg[1][0] - 5.08, Rg[1][1]))
s.label("EN_CHG", (Rg[1][0] - 5.08, Rg[1][1]), "L")
s.text(285, 170, "Qa.Qb.Qc all ON -> CHG_INH pulled low -> LM5176 EN released.\n"
                 "Any of them OFF -> CHG_INH high (100k to 3V3, sheet 2) -> converter off.", 1.27)

s.write(sys.argv[1])
print("wrote", sys.argv[1], len(s.bom))
