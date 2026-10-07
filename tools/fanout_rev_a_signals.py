"""Provide native-DRC-reviewed escapes for disconnected signal clusters.

Candidate only. Conservatively check foreign copper/drills and leave the
reference plane for GND, except bounded MCU In1 escapes explicitly checked
by check_rev_a_routing_completion.py. Exact KiCad DRC is required.
"""
import argparse
import collections
import json
import math
import heapq
import shutil
import pcbnew as p
from build_rev_a_pcb import ROOT, K, POWER, pt, mm
from widen_rev_a_auxiliary_routes import xy, point_distance, segment_distance


class Index:
    def __init__(self):
        self.cells=collections.defaultdict(list)

    def keys(self, box):
        x,y,u,v=box
        for i in range(math.floor(x/5),math.floor(u/5)+1):
            for j in range(math.floor(y/5),math.floor(v/5)+1):
                yield i,j

    def add(self, box, item):
        for key in self.keys(box): self.cells[key].append(item)

    def query(self, box):
        seen=set()
        for key in self.keys(box):
            for item in self.cells.get(key,[]):
                if id(item) not in seen:
                    seen.add(id(item));yield item


def bounds(a,z,r):
    return min(a[0],z[0])-r,min(a[1],z[1])-r,max(a[0],z[0])+r,max(a[1],z[1])+r


