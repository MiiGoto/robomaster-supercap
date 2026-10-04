"""Reproducible bench PCB placement; run with KiCad's bundled Python.

Library footprints are used under KiCad's library exception. No vendor PCB is
copied. Only this script's generated PCB may be rebuilt with --rebuild.
The user's project settings are neither read back into nor written by this tool.
"""
from pathlib import Path
import json, math, uuid, argparse
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
K=ROOT/'hardware/kicad'
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
NS=uuid.UUID('b2b13ce0-d767-49a4-82e9-164ea247930b')
def uid(s): return str(uuid.uuid5(NS,s))
def mm(x): return p.FromMM(x)
def pt(x,y): return p.VECTOR2I(mm(x),mm(y))
def xy(a): return p.ToMM(a.x),p.ToMM(a.y)
POWER={'BUS_LINK','BUS_LINK_IN','CAP_LINK','CAP_LINK_IN','SW_NODE_A','SW_NODE_B','IL_TO_L'}
REGIONS={
 'POWER_STAGE':(20,20,100,85),'GATE_DRIVER':(20,95,95,55),
 'CURRENT_SENSING':(125,20,45,50),'CONTROLLER':(175,20,40,50),
 'SUPERCAP_BANK':(220,20,85,55),'SAFETY':(120,80,90,80),
 'VOLTAGE_SENSING':(215,80,90,75),'TEMPERATURE_SENSING':(215,165,40,45),
 'AUXILIARY_POWER':(20,160,95,55),'PRECHARGE':(120,165,45,60),
 'SAFE_DISCHARGE':(170,170,40,55),'CAN':(270,165,35,40),
 'POWER_INPUT':(20,220,90,20)}
FIXED={'Q12':(45,65),'Q13':(45,78),'Q14':(85,65),'Q15':(85,78),
 'L1':(65,70),'R35':(55,59),'R33':(30,57),'R34':(108,57),
 'C7':(38,60),'C8':(38,84),'C15':(92,60),'C16':(92,84),
 'U5':(43,71.5),'U6':(83,71.5)}
FIXED.update({'R36':(39,65),'D5':(35.5,65),'R37':(39,78),'D6':(35.5,78),
 'R38':(79,65),'D7':(75.5,65),'R39':(79,78),'D8':(75.5,78),
 'R42':(39,68),'R44':(39,81),'R48':(79,68),'R50':(79,81),
 'C19':(47,69),'C20':(49.5,72),'C21':(49.5,75),
 'C22':(87,69),'C23':(89.5,72),'C24':(89.5,75),
 'U12':(27,70),'U13':(27,76),'U14':(27,80),
 'U15':(109,70),'U16':(109,76),'U17':(109,80),
 'U18':(57,82),'U19':(56,87),'U20':(61,87)})
