"""After swapfet: full zone connection on drain pads, re-run the two gate traces that pass between S and D pads."""
import sys, pcbnew
mm, T = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
for f in b.GetFootprints():
    if f.GetReference() in ("Q102", "Q103", "Q104", "Q105"):
        for p in f.Pads():
            if p.GetNumber() == "5":
                p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

def P(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))
def near(a, x, y): return abs(T(a.x) - x) < 1e-3 and abs(T(a.y) - y) < 1e-3
def seg(net, pts):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(mm(0.2))
        t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net)); b.Add(t)

kill = {  # net: list of segments (start,end) to delete
    "/buckboost/LG1": [((135.905, 120.9), (135.905, 120.2231)), ((135.905, 120.2231), (131.7122, 120.2231)),
                       ((131.7122, 120.2231), (131.5861, 120.3492)), ((131.5861, 120.3492), (131.5861, 122.6032)),
                       ((131.5861, 122.6032), (132.1348, 123.1519))],
    "/buckboost/HG2": [((160.405, 109.9), (160.405, 109.2231)), ((160.405, 109.2231), (148.1147, 109.2231))],
}
dead = []
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK" or t.GetNetname() not in kill: continue
    for (s, e) in kill[t.GetNetname()]:
        if (near(t.GetStart(), *s) and near(t.GetEnd(), *e)) or (near(t.GetStart(), *e) and near(t.GetEnd(), *s)):
            dead.append(t)
print("moving", len(dead), "segments")
for t in dead:
    t.SetLayer(pcbnew.Dwgs_User); t.SetNet(b.FindNet(""))   # park on a drawing layer (Remove() crashes SWIG)
yq3, yq4 = 118.0 + 1.765, 107.0 + 1.765
seg("/buckboost/LG1", [(135.905, 120.747), (135.905, yq3), (131.35, yq3), (131.35, 122.367), (132.1348, 123.1519)])
seg("/buckboost/HG2", [(160.405, 109.747), (160.405, yq4), (155.9, yq4), (155.4419, 109.2231), (148.1147, 109.2231)])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
pcbnew.WriteDRCReport(b, sys.argv[2].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
