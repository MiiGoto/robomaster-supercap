"""Build the hierarchical Rev B control board schematic (root + charger + control sheets)."""
import os
import sys
from kisch import uid, write_root

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
root, s1, s2 = uid(), uid(), uid()
sheets = []
for script, fname, su in (("charger.py", "charger.kicad_sch", s1), ("control.py", "control.kicad_sch", s2)):
    sys.argv = [script, os.path.join(out, fname), f"/{root}/{su}"]
    ns = {"__name__": "__main__"}
    exec(compile(open(script).read(), script, "exec"), ns)
    sheets.append(ns["s"])
write_root(os.path.join(out, "control_board.kicad_sch"), "control_board",
           [("charger", "charger.kicad_sch", s1), ("control", "control.kicad_sch", s2)], root)
# merged symbol library
syms = {}
for sh in sheets:
    syms.update(sh.syms)
o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch")']
o += [sy.file_def() for sy in syms.values()]
o.append(")")
open(os.path.join(out, "rev.kicad_sym"), "w", encoding="utf-8").write("\n".join(o) + "\n")
open(os.path.join(out, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "rev")(type "KiCad")(uri "${KIPRJMOD}/rev.kicad_sym")(options "")(descr "Rev B generated symbols"))\n)\n')
open(os.path.join(out, "control_board.kicad_pro"), "w").write('{\n  "meta": { "filename": "control_board.kicad_pro", "version": 1 }\n}\n')
print("built", out)
