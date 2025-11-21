#!/usr/bin/python3
"""
Review API endpoints for the HBnB application.

This module provides RESTful API endpoints for managing reviews.
Reviews are ratings and comments that users can leave about places they've visited.

Routes:
    POST   /reviews/                      - Create a new review (authenticated users)
    GET    /reviews/                      - List all reviews (public)
    GET    /reviews/<id>                  - Get review details (public)
    PUT    /reviews/<id>                  - Update a review (author/admin only)
    DELETE /reviews/<id>                  - Delete a review (author/admin only)
    GET    /reviews/places/<place_id>/reviews - Get all reviews for a place (public)

Business rules:
- Users can only review places they don't own
- Users can only leave one review per place
- Only the review author or admin can update/delete reviews
- Rating must be between 1.0 (worst) and 5.0 (best)
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from app import facade as facade_instance
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import HTTPException


# Create a namespace for review-related operations
reviews_ns = Namespace('reviews', description='Review operations')


# -----------------------
# Swagger API Models
# -----------------------

# Nested model for place display in review responses
review_place_nested_model = reviews_ns.model('ReviewPlaceNested', {
    'id': fields.String(description='Unique place identifier (UUID)'),
    'title': fields.String(description='Title of the place being reviewed'),
})

# Nested model for user display in review responses
review_user_nested_model = reviews_ns.model('ReviewUserNested', {
    'id': fields.String(description='Unique user identifier (UUID)'),
    'first_name': fields.String(description='First name of the review author'),
    'last_name': fields.String(description='Last name of the review author'),
})

# Input model for creating a new review
review_model = reviews_ns.model('ReviewInput', {
    'text': fields.String(
        required=True, 
        description='Review content/comments',
        example='Great place! Very clean and comfortable.'
    ),
    'rating': fields.Float(
        required=True, 
        description='Rating from 1.0 (worst) to 5.0 (best)',
        example=4.5
    ),
    'user_id': fields.String(
        required=True, 
        description='UUID of the user writing the review (must match authenticated user)',
        example='abc-123-def-456'
    ),
    'place_id': fields.String(
        required=True, 
        description='UUID of the place being reviewed',
        example='xyz-789-uvw-012'
    )
})

# Modèle pour la création via /places/<place_id>/reviews
review_create_model = reviews_ns.model('ReviewCreate', {
    'text': fields.String(required=True, min_length=10, description='Review comment (min 10 characters)'),
    'rating': fields.Integer(required=True, min=1, max=5, description='Rating (1-5 stars)')
})

# Response model for review data
review_response_model = reviews_ns.model('ReviewResponse', {
    'id': fields.String(description='Unique review identifier (UUID)'),
    'text': fields.String(description='Review content/comments'),
    'rating': fields.Float(description='Rating from 1.0 to 5.0'),
    'user': fields.Nested(review_user_nested_model, description='Author of the review'),
    'place': fields.Nested(review_place_nested_model, description='Place being reviewed'),
    'created_at': fields.String(description='ISO 8601 timestamp of creation'),
    'updated_at': fields.String(description='ISO 8601 timestamp of last update'),
})

# Input model for updating an existing review
review_update_model = reviews_ns.model('ReviewUpdate', {
    'text': fields.String(description='New review content'),
    'rating': fields.Float(description='New rating (1.0-5.0)')
})


# -----------------------
# API Routes
# -----------------------

@reviews_ns.route('/')
class ReviewList(Resource):
    """
    Handles operations on the collection of reviews.
    
    This resource manages:
    - Creating new reviews (POST - authenticated users)
    - Listing all reviews (GET - public access)
    """
    
    @jwt_required()  # Requires valid JWT token
    @reviews_ns.expect(review_model, validate=True)
    @reviews_ns.response(201, 'Review successfully created', review_response_model)
    @reviews_ns.response(400, 'Invalid input data')
    @reviews_ns.response(403, 'Unauthorized - Cannot review own place or user_id mismatch')
    @reviews_ns.response(404, 'Place not found')
    @reviews_ns.response(409, 'Conflict - User has already reviewed this place')
    def post(self):
        """
        Create a new review for a place.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - user_id must match the authenticated user
        - User cannot review their own place
        - User can only leave one review per place
        
        Database constraint:
        - The combination of (user_id, place_id) is unique in the database
        - This prevents duplicate reviews at the database level
        
        Returns:
            201: Review created successfully
            400: Invalid input (validation errors)
            403: Forbidden (trying to review own place or user_id mismatch)
            404: Place does not exist
            409: User has already reviewed this place
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        try:
            # Extract review data from request body
            review_data = reviews_ns.payload
            
            # Security check: Verify user_id matches authenticated user
            # This prevents users from creating reviews in someone else's name
            if review_data.get('user_id') != current_user_id:
                reviews_ns.abort(403, 'You can only create reviews for yourself')
            
            place_id = review_data.get('place_id')
            
            # Verify the place exists and get its details
            place = facade_instance.get_place(place_id)
            if not place:
                reviews_ns.abort(404, 'Place not found')
            
            # Business rule: Users cannot review their own places
            # This prevents fake reviews and maintains review integrity
            if place.owner_id == current_user_id:
                reviews_ns.abort(403, 'You cannot review your own place')
            
            # Business rule: One review per user per place
            # Check if user has already reviewed this place
            if facade_instance.user_has_reviewed_place(current_user_id, place_id):
                reviews_ns.abort(409, 'You have already reviewed this place')
            
            # Create the review in the database
            review = facade_instance.create_review(review_data)
            
            # SQLAlchemy automatically loads related user and place data
            # via the configured relationships in the Review model
            return review.to_dict(), 201
        
        except HTTPException:
            # Re-raise HTTP exceptions (403, 404, 409, etc.)
            # These are expected errors that should be returned to the client
            raise
        except ValueError as e:
            # Handle validation errors (e.g., rating out of range)
            reviews_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            import traceback
            print("=" * 80)
            print("ERROR in POST /reviews:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            print("=" * 80)
            reviews_ns.abort(500, f"Internal error: {str(e)}")

    @reviews_ns.marshal_list_with(review_response_model)
    @reviews_ns.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """
        Retrieve a list of all reviews in the system.
        
        This is a public endpoint - no authentication required.
        Returns all reviews with their associated user and place information.
        
        SQLAlchemy automatically loads relationships (user, place) for each review,
        so no additional queries are needed.
        
        Returns:
            200: List of all reviews with complete information
        """
        # Fetch all reviews from the database
        reviews = facade_instance.get_all_reviews()
        
        # Convert each review object to a dictionary for JSON serialization
        # SQLAlchemy relationships (user, place) are automatically loaded
        return [r.to_dict() for r in reviews]


@reviews_ns.route('/<string:review_id>')
@reviews_ns.param('review_id', 'The review unique identifier (UUID)')
class ReviewResource(Resource):
    """
    Handles operations on a single review resource.
    
    This resource manages:
    - Retrieving review details (GET - public)
    - Updating review content (PUT - author/admin only)
    - Deleting a review (DELETE - author/admin only)
    """
    
    @reviews_ns.marshal_with(review_response_model)
    @reviews_ns.response(200, 'Review details retrieved successfully')
    @reviews_ns.response(404, 'Review not found')
    def get(self, review_id):
        """
        Get detailed information about a specific review.
        
        This is a public endpoint - no authentication required.
        Returns complete review information including:
        - Review text and rating
        - Author information (user)
        - Place information
        
        Args:
            review_id (str): UUID of the review to retrieve
            
        Returns:
            200: Review details with all relationships loaded
            404: Review with the given ID does not exist
        """
        # Fetch the review from the database
        review = facade_instance.get_review(review_id)
        
        # Return 404 if review doesn't exist
        if not review:
            reviews_ns.abort(404, 'Review not found')
        
        # SQLAlchemy automatically loads user and place relationships
        return review.to_dict()

    @jwt_required()  # Requires valid JWT token
    @reviews_ns.expect(review_update_model, validate=True)
    @reviews_ns.response(200, 'Review updated successfully', review_response_model)
    @reviews_ns.response(400, 'Invalid input data')
    @reviews_ns.response(403, 'Unauthorized - Only author or admin can update')
    @reviews_ns.response(404, 'Review not found')
    def put(self, review_id):
        """
        Update an existing review.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The author of the review
          * An admin user
        
        Updatable fields:
        - text (review content)
        - rating (1.0-5.0)
        
        Restricted fields (cannot be updated):
        - id (immutable)
        - user_id (cannot change authorship)
        - place_id (cannot move review to another place)
        - created_at (immutable timestamp)
        
        Args:
            review_id (str): UUID of the review to update
            
        Returns:
            200: Review updated successfully
            400: Invalid input data
            403: User is not authorized to update this review
            404: Review not found
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the review to verify it exists and check authorship
        review = facade_instance.get_review(review_id)
        if not review:
            reviews_ns.abort(404, 'Review not found')
        
        # Authorization check: Only the review author or admin can update
        if review.user_id != current_user_id and not is_admin:
            reviews_ns.abort(403, 'You can only update your own reviews')
        
        try:
            # Update the review in the database
            # The facade will handle validation and prevent updating restricted fields
            updated_review = facade_instance.update_review(review_id, reviews_ns.payload)
            if not updated_review:
                reviews_ns.abort(404, 'Review not found')

            # SQLAlchemy automatically reloads relationships
            return updated_review.to_dict()
        
        except HTTPException:
            # Re-raise HTTP exceptions (403, 404, etc.)
            raise
        except ValueError as e:
            # Handle validation errors (e.g., invalid rating)
            reviews_ns.abort(400, str(e))
        except Exception as e:
            # Handle unexpected errors
            import traceback
            print("=" * 80)
            print("ERROR in PUT /reviews:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            print("=" * 80)
            reviews_ns.abort(500, f"Internal error: {str(e)}")

    @jwt_required()  # Requires valid JWT token
    @reviews_ns.response(204, 'Review deleted successfully')
    @reviews_ns.response(403, 'Unauthorized - Only author or admin can delete')
    @reviews_ns.response(404, 'Review not found')
    def delete(self, review_id):
        """
        Delete a review.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User must be either:
          * The author of the review
          * An admin user
        
        Args:
            review_id (str): UUID of the review to delete
            
        Returns:
            204: Review deleted successfully (no content)
            403: User is not authorized to delete this review
            404: Review not found
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get additional claims from the JWT (e.g., admin status)
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        # Fetch the review to verify it exists and check authorship
        review = facade_instance.get_review(review_id)
        if not review:
            reviews_ns.abort(404, 'Review not found')
        
        # Authorization check: Only the review author or admin can delete
        if review.user_id != current_user_id and not is_admin:
            reviews_ns.abort(403, 'You can only delete your own reviews')
        
        # Delete the review from the database
        if facade_instance.delete_review(review_id):
            # Return 204 No Content on successful deletion
            return {}, 204
        
        # This shouldn't happen (we already checked), but handle it just in case
        reviews_ns.abort(404, 'Review not found')


@reviews_ns.route('/places/<string:place_id>/reviews')
@reviews_ns.param('place_id', 'The place unique identifier (UUID)')
class PlaceReviewList(Resource):
    """
    Handles retrieval of all reviews for a specific place.
    
    This is a convenience endpoint that filters reviews by place_id.
    Useful for displaying all reviews on a place's detail page.
    """
    
    @reviews_ns.marshal_list_with(review_response_model)
    @reviews_ns.response(200, 'List of reviews for the place retrieved successfully')
    @reviews_ns.response(404, 'Place not found')
    def get(self, place_id):
        """
        Get all reviews for a specific place.
        
        This is a public endpoint - no authentication required.
        Returns all reviews associated with the given place, including:
        - Review text and rating
        - Author information
        - Place information
        
        This endpoint is useful for:
        - Displaying reviews on a place's detail page
        - Calculating average ratings for a place
        - Showing review history
        
        Args:
            place_id (str): UUID of the place to get reviews for
            
        Returns:
            200: List of reviews for the place
            404: Place with the given ID does not exist
        """
        # Fetch all reviews for the specified place
        # The facade will return None if the place doesn't exist
        reviews_data = facade_instance.get_reviews_by_place(place_id)

        # Return 404 if place doesn't exist
        if reviews_data is None:
            reviews_ns.abort(404, 'Place not found')

        # Ensure we always return a list (even if there's only one review)
        # The facade might return a single object in some cases
        reviews = reviews_data if isinstance(reviews_data, list) else [reviews_data]

        # SQLAlchemy automatically loads user and place for each review
        return [r.to_dict() for r in reviews]
    
    @jwt_required()
    @reviews_ns.expect(review_create_model, validate=True)
    @reviews_ns.response(201, 'Review successfully created', review_response_model)
    @reviews_ns.response(400, 'Invalid input data')
    @reviews_ns.response(403, 'Unauthorized - Cannot review own place')
    @reviews_ns.response(404, 'Place not found')
    @reviews_ns.response(409, 'Conflict - User has already reviewed this place')
    def post(self, place_id):
        """
        Create a new review for a specific place.
        
        This endpoint creates a review directly under the place resource.
        The place_id is taken from the URL instead of the request body.
        
        Protection rules:
        - User must be authenticated (JWT token required)
        - User cannot review their own place
        - User can only leave one review per place
        
        Args:
            place_id (str): UUID of the place to review (from URL)
            
        Returns:
            201: Review created successfully
            400: Invalid input (validation errors)
            403: Forbidden (trying to review own place)
            404: Place does not exist
            409: User has already reviewed this place
        """
        # Get the authenticated user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        try:
            # Extract review data from request body
            review_data = reviews_ns.payload
            
            # Override place_id with the one from the URL
            review_data['place_id'] = place_id
            
            # Set user_id to the authenticated user
            review_data['user_id'] = current_user_id
            
            # Verify the place exists and get its details
            place = facade_instance.get_place(place_id)
            if not place:
                reviews_ns.abort(404, 'Place not found')
            
            # Business rule: Users cannot review their own places
            if place.owner_id == current_user_id:
                reviews_ns.abort(403, 'You cannot review your own place')
            
            # Business rule: One review per user per place
            if facade_instance.user_has_reviewed_place(current_user_id, place_id):
                reviews_ns.abort(409, 'You have already reviewed this place')
            
            # Create the review in the database
            review = facade_instance.create_review(review_data)
            
            return review.to_dict(), 201
        
        except HTTPException:
            raise
        except ValueError as e:
            reviews_ns.abort(400, str(e))
        except Exception as e:
            import traceback
            print("=" * 80)
            print("ERROR in POST /places/<place_id>/reviews:")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            print("=" * 80)
            reviews_ns.abort(500, f"Internal error: {str(e)}")
