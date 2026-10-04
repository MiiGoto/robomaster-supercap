"""Import offline Specctra routes and refill the existing board's ground plane."""
import argparse
import pcbnew as p
from build_rev_a_pcb import ROOT,K
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('session',nargs='?',default='.local/rev_a_pcb.ses');a=ap.parse_args()
 path=ROOT/a.session
 if not path.is_file():raise SystemExit('No session file; refusing to claim routed PCB')
 b=p.LoadBoard(str(K/'robomaster_supercap.kicad_pcb'))
 if list(b.GetTracks()):raise SystemExit('Existing routes: refusing to overwrite without review')
 if not p.ImportSpecctraSES(b,str(path)):raise SystemExit('Specctra import failed')
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 p.SaveBoard(str(K/'robomaster_supercap.kicad_pcb'),b)
 print('Imported',len(list(b.GetTracks())),'track/via objects; DRC must follow')
