"""Explicit Rev A power trunks on bottom copper, with parallel-via fanout.
Writes an ignored review candidate; never replaces the live board implicitly.
"""
import argparse
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER,pt,mm
ap=argparse.ArgumentParser();ap.add_argument('--source',default='hardware/kicad/robomaster_supercap.kicad_pcb');ap.add_argument('--output',default='.local/routing_completion/power_candidate.kicad_pcb');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));fps={f.GetReference():f for f in b.GetFootprints()}
# Replace previous provisional power routes only. Preserve every other route.
for t in list(b.GetTracks()):
 if t.GetNetname() in POWER|{'BUS_FAST_NEG','CAP_FAST_NEG','BUS_ISO_FB','BUS_FUSED','BUS_KELVIN_M','CAP_KELVIN_M','IL_KELVIN_M','HO_B','LO_A'}:b.Delete(t)
for ref,xy in [('J24',(15,52)),('J33',(117,12))]:fps[ref].SetPosition(pt(*xy))
def route(net,coords,width=3,layer=p.B_Cu):
 for v,w in zip(coords,coords[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(*v));t.SetEnd(pt(*w));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
def via(net,x,y,d=.8,drill=.4):
 v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(mm(d));v.SetDrill(mm(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));v.SetLocked(True);b.Add(v)
def drain(ref,net):
 f=fps[ref];pad=next(x for x in f.Pads() if x.GetNumber()=='3' and p.ToMM(x.GetSize().x)>4)
 x,y=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)
 for dx in [-1.2,0,1.2]:
  for dy in [-1.3,0,1.3]:via(net,x+dx,y+dy,.6,.3)
 route(net,[(x-1.2,y),(x+1.2,y)],3)
 return x,y
# Three source fingers each have a local fanout; they do not share the gate pad.
for x,net in [(42.2,'SW_NODE_A'),(82.2,'SW_NODE_B')]:
 for y in [63.095,64.365,65.635]:
  route(net,[(x,y),(x-.9,y)],.5,p.F_Cu);via(net,x-.9,y,.6,.3)
 route(net,[(x-.9,63.095),(x-.9,65.635)],1.2)
for ref,net in [('Q12','BUS_LINK'),('Q13','SW_NODE_A'),('Q14','CAP_LINK'),('Q15','SW_NODE_B')]:drain(ref,net)
# Shunts: main terminals1/4 only; Kelvin2/3 are never shorted on the PCB.
for ref in ['R33','R34','R35']:
 for pad in fps[ref].Pads():
  if pad.GetNumber() not in ['1','4']:continue
  x,y=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)
  route(pad.GetNetname(),[(x-1.05,y),(x+1.05,y)],2)
  for dx in [-1.05,0,1.05]:
   for dy in [-.45,.45]:via(pad.GetNetname(),x+dx,y+dy,.6,.3)
for pin,net,x in [('1','IL_TO_L',59.7),('2','SW_NODE_B',70.3)]:
 route(net,[(x,65),(x,75)],3)
 for dx in [-.9,.9]:
  for y in [65,67,69,71,73,75]:via(net,x+dx,y,.6,.3)
route('SW_NODE_A',[(41.3,64.365),(40,64.365)],.7)
route('SW_NODE_A',[(40,64.365),(40,78),(45.33,78)])
route('SW_NODE_A',[(40,64.365),(40,58.365),(52.52,58.365)])
route('IL_TO_L',[(57.48,59.635),(59.7,61.855),(59.7,70)])
route('SW_NODE_B',[(81.3,64.365),(80,64.365)],.7)
route('SW_NODE_B',[(80,64.365),(80,78),(85.33,78)])
route('SW_NODE_B',[(70.3,70),(75.33,70),(79.7,74.37),(80,74.37)])
route('BUS_LINK_IN',[(15,52),(23.155,52),(27.52,56.365)])
route('CAP_LINK_IN',[(117,12),(121,16),(121,50),(105.52,50)],3,p.F_Cu)
route('CAP_LINK_IN',[(105.52,50),(105.52,56.365)],2,p.F_Cu)
for net,offset,shunt in [('BUS_LINK',0,(32.48,57.635)),('CAP_LINK',50,(110.48,57.635))]:
 # Six bulk positive terminals remain through-hole and join the local spine.
 route(net,[(30+offset,48),(58+offset,48)])
 for x in [30+offset,44+offset,58+offset]:
  route(net,[(x,28),(x,42),(x,48)],2.4)
 qx=45.33 if offset==0 else 85.33
 route(net,[(qx,65),(qx,48)],3,p.F_Cu)
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:via(net,qx+dx,48+dy,.6,.3)
 route(net,[(qx-1,48),(qx+1,48)],3)
 sx,sy=shunt
 route(net,[(sx,sy),(sx,48)])
 # Ceramic local link decoupling power pad: 4-via fanout inside its land.
 for ref in (['C7','C8'] if offset==0 else ['C15','C16']):
  pad=next(x for x in fps[ref].Pads() if x.GetNumber()=='1');x,y=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)
  for dy in [-.9,-.3,.3,.9]:via(net,x,y+dy,.6,.3)
  route(net,[(x,y-.9),(x,y+.9)],1.2)
  xx=31 if offset==0 else 95
  route(net,[(x,y),(xx,y),(xx,48)],1.0)
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(ROOT/a.output),b)
print('Power routing candidate saved; DRC required:',a.output)
