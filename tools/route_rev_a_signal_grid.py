"""Join physical signal clusters on F/In2/B using native geometry.

Never route on In1 or modify existing power/GND. Candidate output only;
native DRC/connectivity, not the grid search, establish acceptance.
"""
import argparse, collections, heapq, math, shutil, struct, subprocess, json
import numpy as np
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER,pt,mm
from widen_rev_a_auxiliary_routes import xy,segment_distance
from fanout_rev_a_signals import rectangle_distance

STEP=.1;NX=3201;NY=2401;MULTI=65535
AUX={'V3V3','V12_DRIVER','ACTUATOR_12V'}


def main():
    global STEP,NX,NY
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');ap.add_argument('--max-nodes',type=int,default=250000);ap.add_argument('--java-search',action='store_true');ap.add_argument('--priority-net',action='append',default=[]);ap.add_argument('--allow-signal-ripup',action='store_true');ap.add_argument('--sweeps',type=int,default=1);ap.add_argument('--local-signal-ripup',action='store_true');ap.add_argument('--grid-step',type=float,choices=[.05,.1],default=.1);args=ap.parse_args()
    STEP=args.grid_step;NX=round(320/STEP)+1;NY=round(240/STEP)+1
    b=p.LoadBoard(str(ROOT/args.source));b.BuildConnectivity();c=b.GetConnectivity()
    out=ROOT/args.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True)
    for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
    worker=None
    if args.java_search:
        worker=subprocess.Popen([str(ROOT/'.local/pcb-tools/jre/jdk-25.0.4.1+1-jre/bin/java.exe'),'-Xmx3g' if STEP<.1 else '-Xmx1g',f'-Dgrid.nx={NX}',f'-Dgrid.ny={NY}','-cp',str(ROOT/'.local/pcb-tools/grid_classes'),'RevAGridSearch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    maps={layer:np.zeros((NY,NX),dtype=np.uint16) for layer in [p.In2_Cu,p.B_Cu,p.F_Cu]}
    maps[-1]=np.zeros((NY,NX),dtype=np.uint16) # all-layer through-via exclusion map
    maps[-2]=np.zeros((NY,NX),dtype=np.uint16);maps[-3]=np.zeros((NY,NX),dtype=np.uint16)
    def stamp(layer,net,a,z,r,rectangle=False):
        image=maps[layer]
        x0=max(0,math.floor((min(a[0],z[0])-r)/STEP));x1=min(NX-1,math.ceil((max(a[0],z[0])+r)/STEP))
        y0=max(0,math.floor((min(a[1],z[1])-r)/STEP));y1=min(NY-1,math.ceil((max(a[1],z[1])+r)/STEP))
        if x1<x0 or y1<y0:return
        yy,xx=np.ogrid[y0:y1+1,x0:x1+1];xx=xx*STEP;yy=yy*STEP
        if rectangle:
            mask=(xx>=min(a[0],z[0])-r)&(xx<=max(a[0],z[0])+r)&(yy>=min(a[1],z[1])-r)&(yy<=max(a[1],z[1])+r)
        else:
            dx=z[0]-a[0];dy=z[1]-a[1];dd=dx*dx+dy*dy
            t=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/dd,0,1) if dd else 0
            mask=(xx-a[0]-t*dx)**2+(yy-a[1]-t*dy)**2 <= r*r
        crop=image[y0:y1+1,x0:x1+1];collision=mask&(crop!=0)&(crop!=net)
        crop[mask&(crop==0)]=net;crop[collision]=MULTI
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:
                q=xy(pad.GetPosition());radius=max(xy(pad.GetDrillSize()))/2+.37
                for layer in maps:stamp(layer,MULTI,q,q,radius)
            # New holes in component lands require a separate fabrication
            # decision. Reuse existing vias; do not create via-in-pad routes.
            bb=pad.GetBoundingBox();stamp(-1,MULTI,xy(bb.GetPosition()),xy(bb.GetEnd()),.52,True)
            if pad.GetAttribute()!=p.PAD_ATTRIB_SMD:
                q=xy(pad.GetPosition());radius=max(xy(pad.GetDrillSize()))/2+.42
                stamp(-1,MULTI,q,q,radius)
            for layer in [p.In2_Cu,p.B_Cu,p.F_Cu]:
                if pad.IsOnLayer(layer):
                    bb=pad.GetBoundingBox();stamp(layer,pad.GetNetCode() or MULTI,xy(bb.GetPosition()),xy(bb.GetEnd()),.32,True)
    def stamp_track(t,soft=False):
        net=t.GetNetCode() or MULTI
        if isinstance(t,p.PCB_VIA):
            for layer in [p.In2_Cu,p.B_Cu,p.F_Cu]:stamp(layer,net,xy(t.GetPosition()),xy(t.GetPosition()),p.ToMM(t.GetWidth(p.F_Cu))/2+.32)
            stamp(-1,net,xy(t.GetPosition()),xy(t.GetPosition()),p.ToMM(t.GetWidth(p.F_Cu))/2+.52)
            stamp(-1,MULTI,xy(t.GetPosition()),xy(t.GetPosition()),p.ToMM(t.GetDrill())/2+.42)
        elif t.GetLayer() in maps:
            layer=([-2,-3][[p.In2_Cu,p.B_Cu].index(t.GetLayer())] if soft else t.GetLayer())
            stamp(layer,net,xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth())/2+.32)
        if not isinstance(t,p.PCB_VIA):stamp(-1,net,xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth())/2+.52)
    mutable_ids={t.m_Uuid.AsString() for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer() in [p.In2_Cu,p.B_Cu] and t.GetNetname() not in POWER|AUX|{'GND'} and (not getattr(args,'local_signal_ripup',False) or rectangle_distance(xy(t.GetStart()),xy(t.GetEnd()),(166,12,215,62))<.7)} if args.allow_signal_ripup else set()
    for track in b.GetTracks():stamp_track(track,track.m_Uuid.AsString() in mutable_ids)
    def freeze_net(name):
        # Preserve the complete net, including its pre-existing branches.
        # Locking only newly added bridges allowed later nets to undo them.
        for t in b.GetTracks():
            uid=t.m_Uuid.AsString()
            if uid in mutable_ids and t.GetNetname()==name:
                mutable_ids.remove(uid);t.SetLocked(True);stamp_track(t)
    existing_vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
    for via in existing_vias:
        q=xy(via.GetPosition());maps[-1][round(q[1]/STEP),round(q[0]/STEP)]=via.GetNetCode()
    for zone in b.Zones():
        if zone.GetIsRuleArea():
            bb=zone.GetBoundingBox();stamp(-1,MULTI,xy(bb.GetPosition()),xy(bb.GetEnd()),.52,True)
    for image in maps.values():
        image[:round(7/STEP),:]=MULTI;image[round(238/STEP):,:]=MULTI;image[:,:round(7/STEP)]=MULTI;image[:,round(318/STEP):]=MULTI
    # The molded LQFP body has no exposed pad. Native copper clearance,
    # rather than an artificial solid obstacle, permits local inward escapes.
    # Existing pads and copper retain their normal clearance inflation.
    for via in existing_vias:
        q=xy(via.GetPosition());maps[-1][round(q[1]/STEP),round(q[0]/STEP)]=via.GetNetCode()
    anchor_masks={}
    def register_anchor(net,q,mask):
        key=(net,*q);anchor_masks[key]=anchor_masks.get(key,0)|mask
    for via in existing_vias:register_anchor(via.GetNetCode(),xy(via.GetPosition()),7)
    layer_bits={p.In2_Cu:1,p.B_Cu:2,p.F_Cu:4}
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetCode():register_anchor(pad.GetNetCode(),xy(pad.GetPosition()),sum(bit for layer,bit in layer_bits.items() if pad.IsOnLayer(layer)))
    def search(layer,net,a,z):
        image=maps[layer];start=(round(a[0]/STEP),round(a[1]/STEP));end=(round(z[0]/STEP),round(z[1]/STEP))
        def free(q):return 0<=q[0]<NX and 0<=q[1]<NY and image[q[1],q[0]] in (0,net)
        if worker:
            worker.stdin.write(struct.pack('>8i',net,*start,*end,args.max_nodes,anchor_masks.get((net,*a),7),anchor_masks.get((net,*z),7)))
            for routing_layer in [p.In2_Cu,p.B_Cu,p.F_Cu,-1,-2,-3]:worker.stdin.write(maps[routing_layer].tobytes())
            worker.stdin.flush()
            length=struct.unpack('>i',worker.stdout.read(4))[0]
            if not length:return None
            data=bytearray()
            while len(data)<length*4:data.extend(worker.stdout.read(length*4-len(data)))
            indices=struct.unpack('>'+str(length)+'i',data);path=[((i%(NX*NY))%NX,(i%(NX*NY))//NX,[p.In2_Cu,p.B_Cu,p.F_Cu][i//(NX*NY)]) for i in indices]
            points=[(*a,path[0][2]),(path[0][0]*STEP,path[0][1]*STEP,path[0][2])]
            for i in range(1,len(path)-1):
                before=(path[i][0]-path[i-1][0],path[i][1]-path[i-1][1]);after=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1])
                if before!=after or path[i-1][2]!=path[i][2] or path[i][2]!=path[i+1][2]:points.append((path[i][0]*STEP,path[i][1]*STEP,path[i][2]))
            points.extend([(path[-1][0]*STEP,path[-1][1]*STEP,path[-1][2]),(*z,path[-1][2])]);return points
        if not free(start) or not free(end):return None
        def heuristic(q):
            dx=abs(q[0]-end[0]);dy=abs(q[1]-end[1]);return max(dx,dy)+(math.sqrt(2)-1)*min(dx,dy)
        queue=[(heuristic(start),0.,start)];cost={start:0.};previous={};visited=0
        while queue:
            _,g,q=heapq.heappop(queue)
            if g>cost[q]+1e-9:continue
            if q==end:
                path=[q]
                while path[-1]!=start:path.append(previous[path[-1]])
                path.reverse();points=[a,(path[0][0]*STEP,path[0][1]*STEP)]
                for i in range(1,len(path)-1):
                    before=(path[i][0]-path[i-1][0],path[i][1]-path[i-1][1]);after=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1])
                    if before!=after:points.append((path[i][0]*STEP,path[i][1]*STEP))
                points.extend([(path[-1][0]*STEP,path[-1][1]*STEP),z]);return points
            visited+=1
            if visited>args.max_nodes:return None
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
                nq=q[0]+dx,q[1]+dy
                if not free(nq):continue
                if dx and dy and (not free((q[0]+dx,q[1])) or not free((q[0],q[1]+dy))):continue
                ng=g+math.hypot(dx,dy)
                if ng>=cost.get(nq,math.inf):continue
                cost[nq]=ng;previous[nq]=q;heapq.heappush(queue,(ng+heuristic(nq),ng,nq))
        return None
    pads_by_net=collections.defaultdict(list)
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetCode():pads_by_net[pad.GetNetname()].append(pad)
    via_map={t.m_Uuid.AsString():xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)}
    routed=0;failed=[];diagnostics=[];connection_dirty=False
    for sweep in range(args.sweeps):
        failed=[];diagnostics=[]
        via_map={t.m_Uuid.AsString():xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)}
        priority={name:i for i,name in enumerate(args.priority_net)}
        for name,pads in sorted(pads_by_net.items(),key=lambda item:(priority.get(item[0],len(priority)),item[0])):
            if name in POWER|{'GND'} or len(pads)<2:continue
            if connection_dirty:
                b.BuildConnectivity();c=b.GetConnectivity();connection_dirty=False
            remaining={x.m_Uuid.AsString():x for x in pads};groups=[]
            while remaining:
                uid,anchor=next(iter(remaining.items()));linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(anchor)}|{uid}
                group=[remaining.pop(k) for k in list(remaining) if k in linked]
                points=[via_map[k] for k in linked if k in via_map]
                points.extend(xy(x.GetPosition()) for x in group)
                if any(x.GetParentFootprint().GetReference()=='U11' for x in group):
                    for t in b.GetTracks():
                        if isinstance(t,p.PCB_VIA) or t.GetLayer() not in layer_bits or t.m_Uuid.AsString() not in linked:continue
                        for q in [xy(t.GetStart()),xy(t.GetEnd())]:
                            if 168<q[0]<208 and 12<q[1]<58:
                                register_anchor(t.GetNetCode(),q,layer_bits[t.GetLayer()]);points.append(q)
                points=list(dict.fromkeys(points))
                if len(group)==1 and group[0].GetParentFootprint().GetReference()=='U11':
                    outside=[q for q in points if not (166<q[0]<215 and 12<q[1]<62)]
                    if outside:points=outside
                groups.append(points)
            if len(groups)<2:
                freeze_net(name);continue
            parent=list(range(len(groups)))
            def root(i):
                while parent[i]!=i:i=parent[i]
                return i
            edges=sorted((math.dist(a,z),i,j,a,z) for i in range(len(groups)) for j in range(i+1,len(groups)) for a in groups[i] for z in groups[j])
            tried=collections.Counter();net=pads[0].GetNetCode()
            for distance,i,j,a,z in edges:
                if root(i)==root(j) or tried[i,j]>=10:continue
                tried[i,j]+=1;path=None;layer=None
                for layer in ([p.In2_Cu] if worker else [p.In2_Cu,p.B_Cu,p.F_Cu]):
                    path=search(layer,net,a,z)
                    if not path and worker:
                        backward=search(layer,net,z,a)
                        if backward:path=list(reversed(backward))
                    if path:break
                if not path:continue
                if args.allow_signal_ripup:
                    removed=collections.Counter()
                    for t in list(b.GetTracks()):
                        if t.m_Uuid.AsString() not in mutable_ids or t.GetNetname()==name:continue
                        s,z=xy(t.GetStart()),xy(t.GetEnd());radius=p.ToMM(t.GetWidth())/2+.32
                        if any(x[2]==y[2]==t.GetLayer() and segment_distance(x[:2],y[:2],s,z)<radius for x,y in zip(path,path[1:])):
                            mutable_ids.remove(t.m_Uuid.AsString());removed[t.GetNetname()]+=1;b.Delete(t)
                    if removed:print('Corridor ripup for',name,dict(removed),flush=True)
                for x,y in zip(path,path[1:]):
                    if worker and x[2]!=y[2]:
                        assert math.dist(x[:2],y[:2])<1e-6
                        if any(v.GetNetname()==name and math.dist(x[:2],xy(v.GetPosition()))<.075 for v in existing_vias):continue
                        t=p.PCB_VIA(b);t.SetPosition(pt(*x[:2]));t.SetWidth(mm(.6));t.SetDrill(mm(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH)
                    else:
                        if math.dist(x[:2],y[:2])<1e-6:continue
                        t=p.PCB_TRACK(b);t.SetStart(pt(*x[:2]));t.SetEnd(pt(*y[:2]));t.SetWidth(mm(.2));t.SetLayer(x[2] if worker else layer)
                    t.SetNet(b.FindNet(name));t.SetLocked(True);b.Add(t);stamp_track(t)
                    if isinstance(t,p.PCB_VIA):
                        existing_vias.append(t);q=xy(t.GetPosition());maps[-1][round(q[1]/STEP),round(q[0]/STEP)]=net
                parent[root(i)]=root(j);routed+=1
                connection_dirty=True
                print('Grid joined',name,round(distance,2),'mm on',b.GetLayerName(layer),'connections',routed,flush=True)
            if len({root(i) for i in range(len(groups))})>1:
                failed.append(name)
                diagnostics.append({'net':name,'groups':[{'root':root(i),'anchors':[{'xy':q,'free_layers':[b.GetLayerName(layer) for layer in [p.In2_Cu,p.B_Cu,p.F_Cu] if maps[layer][round(q[1]/STEP),round(q[0]/STEP)] in (0,net)]} for q in points]} for i,points in enumerate(groups)]})
            else:freeze_net(name)
            p.SaveBoard(str(out),b)

    p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();c.RecalculateRatsnest()
    p.SaveBoard(str(out),b)
    for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
    print('Grid candidate:',routed,'joins; unconnected',c.GetUnconnectedCount(False),'remaining nets',failed,flush=True)
    out.with_suffix('.grid.json').write_text(json.dumps(diagnostics,indent=2)+'\n',encoding='utf8')
    if worker:worker.stdin.close();worker.wait()


if __name__=='__main__':main()
