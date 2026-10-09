#!/usr/bin/env python3
"""Export the saved S08 main for Windows and observe one bounded ENet host/client set per mode.

This is a platform-adapted S08 diagnostic. It verifies the exact pinned template archive,
stages the committed 34-file S01/S03/S08 closure from one Git revision, exports Windows
release/debug packages into a fresh external directory, and runs the unchanged S03 proof
through the original 20 ms loopback proxy. It never installs templates, edits the checkout
or retries a failed set. See docs/spikes/s08-windows-observation.md for the contract.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_s03 import POLL_SECONDS, Proxy  # noqa: E402  (original 20 ms service owner)
from script_checks import DIAGNOSTIC, PIN  # noqa: E402

TPZ = {"bytes": 1436879719,
       "sha256": "95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6"}
TEMPLATES = {
    "release": ("windows_release_x86_64.exe", 111895040,
                "b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd"),
    "debug": ("windows_debug_x86_64.exe", 105650176,
              "c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6"),
}
MAIN = "res://tests/fixtures/s08/release_boot.tscn"
CLOSURE_PREFIXES = ("tests/fixtures/s03/", "tests/fixtures/s08/")
CLOSURE_S01 = [
    "art/materials/s01_coral.tres", "art/materials/s01_petrol.tres",
    "art/models/spikes/s01_rig.glb", "art/models/spikes/s01_rig.glb.import",
    "art/models/spikes/s01_static.glb", "art/models/spikes/s01_static.glb.import",
    "art/textures/spikes/s01_palette.png", "art/textures/spikes/s01_palette.png.import",
    "tests/fixtures/s01/fixture_identity.gd", "tests/fixtures/s01/fixture_identity.gd.uid",
    "tests/fixtures/s01/rig_prefab.tscn", "tests/fixtures/s01/roundtrip.tscn",
    "tests/fixtures/s01/static_prefab.tscn", "tests/fixtures/s01/static_variant.tscn",
]
CLOSURE_SIZE = 34
IMPORT_SECONDS = 90
EXPORT_SECONDS = 120
SET_SECONDS = 30.0
HANDOFF_SECONDS = 4.0
WORK_SECONDS = 20.0
GRACE_SECONDS = 2.0
RECEIPT_RESERVE = 0.25
HOST_CASES = ["provisional_rollback", "authority_validation_and_expiry"]
CLIENT_CASES = ["provider_substitution_late_cleanup", "baseline_cancel_retry",
                "held_window_resync", "subset_reorder_loss_recovery"]


def identity(path):
    """Hash actual bytes instead of trusting a filename or earlier receipt."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def private_env(directory):
    """Redirect every platform user/config/cache root used by Godot to a private folder."""
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("GODOT_MCP_"):
            del env[key]
    for variable, folder in [("APPDATA", "appdata"), ("LOCALAPPDATA", "localappdata"),
                             ("XDG_DATA_HOME", "data"), ("XDG_CONFIG_HOME", "config"),
                             ("XDG_CACHE_HOME", "cache"), ("TEMP", "temp"), ("TMP", "temp")]:
        path = directory / folder
        path.mkdir(parents=True, exist_ok=True)
        env[variable] = str(path)
    return env


def bind_templates(archive_path, task):
    """Verify archive and member identities, then extract only the Windows templates."""
    if identity(archive_path) != TPZ:
        raise RuntimeError("template archive differs from the recorded 4.8-dev7 TPZ")
    rows = {}
    with zipfile.ZipFile(archive_path) as archive:
        if archive.read("templates/version.txt").decode().strip() != "4.8.dev7":
            raise RuntimeError("template version differs")
        for mode, (name, size, digest) in TEMPLATES.items():
            target = task / "templates" / name
            target.parent.mkdir(exist_ok=True)
            with archive.open("templates/" + name) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            if identity(target) != {"bytes": size, "sha256": digest}:
                raise RuntimeError("template member differs: " + name)
            rows[mode] = {"path": str(target), "bytes": size, "sha256": digest}
    save(task / "template-binding.json", {"archive": str(archive_path), **TPZ, "members": rows})
    return rows


