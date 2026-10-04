"""Move old generated In1 signal segments into an isolated rerouting candidate.
Do not adopt this intermediate board before all dangling routes are completed.
"""
import argparse,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K
ap=argparse.ArgumentParser();ap.add_argument('--source',default='hardware/kicad/robomaster_supercap.kicad_pcb');ap.add_argument('--output',default='.local/routing_completion/reference/robomaster_supercap.kicad_pcb');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));removed=0
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In1_Cu and t.GetNetname()!='GND':b.Delete(t);removed+=1
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Reference-plane candidate:',removed,'signal segments need rerouting; live board unchanged')
