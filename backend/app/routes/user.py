from flask import Blueprint, request
from ..middleware.auth import require_auth
from ..utils.responses import success_response

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get user profile information."""
    user = request.user
    
    profile_data = {
        'uid': user.get('uid'),
        'email': user.get('email'),
        'email_verified': user.get('email_verified'),
        'name': user.get('name'),
        'picture': user.get('picture'),
        'auth_time': user.get('auth_time'),
        'firebase': user.get('firebase', {})
    }
    
    return success_response(profile_data, "Profile retrieved successfully")