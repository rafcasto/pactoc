from flask import jsonify
from datetime import datetime

def success_response(data=None, message="Success", status_code=200):
    """Standardized success response."""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, error_code=None):
    """Standardized error response."""
    response = {
        'success': False,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_code:
        response['error_code'] = error_code
    
    return jsonify(response), status_code