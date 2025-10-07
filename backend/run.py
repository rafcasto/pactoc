#!/usr/bin/env python3
"""
Vercel-compatible Flask application entry point.
Root-level run.py for Vercel deployment.
"""
import os
import sys

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('VERCEL', '1')

def create_application():
    """Create and configure the Flask application for Vercel."""
    
    # First, try to create the main application
    try:
        from app import create_app
        flask_app = create_app('production')
        
        # Add Vercel-specific logging
        @flask_app.before_request
        def log_request():
            from flask import request
            flask_app.logger.info(f"Vercel Request: {request.method} {request.path}")
        
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
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    @fallback_app.route('/health')
    def fallback_health():
        return jsonify({
            'status': 'fallback',
            'message': 'Main app failed to initialize - running in fallback mode',
            'error': error_message,
            'fallback': True
        })
    
    @fallback_app.route('/api/<path:path>')
    def fallback_api(path):
        return jsonify({
            'status': 'fallback_active',
            'path': path,
            'error': error_message,
            'note': 'Main API unavailable - check dependencies and configuration'
        })
    
    return fallback_app

# Create the application instance
app = create_application()

# For Vercel, we need to expose the app at module level
if __name__ == '__main__':
    # This won't run in Vercel, but useful for local testing
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
