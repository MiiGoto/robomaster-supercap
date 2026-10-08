"""Generate project-authored C data from the reviewed RAM-only JSON, without vendor assets."""
import argparse
import json
from pathlib import Path

def render(path):
    profile = json.loads(path.read_text(encoding="utf-8"))
    assert profile["part"] == "BQ7694204PFBR"
    assert "RAM only" in profile["write_policy"]
    entries = profile["data_memory"]
    seen = set()
    lines = ['/* Generated from firmware/config/bq76942_rev_a.json; do not edit. */',
             '#include "bq76942.h"', 'const bq_profile_entry_t bq_profile[] = {']
    for e in entries:
        address, width = int(e["address"], 16), e["width"]
        assert 0x9200 <= address <= 0x9400 and width in (1, 2)
        assert address not in seen
        seen.add(address)
        data = bytes.fromhex(e["little_endian"])
        assert len(data) == width and int.from_bytes(data, "little") == e["value"]
        data = data.ljust(2, b"\0")
        lines.append(f' {{0x{address:04x}u,{width}u,{{0x{data[0]:02x}u,0x{data[1]:02x}u}}}}, /* {e["name"]} */')
    assert len(entries) == 39
    selected = {int(e["address"], 16):e["value"] for e in entries}
    assert selected[0x9304] == 0x2ff and selected[0x9239] == 16
    assert selected[0x9301] == selected[0x9302] == 0xa6
    lines += ['};', 'const size_t bq_profile_count=sizeof(bq_profile)/sizeof(bq_profile[0]);', '']
    return '\n'.join(lines)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    text=render(root/"config/bq76942_rev_a.json")
    target=root/"controller/config/bq_profile.c"
    if args.check:
        assert target.read_text(encoding="utf-8")==text, "stale BQ generated profile"
    else:
        target.write_text(text,encoding="utf-8")
    print("BQ profile: 39 entries, schema/value/mapping/read-only policy checks PASS")
