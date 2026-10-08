#!/usr/bin/env python3
"""Retrieve only declared public Valve sources; retain failures and exact byte hashes."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SCRATCH = Path('/tmp/s03-s-valve-api-public')
REV = 'd534c19aa760df3fb75fd20db13ba1932b8a5463'
URLS = {
    'api-common.h': f'https://raw.githubusercontent.com/ValveSoftware/GameNetworkingSockets/{REV}/include/steam/steam_api_common.h',
    'messages.h': f'https://raw.githubusercontent.com/ValveSoftware/GameNetworkingSockets/{REV}/include/steam/isteamnetworkingmessages.h',
    'utils.h': f'https://raw.githubusercontent.com/ValveSoftware/GameNetworkingSockets/{REV}/include/steam/isteamnetworkingutils.h',
    'gns-readme.md': f'https://raw.githubusercontent.com/ValveSoftware/GameNetworkingSockets/{REV}/README.md',
    'license': f'https://raw.githubusercontent.com/ValveSoftware/GameNetworkingSockets/{REV}/LICENSE',
    **{name: 'https://partner.steamgames.com/doc/' + locator for name, locator in {
        'sockets.html': 'api/ISteamNetworkingSockets',
        'messages.html': 'api/ISteamNetworkingMessages',
        'utils.html': 'api/ISteamNetworkingUtils',
        'types.html': 'api/steamnetworkingtypes',
        'matchmaking.html': 'api/ISteamMatchmaking',
        'steam-utils.html': 'api/ISteamUtils',
        'sdk-api.html': 'sdk/api',
        'sdr.html': 'features/multiplayer/steamdatagramrelay',
        'friends.html': 'api/ISteamFriends',
    }.items()},
}


def main():
    """Fetch each declared URL at most once, adding only new sources on later calls."""
    SCRATCH.mkdir(exist_ok=True)
    (ROOT / 'retrieval').mkdir(exist_ok=True)
    records = json.loads((ROOT / 'retrieval.json').read_text()) if (ROOT / 'retrieval.json').exists() else []
    for name, url in URLS.items():
        if any(r['name'] == name for r in records):
            continue
        output = SCRATCH / name
        argv = ['curl', '--fail', '--location', '--max-time', '30', '--silent',
                '--show-error', '--output', str(output), url]
        result = subprocess.run(argv, capture_output=True)
        (ROOT / 'retrieval' / (name + '.stdout')).write_bytes(result.stdout)
        (ROOT / 'retrieval' / (name + '.stderr')).write_bytes(result.stderr)
        record = {'name': name, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                  'argv': argv, 'exit': result.returncode,
                  'stdout': 'retrieval/' + name + '.stdout',
                  'stderr': 'retrieval/' + name + '.stderr'}
        if result.returncode == 0:
            data = output.read_bytes()
            record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        records.append(record)
        print(name, result.returncode, record.get('bytes'))
    (ROOT / 'retrieval.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    main()
