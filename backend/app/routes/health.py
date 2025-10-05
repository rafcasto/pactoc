import time
from flask import Blueprint
from ..utils.responses import success_response, error_response
from ..services.database_service import test_connection

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

@health_bp.route('/health/db', methods=['GET'])
def db_health_check():
    """Database health check endpoint."""
    start_time = time.time()
    db_healthy = test_connection(retry_count=1)  # Single attempt for health check
    response_time = time.time() - start_time
    
    if db_healthy:
        data = {
            'status': 'healthy',
            'database': 'PostgreSQL',
            'response_time_ms': round(response_time * 1000, 2)
        }
        return success_response(data, "Database connection is healthy")
    else:
        data = {
            'status': 'unhealthy',
            'database': 'PostgreSQL',
            'response_time_ms': round(response_time * 1000, 2)
        }
        return error_response("Database connection failed", 503, data)