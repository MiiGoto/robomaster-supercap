"""User-approved 0.15mm same-package pad exception; preserve other settings.

The project hard floor must permit the exception. The custom default rule keeps
all other copper at >=0.20mm. Explicit references prevent cross-package matches.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
REFS=[7,8,29]+list(range(34,41))+list(range(43,73))
# U41/U42 are not in the observed fine-pitch pad conflict set.
REFS=[n for n in REFS if n not in (41,42,64)]
def main():
 k=ROOT/'hardware/kicad'
 pro=k/'robomaster_supercap.kicad_pro'
 original=pro.read_bytes()
 backup=ROOT/'.local/project_before_approved_clearance.json'
 backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():backup.write_bytes(original)
 settings=json.loads(original)
 settings['board']['design_settings']['rules']['min_clearance']=0.15
 pro.write_text(json.dumps(settings,indent=2)+'\n',encoding='utf8')
 rules=['(version 1)',
 '# User explicitly approved 2026-10-04: fine-pitch pads0.15mm;all others>=0.20mm.',
 '(rule "Rev A default copper spacing" (constraint clearance (min 0.20mm)))']
 for n in REFS:
  ref='U'+str(n)
  condition="A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('"+ref+"') && B.memberOfFootprint('"+ref+"')"
  rules.append('(rule "'+ref+' internal fine-pitch pads"\n  (condition "'+condition+'")\n  (constraint clearance (min 0.15mm)))')
 (k/'robomaster_supercap.kicad_dru').write_text('\n'.join(rules)+'\n',encoding='utf8')
 before=json.loads(original);before['board']['design_settings']['rules']['min_clearance']=0.15
 assert settings==before,'Unexpected unrelated settings change'
 print(len(REFS),'same-package pad exceptions;other settings preserved')
if __name__=='__main__':main()
