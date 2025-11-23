#!/usr/bin/python3
"""
Authentication API endpoints for the HBnB application.

This module handles user authentication using JWT (JSON Web Tokens).
It provides endpoints for:
- User login with email/password
- Token generation with user identity and admin claims
- Protected route demonstration

The JWT tokens include:
- User ID as the identity claim
- is_admin flag as an additional claim for authorization
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import facade as facade_instance


# Create a namespace for authentication-related operations
auth_ns = Namespace('auth', description='Authentication operations')


# -----------------------
# Swagger API Models
# -----------------------

# Input model for user login credentials
login_model = auth_ns.model('Login', {
    'email': fields.String(
        required=True, 
        description='User email address',
        example='user@example.com'
    ),
    'password': fields.String(
        required=True, 
        description='User password (plaintext - will be hashed for verification)',
        example='password123'
    )
})

# Response model for successful login
login_response_model = auth_ns.model('LoginResponse', {
    'access_token': fields.String(
        description='JWT access token to be used in Authorization header',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    )
})


# -----------------------
# API Routes
# -----------------------

@auth_ns.route('/login')
class Login(Resource):
    """
    Handles user authentication and JWT token generation.
    
    This endpoint authenticates users by verifying their email and password,
    then returns a JWT token that can be used to access protected endpoints.
    """
    
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, 'Login successful', login_response_model)
    @auth_ns.response(400, 'Invalid input data')
    @auth_ns.response(401, 'Invalid credentials - wrong email or password')
    def post(self):
        """
        Authenticate user and generate a JWT access token.
        
        Authentication flow:
        1. Verify that a user with the provided email exists
        2. Verify the password using bcrypt hashing
        3. Generate a JWT token containing:
           - User ID (as identity claim)
           - Admin status (as additional claim)
        4. Return the token to the client
        
        The client should include this token in the Authorization header
        for subsequent requests: "Bearer <token>"
        
        Returns:
            200: Authentication successful with JWT token
            401: Invalid email or password
        """
        # Extract credentials from the request body
        credentials = auth_ns.payload
        
        # Step 1: Retrieve the user from database using their email
        user = facade_instance.get_user_by_email(credentials['email'])
        
        # Step 2: Verify user exists and password is correct
        # - If user doesn't exist, user will be None
        # - verify_password() uses bcrypt to compare hashed password
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token containing user information
        # - identity: User's UUID (used to identify the user in protected routes)
        # - additional_claims: Extra data embedded in the token (e.g., admin status)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )
        
        # Step 4: Return the JWT token to the client
        # Client should store this token and include it in future requests
        return {'access_token': access_token}, 200


@auth_ns.route('/protected')
class ProtectedResource(Resource):
    """
    Demonstration endpoint showing how to protect routes with JWT.
    
    This is an example endpoint that requires a valid JWT token.
    It shows how to extract the user identity from the token.
    """
    
    @jwt_required()  # Decorator that enforces JWT authentication
    @auth_ns.response(200, 'Access granted - Valid token provided')
    @auth_ns.response(401, 'Unauthorized - Invalid, expired, or missing token')
    def get(self):
        """
        Example of a protected endpoint requiring authentication.
        
        This endpoint demonstrates:
        - How to require JWT authentication using @jwt_required()
        - How to extract the user ID from the token using get_jwt_identity()
        
        To access this endpoint, clients must include the JWT token
        in the Authorization header:
        Authorization: Bearer <your_jwt_token>
        
        Returns:
            200: Access granted with user identity
            401: Access denied (invalid/missing token)
        """
        # Extract the user ID from the JWT token
        # This ID matches the 'identity' claim set during login
        current_user = get_jwt_identity()
        
        # Return a personalized message with the authenticated user's ID
        return {'message': f'Hello, user {current_user}'}, 200
