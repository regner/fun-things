"""Owned file delivery for local supervisor controls; MCP requests remain unchanged."""
import hashlib
import json
from pathlib import Path


def read_request(control, scope):
    """Validate complete owned file bytes before issuing an unchanged SDK request."""
    path = Path(control['request_file']).resolve(strict=True)
    if not path.is_relative_to(scope.resolve()) or not path.is_file():
        raise ValueError('request file outside owned scope')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != control['sha256']:
        raise ValueError('request file hash differs')
    request = json.loads(raw)
    if not isinstance(request, dict) or not isinstance(request.get('method'), str):
        raise ValueError('request requires method')
    return request, raw
