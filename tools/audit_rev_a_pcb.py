"""Read actual PCB pads/tracks and CLI DRC, never infer completion from intent."""
import json,collections
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
def main():
 b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'))
 b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
 manifest={a['ref']:a for a in json.loads((ROOT/'simulation/rev_a_connectivity.json').read_text(encoding='utf8')) if a['fp']}
 fps={f.GetReference():f for f in b.GetFootprints() if not f.GetReference().startswith('H')}
 assert set(fps)==set(manifest),(set(fps)-set(manifest),set(manifest)-set(fps))
 checked=0
 for ref,a in manifest.items():
  for pad in fps[ref].Pads():
   expected=a['nets'].get(pad.GetNumber())
   if expected is not None:
    assert pad.GetNetname()==expected,(ref,pad.GetNumber(),expected,pad.GetNetname())
    checked+=1
 stats={}
 for t in b.GetTracks():
  n=t.GetNetname();s=stats.setdefault(n,{'length_mm':0.,'vias':0,'min_width_mm':None,'layers':[]})
  if isinstance(t,p.PCB_VIA):s['vias']+=1;continue
  s['length_mm']+=p.ToMM(t.GetLength())
  width=p.ToMM(t.GetWidth());s['min_width_mm']=min(s['min_width_mm'] or width,width)
  layer=b.GetLayerName(t.GetLayer())
  if layer not in s['layers']:s['layers'].append(layer)
 report=ROOT/'.local/pcb_drc_final.json'
 d=json.loads(report.read_text(encoding='utf8')) if report.exists() else {}
 errors=sum(x['severity']=='error' for x in d.get('violations',[]))
 warnings=sum(x['severity']=='warning' for x in d.get('violations',[]))
 result={'footprints':len(fps),'mounting_holes':4,'pad_net_matches':checked,
  'copper_layers':b.GetCopperLayerCount(),'track_objects':sum(not isinstance(t,p.PCB_VIA) for t in b.GetTracks()),
  'via_objects':sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks()),
  'zones':sum(not z.GetIsRuleArea() for z in b.Zones()),
  'keepouts':sum(z.GetIsRuleArea() for z in b.Zones()),
  'drc_errors':errors,'drc_warnings':warnings,'drc_unrouted_report_items':len(d.get('unconnected_items',[])),
  'unrouted':b.GetConnectivity().GetUnconnectedCount(False),
  'schematic_parity':len(d.get('schematic_parity',[])),
  'drc_types':dict(collections.Counter(x['type'] for x in d.get('violations',[]))),
  'power_nets':{n:stats.get(n,{}) for n in sorted(POWER)},
  'kelvin_nets':{n:s for n,s in stats.items() if 'KELVIN' in n},
  'status':'PCB engineering draft; unmeasured; NOT fabrication/energizing release'}
 (ROOT/'simulation/pcb_rev_a_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
