from functools import wraps
from flask import request, jsonify
from ..services.firebase_service import FirebaseService
from ..utils.responses import error_response

def require_auth(f):
    """Middleware decorator to verify Firebase token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return error_response('No authorization header provided', 401)
        
        try:
            # Extract token (format: "Bearer <token>")
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            
            # Verify the token with Firebase
            decoded_token, error = FirebaseService.verify_token(token)
            
            if error:
                return error_response(f'Invalid token: {error}', 401)
            
            # Add user info to request context
            request.user = decoded_token
            
        except IndexError:
            return error_response('Invalid authorization header format', 401)
        except Exception as e:
            return error_response(f'Authentication failed: {str(e)}', 401)
        
        return f(*args, **kwargs)
    
    return decorated_function