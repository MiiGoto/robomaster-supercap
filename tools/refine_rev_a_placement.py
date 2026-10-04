"""Apply DRC-observed local placement fixes and exact schematic metadata."""
import json,re
import pcbnew as p
from build_rev_a_pcb import ROOT,K,uid,pt
from rev_a_parts import P
def main():
 b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'))
 data={x['ref']:x for x in json.loads((ROOT/'simulation/rev_a_connectivity.json').read_text(encoding='utf8'))}
 root_text=(K/'robomaster_supercap.kicad_sch').read_text(encoding='utf8')
 root=re.search(r'\(uuid "([^"]+)"\)',root_text).group(1)
 sheetids={name:id for id,name in re.findall(r'\(uuid "([^"]+)"\)\s*\(property "Sheetname" "([^"]+)"',root_text)}
 moves={'D5':(34.5,65),'D6':(34.5,78),'D7':(74.5,65),'D8':(74.5,78),
        'D7':(74.5,58),'D8':(74.5,84),
        'C21':(51,75),'C24':(91,75),'C43':(190,55)}
 for f in b.GetFootprints():
  ref=f.GetReference()
  if ref.startswith('H'):
   f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
   continue
  a=data[ref];f.SetPath(p.KIID_PATH('/'+root+'/'+sheetids[a['sheet']]+'/'+uid('component:'+ref)))
  f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM & ~p.FP_EXCLUDE_FROM_POS_FILES)
  f.SetValue(a['value']);f.SetField('MPN',a['mpn']);f.SetField('Datasheet',P[a['typ']].source)
  for field in f.GetFields():
   if field.GetName() not in ['Reference']:field.SetVisible(False)
  if a['dni']:f.SetAttributes(f.GetAttributes()|p.FP_DNP)
  if ref in moves:f.SetPosition(pt(*moves[ref]))
  for pad in f.Pads():
   pin=pad.GetNumber()
   if pin not in a['nets']:continue
   name=a['nets'][pin]
   if name is None:name='unconnected-('+ref+'-'+P[a['typ']].pins[pin][0]+'-Pad'+pin+')'
   ni=b.FindNet(name)
   if not ni:
    ni=p.NETINFO_ITEM(b,name,b.GetNetCount());b.Add(ni)
   pad.SetNet(ni)
 b.BuildConnectivity();p.SaveBoard(str(K/'robomaster_supercap.kicad_pcb'),b)
 print('Schematic metadata/NC nets matched; local placement fixes applied')
if __name__=='__main__':main()
