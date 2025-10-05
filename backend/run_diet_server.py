#!/usr/bin/env python3
"""
Servidor simple para probar el sistema de recetas dietéticas.
"""
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'development')
# DATABASE_URL must be set in .env file - no fallback to ensure PostgreSQL is always used

from app import create_app

def main():
    """Run the Flask development server."""
    app = create_app('development')
    
    print("🚀 Iniciando servidor de desarrollo...")
    print("📡 Sistema de recetas dietéticas disponible en:")
    print("   Backend API: http://localhost:8000")
    print("   Endpoints públicos: http://localhost:8000/api/public/")
    print("\n📋 Para probar el sistema:")
    print("   1. Crear una invitación desde el panel admin")
    print("   2. Usar el token en: /complete-profile/{token}")
    print("   3. Ver el plan en: /my-meal-plan/{meal_plan_token}")
    print("\n🛑 Presiona Ctrl+C para detener el servidor")
    
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")

# For Vercel deployment
app = create_app('production' if os.environ.get('VERCEL') else 'development')

# Vercel needs this at module level
if os.environ.get('VERCEL'):
    # Production handler for Vercel
    pass
else:
    # Development mode
    if __name__ == '__main__':
        main()
