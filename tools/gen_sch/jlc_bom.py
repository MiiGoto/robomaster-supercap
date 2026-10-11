"""Merge per-sheet BOMs into a JLCPCB assembly BOM (DNP / no-LCSC rows are listed separately)."""
import csv, glob, sys, collections
out = sys.argv[1]
rows = []
for f in sorted(glob.glob(f"{out}/*_bom.csv")):
    if f.endswith("jlcpcb_bom.csv"):
        continue
    rows += list(csv.DictReader(open(f, encoding="utf-8")))
g = collections.OrderedDict()
for r in rows:
    g.setdefault((r["Value"], r["Footprint"], r["LCSC"]), []).append(r["Ref"])
with open(f"{out}/jlcpcb_bom.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (v, fp, l), refs in g.items():
        if l:
            w.writerow([v, ",".join(refs), fp.split(":")[-1], l])
print("not assembled:", [(v, refs) for (v, fp, l), refs in g.items() if not l])
