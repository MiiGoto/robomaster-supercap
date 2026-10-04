"""Add a local top-side power return, not a finished high-current layout."""
import pcbnew as p
from build_rev_a_pcb import K
from prepare_rev_a_routing import zone
if __name__=='__main__':
 b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'))
 if any(z.GetLayer()==p.F_Cu and not z.GetIsRuleArea() for z in b.Zones()):
  raise SystemExit('Top-side zone already exists; review before altering it')
 zone(b,'GND',p.F_Cu,(22,20,116,92))
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 p.SaveBoard(str(K/'robomaster_supercap.kicad_pcb'),b)
 print('Added local F.Cu power return; review current necks and switch coupling')
