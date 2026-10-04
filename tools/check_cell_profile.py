"""Offline configuration arithmetic audit; DOES NOT program any device."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'firmware/config/bq76942_rev_a.json'

def check(profile):
    registers=profile['data_memory']
    words={int(r['address'],16):r['value'] for r in registers}
    assert len(words)==len(registers),'duplicate data-memory addresses'
    for r in registers:
        assert r['width'] in (1,2)
        assert 0<=r['value']<1<<(8*r['width'])
        assert len(bytes.fromhex(r['little_endian']))==r['width']
        assert int.from_bytes(bytes.fromhex(r['little_endian']),'little')==r['value']
    assert words[0x9304]==0x2ff and words[0x9304].bit_count()==9
    assert words[0x9301]==words[0x9302]==0xa6
    assert words[0x9236]==0x0d and words[0x9239]==0x10 and words[0x923c]==0x60
    assert words[0x9261]==0x0c and words[0x9265]==0x18 and words[0x9269]==0xe4
    assert words[0x9308]&8 and words[0x9308]&32 and words[0x9309]==0
    assert words[0x9343]&16 and not words[0x9343]&128
    assert words[0x9278]*.0506==2.53
    assert abs(words[0x9275]*.0506-1.2144)<1e-12
    assert words[0x9279]==words[0x9276]==1
    assert words[0x9335]==0 and words[0x9314]==1
    print(f'PASS: {len(registers)} unique RAM entries, widths/endianness,9S mask,CRC,permission polarity,protection mapping,threshold quantization. No hardware readback performed.')

if __name__=='__main__':check(json.loads(PROFILE.read_text(encoding='utf-8')))
