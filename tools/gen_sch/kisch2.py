"""KiCad 7-format schematic writer, wire-based ("hand drawn" style).

Parts are placed with rotation, connected by explicit wires, ground/3V3 by
power symbols, long-distance nets by labels. Each part also carries the
*intended* pin->net map, and check() compares the netlist KiCad itself
extracts from the drawing against that intent (partition comparison).
"""
import math
import os
import re
import subprocess
import sys

from kisch import LibSym, Sym, uid, f  # noqa: F401

G = 1.27
LCSC_MAP = {}  # (symbol nick, value) -> LCSC code (0603 / other packages), filled by parts.py
LCSC_MAP_0402 = {}
FORCE_0603 = set()


def snap(v):
    return round(round(v / G) * G, 4)


def P(x, y):
    return (snap(x), snap(y))


class Part:
    def __init__(self, sheet, sym, ref, x, y, rot, unit, nets, mirror=None):
        self.sheet, self.sym, self.ref, self.x, self.y, self.rot, self.unit = sheet, sym, ref, x, y, rot, unit
        self.mirror = mirror
        self.nets = nets
        geom = sym.geom
        if getattr(sym, "units", None):
            geom = {n: g[:3] for n, g in sym.units[unit].items()}
        self.geom = geom

    def p(self, num):
        px, py, _ = self.geom[str(num)]
        if self.mirror == "y":
            px = -px
        elif self.mirror == "x":
            py = -py
        r = math.radians(self.rot)
        X = px * math.cos(r) - py * math.sin(r)
        Y = px * math.sin(r) + py * math.cos(r)
        return P(self.x + X, self.y - Y)

    def out(self, num):
        """outward direction of the pin as 'R','L','U','D' (screen)."""
        a0 = self.geom[str(num)][2]
        if self.mirror == "y":
            a0 = (180 - a0) % 360
        elif self.mirror == "x":
            a0 = (-a0) % 360
        ang = (a0 + 180 + self.rot) % 360
        return {0: "R", 90: "U", 180: "L", 270: "D"}[int(round(ang)) % 360]

    def __getitem__(self, num):
        return self.p(num)


