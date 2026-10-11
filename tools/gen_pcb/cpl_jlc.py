"""JLCPCB CPL with rotation corrections (JLCKicadTools / kicad-jlcpcb-tools DB) and pad-bbox-centre positions.

usage: python3 cpl_jlc.py board.kicad_pcb cpl_rotations_db.csv out.csv [EXCLUDED,REFS]
"""
import csv, re, sys
import pcbnew
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
db = []
with open(sys.argv[2]) as f:
    r = csv.reader(f, skipinitialspace=True); next(r)
    for row in r:
        if row:
            db.append((re.compile(row[0]), int(row[1]), "db " + row[0]))
# local rule: KiCad ONSemi_SO-8FL has the same orientation as TDSON-8-1 (pins 1-4 on the left) -> same correction
db.insert(0, (re.compile(r"^ONSemi_SO-8FL"), 270, "local (=TDSON-8-1)"))
EXCL = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else {"H1", "H2", "H3", "J201", "R203"}
rows, notes = [], []
for fp in sorted(b.GetFootprints(), key=lambda f: (re.sub(r"\d", "", f.GetReference()), int(re.sub(r"\D", "", f.GetReference()) or 0))):
    ref = fp.GetReference()
    if ref in EXCL:
        continue
    name = str(fp.GetFPID().GetLibItemName())
    corr, why = 0, "none"
    for rx, c, w in db:
        if rx.search(name):
            corr, why = c, w; break
    bottom = fp.IsFlipped()
    rot0 = fp.GetOrientationDegrees()
    if bottom:                                  # same convention as kicad-jlcpcb-tools
        rot0 = (180 - rot0) % 360
    rot = (rot0 + corr) % 360
    pads = [p for p in fp.Pads() if p.GetNumber() and p.IsOnCopperLayer()]
    bb = pads[0].GetBoundingBox()
    for p in pads[1:]:
        bb.Merge(p.GetBoundingBox())
    cx, cy = T(bb.GetCenter().x), T(bb.GetCenter().y)
    ox, oy = cx - T(fp.GetPosition().x), cy - T(fp.GetPosition().y)
    rows.append([ref, f"{cx:.4f}mm", f"{-cy:.4f}mm", "Bottom" if bottom else "Top", f"{rot:.0f}"])
    if corr or abs(ox) > 0.05 or abs(oy) > 0.05:
        notes.append((ref, name, round(fp.GetOrientationDegrees()), corr, why, round(ox, 2), round(oy, 2)))
with open(sys.argv[3], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]); w.writerows(rows)
for n in notes:
    print(*n, sep="\t")
print(len(rows), "parts")