for i in range(6):
 FIXED['C'+str(i+1)]=(30+(i%3)*14,28+(i//3)*14)
 FIXED['C'+str(i+9)]=(80+(i%3)*14,28+(i//3)*14)

def box(fp,x=0,y=0):
 # Courtyard gives body/pad courtyard extents rather than long value texts.
 rect=fp.GetBoundingBox(False,False)
 w,h=max(p.ToMM(rect.GetWidth()),2.5),max(p.ToMM(rect.GetHeight()),2.5)
 return (x-w/2-.6,y-h/2-.6,x+w/2+.6,y+h/2+.6)
def overlap(a,b): return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def build(rebuild=False):
 dest=K/'robomaster_supercap.kicad_pcb'
 old=p.LoadBoard(str(dest))
 if old.GetFootprints() and not rebuild:
  raise SystemExit('Existing PCB has placement. Refusing overwrite without --rebuild.')
 b=p.BOARD();b.SetCopperLayerCount(4)
 settings=b.GetDesignSettings()
 settings.m_MinClearance=mm(.2);settings.m_TrackMinWidth=mm(.2)
 settings.m_ViasMinSize=mm(.6);settings.m_ViasMinAnnularWidth=mm(.15)
 settings.m_CopperEdgeClearance=mm(.5)
 nc=settings.m_NetSettings.GetDefaultNetclass()
 nc.SetClearance(mm(.2));nc.SetTrackWidth(mm(.25));nc.SetViaDiameter(mm(.6));nc.SetViaDrill(mm(.3))
 items=json.loads((ROOT/'simulation/rev_a_connectivity.json').read_text(encoding='utf8'))
 names=sorted({n for a in items if a['fp'] for n in a['nets'].values() if n})
 nets={}
 for i,n in enumerate(names,1):
  ni=p.NETINFO_ITEM(b,n,i);b.Add(ni);nets[n]=ni
 placed={}; data={};occupied=[]
 root=uid('unused')
 import re
 root=re.search(r'\(uuid "([^"]+)"\)',(K/'robomaster_supercap.kicad_sch').read_text(encoding='utf8')).group(1)
 for a in items:
  if not a['fp']:continue
  lib,name=a['fp'].split(':')
  f=p.FootprintLoad(str(LIB/(lib+'.pretty')),name)
  if not f:raise RuntimeError('Missing '+a['fp'])
  f.SetReference(a['ref']);f.SetValue(a['value']);f.SetField('MPN',a['mpn'])
  f.SetFPID(p.LIB_ID(lib,name));f.SetPath(p.KIID_PATH('/'+root+'/'+uid('sheet:'+a['sheet'])+'/'+uid('component:'+a['ref'])))
  f.Value().SetVisible(False);f.Reference().SetLayer(p.F_Fab);f.Reference().SetTextSize(pt(.8,.8));f.Reference().SetTextThickness(mm(.12))
  for pad in f.Pads():
   if pad.GetAttribute()==p.PAD_ATTRIB_SMD:pad.SetLocalSolderMaskMargin(0)
   n=a['nets'].get(pad.GetNumber())
   if n:pad.SetNet(nets[n])
  b.Add(f);placed[a['ref']]=f;data[a['ref']]=a
 def put(ref,x,y):
  f=placed[ref];f.SetPosition(pt(x,y));f.Reference().SetPosition(pt(x,y-2.8))
  occupied.append(box(f,x,y))
 # Fixed critical devices first. Remaining parts are placed without courtyard
 # overlap, near connected devices within their functional region.
 for ref,pos in FIXED.items():put(ref,*pos)
 rest=[a for a in items if a['fp'] and a['ref'] not in FIXED]
 # Harness land positions reflect matching block, not a falsely common bus.
 boundary=[a for a in rest if a['sheet']=='PCB_INTERFACE']
 for i,a in enumerate(boundary):put(a['ref'],10 if i<16 else 315,18+(i%16)*13)
 rest=[a for a in rest if a['sheet']!='PCB_INTERFACE']
 rest.sort(key=lambda a:(a['sheet'],0 if a['ref'].startswith(('U','Q','L','J')) else 1,int(re.sub('[^0-9]','',a['ref']))))
 local={}
 for a in rest:
  x0,y0,w,h=REGIONS[a['sheet']];f=placed[a['ref']]
  related=[xy(placed[z].GetPosition()) for z in local.get(a['sheet'],[]) if
           (set(a['nets'].values()) & set(data[z]['nets'].values()))-{'GND','V3V3','V12_DRIVER',None}]
  target=related[-1] if related else (x0+w/2,y0+h/2)
  ext=box(f)
  nearby=[o for o in occupied if overlap((x0,y0,x0+w,y0+h),o)]
  candidates=[]
  for yy in range(int(y0*2),int((y0+h)*2),2):
   for xx in range(int(x0*2),int((x0+w)*2),2):
    x,y=xx/2,yy/2;bb=(x+ext[0],y+ext[1],x+ext[2],y+ext[3])
    if bb[0]<x0 or bb[1]<y0 or bb[2]>x0+w or bb[3]>y0+h:continue
    if any(overlap(bb,o) for o in nearby):continue
    candidates.append(((x-target[0])**2+(y-target[1])**2,x,y))
  if not candidates:raise RuntimeError('No collision-free position: '+a['ref'])
  _,x,y=min(candidates);put(a['ref'],x,y);local.setdefault(a['sheet'],[]).append(a['ref'])
 # Edge rectangle, four mounting holes, explicit prototype identifier.
 for start,end in [((5,5),(320,5)),((320,5),(320,240)),((320,240),(5,240)),((5,240),(5,5))]:
  s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*start));s.SetEnd(pt(*end));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
 for i,pos in enumerate([(10,10),(315,10),(10,235),(315,235)],1):
  f=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3');f.SetReference('H'+str(i));f.SetPosition(pt(*pos));b.Add(f)
 text=p.PCB_TEXT(b);text.SetText('REV A BENCH PROTOTYPE / NOT RELEASED');text.SetPosition(pt(160,232));text.SetLayer(p.F_SilkS);text.SetTextSize(pt(1.5,1.5));b.Add(text)
 # A separate power-width target is used when exporting for routing. Pad necks
 # and current-carrying geometry require review even when DRC passes.
 b.BuildConnectivity()
 p.SaveBoard(str(dest),b)
 (ROOT/'.local/pcb_placement.json').write_text(json.dumps({r:list(xy(f.GetPosition())) for r,f in placed.items()},indent=2),encoding='utf8')
 print('Placed',len(placed),'electrical footprints +4 mounting holes; board315x235mm,4 copper layers')
 return b
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--rebuild',action='store_true');args=ap.parse_args()
 b=build(args.rebuild)
 print('DSN export',p.ExportSpecctraDSN(b,str(ROOT/'.local/rev_a_pcb.dsn')))
