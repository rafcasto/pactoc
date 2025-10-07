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

def create_application():
    """Create and configure the Flask application for Vercel."""
    try:
        from app import create_app
        
        # Create app with production config
        flask_app = create_app('production')
        
        return flask_app
        
    except Exception as e:
        # Fallback to minimal app if main app fails
        from flask import Flask, jsonify
        
        fallback_app = Flask(__name__)
        
        @fallback_app.route('/')
        def health():
            return jsonify({
                'status': 'error',
                'message': 'Main app failed to initialize',
                'error': str(e),
                'fallback': True
            })
        
        @fallback_app.route('/health')
        def health_check():
            return jsonify({'status': 'fallback_active'})
            
        return fallback_app

# Create the application instance
app = create_application()

# For Vercel, we need to expose the app at module level
if __name__ == '__main__':
    # This won't run in Vercel, but useful for local testing
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
