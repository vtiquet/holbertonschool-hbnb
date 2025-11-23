#!/usr/bin/python3
"""
Amenity API endpoints for the HBnB application.

This module provides RESTful API endpoints for managing amenities (features)
that can be associated with places (e.g., WiFi, Parking, Pool).

Routes:
    POST   /amenities/           - Create a new amenity (ADMIN ONLY)
    GET    /amenities/           - List all amenities (public)
    GET    /amenities/<id>       - Get amenity details (public)
    PUT    /amenities/<id>       - Update an amenity (ADMIN ONLY)
    DELETE /amenities/<id>       - Delete an amenity (ADMIN ONLY)
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from app import facade as facade_instance
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Create a namespace for amenity-related operations
amenities_ns = Namespace('amenities', description='Amenity operations')


# -----------------------
# Swagger API Models
# -----------------------

# Input model for creating/updating amenities
amenity_model = amenities_ns.model('AmenityInput', {
    'name': fields.String(
        required=True, 
        description='Name of the amenity (e.g., WiFi, Parking, Pool)'
    )
})

# Response model for amenity data
amenity_response_model = amenities_ns.model('AmenityResponse', {
    'id': fields.String(description='Unique amenity identifier (UUID)'),
    'name': fields.String(description='Name of the amenity'),
    'created_at': fields.String(description='ISO 8601 timestamp of creation'),
    'updated_at': fields.String(description='ISO 8601 timestamp of last update')
})


# -----------------------
# API Routes
# -----------------------

@amenities_ns.route('/')
class AmenityList(Resource):
    """
    Handles operations on the collection of amenities.
    
    This resource manages:
    - Creating new amenities (POST - ADMIN ONLY)
    - Listing all existing amenities (GET - PUBLIC)
    """
    
    @jwt_required()  # Requires valid JWT token
    @amenities_ns.expect(amenity_model, validate=True)
    @amenities_ns.response(201, 'Amenity successfully created', amenity_response_model)
    @amenities_ns.response(400, 'Invalid input data')
    @amenities_ns.response(403, 'Forbidden - Only administrators can create amenities')
    @amenities_ns.response(409, 'Conflict - Amenity with this name already exists')
    def post(self):
        """
        Create a new amenity (ADMIN ONLY).
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be an administrator (is_admin = True)
        
        Amenities are global resources that can be selected by any place owner.
        Only admins can create new amenity types to maintain consistency.
        
        Returns:
            201: Amenity created successfully with amenity data
            400: Invalid input (missing required fields, validation errors)
            403: User is not an administrator
            409: Amenity with this name already exists
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Check if user is admin
        if not is_admin:
            amenities_ns.abort(403, 'Only administrators can create amenities')
        
        try:
            # Extract amenity data from request body
            amenity_data = amenities_ns.payload
            amenity_name = amenity_data.get('name', '').strip()
            
            # Check if amenity with this name already exists (case-insensitive)
            existing_amenities = facade_instance.get_all_amenities()
            for amenity in existing_amenities:
                if amenity.name.lower() == amenity_name.lower():
                    amenities_ns.abort(409, f'Amenity "{amenity_name}" already exists')
            
            # Create the amenity in the database
            new_amenity = facade_instance.create_amenity(amenity_data)
            
            # Return the created amenity with 201 Created status
            return new_amenity.to_dict(), 201
            
        except ValueError as e:
            # Handle validation errors (e.g., missing required fields)
            amenities_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            amenities_ns.abort(500, f"Internal error: {str(e)}")

    @amenities_ns.marshal_list_with(amenity_response_model)
    @amenities_ns.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """
        Retrieve a list of all amenities.
        
        This is a PUBLIC endpoint - no authentication required.
        Returns all amenities in the system that can be selected when creating/updating places.
        
        Returns:
            200: List of all amenities with their details
        """
        # Fetch all amenities from the database
        amenities = facade_instance.get_all_amenities()
        
        # Convert each amenity object to a dictionary for JSON serialization
        return [amenity.to_dict() for amenity in amenities]


