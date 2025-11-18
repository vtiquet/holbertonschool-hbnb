#!/usr/bin/python3
"""
Review-specific repository for database operations.
Extends SQLAlchemyRepository with review-specific queries:
- get_reviews_by_place(): Find all reviews for a place
- get_reviews_by_user(): Find all reviews by a user
"""

from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository):
    """
    Repository for Review-specific database operations.
    Inherits: get(id), get_all(), add(), update(id, data), delete(id)
    Review-specific: get_reviews_by_place(), get_reviews_by_user()
    """
    
    def __init__(self):
        """Initialize ReviewRepository with Review model"""
        super().__init__(Review)
    
    def get_reviews_by_place(self, place_id):
        """
        Get all reviews for a specific place.
        Args: place_id (str): UUID of the place
        Returns: list: Review objects (empty list if none)
        Use cases: Place details page, calculate average rating
        """
        return self.model.query.filter_by(place_id=place_id).all()
    
    def get_reviews_by_user(self, user_id):
        """
        Get all reviews written by a specific user.
        Args: user_id (str): UUID of the user
        Returns: list: Review objects (empty list if none)
        Use cases: User profile, review history
        """
        return self.model.query.filter_by(user_id=user_id).all()