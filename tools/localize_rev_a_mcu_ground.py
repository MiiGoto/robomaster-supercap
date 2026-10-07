"""Replace MCU peripheral ground fences with short inward plane connections.

Only local controller ground copper changes. Preserve the reference plane and
all main power/ground copper outside the explicitly bounded controller area.
Candidate only; complete pad connectivity and native DRC remain mandatory.
"""
import argparse,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K,pt,mm
from widen_rev_a_auxiliary_routes import xy
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));removed=0
for t in list(b.GetTracks()):
 if t.GetNetname()!='GND':continue
 if isinstance(t,p.PCB_VIA):
  x,y=xy(t.GetPosition());hit=178<x<192 and 25<y<39
 else:
  if t.GetLayer()!=p.F_Cu or p.ToMM(t.GetWidth())>=.7:continue
  x,y=xy(t.GetStart());u,v=xy(t.GetEnd());hit=max(x,u)>=174 and min(x,u)<=215 and max(y,v)>=15 and min(y,v)<=70
 if hit:b.Delete(t);removed+=1
f=next(f for f in b.GetFootprints() if f.GetReference()=='U11');cx,cy=xy(f.GetPosition());added=[]
for pad in f.Pads():
 if pad.GetNetname()!='GND':continue
 x,y=xy(pad.GetPosition());dx,dy=x-cx,y-cy
 q=(x-1.3*(1 if dx>0 else -1),y) if abs(dx)>abs(dy) else (x,y-1.3*(1 if dy>0 else -1))
 t=p.PCB_TRACK(b);t.SetStart(pt(x,y));t.SetEnd(pt(*q));t.SetLayer(p.F_Cu);t.SetWidth(mm(.2));t.SetNet(b.FindNet('GND'));t.SetLocked(True);b.Add(t)
 v=p.PCB_VIA(b);v.SetPosition(pt(*q));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(b.FindNet('GND'));v.SetLocked(True);b.Add(v);added.append((pad.GetNumber(),q))
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=ROOT/a.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('MCU local ground replaced',removed,'objects; new returns',added,'missing',b.GetConnectivity().GetUnconnectedCount(False))