def closure(revision):
    """List the committed S01/S03/S08 closure at one revision; refuse a different size."""
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision, "--",
                                     "tests/fixtures/s03", "tests/fixtures/s08"],
                                    cwd=ROOT, text=True).splitlines()
    paths = sorted(set(CLOSURE_S01 + [name for name in names
                                      if name.startswith(CLOSURE_PREFIXES)]))
    if len(paths) != CLOSURE_SIZE:
        raise RuntimeError(f"closure has {len(paths)} files, expected {CLOSURE_SIZE}")
    return paths


def uid_for(project, name):
    """Read the saved UID from the resource header, script sidecar or import sidecar."""
    path = project / name
    if name.endswith((".uid", ".import")):
        return ""
    if name.endswith(".gd"):
        return (project / (name + ".uid")).read_text().strip()
    if name.endswith((".glb", ".png")):
        match = re.search(r'^uid="([^"]+)"', (project / (name + ".import")).read_text(), re.M)
        return match.group(1) if match else ""
    match = re.search(r'uid="([^"]+)"', path.read_text().splitlines()[0])
    return match.group(1) if match else ""


def stage(task, revision, templates):
    """Write the exact committed closure plus scratch-only configuration and export presets."""
    project = task / "project"
    rows = []
    for name in closure(revision):
        data = subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=ROOT)
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({"path": name, "revision": revision, **identity(target)})
    for row in rows:
        row["uid"] = uid_for(project, row["path"])
    (project / "s08_inputs.json").write_text(json.dumps(
        [{"path": row["path"], "uid": row["uid"]} for row in rows], indent=1) + "\n",
        newline="\n")
    save(task / "staged-input.json", rows)
    config = subprocess.check_output(["git", "show", f"{revision}:project.godot"],
                                     cwd=ROOT).decode()
    config = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", config)
    config = config.replace('config/icon="res://icon.svg"\n', "")
    # Output-delivery condition only: release templates otherwise buffer stdout to pipes/files.
    config = config.replace("[application]\n", "[application]\n"
                            f'run/main_scene="{MAIN}"\nrun/flush_stdout_on_print=true\n', 1)
    (project / "project.godot").write_text(config, newline="\n")
    resources = sorted("res://" + row["path"] for row in rows
                       if not row["path"].endswith((".uid", ".import")))
    presets = []
    for index, mode in enumerate(["release", "debug"]):
        presets.append(
            f'[preset.{index}]\nname="S08 Windows {mode}"\nplatform="Windows Desktop"\n'
            'runnable=true\nexport_filter="resources"\nexport_files=PackedStringArray('
            + ", ".join(json.dumps(name) for name in resources) + ')\n'
            'include_filter="s08_inputs.json"\nexclude_filter=""\nexport_path=""\n'
            'encrypt_pck=false\nencrypt_directory=false\nscript_export_mode=1\n'
            f'[preset.{index}.options]\n'
            f'custom_template/debug={json.dumps(templates["debug"]["path"])}\n'
            f'custom_template/release={json.dumps(templates["release"]["path"])}\n'
            'binary_format/architecture="x86_64"\nbinary_format/embed_pck=false\n'
            'debug/export_console_wrapper=0\napplication/modify_resources=false\n'
            'codesign/enable=false\ntexture_format/s3tc_bptc=true\n'
            'texture_format/etc2_astc=false\n')
    (project / "export_presets.cfg").write_text("\n".join(presets), newline="\n")
    save(task / "scratch-config.json", {
        "project.godot": config, "export_presets.cfg": "\n".join(presets),
        "deviations": ["main scene set to saved S08 main", "flush_stdout_on_print=true",
                       "autoload/editor_plugins/icon removed", "Windows presets added"]})
    return project, rows


