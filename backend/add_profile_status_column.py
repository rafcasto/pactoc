#!/usr/bin/env python3
"""
Migration script to add missing profile_status column to patients table.
"""

import sqlite3
import os

def run_migration():
    """Add the missing profile_status column to patients table."""
    
    db_path = os.path.join(os.path.dirname(__file__), 'pactoc_dev.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Adding profile_status column to patients table...")
        
        # Add the profile_status column with default value
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN profile_status TEXT DEFAULT 'pending_review'
        """)
        
        # Update all existing patients to have pending_review status
        cursor.execute("""
            UPDATE patients 
            SET profile_status = 'pending_review' 
            WHERE profile_status IS NULL
        """)
        
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(patients)")
        columns = cursor.fetchall()
        
        print("✅ Migration completed successfully!")
        print("Current patients table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check how many patients we have
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total patients in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT profile_status, COUNT(*) FROM patients GROUP BY profile_status")
            status_counts = cursor.fetchall()
            print("Status distribution:")
            for status, count in status_counts:
                print(f"  - {status}: {count} patients")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Database migration completed! You can now restart the server.")
    else:
        print("\n💥 Migration failed. Please check the error above.")
