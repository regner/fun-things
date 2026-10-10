"""Write or check the lean producer manifest after validation, imports and handoff edits."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_05"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"
HANDOFF = ROOT / f"docs/assets/production/{NID}.md"
paths = [HANDOFF, ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
for directory in (f"art/source/models/environment/{NID}", f"art/models/environment/{NID}",
                  f"tools/asset_production/{NID}", f"docs/assets/production/{NID}-evidence"):
    paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and p != MANIFEST)
assert not any(p.suffix in (".pyc", ".blend1") for p in paths)
files = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
report = {"asset_id": "d03_apartment_family.05", "scope": "All produced payloads except this manifest",
          "files": files}
validation = json.loads((EVIDENCE / "validation.json").read_text())
for key in ("source", "export"):
    receipt = validation[key]
    assert receipt in files, receipt
    assert receipt["sha256"] in HANDOFF.read_text()
    assert str(receipt["bytes"]) in HANDOFF.read_text()
if "--check" in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report
    print(f"PASS: {len(files)} manifest payloads; handoff source/export receipts match")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(f"Recorded {len(files)} payloads")
