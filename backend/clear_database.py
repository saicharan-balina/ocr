#!/usr/bin/env python3
"""
Script to clear all data from the certificate verification database.
This is a direct database operation that bypasses the Flask API.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.store import CertificateStore

def main():
    """Clear all data from the database."""
    print("Certificate Database Cleaner")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database connection
    try:
        store = CertificateStore()
        print(f"Connected to database: {store.database_name}")
        
        # Check current database stats
        stats = store.stats()
        print(f"\nCurrent database contents:")
        print(f"  - Certificates: {stats['certificates']}")
        print(f"  - Verification logs: {stats['logs']}")
        print(f"  - Unique issuers: {stats['issuers']}")
        
        if stats['certificates'] == 0 and stats['logs'] == 0:
            print("\nDatabase is already empty.")
            return
        
        # Confirm deletion
        confirmation = input(f"\nAre you sure you want to clear ALL data? This cannot be undone! (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        # Clear the database
        print("\nClearing database...")
        result = store.clear_all_data()
        
        if result['success']:
            print(f"✅ Database cleared successfully!")
            print(f"  - Deleted {result['certificates_deleted']} certificates")
            print(f"  - Deleted {result['verifications_deleted']} verification logs")
        else:
            print(f"❌ Failed to clear database: {result['error']}")
            sys.exit(1)
        
        # Verify the database is empty
        final_stats = store.stats()
        print(f"\nFinal database state:")
        print(f"  - Certificates: {final_stats['certificates']}")
        print(f"  - Verification logs: {final_stats['logs']}")
        
        if final_stats['certificates'] == 0 and final_stats['logs'] == 0:
            print("✅ Database successfully emptied!")
        else:
            print("⚠️  Warning: Some data may still remain in the database.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        if 'store' in locals():
            store.close_connection()

if __name__ == '__main__':
    main()