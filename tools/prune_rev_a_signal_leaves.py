"""Prune obsolete signal tails in a candidate, preserving all pad groups.

Native DRC identifies the initial free ends. Direct KiCad adjacency peels
their attached copper chain, stopping at junctions and component lands.
The all-pad partition is checked before saving; power/GND are excluded.
"""
import argparse,collections,json,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
from widen_rev_a_auxiliary_routes import xy,point_distance,segment_distance

ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('drc');ap.add_argument('output');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));b.BuildConnectivity();c=b.GetConnectivity()
pad_nets=collections.defaultdict(list)
for f in b.GetFootprints():
 for x in f.Pads():
  if x.GetNetCode():pad_nets[x.GetNetname()].append(x)
def partitions():
 result={}
 for name,pads in pad_nets.items():
  remaining={x.m_Uuid.AsString():x for x in pads};groups=[]
  while remaining:
   uid,x=next(iter(remaining.items()));linked={t.m_Uuid.AsString() for t in c.GetConnectedItems(x)}|{uid}
   group=frozenset(k for k in remaining if k in linked);groups.append(group)
   for k in group:remaining.pop(k)
  result[name]=frozenset(groups)
 return result
before=partitions();tracks={t.m_Uuid.AsString():t for t in b.GetTracks() if t.GetNetname() not in POWER|{'GND'}}
def center_contact(a,z):
 if isinstance(a,p.PCB_VIA):
  return point_distance(xy(a.GetPosition()),xy(z.GetStart()),xy(z.GetEnd()))<.00001
 if isinstance(z,p.PCB_VIA):return center_contact(z,a)
 return segment_distance(xy(a.GetStart()),xy(a.GetEnd()),xy(z.GetStart()),xy(z.GetEnd()))<.00001
# Ignore neighboring segments' rounded-width overlap when counting graph
# branches; full native pad partitions still guard against removing a real
# copper bridge whose centerlines do not intersect.
adj={uid:{x.m_Uuid.AsString() for x in c.GetConnectedTracks(t) if center_contact(t,x)}&tracks.keys()-{uid} for uid,t in tracks.items()}
land={uid:bool(c.GetConnectedPads(t)) for uid,t in tracks.items()}
r=json.loads((ROOT/a.drc).read_text(encoding='utf8'))
initial={x['uuid'] for v in r['violations'] if v['type']=='track_dangling' for x in v['items']}
queue=collections.deque(uid for uid in initial if uid in tracks and not land[uid]);removed=set()
while queue:
 uid=queue.popleft()
 if uid in removed or land[uid]:continue
 if uid not in initial and len(adj[uid]-removed)>1:continue
 removed.add(uid)
 for other in adj[uid]:
  if not land[other] and len(adj[other]-removed)<=1:queue.append(other)
backups={}
for uid in removed:
 t=tracks[uid];clone=t.Duplicate();backups[uid]=(t.GetNetname(),p.Cast_to_PCB_VIA(clone) if isinstance(t,p.PCB_VIA) else p.Cast_to_PCB_TRACK(clone));b.Delete(t)
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();c=b.GetConnectivity();c.RecalculateRatsnest()
after=partitions();restore={name for name in before if after[name]!=before[name]}
for uid,(name,t) in backups.items():
 if name in restore:
  t.SetParent(b);t.SetNet(b.FindNet(name));b.Add(t);removed.remove(uid)
if restore:
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();c=b.GetConnectivity();c.RecalculateRatsnest()
 print('Preserved copper on nets requiring individual tail review:',sorted(restore))
 def try_subset(name,items):
  global c
  if not items:return
  saved=[]
  for uid,t in items:
   clone=t.Duplicate();saved.append((uid,p.Cast_to_PCB_VIA(clone) if isinstance(t,p.PCB_VIA) else p.Cast_to_PCB_TRACK(clone)));b.Delete(t)
  b.BuildConnectivity();c=b.GetConnectivity()
  if partitions()[name]==before[name]:
   removed.update(uid for uid,_ in items);return
  for uid,t in saved:t.SetParent(b);t.SetNet(b.FindNet(name));b.Add(t)
  b.BuildConnectivity();c=b.GetConnectivity()
  if len(saved)>1:
   mid=len(saved)//2;try_subset(name,saved[:mid]);try_subset(name,saved[mid:])
 for name in restore:
  try_subset(name,[(uid,t) for uid,(n,t) in backups.items() if n==name])
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();c=b.GetConnectivity();c.RecalculateRatsnest()
assert partitions()==before,'Pruning changed a physical pad partition; candidate rejected'
out=ROOT/a.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Pruned signal tail objects:',len(removed),'native unconnected:',c.GetUnconnectedCount(False))