class Sheet2:
    def __init__(self, title, paper="A3", proj="control_board", path="/", ref_base=0, global_nets=()):
        self.title, self.paper, self.proj, self.path, self.ref_base = title, paper, proj, path, ref_base
        self.global_nets = set(global_nets)
        self.root = uid()
        self.syms, self.items, self.refcount, self.bom = {}, [], {}, []
        self.parts = []
        self.segs = []
        self.conn_pts = []  # pin ends + power pins + labels (points that are connection endpoints)
        self.pwr_n = 0

    # ---------------- placement
    def add(self, sym, x, y, value, nets=None, rot=0, ref=None, props=None, unit=1, named=None,
            text=None, bom=True, mirror=None, tpos=None):
        x, y = snap(x), snap(y)
        nets = dict(nets or {})
        part = Part(self, sym, None, x, y, rot, unit, nets, mirror)
        if named:
            for num, nm in getattr(sym, "names", {}).items():
                if num in part.geom and nm in named and num not in nets:
                    nets[num] = named[nm]
        if ref is None:
            n = self.refcount.get(sym.ref_prefix, self.ref_base) + 1
            self.refcount[sym.ref_prefix] = n
            ref = f"{sym.ref_prefix}{n}"
        part.ref = ref
        self.syms[sym.lib] = sym
        props = dict(props or {})
        dnp = "yes" if props.pop("DNP", False) else "no"
        fpn = props.get("Footprint", "")
        if "_0402_" in fpn and ((sym.nick, value) in FORCE_0603 or (sym.nick, value) not in LCSC_MAP_0402):
            props["Footprint"] = fpn.replace("R_0402_1005Metric", "R_0603_1608Metric").replace("C_0402_1005Metric", "C_0603_1608Metric")
            fpn = props["Footprint"]
        if "LCSC" not in props:
            m = LCSC_MAP_0402 if "_0402_" in fpn else LCSC_MAP
            if (sym.nick, value) in m:
                props["LCSC"] = m[(sym.nick, value)]
        # text placement
        xs = [part.p(n)[0] for n in part.geom] + [x]
        ys = [part.p(n)[1] for n in part.geom] + [y]
        npins = len(part.geom)
        if text is None:
            if npins <= 2:
                vertical = abs(xs[0] - xs[1]) < 0.01 if npins == 2 else True
                text = "right" if vertical else "above"
            elif npins <= 6 and not isinstance(sym, Sym):
                text = "right"
            else:
                text = "box"
        if text == "right":
            tx = max(xs) + 1.27 if npins > 2 else x + 2.54
            rpos, vpos, just = (tx, y - 1.27), (tx, y + 1.27), "left"
        elif text == "left":
            tx = min(xs) - 1.27 if npins > 2 else x - 2.54
            rpos, vpos, just = (tx, y - 1.27), (tx, y + 1.27), "right"
        elif text == "above":
            if npins > 2:
                rpos, vpos, just = (x, min(ys) - 6.35), (x, min(ys) - 3.81), None
            else:
                rpos, vpos, just = (x, y - 3.3), (x, y + 3.3), None
        else:  # box: ref above, value below the pin extents
            top = min(ys) if not isinstance(sym, Sym) else y - sym.h / 2
            bot = max(ys) if not isinstance(sym, Sym) else y + sym.h / 2
            if getattr(sym, "units", None) and not isinstance(sym, Sym):
                top, bot = y - sym.h / 2, y + sym.h / 2
            rpos, vpos, just = (x, top - 1.6), (x, bot + 1.6), None
        if tpos:
            rpos, vpos, just = tpos[0], tpos[1], "left"
        eff = '(effects (font (size 1.27 1.27)) (justify %s))' % just if just else "(effects (font (size 1.27 1.27)))"
        tang = 90 if rot in (90, 270) else 0
        inbom = "yes" if bom else "no"
        o = [f'(symbol (lib_id "{sym.lib}") (at {f(x)} {f(y)} {rot}){' (mirror %s)' % mirror if mirror else ''} (unit {unit}) (in_bom {inbom}) (on_board {inbom}) (dnp {dnp})',
             f'(uuid {uid()})',
             f'(property "Reference" "{ref}" (at {f(rpos[0])} {f(rpos[1])} {tang}) {eff})',
             f'(property "Value" "{value}" (at {f(vpos[0])} {f(vpos[1])} {tang}) {eff})',
             f'(property "Footprint" "{props.get("Footprint", "")}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))']
        for k, v in props.items():
            if k != "Footprint":
                o.append(f'(property "{k}" "{v}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        for num in part.geom:
            o.append(f'(pin "{num}" (uuid {uid()}))')
        o.append(f'(instances (project "{self.proj}" (path "{self.path}" (reference "{ref}") (unit {unit}))))')
        o.append(")")
        self.items.append("\n".join(o))
        for num in part.geom:
            self.conn_pts.append(part.p(num))
        if bom and unit == 1:
            self.bom.append((ref, value, props.get("LCSC", "") if dnp == "no" else "", props.get("Footprint", ""), sym.lib))
        if bom:
            self.parts.append(part)
        return part

    def power(self, psym, pt, rot=0):
        self.pwr_n += 1
        ref = f"#PWR{self.ref_base + self.pwr_n:03d}"
        val = psym.nick if psym.nick not in ("PWRFLAG",) else "PWR_FLAG"
        if psym.nick == "PWRFLAG":
            ref = f"#FLG{self.ref_base + self.pwr_n:03d}"
        x, y = P(*pt)
        self.syms[psym.lib] = psym
        vy = y + 5.08 if psym.nick == "GND" else y - 5.08
        if psym.nick == "PWRFLAG":
            vy = y - 5.08
        self.items.append("\n".join([
            f'(symbol (lib_id "{psym.lib}") (at {f(x)} {f(y)} {rot}) (unit 1) (in_bom no) (on_board no) (dnp no)',
            f'(uuid {uid()})',
            f'(property "Reference" "{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))',
            f'(property "Value" "{psym.value}" (at {f(x)} {f(vy)} 0) (effects (font (size 1.27 1.27))))',
            '(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
            f'(pin "1" (uuid {uid()}))',
            f'(instances (project "{self.proj}" (path "{self.path}" (reference "{ref}") (unit 1))))',
            ")"]))
        self.conn_pts.append(P(x, y))

    # ---------------- wiring
    def wire(self, *pts):
        pts = [P(*p) for p in pts]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            assert a[0] == b[0] or a[1] == b[1], ("non-orthogonal wire", a, b)
            self.segs.append((a, b))

    def hv(self, a, b):
        """L-shaped wire: horizontal first, then vertical."""
        self.wire(a, (b[0], a[1]), b)

    def vh(self, a, b):
        self.wire(a, (a[0], b[1]), b)

    def label(self, net, pt, d="R", glob=None):
        x, y = P(*pt)
        ang, just = {"R": (0, "left"), "L": (180, "right"), "U": (90, "left"), "D": (270, "right")}[d]
        eff = f'(effects (font (size 1.27 1.27)) (justify {just}))'
        if glob or (glob is None and net in self.global_nets):
            self.items.append(f'(global_label "{net}" (shape bidirectional) (at {f(x)} {f(y)} {ang}) (fields_autoplaced) {eff} (uuid {uid()}))')
        else:
            self.items.append(f'(label "{net}" (at {f(x)} {f(y)} {ang}) {eff} (uuid {uid()}))')
        self.conn_pts.append((x, y))

    def stub_label(self, part, num, net=None, length=2.54, glob=None):
        """short wire out of a pin plus a label at its end."""
        net = net or part.nets[str(num)]
        a = part.p(num)
        d = part.out(num)
        dx, dy = {"R": (length, 0), "L": (-length, 0), "U": (0, -length), "D": (0, length)}[d]
        b = P(a[0] + dx, a[1] + dy)
        if length:
            self.wire(a, b)
        self.label(net, b, d, glob)
        return b

    def nc_unused(self, part):
        for num in part.geom:
            if part.nets.get(num) is None:
                self.nc(part.p(num))

    def nc(self, pt):
        x, y = P(*pt)
        self.items.append(f'(no_connect (at {f(x)} {f(y)}) (uuid {uid()}))')

    def text(self, x, y, s, size=1.27, bold=False):
        s = s.replace('"', "'").replace("\n", "\\n")
        b = " bold" if bold else ""
        self.items.append(f'(text "{s}" (at {f(x)} {f(y)} 0) (effects (font (size {size} {size}){b}) (justify left top)) (uuid {uid()}))')

    def frame(self, x, y, w, h, title):
        self.items.append(
            f'(rectangle (start {f(x)} {f(y)}) (end {f(x + w)} {f(y + h)}) '
            f'(stroke (width 0.15) (type dash) (color 120 120 120 1)) (fill (type none)) (uuid {uid()}))')
        self.text(x + 1.5, y + 1.5, title, 1.8, bold=True)

    # ---------------- output
    def _junctions(self):
        pts = set()
        for a, b in self.segs:
            pts.add(a)
            pts.add(b)
        pts |= set(self.conn_pts)
        out = []
        for p in pts:
            n = 0
            for a, b in self.segs:
                if p == a or p == b:
                    n += 1
                elif a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1]):
                    n += 2
                elif a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]):
                    n += 2
            if p in self.conn_pts:
                n += self.conn_pts.count(p)
            if n >= 3:
                out.append(p)
        return out

    def write(self, path):
        o = ['(kicad_sch (version 20230121) (generator "claude-kisch2")', f'(uuid {self.root})',
             f'(paper "{self.paper}")', f'(title_block (title "{self.title}") (rev "B-prov") (company "NAGOYA SHACHIHOKO"))',
             "(lib_symbols"]
        o += [s.lib_def() for s in self.syms.values()]
        o.append(")")
        pts = set(self.conn_pts)
        for a, b in self.segs:
            pts.add(a)
            pts.add(b)
        for a, b in self.segs:
            inner = [p for p in pts if p != a and p != b and (
                (a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1])) or
                (a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0])))]
            chain = [a] + sorted(inner, key=lambda p: abs(p[0] - a[0]) + abs(p[1] - a[1])) + [b]
            for u, v in zip(chain, chain[1:]):
                o.append(f'(wire (pts (xy {f(u[0])} {f(u[1])}) (xy {f(v[0])} {f(v[1])})) '
                         f'(stroke (width 0) (type default)) (uuid {uid()}))')
        for p in self._junctions():
            o.append(f'(junction (at {f(p[0])} {f(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
        o += self.items
        o.append('(sheet_instances (path "/" (page "1")))')
        o.append(")")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(o) + "\n")
        with open(path.replace(".kicad_sch", "_bom.csv"), "w", encoding="utf-8") as fh:
            fh.write("Ref,Value,LCSC,Footprint,Symbol\n")
            for row in self.bom:
                fh.write(",".join('"%s"' % x for x in row) + "\n")


