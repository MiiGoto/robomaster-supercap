"""Route the connections Freerouting left open (from the DRC report) with a small grid A* on In2.Cu/B.Cu.

usage: python3 fixup.py routed.kicad_pcb routed_drc.rpt out.kicad_pcb
"""
import heapq
import re
import sys

import numpy as np
import pcbnew
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union

mm = pcbnew.FromMM
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
rpt = open(sys.argv[2]).read()
X0, Y0, X1, Y1 = 100.0, 100.0, 168.0, 157.0
RES = 0.1
TW, CL, VD = 0.2, 0.16, 0.5      # track width, clearance, via diameter
LAYERS = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]

pairs = []
for m in re.finditer(r"\[unconnected_items\].*?\n.*?\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): (.*?)\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): (.*?)\n", rpt):
    pairs.append(((float(m.group(1)), float(m.group(2)), m.group(3)), (float(m.group(4)), float(m.group(5)), m.group(6))))


def netname(desc):
    return re.search(r"\[([^\]]+)\]", desc).group(1)


def pad_shape(p):
    bb = p.GetBoundingBox()
    return box(T(bb.GetX()), T(bb.GetY()), T(bb.GetRight()), T(bb.GetBottom()))


def obstacles(net, layer):
    obs = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net:
                continue
            if p.IsOnLayer(layer) or p.GetDrillSize().x > 0:
                obs.append(pad_shape(p))
    for t in b.GetTracks():
        if t.GetNetname() == net:
            continue
        if t.GetClass() == "PCB_VIA":
            obs.append(Point(T(t.GetPosition().x), T(t.GetPosition().y)).buffer(T(t.GetWidth()) / 2))
        elif t.GetLayer() == layer:
            obs.append(LineString([(T(t.GetStart().x), T(t.GetStart().y)), (T(t.GetEnd().x), T(t.GetEnd().y))]).buffer(T(t.GetWidth()) / 2))
    from shapely.geometry import Polygon as _P
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() in (net, "GND") or not z.IsOnLayer(layer):
            continue
        fl = z.GetFilledPolysList(layer)
        for k in range(fl.OutlineCount()):
            o = fl.Outline(k)
            if o.PointCount() >= 3:
                obs.append(_P([(T(o.CPoint(q).x), T(o.CPoint(q).y)) for q in range(o.PointCount())]).buffer(0))
    for fp in b.GetFootprints():  # mounting holes
        for p in fp.Pads():
            if p.GetDrillSize().x > 0 and not p.GetNetname():
                obs.append(pad_shape(p).buffer(0.3))
    return unary_union(obs)


def grid_block(geom, infl):
    nx, ny = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
    g = np.zeros((ny, nx), dtype=bool)
    gg = geom.buffer(infl)
    xs = X0 + (np.arange(nx) + 0.5) * RES
    for poly in getattr(gg, "geoms", [gg]):
        x0, y0, x1, y1 = poly.bounds
        i0, i1 = max(0, int((y0 - Y0) / RES)), min(ny, int((y1 - Y0) / RES) + 1)
        j0, j1 = max(0, int((x0 - X0) / RES)), min(nx, int((x1 - X0) / RES) + 1)
        from shapely import contains_xy
        for i in range(i0, i1):
            y = Y0 + (i + 0.5) * RES
            g[i, j0:j1] |= contains_xy(poly, xs[j0:j1], np.full(j1 - j0, y))
    # board edge
    e = int(0.6 / RES)
    g[:e, :] = g[-e:, :] = True
    g[:, :e] = g[:, -e:] = True
    return g


ALLPADS = None


def via_ok(x, y, net):
    global ALLPADS
    pt = Point(x, y)
    if ALLPADS is None:
        ALLPADS = unary_union([pad_shape(p) for fp in b.GetFootprints() for p in fp.Pads()])
    if ALLPADS.distance(pt) < VD / 2 + 0.1:
        return False
    for lay in [pcbnew.F_Cu] + LAYERS:
        if obstacles(net, lay).distance(pt) < VD / 2 + CL:
            return False
    return X0 + 0.8 < x < X1 - 0.8 and Y0 + 0.8 < y < Y1 - 0.8


def near_via(x, y, net, layer_obj=None):
    """find a via spot near (x, y) reachable on F.Cu by a straight track."""
    obsF = obstacles(net, pcbnew.F_Cu)
    for r in np.arange(0.5, 3.0, 0.1):
        for k in range(16 if r else 1):
            a = 2 * np.pi * k / 16
            vx, vy = x + r * np.cos(a), y + r * np.sin(a)
            if not via_ok(vx, vy, net):
                continue
            if r and LineString([(x, y), (vx, vy)]).buffer(TW / 2 + CL).intersects(obsF):
                continue
            return vx, vy
    return None


