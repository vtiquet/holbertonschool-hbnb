#!/usr/bin/python3
"""
Place API endpoints for the HBnB application.

This module provides RESTful API endpoints for managing places (properties/listings).
Places represent accommodations that can be rented, such as apartments, houses, or villas.

Routes:
    POST   /places/              - Create a new place (owner only)
    GET    /places/              - List all places (public)
    GET    /places/<id>          - Get place details (public)
    PUT    /places/<id>          - Update a place (owner/admin only)
    DELETE /places/<id>          - Delete a place (owner/admin only)

Each place includes:
- Basic information (title, description, price, location)
- Owner information (user who created the place)
- Amenities (features like WiFi, Parking, Pool)
- Reviews (ratings and comments from users)
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from app import facade as facade_instance
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


# Create a namespace for place-related operations
places_ns = Namespace('places', description='Place operations')


# -----------------------
# Swagger API Models
# -----------------------

# Nested model for amenity display in place responses
amenity_model = places_ns.model('PlaceAmenity', {
    'id': fields.String(description='Unique amenity identifier (UUID)'),
    'name': fields.String(description='Name of the amenity (e.g., WiFi, Parking)')
})

# Nested model for owner/user display in place responses
user_model = places_ns.model('PlaceUser', {
    'id': fields.String(description='Unique user identifier (UUID)'),
    'first_name': fields.String(description='First name of the place owner'),
    'last_name': fields.String(description='Last name of the place owner'),
    'email': fields.String(description='Email address of the place owner')
})

# Nested model for review display in place responses
review_display_model = places_ns.model('PlaceReview', {
    'id': fields.String(description='Unique review identifier (UUID)'),
    'text': fields.String(description='Review content/comments'),
    'rating': fields.Integer(description='Rating from 1 (worst) to 5 (best)'),
    'user_id': fields.String(description='UUID of the user who wrote the review')
})

# Input model for creating a new place
place_model = places_ns.model('PlaceInput', {
    'title': fields.String(
        required=True, 
        description='Title/name of the place',
        example='Cozy Apartment in Paris'
    ),
    'description': fields.String(
        description='Detailed description of the place',
        example='Beautiful 2-bedroom apartment near the Eiffel Tower'
    ),
    'price': fields.Float(
        required=True, 
        description='Price per night in the local currency',
        example=150.0
    ),
    'latitude': fields.Float(
        required=True, 
        description='Geographic latitude coordinate',
        example=48.8566
    ),
    'longitude': fields.Float(
        required=True, 
        description='Geographic longitude coordinate',
        example=2.3522
    ),
    'owner_id': fields.String(
        required=True, 
        description='UUID of the user creating the place (must match authenticated user)',
        example='abc-123-def-456'
    ),
})

# Response model for place data (includes all relationships)
place_response = places_ns.model('PlaceResponse', {
    'id': fields.String(description='Unique place identifier (UUID)'),
    'title': fields.String(description='Title/name of the place'),
    'description': fields.String(description='Detailed description'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Geographic latitude'),
    'longitude': fields.Float(description='Geographic longitude'),
    'owner': fields.Nested(user_model, description='Owner information'),
    'created_at': fields.String(description='ISO 8601 timestamp of creation'),
    'updated_at': fields.String(description='ISO 8601 timestamp of last update'),
    'amenities': fields.List(
        fields.Nested(amenity_model), 
        description='List of amenities associated with this place'
    ),
    'reviews': fields.List(
        fields.Nested(review_display_model), 
        description='List of reviews for this place'
    )
})

# Input model for updating an existing place (all fields optional)
place_update_model = places_ns.model('PlaceUpdateInput', {
    'title': fields.String(description='New title for the place'),
    'description': fields.String(description='New description'),
    'price': fields.Float(description='New price per night'),
    'latitude': fields.Float(description='New latitude coordinate'),
    'longitude': fields.Float(description='New longitude coordinate'),
})


# -----------------------
# API Routes
# -----------------------

@places_ns.route('/')
class PlaceList(Resource):
    """
    Handles operations on the collection of places.
    
    This resource manages:
    - Creating new places (POST - authenticated users only)
    - Listing all places (GET - public access)
    """
    
    @jwt_required()  # Requires valid JWT token
    @places_ns.expect(place_model, validate=True)
    @places_ns.response(201, 'Place registered successfully', place_response)
    @places_ns.response(400, 'Invalid input data')
    @places_ns.response(403, 'Unauthorized - owner_id must match authenticated user')
    def post(self):
        """
        Create a new place listing.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - The owner_id in the request must match the authenticated user's ID
        - Users can only create places for themselves (not for others)
        
        The place will be created with:
        - Empty amenities list (amenities added separately)
        - Empty reviews list (reviews added by other users)
        - Automatic timestamps (created_at, updated_at)
        
        Returns:
            201: Place created successfully with full place data
            400: Invalid input (validation errors)
            403: owner_id doesn't match authenticated user
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        try:
            # Extract place data from request body
            place_data = request.get_json()
            
            # Security check: Verify that owner_id matches the authenticated user
            # This prevents users from creating places in someone else's name
            if place_data.get('owner_id') != current_user_id:
                places_ns.abort(403, 'You can only create places for yourself')
            
            # Create the place in the database
            place = facade_instance.create_place(place_data)
            
            # SQLAlchemy automatically loads related data (owner, amenities, reviews)
            # via the configured relationships in the Place model
            return place.to_dict(), 201
            
        except ValueError as e:
            # Handle validation errors from the facade/model
            places_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            places_ns.abort(500, f"Internal error: {str(e)}")

    @places_ns.marshal_list_with(place_response)
    @places_ns.response(200, 'List of places retrieved successfully')
    def get(self):
        """
        Retrieve a list of all places.
        
        This is a public endpoint - no authentication required.
        Returns all places with their full details including:
        - Owner information
        - Associated amenities
        - User reviews
        
        SQLAlchemy eager loads all relationships automatically,
        so no additional queries are needed for nested data.
        
        Returns:
            200: List of all places with complete information
        """
        # Fetch all places from the database
        places = facade_instance.get_all_places()
        
        # Convert each place object to a dictionary for JSON serialization
        # SQLAlchemy relationships (owner, amenities, reviews) are automatically loaded
        return [p.to_dict() for p in places]


