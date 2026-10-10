"""Minimal KiCad 7 schematic writer (labels-only connectivity).

Self-contained: every symbol is embedded in lib_symbols. Standard-shaped
symbols are copied from the KiCad standard libraries (Device, Connector...)
under the library nickname "rev", so no external library is required.
"""
import re
import uuid

FONT = "(effects (font (size 1.27 1.27)))"
SYMDIR = "/usr/share/kicad/symbols"


def uid():
    return str(uuid.uuid4())


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _block(t, name):
    i = t.find(f'\n  (symbol "{name}"') + 1
    assert i > 0, name
    d, j = 0, i
    while True:
        ch = t[j]
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
            if d == 0:
                break
        j += 1
    return t[i:j + 1]


class LibSym:
    """Symbol copied from a KiCad standard library file (follows 'extends')."""

    def __init__(self, nick_name, lib_file, lib_name, ref_prefix):
        self.lib = f"rev:{nick_name}"
        self.nick = nick_name
        self.ref_prefix = ref_prefix
        t = open(f"{SYMDIR}/{lib_file}", encoding="utf-8").read()
        block = _block(t, lib_name)
        m = re.search(r'\(extends "([^"]+)"\)', block)
        parent = lib_name
        if m:
            parent = m.group(1)
            block = _block(t, parent)
        self.body = block.replace(f'(symbol "{parent}"', f'(symbol "{nick_name}"', 1)
        self.body = re.sub(rf'\(symbol "{re.escape(parent)}_(\d+)_(\d+)"', rf'(symbol "{nick_name}_\1_\2"', self.body)
        # pins per unit
        self.units = {}
        for um in re.finditer(rf'\(symbol "{re.escape(nick_name)}_(\d+)_(\d+)"', self.body):
            u = int(um.group(1))
            i = um.start()
            d, j = 0, i
            while True:
                ch = self.body[j]
                if ch == "(":
                    d += 1
                elif ch == ")":
                    d -= 1
                    if d == 0:
                        break
                j += 1
            sub = self.body[i:j + 1]
            for pm in re.finditer(r'\(pin (\w+) \w+\s+\(at ([-\d.]+) ([-\d.]+) (\d+)\) \(length ([\d.]+)\)'
                                  r'(?:\s*hide)?\s+\(name "([^"]*)".*?\(number "([^"]*)"', sub, re.S):
                if u == 0:
                    continue
                self.units.setdefault(u, {})[pm.group(7)] = (float(pm.group(2)), float(pm.group(3)), int(pm.group(4)), pm.group(6), pm.group(1))
        # pins in unit 0 (shared graphics) are not expected; unit 1 default
        self.geom = {n: g[:3] for n, g in self.units.get(1, {}).items()}
        self.names = {n: g[3] for n, g in self.units.get(1, {}).items()}
        allg = [g for u in self.units.values() for g in u.values()]
        ys = [abs(g[1]) for g in allg] or [2.54]
        self.h = 2 * max(ys) + 2.54
        angs = [g[2] for g in self.units.get(1, {}).values()]
        xs = {g[0] for g in self.units.get(1, {}).values()}
        self.side_text = len(angs) == 2 and all(a in (90, 270) for a in angs) and len(xs) == 1
        vert = any(a in (90, 270) for a in angs)
        self.hh = (max(ys) + 3.81 + 2.5) if vert else (self.h / 2 + 2.5)
        if len(self.units) > 1 or len(allg) > 12:
            self.hh = self.h / 2 + 1.5

    def lib_def(self):
        return self.body.replace(f'(symbol "{self.nick}"', f'(symbol "{self.lib}"', 1)

    def file_def(self):
        return self.body


