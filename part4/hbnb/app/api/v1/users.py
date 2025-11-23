#!/usr/bin/python3
"""
User API endpoints for the HBnB application.

This module provides RESTful API endpoints for managing user accounts.
Users can register, view profiles, and update their own information.

Routes:
    POST   /users/                  - Register a new user (public)
    GET    /users/                  - List all users (public)
    GET    /users/<id>              - Get user details (public)
    PUT    /users/<id>              - Update own profile (owner only, requires password)
    DELETE /users/<id>              - Delete a user (admin only)
    PUT    /users/admin/<id>        - Update any user (admin only)

Authorization model:
- Regular users can only update their own first_name and last_name (requires password verification)
- Admins can update any user's information including email and password
- Only admins can delete users
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from app import facade as facade_instance
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


# Create a namespace for user-related operations
users_ns = Namespace('users', description='User operations')


# -----------------------
# Swagger API Models
# -----------------------

# Input model for user registration
user_model = users_ns.model('UserInput', {
    'first_name': fields.String(
        required=True, 
        description='First name of the user',
        example='John'
    ),
    'last_name': fields.String(
        required=True, 
        description='Last name of the user',
        example='Doe'
    ),
    'email': fields.String(
        required=True, 
        description='Email address (must be unique)',
        example='john.doe@example.com'
    ),
    'password': fields.String(
        required=True, 
        description='Password (will be hashed with bcrypt)',
        example='securePassword123'
    ),
})

# Response model for user data (excludes password hash)
user_response_model = users_ns.model('UserResponse', {
    'id': fields.String(description='Unique user identifier (UUID)'),
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email address'),
    'is_admin': fields.Boolean(
        description='Administrative privileges flag',
        default=False
    ),
    'created_at': fields.String(description='ISO 8601 timestamp of account creation'),
    'updated_at': fields.String(description='ISO 8601 timestamp of last update')
})

# Input model for user self-update (regular users)
user_update_model = users_ns.model('UserUpdateInput', {
    'first_name': fields.String(
        required=True, 
        description='New first name',
        example='Jane'
    ),
    'last_name': fields.String(
        required=True, 
        description='New last name',
        example='Smith'
    ),
    'email': fields.String(
        required=True, 
        description='Current email (for identity verification)',
        example='john.doe@example.com'
    ),
    'password': fields.String(
        required=True, 
        description='Current password (for identity verification)',
        example='securePassword123'
    ),
})

# Input model for admin updates (all fields optional)
admin_update_model = users_ns.model('AdminUpdateInput', {
    'first_name': fields.String(
        required=False, 
        description='New first name',
        example='UpdatedName'
    ),
    'last_name': fields.String(
        required=False, 
        description='New last name',
        example='UpdatedLastName'
    ),
    'email': fields.String(
        required=False, 
        description='New email address (must be unique)',
        example='newemail@example.com'
    ),
    'password': fields.String(
        required=False, 
        description='New password (will be hashed)',
        example='newSecurePassword456'
    ),
})


# -----------------------
# API Routes
# -----------------------

@users_ns.route('/')
class UserList(Resource):
    """
    Handles operations on the collection of users.
    
    This resource manages:
    - User registration (POST - public)
    - Listing all users (GET - public)
    """

    @users_ns.expect(user_model, validate=True)
    @users_ns.response(201, 'User successfully created', user_response_model)
    @users_ns.response(400, 'Email already registered or invalid input')
    @users_ns.response(500, 'Internal server error')
    def post(self):
        """
        Register a new user account.
        
        This is a public endpoint - no authentication required.
        
        The password will be automatically hashed using bcrypt before storage.
        By default, new users are created with is_admin=False.
        
        Email validation:
        - Must be a valid email format
        - Must be unique (not already registered)
        
        Returns:
            201: User created successfully with user data (excluding password)
            400: Invalid input or email already in use
            500: Server error during user creation
        """
        # Extract user data from request body
        user_data = request.get_json() or {}

        try:
            # Create the user in the database
            # The facade will hash the password and validate the email
            new_user = facade_instance.create_user(user_data)
        except (ValueError, TypeError) as e:
            # Handle validation errors (invalid email, missing fields, etc.)
            users_ns.abort(400, message=str(e))
        except Exception:
            # Handle unexpected errors
            users_ns.abort(500, message='Internal server error')

        # Return the created user (password is excluded by to_dict())
        return new_user.to_dict(), 201

    @users_ns.marshal_list_with(user_response_model)
    @users_ns.response(200, 'List of users retrieved successfully')
    def get(self):
        """
        Retrieve a list of all registered users.
        
        This is a public endpoint - no authentication required.
        Returns all users with their basic information (excluding passwords).
        
        This endpoint is useful for:
        - Displaying a list of place owners
        - User search functionality
        - Admin dashboards
        
        Returns:
            200: List of all users
        """
        # Fetch all users from the database
        users = facade_instance.get_all_user()
        
        # Convert each user object to a dictionary (excludes password)
        return [u.to_dict() for u in users]


@users_ns.route('/<string:user_id>')
@users_ns.param('user_id', 'The user unique identifier (UUID)')
class UserResource(Resource):
    """
    Handles operations on a single user resource.
    
    This resource manages:
    - Retrieving user details (GET - public)
    - Updating own profile (PUT - owner only, requires password)
    - Deleting a user (DELETE - admin only)
    """

    @users_ns.marshal_with(user_response_model)
    @users_ns.response(200, 'User details retrieved successfully')
    @users_ns.response(404, 'User not found')
    def get(self, user_id):
        """
        Get detailed information about a specific user.
        
        This is a public endpoint - no authentication required.
        Returns user information excluding sensitive data (password).
        
        Args:
            user_id (str): UUID of the user to retrieve
            
        Returns:
            200: User details
            404: User not found
        """
        # Fetch the user from the database
        user = facade_instance.get_user(user_id) 
        
        # Return 404 if user doesn't exist
        if not user:
            users_ns.abort(404, 'User not found')
        
        # Return user data (password excluded by to_dict())
        return user.to_dict()

    @jwt_required()  # Requires valid JWT token
    @users_ns.expect(user_update_model, validate=True)
    @users_ns.marshal_with(user_response_model) 
    @users_ns.response(200, 'User successfully updated')
    @users_ns.response(400, 'Invalid input data')
    @users_ns.response(401, 'Invalid email or password')
    @users_ns.response(403, 'Unauthorized - Can only update own profile')
    @users_ns.response(404, 'User not found')
    def put(self, user_id):
        """
        Update own user profile (regular users).
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User can only update their own profile (user_id must match token)
        - Requires current email and password for verification
        - Admins must use the /admin/{user_id} endpoint instead
        
        Updatable fields (regular users):
        - first_name
        - last_name
        
        Restricted fields (cannot be updated by regular users):
        - email (admin only)
        - password (admin only)
        - is_admin (admin only)
        
        Security:
        - Requires email + password verification before any change
        - This prevents unauthorized updates if a token is compromised
        
        Args:
            user_id (str): UUID of the user to update
            
        Returns:
            200: User updated successfully
            401: Invalid email or password
            403: Trying to update another user's profile
            404: User not found
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Authorization check: User can only update their own profile
        if current_user_id != user_id:
            if is_admin:
                # Admins should use the dedicated admin endpoint
                users_ns.abort(403, 'Admins must use /api/v1/users/admin/{user_id} endpoint')
            else:
                # Regular users cannot update other profiles
                users_ns.abort(403, 'Unauthorized action')
        
        # Extract update data from request body
        data = users_ns.payload
        
        # Fetch the user to verify credentials
        user = facade_instance.get_user(user_id)
        if not user:
            users_ns.abort(404, 'User not found')
        
        # Security verification: Check email and password match
        # This prevents unauthorized updates even with a valid JWT token
        if user.email != data.get('email') or not user.verify_password(data.get('password', '')):
            users_ns.abort(401, 'Invalid email or password')
        
        # Prepare update data (only allow first_name and last_name for regular users)
        update_data = {
            'first_name': data['first_name'],
            'last_name': data['last_name']
        }

        try:
            # Update the user in the database
            updated_user = facade_instance.update_user(user_id, update_data)
        except ValueError as e:
            # Handle validation errors
            users_ns.abort(400, str(e))

        # This shouldn't happen (we already checked), but handle it just in case
        if not updated_user:
            users_ns.abort(404, 'User not found')

        # Return the updated user data
        return updated_user.to_dict()

    @jwt_required()  # Requires valid JWT token
    @users_ns.response(200, 'User successfully deleted')
    @users_ns.response(403, 'Admin privileges required')
    @users_ns.response(404, 'User not found')
    def delete(self, user_id):
        """
        Delete a user account.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - Only admins can delete users
        
        Cascade behavior:
        - All places owned by the user will be deleted
        - All reviews written by the user will be deleted
        - All amenities created by the user will be deleted
        - This is handled by SQLAlchemy cascade rules
        
        Args:
            user_id (str): UUID of the user to delete
            
        Returns:
            200: User deleted successfully
            403: Non-admin user attempting deletion
            404: User not found
        """
        # Get additional claims from the JWT
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Authorization check: Only admins can delete users
        if not is_admin:
            users_ns.abort(403, 'Admin privileges required')
        
        # Delete the user from the database
        # SQLAlchemy cascade will handle related entities (places, reviews, amenities)
        deleted = facade_instance.delete_user(user_id)
        
        # Return 404 if user doesn't exist
        if not deleted:
            users_ns.abort(404, 'User not found')
        
        # Return success message
        return {"message": "User successfully deleted"}, 200


