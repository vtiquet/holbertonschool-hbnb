#!/usr/bin/python3
"""
Place-specific repository for database operations.

This module defines the PlaceRepository class which extends
SQLAlchemyRepository with place-specific query methods.

The repository pattern provides:
- Abstraction over database operations
- Centralized query logic
- Easier testing (can be mocked)
- Separation of concerns (business logic vs data access)

Place-specific queries:
- get_places_by_owner(): Find all places owned by a specific user
"""

from app.models.place import Place
from app.persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    """
    Repository for Place-specific database operations.
    
    Inherits from SQLAlchemyRepository which provides:
    - get(id): Retrieve place by UUID
    - get_all(): Retrieve all places
    - add(place): Create new place
    - update(id, data): Update place by UUID
    - delete(id): Delete place by UUID
    
    Place-specific methods:
    - get_places_by_owner(owner_id): Find all places owned by a user
    """
    
    def __init__(self):
        """
        Initialize PlaceRepository with Place model.
        
        This constructor passes the Place model class to the parent
        SQLAlchemyRepository, which will use it for all database operations.
        """
        # Call parent constructor with Place model
        super().__init__(Place)
    
    def get_places_by_owner(self, owner_id):
        """
        Get all places owned by a specific user (Place-specific method).
        
        This method is useful for:
        - Displaying a user's profile page (their listings)
        - Admin dashboard (view places by user)
        - User deletion validation (check if user has places)
        
        Args:
            owner_id (str): UUID of the user who owns the places
            
        Returns:
            list: List of Place objects owned by the user
                  Returns empty list [] if user has no places
            
        Usage:
            >>> repo = PlaceRepository()
            >>> user_places = repo.get_places_by_owner("user-123-abc")
            >>> print(f"User has {len(user_places)} places")
        
        Performance:
            - Uses indexed foreign key (owner_id) for fast lookups
            - Returns all places in a single query
        
        Note:
            - Results are NOT ordered (add .order_by() if needed)
            - Includes places even if they have no reviews/amenities
        """
        return self.model.query.filter_by(owner_id=owner_id).all()