class Sym:
    """Box symbol (ICs). pins: list of (number, name, side 'L'|'R', etype)."""

    def __init__(self, lib, ref_prefix, pins, width=20.32):
        self.lib = lib
        self.nick = lib.split(":")[1]
        self.ref_prefix = ref_prefix
        self.pins = pins
        left = [p for p in pins if p[2] == "L"]
        right = [p for p in pins if p[2] == "R"]
        n = max(len(left), len(right))
        self.w = width
        self.h = 2.54 * n + 2.54
        self.side_text = False
        self.hh = self.h / 2 + 1.5
        self.geom = {}
        for side, grp in (("L", left), ("R", right)):
            for i, p in enumerate(grp):
                y = round(1.27 * (n - 1 - 2 * i), 4)
                x = -(self.w / 2 + 2.54) if side == "L" else (self.w / 2 + 2.54)
                self.geom[p[0]] = (x, y, 0 if side == "L" else 180)

    def lib_def(self):
        w, h, nk = self.w, self.h, self.nick
        o = [f'(symbol "{self.lib}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)']
        o.append(f'(property "Reference" "{self.ref_prefix}" (at 0 {f(h/2+1.5)} 0) {FONT})')
        o.append(f'(property "Value" "" (at 0 {f(-h/2-1.5)} 0) {FONT})')
        o.append('(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        o.append(f'(symbol "{nk}_0_1" (rectangle (start {f(-w/2)} {f(h/2)}) (end {f(w/2)} {f(-h/2)}) '
                 f'(stroke (width 0.254) (type default)) (fill (type background))))')
        o.append(f'(symbol "{nk}_1_1"')
        for num, name, side, et in self.pins:
            x, y, ang = self.geom[num]
            o.append(f'(pin {et} line (at {f(x)} {f(y)} {ang}) (length 2.54) '
                     f'(name "{name}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
        o.append(")")
        o.append(")")
        return "\n".join(o)

    def file_def(self):
        return self.lib_def().replace(f'(symbol "{self.lib}"', f'(symbol "{self.nick}"', 1)


class Sheet:
    def __init__(self, title, paper="A2", proj="control_board", path="/", ref_base=0, global_nets=()):
        self.title = title
        self.paper = paper
        self.root = uid()
        self.proj = proj
        self.path = path
        self.ref_base = ref_base
        self.global_nets = set(global_nets)
        self.syms = {}
        self.items = []
        self.refcount = {}
        self.bom = []

    def _label(self, net, lx, ly, ang, just):
        eff = f'(effects (font (size 1.27 1.27)) (justify {just}))'
        if net in self.global_nets:
            self.items.append(f'(global_label "{net}" (shape bidirectional) (at {f(lx)} {f(ly)} {ang}) {eff} (uuid {uid()}))')
        else:
            self.items.append(f'(label "{net}" (at {f(lx)} {f(ly)} {ang}) {eff} (uuid {uid()}))')

    def place(self, sym, x, y, value, nets, ref=None, props=None, unit=1, named=None):
        """nets: dict pin_number -> net. named: dict pin_name -> net (all pins with that name)."""
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        geom = sym.geom
        if hasattr(sym, "units") and sym.units:
            geom = {n: g[:3] for n, g in sym.units[unit].items()}
        nets = dict(nets)
        if named:
            for num, nm in getattr(sym, "names", {}).items():
                if num in geom and nm in named and num not in nets:
                    nets[num] = named[nm]
        if ref is None:
            n = self.refcount.get(sym.ref_prefix, self.ref_base) + 1
            self.refcount[sym.ref_prefix] = n
            ref = f"{sym.ref_prefix}{n}"
        self.syms[sym.lib] = sym
        props = props or {}
        if sym.side_text:
            rpos, vpos = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27)
            eff = '(effects (font (size 1.27 1.27)) (justify left))'
        else:
            rpos, vpos = (x, y - sym.hh), (x, y + sym.hh)
            eff = FONT
        o = [f'(symbol (lib_id "{sym.lib}") (at {f(x)} {f(y)} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no)',
             f'(uuid {uid()})',
             f'(property "Reference" "{ref}" (at {f(rpos[0])} {f(rpos[1])} 0) {eff})',
             f'(property "Value" "{value}" (at {f(vpos[0])} {f(vpos[1])} 0) {eff})',
             f'(property "Footprint" "{props.get("Footprint","")}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))']
        for k, v in props.items():
            if k != "Footprint":
                o.append(f'(property "{k}" "{v}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        for num in geom:
            o.append(f'(pin "{num}" (uuid {uid()}))')
        o.append(f'(instances (project "{self.proj}" (path "{self.path}" (reference "{ref}") (unit {unit}))))')
        o.append(")")
        self.items.append("\n".join(o))
        for num, (px, py, pang) in geom.items():
            ax, ay = x + px, y - py
            net = nets.get(num)
            if net is None:
                self.items.append(f'(no_connect (at {f(ax)} {f(ay)}) (uuid {uid()}))')
                continue
            if pang in (0, 180):
                ang, just = (180, "right") if pang == 0 else (0, "left")
                lx, ly = ax, ay
            else:
                dy = -3.81 if pang == 270 else 3.81
                lx, ly = ax, ay + dy
                self.items.append(f'(wire (pts (xy {f(ax)} {f(ay)}) (xy {f(lx)} {f(ly)})) '
                                  f'(stroke (width 0) (type default)) (uuid {uid()}))')
                ang, just = 0, "left"
            self._label(net, lx, ly, ang, just)
        if unit == 1:
            self.bom.append((ref, value, props.get("LCSC", ""), props.get("Footprint", ""), sym.lib))
        return ref

    def text(self, x, y, s, size=1.8):
        s = s.replace('"', "'").replace("\n", "\\n")
        self.items.append(f'(text "{s}" (at {f(x)} {f(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')

    def frame(self, x, y, w, h, title, note=""):
        self.items.append(
            f'(rectangle (start {f(x)} {f(y)}) (end {f(x + w)} {f(y + h)}) '
            f'(stroke (width 0.3) (type dash)) (fill (type none)) (uuid {uid()}))')
        self.text(x + 3, y + 3, title, 2.5)
        if note:
            self.text(x + 3, y + 9, note, 1.5)

    def write_lib(self, path):
        o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch")']
        for sym in self.syms.values():
            o.append(sym.file_def())
        o.append(")")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(o) + "\n")

    def write(self, path):
        o = ['(kicad_sch (version 20230121) (generator "claude-kisch")',
             f'(uuid {self.root})',
             f'(paper "{self.paper}")',
             f'(title_block (title "{self.title}"))',
             "(lib_symbols"]
        o += [s.lib_def() for s in self.syms.values()]
        o.append(")")
        o += self.items
        o.append('(sheet_instances (path "/" (page "1")))')
        o.append(")")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(o) + "\n")


def write_root(path, proj, subs, root):
    """subs: list of (name, filename, sheet_uuid)."""
    o = ['(kicad_sch (version 20230121) (generator "claude-kisch")', f'(uuid {root})', '(paper "A4")',
         '(title_block (title "Rev B control board (root)"))', '(lib_symbols)']
    for i, (name, fn, su) in enumerate(subs):
        x, y = 30.48, 30.48 + i * 30.48
        o.append(f'(sheet (at {f(x)} {f(y)}) (size 40.64 15.24) (fields_autoplaced) '
                 f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0)) (uuid {su})')
        o.append(f'(property "Sheetname" "{name}" (at {f(x)} {f(y - 0.7)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))')
        o.append(f'(property "Sheetfile" "{fn}" (at {f(x)} {f(y + 16)} 0) (effects (font (size 1.27 1.27)) (justify left top)))')
        o.append(f'(instances (project "{proj}" (path "/{root}" (page "{i + 2}"))))')
        o.append(")")
    o.append('(sheet_instances (path "/" (page "1")))')
    o.append(")")
    open(path, "w", encoding="utf-8").write("\n".join(o) + "\n")
    return root
