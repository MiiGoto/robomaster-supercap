"""Read-only key manufacturer land-dimension checks against installed KiCad.

Not a whole-board fabrication review. No footprint/library file is modified.
"""
from pathlib import Path
from math import hypot
from read_kicad import parse,children,child
from rev_a_parts import P
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')

def pads(name):
    lib,fp=name.split(':')
    root=parse((LIB/(lib+'.pretty')/(fp+'.kicad_mod')).read_text(encoding='utf-8'))
    result={}
    for p in children(root,'pad'):
        if not p[1]:continue
        area=lambda pad: float(child(pad,'size')[1])*float(child(pad,'size')[2])
        if p[1] not in result or area(p)>area(result[p[1]]):result[p[1]]=p
    # Exposed pads can also have same-number peripheral extensions;retain the
    # main thermal land rather than the last extension serialized in the file.
    return result

def xy(p,name):return tuple(float(x) for x in child(p,name)[1:3])

def main():
    shunt=pads(P['WSK25123L000FEA'].footprint)
    # WSK2512 1..4.9mR datasheet land power length a/b3.30mm,
    # Kelvin width c0.76mm; terminal T2.21,not higher-ohm T1.19.
    assert set(shunt)=={'1','2','3','4'}
    assert xy(shunt['1'],'at')[0]<0 and xy(shunt['2'],'at')[0]<0
    assert xy(shunt['3'],'at')[0]>0 and xy(shunt['4'],'at')[0]>0
    for n in ('1','4'):assert abs(xy(shunt[n],'size')[0]-3.30)<.001
    for n in ('2','3'):assert abs(xy(shunt[n],'size')[1]-.76)<.001
    bulk=pads('Capacitor_THT:CP_Radial_D12.5mm_P5.00mm')
    assert abs(hypot(*(a-b for a,b in zip(xy(bulk['1'],'at'),xy(bulk['2'],'at'))))-5)<.001
    mcu=pads(P['STM32G474RET6'].footprint)
    assert len(mcu)==64
    assert abs(hypot(*(a-b for a,b in zip(xy(mcu['1'],'at'),xy(mcu['2'],'at'))))-.5)<.001
    gate=pads(P['UCC27282DRCR'].footprint)
    assert len(gate)==11 and xy(gate['11'],'size')==(1.65,2.4)
    cell=pads(P['BQ7694204PFBR'].footprint)
    assert len(cell)==48
    assert abs(hypot(*(a-b for a,b in zip(xy(cell['1'],'at'),xy(cell['2'],'at'))))-.5)<.001
    print('PASS: WSK3mR four-terminal power/Kelvin land dimensions,bulk5mm pitch,MCU/BQ0.5mm pitch,driver EP dimensions. Assembly tolerances/paste/thermal/clearance remain unreviewed.')

if __name__=='__main__':main()
