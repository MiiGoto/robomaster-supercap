"""Build the hierarchical Rev B control board schematic (kisch2 style)."""
import os, sys, importlib.util
from kisch import uid, write_root
import kisch2

out = sys.argv[1]
only = sys.argv[2:] or None
os.makedirs(out, exist_ok=True)
SHEETS = [("input", "s1_input.py", "power_input.kicad_sch"),
          ("buckboost", "s2_buckboost.py", "buckboost.kicad_sch"),
          ("mcu", "s3_mcu.py", "mcu.kicad_sch"),
          ("protect", "s4_protect.py", "protect_sense.kicad_sch")]
if only:
    SHEETS = [x for x in SHEETS if x[0] in only]
root = uid()
built, subs = [], []
for name, script, fn in SHEETS:
    su = uid()
    sys.argv = [script, os.path.join(out, fn), f"/{root}/{su}"]
    ns = {"__name__": "__main__"}
    exec(compile(open(script).read(), script, "exec"), ns)
    built.append(ns["s"])
    subs.append((name, fn, su))
rootf = os.path.join(out, "control_board.kicad_sch")
write_root(rootf, "control_board", subs, root)
syms = {}
for sh in built:
    syms.update(sh.syms)
o = ['(kicad_symbol_lib (version 20220914) (generator "claude-kisch2")'] + [sy.file_def() for sy in syms.values()] + [")"]
open(os.path.join(out, "rev.kicad_sym"), "w", encoding="utf-8").write("\n".join(o) + "\n")
open(os.path.join(out, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "rev")(type "KiCad")(uri "${KIPRJMOD}/rev.kicad_sym")(options "")(descr "Rev B generated symbols"))\n)\n')
open(os.path.join(out, "control_board.kicad_pro"), "w").write('{\n  "meta": { "filename": "control_board.kicad_pro", "version": 1 }\n}\n')
errs, got = kisch2.check(rootf, built)
print("parts", sum(len(b.parts) for b in built), "nets", len(got))
for e in errs:
    print("  ", e)
print("CHECK", "OK" if not errs else f"{len(errs)} problems")
