import os
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

try:
    from pymongo import MongoClient, ASCENDING
    from pymongo.collection import Collection
    from pymongo.database import Database
    from dotenv import load_dotenv
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Fallback to TinyDB if MongoDB is not available
try:
    from tinydb import TinyDB, Query
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False

# Load environment variables
if MONGODB_AVAILABLE:
    load_dotenv()


class CertificateStore:
    """Hybrid store that can use MongoDB or TinyDB based on availability.
    
    Priority:
    1. MongoDB (if available and configured)
    2. TinyDB (fallback for development)
    3. In-memory storage (last resort)
    """

    def __init__(self, connection_string: Optional[str] = None, database_name: Optional[str] = None, db_path: Optional[str] = None) -> None:
        self.db_type = None
        self.client = None
        self.db = None
        self.certificates = None
        self.verifications = None
        
        # Try MongoDB first
        if MONGODB_AVAILABLE:
            try:
                self._init_mongodb(connection_string, database_name)
                print("✅ Using MongoDB for data storage")
                return
            except Exception as e:
                print(f"⚠️  MongoDB connection failed: {e}")
                print("   Falling back to TinyDB...")
        
        # Fallback to TinyDB
        if TINYDB_AVAILABLE:
            try:
                self._init_tinydb(db_path)
                print("✅ Using TinyDB for data storage")
                return
            except Exception as e:
                print(f"⚠️  TinyDB initialization failed: {e}")
                print("   Using in-memory storage...")
        
        # Last resort: in-memory storage
        self._init_memory_storage()
        print("⚠️  Using in-memory storage (data will not persist)")

    def _init_mongodb(self, connection_string: Optional[str], database_name: Optional[str]) -> None:
        """Initialize MongoDB connection."""
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name or os.getenv('MONGODB_DATABASE', 'certificate_verification_db')
        
        # Test connection
        self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
        self.client.admin.command('ping')  # This will raise an exception if connection fails
        
        self.db = self.client[self.database_name]
        self.certificates = self.db.certificates
        self.verifications = self.db.verifications
        self.db_type = "mongodb"
        
        # Create indexes
        self._create_mongodb_indexes()

    def _init_tinydb(self, db_path: Optional[str]) -> None:
        """Initialize TinyDB connection."""
        base = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(base, '..', 'data', 'certificates.json')
        self.db_path = db_path or default_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.db = TinyDB(self.db_path)
        self.certificates = self.db.table('certificates')
        self.verifications = self.db.table('verifications')
        self.db_type = "tinydb"

    def _init_memory_storage(self) -> None:
        """Initialize in-memory storage as last resort."""
        self.certificates = []
        self.verifications = []
        self.db_type = "memory"
        self._memory_cert_counter = 0
        self._memory_log_counter = 0

    def _create_mongodb_indexes(self) -> None:
        """Create MongoDB indexes for better performance."""
        if self.db_type != "mongodb":
            return
        
        try:
            self.certificates.create_index([("certificate_id_lower", ASCENDING)], unique=False)
            self.certificates.create_index([("file_hash", ASCENDING)], unique=False)
            self.verifications.create_index([("timestamp", ASCENDING)])
            self.certificates.create_index([
                ("name_normalized", ASCENDING),
                ("roll_number_normalized", ASCENDING),
                ("course_normalized", ASCENDING)
            ])
        except Exception:
            pass  # Indexes might already exist

    def _normalize_string(self, text: Optional[str]) -> str:
        """Normalize string for better search matching."""
        if not text:
            return ""
        return ''.join(text.lower().split())

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Insert or update a certificate record."""
        if self.db_type == "mongodb":
            return self._mongodb_upsert_record(record)
        elif self.db_type == "tinydb":
            return self._tinydb_upsert_record(record)
        else:
            return self._memory_upsert_record(record)

    def _mongodb_upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """MongoDB implementation of upsert_record."""
        cert_id = (record.get('certificate_id') or '').strip().lower()
        record['updated_at'] = datetime.utcnow()
        
        if cert_id:
            record['certificate_id_lower'] = cert_id
            existing = self.certificates.find_one({"certificate_id_lower": cert_id})
            if existing:
                merged = {**existing, **record}
                merged['certificate_id_lower'] = cert_id
                self.certificates.update_one({"_id": existing["_id"]}, {"$set": merged})
                updated = self.certificates.find_one({"_id": existing["_id"]})
                return False, updated

        if cert_id:
            record['certificate_id_lower'] = cert_id
        
        record['name_normalized'] = self._normalize_string(record.get('name', ''))
        record['roll_number_normalized'] = self._normalize_string(record.get('roll_number', ''))
        record['course_normalized'] = self._normalize_string(record.get('course', ''))
        record['created_at'] = datetime.utcnow()
        
        result = self.certificates.insert_one(record)
        stored = self.certificates.find_one({"_id": result.inserted_id})
        return True, stored

    def _tinydb_upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """TinyDB implementation of upsert_record."""
        cert_id = (record.get('certificate_id') or '').strip().lower()
        q = Query()

        if cert_id:
            existing = self.certificates.get(q.certificate_id_lower == cert_id)
            if existing:
                merged = {**existing, **record}
                merged['certificate_id_lower'] = cert_id
                self.certificates.update(merged, doc_ids=[existing.doc_id])
                return False, merged

        if cert_id:
            record['certificate_id_lower'] = cert_id
        doc_id = self.certificates.insert(record)
        stored = self.certificates.get(doc_id=doc_id)
        return True, stored

    def _memory_upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """In-memory implementation of upsert_record."""
        cert_id = (record.get('certificate_id') or '').strip().lower()
        
        if cert_id:
            record['certificate_id_lower'] = cert_id
            # Check for existing record
            for i, existing in enumerate(self.certificates):
                if existing.get('certificate_id_lower') == cert_id:
                    merged = {**existing, **record}
                    self.certificates[i] = merged
                    return False, merged
        
        # New record
        self._memory_cert_counter += 1
        record['doc_id'] = self._memory_cert_counter
        if cert_id:
            record['certificate_id_lower'] = cert_id
        
        self.certificates.append(record)
        return True, record

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get certificate by ID."""
        cert_id = (certificate_id or '').strip().lower()
        
        if self.db_type == "mongodb":
            return self.certificates.find_one({"certificate_id_lower": cert_id})
        elif self.db_type == "tinydb":
            q = Query()
            return self.certificates.get(q.certificate_id_lower == cert_id)
        else:
            for record in self.certificates:
                if record.get('certificate_id_lower') == cert_id:
                    return record
            return None

    def find_candidate(self, name: Optional[str], roll: Optional[str], course: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find candidate by name, roll, or course."""
        if self.db_type == "mongodb":
            return self._mongodb_find_candidate(name, roll, course)
        else:
            return self._fallback_find_candidate(name, roll, course)

    def _mongodb_find_candidate(self, name: Optional[str], roll: Optional[str], course: Optional[str]) -> Optional[Dict[str, Any]]:
        """MongoDB implementation of find_candidate."""
        query = {}
        
        if roll:
            n_roll = self._normalize_string(roll)
            if n_roll:
                query["roll_number_normalized"] = n_roll
        
        if name:
            n_name = self._normalize_string(name)
            if n_name:
                query["name_normalized"] = n_name
        
        if course:
            n_course = self._normalize_string(course)
            if n_course:
                query["course_normalized"] = n_course
        
        if query:
            result = self.certificates.find_one(query)
            if result:
                return result
        
        # Fallback search
        if roll:
            n_roll = self._normalize_string(roll)
            candidates = list(self.certificates.find({"roll_number_normalized": n_roll}))
            for candidate in candidates:
                if name and self._normalize_string(candidate.get('name', '')) != self._normalize_string(name):
                    continue
                if course and self._normalize_string(candidate.get('course', '')) != self._normalize_string(course):
                    continue
                return candidate
        
        return None

    def _fallback_find_candidate(self, name: Optional[str], roll: Optional[str], course: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fallback implementation for TinyDB and memory storage."""
        def norm(x: Optional[str]) -> str:
            return self._normalize_string(x)

        n_name, n_roll, n_course = norm(name), norm(roll), norm(course)
        
        records = self.certificates if self.db_type == "memory" else list(self.certificates)
        
        for r in records:
            if n_roll and norm(r.get('roll_number')) == n_roll:
                if not n_name or norm(r.get('name')) == n_name:
                    if not n_course or norm(r.get('course')) == n_course:
                        return r
        return None

    def log_verification(self, entry: Dict[str, Any]) -> str:
        """Log verification entry."""
        entry['timestamp'] = datetime.utcnow()
        
        if self.db_type == "mongodb":
            result = self.verifications.insert_one(entry)
            return str(result.inserted_id)
        elif self.db_type == "tinydb":
            doc_id = self.verifications.insert(entry)
            return str(doc_id)
        else:
            self._memory_log_counter += 1
            entry['doc_id'] = self._memory_log_counter
            self.verifications.append(entry)
            return str(self._memory_log_counter)

    def import_records(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Import multiple records."""
        inserted = 0
        updated = 0
        for r in records:
            ins, _ = self.upsert_record(r)
            if ins:
                inserted += 1
            else:
                updated += 1
        return {"inserted": inserted, "updated": updated, "total": len(records)}

    def list_records(self, limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """List records with pagination."""
        if self.db_type == "mongodb":
            total = self.certificates.count_documents({})
            cursor = self.certificates.find({}).sort([("created_at", -1)]).skip(offset).limit(limit)
            items = list(cursor)
            
            for item in items:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
            
            return items, total
        
        elif self.db_type == "tinydb":
            all_items = list(self.certificates)
            total = len(all_items)
            start = max(0, offset)
            end = max(start, start + max(0, limit))
            return all_items[start:end], total
        
        else:
            total = len(self.certificates)
            start = max(0, offset)
            end = max(start, start + max(0, limit))
            return self.certificates[start:end], total

    def stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self.db_type == "mongodb":
            return self._mongodb_stats()
        else:
            return self._fallback_stats()

    def _mongodb_stats(self) -> Dict[str, Any]:
        """MongoDB implementation of stats."""
        total_certs = self.certificates.count_documents({})
        total_logs = self.verifications.count_documents({})
        
        unique_issuers_pipeline = [
            {"$match": {"issuer": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$issuer"}},
            {"$count": "total"}
        ]
        
        unique_issuers_result = list(self.certificates.aggregate(unique_issuers_pipeline))
        unique_issuers = unique_issuers_result[0]['total'] if unique_issuers_result else 0
        
        recent_certificates = self.certificates.count_documents({
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        return {
            'certificates': total_certs,
            'logs': total_logs,
            'issuers': unique_issuers,
            'recent_certificates': recent_certificates,
            'database_type': 'MongoDB'
        }

    def _fallback_stats(self) -> Dict[str, Any]:
        """Fallback implementation of stats."""
        records = self.certificates if self.db_type == "memory" else list(self.certificates)
        logs = self.verifications if self.db_type == "memory" else list(self.verifications)
        
        total_certs = len(records)
        total_logs = len(logs)
        
        issuers = set()
        for r in records:
            if r.get('issuer'):
                issuers.add(r['issuer'])
        
        return {
            'certificates': total_certs,
            'logs': total_logs,
            'issuers': len(issuers),
            'database_type': self.db_type.title()
        }

    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        if self.db_type == "mongodb":
            try:
                self.client.admin.command('ping')
                return True
            except Exception:
                return False
        else:
            return True  # TinyDB and memory storage are always "healthy"

    def close_connection(self) -> None:
        """Close database connection."""
        if self.db_type == "mongodb" and self.client:
            self.client.close()

    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database setup."""
        return {
            'type': self.db_type,
            'mongodb_available': MONGODB_AVAILABLE,
            'tinydb_available': TINYDB_AVAILABLE,
            'connection_healthy': self.health_check()
        }