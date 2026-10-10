"""Generate/check the lean producer manifest last, including final handoff and import metadata."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_11"
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
report = {"asset_id": "d03_apartment_family.11", "scope": "All produced payloads except this manifest",
          "files": files}
validation = json.loads((EVIDENCE / "validation.json").read_text())
for receipt in (validation["source"], validation["export"]):
    assert receipt in files, receipt
    assert receipt["sha256"] in HANDOFF.read_text()
    assert str(receipt["bytes"]) in HANDOFF.read_text()
for receipt in validation["junction"]["linked_export_receipts"]:
    path = ROOT / receipt["path"]
    assert path.stat().st_size == receipt["bytes"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"]
path = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
assert validation["godot"]["roundtrip"]["byte_stable"]
assert hashlib.sha256(path.read_bytes()).hexdigest() == (
    validation["godot"]["roundtrip"]["normalized_sha256"])
if "--check" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report
    print(f"PASS: {len(files)} payloads; final handoff receipts, dependencies and wrapper match")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(files)} payloads")
