"""Open the controller fanout area in a candidate, without changing power copper."""
import argparse,shutil,collections
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER,pt
from widen_rev_a_auxiliary_routes import xy
from fanout_rev_a_signals import rectangle_distance
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));removed=collections.Counter()
positions={'C45':(185,18),'C46':(180,18),'R69':(190,18),'R70':(195,18),'C49':(198,34),'R71':(198,30),'C47':(185,44),'C48':(185,48),'R72':(177,44),'R73':(177,48),'R78':(177,52),'R77':(185,52)}
for t in list(b.GetTracks()):
 if t.GetNetname() in POWER:continue
 via=isinstance(t,p.PCB_VIA)
 if t.GetNetname()=='GND' and not via and (t.GetLayer()!=p.F_Cu or p.ToMM(t.GetWidth())>=.7):continue
 if via:q=xy(t.GetPosition());hit=172<q[0]<207 and 16<q[1]<58
 else:hit=rectangle_distance(xy(t.GetStart()),xy(t.GetEnd()),(172,16,207,58))<.7
 if hit:removed[t.GetNetname()]+=1;b.Delete(t)
for f in b.GetFootprints():
 if f.GetReference() in positions:f.SetPosition(pt(*positions[f.GetReference()]))
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);assert out!=K/'robomaster_supercap.kicad_pcb';p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Controller local spacing:',positions,'removed:',dict(removed),'missing:',b.GetConnectivity().GetUnconnectedCount(False))
