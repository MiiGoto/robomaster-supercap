"""Resolve two individually reviewed copper tails in a routing candidate.

No exclusions or DRC overrides. Preserve all native pad connectivity;
require fresh full DRC after saving. Coordinates identify the reviewed
geometry rather than relying on regenerated UUIDs.
"""
import argparse,shutil,math
import pcbnew as p
from build_rev_a_pcb import ROOT,K,pt
from widen_rev_a_auxiliary_routes import xy
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));changes=[]
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):continue
 s,z=xy(t.GetStart()),xy(t.GetEnd())
 if t.GetNetname()=='SW_NODE_B' and math.dist(s,(80.5,72.5))<.00001 and math.dist(z,(79.5,73.5))<.00001:
  # Relocated via already lies inside the retained broad switch-node path.
  # This thin diagonal continues to the removed via's original location.
  assert p.ToMM(t.GetWidth())<=.2+1e-6;b.Delete(t);changes.append('removed obsolete SW_NODE_B via-relocation tail');continue
 if t.GetNetname()=='PWM_BH_SAFE' and math.dist(s,(67.45,117.475))<.00001 and math.dist(z,(67.45,116.675))<.00001:
  # Stop exactly at the existing diagonal's endpoint instead of extending
  # beyond its copper contact; retain the hardware-gated PWM connection.
  t.SetEnd(pt(67.4666,116.994));changes.append('trimmed PWM_BH_SAFE to retained diagonal endpoint')
p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();b.GetConnectivity().RecalculateRatsnest()
assert b.GetConnectivity().GetUnconnectedCount(False)==0,'Reviewed edit changed native connectivity'
out=ROOT/a.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Reviewed tails:',changes)
