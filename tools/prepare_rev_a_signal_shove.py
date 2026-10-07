"""Allow signal-layer rerouting while preserving power, ground and SMD escapes."""
import argparse,math,shutil
import pcbnew as p
from build_rev_a_pcb import ROOT,K,POWER
from widen_rev_a_auxiliary_routes import xy,point_distance
from fanout_rev_a_signals import rectangle_distance
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');ap.add_argument('--fanout-baseline');ap.add_argument('--release-mcu-fanout',action='store_true');a=ap.parse_args()
original=None
if a.fanout_baseline:
 base=p.LoadBoard(str(ROOT/a.fanout_baseline));original={t.m_Uuid.AsString() for t in base.GetTracks()}
b=p.LoadBoard(str(ROOT/a.source));front=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu and (original is None or t.m_Uuid.AsString() in original)]
mcu_nets={pad.GetNetname() for f in b.GetFootprints() if f.GetReference()=='U11' for pad in f.Pads() if pad.GetNetCode()}
for t in b.GetTracks():
 fixed=t.GetNetname() in POWER|{'GND'}
 if isinstance(t,p.PCB_VIA):
  q=xy(t.GetPosition());fixed|=any(x.GetNetname()==t.GetNetname() and point_distance(q,xy(x.GetStart()),xy(x.GetEnd()))<.3 for x in front)
 else:fixed|=t.GetLayer()==p.F_Cu and (original is None or t.m_Uuid.AsString() in original)
 if getattr(a,'release_mcu_fanout',False) and t.GetNetname() in mcu_nets-POWER-{'GND'}:
  if isinstance(t,p.PCB_VIA):q=xy(t.GetPosition());local=172<q[0]<207 and 16<q[1]<58
  else:local=rectangle_distance(xy(t.GetStart()),xy(t.GetEnd()),(172,16,207,58))<.7
  if local:fixed=False
 t.SetLocked(fixed)
out=ROOT/a.output;assert out!=K/'robomaster_supercap.kicad_pcb';out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(K/('robomaster_supercap'+ext),out.with_suffix(ext))
print('Signal-layer shove candidate prepared')
