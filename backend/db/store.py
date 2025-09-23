import os
import hashlib
from typing import Any, Dict, List, Optional, Tuple

from tinydb import TinyDB, Query  # type: ignore


class CertificateStore:
    """Schemaless store for certificate records and verification logs.

    Backed by TinyDB JSON file for easy local prototyping; can be swapped
    later with MongoDB by implementing the same interface.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        base = os.path.dirname(os.path.abspath(__file__))
        # default ../data/certificates.json
        default_path = os.path.join(base, '..', 'data', 'certificates.json')
        self.db_path = db_path or default_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = TinyDB(self.db_path)
        self.tbl_certs = self.db.table('certificates')
        self.tbl_logs = self.db.table('verifications')

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Insert or update a certificate record.

        Enforces uniqueness on certificate_id (case-insensitive) if provided.
        Returns (inserted, stored_record)
        """
        cert_id = (record.get('certificate_id') or '').strip().lower()
        q = Query()

        if cert_id:
            existing = self.tbl_certs.get(q.certificate_id_lower == cert_id)
            if existing:
                # Update existing record (merge fields)
                merged = {**existing, **record}
                merged['certificate_id_lower'] = cert_id
                self.tbl_certs.update(merged, doc_ids=[existing.doc_id])
                return False, merged

        # New record
        if cert_id:
            record['certificate_id_lower'] = cert_id
        doc_id = self.tbl_certs.insert(record)
        stored = self.tbl_certs.get(doc_id=doc_id)
        return True, stored

    def import_records(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        inserted = 0
        updated = 0
        for r in records:
            ins, _ = self.upsert_record(r)
            if ins:
                inserted += 1
            else:
                updated += 1
        return {"inserted": inserted, "updated": updated, "total": len(records)}

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        cert_id = (certificate_id or '').strip().lower()
        q = Query()
        return self.tbl_certs.get(q.certificate_id_lower == cert_id)

    def find_candidate(self, name: Optional[str], roll: Optional[str], course: Optional[str]) -> Optional[Dict[str, Any]]:
        """Very simple candidate finder for prototype: exact-ish match ignoring case and spaces."""
        def norm(x: Optional[str]) -> str:
            return ''.join((x or '').lower().split())

        n_name, n_roll, n_course = norm(name), norm(roll), norm(course)
        for r in self.tbl_certs:
            if n_roll and norm(r.get('roll_number')) == n_roll:
                if not n_name or norm(r.get('name')) == n_name:
                    if not n_course or norm(r.get('course')) == n_course:
                        return r
        return None

    def log_verification(self, entry: Dict[str, Any]) -> int:
        return self.tbl_logs.insert(entry)
