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
from .routes.meal_plan_workflow import workflow_bp
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
        try:
            FirebaseService.initialize()
        except Exception as e:
            app.logger.warning(f"Firebase initialization failed: {e}")
    
    # Initialize PostgreSQL database
    with app.app_context():
        try:
            # Only initialize DB if DATABASE_URL is provided
            if os.getenv('DATABASE_URL'):
                init_db(app)
            else:
                app.logger.warning("DATABASE_URL not set, skipping database initialization")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
            # In Vercel/serverless, continue without DB for health checks
            # The database will be initialized on first actual use
            if not os.getenv('VERCEL') and not os.getenv('SERVERLESS'):
                raise
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    # Register meal plan system blueprints (PostgreSQL-based)
    app.register_blueprint(invitations_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(catalogs_bp)
    app.register_blueprint(meal_plans_bp)
    app.register_blueprint(workflow_bp)
    
    # Register new business rules routes
    from .routes.nutritionist_routes import nutritionist_bp
    from .routes.patient_meal_plan_routes import patient_meal_plan_bp
    app.register_blueprint(nutritionist_bp)
    app.register_blueprint(patient_meal_plan_bp)
    
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