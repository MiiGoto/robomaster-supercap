"""Read-only audit against KiCad-exported netlist, not just generation intent.

Invoke after sch export netlist to .local/rev_a.net. This detects empty exports,
unintended global-label disconnects, footprint pin loss and dead protection logic.
It cannot validate analog dynamics, ratings, land geometry or physical hardware.
"""
from pathlib import Path
import json,sys
from read_kicad import parse,child,children
from rev_a_parts import P
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
PERMITS=['IL_POS_OK','IL_NEG_OK','BUS_POS_OK','BUS_NEG_OK','CAP_POS_OK','CAP_NEG_OK','PG_DRV','PG_MCU','RAIL_OK','WATCHDOG_OK','MON_DCHG','MON_DDSG','MON_CONFIG_VALID','REFEREE_PERMIT','FET_TEMP_LO_OK','FET_TEMP_HI_OK','L_TEMP_LO_OK','L_TEMP_HI_OK','BANK_TEMP_LO_OK','BANK_TEMP_HI_OK','BUS_OV_OK','BUS_UV_OK','BANK_OV_OK','DRIVER_UV_OK','DRIVER_OV_OK']
def load():return json.loads((ROOT/'simulation/rev_a_connectivity.json').read_text(encoding='utf-8'))
PERMITS += ['ACTUATOR_UV_OK','ACTUATOR_OV_OK']
def logic(items,inputs,qstate=1):
    values=dict.fromkeys(PERMITS,1);values.update({'V3V3':1,'GND':0,'NRST':1,'MCU_GATE_REQUEST':1,'FAULT_LATCH_Q':qstate});values.update(inputs)
    gates=[p for p in items if p['typ']=='SN74LVC2G08DCUR']
    for _ in range(len(gates)+2):
        for g in gates:
            n=g['nets']
            for a,b,y in [('1','2','7'),('5','6','3')]:
                if n[y]:values[n[y]]=bool(values.get(n[a],0) and values.get(n[b],0))
    return values
def main():
    items=load(); netlist=parse((ROOT/'.local/rev_a.net').read_text(encoding='utf-8'))
    comps=children(child(netlist,'components'),'comp');assert len(comps)==sum(not p['ref'].startswith('#') for p in items),(len(comps),len(items))
    assert len({p['ref'] for p in items})==len(items),'duplicate references'
    actual={}
    for net in children(child(netlist,'nets'),'net'):
        name=child(net,'name')[1]
        for node in children(net,'node'):actual[child(node,'ref')[1],child(node,'pin')[1]]=name
    checked=0;missing=[];nofp=[]
    for p in items:
        if p['ref'].startswith('#'):continue
        for pin,net in p['nets'].items():
            if net is not None:
                assert actual.get((p['ref'],pin))==net,(p['ref'],pin,net,actual.get((p['ref'],pin)))
                checked+=1
        if not p['fp']:nofp.append(p['ref']);continue
        lib,name=p['fp'].split(':');path=LIB/(lib+'.pretty')/(name+'.kicad_mod')
        assert path.exists(),p['fp']
        pads={v[1] for v in children(parse(path.read_text(encoding='utf-8')),'pad') if v[1]}
        if pads!=set(P[p['typ']].pins):missing.append((p['ref'],p['fp'],sorted(pads),sorted(P[p['typ']].pins)))
    assert not missing,missing
    assert logic(items,{})['GATE_PERMIT']
    for input_name in PERMITS:
        v=logic(items,{input_name:0})
        assert not v['GATE_PERMIT'],('uncoupled protection',input_name)
        assert not v['FAULT_CLEAR_N'],('latch not cleared',input_name)
    assert not logic(items,{},qstate=0)['GATE_PERMIT'],'unarmed state must be off'
    assert not logic(items,{},qstate=0)['CONTACT_PERMIT'],'contacts must not auto-reclose after fault clear'
    assert not logic(items,{'NRST':0})['LATCH_CLEAR_N'],'reset must async-clear permit'
    # Check all four PWM outputs disappear when gate permit is absent.
    for input_name in PERMITS:
        v=logic(items,{input_name:0,'PWM_AH':1,'PWM_AL':1,'PWM_BH':1,'PWM_BL':1})
        assert not any(v[n] for n in ['PWM_AH_SAFE','PWM_AL_SAFE','PWM_BH_SAFE','PWM_BL_SAFE'])
    print(f'PASS: {len(comps)} exported components; {len(children(child(netlist,"nets"),"net"))} nets; {checked} pin/net connections; candidate footprint pad sets; {len(PERMITS)} independent inhibit cases; unarmed/reset; 4 PWM kills.')
    print(f'External/candidate components without PCB footprint: {len(nofp)}. Physical land geometry, component ratings and latency still need independent review.')
if __name__=='__main__':main()
