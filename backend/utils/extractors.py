import re
from typing import Any, Dict, Optional

try:
    from pyzbar.pyzbar import decode as qr_decode  # type: ignore
    _QR_AVAILABLE = True
except Exception:
    _QR_AVAILABLE = False

from PIL import Image


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """Very simple regex-based field extraction prototype.

    Looks for certificate id, roll number, name, course in plain text.
    This is heuristic and should be replaced with proper templates/ML later.
    """
    patterns = {
        'certificate_id': r'(?:Certificate\s*ID|Cert(?:ificate)?\s*No\.?|Serial\s*No\.?)[\s:]*([A-Za-z0-9\-/]+)',
        'roll_number': r'(?:Roll\s*No\.?|Enrollment\s*No\.?|Reg(?:istration)?\s*No\.?)[\s:]*([A-Za-z0-9\-/]+)',
        'name': r'(?:Name|Student\s*Name|Candidate)\s*[:\-\s]*([A-Za-z ,\-.]+)',
        'course': r'(?:Course|Programme|Degree)\s*[:\-\s]*([A-Za-z0-9 &\-.]+)',
    }

    out: Dict[str, Optional[str]] = {k: None for k in patterns}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            out[key] = m.group(1).strip()
    return out


def extract_qr_content(image: Image.Image) -> Optional[str]:
    if not _QR_AVAILABLE:
        return None
    try:
        results = qr_decode(image)
        for r in results:
            data = r.data.decode('utf-8', errors='ignore').strip()
            if data:
                return data
    except Exception:
        return None
    return None
