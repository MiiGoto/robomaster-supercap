"""Export signal-only continuation after fixed power/GND paths are connected."""
import argparse,re
import pcbnew as p
from build_rev_a_pcb import ROOT,POWER
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('output');a=ap.parse_args()
b=p.LoadBoard(str(ROOT/a.source));b.BuildConnectivity();c=b.GetConnectivity()
for net in POWER|{'GND'}:
 pads=[x for f in b.GetFootprints() for x in f.Pads() if x.GetNetname()==net]
 if not pads:continue
 linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(pads[0])}|{pads[0].m_Uuid.AsString()}
 assert all(x.m_Uuid.AsString() in linked for x in pads),'Cannot exclude unconnected net '+net
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True)
assert p.ExportSpecctraDSN(b,str(out));s=out.read_text(encoding='utf8')
i=s.index('(plane GND (polygon F.Cu');depth=0
for j in range(i,len(s)):
 if s[j]=='(':depth+=1
 if s[j]==')':depth-=1
 if depth==0:break
s=s[:i]+s[j+1:]
s=s.replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)')
s=s.replace('(width 250)','(width 200)').replace('(clearance 50 (type smd_smd))','(clearance 150 (type smd_smd))')
start=s.index('(class kicad_default');end=s.index('(circuit',start);head=s[start:end]
aux={'V3V3','V12_DRIVER','ACTUATOR_12V'}
for n in POWER|aux|{'GND'}:head=re.sub(r'(?<![\w])'+re.escape(n)+r'(?![\w])','',head)
s=s[:start]+head+s[end:]
extra='\n(class FIXED_POWER '+' '.join(sorted(POWER))+' (rule (width 200) (clearance 200)))'
extra+='\n(class GND_PLANE GND (rule (width 200) (clearance 200)))'
extra+='\n(class AUX '+' '.join(sorted(aux))+' (circuit (use_via "Via[0-3]_600:300_um")) (rule (width 700) (clearance 200)))\n'
at=s.index('  (wiring');before=s[:at];last=before.rfind('  )');s=before[:last]+extra+before[last:]+s[at:]
out.write_text(s,encoding='utf8');print('Excluded nets independently connected; In1 reserved for GND; signal continuation exported')
