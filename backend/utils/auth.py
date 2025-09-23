import json
import os
from typing import Dict, Optional


class AuthError(Exception):
    pass


def _load_keys() -> Dict[str, Dict[str, str]]:
    """Load API keys from env ADMIN_KEYS (JSON) or use a default demo key.

    Format example:
      ADMIN_KEYS='[{"key":"demo-admin-key","role":"superadmin","issuer_id":"*"}]'
    """
    raw = os.getenv('ADMIN_KEYS')
    mapping: Dict[str, Dict[str, str]] = {}
    if raw:
        try:
            arr = json.loads(raw)
            for x in arr:
                mapping[x['key']] = { 'role': x.get('role','admin'), 'issuer_id': x.get('issuer_id','*') }
            return mapping
        except Exception:
            pass
    # Default fallback demo key
    mapping['demo-admin-key'] = { 'role': 'superadmin', 'issuer_id': '*' }
    return mapping


_KEYS = _load_keys()


def require_api_key(headers) -> Dict[str, str]:
    key = headers.get('X-API-Key') or headers.get('x-api-key')
    if not key:
        raise AuthError('Missing X-API-Key')
    user = _KEYS.get(key)
    if not user:
        raise AuthError('Invalid API key')
    return { 'api_key': key, **user }
