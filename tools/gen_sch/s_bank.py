"""Rev B bank board v2 (10S 2.7V 50F, per-cell TLV431 + PNP clamp) - kisch2 wire style, flat sheet.

usage: python3 s_bank.py out/bank_board.kicad_sch

Changes vs. the first bank schematic (hardware/revb/bank_board, 2026-10-10):
- TLV431 DBZ pinout per TI SLVS139Z Table 4-1: 1=REF, 2=CATHODE, 3=ANODE (old note had 1=A 2=REF 3=K).
- XT30: KiCad AMASS footprint pad1 = '-', pad2 = '+' (old schematic had pin1 = +).
- Clamp raised to 2.66 V typ (22.9k/20k) so that 26.2 V charge (2.62 V/cell) stays below every clamp.
- 100R base resistor limits the TLV431 cathode current (<= ~7 mA) when the PNP is driven hard.
"""
import sys
import kisch2
from kisch2 import Sheet2, LibSym, Box

R = LibSym("R", "Device.kicad_sym", "R", "R")
CP = LibSym("CP", "Device.kicad_sym", "C_Polarized", "C")
PNP = LibSym("PNP", "Device.kicad_sym", "Q_PNP_BCE", "Q")          # BCP69 SOT-223: 1=B 2=C(tab) 3=E
F = LibSym("FUSE", "Device.kicad_sym", "Fuse", "F")
CON2 = LibSym("CON2", "Connector_Generic.kicad_sym", "Conn_01x02", "J")
_p = "passive"
TLV = Box("rev:TLV431_DBZ", "U", [None, ("1", "REF", _p), None], [("2", "K", _p), None, ("3", "A", _p)], width=10.16)

R06 = "Resistor_SMD:R_0603_1608Metric"
FP_CELL = "Capacitor_THT:CP_Radial_D18.0mm_P7.50mm"
kisch2.LCSC_MAP.update({
    ("R", "22.9k 0.1%"): "C4197857", ("R", "20k 0.1%"): "C723637", ("R", "1k"): "C21190", ("R", "100R"): "C22775",
    ("TLV431_DBZ", "TLV431BQDBZR"): "C398374", ("PNP", "BCP69-16"): "C75011",
    ("CON2", "XT30 bank"): "C428721", ("FUSE", "20A mini blade"): "C151096",
})

s = Sheet2("Rev B bank board v2 - 10S 2.7V 50F, per-cell clamp", paper="A3", proj="bank_board", path="/")
s.text(15, 12, "Rev B bank board v2   10S 2.7 V 50 F (27 V 5 F, 1822 J)   per-cell TLV431 + PNP parallel clamp", 2.5, bold=True)
s.text(15, 18, "Clamp Vc = Vref(1 + Ra/Rb) + Iref*Ra = 1.24 x (1 + 22.9k/20k) = 2.66 V typ  (25 C: about 2.644 - 2.689 V).  "
               "Charge 26.2 V = 2.62 V/cell average stays below every clamp.", 1.5)
s.text(15, 22, "TLV431 SOT-23 (DBZ) pinout from TI SLVS139Z Table 4-1: 1 = REF, 2 = CATHODE, 3 = ANODE.   "
               "Rbase 100R limits the TLV431 cathode current to about 7 mA (abs max 20 mA).", 1.5)
s.text(15, 26, "Only external interface: XT30 (S189).  Cells: 50 F 2.7 V, 18 x 40 mm radial, P 7.5 mm - hand soldered (not stocked at JLCPCB).  "
               "Fuse: 20 A mini blade (1 kA @ 32 V), soldered directly.", 1.5)

# ---------------- power port
J = s.add(CON2, 50.8, 80, "XT30 bank", {"1": "BANK_N", "2": "BANK_PIN"},
          props={"Footprint": "Connector_AMASS:AMASS_XT30UPB-M_1x02_P5.0mm_Vertical",
                 "Note": "AMASS footprint: pad1 = '-', pad2 = '+'. Mates with control board J102"}, text="right")
F1 = s.add(F, 38.1, J[2][1], "20A mini blade", {"1": "BANK_PIN", "2": "BANK_P"}, rot=270,
           props={"Footprint": "Fuse:Fuse_Blade_Mini_directSolder", "Note": "Littelfuse 0297020.WXNV, 32 V, 1 kA"}, text="above")
