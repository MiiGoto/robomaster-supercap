"""Set prototype planes and local routing rules; no project-settings writes."""
from pathlib import Path
import re,json
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER,mm,pt,uid
def zone(b,net,layer,rect):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet(net));z.SetLocalClearance(mm(.25))
 z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2))
 poly=z.Outline();poly.NewOutline()
 x1,y1,x2,y2=rect
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:poly.Append(mm(x),mm(y))
 b.Add(z)
 return z
def main():
 b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'))
 # Full reference plane. Critical switch-node keepouts are included; no signal
 # ground split is created across controller or Kelvin signal returns.
 zone(b,'GND',p.In1_Cu,(6,6,319,239))
 for rect in [(44,62,49,68),(44,75,49,81),(52,56,59,62),(82,62,89,68),(82,75,89,81)]:
  z=zone(b,'GND',p.In1_Cu,rect);z.SetIsRuleArea(True);z.SetDoNotAllowZoneFills(True)
  z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(False)
 # Datasheet-ground EPs use the reference plane, with fanout added by local
 # offline routing. Missing vias remain explicit unrouted DRC results.
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 p.SaveBoard(str(K/'robomaster_supercap.kicad_pcb'),b)
 assert p.ExportSpecctraDSN(b,str(ROOT/'.local/rev_a_pcb.dsn'))
 dsn=(ROOT/'.local/rev_a_pcb.dsn').read_text(encoding='utf8')
 start=dsn.index('(class kicad_default');end=dsn.index('(circuit',start)
 head=dsn[start:end]
 low={'ACTUATOR_12V','V12_DRIVER','V3V3'}
 for n in POWER|low:head=re.sub(r'(?<![\w])'+re.escape(n)+r'(?![\w])','',head)
 dsn=dsn[:start]+head+dsn[end:]
 # All signal classes inherit 0.25mm /0.20mm rules. Power tracks target3mm;
 # pad escapes may neck down and require separate physical review.
 extra='\n(class POWER '+ ' '.join(sorted(POWER))+' (circuit (use_via "Via[0-3]_600:300_um")) (rule (width 3000) (clearance 250)))'
 extra+='\n(class AUX '+ ' '.join(sorted(low))+' (circuit (use_via "Via[0-3]_600:300_um")) (rule (width 700) (clearance 200)))\n'
 # network is followed by wiring. Inject class definitions before its end.
 marker='  (wiring';at=dsn.index(marker)
 before=dsn[:at];last=before.rfind('  )')
 dsn=before[:last]+extra+before[last:]+dsn[at:]
 (ROOT/'.local/rev_a_pcb_route.dsn').write_text(dsn,encoding='utf8')
 print('Prepared ground plane with5 switch keepouts; POWER3mm/AUX0.7mm routing targets')
if __name__=='__main__':main()
