# Database Migration and Utility Scripts

This directory contains utility scripts for database management, migrations, and testing.

## Scripts Description

- `add_profile_status_column.py` - Adds profile status column to database tables
- `check_enum_db.py` - Validates enum values in the database
- `create_test_invitation.py` - Creates test invitation data
- `direct_enum_fix.py` - Direct fix for enum issues
- `emergency_enum_fix.py` - Emergency fix for critical enum problems
- `migrate_workflow_enums.py` - Migrates workflow enum values
- `migrate_workflow.py` - General workflow migration script
- `quick_enum_fix.py` - Quick fix for enum inconsistencies
- `test_enum_workflow.py` - Tests enum workflow functionality
- `validate_enums.py` - Validates enum integrity across the application

## Usage

Most scripts should be run from the backend directory with the virtual environment activated:

```bash
cd backend
source venv/bin/activate  # or activate your virtual environment
python scripts/script_name.py
```

## Note

These scripts are for development and maintenance purposes. Be careful when running them in production environments.
