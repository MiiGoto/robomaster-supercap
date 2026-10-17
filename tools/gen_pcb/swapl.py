"""v3: L101 -> TAI-TECH TMPA1265SP-100MN-D (rev:L_TAI-TECH_TMPA1265); C101 -> 220p C0G. usage: swapl.py in out libdir"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
fps = {f.GetReference(): f for f in b.GetFootprints()}
old = fps["L101"]
nets = {p.GetNumber(): p.GetNet() for p in old.Pads() if p.GetNumber()}
new = pcbnew.FootprintLoad(sys.argv[3], "L_TAI-TECH_TMPA1265")
new.SetFPID(pcbnew.LIB_ID("rev", "L_TAI-TECH_TMPA1265"))
new.SetReference("L101"); new.SetValue("10uH")
new.SetPath(old.GetPath())
pr = dict(old.GetProperties())
pr.update({"LCSC": "C2880060", "Note": "TAI-TECH TMPA1265SP-100MN-D 10uH Isat 17A (-30%) Irms 13A DCR 13mR typ"})
new.SetProperties(pr)
new.SetPosition(old.GetPosition()); new.SetOrientation(old.GetOrientation()); new.SetAttributes(old.GetAttributes())
for p in new.Pads():
    p.SetNet(nets[p.GetNumber()])
r0 = old.Reference()
new.Reference().SetLayer(r0.GetLayer()); new.Reference().SetVisible(r0.IsVisible()); new.Reference().SetPosition(r0.GetPosition())
new.Reference().SetTextAngle(r0.GetTextAngle()); new.Reference().SetTextSize(r0.GetTextSize()); new.Reference().SetTextThickness(r0.GetTextThickness())
new.Value().SetLayer(pcbnew.F_Fab)
b.Remove(old); b.Add(new)
c = fps["C101"]
c.SetValue("220p C0G")
pr = dict(c.GetProperties()); pr["LCSC"] = "C2994655"; c.SetProperties(pr)
tb = b.GetTitleBlock(); tb.SetRevision("B-v3"); tb.SetDate("2026-10-17"); b.SetTitleBlock(tb)
b.Save(sys.argv[2] + ".tmp.kicad_pcb")
b2 = pcbnew.LoadBoard(sys.argv[2] + ".tmp.kicad_pcb")
pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
b2.Save(sys.argv[2])
pcbnew.WriteDRCReport(b2, sys.argv[2].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
