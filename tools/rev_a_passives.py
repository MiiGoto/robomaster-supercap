"""Rev A purchasing selections from manufacturer ordering systems.

Stock and orderable suffix availability are not asserted. Engineering selections
are not an assembly release. All capacitor DC-bias/ripple limits need validation.
"""
from decimal import Decimal
import re

CAPS={
 '100pF':'C0805C101J1GACTU', '1nF':'C0805C102J1GACTU',
 '2.2nF':'C0805C222K5RACTU', '4.7nF':'C0805C472J5GACTU',
 '10nF':'C0805C103J5GACTU', '100nF':'C0805C104K5RACTU',
 '470nF':'GRM21BR71H474KA88L', '1uF':'GRM21BR71H105KA12L',
 '2.2uF':'GRM32ER72A225KA35L', '4.7uF':'C0805C475K4RACTU',
 '22uF':'C1210C226K3RACTU', '470uF':'EEUFR1J471', '50F':'SCCV40B506SRB',
}

def resistor_code(value):
    m=re.match(r'(\d+(?:\.\d+)?)([RkM]?)',value)
    if not m:raise ValueError(value)
    number=Decimal(m[1]);unit={'':'R','R':'R','k':'K','M':'M'}[m[2]]
    literal=format(number,'f').replace('.',unit)
    if unit not in literal:literal+=unit
    return literal.ljust(4,'0')

def mpn(typ,value,fp):
    if typ=='C':return CAPS[value.split()[0]]
    if typ=='R':
        if 'NTCLE' in value:return 'NTCLE100E3103JB0'
        if 'HS25' in value:return 'HS25 100R F'
        size='2512' if 'R_2512' in fp or '1W' in value else '0603' if 'R_0603' in fp else '0805'
        if value.startswith('0R'):return 'CRCW'+size+'0000Z0EA'
        raw=re.match(r'(\d+(?:\.\d+)?)([RkM]?)',value)
        low_ohms=raw[2] in ('','R') and Decimal(raw[1])<10
        return 'CRCW'+size+resistor_code(value)+('FN' if low_ohms else 'FK')+('EG' if size=='2512' else 'EA')
    if typ=='L':return value.split(' /')[0] if value.startswith('XAL') else value.split(' / ')[-1].split()[0]
    if typ=='FUSE':return value.split()[0]
    if typ=='CONTACT':return 'AEV14012'
    if typ=='DDR60L12':return 'DDR-60L-12'
    if typ=='DISCONNECT':return '6006'
    if typ=='Q_NPN':return 'BC847B,215'
    if typ=='Q_PNP':return 'BC857B,215'
    if typ=='D':return value.split()[0]
    if typ=='LED':return 'LTST-C170KRKT'
    if typ=='AQZ202G':return typ
    if typ.startswith('J') or typ=='PWR_FLAG':return ''
    return typ
