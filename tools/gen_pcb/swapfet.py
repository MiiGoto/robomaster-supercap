"""Replace Q102-Q105 TDSON-8-1 with ONSemi_SO-8FL_488AA (same pinout/orientation), keep nets/pos/path."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
lib = sys.argv[3]
OLD = {f.GetReference(): f for f in b.GetFootprints() if f.GetReference() in ("Q102", "Q103", "Q104", "Q105")}
for ref in ["Q102", "Q103", "Q104", "Q105"]:
    old = OLD[ref]
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads() if p.GetNumber()}
    new = pcbnew.FootprintLoad(lib, "ONSemi_SO-8FL_488AA")
    new.SetFPID(pcbnew.LIB_ID("Package_SO", "ONSemi_SO-8FL_488AA"))
    new.SetReference(ref); new.SetValue(old.GetValue())
    new.SetPath(old.GetPath())
    new.SetProperties(old.GetProperties())
    new.SetPosition(old.GetPosition())
    new.SetOrientation(old.GetOrientation())
    new.SetAttributes(old.GetAttributes())
    for p in new.Pads():
        if p.GetNumber() in nets:
            p.SetNet(nets[p.GetNumber()])
    new.Reference().SetLayer(old.Reference().GetLayer()); new.Reference().SetVisible(old.Reference().IsVisible())
    new.Reference().SetPosition(old.Reference().GetPosition()); new.Reference().SetTextAngle(old.Reference().GetTextAngle())
    new.Reference().SetTextSize(old.Reference().GetTextSize()); new.Reference().SetTextThickness(old.Reference().GetTextThickness())
    new.Value().SetLayer(pcbnew.F_Fab)
    b.Remove(old)
    b.Add(new)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
pcbnew.WriteDRCReport(b, sys.argv[2].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