def astar(net, starts, goals):
    """starts/goals: lists of (layer_index, x, y). 3-layer grid router with vias."""
    blocks = [grid_block(obstacles(net, lay), TW / 2 + CL) for lay in LAYERS]
    vblock = grid_block(unary_union([obstacles(net, lay) for lay in LAYERS] + [ALLPADS_()]), VD / 2 + CL)
    ny, nx = blocks[0].shape
    def cell(x, y):
        return int((y - Y0) / RES), int((x - X0) / RES)
    gset = set()
    for L, x, y in goals:
        i, j = cell(x, y)
        gset.add((L, i, j))
        blocks[L][max(0, i - 1):i + 2, max(0, j - 1):j + 2] = False
    gi = [g[1] for g in gset]
    gj = [g[2] for g in gset]
    tgi, tgj = sum(gi) / len(gi), sum(gj) / len(gj)
    dist, prev, pq = {}, {}, []
    for L, x, y in starts:
        i, j = cell(x, y)
        blocks[L][max(0, i - 1):i + 2, max(0, j - 1):j + 2] = False
        dist[(L, i, j)] = 0
        heapq.heappush(pq, (0, 0, (L, i, j)))
    moves = [(0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    found = None
    while pq:
        _f, d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e18):
            continue
        if u in gset:
            found = u
            break
        L, i, j = u
        cand = [((L, i + di, j + dj), c + (0.2 if prev.get(u, (0,) * 5)[3:] != (di, dj) else 0)) for di, dj, c in moves]
        if not vblock[i, j]:
            cand += [((L2, i, j), 25.0) for L2 in range(len(LAYERS)) if L2 != L]
        for v, c in cand:
            if not (0 <= v[1] < ny and 0 <= v[2] < nx) or blocks[v[0]][v[1], v[2]]:
                continue
            nd = d + c + (0.5 if v[0] == 0 else 0)  # prefer inner/bottom layers
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = (u[0], u[1], u[2], v[1] - u[1], v[2] - u[2])
                heapq.heappush(pq, (nd + max(abs(v[1] - tgi), abs(v[2] - tgj)), nd, v))
    if not found:
        return None
    path = [found]
    while path[-1] in prev:
        p = prev[path[-1]]
        path.append((p[0], p[1], p[2]))
    path.reverse()
    return path


def ALLPADS_():
    global ALLPADS
    if ALLPADS is None:
        ALLPADS = unary_union([pad_shape(p) for fp in b.GetFootprints() for p in fp.Pads()])
    return ALLPADS


def add_track(x1, y1, x2, y2, layer, net):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    t.SetWidth(mm(TW))
    t.SetLayer(layer)
    t.SetNet(b.FindNet(net))
    b.Add(t)


def add_via(x, y, net):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(VD))
    v.SetDrill(mm(0.25))
    v.SetNet(b.FindNet(net))
    b.Add(v)


def endpoint(item, other):
    x, y, desc = item
    net = netname(desc)
    if desc.startswith("Zone"):
        for z in b.Zones():
            if z.GetNetname() == net and not z.GetIsRuleArea() and z.IsOnLayer(pcbnew.F_Cu):
                fp_ = z.GetFilledPolysList(pcbnew.F_Cu)
                best = None
                for k in range(fp_.OutlineCount()):
                    o = fp_.Outline(k)
                    from shapely.geometry import Polygon
                    pg = Polygon([(T(o.CPoint(q).x), T(o.CPoint(q).y)) for q in range(o.PointCount())]).buffer(-0.5)
                    if pg.is_empty:
                        continue
                    from shapely.ops import nearest_points
                    p = nearest_points(pg, Point(other[0], other[1]))[0]
                    dd = p.distance(Point(other[0], other[1]))
                    if best is None or dd < best[0]:
                        best = (dd, p.x, p.y)
                if best:
                    return best[1], best[2], net, True
    m = re.search(r"Pad (\S+) \[.*\] of (\S+)", desc)
    if m:
        fp = b.FindFootprintByReference(m.group(2))
        p = [q for q in fp.Pads() if q.GetNumber() == m.group(1)][0]
        return T(p.GetPosition().x), T(p.GetPosition().y), net, False
    return x, y, net, False


done = 0
for A, B in pairs:
    net = netname(A[2])
    if "Zone [GND]" in A[2] and "Zone [GND]" in B[2]:
        continue
    ax, ay, _, az = endpoint(A, B)
    bx, by, _, bz = endpoint(B, (ax, ay))
    path = astar(net, [(0, ax, ay)], [(0, bx, by)])
    if not path:
        print("no path for", net)
        continue
    pts = [(X0 + (j + 0.5) * RES, Y0 + (i + 0.5) * RES, L) for (L, i, j) in path]
    pts[0] = (ax, ay, pts[0][2])
    pts[-1] = (bx, by, pts[-1][2])
    seg = pts[0]
    for k in range(1, len(pts)):
        if pts[k][2] != pts[k - 1][2]:          # via
            if (seg[0], seg[1]) != (pts[k - 1][0], pts[k - 1][1]):
                add_track(seg[0], seg[1], pts[k - 1][0], pts[k - 1][1], LAYERS[pts[k - 1][2]], net)
            add_via(pts[k][0], pts[k][1], net)
            seg = pts[k]
            continue
        last = k == len(pts) - 1
        if not last and pts[k + 1][2] == pts[k][2]:
            d1 = (round((pts[k][0] - pts[k - 1][0]) / RES), round((pts[k][1] - pts[k - 1][1]) / RES))
            d2 = (round((pts[k + 1][0] - pts[k][0]) / RES), round((pts[k + 1][1] - pts[k][1]) / RES))
            if d1 == d2:
                continue
        add_track(seg[0], seg[1], pts[k][0], pts[k][1], LAYERS[pts[k][2]], net)
        seg = pts[k]
    done += 1
    print("routed", net, len(path))
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(sys.argv[3])
pcbnew.WriteDRCReport(b, sys.argv[3].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
print("fixed", done)
