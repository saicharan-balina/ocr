import os
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CertificateStore:
    """Schemaless store for certificate records and verification logs.

    Backed by MongoDB for professional, scalable data storage.
    Maintains the same interface as the previous TinyDB implementation.
    """

    def __init__(self, connection_string: Optional[str] = None, database_name: Optional[str] = None) -> None:
        # Get configuration from environment variables or use defaults
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name or os.getenv('MONGODB_DATABASE', 'certificate_verification_db')
        
        # Initialize MongoDB connection
        self.client = MongoClient(self.connection_string)
        self.db: Database = self.client[self.database_name]
        
        # Collections (equivalent to tables in TinyDB)
        self.certificates: Collection = self.db.certificates
        self.verifications: Collection = self.db.verifications
        
        # Create indexes for better performance
        self._create_indexes()

    @staticmethod
    def _stringify_id(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Return a copy of doc with MongoDB ObjectId converted to string."""
        if not doc:
            return doc
        d = dict(doc)
        _id = d.get('_id')
        try:
            # Avoid importing bson here; rely on str() being acceptable
            if _id is not None:
                d['_id'] = str(_id)
        except Exception:
            pass
        return d

    def _create_indexes(self) -> None:
        """Create database indexes for better performance."""
        # Index on certificate_id_lower for fast lookups
        self.certificates.create_index([("certificate_id_lower", ASCENDING)], unique=False)
        
        # Index on file_hash for duplicate detection
        self.certificates.create_index([("file_hash", ASCENDING)], unique=False)
        
        # Index on verification logs timestamp
        self.verifications.create_index([("timestamp", ASCENDING)])
        
        # Compound index for candidate search
        self.certificates.create_index([
            ("name_normalized", ASCENDING),
            ("roll_number_normalized", ASCENDING),
            ("course_normalized", ASCENDING)
        ])

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def upsert_record(self, record: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Insert or update a certificate record.

        Enforces uniqueness on certificate_id (case-insensitive) if provided.
        Returns (inserted, stored_record)
        """
        cert_id = (record.get('certificate_id') or '').strip().lower()
        
        # Add timestamp for audit trail
        record['updated_at'] = datetime.utcnow()
        
        if cert_id:
            record['certificate_id_lower'] = cert_id
            
            # Check if record already exists
            existing = self.certificates.find_one({"certificate_id_lower": cert_id})
            if existing:
                # Update existing record (merge fields)
                merged = {**existing, **record}
                merged['certificate_id_lower'] = cert_id
                # Update normalized fields only if corresponding raw fields are provided
                if 'name' in record:
                    merged['name_normalized'] = self._normalize_string(record.get('name', ''))
                if 'roll_number' in record:
                    merged['roll_number_normalized'] = self._normalize_string(record.get('roll_number', ''))
                if 'course' in record:
                    merged['course_normalized'] = self._normalize_string(record.get('course', ''))
                # Do not attempt to set immutable _id
                merged.pop('_id', None)
                
                # Update the document
                self.certificates.update_one(
                    {"_id": existing["_id"]},
                    {"$set": merged}
                )
                
                # Return the updated document
                updated = self.certificates.find_one({"_id": existing["_id"]})
                return False, self._stringify_id(updated)

        # New record
        if cert_id:
            record['certificate_id_lower'] = cert_id
            
        # Add normalized fields for better search
        record['name_normalized'] = self._normalize_string(record.get('name', ''))
        record['roll_number_normalized'] = self._normalize_string(record.get('roll_number', ''))
        record['course_normalized'] = self._normalize_string(record.get('course', ''))
        
        record['created_at'] = datetime.utcnow()
        
        # Insert new record
        result = self.certificates.insert_one(record)
        stored = self.certificates.find_one({"_id": result.inserted_id})
        return True, self._stringify_id(stored)

    def _normalize_string(self, text: Optional[str]) -> str:
        """Normalize string for better search matching."""
        if not text:
            return ""
        return ''.join(text.lower().split())

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
        return self._stringify_id(self.certificates.find_one({"certificate_id_lower": cert_id}))

    def find_candidate(self, name: Optional[str], roll: Optional[str], course: Optional[str]) -> Optional[Dict[str, Any]]:
        """Enhanced candidate finder using MongoDB queries and normalized fields."""
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
        
        # If we have at least one search criteria, search with it
        if query:
            result = self.certificates.find_one(query)
            if result:
                return self._stringify_id(result)
        
        # Fallback to flexible search if exact match fails
        if roll:
            n_roll = self._normalize_string(roll)
            candidates = list(self.certificates.find({"roll_number_normalized": n_roll}))
            if candidates:
                # If we have name or course criteria, filter further
                for candidate in candidates:
                    if name and self._normalize_string(candidate.get('name', '')) != self._normalize_string(name):
                        continue
                    if course and self._normalize_string(candidate.get('course', '')) != self._normalize_string(course):
                        continue
                    return self._stringify_id(candidate)
        
        return None

    def log_verification(self, entry: Dict[str, Any]) -> str:
        """Log verification entry and return the inserted document ID."""
        entry['timestamp'] = datetime.utcnow()
        result = self.verifications.insert_one(entry)
        return str(result.inserted_id)

    # --- Helpers for admin views ---
    def list_records(self, limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Return a slice of certificate records and total count with efficient pagination."""
        # Get total count
        total = self.certificates.count_documents({})
        
        # Get paginated results with proper sorting
        cursor = self.certificates.find({}).sort([("created_at", -1)]).skip(offset).limit(limit)
        items = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for item in items:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        
        return items, total

    def stats(self) -> Dict[str, Any]:
        """Enhanced statistics using MongoDB aggregation for better performance."""
        # Get certificate count
        total_certs = self.certificates.count_documents({})
        
        # Get verification logs count
        total_logs = self.verifications.count_documents({})
        
        # Get unique issuers count using aggregation
        unique_issuers_pipeline = [
            {"$match": {"issuer": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$issuer"}},
            {"$count": "total"}
        ]
        
        unique_issuers_result = list(self.certificates.aggregate(unique_issuers_pipeline))
        unique_issuers = unique_issuers_result[0]['total'] if unique_issuers_result else 0
        
        # Additional stats
        recent_certificates = self.certificates.count_documents({
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        return {
            'certificates': total_certs,
            'logs': total_logs,
            'issuers': unique_issuers,
            'recent_certificates': recent_certificates,
        }

    def close_connection(self) -> None:
        """Close MongoDB connection when done."""
        if self.client:
            self.client.close()

    def health_check(self) -> bool:
        """Check if MongoDB connection is healthy."""
        try:
            # Ping the server
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all data from the database (admin operation)."""
        result = {
            'certificates_deleted': 0,
            'verifications_deleted': 0,
            'success': True,
            'error': None
        }
        
        try:
            # Count documents before deletion
            cert_count = self.certificates.count_documents({})
            verify_count = self.verifications.count_documents({})
            
            # Delete all documents from both collections
            cert_result = self.certificates.delete_many({})
            verify_result = self.verifications.delete_many({})
            
            result['certificates_deleted'] = cert_result.deleted_count
            result['verifications_deleted'] = verify_result.deleted_count
            
            # Verify deletion
            remaining_certs = self.certificates.count_documents({})
            remaining_verifs = self.verifications.count_documents({})
            
            if remaining_certs > 0 or remaining_verifs > 0:
                result['success'] = False
                result['error'] = f"Incomplete deletion: {remaining_certs} certificates and {remaining_verifs} verifications remain"
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
