#!/usr/bin/env python3
"""
Script de inicialización para el sistema de recetas dietéticas.
"""
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DATABASE_URL', 'sqlite:///pactoc_dev.db')

from app import create_app
from app.services.database_service import db, create_tables

def main():
    """Initialize the database and seed with sample data."""
    print("🚀 Inicializando sistema de recetas dietéticas...")
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        # Create tables
        print("📋 Creando tablas de base de datos...")
        if create_tables():
            print("✅ Tablas creadas exitosamente")
        else:
            print("❌ Error creando tablas")
            return False
        
        # Import seed functions
        from seed_data import seed_all_data
        
        # Seed data
        print("🌱 Sembrando datos de ejemplo...")
        if seed_all_data():
            print("🎉 Sistema inicializado exitosamente!")
            print("\nEl sistema está listo para usar.")
            print("Puedes crear invitaciones desde el panel de administración.")
            return True
        else:
            print("❌ Error sembrando datos")
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
