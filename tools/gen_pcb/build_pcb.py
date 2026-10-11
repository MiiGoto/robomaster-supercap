"""Build the Rev B control board PCB (placement + outline + zones) from the KiCad netlist with pcbnew (KiCad 7).

usage: python3 build_pcb.py board.net out.kicad_pcb
Placement coordinates are board-relative mm (origin = top-left corner of the outline).
"""
import re
import sys

import pcbnew

KFP = "/tmp/claude-0/-home-claude/80c875b0-5767-57b7-8350-9ee3ea570a9c/scratchpad/kfp"
OX, OY = 100.0, 100.0
W, H = 68.0, 57.0
mm = pcbnew.FromMM


def P(x, y):
    return pcbnew.VECTOR2I(mm(float(OX + x)), mm(float(OY + y)))


# ------------------------------------------------------------------ netlist
t = open(sys.argv[1], encoding="utf-8").read()
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

# ------------------------------------------------------------------ placement  ref: (x, y, rot[, 'B'])
PL = {
    # power input (left)
    "J1": (4.2, 11.0, 270), "F1": (9.6, 16.0, 0), "D1": (10.0, 23.5, 180), "Q1": (17.5, 16.0, 180),
    "R4": (27.0, 13.7, 0),
    # buck leg / inductor / boost leg (top band)
    "Q102": (34.0, 7.0, 90), "Q103": (34.0, 18.0, 90), "L101": (46.0, 12.0, 0),
    "Q104": (58.5, 7.0, 90), "Q105": (58.5, 18.0, 90), "R113": (46.0, 25.0, 270),
    # input caps (VIN_P) above Q1/R4
    "C1": (21.0, 3.2, 90), "C2": (23.6, 3.2, 90), "C3": (26.2, 3.2, 90), "C4": (28.8, 3.2, 90),
    "C5": (21.0, 8.4, 90), "C6": (23.6, 8.4, 90), "C7": (12.5, 5.5, 180),
    # output caps (NODE) along the right edge
    "C108": (65.0, 3.2, 0), "C109": (65.0, 6.2, 0), "C110": (65.0, 9.2, 0), "C111": (65.0, 12.2, 0),
    "C112": (65.0, 15.2, 0), "C113": (61.5, 26.0, 0), "D101": (52.0, 28.0, 90),
    # outputs (bottom right)
    "J101": (60.0, 37.0, 180), "R114": (49.5, 43.0, 270), "J102": (55.0, 50.0, 180),
    "J202": (34.5, 52.5, 0), "J203": (42.5, 52.5, 0),
    # controllers
    "U101": (36.0, 33.5, 0), "U202": (10.5, 45.0, 0), "J201": (2.2, 40.0, 0),
}
# small parts: greedy placement near the pads they connect to (order matters), optional hint (x, y)
GROUPS = [
    ((10.0, 25.0), ["D2", "R1", "R2", "Q2", "R3"]),
    ((7.0, 29.0), ["D201", "D202", "D203", "R201", "C201", "C202", "U201", "L201", "C203", "C204", "C205"]),
    ((21.0, 22.0), ["U1", "C9", "R9", "C10", "R5", "Q3", "C8", "R6", "R7", "R8"]),
    ((36.0, 33.5), ["R109", "R110", "R111", "R112", "C106", "C107", "C105", "R101", "R102", "Q101", "R103",
                    "R104", "R105", "C101", "C102", "C103", "R106", "C104", "R107", "R108"]),
    ((43.0, 46.0), ["U102", "C114", "R115", "C115"]),
    ((8.0, 44.0), ["C206", "C207", "C208", "C209", "C210", "C211", "Y201", "C212", "C213", "C214", "R202"]),
    ((26.0, 50.0), ["U203", "C215", "R203", "R204", "R205", "R206", "R207", "D204", "D205"]),
    ((26.0, 42.0), ["R306", "U301", "R307", "R308", "C304", "U302", "C307", "R309", "R310", "C305", "R311", "R312",
                    "R313", "R314", "C306", "R315", "R316", "R317", "R318", "R319", "Q301", "Q302", "Q303",
                    "R320", "R321", "R301", "R302", "C301", "R303", "R304", "C302", "TH301", "R305", "C303"]),
]
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(4)
ds.m_TrackMinWidth = mm(0.127)
ds.m_ViasMinSize = mm(0.45)
ds.m_MinThroughDrill = mm(0.2)
ds.m_CopperEdgeClearance = mm(0.3)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.15))
nc.SetTrackWidth(mm(0.2))
nc.SetViaDiameter(mm(0.6))
nc.SetViaDrill(mm(0.3))

