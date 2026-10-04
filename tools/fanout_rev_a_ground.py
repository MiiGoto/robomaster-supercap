"""Add short clearance-checked ground escapes into the existing In1 plane.
Candidate only; exact native DRC must pass before adoption.
"""
import math,shutil,json,argparse
from pathlib import Path
import pcbnew as p
from build_rev_a_pcb import K,ROOT,pt,mm
ap=argparse.ArgumentParser();ap.add_argument('--source',default='hardware/kicad/robomaster_supercap.kicad_pcb');ap.add_argument('--output',default='.local/routing_completion/ground');args=ap.parse_args()
work=ROOT/args.output;work.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(ROOT/args.source));b.BuildConnectivity();c=b.GetConnectivity()
def pos(v):return p.ToMM(v.x),p.ToMM(v.y)
def dist(q,a,z):
 dx=z[0]-a[0];dy=z[1]-a[1];dd=dx*dx+dy*dy
 t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/dd)) if dd else 0
 return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segdist(a,b,c,d):
 if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:return 0
 return min(dist(a,c,d),dist(b,c,d),dist(c,a,b),dist(d,a,b))
tracks=[];boxes=[];holes=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):holes.append((pos(t.GetPosition()),p.ToMM(t.GetDrill())/2))
 if t.GetNetname()=='GND':continue
 if isinstance(t,p.PCB_VIA):tracks.append((pos(t.GetPosition()),pos(t.GetPosition()),p.ToMM(t.GetWidth(p.F_Cu))/2,True))
 else:tracks.append((pos(t.GetStart()),pos(t.GetEnd()),p.ToMM(t.GetWidth())/2,t.GetLayer()==p.F_Cu))
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetAttribute()!=p.PAD_ATTRIB_SMD:holes.append((pos(pad.GetPosition()),max(pos(pad.GetDrillSize()))/2))
  if pad.GetNetname()=='GND':continue
  bb=pad.GetBoundingBox();x,y=pos(bb.GetPosition());u,v=pos(bb.GetEnd());boxes.append((x,y,u,v,pad.IsOnLayer(p.F_Cu)))
keepouts=[]
for z in b.Zones():
 if z.GetIsRuleArea():
  bb=z.GetBoundingBox();keepouts.append((*pos(bb.GetPosition()),*pos(bb.GetEnd())))
def safe(a,q,via_required=True):
 if not(7<q[0]<318 and 7<q[1]<238):return False
 if via_required and any(math.dist(q,center)<r+.405 for center,r in holes):return False
 if via_required and any(x<=q[0]<=u and y<=q[1]<=v for x,y,u,v in keepouts):return False
 for x,y,u,v,front in boxes:
  near=(max(x,min(u,q[0])),max(y,min(v,q[1])))
  if via_required and math.dist(q,near)<.51:return False
  if front:
   edges=[((x,y),(u,y)),((u,y),(u,v)),((u,v),(x,v)),((x,v),(x,y))]
   if x<=a[0]<=u and y<=a[1]<=v:return False
   if min(segdist(a,q,s,t) for s,t in edges)<.315:return False
 for s,t,r,front in tracks:
  if via_required and dist(q,s,t)<r+.51:return False
  if front and segdist(a,q,s,t)<r+.315:return False
 return True
pads=[(f.GetReference(),x) for f in b.GetFootprints() for x in f.Pads() if x.GetNetname()=='GND']
anchor=next(x for ref,x in pads if ref=='C1' and x.GetNumber()=='2')
added=[];skipped=[]
for ref,pad in pads:
 linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(anchor)}|{anchor.m_Uuid.AsString()}
 if pad.m_Uuid.AsString() in linked:continue
 if pad.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
 a=pos(pad.GetPosition());selected=None;existing_target=False
 for radius in [.9,1.3,1.8,2.3,3.,4.,5.]:
  for dx,dy in [(radius,0),(-radius,0),(0,radius),(0,-radius)]:
   q=(a[0]+dx,a[1]+dy)
   if safe(a,q):selected=q;break
  if selected:break
 path=[a,selected]
 if not selected:
  for r1 in [.35,.6,.9,1.3]:
   for dx,dy in [(r1,0),(-r1,0),(0,r1),(0,-r1)]:
    mid=(a[0]+dx,a[1]+dy)
    if not safe(a,mid,False):continue
    for r2 in [1.,1.5,2.,3.,4.]:
     for ex,ey in [(r2,0),(-r2,0),(0,r2),(0,-r2)]:
      q=(mid[0]+ex,mid[1]+ey)
      if safe(mid,q):selected=q;path=[a,mid,q];break
     if selected:break
    if selected:break
   if selected:break
 if not selected:
  targets=[pos(x.GetPosition()) for x in c.GetConnectedItems(anchor) if isinstance(x,(p.PAD,p.PCB_VIA)) and math.dist(a,pos(x.GetPosition()))<10]
  for q in sorted(targets,key=lambda x:math.dist(a,x)):
   if safe(a,q,False):selected=q;path=[a,q];existing_target=True;break
   for r1 in [.35,.6,.9,1.3]:
    for dx,dy in [(r1,0),(-r1,0),(0,r1),(0,-r1)]:
     mid=(a[0]+dx,a[1]+dy)
     if safe(a,mid,False) and safe(mid,q,False):selected=q;path=[a,mid,q];existing_target=True;break
    if selected:break
   if selected:break
 if not selected:skipped.append((ref,pad.GetNumber()));continue
 for start,end in zip(path,path[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(*start));t.SetEnd(pt(*end));t.SetLayer(p.F_Cu);t.SetWidth(mm(.2));t.SetNet(b.FindNet('GND'));t.SetLocked(True);b.Add(t)
 if not existing_target:
  v=p.PCB_VIA(b);v.SetPosition(pt(*selected));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(b.FindNet('GND'));v.SetLocked(True);b.Add(v)
  holes.append((selected,.15))
 c.Build(b);added.append((ref,pad.GetNumber(),selected))
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
out=work/'robomaster_supercap.kicad_pcb';p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
result={'added_ground_escapes':len(added),'skipped_pad_candidates':skipped,'native_unconnected':b.GetConnectivity().GetUnconnectedCount(False),'added':added}
(work/'fanout.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print('Ground escapes',len(added),'native unconnected',result['native_unconnected'])
