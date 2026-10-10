"""Rev B bank board (10S 2.7V 50F) - per-cell parallel clamp balancing (plan Y, provisional).

Single XT30 power port + fuse. No sense/communication lines leave the board (S189).
Per cell: TLV431 shunt reference (Vref 1.24V) sets the clamp; PNP bypass shunts surplus current.
TLV431 SOT-23 (DBZ) pin map from TI SLVS139Z (rev. June 2024): 1=ANODE, 2=REF, 3=CATHODE.
(NOTE: differs from TL431DBZ numbering used in KiCad's TL431 symbol -> own symbol here.)
"""
import sys
from kisch import Sheet, LibSym, Sym

PATH = sys.argv[2] if len(sys.argv) > 2 else "/"
R = LibSym("R", "rev.kicad_sym", "R", "R")
C = LibSym("C", "rev.kicad_sym", "C", "C")
CP = LibSym("CP", "rev.kicad_sym", "CP", "C")
TLV = Sym("rev:TLV431_DBZ", "U", [("1", "ANODE", "L", "passive"), ("2", "REF", "L", "passive"), ("3", "CATHODE", "R", "passive")], width=12.7)
PNP = Sym("rev:Q_PNP_BCE", "Q", [("1", "B", "L", "passive"), ("2", "C", "R", "passive"), ("3", "E", "R", "passive")], width=12.7)
FUSE = Sym("rev:FUSE2", "F", [("1", "1", "L", "passive"), ("2", "2", "R", "passive")], width=10.16)
CON2 = Sym("rev:XT30_2P", "J", [("1", "+", "L", "passive"), ("2", "-", "L", "passive")], width=10.16)
TP = Sym("rev:TP", "TP", [("1", "1", "L", "passive")], width=5.08)

s = Sheet("Rev B bank board - 10S 2.7V 50F with per-cell clamp (plan Y, provisional)", "A2", proj="bank_board", path=PATH, ref_base=0)
R06 = "Resistor_SMD:R_0603_1608Metric"


def node(k):
    return "BANK_N" if k == 0 else ("BANK_P" if k == 10 else f"V{k}")


s.text(20, 17, "Rev B bank board: 10S 2.7V 50F, per-cell TLV431 + PNP parallel clamp  -  plan Y, PROVISIONAL (not verified by test)", 3.0)
s.text(20, 26, "Clamp Vc = Vref*(1+Ra/Rb) = 1.24*(1+22.1k/20k) = 2.61V typ. Worst-case spread (Vref, Iref*Ra, temp) ~2.57-2.68V; rated 2.7V. See docs/revb/bank_board.md.", 1.6)
s.text(20, 31, "Only external interface: XT30 power (S189). Fuse rating/type TBD. PNP candidate BCP69 (SOT-223) datasheet NOT checked. Cell terminals/footprint TBD (mechanical).", 1.6)

# power entry
s.frame(20, 40, 150, 60, "Power port", "XT30 -> fuse -> stack top")
s.place(CON2, 50, 75, "XT30 (bank port)", {"1": "BANK_PIN", "2": "BANK_N"}, props={"Footprint": "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"})
s.place(FUSE, 110, 70, "Fuse TBD (>=15A class, DC>=32V)", {"1": "BANK_PIN", "2": "BANK_P"}, props={"Footprint": "TBD"})

# cells and clamps
X0, DX = 30, 70
s.frame(20, 110, X0 - 20 + DX * 10 + 10, 330, "10 cells with clamp", "Each column: cell k between V(k-1) and Vk.")
for k in range(1, 11):
    x = X0 + (k - 1) * DX
    lo, hi = node(k - 1), node(k)
    ck = f"C{k}"
    s.text(x, 125, f"Cell {k}", 1.8)
    s.place(CP, x + 10, 170, "50F 2.7V (cell)", {"1": hi, "2": lo}, props={"Footprint": "TBD", "Note": "cell terminals mechanical TBD"})
    s.place(R, x + 30, 150, "22.1k 0.1%", {"1": hi, "2": f"REF{k}"}, props={"Footprint": R06})
    s.place(R, x + 30, 190, "20k 0.1%", {"1": f"REF{k}", "2": lo}, props={"Footprint": R06})
    s.place(TLV, x + 30, 240, "TLV431B (SOT-23)", {"1": lo, "2": f"REF{k}", "3": f"CAT{k}"}, props={"Footprint": "Package_TO_SOT_SMD:SOT-23", "Note": "pin map DBZ: 1=A 2=REF 3=K"})
    s.place(R, x + 10, 215, "1k", {"1": hi, "2": f"CAT{k}"}, props={"Footprint": R06})
    s.place(PNP, x + 30, 300, "PNP bypass (BCP69 cand.)", {"1": f"CAT{k}", "2": lo, "3": hi}, props={"Footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "Note": "Ic>=1A, P~1.3W at 0.5A"})
for k in range(0, 11):
    s.place(TP, 30 + k * 60, 400, node(k), {"1": node(k)}, props={"Footprint": "TestPoint:TestPoint_Pad_D1.5mm"})

s.write(sys.argv[1])
with open(sys.argv[1].replace(".kicad_sch", "_bom.csv"), "w", encoding="utf-8") as fh:
    fh.write("Ref,Value,LCSC,Footprint,Symbol\n")
    for row in s.bom:
        fh.write(",".join('"%s"' % x for x in row) + "\n")
syms = s.syms
o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch")']
o += [sy.file_def() for sy in syms.values()]
o.append(")")
open(sys.argv[1].replace(".kicad_sch", "_rev.kicad_sym"), "w", encoding="utf-8").write("\n".join(o) + "\n")
print("wrote", sys.argv[1], len(s.bom), "parts")
