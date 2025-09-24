#!/usr/bin/env python3
"""
Verification script to check MongoDB data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.store import CertificateStore

def main():
    print("🔍 Verifying MongoDB Data")
    print("=" * 30)
    
    try:
        store = CertificateStore()
        
        # Check connection
        if store.health_check():
            print("✅ MongoDB connection: OK")
        else:
            print("❌ MongoDB connection: FAILED")
            return
        
        # Get statistics
        stats = store.stats()
        print(f"\n📊 Database Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Get sample records
        print(f"\n📋 Sample Certificates:")
        items, total = store.list_records(limit=3)
        
        if items:
            for i, item in enumerate(items):
                cert_id = item.get('certificate_id', 'N/A')
                name = item.get('name', 'N/A')
                course = item.get('course', 'N/A')
                print(f"   {i+1}. ID: {cert_id}")
                print(f"      Name: {name}")
                print(f"      Course: {course}")
                print()
        else:
            print("   No certificates found")
        
        # Check indexes
        try:
            indexes = list(store.certificates.list_indexes())
            print(f"\n🗂️  Database Indexes: {len(indexes)} indexes created")
            for idx in indexes:
                print(f"   - {idx.get('name', 'Unknown')}")
        except Exception as e:
            print(f"   Could not list indexes: {e}")
        
        store.close_connection()
        print("\n🎉 Verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == '__main__':
    main()