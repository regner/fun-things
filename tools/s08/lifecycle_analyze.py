#!/usr/bin/env python3
"""Independent literal expectations for retained S03 traces; never launches runtime or imports."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path

HOST_CASES = ['provisional_rollback', 'authority_validation_and_expiry']
CLIENT_CASES = ['provider_substitution_late_cleanup', 'baseline_cancel_retry',
                'held_window_resync', 'subset_reorder_loss_recovery']
HELD = ['NOT_ADMITTED', 'OK', 'STALE_SEQUENCE', 'STALE_CONTEXT', 'INVALID', 'INVALID',
        'WINDOW', 'WINDOW', 'WINDOW', 'NOT_ADMITTED', 'STALE_CONTEXT', 'OK']
SCHEDULE = ['armed', 'hold_subset_A', 'deliver_B_then_A', 'drop_subset_A',
            'refresh_subset', 'refresh_subset']


def events(directory, role):
    """Read every actual role record, including records after the live consumer stopped."""
    return [json.loads(line[4:]) for line in (directory / role / 'stdout.log').read_text().splitlines()
            if line.startswith('S03 ')]


def verify(directory, release=False, override=None):
    """Assert independently declared outcomes while reporting strict diagnostics separately."""
    record = json.loads((directory / 'result.json').read_text())
    logs = {role: events(directory, role) for role in ['host', 'client']}
    if override is not None:
        logs = override
    for role, expected in [('host', HOST_CASES), ('client', CLIENT_CASES)]:
        terminal = [event for event in logs[role] if event['event'] == 'result']
        assert len(terminal) == 1 and terminal[0]['ok'] is True
        assert terminal[0]['cases'] == expected
        command = json.loads((directory / role / 'command.json').read_text())
        assert command['exit'] == 0 and command['reaped'] is True
        assert all(event['pid'] == command['pid'] for event in logs[role])
        assert all(event['role'] == role for event in logs[role])
        ticks = [event['ticks_usec'] for event in logs[role]]
        assert ticks == sorted(ticks)
        assert all(event['clock_domain'] == 'engine_elapsed_usec_pid_' + str(command['pid'])
                   for event in logs[role])
    assert [event['reason'] for event in logs['client'] if event['event'] == 'held_receipt'] == HELD
    assert [event['expected'] for event in logs['client'] if event['event'] == 'held_send'] == HELD
    host_result = next(event for event in logs['host'] if event['event'] == 'result')
    client_result = next(event for event in logs['client'] if event['event'] == 'result')
    assert 0 < host_result['baseline_bytes'] <= 8192
    assert 0 < host_result['max_held_bytes'] <= 1200
    assert 0 < host_result['max_movement_bytes'] <= 1200
    assert client_result['movement_received'] == 5
    assert host_result['user_dir'] != client_result['user_dir']
    assert host_result['close_outcome'] == 'LEFT' and host_result['phase'] == 'IDLE'
    assert client_result['close_outcome'] == 'HOST_LOST' and client_result['phase'] == 'IDLE'
    simulation = [event for event in logs['host'] if event['event'] == 'simulation_observed']
    assert any(any(row['health'] == 75 for row in event['bindings'].values()) for event in simulation)
    assert any(any(row['health'] == 70 and row['control'] == 2
                   for row in event['bindings'].values()) for event in simulation)
    final = next(event for event in reversed(simulation) if event['bindings'])
    assert final['accepted'] == 2
    assert final['rejected'] == {'NOT_ADMITTED': 2, 'STALE_SEQUENCE': 1,
        'STALE_CONTEXT': 2, 'INVALID': 2, 'WINDOW': 3}
    assert all(row['held'] == 0.0 for row in final['bindings'].values())
    assert any(any(row['held'] == 1.0 for row in event['bindings'].values()) for event in simulation)
    packets = [json.loads(line) for line in (directory / 'traffic.jsonl').read_text().splitlines()]
    counts = Counter()
    for packet in packets:
        assert packet['bytes'] > 0 and len(packet['sha256']) == 64
        assert packet['clock_domain'] == 'supervisor_python_monotonic'
        counts[packet['event'] + '_datagrams'] += 1
        counts[packet['event'] + '_bytes'] += packet['bytes']
    assert dict(counts) == record['traffic']
    assert counts['recv_datagrams'] - counts['send_datagrams'] == 1
    assert counts['recv_bytes'] - counts['send_bytes'] == 246
    schedule = [json.loads(line) for line in (directory / 'proxy.jsonl').read_text().splitlines()]
    assert [row['event'] for row in schedule] == SCHEDULE
    assert all(row['datagram_bytes'] == 246 for row in schedule[1:])
    assert record['proxy_count'] == 5
    assert record['cleanup']['all_children_reaped'] and record['cleanup']['streams_closed']
    assert record['cleanup']['proxy_closed'] and not record['cleanup']['errors']
    observations = record['observations']
    host_close = next(row for row in observations if row.get('record', {}).get('event') == 'close_started'
                      and row['role'] == 'host' and row['record']['outcome'] == 'LEFT')
    client_close = next(row for row in observations if row.get('record', {}).get('event') == 'close_started'
                        and row['role'] == 'client' and row['record']['outcome'] == 'HOST_LOST')
    exits = [row for row in observations if row.get('event') == 'exit_observed']
    assert len(exits) == 2
    assert host_close['host_poll'] is None and client_close['host_poll'] is None
    assert host_close['monotonic'] < client_close['monotonic'] < min(row['monotonic'] for row in exits)
    diagnostics = {}
    for role in ['host', 'client']:
        diagnostics[role] = [line for line in (directory / role / 'stderr.log').read_text().splitlines()
                             if 'ERROR:' in line or 'WARNING:' in line]
    assert {role: len(lines) for role, lines in diagnostics.items()} == (
        {'host': 2, 'client': 6} if release else {'host': 0, 'client': 0})
    assert record['gameplay_ok'] is True and record['ok'] is (not release)
    return {'matrix': 'PASS', 'strict_diagnostics': 'FAIL' if release else 'PASS',
        'traffic': dict(counts), 'errors_by_role': {role: len(lines) for role, lines in diagnostics.items()},
        'host_left_receipt': host_close['monotonic'], 'client_host_lost_receipt': client_close['monotonic'],
        'exit_observations': exits, 'duration_seconds': record['duration_seconds'],
        'limits': 'Healthy teardown ordering; does not reproduce historical stall or establish a fix.'}


def main():
    """Check both real traces and prove a wrong held receipt cannot be accepted."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    args = parser.parse_args()
    result = {'debug': verify(args.debug), 'release': verify(args.release, True)}
    wrong = {role: copy.deepcopy(events(args.release, role)) for role in ['host', 'client']}
    next(event for event in wrong['client'] if event['event'] == 'held_receipt')['reason'] = 'WRONG'
    try:
        verify(args.release, True, wrong)
    except AssertionError:
        result['independent_negative'] = 'wrong held receipt rejected'
    else:
        raise AssertionError('wrong held receipt accepted')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
