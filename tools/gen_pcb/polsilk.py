"""Put the original silkscreen (0.12 mm lines incl. cathode/+ marks) back on polarized 2-pin parts. usage: polsilk.py in out"""
import sys, pcbnew
mm, T = pcbnew.FromMM, pcbnew.ToMM
POL = ("D1", "D101", "D2", "D201", "D202", "D203", "C7", "C113")
b = pcbnew.LoadBoard(sys.argv[1])
for fp in b.GetFootprints():
    if fp.GetReference() in POL:
        n = 0
        for it in fp.GraphicalItems():
            if it.GetLayer() == pcbnew.F_Fab and hasattr(it, "GetWidth") and abs(T(it.GetWidth()) - 0.12) < 1e-3:
                it.SetLayer(pcbnew.F_SilkS); n += 1
        print(fp.GetReference(), n)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
pcbnew.WriteDRCReport(b, sys.argv[2].replace(".kicad_pcb", "_drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
