"""Rev B bank board v2 PCB: 10 x (18x40 mm, P7.5) cells standing 5 x 2, clamp SMD on the bottom, 2 layers.

usage: python3 build_bank.py bank.net footprint_dir out.kicad_pcb
Board-relative mm (origin = top-left of the outline), KiCad absolute = +100.
Series path: row 1 C1..C5 left->right (- left, + right), turn at the right end, row 2 C6..C10 right->left.
Every node V0..V10 is a copper pour on F.Cu and B.Cu between two neighbouring cell centres.
Per cell the clamp parts sit under the cell on B.Cu; lo-net pads left of the cell centre line, hi-net
pads right of it (cell-local frame: u along the row from - to +, v towards the board middle).
"""
import math
import re
import sys

import pcbnew

NET, KFP, OUT = sys.argv[1:4]
OX = OY = 100.0
mm = pcbnew.FromMM
T = pcbnew.ToMM
P_CELL = 19.0                  # cell pitch (18 mm cans + 1 mm)
XL = 13.0                      # left strip for XT30 + fuse
XC = [XL + P_CELL / 2 + P_CELL * i for i in range(5)]
Y1, Y2 = 10.0, 29.0
W, H = round(XC[4] + P_CELL / 2 + 0.5, 1), 39.0
YM = (Y1 + Y2) / 2             # row split
GAP = 0.5                      # half gap between node pours


def V(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


# ------------------------------------------------------------- netlist
t = open(NET, encoding="utf-8").read()
comps = re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)', t)
meta = {}
for blk in re.split(r'\n    \(comp ', t)[1:]:
    r_ = re.search(r'\(ref "([^"]+)"\)', blk).group(1)
    sp = re.search(r'\(sheetpath \(names "[^"]*"\) \(tstamps "([^"]*)"\)\)', blk)
    ts = re.search(r'\)\)\s*\(tstamps "([^"]*)"\)\)', blk)
    lc = re.search(r'\(property \(name "LCSC"\) \(value "([^"]*)"\)\)', blk)
    meta[r_] = (sp.group(1) if sp else "/", ts.group(1) if ts else "", lc.group(1) if lc else "")
pad_net = {}
for m in re.finditer(r'\(net \(code "\d+"\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', t, re.S):
    for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
        pad_net[(ref, pin)] = m.group(1)

b = pcbnew.BOARD()
b.SetCopperLayerCount(2)
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.15)
ds.m_ViasMinSize = mm(0.5)
ds.m_MinThroughDrill = mm(0.25)
ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.2))
nc.SetTrackWidth(mm(0.25))
nc.SetViaDiameter(mm(0.6))
nc.SetViaDrill(mm(0.3))

nets = {}


def net(name):
    if not name.startswith("/") and "/" + name in pad_net.values():
        name = "/" + name             # local schematic labels carry the sheet path
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(b, name)
        b.Add(n)
        nets[name] = n
    return nets[name]


fps = {}
for ref, val, fpid in comps:
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(f"{KFP}/{lib}.pretty", name)
    assert fp, fpid
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    sp_, ts_, lc_ = meta[ref]
    fp.SetPath(pcbnew.KIID_PATH(sp_ + ts_))
    if lc_:
        fp.SetProperty("LCSC", lc_)
    b.Add(fp)
    for pad in fp.Pads():
        n = pad_net.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(net(n))
    fps[ref] = fp


def place(ref, x, y, rot, bottom=False):
    fp = fps[ref]
    fp.SetPosition(V(x, y))
    if bottom and not fp.IsFlipped():
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(rot % 360)


# ------------------------------------------------------------- cells
def cell_frame(k):
    """cell k (1..10) -> (xc, yc, s) ; s = +1 row 1 (u = +x), -1 row 2 (rotated 180)."""
    if k <= 5:
        return XC[k - 1], Y1, 1
    return XC[10 - k], Y2, -1


def loc(k, u, v):
    xc, yc, s = cell_frame(k)
    return xc + s * u, yc + s * v


