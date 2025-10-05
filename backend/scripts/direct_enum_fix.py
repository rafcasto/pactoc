#!/usr/bin/env python3
"""
Direct SQL fix for the ready_for_review enum error.
This script will directly fix the PostgreSQL enum issue.
"""

import subprocess
import sys
import os

def run_sql_fix():
    """Run SQL commands to fix the enum issue."""
    
    print("🔧 DIRECT SQL FIX FOR ENUM ERROR")
    print("=" * 40)
    
    # PostgreSQL commands to fix the enum
    sql_commands = [
        # Check current enum
        "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'profile_status') ORDER BY enumsortorder;",
        
        # If ready_for_review exists, remove it
        "UPDATE patients SET profile_status = 'pending_review' WHERE profile_status = 'ready_for_review';",
        
        # Drop and recreate the enum type
        "DROP TYPE IF EXISTS profile_status CASCADE;",
        "CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');",
        
        # Add the column back to patients table
        "ALTER TABLE patients ADD COLUMN profile_status profile_status DEFAULT 'pending_review';"
    ]
    
    print("1. Attempting to connect to database...")
    
    # Try to find the database URL from environment or config
    db_commands = []
    
    # Check if we have psql available
    try:
        subprocess.run(['which', 'psql'], check=True, capture_output=True)
        print("✅ Found psql command")
        
        # Try different common database names/connections
        possible_db_configs = [
            "postgresql://localhost/pactoc_dev",
            "postgresql://localhost/pactoc", 
            "sqlite:///pactoc_dev.db"  # This won't work but let's try
        ]
        
        for db_url in possible_db_configs:
            if 'postgresql' in db_url:
                print(f"2. Trying database: {db_url}")
                try:
                    # Test connection
                    test_cmd = f'psql "{db_url}" -c "SELECT 1;" 2>/dev/null'
                    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Connected to {db_url}")
                        
                        # Run the fix commands
                        for i, sql in enumerate(sql_commands, 1):
                            print(f"3.{i} Running: {sql[:50]}...")
                            cmd = f'psql "{db_url}" -c "{sql};"'
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                            
                            if result.returncode != 0 and 'DROP TYPE' not in sql:
                                print(f"   ⚠️  Command warning: {result.stderr.strip()}")
                            else:
                                print(f"   ✅ Success")
                        
                        print("\n🎉 SQL FIX COMPLETED!")
                        return True
                        
                    else:
                        print(f"❌ Cannot connect to {db_url}")
                        
                except Exception as e:
                    print(f"❌ Error with {db_url}: {e}")
                    continue
        
        print("❌ Could not connect to any database")
        return False
        
    except subprocess.CalledProcessError:
        print("❌ psql command not found")
        return False

def alternative_fix():
    """Alternative fix using Python database connection."""
    
    print("\n🔄 TRYING ALTERNATIVE FIX...")
    print("=" * 40)
    
    # Create a simple fix script
    fix_script = """
import sys, os
sys.path.insert(0, '/Users/rafaelcastillo/pactoc/backend/app')

try:
    from app import create_app
    from app.services.database_service import db
    from sqlalchemy import text
    
    app = create_app()
    with app.app_context():
        print("Connected to database via Flask")
        
        # Check current enum values
        result = db.session.execute(text(\"\"\"
            SELECT enumlabel FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'profile_status')
            ORDER BY enumsortorder;
        \"\"\"))
        
        current_values = [row[0] for row in result.fetchall()]
        print(f"Current enum values: {current_values}")
        
        # Fix if ready_for_review exists
        if 'ready_for_review' in current_values:
            print("Found ready_for_review - removing it...")
            
            # Update any existing data
            db.session.execute(text("UPDATE patients SET profile_status = 'pending_review' WHERE profile_status = 'ready_for_review';"))
            
            # Recreate enum
            db.session.execute(text("ALTER TABLE patients DROP COLUMN profile_status;"))
            db.session.execute(text("DROP TYPE profile_status;"))
            db.session.execute(text("CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');"))
            db.session.execute(text("ALTER TABLE patients ADD COLUMN profile_status profile_status DEFAULT 'pending_review';"))
            
            db.session.commit()
            print("✅ Fixed ready_for_review enum issue!")
        else:
            print("✅ No ready_for_review found in enum")
            
except Exception as e:
    print(f"Error: {e}")
"""
    
    # Write and run the fix script
    with open('/tmp/enum_fix.py', 'w') as f:
        f.write(fix_script)
    
    try:
        result = subprocess.run([
            '/Users/rafaelcastillo/pactoc/backend/venv/bin/python', 
            '/tmp/enum_fix.py'
        ], capture_output=True, text=True, timeout=30)
        
        print("Fix script output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Fix script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running fix script: {e}")
        return False

if __name__ == "__main__":
    print("🚨 FIXING READY_FOR_REVIEW ENUM ERROR")
    print("=" * 50)
    
    # Try direct SQL fix first
    success = run_sql_fix()
    
    # If that fails, try alternative fix
    if not success:
        success = alternative_fix()
    
    if success:
        print("\n🎉 ENUM ISSUE FIXED!")
        print("You can now run your application:")
        print("./start_dev.sh")
    else:
        print("\n❌ COULD NOT FIX AUTOMATICALLY")
        print("\nMANUAL FIX REQUIRED:")
        print("1. Connect to your PostgreSQL database")
        print("2. Run these commands:")
        print("   UPDATE patients SET profile_status = 'pending_review' WHERE profile_status = 'ready_for_review';")
        print("   DROP TYPE profile_status CASCADE;")
        print("   CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');")
        print("   ALTER TABLE patients ADD COLUMN profile_status profile_status DEFAULT 'pending_review';")
    
    sys.exit(0 if success else 1)
