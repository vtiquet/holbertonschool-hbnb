#!/usr/bin/python3
"""
Flask application factory for HBnB API.
Initializes Flask extensions (SQLAlchemy, JWT, Bcrypt), registers API namespaces, and configures error handlers.
"""

from flask import Flask, jsonify
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from flask_cors import CORS

# ========================================
# Initialize Flask extensions (before app creation)
# ========================================
bcrypt = Bcrypt()  # Password hashing (bcrypt algorithm)
jwt = JWTManager()  # JWT token management (authentication)
db = SQLAlchemy()  # ORM for database operations

# Facade will be imported after db is initialized to avoid circular imports
facade = None


def create_app(config_class=DevelopmentConfig):
    """
    Application factory pattern for creating Flask app instances.
    Args: config_class: Configuration class (default: DevelopmentConfig)
    Returns: Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ========================================
    # Initialize extensions with app context
    # ========================================
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ========================================
    # Create database tables (development only)
    # ========================================
    with app.app_context():
        # Import models so SQLAlchemy knows about them
        from app.models.user import User
        from app.models.place import Place
        from app.models.amenity import Amenity
        from app.models.review import Review
        
        # Create all tables if they don't exist
        db.create_all()
    
    # ========================================
    # Initialize facade after app context is created
    # ========================================
    global facade
    from app.services.facade import HBnBFacade
    facade = HBnBFacade()

    # ========================================
    # JWT ERROR HANDLERS (Flask-JWT-Extended)
    # ========================================
    
    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        """
        Handle expired JWT tokens (401 Unauthorized).
        Triggered when token exp claim has passed.
        """
        return jsonify({
            'error': 'Expired token',
            'message': 'The token has expired. Please login again.'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(_error):
        """
        Handle invalid JWT tokens (401 Unauthorized).
        Triggered when signature verification fails or token is malformed.
        """
        return jsonify({
            'error': 'Invalid token',
            'message': 'Signature verification failed or token is malformed.'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(_error):
        """
        Handle missing JWT tokens (401 Unauthorized).
        Triggered when Authorization header is missing or doesn't contain 'Bearer <token>'.
        """
        return jsonify({
            'error': 'Missing Authorization Header',
            'message': 'Request does not contain a valid access token.'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        """
        Handle revoked JWT tokens (401 Unauthorized).
        Triggered when token is in revocation list (if implemented).
        """
        return jsonify({
            'error': 'Revoked token',
            'message': 'The token has been revoked.'
        }), 401

    # ========================================
    # Configure JWT authorization in Swagger UI
    # ========================================
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }

    # ========================================
    # Initialize Flask-RESTX API with Swagger documentation
    # ========================================
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='A simple API for HBnB by Loic & Val',
        doc='/',  # Swagger UI available at root path
        authorizations=authorizations,  # Enable JWT auth in Swagger UI
        security='Bearer'  # Apply Bearer auth globally
    )

    # ========================================
    # GLOBAL ERROR HANDLERS (Flask-RESTX + PyJWT)
    # ========================================
    
    @api.errorhandler(ExpiredSignatureError)
    def handle_expired_signature(_error):
        """
        Handle expired JWT tokens from PyJWT library (401 Unauthorized).
        Catches errors raised by jwt.decode() when token exp has passed.
        """
        return {
            'error': 'Expired token',
            'message': 'The token has expired. Please login again.'
        }, 401

    @api.errorhandler(InvalidTokenError)
    def handle_invalid_token(_error):
        """
        Handle invalid JWT tokens from PyJWT library (401 Unauthorized).
        Catches errors raised by jwt.decode() when signature verification fails.
        """
        return {
            'error': 'Invalid token',
            'message': 'Signature verification failed or token is malformed.'
        }, 401

    @api.errorhandler(NoAuthorizationError)
    def handle_no_authorization(_error):
        """
        Handle missing authorization header (401 Unauthorized).
        Catches errors raised by @jwt_required decorator when header is missing.
        """
        return {
            'error': 'Missing Authorization Header',
            'message': 'Request does not contain a valid access token.'
        }, 401

    # ========================================
    # Register API namespaces (route blueprints)
    # ========================================
    from .api.v1.users import users_ns
    from .api.v1.places import places_ns
    from .api.v1.reviews import reviews_ns
    from .api.v1.amenities import amenities_ns
    from .api.v1.auth import auth_ns

    # Add namespaces to API with URL prefixes
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    return app