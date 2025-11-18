#!/usr/bin/python3
"""
Place model for the HBnB application.

This module defines the Place entity using SQLAlchemy ORM.
Places represent rental properties/accommodations (apartments, houses, villas)
that users can list and other users can review.

Database schema:
- Primary key: id (inherited from BaseModel, UUID)
- Foreign keys: owner_id (references users.id)
- Relationships: owner (User), reviews (Review), amenities (Amenity, Many-to-Many)

Business rules:
- Title is required and must be non-empty
- Price must be non-negative (stored as Decimal for precision)
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- Each place must have an owner (user who created it)
- Deleting a place cascades to delete all its reviews
"""

from app import db
from app.models.BaseModel import BaseModel
from sqlalchemy.orm import validates
from decimal import Decimal


# Many-to-Many association table between Place and Amenity
# This table has no model class, it's just a link table
# CASCADE: When a place or amenity is deleted, the association is removed
place_amenity = db.Table('place_amenity',
    db.Column('place_id', db.String(36), db.ForeignKey('places.id', ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id', ondelete='CASCADE'), primary_key=True)
)


class Place(BaseModel):
    """
    Place model representing rental properties/accommodations.
    
    Inherits from BaseModel which provides:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    
    Attributes:
        title (str): Name/title of the place (max 255 characters)
        description (str): Detailed description of the place (optional, no length limit)
        price (Decimal): Price per night (stored with 2 decimal precision)
        latitude (float): Geographic latitude coordinate (-90 to 90)
        longitude (float): Geographic longitude coordinate (-180 to 180)
        owner_id (str): UUID of the user who owns/created this place
        
    Relationships:
        owner (User): The user who created this place (Many-to-One)
        reviews (List[Review]): Reviews written about this place (One-to-Many, cascade delete)
        amenities (List[Amenity]): Features/services available (Many-to-Many)
    """
    
    __tablename__ = 'places'
    
    # -----------------------
    # Database Columns
    # -----------------------
    
    # Place title/name (required, max 255 characters)
    title = db.Column(db.String(255), nullable=False)
    
    # Detailed description (optional, unlimited length using TEXT type)
    description = db.Column(db.Text, nullable=True)
    
    # Price per night (Numeric(10,2) = max 99999999.99)
    # Uses Decimal type for financial precision (avoids float rounding errors)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Geographic coordinates for map display
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Foreign key to User (who owns this place)
    # index=True for faster queries like "find all places by owner"
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # -----------------------
    # Relationships
    # -----------------------
    
    # Many-to-One: Many places belong to one user
    # back_populates='places' creates bidirectional relationship with User.places
    owner = db.relationship('User', back_populates='places')
    
    # One-to-Many: One place has many reviews
    # cascade='all, delete-orphan' deletes all reviews when place is deleted
    # lazy=True loads reviews only when accessed (on-demand loading)
    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    
    # Many-to-Many: Place has many amenities, Amenity has many places
    # secondary='place_amenity' specifies the association table
    # lazy='subquery' loads amenities in a single query for better performance
    amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery', back_populates='places')

    def __init__(self, title=None, description=None, price=None, latitude=None, 
                 longitude=None, owner_id=None, amenities=None, **kwargs):
        """
        Initialize a new Place instance.
        
        Args:
            title (str, optional): Name of the place
            description (str, optional): Detailed description
            price (float/Decimal, optional): Price per night
            latitude (float, optional): Geographic latitude
            longitude (float, optional): Geographic longitude
            owner_id (str, optional): UUID of the owner
            amenities (list, optional): List of Amenity objects to associate
            **kwargs: Additional arguments passed to BaseModel (id, created_at, etc.)
            
        Raises:
            ValueError: If validation fails for any field
        """
        # Call parent constructor to initialize id, created_at, updated_at
        super().__init__(**kwargs)
        
        # Set place-specific attributes if provided
        # Each setter triggers the corresponding @validates decorator
        if title:
            self.title = title
        if description:
            self.description = description
        if price is not None:
            self.price = price
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if owner_id:
            self.owner_id = owner_id
        if amenities:
            self.amenities = amenities if isinstance(amenities, list) else []

    @validates('title')
    def validate_title(self, key, value):
        """
        Validate place title before saving to database.
        
        Validation rules:
        - Must not be None or empty string
        - Must be a string type
        - Must contain at least one non-whitespace character
        - Must be 255 characters or less
        
        Args:
            key (str): Attribute name ('title')
            value (str): Proposed title value
            
        Returns:
            str: Validated and cleaned title (whitespace stripped)
            
        Raises:
            ValueError: If validation fails
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("title must be a non-empty string")
        if len(value) > 255:
            raise ValueError("title must be less than 255 characters")
        return value.strip()

    @validates('price')
    def validate_price(self, key, value):
        """
        Validate place price before saving to database.
        
        Validation rules:
        - Must not be None
        - Must be convertible to Decimal (numeric type)
        - Must be non-negative (>= 0)
        
        Args:
            key (str): Attribute name ('price')
            value (float/int/str): Proposed price value
            
        Returns:
            Decimal: Validated price as Decimal for precision
            
        Raises:
            ValueError: If price is None or negative
            TypeError: If price is not numeric
            
        Note:
            Using Decimal instead of float prevents rounding errors
            in financial calculations (e.g., 0.1 + 0.2 = 0.3 exactly)
        """
        if value is None:
            raise ValueError("Price is required")
        
        # Convert to Decimal for precision (handles float, int, str inputs)
        try:
            decimal_value = Decimal(str(value))
        except:
            raise TypeError("Price must be a number")
        
        if decimal_value < 0:
            raise ValueError("Price must be non-negative")
        
        return decimal_value

    @validates('latitude')
    def validate_latitude(self, key, value):
        """
        Validate geographic latitude before saving to database.
        
        Validation rules:
        - Must not be None
        - Must be numeric (int or float)
        - Must be between -90 and 90 (valid latitude range)
        
        Args:
            key (str): Attribute name ('latitude')
            value (float/int): Proposed latitude value
            
        Returns:
            float: Validated latitude
            
        Raises:
            TypeError: If value is not numeric
            ValueError: If latitude is out of valid range
            
        Geographic context:
            -90 = South Pole
            0 = Equator
            +90 = North Pole
        """
        if value is None or not isinstance(value, (int, float)):
            raise TypeError("Latitude must be a number")
        if value < -90 or value > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return float(value)

    @validates('longitude')
    def validate_longitude(self, key, value):
        """
        Validate geographic longitude before saving to database.
        
        Validation rules:
        - Must not be None
        - Must be numeric (int or float)
        - Must be between -180 and 180 (valid longitude range)
        
        Args:
            key (str): Attribute name ('longitude')
            value (float/int): Proposed longitude value
            
        Returns:
            float: Validated longitude
            
        Raises:
            TypeError: If value is not numeric
            ValueError: If longitude is out of valid range
            
        Geographic context:
            -180/+180 = International Date Line (Pacific Ocean)
            0 = Prime Meridian (Greenwich, UK)
        """
        if value is None or not isinstance(value, (int, float)):
            raise TypeError("Longitude must be a number")
        if value < -180 or value > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return float(value)

    def add_amenity(self, amenity):
        """
        Associate an amenity with this place (SQLAlchemy way).
        
        This method adds an amenity to the place's amenities list
        if it's not already present. SQLAlchemy will automatically
        create an entry in the place_amenity association table.
        
        Args:
            amenity (Amenity): The Amenity object to associate
            
        Usage:
            >>> place = Place.query.get(place_id)
            >>> wifi = Amenity.query.filter_by(name="WiFi").first()
            >>> place.add_amenity(wifi)
            >>> db.session.commit()
        
        Note:
            Duplicate prevention: Only adds if amenity not already associated
        """
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def to_dict(self, **kwargs):
        """
        Convert the Place instance to a dictionary for JSON serialization.
        
        This method is used by Flask-RESTX to serialize place objects
        for API responses. It includes all related data (owner, amenities, reviews).
        
        The dictionary includes:
        - Basic place data (id, title, description, price, coordinates, timestamps)
        - Owner information (nested object with id, name, email)
        - List of amenities (id and name only)
        - List of reviews (id, text, rating, user_id)
        
        Relationship loading:
        - All relationships are automatically loaded by SQLAlchemy
        - lazy='subquery' ensures amenities are loaded in one query
        - reviews are loaded via lazy=True (on-demand)
        
        Args:
            **kwargs: Additional arguments passed to BaseModel.to_dict()
            
        Returns:
            dict: Complete place data with all relationships
            
        Example output:
            {
                'id': 'abc-123',
                'title': 'Cozy Apartment',
                'price': 150.0,
                'latitude': 48.8566,
                'longitude': 2.3522,
                'owner': {
                    'id': 'user-123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com'
                },
                'amenities': [
                    {'id': 'am-1', 'name': 'WiFi'},
                    {'id': 'am-2', 'name': 'Pool'}
                ],
                'reviews': [
                    {'id': 'rev-1', 'text': 'Great!', 'rating': 5.0, 'user_id': 'u-2'}
                ]
            }
        """
        # Get base dictionary from BaseModel (id, created_at, updated_at, etc.)
        place_dict = super().to_dict(**kwargs)
        
        # Convert Decimal price to float for JSON compatibility
        # JSON doesn't support Decimal type, only float
        if 'price' in place_dict and isinstance(place_dict['price'], Decimal):
            place_dict['price'] = float(place_dict['price'])

        # ----- OWNER ----- (SQLAlchemy relationship loaded automatically)
        if hasattr(self, 'owner') and self.owner:
            # Owner is loaded, create nested dictionary
            place_dict['owner'] = {
                'id': self.owner.id,
                'first_name': self.owner.first_name,
                'last_name': self.owner.last_name,
                'email': self.owner.email
            }
        else:
            # Fallback if owner relationship is not loaded (shouldn't happen with eager loading)
            place_dict['owner'] = {
                'id': place_dict.get('owner_id'),
                'first_name': None,
                'last_name': None,
                'email': None
            }
        # Remove raw owner_id from output (replaced by owner object)
        place_dict.pop('owner_id', None)

        # ----- AMENITIES ----- (SQLAlchemy relationship loaded via lazy='subquery')
        place_dict['amenities'] = []
        if hasattr(self, 'amenities') and self.amenities:
            # Iterate through loaded amenities and create minimal dictionaries
            for amenity in self.amenities:
                place_dict['amenities'].append({
                    'id': amenity.id,
                    'name': amenity.name
                })

        # ----- REVIEWS ----- (SQLAlchemy relationship loaded via lazy=True)
        place_dict['reviews'] = []
        if hasattr(self, 'reviews') and self.reviews:
            # Iterate through loaded reviews and create minimal dictionaries
            for review in self.reviews:
                place_dict['reviews'].append({
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user_id
                })

        return place_dict

    def __repr__(self):
        """
        Return a string representation of the Place for debugging.
        
        Returns:
            str: Human-readable representation
                 Format: <Place title>
                 Example: <Place Cozy Apartment in Paris>
        """
        return f"<Place {self.title}>"