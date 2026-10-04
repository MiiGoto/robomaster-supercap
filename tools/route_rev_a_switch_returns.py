"""Close local switched-source driver/bootstrap returns and short HV sense taps.
Writes an ignored candidate; native DRC and remaining-routing review required.
"""
import shutil,pcbnew as p
from build_rev_a_pcb import ROOT,K,pt,mm
work=ROOT/'.local/routing_completion/branches';work.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
for t in list(b.GetTracks()):
 if t.GetNetname() in ['BUS_DIV_TOP','CAP_DIV_TOP']:b.Delete(t)
def tr(net,coords,layer=p.F_Cu,w=.2):
 for a,c in zip(coords,coords[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*c));t.SetLayer(layer);t.SetWidth(mm(w));t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t)
def vi(net,x,y):
 v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(b.FindNet(net));v.SetLocked(True);b.Add(v)
for net,x,diode_x,diode_y in [('SW_NODE_A',40,35.9,65),('SW_NODE_B',80,75.9,58)]:
 vi(net,x-.0875,65)
 vi(net,diode_x,diode_y);tr(net,[(diode_x,diode_y),(x,diode_y),(x,65)],p.B_Cu)
 tr(net,[(x+1.525,72.5),(x+.5,72.5)]);vi(net,x+.5,72.5)
 tr(net,[(x+7.95,69),(x+8.5,69)]);vi(net,x+8.5,69);tr(net,[(x+8.5,69),(x,69)],p.B_Cu)
vi('SW_NODE_A',69.0875,55);tr('SW_NODE_A',[(69.0875,55),(69,54),(40,54),(40,58.365)],p.B_Cu)
vi('SW_NODE_B',64.0875,55);vi('SW_NODE_B',80,64.365);tr('SW_NODE_B',[(64.0875,55),(64,52),(80,52),(80,64.365)],p.In2_Cu)
# First33k divider resistors sit at the power region; long outgoing paths are
# downstream of that resistor rather than raw high-energy rail stubs.
for ref,net,xy,capxy in [('R85','BUS_LINK',(61,20),(58,28)),('R88','CAP_LINK',(111,20),(108,28))]:
 fps[ref].SetPosition(pt(*xy));pad=next(x for x in fps[ref].Pads() if x.GetNumber()=='1');pos=pad.GetPosition();a=(p.ToMM(pos.x),p.ToMM(pos.y));tr(net,[capxy,(capxy[0],20),a])
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(work/'robomaster_supercap.kicad_pcb'),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),work/('robomaster_supercap'+ext))
print('Candidate local switch returns and current-limited voltage taps saved')
