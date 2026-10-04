"""Rank actual disconnected pad groups for manual routing follow-up."""
import json,collections
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity();c.RecalculateRatsnest()
by_net=collections.defaultdict(list)
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNetCode():by_net[pad.GetNetname()].append((f.GetReference(),pad))
result=[]
for net,pads in by_net.items():
 remaining={x.m_Uuid.AsString():(ref,x) for ref,x in pads};groups=[]
 while remaining:
  key,(ref,anchor)=next(iter(remaining.items()))
  ids={x.m_Uuid.AsString() for x in c.GetConnectedItems(anchor)}|{key}
  group=[]
  for id in list(remaining):
   if id not in ids:continue
   ref,pad=remaining.pop(id);pos=pad.GetPosition()
   group.append({'ref':ref,'pin':pad.GetNumber(),'xy_mm':[round(p.ToMM(pos.x),4),round(p.ToMM(pos.y),4)]})
  groups.append(group)
 if len(groups)>1:
  priority=0 if net in POWER else 1 if any(t in net for t in ['KELVIN','GATE','HO_','LO_','PWM','FAULT','FAST','PERMIT','LIMIT','KILL']) else 2 if net in ['GND','V3V3','V12_DRIVER','ACTUATOR_12V'] else 3
  result.append({'net':net,'priority':priority,'pad_groups':len(groups),'minimum_pad_connections':len(groups)-1,'groups':groups})
result.sort(key=lambda x:(x['priority'],-x['minimum_pad_connections'],x['net']))
out={'native_unconnected_edges':c.GetUnconnectedCount(False),'disconnected_nets':len(result),'minimum_pad_connections':sum(x['minimum_pad_connections'] for x in result),'scope':'Pad clusters only; does not replace full native ratsnest or DRC.','nets':result}
(ROOT/'simulation/remaining_routes.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('Native unconnected:',out['native_unconnected_edges'],'disconnected pad nets:',len(result),'minimum pad links:',out['minimum_pad_connections'])
