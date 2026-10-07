"""Remove identified obsolete dangling branches, retaining planned SMD access.

Only remove DRC-identified dangling UUIDs outside power/GND. Normal cleanup
restores any individual deletion that splits a physical pad group. Explicit
ripup/conflict-removal modes instead require rerouting and full validation.
Candidate output and repeat native DRC required.
"""
import argparse,json,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('drc');ap.add_argument('output');ap.add_argument('--ripup-net',action='append',default=[]);ap.add_argument('--remove-conflicting-signals',action='store_true');ap.add_argument('--prune-unused-vias',action='store_true');a=ap.parse_args()
assert not set(a.ripup_net)&(POWER|{'GND'})
b=p.LoadBoard(str(ROOT/a.source));r=json.loads((ROOT/a.drc).read_text(encoding='utf8'))
b.BuildConnectivity();c=b.GetConnectivity();net_pads={}
def pad_groups(name):
 if name not in net_pads:net_pads[name]=[x for f in b.GetFootprints() for x in f.Pads() if x.GetNetname()==name]
 remaining={x.m_Uuid.AsString():x for x in net_pads[name]};count=0
 while remaining:
  uid,pad=next(iter(remaining.items()));linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(pad)}|{uid}
  remaining={k:x for k,x in remaining.items() if k not in linked};count+=1
 return count
ids={i['uuid'] for v in r['violations'] if v['type']=='track_dangling' for i in v['items']}
if a.remove_conflicting_signals:
 ids.update(i['uuid'] for v in r['violations'] if v['severity']=='error' or v['type'] in ['hole_to_hole','holes_co_located'] for i in v['items'])
removed=[]
for t in list(b.GetTracks()):
 if (t.m_Uuid.AsString() in ids or t.GetNetname() in a.ripup_net) and t.GetNetname() not in POWER|{'GND'}:
  name=t.GetNetname();uid=t.m_Uuid.AsString();before=pad_groups(name)
  clone=t.Duplicate();backup=p.Cast_to_PCB_VIA(clone) if isinstance(t,p.PCB_VIA) else p.Cast_to_PCB_TRACK(clone);b.Delete(t)
  b.BuildConnectivity();c=b.GetConnectivity()
  if not a.ripup_net and not a.remove_conflicting_signals and pad_groups(name)>before:
   backup.SetParent(b);backup.SetNet(b.FindNet(name));b.Add(backup);b.BuildConnectivity();c=b.GetConnectivity()
  else:removed.append((name,uid))
# Co-located generated vias have one physical drill, not duplicated holes.
seen=set()
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA):continue
 q=t.GetPosition();key=(t.GetNetname(),q.x,q.y,t.GetWidth(p.F_Cu),t.GetDrill(),t.TopLayer(),t.BottomLayer())
 if key in seen:removed.append((t.GetNetname(),t.m_Uuid.AsString()));b.Delete(t)
 else:seen.add(key)
b.BuildConnectivity();c=b.GetConnectivity()
if a.prune_unused_vias:
 via_ids={i['uuid'] for v in r['violations'] if v['type']=='via_dangling' for i in v['items']}
 for t in list(b.GetTracks()):
  name=t.GetNetname()
  if t.m_Uuid.AsString() not in via_ids or name in POWER|{'GND'}:continue
  before=pad_groups(name);uid=t.m_Uuid.AsString();backup=p.Cast_to_PCB_VIA(t.Duplicate());b.Delete(t)
  b.BuildConnectivity();c=b.GetConnectivity()
  if pad_groups(name)>before:
   backup.SetParent(b);backup.SetNet(b.FindNet(name));b.Add(backup);b.BuildConnectivity();c=b.GetConnectivity()
  else:removed.append((name,uid))
 b.BuildConnectivity();c=b.GetConnectivity()
pad_ids={x.m_Uuid.AsString() for f in b.GetFootprints() for x in f.Pads()}
orphan_ids=set()
visited_ids=set()
for t in b.GetTracks():
 if t.GetNetname() in POWER|{'GND'} or t.m_Uuid.AsString() in visited_ids:continue
 linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(t)}|{t.m_Uuid.AsString()}
 visited_ids.update(linked)
 if not linked&pad_ids:orphan_ids.update(linked)
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in orphan_ids:
  removed.append((t.GetNetname(),t.m_Uuid.AsString()));b.Delete(t)
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=ROOT/a.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Removed obsolete dangling branches',len(removed),'unconnected',b.GetConnectivity().GetUnconnectedCount(False))
out.with_suffix('.cleanup.json').write_text(json.dumps(removed,indent=2)+'\n',encoding='utf8')