def checked(task, phase, argv, budget, env, cwd):
    """Run one bounded engine phase with separate full streams and diagnostic scan."""
    logs = task / phase
    logs.mkdir()
    argv = [*argv, "--log-file", str(logs / "engine.log")]
    command = {"phase": phase, "argv": argv, "cwd": str(cwd), "budget_seconds": budget,
               "started_unix": time.time()}
    with (logs / "stdout.log").open("wb") as out, (logs / "stderr.log").open("wb") as err:
        child = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err)
        try:
            command["exit"] = child.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            child.kill()
            command["exit"] = child.wait(timeout=GRACE_SECONDS)
            command["timeout"] = True
    command["ended_unix"] = time.time()
    text = "".join((logs / name).read_text(errors="replace")
                   for name in ["stdout.log", "stderr.log", "engine.log"]
                   if (logs / name).exists())
    command["diagnostics"] = sorted(set(line.strip() for line in text.splitlines()
                                        if DIAGNOSTIC.search(line)))
    save(logs / "command.json", command)
    return command


def export(task, project, env):
    """Import once, export both modes and bind the actual output folders."""
    engine = shutil.which("godot") if ARGS.godot is None else ARGS.godot
    if engine is None:
        raise RuntimeError("godot not found on PATH; pass --godot")
    version = subprocess.run([engine, "--version"], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    if version != PIN:
        raise RuntimeError(f"expected pinned engine {PIN}; got {version}")
    record = {"engine": {"path": engine, "version": version, **identity(Path(engine))}}
    imported = checked(task, "import", [engine, "--headless", "--editor", "--path",
                                        str(project), "--import", "--quit"],
                       IMPORT_SECONDS, env, project)
    record["import"] = imported
    if imported["exit"] != 0 or imported["diagnostics"]:
        raise RuntimeError("scratch import failed or reported diagnostics")
    folders = {}
    for mode in ["release", "debug"]:
        folder = task / f"export-{mode}"
        folder.mkdir()
        result = checked(task, f"export-{mode}-log", [
            engine, "--headless", "--path", str(project), f"--export-{mode}",
            f"S08 Windows {mode}", str(folder / "FunThingsS08.exe")], EXPORT_SECONDS, env, project)
        record[f"export_{mode}"] = result
        outputs = sorted(path.name for path in folder.iterdir())
        if result["exit"] != 0 or result["diagnostics"] or (
                outputs != ["FunThingsS08.exe", "FunThingsS08.pck"]):
            raise RuntimeError(f"{mode} export failed, reported diagnostics or produced {outputs}")
        name, size, digest = TEMPLATES[mode]
        if identity(folder / "FunThingsS08.exe") != {"bytes": size, "sha256": digest}:
            raise RuntimeError(f"{mode} executable differs from template {name}")
        record[f"folder_{mode}"] = {name: identity(folder / name) for name in outputs}
        folders[mode] = folder
    return record, folders


def read_records(path, offset):
    """Return complete newline-terminated S03/S08 records after a byte offset."""
    with path.open("rb") as stream:
        stream.seek(offset)
        data = stream.read()
    end = data.rfind(b"\n") + 1
    records = []
    position = offset
    for raw in data[:end].splitlines(keepends=True):
        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        for prefix in ("S03 ", "S08 "):
            if line.startswith(prefix):
                try:
                    records.append((prefix.strip(), json.loads(line[4:]), position))
                except json.JSONDecodeError:
                    records.append((prefix.strip(), {"event": "unparsed"}, position))
        position += len(raw)
    return records, offset + end


def stop_children(children, absolute):
    """Shared graceful wait, terminate, then kill; observed exits own reap truth."""
    actions = []
    stages = [("grace", None), ("terminate", "terminate"), ("kill", "kill")]
    for stage_name, method in stages:
        live = [child for child in children if child.poll() is None]
        if not live:
            break
        for child in live:
            if method is not None:
                try:
                    getattr(child, method)()
                    actions.append({"pid": child.pid, "action": method})
                except OSError as error:
                    actions.append({"pid": child.pid, "action": method, "error": str(error)})
        stage_end = min(time.monotonic() + GRACE_SECONDS, absolute - RECEIPT_RESERVE)
        for child in live:
            try:
                child.wait(timeout=max(0.0, stage_end - time.monotonic()))
            except subprocess.TimeoutExpired:
                actions.append({"pid": child.pid, "action": stage_name + "_timeout"})
    return actions, all(child.poll() is not None for child in children)


def observe(task, mode, folder):
    """Run one host/client set with an absolute deadline and retain every receipt."""
    directory = task / f"set-{mode}"
    directory.mkdir()
    started = time.monotonic()
    absolute = started + SET_SECONDS
    work_end = started + WORK_SECONDS
    port = ARGS.port + (0 if mode == "release" else 10)
    proxy_port = port + 1
    executable = folder / "FunThingsS08.exe"
    children, streams, commands, receipts = {}, [], {}, []
    results, offsets, s08 = {}, {}, {}
    failure = None
    proxy_log = (directory / "proxy.jsonl").open("w", newline="\n")
    proxy = Proxy(port, proxy_port, proxy_log)
    readiness = handoff = None
    service = {"wakes": 0, "max_gap_seconds": 0.0}
    try:
        def start(role, target_port):
            logs = directory / role
            logs.mkdir()
            argv = [str(executable), "--headless", "--log-file", str(logs / "engine.log"),
                    "--", f"--role={role}", f"--port={target_port}"]
            out = (logs / "stdout.log").open("wb")
            err = (logs / "stderr.log").open("wb")
            streams.extend([out, err])
            child = subprocess.Popen(argv, cwd=folder, stdout=out, stderr=err,
                                     env=private_env(logs / "user"))
            commands[role] = {"argv": argv, "pid": child.pid,
                              "started_offset_seconds": time.monotonic() - started}
            children[role] = child
            offsets[role] = 0

        start("host", port)
        last_wake = time.monotonic()
        while time.monotonic() < work_end:
            now = time.monotonic()
            service["wakes"] += 1
            service["max_gap_seconds"] = max(service["max_gap_seconds"], now - last_wake)
            last_wake = now
            proxy.poll()
            for role in list(children):
                records, offsets[role] = read_records(directory / role / "stdout.log",
                                                      offsets[role])
                for prefix, record, position in records:
                    receipt = {"role": role, "prefix": prefix, "event": record.get("event"),
                               "parent_offset_seconds": time.monotonic() - started,
                               "byte_offset": position,
                               "live": children[role].poll() is None}
                    receipts.append(receipt)
                    if prefix == "S08":
                        s08[role] = record
                        if record.get("ok") is not True:
                            raise RuntimeError(f"{role} S08 receipt failed")
                        continue
                    event = record.get("event")
                    if event == "ready" and role == "host":
                        readiness = receipt
                    elif event == "snapshots" and role == "host":
                        proxy.armed = True
                        proxy.record("armed")
                    elif event == "result":
                        results[role] = record
                        if record.get("ok") is not True:
                            raise RuntimeError(f"{role} assertion: {record.get('failure')}")
            if readiness and "client" not in children:
                if time.monotonic() - started >= HANDOFF_SECONDS:
                    raise RuntimeError("readiness after the four-second handoff boundary")
                if children["host"].poll() is not None:
                    raise RuntimeError("host exited before client handoff")
                start("client", proxy_port)
                handoff = commands["client"]["started_offset_seconds"]
            if len(results) == 2 and all(child.poll() is not None
                                         for child in children.values()):
                break
            for role, child in children.items():
                if child.poll() is not None and role not in results:
                    raise RuntimeError(f"{role} exited before a result ({child.returncode})")
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("work deadline (20 s) expired")
    except (OSError, RuntimeError, ValueError) as error:
        failure = str(error)
    finally:
        actions, reaped = stop_children(list(children.values()), absolute)
        for stream in streams:
            stream.close()
        proxy.socket.close()
        proxy_log.close()
    # Post-exit full-stream readback preserves results that arrived after a live failure.
    readback = {}
    diagnostics = {}
    for role in children:
        records, _ = read_records(directory / role / "stdout.log", 0)
        readback[role] = [record for prefix, record, _ in records if prefix == "S03"
                          and record.get("event") == "result"]
        text = "".join((directory / role / name).read_text(errors="replace")
                       for name in ["stdout.log", "stderr.log", "engine.log"]
                       if (directory / role / name).exists())
        diagnostics[role] = [line.strip() for line in text.splitlines()
                             if DIAGNOSTIC.search(line)]
    criteria = {
        "s08_receipts": all(s08.get(role, {}).get("ok") is True for role in ["host", "client"]),
        "live_handoff": handoff is not None and handoff < HANDOFF_SECONDS,
        "results_ok": all(results.get(role, {}).get("ok") is True for role in ["host", "client"]),
        "host_cases": results.get("host", {}).get("cases") == HOST_CASES,
        "client_cases": results.get("client", {}).get("cases") == CLIENT_CASES,
        "exits_zero": all(child.returncode == 0 for child in children.values()),
        "proxy_schedule": proxy.count == 5 and proxy.events.count("refresh_subset") == 2,
        "distinct_users": len({results.get(role, {}).get("user_dir") for role in results}) == 2,
        "no_diagnostics": not any(diagnostics.values()),
        "reaped": reaped,
        "within_absolute": time.monotonic() <= absolute,
    }
    result = {"mode": mode, "ok": failure is None and all(criteria.values()),
              "failure": failure, "criteria": criteria, "commands": commands,
              "exits": {role: child.returncode for role, child in children.items()},
              "readiness": readiness, "handoff_seconds": handoff, "results": results,
              "post_exit_results": readback, "s08": {role: {key: s08[role].get(key)
                for key in ["ok", "failures", "user_dir", "executable_sha256", "role"]}
                for role in s08},
              "s08_check_counts": {role: len(s08[role].get("checks", [])) for role in s08},
              "proxy": {"events": proxy.events, "count": proxy.count},
              "service": {**service, "poll_seconds": POLL_SECONDS},
              "diagnostics": diagnostics, "cleanup": actions,
              "duration_seconds": time.monotonic() - started, "receipts": receipts}
    save(directory / "result.json", result)
    return result


def main():
    """Spend one export pass and at most one set per mode; never retry automatically."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--godot", default=None)
    parser.add_argument("--templates", type=Path, required=True,
                        help="already downloaded Godot_v4.8-dev7_export_templates.tpz")
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--modes", nargs="+", choices=["release", "debug"],
                        default=["release", "debug"])
    parser.add_argument("--port", type=int, default=24760)
    parser.add_argument("--output", type=Path)
    global ARGS
    ARGS = parser.parse_args()
    task = (ARGS.output or Path(tempfile.mkdtemp(prefix="s08-windows-"))).resolve()
    if task.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    task.mkdir(parents=True, exist_ok=True)
    if any(task.iterdir()):
        parser.error("output must be a fresh empty directory")
    revision = subprocess.check_output(["git", "rev-parse", ARGS.revision], cwd=ROOT,
                                       text=True).strip()
    summary = {"ok": False, "revision": revision, "platform": platform.platform(),
               "python": sys.version, "poll_seconds": POLL_SECONDS, "sets": {}}
    print(f"S08 Windows evidence: {task}", flush=True)
    try:
        templates = bind_templates(ARGS.templates.resolve(), task)
        project, rows = stage(task, revision, templates)
        summary["closure"] = len(rows)
        record, folders = export(task, project, private_env(task / "export-user"))
        summary["export"] = record
        for mode in ARGS.modes:
            summary["sets"][mode] = observe(task, mode, folders[mode])
        summary["ok"] = all(row["ok"] for row in summary["sets"].values())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        summary["failure"] = str(error)
    save(task / "summary.json", summary)
    brief = {mode: {"ok": row["ok"], "failure": row["failure"], "criteria": row["criteria"]}
             for mode, row in summary["sets"].items()}
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure"), "sets": brief},
                     indent=1))
    return 0 if summary["ok"] else 1


ARGS = None

if __name__ == "__main__":
    raise SystemExit(main())
