#!/usr/bin/env python3
"""
Migration script to transfer data from TinyDB JSON files to MongoDB.
Run this script to migrate existing certificate data to the new MongoDB setup.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.store import CertificateStore


def load_tinydb_data(json_file_path: str) -> Dict[str, Any]:
    """Load data from TinyDB JSON file."""
    if not os.path.exists(json_file_path):
        print(f"JSON file not found: {json_file_path}")
        return {"certificates": {}, "verifications": {}}
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return {"certificates": {}, "verifications": {}}


def migrate_certificates(mongo_store: CertificateStore, certificates_data: Dict[str, Any]) -> int:
    """Migrate certificate records to MongoDB."""
    count = 0
    
    for doc_id, cert_record in certificates_data.items():
        try:
            # Add migration metadata
            cert_record['migrated_from_tinydb'] = True
            cert_record['migration_date'] = datetime.utcnow()
            cert_record['original_doc_id'] = doc_id
            
            # Insert record using the upsert method
            inserted, stored = mongo_store.upsert_record(cert_record)
            
            if inserted:
                count += 1
                print(f"✓ Migrated certificate: {cert_record.get('certificate_id', 'Unknown ID')}")
            else:
                print(f"→ Updated existing certificate: {cert_record.get('certificate_id', 'Unknown ID')}")
                
        except Exception as e:
            print(f"✗ Error migrating certificate {doc_id}: {e}")
    
    return count


def migrate_verifications(mongo_store: CertificateStore, verifications_data: Dict[str, Any]) -> int:
    """Migrate verification logs to MongoDB."""
    count = 0
    
    for doc_id, log_entry in verifications_data.items():
        try:
            # Add migration metadata
            log_entry['migrated_from_tinydb'] = True
            log_entry['migration_date'] = datetime.utcnow()
            log_entry['original_doc_id'] = doc_id
            
            # Insert verification log
            inserted_id = mongo_store.log_verification(log_entry)
            
            count += 1
            print(f"✓ Migrated verification log: {doc_id} -> {inserted_id}")
                
        except Exception as e:
            print(f"✗ Error migrating verification log {doc_id}: {e}")
    
    return count


def main():
    """Main migration function."""
    print("🔄 Starting migration from TinyDB to MongoDB...")
    print("=" * 50)
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'data', 'certificates.json')
    
    # Load existing data
    print(f"📂 Loading data from: {json_file_path}")
    data = load_tinydb_data(json_file_path)
    
    certificates_data = data.get('certificates', {})
    verifications_data = data.get('verifications', {})
    
    print(f"📊 Found {len(certificates_data)} certificates and {len(verifications_data)} verification logs")
    
    if not certificates_data and not verifications_data:
        print("ℹ️  No data to migrate. Exiting.")
        return
    
    # Initialize MongoDB store
    try:
        print("🔌 Connecting to MongoDB...")
        mongo_store = CertificateStore()
        
        # Test connection
        if not mongo_store.health_check():
            print("❌ Failed to connect to MongoDB. Please check your connection settings.")
            return
        
        print("✅ MongoDB connection successful!")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("💡 Make sure MongoDB is running and check your connection settings in .env file")
        return
    
    try:
        # Migrate certificates
        if certificates_data:
            print(f"\n📋 Migrating {len(certificates_data)} certificates...")
            cert_count = migrate_certificates(mongo_store, certificates_data)
            print(f"✅ Successfully migrated {cert_count} certificates")
        
        # Migrate verification logs
        if verifications_data:
            print(f"\n📝 Migrating {len(verifications_data)} verification logs...")
            log_count = migrate_verifications(mongo_store, verifications_data)
            print(f"✅ Successfully migrated {log_count} verification logs")
        
        # Show final stats
        print(f"\n📈 Final Statistics:")
        stats = mongo_store.stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 Migration completed successfully!")
        print("💡 You can now safely backup the old certificates.json file")
        
        # Create backup suggestion
        backup_path = json_file_path + '.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"💡 Suggested backup command: cp '{json_file_path}' '{backup_path}'")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    
    finally:
        # Close MongoDB connection
        mongo_store.close_connection()
        print("🔌 MongoDB connection closed.")


if __name__ == '__main__':
    main()