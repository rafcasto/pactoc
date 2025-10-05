# 🥗 Sistema de Recetas Dietéticas (Cleaned Up)

## 📋 Project Overview

This is a clean, dietary recipe system that allows nutritionists to create invitations for patients to complete their medical profile publicly (without login) and automatically receive a personalized meal plan.

## 🏗️ Clean Architecture

### Backend (Flask + SQLAlchemy + SQLite)
- **Database**: SQLite (configurable to PostgreSQL)
- **ORM**: SQLAlchemy with migrations
- **Authentication**: Firebase Auth (admin panel only)
- **Public API**: No authentication required for patients

### Frontend (Next.js 15 + React 19 + TypeScript)
- **Framework**: Next.js with App Router
- **UI**: Tailwind CSS + Lucide Icons
- **Forms**: React Hook Form + Zod
- **State**: React state management

## 📁 Clean Project Structure

```
pactoc/
├── README_SISTEMA_RECETAS.md    # Main documentation
├── CLEANUP_PLAN.md              # Cleanup documentation
├── start_dev.sh                 # Main startup script
├── backend/                     # Python Flask Backend
│   ├── app/                     # Main Flask application
│   │   ├── __init__.py         # Application factory
│   │   ├── config.py           # Configuration
│   │   ├── extensions.py       # Flask extensions
│   │   ├── models/             # Database models
│   │   ├── routes/             # API endpoints
│   │   ├── services/           # Business logic
│   │   ├── middleware/         # Auth middleware
│   │   └── utils/              # Utilities
│   ├── instance/               # Flask instance folder
│   │   └── pactoc_dev.db      # SQLite database
│   ├── venv/                   # Python virtual environment
│   ├── init_system.py          # System initialization
│   ├── run_diet_server.py      # Flask development server
│   ├── seed_data.py            # Database seeding
│   ├── create_test_invitation.py # Test invitation creator
│   ├── requirements.txt        # Python dependencies
│   ├── serviceAccountKey.json  # Firebase credentials
│   └── pactoc_dev.db          # Main database file
└── frontend/                   # Next.js Frontend
    ├── app/                    # Next.js App Router
    │   ├── complete-profile/   # Patient profile form
    │   ├── my-meal-plan/      # Meal plan viewer
    │   ├── dashboard/         # Admin dashboard
    │   └── ...
    ├── components/            # React components
    ├── lib/                   # Utilities and hooks
    ├── types/                 # TypeScript types
    ├── package.json           # Node dependencies
    └── ...
```

## 🚀 Quick Start (Cleaned System)

### 1. Initialize the System
```bash
cd /Users/rafaelcastillo/pactoc/backend
python3.11 init_system.py
```

### 2. Create Test Invitation
```bash
python3.11 create_test_invitation.py
```

### 3. Start Development Servers
```bash
cd /Users/rafaelcastillo/pactoc
./start_dev.sh
```

### 4. Access the System
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Test Form**: http://localhost:3000/complete-profile/QizKtpixpDYa6_UwgWgW54Rh0GcTUO2x8oblSAloT-E

## 🧹 What Was Removed

### Redundant Server Files (Removed)
- `final_backend_server.py` - Simple HTTP server
- `fixed_backend_server.py` - Old server version
- `database_server.py` - Alternative server
- `diet_system_server.py` - Alternative server
- `flask_server.py` - Basic Flask server
- `http_server.py` - HTTP server
- `minimal_server.py` - Minimal server
- `simple_api_server.py` - Simple API server
- `simple_server.py` - Simple server
- `run.py` - Generic run script
- `run_simple.py` - Simple run script

### Test Files (Removed)
- `quick_test.py` - Quick test script
- `test_basic_db.py` - Basic DB test
- `test_firebase.py` - Firebase test
- `test_postgres_connection.py` - Postgres test
- `test_server.py` - Server test

### Alternative Implementations (Removed)
- `simple_init.py` - Alternative init
- `seed_catalogs.py` - Alternative seeding
- `seed_catalogs_simple.py` - Simple catalog seeding
- `seed_diet_system.py` - Alternative system seeding
- `seed_postgres.py` - Postgres seeding
- `show_conversion_summary.py` - Utility script

### Documentation (Removed)
- `README_MEAL_PLAN_EXTENSION.md` - Extension docs
- `README_POSTGRESQL.md` - PostgreSQL docs
- `SYSTEM_STATUS.md` - Status docs
- `test_system.sh` - Test script
- `quick_start.sh` - Alternative start script

### Unused Directories (Removed)
- `meal-plan-backend/` - Empty TypeScript backend attempt

## 🎯 Current Core Files

### Essential Backend Files
- `backend/app/` - **Main Flask application** (All files kept)
- `backend/init_system.py` - **System initialization**
- `backend/run_diet_server.py` - **Main Flask server**
- `backend/seed_data.py` - **Database seeding**
- `backend/create_test_invitation.py` - **Test invitation creator**
- `backend/requirements.txt` - **Python dependencies**
- `backend/pactoc_dev.db` - **SQLite database**
- `backend/serviceAccountKey.json` - **Firebase credentials**

### Essential Frontend Files
- `frontend/` - **Complete Next.js 15 application** (All files kept)

### Project Files
- `start_dev.sh` - **Main development startup script**
- `README_SISTEMA_RECETAS.md` - **Complete system documentation**

## 🔧 Key Features (Unchanged)

✅ **Public Patient Form**: Complete profile via unique link  
✅ **Automatic Meal Plan Generation**: AI-powered recipe filtering  
✅ **Public Meal Plan View**: Detailed recipes with nutritional info  
✅ **Complete Database**: 13 related tables with sample data  
✅ **Firebase Authentication**: Admin panel authentication  
✅ **Responsive Design**: Mobile-first UI with Tailwind CSS  

## 🚀 Deployment Ready

The cleaned project is now ready for:
- Development work
- Production deployment
- Easy maintenance
- Code collaboration

## 📊 System Benefits After Cleanup

- **-15 Python files**: Removed redundant servers and tests
- **-4 Documentation files**: Kept only essential docs
- **-1 Directory**: Removed unused meal-plan-backend
- **Cleaner structure**: Easy to understand and maintain
- **Single entry point**: `start_dev.sh` for development
- **Clear dependencies**: Only essential files remain

---

**System Status**: ✅ **Clean and Ready**  
**Last Cleanup**: October 4, 2025  
**Core Technology**: Flask + Next.js + SQLite  
**Authentication**: Firebase (Admin only)
