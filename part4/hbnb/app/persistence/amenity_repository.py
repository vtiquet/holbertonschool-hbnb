#!/usr/bin/python3
"""
Amenity-specific repository for database operations.

This module defines the AmenityRepository class which extends
SQLAlchemyRepository with amenity-specific query methods.

The repository pattern provides:
- Abstraction over database operations
- Centralized query logic
- Easier testing (can be mocked)
- Separation of concerns (business logic vs data access)

Amenity-specific queries:
- get_amenity_by_name(): Find amenity by name (not unique, returns first match)
"""

from app.models.amenity import Amenity
from app.persistence.repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):
    """
    Repository for Amenity-specific database operations.
    
    Inherits from SQLAlchemyRepository which provides:
    - get(id): Retrieve amenity by UUID
    - get_all(): Retrieve all amenities
    - add(amenity): Create new amenity
    - update(id, data): Update amenity by UUID
    - delete(id): Delete amenity by UUID
    
    Amenity-specific methods:
    - get_amenity_by_name(name): Find amenity by name
    """
    
    def __init__(self):
        """
        Initialize AmenityRepository with Amenity model.
        
        This constructor passes the Amenity model class to the parent
        SQLAlchemyRepository, which will use it for all database operations.
        """
        # Call parent constructor with Amenity model
        super().__init__(Amenity)
    
    def get_amenity_by_name(self, name):
        """
        Get an amenity by name (Amenity-specific method).
        
        This is an amenity-specific query method that searches for
        an amenity by its name. Note that amenity names are NOT unique
        in the database, so this method returns the FIRST match found.
        
        Args:
            name (str): Amenity name to search for (e.g., "WiFi", "Pool")
            
        Returns:
            Amenity: First amenity matching the name, or None if not found
            
        Usage:
            >>> repo = AmenityRepository()
            >>> wifi = repo.get_amenity_by_name("WiFi")
            >>> if wifi:
            >>>     print(f"Found amenity: {wifi.id}")
        
        Note:
            - Case-sensitive search (use .ilike() for case-insensitive)
            - Returns FIRST match only (names are not unique)
            - Returns None if no match found
        """
        return self.model.query.filter_by(name=name).first()