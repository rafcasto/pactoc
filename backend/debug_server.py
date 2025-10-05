#!/usr/bin/env python3
"""
Debug version of the server to identify deployment issues.
"""
import os
import sys
import traceback
from flask import Flask, jsonify

def create_debug_app():
    """Create a minimal Flask app for debugging."""
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Debug server is running',
            'python_version': sys.version,
            'environment': 'production' if os.environ.get('VERCEL') else 'development'
        })
    
    @app.route('/debug/env')
    def debug_env():
        """Debug endpoint to check environment variables."""
        env_vars = {}
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY', 
            'FIREBASE_SERVICE_ACCOUNT_BASE64',
            'VERCEL',
            'FLASK_ENV'
        ]
        
        for var in required_vars:
            value = os.environ.get(var)
            env_vars[var] = 'SET' if value else 'NOT_SET'
            
        return jsonify({
            'environment_variables': env_vars,
            'total_env_vars': len(os.environ),
            'python_path': sys.path[:3]  # First 3 entries
        })
    
    @app.route('/debug/import-test')
    def test_imports():
        """Test if we can import required modules."""
        results = {}
        
        modules_to_test = [
            'flask',
            'flask_cors',
            'firebase_admin',
            'psycopg2',
            'flask_sqlalchemy',
            'dotenv'
        ]
        
        for module in modules_to_test:
            try:
                __import__(module)
                results[module] = 'OK'
            except ImportError as e:
                results[module] = f'FAILED: {str(e)}'
            except Exception as e:
                results[module] = f'ERROR: {str(e)}'
        
        return jsonify({
            'import_results': results
        })
    
    @app.route('/debug/full-error')
    def test_full_app():
        """Try to import the full app and see what fails."""
        try:
            # Add the backend directory to the Python path
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, backend_dir)
            
            from app import create_app
            test_app = create_app('production' if os.environ.get('VERCEL') else 'development')
            
            return jsonify({
                'status': 'success',
                'message': 'Full app import successful'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    return app

# For Vercel deployment
app = create_debug_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