# CP_Radial: pad1 (+) at origin, pad2 (-) at +7.5 -> rotate 180 so that + is at u = +3.75
for k in range(1, 11):
    x, y = loc(k, 3.75, 0)
    place(f"C{k}", x, y, 180 if k <= 5 else 0)

# per-cell clamp, local positions (u, v, local rot) on B.Cu; refs: Ra R(4k-3), Rb R(4k-2), Rpu R(4k-1), Rbase R(4k)
LOCAL = {"Q": (0.0, 5.3, 180), "U": (0.6, -4.5, 180),
         "Ra": (3.4, -6.4, 270), "Rb": (-0.4, -7.2, 180), "Rpu": (6.82, 5.4, 90), "Rbase": (6.0, 3.0, 180)}
for k in range(1, 11):
    s = cell_frame(k)[2]
    refs = {"Q": f"Q{k}", "U": f"U{k}", "Ra": f"R{4 * k - 3}", "Rb": f"R{4 * k - 2}", "Rpu": f"R{4 * k - 1}", "Rbase": f"R{4 * k}"}
    for key, (u, v, r) in LOCAL.items():
        x, y = loc(k, u, v)
        place(refs[key], x, y, r + (0 if s > 0 else 180), bottom=True)

# power port
place("J1", 4.6, 11.0, 270)
place("F1", 10.3, 18.0, 270)

# mounting holes (board only, between 2 x 2 cells)
HOLES = [(XC[0] + P_CELL / 2, YM), (XC[3] + P_CELL / 2, YM)]
for i, (hx, hy) in enumerate(HOLES):
    h = pcbnew.FootprintLoad(f"{KFP}/MountingHole.pretty", "MountingHole_3.2mm_M3")
    h.SetReference(f"H{i + 1}")
    h.SetValue("M3")
    h.Reference().SetVisible(False)
    h.SetAttributes(h.GetAttributes() | pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
    b.Add(h)
    h.SetPosition(V(hx, hy))

# ------------------------------------------------------------- tracks (cell-local templates)
TW = 0.25
TRACKS = [  # (net key, width, [(u, v), ...])
    ("C", 0.6, [(3.15, 5.3), (-3.15, 5.3)]),                       # Q pin2 -> tab (collector)
    ("B", TW, [(3.15, 3.0), (5.18, 3.0)]),                          # Q base -> Rbase
    ("CAT", TW, [(6.82, 4.58), (6.82, 3.0)]),                       # Rpu -> Rbase
    ("CAT", TW, [(6.82, 3.0), (6.82, -3.55), (1.6, -3.55)]),        # Rbase -> TLV431 K
    ("REF", TW, [(3.4, -5.58), (1.6, -5.58), (1.6, -5.45)]),        # Ra -> TLV431 REF
    ("REF", TW, [(0.42, -7.2), (1.0, -7.2), (1.6, -6.6), (1.6, -5.58)]),   # Rb -> REF
    ("LO", 0.4, [(-0.4, -4.5), (-1.4, -4.5)]),                      # TLV431 anode into the lo pour
]


def node(k):
    return "BANK_N" if k == 0 else ("BANK_P" if k == 10 else f"V{k}")


def add_track(pts, width, netname, layer=pcbnew.B_Cu):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        tr = pcbnew.PCB_TRACK(b)
        tr.SetStart(V(x1, y1))
        tr.SetEnd(V(x2, y2))
        tr.SetWidth(mm(width))
        tr.SetLayer(layer)
        tr.SetNet(net(netname))
        b.Add(tr)


VIAS = [(-5.0, 3.8, 0), (-5.0, 5.3, 0), (-5.0, 6.8, 0), (-1.2, 2.6, 0),   # PNP tab (collector, lo pour) to F.Cu
        (5.0, 7.9, 1), (1.3, 7.6, 1)]                                     # PNP emitter (hi pour) to F.Cu
for k in range(1, 11):
    for u, v, hi in VIAS:
        x, y = loc(k, u, v)
        via = pcbnew.PCB_VIA(b)
        via.SetPosition(V(x, y))
        via.SetWidth(mm(0.6))
        via.SetDrill(mm(0.3))
        via.SetNet(net(node(k - 1 + hi)))
        b.Add(via)
for k in range(1, 11):
    names = {"C": node(k - 1), "B": pad_net[(f"Q{k}", "1")], "CAT": pad_net[(f"U{k}", "2")],
             "REF": pad_net[(f"U{k}", "1")], "LO": node(k - 1)}
    for key, w, pts in TRACKS:
        add_track([loc(k, u, v) for u, v in pts], w, names[key])

# ------------------------------------------------------------- outline
edge = [(0, 0), (W, 0), (W, H), (0, H)]
for (x1, y1), (x2, y2) in zip(edge, edge[1:] + edge[:1]):
    sg = pcbnew.PCB_SHAPE(b)
    sg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    sg.SetStart(V(x1, y1))
    sg.SetEnd(V(x2, y2))
    sg.SetLayer(pcbnew.Edge_Cuts)
    sg.SetWidth(mm(0.1))
    b.Add(sg)


# ------------------------------------------------------------- node pours (both layers)
def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


E = 0.4   # inset from the board edge
POURS = {
    "BANK_N": [(E, E), (XC[0] - GAP, E), (XC[0] - GAP, YM - GAP), (XL, YM - GAP), (XL, 13.4), (E, 13.4)],
    "BANK_PIN": rect(E, 14.4, XL - 0.6, 21.6),
    "BANK_P": [(E, 22.6), (XL, 22.6), (XL, YM + GAP), (XC[0] - GAP, YM + GAP), (XC[0] - GAP, H - E), (E, H - E)],
    "V5": rect(XC[4] + GAP, E, W - E, H - E),
}
for k in range(1, 5):      # row 1: V1..V4 between cell k and k+1
    POURS[f"V{k}"] = rect(XC[k - 1] + GAP, E, XC[k] - GAP, YM - GAP)
for j in range(1, 5):      # row 2: V6..V9
    col = 5 - j
    POURS[f"V{5 + j}"] = rect(XC[col - 1] + GAP, YM + GAP, XC[col] - GAP, H - E)


def add_zone(netname, pts, layer):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net(netname))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(mm(OX + x), mm(OY + y))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)