@places_ns.route('/<string:place_id>')
@places_ns.param('place_id', 'The place unique identifier (UUID)')
class PlaceResource(Resource):
    """
    Handles operations on a single place resource.
    
    This resource manages:
    - Retrieving place details (GET - public)
    - Updating place information (PUT - owner/admin only)
    - Deleting a place (DELETE - owner/admin only)
    """
    
    @places_ns.marshal_with(place_response)
    @places_ns.response(200, 'Place details retrieved successfully')
    @places_ns.response(404, 'Place not found')
    def get(self, place_id):
        """
        Get detailed information about a specific place.
        
        This is a public endpoint - no authentication required.
        Returns complete place information including:
        - Basic details (title, description, price, location)
        - Owner information
        - List of amenities
        - List of reviews
        
        Args:
            place_id (str): UUID of the place to retrieve
            
        Returns:
            200: Place details with all relationships loaded
            404: Place with the given ID does not exist
        """
        # Fetch the place from the database
        place = facade_instance.get_place(place_id)
        
        # Return 404 if place doesn't exist
        if not place:
            places_ns.abort(404, 'Place not found')

        # SQLAlchemy automatically loads owner, amenities, and reviews
        # via the configured relationships in the Place model
        return place.to_dict()

    @jwt_required()  # Requires valid JWT token
    @places_ns.expect(place_update_model, validate=True)
    @places_ns.response(200, 'Place updated successfully', place_response)
    @places_ns.response(400, 'Invalid input data')
    @places_ns.response(403, 'Unauthorized - Only owner or admin can update')
    @places_ns.response(404, 'Place not found')
    def put(self, place_id):
        """
        Update an existing place.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The owner of the place
          * An admin user
        
        Restricted fields (cannot be updated):
        - id (immutable)
        - owner_id (cannot transfer ownership)
        - created_at (immutable timestamp)
        
        Args:
            place_id (str): UUID of the place to update
            
        Returns:
            200: Place updated successfully with updated data
            400: Invalid input data
            403: User is not authorized to update this place
            404: Place not found
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the place to verify it exists and check ownership
        place = facade_instance.get_place(place_id)
        if not place:
            places_ns.abort(404, "Place not found")
        
        # Authorization check: Only owner or admin can update
        if place.owner_id != current_user_id and not is_admin:
            places_ns.abort(403, 'You can only update your own places')
        
        try:
            # Extract update data from request body
            place_data = request.get_json()
            
            # Update the place in the database
            # The facade will handle validation and prevent updating restricted fields
            updated_place = facade_instance.update_place(place_id, place_data)
            
            # SQLAlchemy automatically reloads relationships
            return updated_place.to_dict()
            
        except ValueError as e:
            # Handle validation errors from the facade/model
            places_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            places_ns.abort(500, f"Internal error: {str(e)}")

    @jwt_required()  # Requires valid JWT token
    @places_ns.response(204, 'Place successfully deleted')
    @places_ns.response(403, 'Unauthorized - Only owner or admin can delete')
    @places_ns.response(404, 'Place not found')
    def delete(self, place_id):
        """
        Delete a place.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The owner of the place
          * An admin user
        
        Cascade behavior:
        - SQLAlchemy will automatically delete all associated reviews
        - Amenities are NOT deleted (they may be shared with other places)
        - The relationship entries in place_amenity table are removed
        
        Args:
            place_id (str): UUID of the place to delete
            
        Returns:
            204: Place deleted successfully (no content)
            403: User is not authorized to delete this place
            404: Place not found
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the place to verify it exists and check ownership
        place = facade_instance.get_place(place_id)
        if not place:
            places_ns.abort(404, 'Place not found')
        
        # Authorization check: Only owner or admin can delete
        if place.owner_id != current_user_id and not is_admin:
            places_ns.abort(403, 'You can only delete your own places')
        
        # Delete the place from the database
        # SQLAlchemy cascade will handle related reviews
        facade_instance.delete_place(place_id)

        # Return 204 No Content on successful deletion
        return {"message": "Place successfully deleted"}, 204