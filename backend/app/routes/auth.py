from flask import Blueprint, request
from ..middleware.auth import require_auth
from ..utils.responses import success_response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/hello', methods=['GET'])
@require_auth
def hello_world():
    """Simple authenticated endpoint."""
    user = request.user
    
    data = {
        'message': 'Hello from authenticated Python backend!',
        'user': {
            'uid': user.get('uid'),
            'email': user.get('email'),
            'name': user.get('name', 'Anonymous')
        },
        'auth_time': user.get('auth_time')
    }
    
    return success_response(data, "Authentication successful")

@auth_bp.route('/protected', methods=['POST'])
@require_auth
def protected_endpoint():
    """Protected POST endpoint."""
    user = request.user
    data = request.get_json() or {}
    
    response_data = {
        'message': 'This is a protected endpoint',
        'received_data': data,
        'authenticated_user': user.get('email'),
        'user_id': user.get('uid')
    }
    
    return success_response(response_data, "Protected endpoint accessed successfully")
