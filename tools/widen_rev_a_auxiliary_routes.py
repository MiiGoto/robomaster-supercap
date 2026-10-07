"""Widen auxiliary traces where conservative geometry allows, candidate only.

Retain 0.20 mm fine-pitch escapes. Native DRC remains authoritative; this
does not certify ampacity, via current sharing or thermal performance.
"""
import argparse
import math
import shutil
import pcbnew as p
from build_rev_a_pcb import ROOT, K, mm

AUX = {'V3V3', 'V12_DRIVER', 'ACTUATOR_12V'}


def xy(v):
    return p.ToMM(v.x), p.ToMM(v.y)


def point_distance(q, a, z):
    dx, dy = z[0]-a[0], z[1]-a[1]
    dd = dx*dx+dy*dy
    t = max(0, min(1, ((q[0]-a[0])*dx+(q[1]-a[1])*dy)/dd)) if dd else 0
    return math.hypot(q[0]-a[0]-t*dx, q[1]-a[1]-t*dy)


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def segment_distance(a, b, c, d):
    if cross(a,b,c)*cross(a,b,d) < 0 and cross(c,d,a)*cross(c,d,b) < 0:
        return 0
    return min(point_distance(a,c,d), point_distance(b,c,d),
               point_distance(c,a,b), point_distance(d,a,b))


def box_distance(a, z, bb):
    x,y = xy(bb.GetPosition()); u,v = xy(bb.GetEnd())
    if x <= a[0] <= u and y <= a[1] <= v:
        return 0
    if x <= z[0] <= u and y <= z[1] <= v:
        return 0
    return min(segment_distance(a,z,s,t) for s,t in
               [((x,y),(u,y)),((u,y),(u,v)),((u,v),(x,v)),((x,v),(x,y))])


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('output')
    args=ap.parse_args(); b=p.LoadBoard(str(ROOT/args.source))
    pads=[x for f in b.GetFootprints() for x in f.Pads()]
    tracks=list(b.GetTracks()); changed=0; narrow=0
    for t in tracks:
        if isinstance(t,p.PCB_VIA) or t.GetNetname() not in AUX or t.GetLayer()==p.In1_Cu:
            continue
        a,z=xy(t.GetStart()),xy(t.GetEnd()); layer=t.GetLayer()
        maximum=.7
        for pad in pads:
            if pad.GetNetCode()==t.GetNetCode() or not pad.IsOnLayer(layer):
                continue
            maximum=min(maximum,2*(box_distance(a,z,pad.GetBoundingBox())-.215))
        for q in tracks:
            if q is t or q.GetNetCode()==t.GetNetCode() or not q.IsOnLayer(layer):
                continue
            if isinstance(q,p.PCB_VIA):
                distance=point_distance(xy(q.GetPosition()),a,z)
                radius=p.ToMM(q.GetWidth(p.F_Cu))/2
            else:
                distance=segment_distance(a,z,xy(q.GetStart()),xy(q.GetEnd()))
                radius=p.ToMM(q.GetWidth())/2
            maximum=min(maximum,2*(distance-radius-.215))
        width=next((w for w in [.7,.5,.4,.3] if w <= maximum),.2)
        if width > p.ToMM(t.GetWidth())+.001:
            t.SetWidth(mm(width)); changed+=1
        elif width == .2:
            narrow+=1
    p.ZONE_FILLER(b).Fill(b.Zones())
    out=ROOT/args.output
    assert out != K/'robomaster_supercap.kicad_pcb'
    out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
    for ext in ['.kicad_pro','.kicad_dru']:
        shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
    print('Auxiliary widened segments:',changed,'remaining narrow escapes:',narrow)


if __name__=='__main__':
    main()