class PowerSym(LibSym):
    def __init__(self, name, value=None):
        nick = {"PWR_FLAG": "PWRFLAG"}.get(name, name)
        super().__init__(nick, "power.kicad_sym", name, "#PWR")
        self.value = value or name


# ---------------- netlist check
def parse_netlist(path):
    t = open(path, encoding="utf-8").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', t, re.S):
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))
        nets[m.group(1)] = {(r, p) for r, p in nodes if not r.startswith("#")}
    return nets


def check(root_sch, sheets, alias=None):
    """Compare KiCad's extracted connectivity to the intended nets of all parts."""
    alias = alias or {}
    out = "/tmp/_chk.net"
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "--output", out, root_sch],
                   check=True, capture_output=True)
    got = parse_netlist(out)
    intent = {}
    for sh in sheets:
        for part in sh.parts:
            for num in part.geom:
                net = part.nets.get(num)
                if net is None:
                    net = f"__NC__{part.ref}.{num}"
                net = alias.get(net, net)
                intent.setdefault(net, set()).add((part.ref, num))
    got_by_pin = {}
    for n, pins in got.items():
        for pin in pins:
            got_by_pin[pin] = n
    errs = []
    for net, pins in intent.items():
        names = {got_by_pin.get(p) for p in pins}
        if len(names) != 1 or None in names:
            errs.append(f"SPLIT {net}: " + ", ".join(f"{r}.{p}->{got_by_pin.get((r, p))}" for r, p in sorted(pins)))
            continue
        gname = names.pop()
        extra = got[gname] - pins
        if extra and not net.startswith("__NC__"):
            errs.append(f"MERGED {net} with {sorted(extra)} (kicad net {gname})")
        if net.startswith("__NC__") and len(got[gname]) > 1:
            errs.append(f"NC pin {pins} connected to {sorted(got[gname])}")
    return errs, got


