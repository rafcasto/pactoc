"""
Minimal debug server for Vercel deployment troubleshooting.
"""

def app(environ, start_response):
    """WSGI application for basic debugging."""
    import json
    import os
    
    # Basic health check
    if environ['PATH_INFO'] == '/':
        response_body = json.dumps({
            'status': 'ok',
            'message': 'Minimal debug server running',
            'vercel': os.environ.get('VERCEL', 'Not set'),
            'python_executable': os.environ.get('PYTHON_EXECUTABLE', 'Not available')
        })
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [response_body.encode('utf-8')]
    
    # Environment check
    elif environ['PATH_INFO'] == '/env':
        env_check = {}
        required_vars = ['DATABASE_URL', 'SECRET_KEY', 'FIREBASE_SERVICE_ACCOUNT_BASE64']
        
        for var in required_vars:
            env_check[var] = 'SET' if os.environ.get(var) else 'NOT_SET'
        
        response_body = json.dumps({
            'environment_variables': env_check,
            'total_env_count': len(os.environ)
        })
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [response_body.encode('utf-8')]
    
    # Flask import test
    elif environ['PATH_INFO'] == '/flask-test':
        try:
            from flask import Flask
            test_app = Flask(__name__)
            
            response_body = json.dumps({
                'flask_import': 'SUCCESS',
                'flask_version': getattr(Flask, '__version__', 'Unknown')
            })
            status = '200 OK'
        except Exception as e:
            response_body = json.dumps({
                'flask_import': 'FAILED',
                'error': str(e)
            })
            status = '500 Internal Server Error'
        
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [response_body.encode('utf-8')]
    
    # 404 for other paths
    else:
        response_body = json.dumps({
            'error': 'Not found',
            'available_endpoints': ['/', '/env', '/flask-test']
        })
        status = '404 Not Found'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [response_body.encode('utf-8')]
