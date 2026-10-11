"""Enlarge 0.5/0.25 vias to 0.6/0.3 where clearance allows. usage: viafix.py in out"""
import sys
import pcbnew
from shapely.geometry import Point, LineString, box
from shapely.strtree import STRtree
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
items = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        items.append((p.GetNetname(), box(T(bb.GetX()), T(bb.GetY()), T(bb.GetRight()), T(bb.GetBottom()))))
vias = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        g = Point(T(t.GetPosition().x), T(t.GetPosition().y)).buffer(T(t.GetWidth()) / 2)
        items.append((t.GetNetname(), g))
        vias.append(t)
    else:
        items.append((t.GetNetname(), LineString([(T(t.GetStart().x), T(t.GetStart().y)), (T(t.GetEnd().x), T(t.GetEnd().y))]).buffer(T(t.GetWidth()) / 2)))
geoms = [g for _, g in items]
tree = STRtree(geoms)
n = k = 0
for v in vias:
    if v.GetDrill() >= pcbnew.FromMM(0.3):
        continue
    n += 1
    c = Point(T(v.GetPosition().x), T(v.GetPosition().y))
    ok = True
    for i in tree.query(c.buffer(0.3 + 0.152)):
        net, g = items[i]
        if net != v.GetNetname() and g.distance(c) < 0.3 + 0.152:
            ok = False
            break
    if ok:
        v.SetDrill(pcbnew.FromMM(0.3))
        v.SetWidth(pcbnew.FromMM(0.6))
        k += 1
print("small vias", n, "enlarged", k)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
pcbnew.WriteDRCReport(b, sys.argv[2].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
