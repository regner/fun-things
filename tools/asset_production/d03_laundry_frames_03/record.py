"""Record final owned payloads and verify handoff/receipt consistency before committing."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_laundry_frames_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def receipt(path):
    """Hash actual final bytes rather than cached timestamps."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Require source/export, final engine and documented identities before manifest creation."""
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    assert validation["status"] == "PASS" and validation["godot"]["ok"]
    handoff = ROOT / f"docs/assets/production/{NID}.md"
    text = handoff.read_text(encoding="utf-8")
    entries = [validation["source"]]
    for variant in validation["variants"].values():
        assert variant["fresh_reexport_byte_identical"]
        entries.append(variant["export"])
    for entry in entries:
        assert receipt(ROOT / entry["path"]) == entry
        assert entry["sha256"] in text and str(entry["bytes"]) in text
    for path, entry in validation["godot"]["roundtrip"].items():
        if path.startswith("res://"):
            assert entry["byte_stable"] and entry["stable_reload_count"] == 2
            assert receipt(ROOT / path[6:])["sha256"] == entry["sha256"]
    for dependency in validation["existing_dependencies_not_produced"]:
        assert receipt(ROOT / dependency["path"]) == dependency

    # The standing sibling-status exception allows only this handoff and its manifest entry.
    sibling_doc = ROOT / "docs/assets/production/d03_laundry_frames_01.md"
    sibling_manifest = ROOT / "docs/assets/production/d03_laundry_frames_01-evidence/manifest.json"
    sibling = json.loads(sibling_manifest.read_text())
    entry = next(item for item in sibling["files"]
                 if item["path"] == sibling_doc.relative_to(ROOT).as_posix())
    assert receipt(sibling_doc) == entry
    files = [handoff, sibling_doc, sibling_manifest]
    files.extend((ROOT / "scenes/prefabs/environment").glob(f"{NID}*.tscn"))
    for directory in (ROOT / f"art/source/models/environment/{NID}",
                      ROOT / f"art/models/environment/{NID}",
                      ROOT / f"tools/asset_production/{NID}", EVIDENCE):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and path.name != "manifest.json" and "__pycache__" not in path.parts)
    manifest = {"asset": "d03_laundry_frames.03", "producer": "commissioned worker specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True,
                "sibling_status_exception": [sibling_doc.relative_to(ROOT).as_posix(),
                                             sibling_manifest.relative_to(ROOT).as_posix()],
                "files": [receipt(path) for path in sorted(set(files))]}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("MANIFEST_PASS", len(manifest["files"]), "payloads; handoff and receipt hashes agree")


if __name__ == "__main__":
    main()
