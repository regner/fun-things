"""Record complete final owned payload hashes, with only the manifest self-excluded."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_laundry_frames_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def main():
    """Require final source/export and scene receipts before hashing the lean delivery."""
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    assert validation["status"] == "PASS"
    assert validation["fresh_reexport_byte_identical"]
    assert validation["godot"]["ok"]
    handoff = ROOT / f"docs/assets/production/{NID}.md"
    text = handoff.read_text(encoding="utf-8")
    for key in ("source", "export"):
        entry = validation[key]
        raw = (ROOT / entry["path"]).read_bytes()
        assert len(raw) == entry["bytes"]
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        assert entry["sha256"] in text and str(entry["bytes"]) in text
    for path, entry in validation["godot"]["roundtrip"].items():
        if path.startswith("res://"):
            assert entry["byte_stable"] and entry["stable_reload_count"] == 2
            assert hashlib.sha256((ROOT / path[6:]).read_bytes()).hexdigest() == entry["sha256"]
    files = [handoff, ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
    for directory in (ROOT / f"art/source/models/environment/{NID}",
                      ROOT / f"art/models/environment/{NID}",
                      ROOT / f"tools/asset_production/{NID}", EVIDENCE):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and path.name != "manifest.json" and "__pycache__" not in path.parts)
    payload = []
    for path in sorted(set(files)):
        raw = path.read_bytes()
        payload.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"asset": "d03_laundry_frames.01", "producer": "commissioned worker specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": payload}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(payload), "payloads; handoff/receipt hashes and scene bytes verified")


if __name__ == "__main__":
    main()