s.wire(J[2], F1[1])
s.label("BANK_PIN", ((J[2][0] + F1[1][0]) / 2, J[2][1]), "U")
s.wire(F1[2], (F1[2][0] - 5.08, F1[2][1]))
s.label("BANK_P", (F1[2][0] - 5.08, F1[2][1]), "L")
yn = J[1][1] - 7.62
s.wire(J[1], (J[1][0] - 2.54, J[1][1]), (J[1][0] - 2.54, yn), (F1[2][0] - 5.08, yn))
s.label("BANK_N", (F1[2][0] - 5.08, yn), "L")
s.frame(15.24, 60, 53.34, 38, "Power port (only external connection)")
s.text(J[2][0] - 1.27, J[2][1] + 7.62, "J1: pin1 = -, pin2 = +", 1.27)


# ---------------- cells
def node(k):
    return "BANK_N" if k == 0 else ("BANK_P" if k == 10 else f"V{k}")


H = 60.96       # rail spacing
for k in range(1, 11):
    col, row = (k - 1) % 5, (k - 1) // 5
    X, Y = 76.2 + col * 66.04, 50.8 + row * 101.6
    hi, lo = node(k), node(k - 1)
    s.frame(X - 7.62, Y - 10.16, 63.5, H + 17.78, f"Cell {k}")
    cell = s.add(CP, X + 5.08, Y + 30.48, "50F 2.7V", {"1": hi, "2": lo},
                 props={"Footprint": FP_CELL, "Note": "18x40 mm radial, hand solder"})
    ra = s.add(R, X + 15.24, Y + 11.43, "22.9k 0.1%", {"1": hi, "2": f"REF{k}"}, props={"Footprint": R06})
    rb = s.add(R, X + 15.24, Y + 44.45, "20k 0.1%", {"1": f"REF{k}", "2": lo}, props={"Footprint": R06})
    u = s.add(TLV, X + 25.4, Y + 27.94, "TLV431BQDBZR", {"1": f"REF{k}", "2": f"CAT{k}", "3": lo},
              props={"Footprint": "Package_TO_SOT_SMD:SOT-23", "Note": "DBZ: 1=REF 2=K 3=A"})
    rpu = s.add(R, u[2][0], Y + 12.7, "1k", {"1": hi, "2": f"CAT{k}"}, props={"Footprint": R06}, text="right")
    rbs = s.add(R, u[2][0] + 5.08, u[2][1], "100R", {"1": f"CAT{k}", "2": f"B{k}"}, rot=90,
                props={"Footprint": R06}, text="above")
    q = s.add(PNP, rbs[2][0] + 5.08, u[2][1], "BCP69-16", {"1": f"B{k}", "2": lo, "3": hi}, mirror="x",
              props={"Footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2"}, text="right")
    xr = q[3][0]
    # rails
    s.wire((X, Y), (xr, Y))
    s.wire((X, Y + H), (xr, Y + H))
    s.label(hi, (X, Y), "L")
    s.label(lo, (X, Y + H), "L")
    s.wire(cell[1], (cell[1][0], Y))
    s.wire(cell[2], (cell[2][0], Y + H))
    s.wire(ra[1], (ra[1][0], Y))
    s.wire(rb[2], (rb[2][0], Y + H))
    s.wire(ra[2], rb[1])                       # REF divider node
    s.wire(u[1], (ra[2][0], u[1][1]))
    s.wire(rpu[1], (rpu[1][0], Y))
    s.wire(rpu[2], u[2])                       # pull-up to cathode
    s.wire(u[2], rbs[1])
    s.wire(rbs[2], q[1])
    s.wire(u[3], (u[3][0], Y + H))
    s.wire(q[3], (q[3][0], Y))
    s.wire(q[2], (q[2][0], Y + H))

s.write(sys.argv[1])
o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch2")'] + [sy.file_def() for sy in s.syms.values()] + [")"]
open(sys.argv[1].replace("bank_board.kicad_sch", "rev.kicad_sym"), "w", encoding="utf-8").write("\n".join(o) + "\n")
errs, got = kisch2.check(sys.argv[1], [s])
print("parts", len(s.parts), "nets", len(got))
for e in errs:
    print("  ", e)
print("CHECK", "OK" if not errs else f"{len(errs)} problems")
