"""Offline integrity/scope checks for the bounded upstream source record; no native calls."""

import argparse
import hashlib
import json
import pathlib
import re
import subprocess


def git(*args):
    """Read repository state without changing it."""
    return subprocess.check_output(["git", *args], text=True)


def digest(data):
    """Return the source/snapshot SHA-256 used in the evidence ledger."""
    return hashlib.sha256(data).hexdigest()


def main():
    """Check the complete declared source set, saved bytes, links and owned base delta."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=pathlib.Path)
    args = parser.parse_args()
    repo = pathlib.Path(git("rev-parse", "--show-toplevel").strip())
    root = repo / "docs/spikes/s03-s-upstream-peer-evidence"
    doc = repo / "docs/spikes/s03-s-upstream-peer-evidence.md"
    manifest = json.loads((root / "sources.json").read_text())
    base = manifest["base"]
    assert base == "52941da4b4c92a547a8066b5c13f733043ecbe48"
    expected_sources = {
        "gde": {
            "godotsteam/godotsteam_multiplayer_peer.cpp",
            "godotsteam/godotsteam_multiplayer_peer.h",
            "godotsteam/steam_packet_peer.cpp",
            "godotsteam/steam_packet_peer.h",
            "godotsteam/godotsteam.cpp",
            "godotsteam/godotsteam_project_settings.cpp",
            "SConstruct", "readme.md",
        },
        "expresso": {
            "steam-multiplayer-peer/steam_multiplayer_peer.cpp",
            "steam-multiplayer-peer/steam_multiplayer_peer.h",
            "steam-multiplayer-peer/steam_connection.cpp",
            "steam-multiplayer-peer/steam_connection.h",
            "steam-multiplayer-peer/steam_packet_peer.cpp",
            "steam-multiplayer-peer/steam_packet_peer.h", "README.md",
        },
        "csharp": {"addons/steam-multiplayer-peer-csharp/SteamMultiplayerPeer.cs", "README.md"},
        "valve": {"include/steam/isteamnetworkingsockets.h", "include/steam/steamnetworkingtypes.h"},
    }
    expected = {(candidate, path) for candidate, paths in expected_sources.items() for path in paths}
    rows = manifest["files"]
    assert len(rows) == len(expected) == 19
    assert {(row["candidate"], row["path"]) for row in rows} == expected
    assert {root / row["stored_path"] for row in rows} == set((root / "sources").rglob("*.txt"))
    candidates = json.loads((root / "candidates.json").read_text())
    commits = {row["id"]: row["commit"] for row in candidates}
    assert commits == {
        "gde": "2cfe81d58d85f7a8a78cd0a19a5642d011e9c8fc",
        "expresso": "13a2e888a7159c1a145333c7ea100dfd2b6a8aa7",
        "csharp": "a826c72e7d936c6af6a10122be1047a89e29cd36",
        "valve": "d534c19aa760df3fb75fd20db13ba1932b8a5463",
    }
    assert sum(row["role"] == "peer candidate" for row in candidates) == 3
    metadata_names = {
        "gde": "gde-commit", "expresso": "expresso-head",
        "csharp": "csharp-head", "valve": "valve-head",
    }
    for row in candidates:
        raw = (root / "metadata" / (metadata_names[row["id"]] + ".json")).read_bytes()
        assert digest(raw) == row["metadata_sha256"]
        assert json.loads(raw)["sha"] == row["commit"]
    for row in rows:
        saved = (root / row["stored_path"]).read_bytes()
        assert len(saved) == row["stored_bytes"] and digest(saved) == row["stored_sha256"]
        assert commits[row["candidate"]] in row["url"]
        original = None
        if args.source_dir:
            original = (args.source_dir / row["candidate"] / row["path"]).read_bytes()
            assert len(original) == row["bytes"] and digest(original) == row["sha256"]
        elif row["stored_kind"] == "complete exact source bytes":
            original = saved
            assert len(original) == row["bytes"] and digest(original) == row["sha256"]
        if original is not None and "git_blob_sha1" in row:
            git_blob = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original)
            assert git_blob.hexdigest() == row["git_blob_sha1"]
        if row["candidate"] != "valve":
            tree = json.loads((root / "metadata" / (row["candidate"] + "-selected-tree.json")).read_text())
            assert tree["raw_tree_sha"] == commits[row["candidate"]]
            assert next(x["sha"] for x in tree["entries"] if x["path"] == row["path"]) == row["git_blob_sha1"]
        if original is not None and "stored_line_ranges" in row:
            lines = original.decode().splitlines()
            expected_text = "".join(
                f"\n--- {row['path']} lines {a}-{b} (1-based) ---\n"
                + "".join(f"{i}: {lines[i - 1]}\n" for i in range(a, b + 1))
                for a, b in row["stored_line_ranges"]
            )
            assert saved == expected_text.encode()
    for path in root.rglob("*.json"):
        json.loads(path.read_text())
    licenses = json.loads((root / "licenses.json").read_text())
    assert {row["candidate"] for row in licenses} == {"expresso", "csharp", "valve"}
    for row in licenses:
        raw = (root / row["stored_path"]).read_bytes()
        assert len(raw) == row["bytes"] and digest(raw) == row["sha256"]
        assert commits[row["candidate"]] in row["url"]
    indexed = set(git("ls-files", "docs/spikes/s03-s-upstream-peer-evidence").splitlines())
    for path in root.rglob("*"):
        if path.is_file() and str(path.relative_to(repo)) in indexed:
            blob = subprocess.check_output(["git", "show", ":" + str(path.relative_to(repo))])
            assert blob == path.read_bytes(), path
    local_links = []
    for path in [doc, repo / "TODO.md"]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            assert resolved.exists(), (path, target)
            local_links.append(target)
    prefix = "docs/spikes/s03-s-upstream-peer-evidence"
    changed = set(git("diff", "--name-only", base).splitlines())
    assert all(path == "TODO.md" or path == prefix + ".md" or path.startswith(prefix + "/") for path in changed)
    original_todo = git("show", base + ":TODO.md")
    todo = (repo / "TODO.md").read_text()
    addition = (
        "  [Exact upstream source evidence](docs/spikes/s03-s-upstream-peer-evidence.md)\n"
        "  assesses three immutable peers; none meets the unchanged streams/bounds/lifecycle.\n"
        "  Remaining decision: separately commission the native-boundary design or keep Steam unavailable.\n"
    )
    assert todo.count(addition) == 1
    assert todo.replace(addition, "", 1) == original_todo
    assert git("merge-base", base, "HEAD").strip() == base
    diff = subprocess.run(["git", "diff", "--check", base], capture_output=True, text=True)
    assert diff.returncode == 0, (diff.stdout, diff.stderr)
    print(f"PASS: {len(rows)} immutable source identities/snapshots; exactly three peer candidates.")
    print(f"PASS: {len(local_links)} existing local links; JSON and metadata readback.")
    print("PASS: exact base ancestry, owned paths, three-line S03-S delta, all other TODO bytes preserved.")
    print("PASS: git diff --check; no native/engine/platform calls.")


if __name__ == "__main__":
    main()
