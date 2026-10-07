"""Import an offline routing session into an ignored review candidate.
Keeps live board untouched until native DRC and connectivity review pass.
"""
import argparse,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
ap=argparse.ArgumentParser();ap.add_argument('session');ap.add_argument('--source',default='.local/routing_completion/power_candidate.kicad_pcb');ap.add_argument('--output',default='.local/routing_completion/robomaster_supercap.kicad_pcb');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source))
for t in list(b.GetTracks()):
 # Excluded power/ground copper may include older unlocked segments. SES omits
 # fixed wiring, so retain these physical paths independently of lock state.
 if not t.IsLocked() and t.GetNetname() not in POWER|{'GND'}:b.Delete(t)
if not p.ImportSpecctraSES(b,str(ROOT/a.session)):raise SystemExit('SES import failed')
# Older sessions can include unchanged unlocked ground copper. Retain the
# original item once rather than creating concentric duplicate drills.
seen=set()
for t in sorted(b.GetTracks(),key=lambda x:not x.IsLocked()):
 if isinstance(t,p.PCB_VIA):
  q=t.GetPosition();key=('via',t.GetNetname(),q.x,q.y,t.GetWidth(p.F_Cu),t.GetDrill(),t.TopLayer(),t.BottomLayer())
 else:
  q=t.GetStart();r=t.GetEnd();ends=tuple(sorted([(q.x,q.y),(r.x,r.y)]));key=('track',t.GetNetname(),t.GetLayer(),t.GetWidth(),ends)
 if key in seen:b.Delete(t)
 else:seen.add(key)
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=ROOT/a.output;assert out.resolve()!=(K/'robomaster_supercap.kicad_pcb').resolve();out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:
 shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Review candidate:',out,'unconnected:',b.GetConnectivity().GetUnconnectedCount(False),'tracks/vias:',len(list(b.GetTracks())))