for n, pts in POURS.items():
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        add_zone(n, pts, lay)

# keepouts around the M3 holes (screw head / washer 7 mm)
for hx, hy in HOLES:
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    ol = z.Outline()
    ol.NewOutline()
    for i in range(24):
        a = 2 * math.pi * i / 24
        ol.Append(mm(OX + hx + 3.6 * math.cos(a)), mm(OY + hy + 3.6 * math.sin(a)))
    b.Add(z)

# ------------------------------------------------------------- silk / text
for ref, fp in fps.items():
    rt = fp.Reference()
    if ref.startswith("C"):
        k = int(ref[1:])
        x, y = loc(k, 4.2, -5.2)
        rt.SetPosition(V(x, y))
        rt.SetTextAngleDegrees(0)
        rt.SetTextSize(pcbnew.VECTOR2I(mm(1.5), mm(1.5)))
        rt.SetTextThickness(mm(0.22))
    elif fp.IsFlipped() or ref.startswith("H"):
        rt.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
    fp.Value().SetVisible(False)


def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0):
    tx = pcbnew.PCB_TEXT(b)
    tx.SetText(s)
    tx.SetPosition(V(x, y))
    tx.SetLayer(layer)
    tx.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    tx.SetTextThickness(mm(0.15))
    tx.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        tx.SetMirrored(True)
    b.Add(tx)


text("BANK 10S 2.7V 50F  rev B", XC[2], YM, 1.0, pcbnew.B_SilkS)

b.Save(OUT)
b = pcbnew.LoadBoard(OUT)          # a freshly built BOARD crashes ZONE_FILLER; reload first
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(OUT)
pcbnew.WriteDRCReport(b, OUT.replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
print("board", W, "x", H, "mm")