nets = {}


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
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
    if ref in meta:
        sp_, ts_, lc_ = meta[ref]
        fp.SetPath(pcbnew.KIID_PATH(sp_ + ts_))
        if lc_:
            try:
                fp.SetProperty("LCSC", lc_)
            except Exception:
                pass
    board.Add(fp)
    x, y, rot = PL.get(ref, (W + 10, 0, 0))[:3]
    fp.SetPosition(P(x, y))
    fp.SetOrientationDegrees(rot)
    fp.BuildCourtyardCaches()
    for pad in fp.Pads():
        n = pad_net.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(net(n))
    fps[ref] = fp
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
    fp.Reference().SetTextThickness(mm(0.12))

# ------------------------------------------------------------------ greedy placement of small parts
HOLES = [(3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5)]
BIGNETS = {"GND", "+3V3", "NODE", "VIN_P"}


def cbox(fp, margin=0.2):
    fp.BuildCourtyardCaches()
    sh = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = sh.BBox() if sh.OutlineCount() else fp.GetBoundingBox(False, False)
    return (pcbnew.ToMM(bb.GetX()) - OX - margin, pcbnew.ToMM(bb.GetY()) - OY - margin,
            pcbnew.ToMM(bb.GetRight()) - OX + margin, pcbnew.ToMM(bb.GetBottom()) - OY + margin)


placed = {r: cbox(fps[r], {'U202': 1.2, 'U101': 0.3}.get(r, 0.0)) for r in fps if r in PL and not any(r in g[1] for g in GROUPS)}
_ks = list(placed)
for i, a in enumerate(_ks):
    A = placed[a]
    for b in _ks[i + 1:]:
        B = placed[b]
        if A[0] < B[2] and A[2] > B[0] and A[1] < B[3] and A[3] > B[1]:
            print("fixed overlap", a, b)


import numpy as np
RES = 0.25
MARGIN = 0.15
GW, GH = int(W / RES), int(H / RES)
occ = np.zeros((GH, GW), dtype=np.int32)


def mark(b):
    x0, y0 = max(0, int(math.floor(b[0] / RES))), max(0, int(math.floor(b[1] / RES)))
    x1, y1 = min(GW, int(math.ceil(b[2] / RES))), min(GH, int(math.ceil(b[3] / RES)))
    occ[y0:y1, x0:x1] = 1


import math
EDGE = 0.4
occ[:, :int(EDGE / RES)] = 1
occ[:, GW - int(EDGE / RES):] = 1
occ[:int(EDGE / RES), :] = 1
occ[GH - int(EDGE / RES):, :] = 1
for hx, hy in HOLES:
    mark((hx - 3.7, hy - 3.7, hx + 3.7, hy + 3.7))
for r, bb in placed.items():
    mark(bb)
# routing channels kept free of small parts
for ch in ((30.2, 28.6, 32.6, 38.6), (39.4, 28.6, 41.2, 38.6)):
    mark(ch)