def rectangle_distance(a,z,box):
    x,y,u,v=box
    if (x<=a[0]<=u and y<=a[1]<=v) or (x<=z[0]<=u and y<=z[1]<=v):return 0
    return min(segment_distance(a,z,s,t) for s,t in
               [((x,y),(u,y)),((u,y),(u,v)),((u,v),(x,v)),((x,v),(x,y))])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');ap.add_argument('--maze',action='store_true');ap.add_argument('--maze-step',type=float,default=.1);ap.add_argument('--extra-escapes',action='store_true');ap.add_argument('--net',action='append',default=[]);ap.add_argument('--minimum-reach',type=float,default=.7);ap.add_argument('--layer',choices=['F.Cu','In1.Cu','In2.Cu','B.Cu'],default='F.Cu');ap.add_argument('--include-ground',action='store_true');ap.add_argument('--join-ground-targets',action='store_true');ap.add_argument('--maze-radius',type=float,default=6);ap.add_argument('--join-existing-net',action='store_true');ap.add_argument('--mcu-outward-only',action='store_true');ap.add_argument('--mcu-via-spacing',type=float,default=0);ap.add_argument('--mcu-inward-only',action='store_true');ap.add_argument('--only-mcu-clusters',action='store_true');args=ap.parse_args()
    assert .025 <= args.maze_step <= .1
    if args.layer=='In1.Cu':
        assert args.only_mcu_clusters and args.extra_escapes and args.maze_radius<=38
        assert args.net and set(args.net)<={'V3V3','CAP_I_ADC','PRE_CAP_REQUEST','TEMP_BANK_ADC','TEMP_FET_ADC','TEMP_L_ADC','WD_HEARTBEAT'}
    b=p.LoadBoard(str(ROOT/args.source));b.BuildConnectivity();c=b.GetConnectivity()
    escape_layer=b.GetLayerID(args.layer)
    copper=Index();holes=Index();keepouts=[];via_ids=set();pad_nets=collections.defaultdict(list)
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetCode():pad_nets[pad.GetNetname()].append(pad)
            bb=pad.GetBoundingBox();a,z=xy(bb.GetPosition()),xy(bb.GetEnd());box=(*a,*z)
            copper.add(box,('pad',pad.GetNetname(),box,pad.IsOnLayer(escape_layer),pad.GetAttribute()!=p.PAD_ATTRIB_SMD))
            if pad.GetAttribute()!=p.PAD_ATTRIB_SMD:
                q=xy(pad.GetPosition());r=max(xy(pad.GetDrillSize()))/2
                holes.add(bounds(q,q,r),(q,r))
    def add_copper(t):
        if isinstance(t,p.PCB_VIA):
            q=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.F_Cu))/2
            copper.add(bounds(q,q,r),('trace',t.GetNetname(),q,q,r,True,True))
            hr=p.ToMM(t.GetDrill())/2;holes.add(bounds(q,q,hr),(q,hr));via_ids.add(t.m_Uuid.AsString())
        else:
            a,z=xy(t.GetStart()),xy(t.GetEnd());r=p.ToMM(t.GetWidth())/2
            copper.add(bounds(a,z,r),('trace',t.GetNetname(),a,z,r,t.GetLayer()==escape_layer,True))
    for t in b.GetTracks():add_copper(t)
    for zone in b.Zones():
        if zone.GetIsRuleArea():
            bb=zone.GetBoundingBox();keepouts.append((*xy(bb.GetPosition()),*xy(bb.GetEnd())))
    def safe(net,a,z,via):
        if mcu_origin and escape_layer==p.F_Cu and (getattr(args,'mcu_outward_only',False) or getattr(args,'mcu_inward_only',False)):
            origin=xy(pad.GetPosition());center=xy(pad.GetParentFootprint().GetPosition());vx=origin[0]-center[0];vy=origin[1]-center[1]
            for q in [a,z]:
                depth=(q[0]-origin[0])*(1 if vx>0 else -1) if abs(vx)>abs(vy) else (q[1]-origin[1])*(1 if vy>0 else -1)
                if getattr(args,'mcu_outward_only',False) and depth < -1e-6:return False
                if getattr(args,'mcu_inward_only',False) and depth > 1e-6:return False
        if not (7<z[0]<318 and 7<z[1]<238):return False
        if via:
            if escape_layer==p.In1_Cu and 166<z[0]<215 and 12<z[1]<62:
                return False
            if getattr(args,'mcu_via_spacing',0) and (mcu_origin or 168<z[0]<208 and 12<z[1]<52):
                for q,r in holes.query(bounds(z,z,args.mcu_via_spacing)):
                    if r<=.16 and math.dist(z,q)<args.mcu_via_spacing:return False
            if any(x<=z[0]<=u and y<=z[1]<=v for x,y,u,v in keepouts):return False
            for q,r in holes.query(bounds(z,z,.8)):
                if math.dist(z,q)<r+.405:return False
        for item in copper.query(bounds(a,z,.6)):
            kind,n,*data=item
            if n==net:continue
            if kind=='pad':
                box,front,through=data
                if via and rectangle_distance(z,z,box)<.505:return False
                if front and rectangle_distance(a,z,box)<.305:return False
            else:
                s,t,r,front,all_layers=data
                if via and all_layers and point_distance(z,s,t)<r+.505:return False
                if front and segment_distance(a,z,s,t)<r+.305:return False
        return True
    def outward(pad,a,z):
        if getattr(args,'mcu_inward_only',False) and pad.GetParentFootprint().GetReference()=='U11':
            center=xy(pad.GetParentFootprint().GetPosition());vx=a[0]-center[0];vy=a[1]-center[1]
            inside=abs(z[0]-center[0])<=4.25 and abs(z[1]-center[1])<=4.25
            depth=(z[0]-a[0])*(1 if vx>0 else -1) if abs(vx)>abs(vy) else (z[1]-a[1])*(1 if vy>0 else -1)
            return inside and depth<=-2.5
        if not getattr(args,'mcu_outward_only',False) or pad.GetParentFootprint().GetReference()!='U11':return True
        center=xy(pad.GetParentFootprint().GetPosition());vx=a[0]-center[0];vy=a[1]-center[1]
        return (z[0]-a[0])*(1 if vx>0 else -1)>=.7 if abs(vx)>abs(vy) else (z[1]-a[1])*(1 if vy>0 else -1)>=.7
    ground_targets=Index()
    if args.join_ground_targets:
        anchor=next(pad for f in b.GetFootprints() if f.GetReference()=='C1' for pad in f.Pads() if pad.GetNetname()=='GND')
        main_ids={x.m_Uuid.AsString() for x in c.GetConnectedItems(anchor)}|{anchor.m_Uuid.AsString()}
        for item in [x for f in b.GetFootprints() for x in f.Pads()]+list(b.GetTracks()):
            if item.m_Uuid.AsString() in main_ids and (isinstance(item,p.PCB_VIA) or isinstance(item,p.PAD) and item.IsOnLayer(p.F_Cu)):
                q=xy(item.GetPosition());ground_targets.add(bounds(q,q,.1),q)
    added=[];skipped=[];jobs=[]
    for net,pads in sorted(pad_nets.items()):
        if net in POWER or (net=='GND' and not args.include_ground) or len(pads)<2:continue
        if args.net and net not in args.net:continue
        remaining={x.m_Uuid.AsString():x for x in pads};groups=[]
        while remaining:
            uid,pad=next(iter(remaining.items()))
            linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(pad)}|{uid}
            group=[remaining.pop(k) for k in list(remaining) if k in linked]
            groups.append((group,linked))
        if len(groups)<2:continue
        if getattr(args,'join_existing_net',False):
            main_group,main_ids=max(groups,key=lambda item:len(item[0]))
            ground_targets=Index()
            for item in [x for f in b.GetFootprints() for x in f.Pads()]+list(b.GetTracks()):
                if item.m_Uuid.AsString() in main_ids and (isinstance(item,p.PCB_VIA) or isinstance(item,p.PAD) and item.IsOnLayer(escape_layer)):
                    q=xy(item.GetPosition());ground_targets.add(bounds(q,q,.1),q)
        for group,linked in groups:
            if getattr(args,'only_mcu_clusters',False) and not any(x.GetParentFootprint().GetReference()=='U11' for x in group):continue
            if getattr(args,'join_existing_net',False) and linked&main_ids:continue
            if not args.extra_escapes and not getattr(args,'join_existing_net',False) and (linked&via_ids or any(x.GetAttribute()!=p.PAD_ATTRIB_SMD for x in group)):continue
            jobs.append((net,group,linked,ground_targets))
    def job_key(job):
        pins=[int(x.GetNumber()) for x in job[1] if x.GetParentFootprint().GetReference()=='U11']
        return (0,min(pins)) if pins else (1,job[0])
    for net,group,linked,ground_targets in sorted(jobs,key=job_key):
        found=None;existing_target=False
        origins=[(pad,xy(pad.GetPosition())) for pad in group if pad.IsOnLayer(escape_layer)]
        if escape_layer!=p.F_Cu or getattr(args,'join_existing_net',False):
            origins.extend((group[0],xy(t.GetPosition())) for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in linked)
        for pad,a in origins:
            mcu_origin=pad.GetParentFootprint().GetReference()=='U11'
            if mcu_origin and getattr(args,'mcu_outward_only',False) and escape_layer==p.F_Cu:
                center=xy(pad.GetParentFootprint().GetPosition());dx=a[0]-center[0];dy=a[1]-center[1]
                normal=(1 if dx>0 else -1,0) if abs(dx)>abs(dy) else (0,1 if dy>0 else -1)
                tangent=(0,1) if normal[0] else (1,0);offset=dy if normal[0] else dx
                slope=max(-.65,min(.65,.65*offset/3.75))
                mid=(a[0]+normal[0]*1.1,a[1]+normal[1]*1.1)
                if safe(net,a,mid,False):
                    for depth in [3.,4.5,6.,7.5,9.,10.5,12.]:
                        z=(a[0]+normal[0]*depth+tangent[0]*(depth-1.1)*slope,a[1]+normal[1]*depth+tangent[1]*(depth-1.1)*slope)
                        if safe(net,mid,z,True):found=(pad,[a,mid,z]);break
            for radius in ([8.,12.,18.,24.,30.,36.] if escape_layer==p.In1_Cu else [.9,1.3,1.8,2.3,3.,4.,5.,6.]):
                if found:break
                if getattr(args,'join_existing_net',False):break
                if radius<args.minimum_reach:continue
                directions=[(radius,0),(-radius,0),(0,radius),(0,-radius),(radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)]
                if pad.GetParentFootprint().GetReference()=='U11':
                    center=xy(pad.GetParentFootprint().GetPosition());vx=a[0]-center[0];vy=a[1]-center[1]
                    directions.sort(key=lambda q:-(q[0]*vx+q[1]*vy)/math.hypot(*q))
                for dx,dy in directions:
                    z=a[0]+dx,a[1]+dy
                    if outward(pad,a,z) and safe(net,a,z,True):found=(pad,[a,z]);break
                if found:break
            if not found:
                for r1 in [.35,.6,.9,1.3]:
                    if getattr(args,'join_existing_net',False):break
                    for dx,dy in [(r1,0),(-r1,0),(0,r1),(0,-r1)]:
                        mid=a[0]+dx,a[1]+dy
                        if not safe(net,a,mid,False):continue
                        for r2 in [1.,1.5,2.,3.,4.,5.]:
                            for ex,ey in [(r2,0),(-r2,0),(0,r2),(0,-r2)]:
                                z=mid[0]+ex,mid[1]+ey
                                if math.dist(a,z)>=args.minimum_reach and outward(pad,a,z) and safe(net,mid,z,True):found=(pad,[a,mid,z]);break
                            if found:break
                        if found:break
                    if found:break
            if not found and args.maze:
                # Local 0.10 mm escape search around fixed copper. This
                # only creates short front escapes, never a board-wide
                # substitute for routing/return-path review.
                step=args.maze_step;queue=[(0.,(0,0))];cost={(0,0):0.};previous={};goal=None;ground_end=None
                def position(node):return a[0]+node[0]*step,a[1]+node[1]*step
                while queue:
                    distance,node=heapq.heappop(queue)
                    if distance>cost[node]+1e-9:continue
                    q=position(node)
                    if args.join_ground_targets and net=='GND' or getattr(args,'join_existing_net',False):
                        for target in ground_targets.query(bounds(q,q,.1)):
                            if math.dist(q,target)<=.1 and safe(net,q,target,False):goal=node;ground_end=target;existing_target=True;break
                        if goal is not None:break
                    if not getattr(args,'join_existing_net',False) and math.dist(a,q)>=args.minimum_reach and outward(pad,a,q) and safe(net,q,q,True):goal=node;break
                    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
                        next_node=node[0]+dx,node[1]+dy
                        if max(abs(next_node[0]),abs(next_node[1]))>math.ceil(args.maze_radius/step):continue
                        new_cost=distance+step*math.hypot(dx,dy)
                        if new_cost>=cost.get(next_node,math.inf):continue
                        z=position(next_node)
                        if not safe(net,q,z,False):continue
                        cost[next_node]=new_cost;previous[next_node]=node
                        heapq.heappush(queue,(new_cost,next_node))
                if goal is not None:
                    nodes=[goal]
                    while nodes[-1]!=(0,0):nodes.append(previous[nodes[-1]])
                    nodes.reverse();path=[position(nodes[0])]
                    for i in range(1,len(nodes)-1):
                        before=(nodes[i][0]-nodes[i-1][0],nodes[i][1]-nodes[i-1][1])
                        after=(nodes[i+1][0]-nodes[i][0],nodes[i+1][1]-nodes[i][1])
                        if before!=after:path.append(position(nodes[i]))
                    path.append(position(nodes[-1]))
                    if ground_end:path.append(ground_end)
                    found=(pad,path)
            if found:break
        if not found:
            skipped.append({'net':net,'pads':[(x.GetParentFootprint().GetReference(),x.GetNumber()) for x in group]});continue
        pad,path=found
        for a,z in zip(path,path[1:]):
            t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetLayer(escape_layer);t.SetWidth(mm(.2));t.SetNet(b.FindNet(net));t.SetLocked(True);b.Add(t);add_copper(t)
        if not existing_target:
            v=p.PCB_VIA(b);v.SetPosition(pt(*path[-1]));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(b.FindNet(net));v.SetLocked(True);b.Add(v);add_copper(v)
        added.append({'net':net,'ref':pad.GetParentFootprint().GetReference(),'pin':pad.GetNumber(),'path_mm':path})
        if len(added)%20==0:print('Signal escapes added:',len(added),flush=True)

    p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();c.RecalculateRatsnest()
    out=ROOT/args.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
    for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
    result={'added':added,'skipped':skipped,'native_unconnected':c.GetUnconnectedCount(False)}
    out.with_suffix('.fanout.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('Signal cluster escapes:',len(added),'skipped:',len(skipped),'native unconnected:',result['native_unconnected'])


if __name__=='__main__':main()
