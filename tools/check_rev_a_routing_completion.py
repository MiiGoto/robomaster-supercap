"""Require actual native connectivity and DRC evidence for routing completion.

Run with KiCad's Python after CLI DRC on the same board. The separate
footprint/manifest audit and schematic-parity check remain required.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import pcbnew as p
from build_rev_a_pcb import ROOT, POWER


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('drc')
    ap.add_argument('--result')
    args = ap.parse_args()
    source = ROOT / args.board
    board = p.LoadBoard(str(source))
    board.BuildConnectivity()
    connection = board.GetConnectivity()
    connection.RecalculateRatsnest()
    missing = connection.GetUnconnectedCount(False)
    disconnected = []
    pad_nets = collections.defaultdict(list)
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetCode():
                pad_nets[pad.GetNetname()].append(pad)
    assert pad_nets and POWER | {'GND'} <= set(pad_nets)
    for net, pads in pad_nets.items():
        if len(pads) < 2:
            continue
        linked = {x.m_Uuid.AsString() for x in connection.GetConnectedItems(pads[0])}
        linked.add(pads[0].m_Uuid.AsString())
        if any(x.m_Uuid.AsString() not in linked for x in pads):
            disconnected.append(net)
    drc = json.loads((ROOT / args.drc).read_text(encoding='utf8'))
    violations = drc.get('violations', [])
    inner_signals = [t for t in board.GetTracks()
                     if not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.In1_Cu
                     and t.GetNetname() != 'GND']
    local_nets={'V3V3','CAP_I_ADC','PRE_CAP_REQUEST','TEMP_BANK_ADC',
                'TEMP_FET_ADC','TEMP_L_ADC','WD_HEARTBEAT'}
    local_escape_ok=all(t.GetNetname() in local_nets and abs(p.ToMM(t.GetWidth())-.2)<1e-6
                        and all(160<=p.ToMM(q.x)<=215 and 7<=p.ToMM(q.y)<=65
                                for q in (t.GetStart(),t.GetEnd())) for t in inner_signals)
    plane_zones=[z for z in board.Zones() if not z.GetIsRuleArea()
                 and z.IsOnLayer(p.In1_Cu) and z.GetNetname()=='GND']
    plane_polygons=[z.GetFilledPolysList(p.In1_Cu).OutlineCount() for z in plane_zones]
    result = {
        'board_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'native_unconnected': missing,
        'checked_pad_nets': len(pad_nets),
        'checked_net_assigned_pads': sum(map(len, pad_nets.values())),
        'disconnected_pad_nets': disconnected,
        'drc_errors': sum(v['severity'] == 'error' for v in violations),
        'drc_warnings': sum(v['severity'] == 'warning' for v in violations),
        'drc_unconnected_items': len(drc.get('unconnected_items', [])),
        'schematic_parity_items': len(drc.get('schematic_parity', [])),
        'reference_plane_signal_segments': len(inner_signals),
        'reference_plane_local_escape_contract':local_escape_ok,
        'ground_reference_filled_outline_counts':plane_polygons,
        'required_power_nets': sorted(POWER),
        'scope': 'CAD connectivity/DRC only; hardware performance remains unmeasured',
    }
    if args.result:
        (ROOT / args.result).write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result, indent=2))
    assert missing == 0 and not disconnected, 'Native routing incomplete'
    assert not violations and not drc.get('unconnected_items'), 'Native DRC not clean'
    assert not drc.get('schematic_parity'), 'Schematic parity failed'
    assert local_escape_ok, 'Reference escapes exceed their reviewed MCU-only envelope'
    assert plane_polygons==[1], 'Ground reference plane is split into separate filled polygons'


if __name__ == '__main__':
    main()
