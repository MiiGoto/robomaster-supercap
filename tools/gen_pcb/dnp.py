"""Text patch (KiCad 7 can't write these): DNP on J201/R203, board_only on H1-H3."""
import re, sys
src = open(sys.argv[1]).read()
parts = re.split(r"(?m)^(?=  \(footprint )", src)
out = []
for blk in parts:
    m = re.search(r'\(fp_text reference "([^"]+)"', blk)
    ref = m.group(1) if m else None
    if ref in ("J201", "R203"):
        blk = re.sub(r"\(attr ([^)]*)\)", lambda a: "(attr " + " ".join(dict.fromkeys(a.group(1).split() + ["exclude_from_pos_files", "exclude_from_bom", "dnp"])) + ")", blk, count=1)
    if ref in ("H1", "H2", "H3"):
        blk = re.sub(r"\(attr ([^)]*)\)", lambda a: "(attr " + " ".join(dict.fromkeys(["board_only"] + a.group(1).split())) + ")", blk, count=1)
    out.append(blk)
open(sys.argv[2], "w").write("".join(out))
