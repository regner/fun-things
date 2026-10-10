"""Write/check the final lean manifest after imports, validation and handoff edits."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_10"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"
HANDOFF = ROOT / f"docs/assets/production/{NID}.md"
paths = [HANDOFF]
paths.extend((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn*"))
for directory in (f"art/source/models/environment/{NID}", f"art/models/environment/{NID}",
                  f"tools/asset_production/{NID}", f"docs/assets/production/{NID}-evidence"):
    paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and p != MANIFEST)
assert not any(p.suffix in (".pyc", ".blend1") for p in paths)
files = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
report = {"asset_id": "d03_apartment_family.10", "scope": "All produced payloads except this manifest",
          "files": files}
validation = json.loads((EVIDENCE / "validation.json").read_text())
receipts = [validation["source"]]
receipts.extend(variant["export"] for variant in validation["variants"].values())
for receipt in receipts:
    assert receipt in files, receipt
    assert receipt["sha256"] in HANDOFF.read_text()
    assert str(receipt["bytes"]) in HANDOFF.read_text()
for variant in ("straight", "end", "outside", "inside"):
    path = ROOT / f"scenes/prefabs/environment/{NID}_{variant}.tscn"
    assert validation["godot"]["roundtrip"][variant]["byte_stable"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        validation["godot"]["roundtrip"][variant]["normalized_sha256"])
if "--check" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report
    print(f"PASS: {len(files)} manifest payloads; handoff receipts and normalized wrappers match")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(files)} payloads")
