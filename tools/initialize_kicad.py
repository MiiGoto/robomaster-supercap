"""Create a new concept-only project. Refuse to overwrite any target."""
from pathlib import Path
import json
import uuid

ROOT = Path(__file__).resolve().parents[1] / 'hardware' / 'kicad'
NAME = 'robomaster_supercap'
BLOCKS = ['POWER_INPUT', 'POWER_STAGE', 'SUPERCAP_BANK', 'CONTROLLER',
          'SENSING', 'CAN', 'SAFETY']

def uid():
    return str(uuid.uuid4())

def quote(value):
    return json.dumps(value, ensure_ascii=False)

def text(value, x, y, size=1.4):
    return (f'(text {quote(value)} (at {x} {y} 0) '
            f'(effects (font (size {size} {size}))) (uuid "{uid()}"))\n')

def header(identity, title):
    return (f'(kicad_sch (version 20250114) (generator "eeschema") '
            f'(uuid "{identity}") (paper "A4") '
            f'(title_block (title {quote(title)}) (date "2026-10-03") '
            '(rev "0.1-concept") (comment 1 "No electrical implementation; ratings TBD")) '
            '(lib_symbols)\n')

def generate():
    ROOT.mkdir(parents=True, exist_ok=True)
    targets = [ROOT / (NAME + ext) for ext in ['.kicad_pro', '.kicad_sch', '.kicad_pcb']]
    targets += [ROOT / (block + '.kicad_sch') for block in BLOCKS]
    if any(path.exists() for path in targets):
        raise SystemExit('Refusing to overwrite an existing target')
    root_id = uid()
    root = header(root_id, 'RoboMaster Supercap - Architecture Only')
    root += text('TASK 1 CONCEPT ONLY - NO PARTS / NETS / RATINGS', 148, 15, 2)
    positions = [(15, 32), (100, 32), (185, 32), (100, 95),
                 (15, 95), (185, 95), (100, 151)]
    for block, (x, y) in zip(BLOCKS, positions):
        sid = uid()
        root += (f'(sheet (at {x} {y}) (size 65 28) (stroke (width 0.254) (type default)) '
                 f'(fill (color 0 0 0 0)) (uuid "{sid}") '
                 f'(property "Sheetname" "{block}" (at {x} {y-1} 0) '
                 '(effects (font (size 1.4 1.4)) (justify left bottom))) '
                 f'(property "Sheetfile" "{block}.kicad_sch" (at {x} {y+29} 0) '
                 '(effects (font (size 1.2 1.2)) (justify left top))) '
                 f'(instances (project "{NAME}" (path "/{root_id}" (page "{BLOCKS.index(block)+2}")))))\n')
        child = header(uid(), block + ' - Placeholder')
        child += text(block + '\nRequirements and safety review required\nParts, pins, nets and ratings TBD', 145, 70, 2)
        child += text('See docs/architecture.md and docs/safety.md\nNo power-stage detail in Task 1', 145, 105)
        (ROOT / (block + '.kicad_sch')).write_text(child + ')\n', encoding='utf-8')
    root += text('BUS <-> INPUT PROTECTION <-> CONVERTER <-> BANK', 145, 77)
    root += text('SENSE -> MCU -> DRIVER CONTROL; SAFETY INHIBIT OVERRIDES ENABLE\nCAN <-> MCU; official module placement TBD', 148, 139)
    root += text('Graphic text is explanatory only; no electrical connectivity', 148, 193)
    root += f'(sheet_instances (path "/" (page "1")))\n)\n'
    (ROOT / (NAME + '.kicad_sch')).write_text(root, encoding='utf-8')
    (ROOT / (NAME + '.kicad_pro')).write_text(json.dumps({
        'meta': {'filename': NAME + '.kicad_pro', 'version': 1},
        'board': {}, 'schematic': {}, 'net_settings': {'classes': [], 'meta': {'version': 3}}
    }, indent=2) + '\n', encoding='utf-8')
    board = '''(kicad_pcb (version 20241229) (generator "pcbnew")
      (general (thickness 1.6)) (paper "A4")
      (layers (0 "F.Cu" signal) (2 "B.Cu" signal)
              (9 "F.SilkS" user "f.silkscreen")
              (8 "B.SilkS" user "b.silkscreen")
              (44 "Edge.Cuts" user))
      (setup (pad_to_mask_clearance 0))
    )
    '''
    # Thickness is KiCad's placeholder default, not an approved mechanical spec.
    (ROOT / (NAME + '.kicad_pcb')).write_text(board.rstrip() + '\n', encoding='utf-8')
    print('Created project, 8 schematic pages, empty PCB; no symbols/nets/footprints.')

if __name__ == '__main__':
    generate()
