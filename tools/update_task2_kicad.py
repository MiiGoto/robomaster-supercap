"""Update the existing concept project; preserve sheets, project and PCB UUIDs."""
from pathlib import Path
import re
from initialize_kicad import header, text, uid

ROOT=Path(__file__).resolve().parents[1]/'hardware'/'kicad'
root=ROOT/'robomaster_supercap.kicad_sch'
pre=ROOT/'PRECHARGE.kicad_sch'
if pre.exists():
    raise SystemExit('PRECHARGE already exists; inspect rather than overwrite')
content=root.read_text(encoding='utf-8')
root_id=re.search(r'\(uuid "([^"]+)"\)',content).group(1)
content=content.replace('0.1-concept','0.2-proposal')
content=content.replace('TASK 1 CONCEPT ONLY - NO PARTS / NETS / RATINGS',
                        'TASK 2 PROPOSAL - HUMAN REVIEW REQUIRED - NO CIRCUIT')
content=content.replace('BUS <-> INPUT PROTECTION <-> CONVERTER <-> BANK',
                        'BUS <-> PROTECTION / PRECHARGE <-> 4-SWITCH CONCEPT <-> OFFICIAL MODULE <-> BANK')
content=content.replace('CAN <-> MCU; official module placement TBD',
                        'CAN <-> MCU; official module CAN -> referee CAN1')
sid=uid()
sheet=(f'(sheet (at 15 151) (size 65 28) (stroke (width 0.254) (type default)) '
       f'(fill (color 0 0 0 0)) (uuid "{sid}") '
       '(property "Sheetname" "PRECHARGE" (at 15 150 0) '
       '(effects (font (size 1.4 1.4)) (justify left bottom))) '
       '(property "Sheetfile" "PRECHARGE.kicad_sch" (at 15 180 0) '
       '(effects (font (size 1.2 1.2)) (justify left top))) '
       f'(instances (project "robomaster_supercap" (path "/{root_id}" (page "9")))))\n')
index=content.rfind('(sheet_instances')
content=content[:index]+sheet+content[index:]
root.write_text(content,encoding='utf-8')
notes={
 'CONTROLLER':'G474RE / LQFP64 proposal\nHRTIM -> PWM x4; synchronized ADC -> current loop\nExternal kill overrides MCU; pin assignment TBD',
 'POWER_INPUT':'Referee Chassis -> polarity / disconnect / DC link\nAuxiliary supply separate from converter path\nCutoff must inhibit cap assist; surge / ratings TBD',
 'PRECHARGE':'BUS -> resistor path -> local DC link\nNormally OFF bypass; delta-V / current / timeout feedback\nBank link equalization via SINGLE official power port',
 'POWER_STAGE':'Four-switch bidirectional buck-boost CONCEPT\nTwo half bridges + single inductor; no components placed\nPWM x4 / ENABLE <- controller; FAULT -> safety latch',
 'SUPERCAP_BANK':'9S / SCC50 proposal; all numerical limits pending review\nSingle port -> OFFICIAL MODULE -> converter\nCell OV inhibit / switched shunts / bleed / voltage indicator',
 'SENSING':'Bus V / bank V / 9 cell monitor with open-wire diagnosis\nBus + cap high-side shunts; separate inductor current\nMOSFET / inductor / bank temperature -> MCU',
 'CAN':'MCU FDCAN -> external transceiver -> robot controller\nClassic CAN compatibility; ID / bitrate / termination TBD\nOfficial module -> referee CAN1 is separate',
 'SAFETY':'External OC / OV / watchdog / supervisor -> latch\nLatch -> DRIVER KILL + MCU HRTIM fault + disconnect\nFloat / reset / crash / aux loss -> ENABLE OFF',
}
for block,note in notes.items():
    path=ROOT/(block+'.kicad_sch')
    if path.exists():
        original=path.read_text(encoding='utf-8')
        identity=re.search(r'\(uuid "([^"]+)"\)',original).group(1)
    else:
        identity=uid()
    body=header(identity,block+' - Task 2 Proposal')
    body=body.replace('0.1-concept','0.2-proposal')
    body+=text(note,145,70,1.7)
    body+=text('See docs/task2_decisions.md and docs/interfaces.md\nNo electrical connectivity; no validated circuit',145,110,1.4)
    path.write_text(body+')\n',encoding='utf-8')
print('Updated same project: 9 concept pages. PCB/project files unchanged.')
