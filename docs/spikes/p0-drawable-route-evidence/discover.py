"""Retain finite read-only public-source and display-capability discovery receipts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent
REVISION = 'c971f93e7e76b0ef919bf6009e7b868bea04db7f'
SOURCES = [
    'main/main.cpp',
    'platform/linuxbsd/wayland/display_server_wayland.cpp',
    'servers/rendering/rendering_server_default.cpp',
    'servers/movie_writer/movie_writer.cpp',
    'servers/movie_writer/movie_writer_pngwav.cpp',
    'doc/classes/RenderingServer.xml',
    'doc/classes/MovieWriter.xml',
]
COMMANDS = [
    ['wayland-info'],
    ['xrandr', '--query'],
    ['xdpyinfo'],
    ['bash', '-c', 'for t in wayland-info xrandr xdpyinfo Xvfb Xwayland weston '
     'gamescope vulkaninfo eglinfo curl; do command -v "$t" || true; done; '
     'ls -l /tmp/.X11-unix /run/user/1000/wayland-* /dev/dri; '
     'for p in /sys/class/drm/card1-*/status; do printf "%s " "$p"; '
     'read -r state < "$p"; printf "%s\\n" "$state"; done'],
]


def retain(path, data):
    """Write exact acquisition bytes and return their independently readable identity."""
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    """Acquire only declared public files and non-mutating display metadata once."""
    rows = []
    for source in SOURCES:
        url = f'https://raw.githubusercontent.com/godotengine/godot/{REVISION}/{source}'
        row = {'url': url, 'revision': REVISION}
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = response.read(2 * 1024 * 1024)
                row['status'] = response.status
            row['payload'] = retain('source/' + source, data)
        except Exception as error:
            row['failure'] = repr(error)
        rows.append(row)
    for index, argv in enumerate(COMMANDS):
        result = subprocess.run(argv, capture_output=True, timeout=15, check=False)
        rows.append({'argv': argv, 'exit': result.returncode,
                     'stdout': retain(f'inventory/{index}.stdout', result.stdout),
                     'stderr': retain(f'inventory/{index}.stderr', result.stderr)})
    rows.append({'environment': {key: os.environ.get(key) for key in
                 ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR', 'XDG_SESSION_TYPE']}})
    (ROOT / 'acquisition.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    main()
