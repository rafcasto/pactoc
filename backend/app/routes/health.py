from flask import Blueprint
from ..utils.responses import success_response

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    data = {
        'status': 'healthy',
        'service': 'Python Flask backend with Firebase auth',
        'version': '1.0.0'
    }
    return success_response(data, "Service is running")