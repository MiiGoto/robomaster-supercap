"""Independent KiCad DRC probes for the scope of the approved pad exception."""
import json,shutil,subprocess
from pathlib import Path
import pcbnew as p
from build_rev_a_pcb import ROOT,K,pt,mm
CLI='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
CASES=[('fine_015','U7',.15,False,False,0),
 ('fine_014','U7',.14,False,False,1),
 ('other_019','U99',.19,False,False,1),
 ('other_020','U99',.20,False,False,0),
 ('cross_package_019','U7',.19,True,False,1),
 ('pad_track_019','U7',.19,False,True,1)]
def main():
 result=[]
 for name,ref,gap,cross,track,expected in CASES:
  out=ROOT/'.local/rule_probes'/name;out.mkdir(parents=True,exist_ok=True)
  stem=out/'robomaster_supercap'
  shutil.copyfile(K/'robomaster_supercap.kicad_dru',str(stem)+'.kicad_dru')
  Path(str(stem)+'.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.15}}}}),encoding='utf8')
  b=p.BOARD();nets=[]
  for i in [1,2]:
   n=p.NETINFO_ITEM(b,'N'+str(i),i);b.Add(n);nets.append(n)
  f=p.FOOTPRINT(b);f.SetReference(ref);f.SetPosition(pt(8,8));b.Add(f)
  for i in [0,1]:
   if i==1 and track:
    t=p.PCB_TRACK(b);xx=8+.175+gap+.125
    t.SetStart(pt(xx,7.5));t.SetEnd(pt(xx,8.5));t.SetWidth(mm(.25));t.SetLayer(p.F_Cu);t.SetNet(nets[i]);b.Add(t);continue
   parent=f
   if i==1 and cross:
    parent=p.FOOTPRINT(b);parent.SetReference('U8');parent.SetPosition(pt(8,8));b.Add(parent)
   pad=p.PAD(parent);pad.SetNumber(str(i+1));pad.SetAttribute(p.PAD_ATTRIB_SMD)
   layers=p.LSET();layers.AddLayer(p.F_Cu)
   pad.SetShape(p.PAD_SHAPE_RECT);pad.SetSize(pt(.35,.8));pad.SetLayerSet(layers)
   pad.SetPosition(pt(8+i*(.35+gap),8));pad.SetNet(nets[i]);parent.Add(pad)
  for a,c in [((5,5),(15,5)),((15,5),(15,15)),((15,15),(5,15)),((5,15),(5,5))]:
   s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*c));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
  board=str(stem)+'.kicad_pcb';p.SaveBoard(board,b)
  report=out/'drc.json'
  subprocess.run([CLI,'pcb','drc',board,'--format','json','-o',str(report)],check=True,capture_output=True)
  d=json.loads(report.read_text(encoding='utf8'))
  found=sum(v['type']=='clearance' for v in d['violations'])
  assert bool(found)==bool(expected),(name,found,expected)
  result.append({'case':name,'clearance_violations':found,'passed':True})
 (ROOT/'simulation/clearance_rule_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print('PASS:',len(result),'independent DRC scope/boundary probes')
if __name__=='__main__':main()
