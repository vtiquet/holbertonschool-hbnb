#!/usr/bin/python3
"""
Amenity model for the HBnB application.

This module defines the Amenity entity using SQLAlchemy ORM.
Amenities represent features or services available at a place,
such as WiFi, Pool, Parking, Air Conditioning, etc.

Database schema:
- Primary key: id (inherited from BaseModel, UUID)
- Unique constraint: None (multiple places can have the same amenity name)
- Foreign keys: place_id, owner_id
- Relationships: owner (User), place (Place), places (Many-to-Many)

Business rules:
- Amenity name is required and must be non-empty
- Name can be duplicated (e.g., multiple "WiFi" amenities for different places)
- Optional ownership tracking (owner_id can be null)
"""

from app import db
from app.models.BaseModel import BaseModel
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    """
    Amenity model representing place features/services.
    
    Inherits from BaseModel which provides:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    
    Attributes:
        name (str): Name of the amenity (e.g., "WiFi", "Pool", "Parking")
        place_id (str): Optional UUID of the associated place (legacy field)
        owner_id (str): Optional UUID of the user who created this amenity
        
    Relationships:
        owner (User): The user who created this amenity (optional)
        place (Place): Direct relationship to a single place (legacy, rarely used)
        places (List[Place]): Many-to-Many relationship with places via place_amenity table
    """
    
    __tablename__ = 'amenities'
    
    # -----------------------
    # Database Columns
    # -----------------------
    
    # Amenity name (not unique - multiple places can have "WiFi")
    name = db.Column(
        db.String(255), 
        nullable=False,  # Required field
        unique=False,    # Allows duplicates (e.g., multiple "WiFi" amenities)
    )
    
    # Optional foreign key to a specific place (legacy field, rarely used)
    place_id = db.Column(
        db.String(36),                     # UUID format
        db.ForeignKey('places.id'),        # References places table
        nullable=True,                     # Optional relationship
        index=True                         # Index for joins
    )
    
    # Optional foreign key to track who created the amenity
    owner_id = db.Column(
        db.String(36),                     # UUID format
        db.ForeignKey('users.id'),         # References users table
        nullable=True,                     # Optional relationship
        index=True                         # Index for joins
    )
    
    # -----------------------
    # Relationships
    # -----------------------
    
    # One-to-Many: User can own multiple amenities
    # backref creates 'owned_amenities' attribute on User model
    # lazy='subquery' loads owner data in a single query for better performance
    owner = db.relationship(
        'User', 
        backref='owned_amenities', 
        lazy='subquery'
    )
    
    # One-to-Many: Direct relationship to a single place (legacy, rarely used)
    # foreign_keys specifies which FK to use (since we have multiple relationships with Place)
    # backref creates 'direct_amenities' attribute on Place model
    place = db.relationship(
        'Place', 
        foreign_keys=[place_id], 
        backref='direct_amenities', 
        lazy='subquery'
    )

    # Many-to-Many: Amenities can be associated with multiple places
    # secondary='place_amenity' specifies the association table
    # back_populates='amenities' links to the 'amenities' attribute in Place model
    # This is the PRIMARY way amenities are linked to places
    places = db.relationship(
        'Place', 
        secondary='place_amenity',      # Association table name
        back_populates='amenities',     # Corresponding attribute in Place
        lazy='subquery'                 # Eager load for performance
    )

    def __init__(self, name=None, place_id=None, owner_id=None, **kwargs):
        """
        Initialize a new Amenity instance.
        
        Args:
            name (str, optional): Name of the amenity (e.g., "WiFi")
            place_id (str, optional): UUID of the associated place (legacy)
            owner_id (str, optional): UUID of the user creating the amenity
            **kwargs: Additional arguments passed to BaseModel (id, created_at, etc.)
            
        Raises:
            ValueError: If name validation fails (empty, too long, etc.)
        """
        # Call parent constructor to initialize id, created_at, updated_at
        super().__init__(**kwargs)
        
        # Set amenity-specific attributes if provided
        if name:
            self.name = name  # Will trigger validate_name()
        if place_id:
            self.place_id = place_id
        if owner_id:
            self.owner_id = owner_id

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
        for API responses. It excludes sensitive/internal fields.
        
        The dictionary includes:
        - id: Unique identifier (UUID)
        - name: Amenity name
        - created_at: ISO 8601 timestamp
        - updated_at: ISO 8601 timestamp
        - place_id: Associated place UUID (if set)
        - owner_id: Creator's UUID (if set)
        
        Excluded fields:
        - owner: Full User object (to prevent circular references)
        - place: Full Place object (to prevent circular references)
        - places: List of Place objects (to prevent circular references)
        
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
                'updated_at': '2023-11-09T10:30:00',
                'place_id': None,
                'owner_id': None
            }
        """
        # Call parent to_dict() to get base fields (id, created_at, updated_at)
        data = super().to_dict(**kwargs)
        
        # Relationships are NOT included in to_dict() to avoid:
        # 1. Circular references (Place -> Amenity -> Place -> ...)
        # 2. Performance issues (loading entire object graphs)
        # 3. Exposing unnecessary data in API responses
        #
        # If you need relationship data, access it directly:
        # amenity.owner.to_dict() or amenity.places[0].to_dict()
        
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