class Box(Sym):
    """IC box symbol with explicit rows. left/right: lists of (num, name, etype) or None (empty row)."""

    def __init__(self, lib, ref_prefix, left, right, width=25.4):
        self.lib = lib
        self.nick = lib.split(":")[1]
        self.ref_prefix = ref_prefix
        self.pins = []
        n = max(len(left), len(right))
        self.w = width
        self.h = 2.54 * n + 2.54
        self.side_text = False
        self.hh = self.h / 2 + 1.5
        self.geom = {}
        for side, grp in (("L", left), ("R", right)):
            for i, p in enumerate(grp):
                if p is None:
                    continue
                num, name, et = p
                y = round(1.27 * (n - 1 - 2 * i), 4)
                x = -(self.w / 2 + 2.54) if side == "L" else (self.w / 2 + 2.54)
                self.geom[num] = (x, y, 0 if side == "L" else 180)
                self.pins.append((num, name, side, et))
        self.names = {p[0]: p[1] for p in self.pins}


def debug_groups(sheet):
    """Local (geometric) connectivity groups; report groups mixing intended nets."""
    pts = set(sheet.conn_pts)
    for a, b in sheet.segs:
        pts |= {a, b}
    parent = {p: p for p in pts}

    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def uni(a, b):
        parent[find(a)] = find(b)
    for a, b in sheet.segs:
        on = [p for p in pts if (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) or
              (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))]
        for p in on:
            uni(a, p)
    groups = {}
    for part in sheet.parts:
        for num in part.geom:
            groups.setdefault(find(part.p(num)), set()).add((part.ref, num, part.nets.get(num)))
    for g, mem in groups.items():
        nets = {m[2] for m in mem}
        if len(nets) > 1:
            print("MIX at", g, sorted(mem, key=str))
