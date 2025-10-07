#!/usr/bin/env python3
"""
Fix patient_invitations table schema to match SQLAlchemy model.
"""
import sqlite3
import os
import sys

def fix_patient_invitations_schema():
    """Update patient_invitations table to match the SQLAlchemy model."""
    
    # Database file path
    db_path = '../pactoc_dev.db'
    if not os.path.exists(db_path):
        db_path = '../instance/pactoc_dev.db'
        if not os.path.exists(db_path):
            print("❌ Database file not found")
            return False
    
    print(f"🔧 Updating schema for database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(patient_invitations)")
        current_columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"📋 Current columns: {list(current_columns.keys())}")
        
        # Add missing columns
        migrations = []
        
        if 'email' not in current_columns:
            migrations.append("ALTER TABLE patient_invitations ADD COLUMN email TEXT")
            print("  ➕ Adding email column")
        
        if 'invited_by_uid' not in current_columns:
            migrations.append("ALTER TABLE patient_invitations ADD COLUMN invited_by_uid TEXT")
            print("  ➕ Adding invited_by_uid column")
        
        if 'status' not in current_columns:
            migrations.append("ALTER TABLE patient_invitations ADD COLUMN status TEXT DEFAULT 'pending'")
            print("  ➕ Adding status column")
        
        if 'completed_at' not in current_columns:
            migrations.append("ALTER TABLE patient_invitations ADD COLUMN completed_at TIMESTAMP")
            print("  ➕ Adding completed_at column")
        
        if 'updated_at' not in current_columns:
            migrations.append("ALTER TABLE patient_invitations ADD COLUMN updated_at TIMESTAMP")
            print("  ➕ Adding updated_at column")
        
        # Execute migrations
        for migration in migrations:
            cursor.execute(migration)
            print(f"  ✅ Executed: {migration}")
        
        # If is_used column exists, migrate its data to status
        if 'is_used' in current_columns:
            print("  🔄 Migrating is_used column to status...")
            cursor.execute("""
                UPDATE patient_invitations 
                SET status = CASE 
                    WHEN is_used = 1 THEN 'completed' 
                    ELSE 'pending' 
                END
                WHERE status IS NULL OR status = 'pending'
            """)
            print("  ✅ Migrated is_used data to status column")
        
        # Set default values for invited_by_uid where missing
        cursor.execute("""
            UPDATE patient_invitations 
            SET invited_by_uid = 'legacy-import'
            WHERE invited_by_uid IS NULL
        """)
        print("  ✅ Set default invited_by_uid for existing records")
        
        # Set email from existing data if available
        cursor.execute("""
            UPDATE patient_invitations 
            SET email = first_name || '.' || last_name || '@example.com'
            WHERE email IS NULL
        """)
        print("  ✅ Set placeholder emails for existing records")
        
        # Set updated_at to created_at for existing records
        cursor.execute("""
            UPDATE patient_invitations 
            SET updated_at = created_at
            WHERE updated_at IS NULL
        """)
        print("  ✅ Set updated_at for existing records")
        
        # Commit changes
        conn.commit()
        
        # Show final schema
        cursor.execute("PRAGMA table_info(patient_invitations)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Final columns: {final_columns}")
        
        conn.close()
        print("✅ Schema migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_patient_invitations_schema()
    sys.exit(0 if success else 1)