@users_ns.route('/admin/<string:user_id>')
@users_ns.param('user_id', 'The user unique identifier (UUID)')
class AdminUserResource(Resource):
    """
    Handles admin-only operations on user accounts.
    
    This endpoint allows admins to update any user's information,
    including sensitive fields like email and password.
    """

    @jwt_required()  # Requires valid JWT token
    @users_ns.expect(admin_update_model, validate=True)
    @users_ns.marshal_with(user_response_model) 
    @users_ns.response(200, 'User successfully updated by admin')
    @users_ns.response(400, 'Invalid input data or email already in use')
    @users_ns.response(403, 'Admin privileges required')
    @users_ns.response(404, 'User not found')
    def put(self, user_id):
        """
        Update any user's profile (admin only).
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must have admin privileges (is_admin=True)
        
        Updatable fields (all optional):
        - first_name
        - last_name
        - email (must remain unique)
        - password (will be hashed before storage)
        
        Differences from regular user update:
        - No password verification required (admin privilege)
        - Can update any user (not just own profile)
        - Can modify email and password
        
        Args:
            user_id (str): UUID of the user to update
            
        Returns:
            200: User updated successfully
            400: Invalid input or email already in use
            403: Non-admin user attempting admin operation
            404: User not found
        """
        # Get additional claims from the JWT
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Authorization check: Only admins can use this endpoint
        if not is_admin:
            users_ns.abort(403, 'Admin privileges required')
        
        # Extract update data from request body
        data = users_ns.payload
        
        # Fetch the user to verify it exists
        user = facade_instance.get_user(user_id)
        if not user:
            users_ns.abort(404, 'User not found')
        
        # Email uniqueness check (only if email is being changed)
        if 'email' in data and data['email']:
            # Check if the new email is already used by another user
            existing_user = facade_instance.get_user_by_email(data['email'])
            if existing_user and existing_user.id != user_id:
                users_ns.abort(400, 'Email already in use')

        # Remove empty fields from the update data
        # This allows partial updates (only send fields you want to change)
        update_data = {k: v for k, v in data.items() if v not in [None, '', []]}

        try:
            # Update the user in the database
            # If password is included, the facade will hash it before storage
            updated_user = facade_instance.update_user(user_id, update_data)
        except ValueError as e:
            # Handle validation errors
            users_ns.abort(400, str(e))

        # This shouldn't happen (we already checked), but handle it just in case
        if not updated_user:
            users_ns.abort(404, 'User not found')

        # Return the updated user data
        return updated_user.to_dict()