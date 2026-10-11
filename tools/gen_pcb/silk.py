"""Silkscreen clean-up: small passives' references -> F.Fab, others kept small; add labels. usage: silk.py in out"""
import sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
mm = pcbnew.FromMM
KEEP = ("U", "J", "Q1", "Q102", "Q103", "Q104", "Q105", "L101", "F1", "D204", "D205", "H")
for fp in b.GetFootprints():
    r = fp.GetReference()
    ref = fp.Reference()
    big = r.startswith(("U", "J")) or r in KEEP
    if not big:
        ref.SetLayer(pcbnew.F_Fab)
    else:
        ref.SetTextSize(pcbnew.VECTOR2I(mm(0.9), mm(0.9)))
        ref.SetTextThickness(mm(0.15))
    fp.Value().SetVisible(False)
    # drop footprint silk lines that only outline tiny parts (keep pin-1 marks of ICs)
    if not big:
        for it in fp.GraphicalItems():
            if it.GetLayer() == pcbnew.F_SilkS:
                it.SetLayer(pcbnew.F_Fab)


def txt(s, x, y, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(mm(100 + x), mm(100 + y)))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(0.15))
    t.SetTextAngleDegrees(rot)
    b.Add(t)


txt("SUPERCAP CTRL rev B", 34, 55.6 - 0.2, 0.8)
b.Save(sys.argv[2])
