"""Profile schema/generation rejection tests, no hardware or external packages."""
import copy
import json
import tempfile
from pathlib import Path
from generate_bq_profile import render

source = Path(__file__).resolve().parents[2] / "config/bq76942_rev_a.json"
profile = json.loads(source.read_text(encoding="utf-8"))
assert "{0x9304u,2u,{0xffu,0x02u}}" in render(source)
checks = 1
with tempfile.TemporaryDirectory() as directory:
    for change in ("part", "value", "length", "duplicate", "policy"):
        bad = copy.deepcopy(profile)
        if change == "part":
            bad["part"] = "unreviewed"
        elif change == "value":
            bad["data_memory"][0]["value"] ^= 1
        elif change == "length":
            bad["data_memory"].pop()
        elif change == "duplicate":
            bad["data_memory"][1]["address"] = bad["data_memory"][0]["address"]
        else:
            bad["write_policy"] = "OTP"
        path = Path(directory) / "invalid.json"
        path.write_text(json.dumps(bad), encoding="utf-8")
        try:
            render(path)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError(f"accepted invalid profile: {change}")
print(f"PASS {checks} profile generation / rejection checks")