# power pours (route.py) are reserved for the power stage
sys.path.insert(0, ".")
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
import importlib.util as _iu
_spec = _iu.spec_from_file_location("route_zones", "route.py")
_src = open("route.py").read()
_ns = {}
exec(_src[_src.index("ZONES_F = {"):_src.index("def add_zone")], {"pcbnew": pcbnew}, _ns)
for n, pts in _ns["ZONES_F"].items():
    pg = prep(Polygon(pts).buffer(0.3))
    x0, y0, x1, y1 = Polygon(pts).buffer(0.3).bounds
    for gy in range(max(0, int(y0 / RES)), min(GH, int(y1 / RES) + 1)):
        for gx in range(max(0, int(x0 / RES)), min(GW, int(x1 / RES) + 1)):
            if pg.contains(Point((gx + 0.5) * RES, (gy + 0.5) * RES)):
                occ[gy, gx] = 1


def target(ref, hint):
    pts = []
    for pad in fps[ref].Pads():
        n = pad.GetNetname()
        if not n or n in BIGNETS:
            continue
        for r2, fp2 in fps.items():
            if r2 == ref or r2 not in placed:
                continue
            for p2 in fp2.Pads():
                if p2.GetNetname() == n:
                    pos = p2.GetPosition()
                    pts.append((pcbnew.ToMM(pos.x) - OX, pcbnew.ToMM(pos.y) - OY))
    if not pts:
        return hint
    x = sum(p[0] for p in pts) / len(pts)
    y = sum(p[1] for p in pts) / len(pts)
    return (0.7 * x + 0.3 * hint[0], 0.7 * y + 0.3 * hint[1])


import os, random
_rng = random.Random(int(os.environ.get('SEED', '0')))
JIT = float(os.environ.get('JIT', '0'))
yy, xx = np.mgrid[0:GH, 0:GW]
for hint, refs in GROUPS:
    for ref in refs:
        if ref in placed:
            continue
        fp = fps[ref]
        tx, ty = target(ref, hint)
        tx += _rng.uniform(-JIT, JIT)
        ty += _rng.uniform(-JIT, JIT)
        I = np.pad(occ, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
        best = None
        for rot in (0, 90):
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(P(0, 0))
            b = cbox(fp, MARGIN)
            w, h = int(math.ceil((b[2] - b[0]) / RES)), int(math.ceil((b[3] - b[1]) / RES))
            if w >= GW or h >= GH:
                continue
            # window sums for top-left corners
            S = I[h:, w:] - I[:-h, w:] - I[h:, :-w] + I[:-h, :-w]
            ok = S == 0
            if not ok.any():
                continue
            cy, cx = np.nonzero(ok)
            # centre of footprint origin for each candidate: origin offset = -b[0], -b[1]
            ox = cx * RES - b[0]
            oy = cy * RES - b[1]
            d = (ox - tx) ** 2 + (oy - ty) ** 2
            k = int(np.argmin(d))
            if best is None or d[k] < best[0]:
                best = (float(d[k]), float(ox[k]), float(oy[k]), rot)
        if not best:
            print("NO SPACE", ref)
            fp.SetPosition(P(W + 5, 5))
            continue
        _, x, y, rot = best
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(P(x, y))
        placed[ref] = cbox(fp, MARGIN)
        mark(placed[ref])
        PL[ref] = (x, y, rot)

# outline
for (x1, y1, x2, y2) in ((0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1))
    s.SetEnd(P(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    board.Add(s)

# mounting holes (M3)
for i, (x, y) in enumerate(((3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5))):
    h = pcbnew.FootprintLoad(f"{KFP}/MountingHole.pretty", "MountingHole_3.2mm_M3")
    h.SetReference(f"H{i + 1}")
    h.SetPosition(P(x, y))
    board.Add(h)

board.Save(sys.argv[2])
off = [r for r in fps if r not in PL]
open(sys.argv[2].replace(".kicad_pcb", "_placement.txt"), "w").write("\n".join(f"{r} {v[0]:.2f} {v[1]:.2f} {v[2]}" for r, v in sorted(PL.items())))
print("placed", len(fps) - len(off), "unplaced", off)
