"""Import an offline routing session into an ignored review candidate.
Keeps live board untouched until native DRC and connectivity review pass.
"""
import argparse,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K
ap=argparse.ArgumentParser();ap.add_argument('session');ap.add_argument('--source',default='.local/routing_completion/power_candidate.kicad_pcb');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source))
for t in list(b.GetTracks()):
 if not t.IsLocked():b.Delete(t)
if not p.ImportSpecctraSES(b,str(ROOT/a.session)):raise SystemExit('SES import failed')
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=ROOT/'.local/routing_completion/robomaster_supercap.kicad_pcb';p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:
 shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Review candidate:',out,'unconnected:',b.GetConnectivity().GetUnconnectedCount(False),'tracks/vias:',len(list(b.GetTracks())))
