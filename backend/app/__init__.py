from flask import Flask
from .config import config
from .extensions import cors
from .services.firebase_service import FirebaseService
from .services.database_service import init_db
from .routes.health import health_bp
from .routes.auth import auth_bp
from .routes.user import user_bp
# New meal plan system routes (PostgreSQL-based)
from .routes.invitations_sql import invitations_bp
from .routes.patients_sql import patients_bp
from .routes.catalogs_sql import catalogs_bp
from .routes.meal_plans import meal_plans_bp
from .utils.responses import error_response
import logging
import os

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Firebase (only for authentication)
    with app.app_context():
        FirebaseService.initialize()
    
    # Initialize PostgreSQL database
    with app.app_context():
        init_db(app)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    # Register meal plan system blueprints (PostgreSQL-based)
    app.register_blueprint(invitations_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(catalogs_bp)
    app.register_blueprint(meal_plans_bp)
    
    # Register public routes (no authentication required)
    from .routes.public import public_bp
    app.register_blueprint(public_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return error_response('Endpoint not found', 404, 'NOT_FOUND')
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response('Internal server error', 500, 'INTERNAL_ERROR')
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response('Bad request', 400, 'BAD_REQUEST')
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    return app