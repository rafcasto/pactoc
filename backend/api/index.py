#!/usr/bin/env python3
"""
Vercel-compatible Flask application entry point.
"""
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('VERCEL', '1')

def create_application():
    """Create and configure the Flask application for Vercel."""
    
    # First, try to create the main application
    try:
        from app import create_app
        flask_app = create_app('production')
        
        # Add Vercel-specific middleware and routes
        @flask_app.before_request
        def handle_vercel_routing():
            from flask import request
            flask_app.logger.info(f"Vercel Request: {request.method} {request.path}")
        
        @flask_app.route('/api')
        def api_status():
            from flask import jsonify
            return jsonify({
                'status': 'success',
                'message': 'PactoC API is running on Vercel',
                'version': '1.0.0',
                'environment': 'production',
                'routes': [str(rule) for rule in flask_app.url_map.iter_rules()]
            })
        
        return flask_app
        
    except ImportError as import_err:
        # Handle missing dependencies gracefully
        return create_fallback_app(f"Import error: {import_err}")
        
    except Exception as init_err:
        # Handle other initialization errors
        return create_fallback_app(f"Initialization error: {init_err}")

def create_fallback_app(error_message):
    """Create a minimal fallback app when main app fails."""
    from flask import Flask, jsonify
    import traceback
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    def fallback_root():
        return jsonify({
            'status': 'fallback',
            'message': 'Main app failed to initialize - running in fallback mode',
            'error': error_message,
            'fallback': True,
            'note': 'This may be normal during local testing without all dependencies'
        })
    
    @fallback_app.route('/health')
    def fallback_health():
        return jsonify({
            'status': 'fallback_active',
            'healthy': False,
            'error': error_message
        })
    
    @fallback_app.route('/api')
    @fallback_app.route('/api/health')
    def fallback_api():
        return jsonify({
            'status': 'fallback_active',
            'api': True,
            'error': error_message,
            'note': 'Main API unavailable - check dependencies and configuration'
        })
    
    return fallback_app

# Create the application instance
app = create_application()

# Vercel handler function
def handler(event, context):
    """Vercel serverless handler."""
    return app

# For Vercel, we need to expose the app at module level
if __name__ == '__main__':
    # This won't run in Vercel, but useful for local testing
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
