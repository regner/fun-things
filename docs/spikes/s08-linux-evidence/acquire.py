"""Acquire exactly the commissioned archive once and retain the outcome."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).parent
receipt_dir = root / 'acquisition'
space = json.loads((receipt_dir / 'space.json').read_text())
if not space['sufficient']:
    raise SystemExit('STOP: insufficient disk headroom')
archive = root / 'Godot_v4.8-dev7_export_templates.tpz'
if archive.exists() or (receipt_dir / 'download.json').exists():
    raise SystemExit('STOP: acquisition already attempted')
url = 'https://github.com/godotengine/godot-builds/releases/download/4.8-dev7/Godot_v4.8-dev7_export_templates.tpz'
argv = ['curl', '--location', '--fail', '--retry', '0', '--connect-timeout', '30',
        '--max-time', '600', '--output', str(archive), '--write-out',
        '%{http_code} %{size_download} %{time_total}\n', url]
record = {'argv': argv, 'requested_url': url, 'published_asset': 603460756,
          'expected_bytes': 1436879719,
          'expected_sha256': '95c2677555b4f66c7eeca1a41368674703497e1907aad3fe56576423ca3c8cc6',
          'attempt': 1, 'started_unix': time.time()}
(receipt_dir / 'download.json').write_text(json.dumps(record, indent=2)+'\n')
with (receipt_dir / 'stdout.log').open('wb') as out, (receipt_dir / 'stderr.log').open('wb') as err:
    child = subprocess.Popen(argv, stdout=out, stderr=err)
    record['owned_pid'] = child.pid
    try:
        record['exit'] = child.wait(timeout=602)
    except subprocess.TimeoutExpired:
        child.terminate()
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
        record['exit'] = child.returncode
        record['timeout'] = True
record['ended_unix'] = time.time()
record['child_reaped'] = child.poll() is not None
record['actual_bytes'] = archive.stat().st_size if archive.exists() else 0
if archive.exists():
    with archive.open('rb') as stream:
        record['actual_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
record['ok'] = (record['exit'] == 0 and not record.get('timeout') and
                record['actual_bytes'] == record['expected_bytes'] and
                record.get('actual_sha256') == record['expected_sha256'])
(receipt_dir / 'download.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
raise SystemExit(0 if record['ok'] else 1)
