#!/usr/bin/python3
"""
Auth namespace for handling user authentication (login/logout).
"""

from flask import request
from flask_restx import Namespace, Resource, fields
# CRITICAL IMPORT: Used to create the JWT token
from flask_jwt_extended import create_access_token 

# ====================================================================
# FIX: Ensure correct import of initialized application extensions/services
# 'facade' and 'bcrypt' must be imported from the main 'app' module.
# ====================================================================
try:
    from app import facade, bcrypt 
except ImportError:
    # Fallback import path if the direct 'from app import' fails
    from hbnb.app import facade, bcrypt 


auth_ns = Namespace('auth', description='User authentication operations')

# Define the data model for the login request
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
})

@auth_ns.route('/login')
class AuthLogin(Resource):
    """
    Handles user login requests.
    """
    @auth_ns.doc('user_login')
    @auth_ns.expect(login_model, validate=True)
    def post(self):
        """
        Logs in a user and returns an access token upon success.
        """
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {'message': 'Missing email or password in request.'}, 400

            user = facade.get_user_by_email(email)

            # CRITICAL FIX: Ensure password hash is encoded to bytes for bcrypt if necessary.
            # We also check if user exists AND has a hash to prevent an AttributeError if facade returns a User object without a hash.
            if not user or not user.password_hash or not bcrypt.check_password_hash(user.password_hash.encode('utf-8'), password):
                return {'message': 'Invalid credentials (email or password).'}, 401

            # Generate token
            access_token = create_access_token(identity=user.id)

            # Return the token
            return {
                'message': 'Login successful',
                'token': access_token
            }, 200

        except Exception as e:
            # Catch all unexpected errors
            print(f"Login error: {e}")
            return {'message': 'An internal error occurred during login.'}, 500


@auth_ns.route('/logout')
class AuthLogout(Resource):
    """
    Handles user logout requests (optional for server-side).
    """
    def post(self):
        """
        Server-side logout placeholder (client-side handles cookie deletion).
        """
        return {'message': 'Logout successful.'}, 200