@amenities_ns.route('/<string:amenity_id>')
@amenities_ns.param('amenity_id', 'The Amenity identifier (UUID)')
class AmenityResource(Resource):
    """
    Handles operations on a single amenity resource.
    
    This resource manages:
    - Retrieving amenity details (GET - PUBLIC)
    - Updating amenity information (PUT - ADMIN ONLY)
    - Deleting an amenity (DELETE - ADMIN ONLY)
    """
    
    @amenities_ns.marshal_with(amenity_response_model)
    @amenities_ns.response(200, 'Amenity details retrieved successfully')
    @amenities_ns.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Get details of a specific amenity by its ID.
        
        This is a PUBLIC endpoint - no authentication required.
        
        Args:
            amenity_id (str): UUID of the amenity to retrieve
            
        Returns:
            200: Amenity details
            404: Amenity with the given ID does not exist
        """
        # Fetch the amenity from the database
        amenity = facade_instance.get_amenity(amenity_id)
        
        # Return 404 if amenity doesn't exist
        if not amenity:
            amenities_ns.abort(404, 'Amenity not found')
        
        # Return the amenity details
        return amenity.to_dict()

    @jwt_required()  # Requires valid JWT token
    @amenities_ns.expect(amenity_model, validate=True)
    @amenities_ns.marshal_with(amenity_response_model)
    @amenities_ns.response(200, 'Amenity updated successfully')
    @amenities_ns.response(400, 'Invalid input data')
    @amenities_ns.response(403, 'Forbidden - Only administrators can update amenities')
    @amenities_ns.response(404, 'Amenity not found')
    @amenities_ns.response(409, 'Conflict - Amenity with this name already exists')
    def put(self, amenity_id):
        """
        Update an existing amenity (ADMIN ONLY).
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be an administrator (is_admin = True)
        
        Args:
            amenity_id (str): UUID of the amenity to update
            
        Returns:
            200: Amenity updated successfully with updated data
            400: Invalid input data
            403: User is not an administrator
            404: Amenity not found
            409: Amenity with this name already exists
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Check if user is admin
        if not is_admin:
            amenities_ns.abort(403, 'Only administrators can update amenities')
        
        # Fetch the amenity to verify it exists
        amenity = facade_instance.get_amenity(amenity_id)
        if not amenity:
            amenities_ns.abort(404, 'Amenity not found')
        
        try:
            # Extract update data from request body
            amenity_data = amenities_ns.payload
            new_name = amenity_data.get('name', '').strip()
            
            # Check if new name conflicts with existing amenities (except itself)
            if new_name:
                existing_amenities = facade_instance.get_all_amenities()
                for existing in existing_amenities:
                    if existing.id != amenity_id and existing.name.lower() == new_name.lower():
                        amenities_ns.abort(409, f'Amenity "{new_name}" already exists')
            
            # Update the amenity in the database
            updated_amenity = facade_instance.update_amenity(amenity_id, amenity_data)
            
            if not updated_amenity:
                amenities_ns.abort(404, 'Amenity not found')
            
            # Return the updated amenity data
            return updated_amenity.to_dict()
            
        except ValueError as e:
            # Handle validation errors
            amenities_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            amenities_ns.abort(500, f"Internal error: {str(e)}")

    @jwt_required()  # Requires valid JWT token
    @amenities_ns.response(204, 'Amenity deleted successfully')
    @amenities_ns.response(403, 'Forbidden - Only administrators can delete amenities')
    @amenities_ns.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """
        Delete an amenity (ADMIN ONLY).
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be an administrator (is_admin = True)
        
        Note: Deleting an amenity will remove it from all places that use it.
        
        Args:
            amenity_id (str): UUID of the amenity to delete
            
        Returns:
            204: Amenity deleted successfully (no content)
            403: User is not an administrator
            404: Amenity not found
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Check if user is admin
        if not is_admin:
            amenities_ns.abort(403, 'Only administrators can delete amenities')
        
        # Fetch the amenity to verify it exists
        amenity = facade_instance.get_amenity(amenity_id)
        if not amenity:
            amenities_ns.abort(404, 'Amenity not found')
        
        # Delete the amenity from the database
        if facade_instance.delete_amenity(amenity_id):
            # Return 204 No Content on successful deletion
            return {}, 204
        
        # This shouldn't happen (we already checked), but handle it just in case
        amenities_ns.abort(404, 'Amenity not found')