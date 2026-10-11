"""Add power zones + GND plane, export DSN for Freerouting, or import SES and finish (pours, fill).

usage: python3 route.py prep  in.kicad_pcb out.kicad_pcb out.dsn
       python3 route.py finish in.kicad_pcb in.ses out.kicad_pcb
"""
import sys

import pcbnew

OX, OY = 100.0, 100.0
W, H = 68.0, 57.0
mm = pcbnew.FromMM

ZONES_F = {  # net name -> polygon (board mm)
    "Net-(J1-Pin_2)": [(2.4, 14.2), (9.0, 14.2), (9.0, 17.8), (2.4, 17.8)],
    "VIN_F": [(10.3, 12.6), (19.1, 12.6), (19.1, 19.3), (14.2, 19.3), (14.2, 25.2), (10.3, 25.2)],
    "VIN_C": [(20.3, 11.8), (25.0, 11.8), (25.0, 15.7), (20.3, 15.7)],
    "VIN_P": [(13.2, 3.4), (37.0, 3.4), (37.0, 8.7), (31.3, 8.7), (31.3, 15.8), (28.9, 15.8), (28.9, 11.2),
              (13.2, 11.2)],
    "/buckboost/SW1": [(31.5, 9.2), (35.3, 9.2), (35.3, 10.8), (43.3, 10.8), (43.3, 14.8), (36.5, 14.8),
                       (36.5, 19.4), (31.5, 19.4)],
    "/buckboost/SW2": [(49.2, 10.8), (56.0, 10.8), (56.0, 9.2), (59.8, 9.2), (59.8, 10.8), (60.95, 10.8),
                       (60.95, 19.4), (55.9, 19.4), (55.9, 14.8), (49.2, 14.8)],
    "NODE": [(55.9, 0.5), (67.5, 0.5), (67.5, 41.2), (46.8, 41.2), (46.8, 31.6), (50.2, 31.6), (50.2, 27.3),
             (55.0, 27.3), (55.0, 23.8), (61.3, 23.8), (61.3, 8.7), (55.9, 8.7)],
    "/buckboost/CS_N": [(31.5, 20.0), (35.3, 20.0), (35.3, 21.75), (55.9, 21.75), (55.9, 20.0), (59.8, 20.0),
                        (59.8, 23.3), (31.5, 23.3)],
    "Net-(J102-Pin_2)": [(47.6, 45.2), (52.6, 45.2), (52.6, 51.7), (47.6, 51.7)],
}


def add_zone(board, net, layer, pts, prio=1, clearance=0.25, minw=0.25):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(net))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(minw))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def add_keepout(board, pts, layers, holes=()):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowCopperPour(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(OX + x), mm(OY + y))
    for h in holes:
        hi = o.NewHole()
        for x, y in h:
            o.Append(mm(OX + x), mm(OY + y), 0, hi)
    board.Add(z)


