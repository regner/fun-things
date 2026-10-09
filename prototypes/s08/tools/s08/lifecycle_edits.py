#!/usr/bin/env python3
"""Declare log-only S03 toolkit replacements and verify removal recovers the exact base."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '233493abc7d2e3c106fb620105cfb766f542813b'
EDITS = {
    'session.gd': [
        ('signal changed()\n', 'signal changed()\nsignal close_started(outcome: String)\n'),
        ('\tclose_outcome = outcome\n', '\tclose_outcome = outcome\n\tclose_started.emit(outcome)\n'),
    ],
    'proof.gd': [
        ('var snapshots_done: bool = false\n',
         'var snapshots_done: bool = false\nvar diagnostic_state: String = ""\n'),
        ('\tsession.completed.connect(_completed)\n',
         '\tsession.completed.connect(_completed)\n'
         '\tsession.changed.connect(_session_changed)\n'
         '\tsession.close_started.connect(_close_started)\n'),
        ('\t\tawait _client()\n', '\t\tawait _client()\n'),
        ('\toutcomes.clear()\n\treplication.send_held(envelope)\n',
         '\toutcomes.clear()\n'
         '\t_emit("held_send", { "sequence": envelope.get("sequence"), "expected": expected })\n'
         '\treplication.send_held(envelope)\n'),
        ('\tbaseline_count += 1\n',
         '\tbaseline_count += 1\n\t_emit("baseline_installed", { "baseline": _baseline_id })\n'),
        ('\tcompletions[source_operation].append(outcome)\n',
         '\tcompletions[source_operation].append(outcome)\n'
         '\t_emit("completed", { "source_operation": source_operation, "outcome": outcome })\n'),
        ('\toutcomes.append(reason)\n', '\toutcomes.append(reason)\n'
         '\t_emit("held_receipt", { "sequence": _sequence, "reason": reason })\n'),
        ('\tdata.event = event\n', '\tdata.event = event\n'
         '\tdata.ticks_usec = Time.get_ticks_usec()\n'
         '\tdata.clock_domain = "engine_elapsed_usec_pid_" + str(OS.get_process_id())\n'
         '\tdata.pid = OS.get_process_id()\n\tdata.role = role\n'
         '\tdata.phase = session.phase\n\tdata.operation = session.operation_id\n'
         '\tdata.close_outcome = session.close_outcome\n'
         '\tdata.session_deadline_ms = session.deadline_ms\n'
         '\tdata.case_deadline_ms = deadline_ms\n'),
        ('## Assert host-owned provisional rollback, admission and simulation outcomes.\n',
         '## Observe host simulation changes without deciding or rewriting outcomes.\n'
         'func _physics_process(_delta: float) -> void:\n'
         '\tif role != "host" or match_state == null:\n\t\treturn\n\n'
         '\tvar rows: Dictionary = {}\n'
         '\tfor participant: int in match_state.bindings:\n'
         '\t\trows[participant] = match_state.bindings[participant].duplicate()\n\n'
         '\tvar state: Dictionary = {"bindings": rows, "accepted": match_state.accepted_count,\n'
         '\t\t"rejected": match_state.rejected.duplicate()}\n'
         '\tvar signature: String = JSON.stringify(state)\n'
         '\tif signature != diagnostic_state:\n'
         '\t\tdiagnostic_state = signature\n\t\t_emit("simulation_observed", state)\n\n\n'
         '## Assert host-owned provisional rollback, admission and simulation outcomes.\n'),
        ('## Count completed baseline applications.\n',
         '## Timestamp published session state in this process clock domain.\n'
         'func _session_changed() -> void:\n'
         '\t_emit("session_changed", { "participant": session.local_participant })\n\n\n'
         '## Record close initiation before peer replacement and match teardown.\n'
         'func _close_started(outcome: String) -> void:\n'
         '\t_emit("close_started", { "outcome": outcome })\n\n\n'
         '## Count completed baseline applications.\n'),
    ],
}
# Identity entry is retained only for readable grouping, not sent as a no-op edit.
EDITS['proof.gd'] = [(old, new) for old, new in EDITS['proof.gd'] if old != new]


def base_source(name):
    """Read the immutable script rather than an editor or cached stage."""
    return subprocess.check_output(['git', 'show', BASE + ':tests/fixtures/s03/' + name],
                                   cwd=ROOT).decode()


def candidate(name):
    """Compute intended toolkit input; never write an editor-managed source directly."""
    source = base_source(name)
    for old, new in EDITS[name]:
        if source.count(old) != 1:
            raise RuntimeError('replacement not unique: ' + name)
        source = source.replace(old, new)
    restored = source
    for old, new in reversed(EDITS[name]):
        if restored.count(new) != 1:
            raise RuntimeError('inverse not unique: ' + name)
        restored = restored.replace(new, old)
    if restored != base_source(name):
        raise RuntimeError('log-only inverse differs')
    return source


def main():
    """Prepare exact requests or independently read back saved diagnostic bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.requests:
        args.requests.mkdir(parents=True, exist_ok=False)
    for index, name in enumerate(EDITS, 1):
        source = candidate(name)
        if args.requests:
            request = {'name': 'script_edit', 'args': {
                'file_path': 'res://tests/fixtures/s03/' + name,
                'old_string': base_source(name), 'new_string': source}}
            (args.requests / f'{index:03}.json').write_text(json.dumps(request) + '\n')
        if args.verify:
            if (args.verify / 'tests/fixtures/s03' / name).read_text() != source:
                raise RuntimeError('saved toolkit bytes differ: ' + name)
        print(json.dumps({'script': name, 'sha256': hashlib.sha256(source.encode()).hexdigest(),
                          'inverse_recovers_base': True}))


if __name__ == '__main__':
    main()
