#!/usr/bin/python3
"""
Review model for the HBnB application.

This module defines the Review entity using SQLAlchemy ORM.
Reviews are ratings and comments that users leave about places they've visited.

Database schema:
- Primary key: id (inherited from BaseModel, UUID)
- Foreign keys: user_id (references users.id), place_id (references places.id)
- Unique constraint: (user_id, place_id) - One review per user per place
- Relationships: user (User), place (Place)

Business rules:
- Review text is required and must be non-empty
- Rating must be an integer between 1 (worst) and 5 (best)
- Each user can only leave ONE review per place (enforced by unique constraint)
- Users cannot review their own places (enforced in API layer)
"""

from app import db
from app.models.BaseModel import BaseModel
from sqlalchemy.orm import validates


class Review(BaseModel):
    """
    Review model representing user ratings and comments about places.
    
    Inherits from BaseModel which provides:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    
    Attributes:
        text (str): Review content/comments (required, no length limit)
        rating (int): Rating from 1 (worst) to 5 (best)
        user_id (str): UUID of the user who wrote the review
        place_id (str): UUID of the place being reviewed
        
    Relationships:
        user (User): The author of the review (Many-to-One)
        place (Place): The place being reviewed (Many-to-One)
        
    Database constraints:
        - UNIQUE(user_id, place_id): Prevents duplicate reviews
    """
    
    __tablename__ = 'reviews'

    # Unique constraint: One user can only review each place once
    # This is enforced at the database level for data integrity
    __table_args__ = (
        db.UniqueConstraint('user_id', 'place_id', name='unique_user_place_review'),
    )
    
    # -----------------------
    # Database Columns
    # -----------------------
    
    # Review content (required, unlimited length using TEXT type)
    text = db.Column(db.Text, nullable=False)
    
    # Rating value (1 to 5, stored as integer for simplicity)
    # 1 = worst, 5 = best
    rating = db.Column(db.Integer, nullable=False)
    
    # Foreign key to User (who wrote the review)
    # index=True for faster queries like "find all reviews by user"
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Foreign key to Place (being reviewed)
    # index=True for faster queries like "find all reviews for a place"
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False, index=True)
    
    # -----------------------
    # Relationships
    # -----------------------
    # Relationships are defined via backref in User and Place models
    # - User model has: reviews = relationship('Review', backref='user')
    # - Place model has: reviews = relationship('Review', backref='place')
    # This creates bidirectional relationships automatically

    def __init__(self, place_id=None, user_id=None, text=None, rating=None, **kwargs):
        """
        Initialize a new Review instance.
        
        Args:
            place_id (str, optional): UUID of the place being reviewed
            user_id (str, optional): UUID of the review author
            text (str, optional): Review content/comments
            rating (int, optional): Rating value (1-5)
            **kwargs: Additional arguments passed to BaseModel (id, created_at, etc.)
            
        Raises:
            ValueError: If validation fails for text or rating
            TypeError: If rating is not an integer
        """
        # Call parent constructor to initialize id, created_at, updated_at
        super().__init__(**kwargs)
        
        # Set review-specific attributes if provided
        # Each setter triggers the corresponding @validates decorator
        if text:
            self.text = text
        if rating is not None:
            self.rating = rating
        if user_id:
            self.user_id = user_id
        if place_id:
            self.place_id = place_id

    @validates('text')
    def validate_text(self, key, value):
        """
        Validate review text before saving to database.
        
        Validation rules:
        - Must not be None or empty string
        - Must be a string type
        - Must contain at least one non-whitespace character
        
        Args:
            key (str): Attribute name ('text')
            value (str): Proposed text value
            
        Returns:
            str: Validated and cleaned text (whitespace stripped)
            
        Raises:
            ValueError: If validation fails
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("text must be a non-empty string")
        return value.strip()

    @validates('rating')
    def validate_rating(self, key, value):
        """
        Validate rating value before saving to database.
        
        Validation rules:
        - Must be an integer type
        - Must be between 1 (worst) and 5 (best), inclusive
        
        Args:
            key (str): Attribute name ('rating')
            value (int): Proposed rating value
            
        Returns:
            int: Validated rating
            
        Raises:
            TypeError: If value is not an integer
            ValueError: If rating is outside 1-5 range
            
        Rating scale:
            1 = Very poor
            2 = Poor
            3 = Average
            4 = Good
            5 = Excellent
        """
        if not isinstance(value, int):
            raise TypeError("rating must be a number (integer or float)")
        if value < 1 or value > 5:
            raise ValueError("rating must be between 1 and 5")
        return value

    def to_dict(self, **kwargs):
        """
        Convert the Review instance to a dictionary for JSON serialization.
        
        This method is used by Flask-RESTX to serialize review objects
        for API responses. It includes related user and place information.
        
        The dictionary includes:
        - Basic review data (id, text, rating, timestamps)
        - User information (nested object with id, first_name, last_name)
        - Place information (nested object with id, title)
        
        Relationship loading:
        - user and place relationships are loaded via backref
        - SQLAlchemy automatically loads these relationships when accessed
        
        Args:
            **kwargs: Additional arguments passed to BaseModel.to_dict()
            
        Returns:
            dict: Complete review data with user and place nested objects
            
        Example output:
            {
                'id': 'rev-123',
                'text': 'Great place, highly recommended!',
                'rating': 5,
                'created_at': '2023-11-09T10:30:00',
                'updated_at': '2023-11-09T10:30:00',
                'user': {
                    'id': 'user-456',
                    'first_name': 'John',
                    'last_name': 'Doe'
                },
                'place': {
                    'id': 'place-789',
                    'title': 'Cozy Apartment'
                }
            }
        """
        # Get base dictionary from BaseModel (id, created_at, updated_at, etc.)
        review_dict = super().to_dict(**kwargs)

        # ----- USER ----- (SQLAlchemy relationship loaded via backref)
        if hasattr(self, 'user') and self.user:
            # User relationship is loaded, create nested dictionary
            review_dict['user'] = {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            }
        else:
            # Fallback if user relationship is not loaded
            review_dict['user'] = {
                'id': review_dict.get('user_id'),
                'first_name': None,
                'last_name': None
            }
        # Remove raw user_id from output (replaced by user object)
        review_dict.pop('user_id', None)

        # ----- PLACE ----- (SQLAlchemy relationship loaded via backref)
        if hasattr(self, 'place') and self.place:
            # Place relationship is loaded, create nested dictionary
            review_dict['place'] = {
                'id': self.place.id,
                'title': self.place.title
            }
        else:
            # Fallback if place relationship is not loaded
            review_dict['place'] = {
                'id': review_dict.get('place_id'),
                'title': None
            }
        # Remove raw place_id from output (replaced by place object)
        review_dict.pop('place_id', None)

        return review_dict

    def __repr__(self):
        """
        Return a string representation of the Review for debugging.
        
        Returns:
            str: Human-readable representation
                 Format: <Review {id} by User {user_id}>
                 Example: <Review abc-123-def by User xyz-456-uvw>
        """
        return f"<Review {self.id} by User {self.user_id}>"