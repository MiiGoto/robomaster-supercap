"""Move optional turn-off branches next to their gate resistors, candidate only.

Do not rebuild placement or touch fixed power/GND copper. Exact native DRC
and rerouting are required before adopting the candidate.
"""
import argparse
import shutil
import pcbnew as p
from build_rev_a_pcb import ROOT, K, pt

MOVES = {
    'D9': (34.5, 68., 0), 'R43': (34.5, 71., 180),
    'D10': (34.5, 81., 0), 'R45': (33., 84., 180),
    'D11': (75.5, 68., 90), 'R49': (75.5, 63., 180),
    'D12': (75.5, 78., 90), 'R51': (75.5, 73., 180),
}
NETS = {'GATE_AH', 'GATE_AL', 'GATE_BH', 'GATE_BL',
        'HO_A', 'LO_A', 'HO_B', 'LO_B',
        'HO_A_FAST', 'LO_A_FAST', 'HO_B_FAST', 'LO_B_FAST', 'GATE_PERMIT'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('output')
    args = ap.parse_args()
    b = p.LoadBoard(str(ROOT / args.source))
    footprints = {f.GetReference(): f for f in b.GetFootprints()}
    for ref, (x, y, angle) in MOVES.items():
        f = footprints[ref]
        assert all(pad.GetNetname() in NETS for pad in f.Pads() if pad.GetNumber()), ref
        f.SetPosition(pt(x, y))
        f.SetOrientationDegrees(angle)
    for track in list(b.GetTracks()):
        if track.GetNetname() in NETS:
            b.Delete(track)
    p.ZONE_FILLER(b).Fill(b.Zones())
    output = ROOT / args.output
    assert output != K / 'robomaster_supercap.kicad_pcb', 'Candidate output required'
    output.parent.mkdir(parents=True, exist_ok=True)
    p.SaveBoard(str(output), b)
    for ext in ['.kicad_pro', '.kicad_dru']:
        shutil.copy2(K / ('robomaster_supercap' + ext), output.with_suffix(ext))
    print('Localized eight optional gate components; thirteen nets require rerouting')


if __name__ == '__main__':
    main()
