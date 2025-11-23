#!/usr/bin/python3
"""
Amenity model for the HBnB application.

This module defines the Amenity entity using SQLAlchemy ORM.
Amenities represent features or services available at a place,
such as WiFi, Pool, Parking, Air Conditioning, etc.

Database schema:
- Primary key: id (inherited from BaseModel, UUID)
- Unique constraint: name (to avoid duplicates)
- Foreign keys: None (amenities are global resources)
- Relationships: places (Many-to-Many via place_amenity table)

Business rules:
- Amenity name is required and must be unique
- Only admins can create/update/delete amenities
- Owners select from existing amenities when creating places
"""

from app import db
from app.models.BaseModel import BaseModel
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    """
    Amenity model representing global place features/services.
    
    Inherits from BaseModel which provides:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    
    Attributes:
        name (str): Unique name of the amenity (e.g., "WiFi", "Pool", "Parking")
        
    Relationships:
        places (List[Place]): Many-to-Many relationship with places via place_amenity table
    """
    
    __tablename__ = 'amenities'
    
    # -----------------------
    # Database Columns
    # -----------------------
    
    # Amenity name - UNIQUE to avoid duplicates
    name = db.Column(
        db.String(255), 
        nullable=False,  # Required field
        unique=True,     # Only one "WiFi" amenity in the entire system
        index=True       # Index for fast lookups
    )
    
    # -----------------------
    # Relationships
    # -----------------------
    
    # Many-to-Many: Amenities can be associated with multiple places
    # secondary='place_amenity' specifies the association table
    # back_populates='amenities' links to the 'amenities' attribute in Place model
    # This is how owners select amenities for their places
    places = db.relationship(
        'Place', 
        secondary='place_amenity',      # Association table name
        back_populates='amenities',     # Corresponding attribute in Place
        lazy='subquery'                 # Eager load for performance
    )

    def __init__(self, name=None, **kwargs):
        """
        Initialize a new Amenity instance.
        
        Args:
            name (str, optional): Unique name of the amenity (e.g., "WiFi")
            **kwargs: Additional arguments passed to BaseModel (id, created_at, etc.)
            
        Raises:
            ValueError: If name validation fails (empty, too long, duplicate, etc.)
        """
        # Call parent constructor to initialize id, created_at, updated_at
        super().__init__(**kwargs)
        
        # Set amenity name if provided
        if name:
            self.name = name  # Will trigger validate_name()

    @validates('name')
    def validate_name(self, key, value):
        """
        Validate amenity name before saving to database.
        
        This validator is automatically called by SQLAlchemy whenever
        the 'name' attribute is set or modified.
        
        Validation rules:
        - Must not be None or empty string
        - Must be a string type
        - Must contain at least one non-whitespace character
        - Must be 255 characters or less
        - Must be unique (enforced by database constraint)
        
        Args:
            key (str): The attribute name being validated ('name')
            value (str): The proposed value for the name
            
        Returns:
            str: The validated and cleaned name (with whitespace stripped)
            
        Raises:
            ValueError: If validation fails
            
        Examples:
            >>> amenity.name = "WiFi"          # Valid
            >>> amenity.name = "  Pool  "      # Valid, strips to "Pool"
            >>> amenity.name = ""              # ValueError
            >>> amenity.name = None            # ValueError
            >>> amenity.name = "x" * 300       # ValueError (too long)
        """
        # Check for None, empty string, or non-string types
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("Amenity name must be a non-empty string")
        
        # Check maximum length (database constraint)
        if len(value) > 255:
            raise ValueError("Amenity name must be less than 255 characters")
        
        # Return cleaned value with leading/trailing whitespace removed
        return value.strip()

    def to_dict(self, **kwargs):
        """
        Convert the Amenity instance to a dictionary for JSON serialization.
        
        This method is used by Flask-RESTX to serialize amenity objects
        for API responses.
        
        The dictionary includes:
        - id: Unique identifier (UUID)
        - name: Amenity name
        - created_at: ISO 8601 timestamp
        - updated_at: ISO 8601 timestamp
        
        Excluded fields:
        - places: List of Place objects (to prevent circular references and huge responses)
        
        Args:
            **kwargs: Additional arguments passed to BaseModel.to_dict()
            
        Returns:
            dict: Dictionary representation of the amenity
            
        Example:
            >>> amenity = Amenity(name="WiFi")
            >>> amenity.to_dict()
            {
                'id': 'abc-123-def-456',
                'name': 'WiFi',
                'created_at': '2023-11-09T10:30:00',
                'updated_at': '2023-11-09T10:30:00'
            }
        """
        # Call parent to_dict() to get base fields (id, created_at, updated_at)
        data = super().to_dict(**kwargs)
        
        # The 'places' relationship is NOT included to avoid:
        # 1. Circular references (Place -> Amenity -> Place -> ...)
        # 2. Performance issues (loading entire object graphs)
        # 3. Huge responses (an amenity might be linked to thousands of places)
        
        return data

    def __repr__(self):
        """
        Return a string representation of the Amenity for debugging.
        
        Used in Python console, logs, and debugging tools.
        
        Returns:
            str: Human-readable representation of the amenity
            
        Example:
            >>> amenity = Amenity(name="WiFi")
            >>> print(amenity)
            <Amenity WiFi>
        """
        return f"<Amenity {self.name}>"