def gnd_fanout(b):
    from shapely.geometry import Polygon as SP, Point as SPt, box as SBox
    from shapely.ops import unary_union

    def pad_poly(pd):
        bb = pd.GetBoundingBox()
        return SBox(pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))

    def seg_poly(t):
        from shapely.geometry import LineString
        return LineString([(pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)),
                           (pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y))]).buffer(pcbnew.ToMM(t.GetWidth()) / 2)

    def obstacles(net):
        """union of copper of other nets on any layer + holes + edge (via goes through all layers)."""
        obs = []
        for fp in b.GetFootprints():
            for pd in fp.Pads():
                if pd.GetNetname() != net or pd.GetDrillSize().x > 0:
                    obs.append(pad_poly(pd))
        for t in b.GetTracks():
            if t.GetNetname() != net or t.GetClass() == "PCB_VIA":
                if t.GetClass() == "PCB_VIA":
                    obs.append(SPt(pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)).buffer(pcbnew.ToMM(t.GetWidth()) / 2))
                else:
                    obs.append(seg_poly(t))
        for z in b.Zones():  # other-net pours on F.Cu are refilled later, but keep vias out of their pads area only
            pass
        u = unary_union(obs)
        edge = SBox(OX, OY, OX + W, OY + H).exterior.buffer(0.6)
        return unary_union([u, edge])

    obs = obstacles("GND")
    vr, cl = 0.25, 0.2
    added = 0
    gvias = []
    POWER_GND = {"R113": 6, "D101": 4, "D1": 4, "C113": 3, "C7": 3, "C1": 2, "C2": 2, "C3": 2, "C4": 2, "C5": 2,
                 "C6": 2, "C108": 2, "C109": 2, "C110": 2, "C111": 2, "C112": 2}
    jobs = []
    for fp in b.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetname() != "GND" or pd.GetDrillSize().x > 0 or not pd.IsOnLayer(pcbnew.F_Cu):
                continue
            for rep in range(POWER_GND.get(fp.GetReference(), 1)):
                jobs.append((fp, pd, rep))
    for fp, pd, rep in jobs:
        if True:
            pp = pad_poly(pd)
            if rep == 0 and any(pp.distance(SPt(v)) < 1.2 for v in gvias):
                continue
            cx, cy = pp.centroid.x, pp.centroid.y
            best = None
            for d in (0.45, 0.7, 1.0, 1.4):
                ring = pp.buffer(d + vr, join_style=2).exterior
                L = ring.length
                for k in range(24):
                    q = ring.interpolate(L * k / 24)
                    if obs.distance(q) >= vr + cl:
                        from shapely.geometry import LineString as _LS
                        if _LS([(cx, cy), (q.x, q.y)]).buffer(0.125 + 0.152).intersects(obs):
                            continue
                        dist = q.distance(SPt(cx, cy))
                        if best is None or dist < best[0]:
                            best = (dist, q)
                if best:
                    break
            if not best:
                if rep == 0:
                    print("no via spot for", fp.GetReference(), pd.GetNumber())
                continue
            q = best[1]
            via = pcbnew.PCB_VIA(b)
            via.SetPosition(pcbnew.VECTOR2I(mm(q.x), mm(q.y)))
            via.SetWidth(mm(2 * vr))
            via.SetDrill(mm(0.25))
            via.SetNet(b.FindNet("GND"))
            b.Add(via)
            t = pcbnew.PCB_TRACK(b)
            near = pp.boundary.interpolate(pp.boundary.project(q))
            t.SetStart(pcbnew.VECTOR2I(mm(cx), mm(cy)))
            t.SetEnd(pcbnew.VECTOR2I(mm(q.x), mm(q.y)))
            t.SetWidth(mm(0.25))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(b.FindNet("GND"))
            b.Add(t)
            obs = unary_union([obs, SPt(q.x, q.y).buffer(vr)])
            gvias.append((q.x, q.y))
            added += 1
    print("GND fanout vias", added)
    return gvias


def import_ses(b, path):
    import re

    def sexp(txt):
        toks = re.findall(r'\(|\)|"[^"]*"|[^\s()]+', txt)
        st = [[]]
        for tk in toks:
            if tk == "(":
                st.append([])
            elif tk == ")":
                x = st.pop()
                st[-1].append(x)
            else:
                st[-1].append(tk.strip('"'))
        return st[0][0]

    def find(node, key):
        return [c for c in node if isinstance(c, list) and c and c[0] == key]

    ses = sexp(open(path).read())
    def _k(x, y):
        return (round(x, 2), round(y, 2))
    have_v = set()
    have_t = set()
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            have_v.add(_k(pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)))
        else:
            a_ = _k(pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y))
            b_ = _k(pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y))
            have_t.add((a_, b_, t.GetLayer()))
            have_t.add((b_, a_, t.GetLayer()))
    LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
    nt = nv = 0
    ro = find(ses, "routes")[0]
    for net_node in find(find(ro, "network_out")[0], "net"):
        name = net_node[1]
        net = b.FindNet(name)
        if net is None:
            print("unknown net", name)
            continue
        for w in find(net_node, "wire"):
            for pth in find(w, "path"):
                lay, wid = pth[1], int(pth[2]) / 10000.0
                c = [int(v) / 10000.0 for v in pth[3:]]
                pts = list(zip(c[0::2], c[1::2]))
                for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                    if (_k(x1, -y1), _k(x2, -y2), LAY[lay]) in have_t:
                        continue
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(-y1)))
                    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(-y2)))
                    t.SetWidth(mm(wid))
                    t.SetLayer(LAY[lay])
                    t.SetNet(net)
                    b.Add(t)
                    nt += 1
        for v in find(net_node, "via"):
            vx_, vy_ = int(v[2]) / 10000.0, -int(v[3]) / 10000.0
            if any(abs(vx_ - hx) < 0.03 and abs(vy_ - hy) < 0.03 for hx, hy in have_v):
                continue
            via = pcbnew.PCB_VIA(b)
            via.SetPosition(pcbnew.VECTOR2I(mm(int(v[2]) / 10000.0), mm(-int(v[3]) / 10000.0)))
            via.SetWidth(mm(0.6))
            via.SetDrill(mm(0.3))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(net)
            b.Add(via)
            nv += 1
    print("tracks", nt, "vias", nv)


full = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]

if sys.argv[1] == "reprep":
    # prep board + previous SES -> new DSN (Freerouting continues from the existing routes)
    b = pcbnew.LoadBoard(sys.argv[2])
    import_ses(b, sys.argv[3])
    b.Save(sys.argv[4].replace(".dsn", ".kicad_pcb"))
    pcbnew.ExportSpecctraDSN(b, sys.argv[4])
    d = open(sys.argv[4]).read()
    d = d.replace("(layer In1.Cu\n      (type signal)", "(layer In1.Cu\n      (type power)")
    open(sys.argv[4], "w").write(d)
elif sys.argv[1] == "prep":
    b = pcbnew.LoadBoard(sys.argv[2])
    for n, pts in ZONES_F.items():
        assert b.FindNet(n), n
        add_zone(b, n, pcbnew.F_Cu, pts, prio=2)
    add_zone(b, "GND", pcbnew.In1_Cu, full, prio=0)
    # thermal vias in the LM5176 exposed pad (GND)
    ep = [p for p in b.FindFootprintByReference("U101").Pads() if p.GetNumber() == "29"][0]
    ex, ey = pcbnew.ToMM(ep.GetPosition().x), pcbnew.ToMM(ep.GetPosition().y)
    for dx in (-0.7, 0.7):
        for dy in (-1.8, -0.6, 0.6, 1.8):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(mm(ex + dx), mm(ey + dy)))
            v.SetWidth(mm(0.5))
            v.SetDrill(mm(0.25))
            v.SetNet(b.FindNet("GND"))
            b.Add(v)
    gv = gnd_fanout(b)
    # keep other nets' tracks/vias out of the power pours (inset so the pour edge stays reachable)
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union as _uu
    holes = _uu([Point(x - OX, y - OY).buffer(0.8) for x, y in gv]) if gv else None
    for n, pts in ZONES_F.items():
        g = Polygon(pts).buffer(-0.6, join_style=2)
        if holes is not None:
            g = g.difference(holes)
        if g.is_empty:
            continue
        for poly in getattr(g, "geoms", [g]):
            if poly.area < 0.5:
                continue
            ext = list(poly.exterior.coords)[:-1]
            add_keepout(b, ext, [pcbnew.F_Cu], [list(h.coords)[:-1] for h in poly.interiors])
    # board-edge band on all copper layers
    e = 0.5
    for pts in ([(0, 0), (W, 0), (W, e), (0, e)], [(0, H - e), (W, H - e), (W, H), (0, H)],
                [(0, 0), (e, 0), (e, H), (0, H)], [(W - e, 0), (W, 0), (W, H), (W - e, H)]):
        add_keepout(b, pts, [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu])
    b.Save(sys.argv[3])
    pcbnew.ExportSpecctraDSN(b, sys.argv[4])
    d = open(sys.argv[4]).read()
    d = d.replace("(layer In1.Cu\n      (type signal)", "(layer In1.Cu\n      (type power)")
    open(sys.argv[4], "w").write(d)
else:
    b = pcbnew.LoadBoard(sys.argv[2])
    import_ses(b, sys.argv[3])
    for lay in (pcbnew.B_Cu, pcbnew.F_Cu, pcbnew.In2_Cu):
        z = add_zone(b, "GND", lay, full, prio=0)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    # remove routing-only keepouts (power pours / edge band); edge band is kept
    for z in list(b.Zones()):
        if z.GetIsRuleArea():
            bb = z.GetBoundingBox()
            if pcbnew.ToMM(bb.GetWidth()) > 1.0 and pcbnew.ToMM(bb.GetHeight()) > 1.0:
                b.Remove(z)
    filler.Fill(b.Zones())
    b.Save(sys.argv[4])
    pcbnew.WriteDRCReport(b, sys.argv[4].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
