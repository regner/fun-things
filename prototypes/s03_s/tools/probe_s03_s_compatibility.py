#!/usr/bin/env python3
"""One finite static/synthetic probe; never imports Godot or calls Steam networking."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/spikes/s03-s-compatibility-evidence'


def function(source: str, signature: str) -> tuple[str, int]:
    """Extract one exact pinned C++ body; this is inspection, not C++ execution."""
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end], source.count('\n', 0, start) + 1


def ordered(trace: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Model four stream-local watermarks with no retransmission or reorder history."""
    watermarks = [0] * 4
    accepted = []
    for stream, sequence in trace:
        assert 0 <= stream < 4 and sequence > 0
        if sequence > watermarks[stream]:
            watermarks[stream] = sequence
            accepted.append((stream, sequence))
    return accepted


def main() -> None:
    """Verify exact sources and emit finite counterexamples with explicit evidence kinds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((EVIDENCE / 'sources.json').read_text())
    sources = {}
    for entry in manifest['files']:
        data = (args.source_dir / entry['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['file']
        sources[entry['file']] = data.decode()
    cpp = sources['godotsteam.cpp']
    facts = {}
    for name, signature in {
        'sendMessageToConnection': 'Dictionary Steam::sendMessageToConnection(',
        'sendMessages': 'PackedInt64Array Steam::sendMessages(',
        'receiveMessagesOnConnection': 'Array Steam::receiveMessagesOnConnection(',
        'receiveMessagesOnPollGroup': 'Array Steam::receiveMessagesOnPollGroup(',
        'configureConnectionLanes': 'int Steam::configureConnectionLanes(',
        'getConnectionRealTimeStatus': 'Dictionary Steam::getConnectionRealTimeStatus(',
        'network_connection_status_changed': 'void Steam::network_connection_status_changed(',
        'createLobby': 'void Steam::createLobby(',
        'joinLobby': 'void Steam::joinLobby(',
    }.items():
        body, line = function(cpp, signature)
        facts[name] = {
            'line': line, 'signature': body.split('{', 1)[0].strip(),
            'mentions_lane_index': 'm_idxLane' in body,
            'dictionary_keys': sorted(set(re.findall(r'\["([^"\n]+)"\]', body))),
        }
    assert not facts['sendMessageToConnection']['mentions_lane_index']
    assert not facts['sendMessages']['mentions_lane_index']
    for name in ['receiveMessagesOnConnection', 'receiveMessagesOnPollGroup']:
        assert not facts[name]['mentions_lane_index']
        assert {'message_number', 'flags', 'payload', 'connection'} <= set(
            facts[name]['dictionary_keys'])
    send, _ = function(cpp, 'PackedInt64Array Steam::sendMessages(')
    facts['sendMessages']['release_before_native_send'] = (
        send.index('SteamAPI_SteamNetworkingMessage_t_Release(message)')
        < send.index('SteamAPI_ISteamNetworkingSockets_SendMessages('))
    facts['sendMessages']['allocation_expression_is_variant_size'] = 'sizeof(messages[i])' in send
    assert facts['sendMessages']['release_before_native_send']
    assert facts['sendMessages']['allocation_expression_is_variant_size']
    packet = sources['steam_packet_peer.cpp']
    send, line = function(packet, 'Error SteamPacketPeer::send(')
    assert 'p_channel >= (configured_lanes - 1)' in send
    assert 'messages, nullptr, false' in send and 'return OK' in send
    bind, _ = function(packet, 'void SteamPacketPeer::_bind_methods(')
    assert 'D_METHOD("send"' not in bind
    put, _ = function(packet, 'Error SteamPacketPeer::put_packet(')
    assert 'send(0, p_buffer, p_buffer_size, k_nSteamNetworkingSend_Reliable)' in put
    facts['SteamPacketPeer::send'] = {
        'line': line, 'native_send_result_discarded': True,
        'send_not_script_bound': True, 'public_put_defaults_reliable_lane_zero': True,
    }
    mode, line = function(sources['godotsteam_multiplayer_peer.cpp'],
                          'const int SteamMultiplayerPeer::_get_steam_packet_flags(')
    ordered_case = mode.split('case TransferMode::TRANSFER_MODE_UNRELIABLE_ORDERED:')[1]
    assert 'return k_nSteamNetworkingSend_Reliable | flags' in ordered_case
    facts['ordered_unreliable'] = {'line': line, 'source_maps_to_reliable': True}

    # Independent expected traces come from criteria.md; no model of Steam timing.
    reordered = ordered([(2, 2), (2, 1), (2, 2)])
    independent = ordered([(2, 20), (3, 1), (2, 19), (3, 2)])
    assert reordered == [(2, 2)]
    assert independent == [(2, 20), (3, 1), (3, 2)]
    subsets = ordered([(3, 101), (3, 100), (3, 103), (3, 104)])
    rows = {100: ('A', 100), 101: ('B', 101), 103: ('B', 103), 104: ('A', 104)}
    entity_freshness = {}
    for _, sequence in subsets:
        entity, tick = rows[sequence]
        entity_freshness[entity] = tick
    assert entity_freshness == {'A': 104, 'B': 103}

    # A pair of possible native observations projects to the same wrapper fields.
    # Payload deliberately identical: the adapter must carry arbitrary Godot bytes.
    observations = [{'lane': 2, 'number': 1, 'flags': 0, 'payload': 'same'},
                    {'lane': 3, 'number': 1, 'flags': 0, 'payload': 'same'}]
    projected = [{k: v for k, v in row.items() if k != 'lane'} for row in observations]
    assert projected[0] == projected[1]
    print(json.dumps({
        'source_ref': manifest['ref'], 'source_kind': 'static exact-source inspection',
        'facts': facts,
        'model_kind': 'synthetic finite traces, NOT Steam/native delivery or lifecycle',
        'reorder_duplicate': reordered, 'independent_streams': independent,
        'lost_102_subset_refresh': entity_freshness,
        'lane_metadata_collision': {'possible_native': observations, 'wrapper': projected},
        'default_channel_projection': [0, 1, 2, 0],
        'five_lane_projection': [0, 1, 2, 3],
        'native_network_calls': 0,
        'bounds': {'streams': 4, 'watermarks': 4, 'example_entities': 2,
                   'largest_trace': 4, 'reorder_history': 0},
    }, indent=2))


if __name__ == '__main__':
    main()
