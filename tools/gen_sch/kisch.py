"""Minimal KiCad 7 schematic writer (labels-only connectivity).

Self-contained: every symbol is embedded in lib_symbols, so no external
symbol library is needed. Pins connect through net labels placed exactly
on the pin end points.
"""
import uuid

FONT = "(effects (font (size 1.27 1.27)))"


def uid():
    return str(uuid.uuid4())


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


class Sym:
    """Box symbol. pins: list of (number, name, side 'L'|'R', etype)."""

    def __init__(self, lib, ref_prefix, pins, width=20.32, small=False):
        self.lib = lib
        self.ref_prefix = ref_prefix
        self.pins = pins
        self.small = small
        left = [p for p in pins if p[2] == "L"]
        right = [p for p in pins if p[2] == "R"]
        n = max(len(left), len(right))
        self.w = 5.08 if small else width
        self.h = 2.54 * n + 2.54
        self.pos = {}
        for side, grp in (("L", left), ("R", right)):
            for i, p in enumerate(grp):
                y = round(1.27 * (n - 1 - 2 * i), 4)
                x = -(self.w / 2 + 2.54) if side == "L" else (self.w / 2 + 2.54)
                self.pos[p[0]] = (x, y, side)

    def lib_def(self):
        w, h = self.w, self.h
        o = [f'(symbol "{self.lib}" (pin_names (offset 1.016)' + (" hide" if self.small else "") + ")"
             + (" (pin_numbers hide)" if self.small else "")
             + " (in_bom yes) (on_board yes)"]
        o.append(f'(property "Reference" "{self.ref_prefix}" (at 0 {f(h/2+1.5)} 0) {FONT})')
        o.append(f'(property "Value" "" (at 0 {f(-h/2-1.5)} 0) {FONT})')
        o.append(f'(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        o.append(f'(symbol "{self.lib.split(":")[1]}_0_1" (rectangle (start {f(-w/2)} {f(h/2)}) (end {f(w/2)} {f(-h/2)}) '
                 f'(stroke (width 0.254) (type default)) (fill (type background))))')
        o.append(f'(symbol "{self.lib.split(":")[1]}_1_1"')
        for num, name, side, et in self.pins:
            x, y, s = self.pos[num]
            ang = 0 if s == "L" else 180
            o.append(f'(pin {et} line (at {f(x)} {f(y)} {ang}) (length 2.54) '
                     f'(name "{name}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
        o.append(")")
        o.append(")")
        return "\n".join(o)


class Sheet:
    def __init__(self, title, paper="A2"):
        self.title = title
        self.paper = paper
        self.root = uid()
        self.syms = {}
        self.items = []
        self.refcount = {}
        self.bom = []

    def add_lib(self, sym):
        self.syms[sym.lib] = sym

    def place(self, sym, x, y, value, nets, ref=None, props=None):
        """nets: dict pin_number -> net name."""
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        if ref is None:
            n = self.refcount.get(sym.ref_prefix, 0) + 1
            self.refcount[sym.ref_prefix] = n
            ref = f"{sym.ref_prefix}{n}"
        self.add_lib(sym)
        props = props or {}
        o = [f'(symbol (lib_id "{sym.lib}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)',
             f'(uuid {uid()})',
             f'(property "Reference" "{ref}" (at {f(x)} {f(y - sym.h/2 - 1.5)} 0) {FONT})',
             f'(property "Value" "{value}" (at {f(x)} {f(y + sym.h/2 + 1.5)} 0) {FONT})',
             f'(property "Footprint" "{props.get("Footprint","")}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))']
        for k, v in props.items():
            if k != "Footprint":
                o.append(f'(property "{k}" "{v}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        for num, *_ in sym.pins:
            o.append(f'(pin "{num}" (uuid {uid()}))')
        o.append(f'(instances (project "charger" (path "/{self.root}" (reference "{ref}") (unit 1))))')
        o.append(")")
        self.items.append("\n".join(o))
        for num, net in nets.items():
            px, py, side = sym.pos[num]
            ax, ay = x + px, y - py
            ang, just = (180, "right") if side == "L" else (0, "left")
            eff = f'(effects (font (size 1.27 1.27)) (justify {just}))'
            self.items.append(f'(label "{net}" (at {f(ax)} {f(ay)} {ang}) {eff} (uuid {uid()}))')
        self.bom.append((ref, value, props.get("LCSC", ""), props.get("Footprint", ""), sym.lib))
        return ref

    def text(self, x, y, s, size=1.8):
        s = s.replace('"', "'").replace("\n", "\\n")
        self.items.append(f'(text "{s}" (at {f(x)} {f(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')

    def write_lib(self, path):
        o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch")']
        for sym in self.syms.values():
            o.append(sym.lib_def().replace('(symbol "rev:', '(symbol "', 1))
        o.append(")")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(o) + "\n")

    def write(self, path):
        o = [f'(kicad_sch (version 20230121) (generator "claude-kisch")',
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
