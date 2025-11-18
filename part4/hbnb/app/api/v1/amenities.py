#!/usr/bin/python3
"""
Amenity API endpoints for the HBnB application.

This module provides RESTful API endpoints for managing amenities (features)
that can be associated with places (e.g., WiFi, Parking, Pool).

Routes:
    POST   /amenities/           - Create a new amenity (owner/admin only)
    GET    /amenities/           - List all amenities (public)
    GET    /amenities/<id>       - Get amenity details (public)
    PUT    /amenities/<id>       - Update an amenity (owner/admin only)
    DELETE /amenities/<id>       - Delete an amenity (owner/admin only)
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
    ),
    'place_id': fields.String(
        required=True, 
        description='UUID of the place this amenity belongs to'
    )
})

# Response model for amenity data
amenity_response_model = amenities_ns.model('AmenityResponse', {
    'id': fields.String(description='Unique amenity identifier (UUID)'),
    'name': fields.String(description='Name of the amenity'),
    'place_id': fields.String(description='UUID of the associated place'),
    'owner_id': fields.String(description='UUID of the place owner who created this amenity'),
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
    - Creating new amenities (POST)
    - Listing all existing amenities (GET)
    """
    
    @jwt_required()  # Requires valid JWT token
    @amenities_ns.expect(amenity_model, validate=True)
    @amenities_ns.response(201, 'Amenity successfully created', amenity_response_model)
    @amenities_ns.response(400, 'Invalid input data')
    @amenities_ns.response(403, 'Unauthorized - Only place owner or admin can create amenities')
    @amenities_ns.response(404, 'Place not found')
    def post(self):
        """
        Create a new amenity for a place.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The owner of the place
          * An admin user
        
        The amenity will be automatically linked to the place specified
        in the request and assigned to the place's owner.
        
        Returns:
            201: Amenity created successfully with amenity data
            400: Invalid input (missing required fields, validation errors)
            403: User is not authorized to add amenities to this place
            404: The specified place does not exist
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        try:
            # Extract amenity data from request body
            amenity_data = amenities_ns.payload
            place_id = amenity_data.get('place_id')
            
            # Verify that the place exists
            place = facade_instance.get_place(place_id)
            if not place:
                amenities_ns.abort(404, 'Place not found')
            
            # Authorization check: Only the place owner or an admin can add amenities
            if place.owner_id != current_user_id and not is_admin:
                amenities_ns.abort(403, 'You can only add amenities to your own places')
            
            # Automatically set the owner_id to the place owner's ID
            # (This ensures amenity ownership matches place ownership)
            amenity_data['owner_id'] = place.owner_id
            
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
        
        This is a public endpoint - no authentication required.
        Returns all amenities in the system, regardless of which place they belong to.
        
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
    - Retrieving amenity details (GET)
    - Updating amenity information (PUT)
    - Deleting an amenity (DELETE)
    """
    
    @amenities_ns.marshal_with(amenity_response_model)
    @amenities_ns.response(200, 'Amenity details retrieved successfully')
    @amenities_ns.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Get details of a specific amenity by its ID.
        
        This is a public endpoint - no authentication required.
        
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
    @amenities_ns.response(403, 'Unauthorized - Only place owner or admin can update amenities')
    @amenities_ns.response(404, 'Amenity or place not found')
    def put(self, amenity_id):
        """
        Update an existing amenity.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The owner of the place that the amenity belongs to
          * An admin user
        - If changing place_id, user must also own the new place (or be admin)
        
        Args:
            amenity_id (str): UUID of the amenity to update
            
        Returns:
            200: Amenity updated successfully with updated data
            400: Invalid input data
            403: User is not authorized to update this amenity
            404: Amenity or new place not found
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the amenity to verify it exists and check ownership
        amenity = facade_instance.get_amenity(amenity_id)
        if not amenity:
            amenities_ns.abort(404, 'Amenity not found')
        
        # Authorization check: Only the place owner or an admin can update amenities
        if amenity.owner_id != current_user_id and not is_admin:
            amenities_ns.abort(403, 'You can only update amenities of your own places')
        
        try:
            # Extract update data from request body
            amenity_data = amenities_ns.payload
            
            # If the place is being changed, verify the new place exists and check ownership
            if 'place_id' in amenity_data:
                new_place_id = amenity_data['place_id']
                new_place = facade_instance.get_place(new_place_id)
                
                # Verify the new place exists
                if not new_place:
                    amenities_ns.abort(404, 'New place not found')
                
                # Verify user owns the new place (or is admin)
                if new_place.owner_id != current_user_id and not is_admin:
                    amenities_ns.abort(403, 'You can only move amenities to your own places')
            
            # Update the amenity in the database
            updated_amenity = facade_instance.update_amenity(amenity_id, amenity_data)
            
            # This shouldn't happen (we already checked), but handle it just in case
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
    @amenities_ns.response(403, 'Unauthorized - Only place owner or admin can delete amenities')
    @amenities_ns.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """
        Delete an amenity.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The owner of the place that the amenity belongs to
          * An admin user
        
        Args:
            amenity_id (str): UUID of the amenity to delete
            
        Returns:
            204: Amenity deleted successfully (no content)
            403: User is not authorized to delete this amenity
            404: Amenity not found
        """
        # Get the current authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the amenity to verify it exists and check ownership
        amenity = facade_instance.get_amenity(amenity_id)
        if not amenity:
            amenities_ns.abort(404, 'Amenity not found')
        
        # Authorization check: Only the place owner or an admin can delete amenities
        if amenity.owner_id != current_user_id and not is_admin:
            amenities_ns.abort(403, 'You can only delete amenities of your own places')
        
        # Delete the amenity from the database
        if facade_instance.delete_amenity(amenity_id):
            # Return 204 No Content on successful deletion
            return {}, 204
        
        # This shouldn't happen (we already checked), but handle it just in case
        amenities_ns.abort(404, 'Amenity not found')