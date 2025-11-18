#!/usr/bin/python3
"""
User model for the HBnB application.

This module defines the User entity using SQLAlchemy ORM.
Users are the primary actors in the system who can:
- Create and manage places (listings)
- Write reviews for places
- Have admin privileges (optional)

Database schema:
- Primary key: id (inherited from BaseModel, UUID)
- Unique constraint: email (must be unique across all users)
- Relationships: places (Place), reviews (Review), owned_amenities (Amenity)

Security:
- Passwords are hashed using bcrypt before storage
- Passwords are never exposed in API responses (excluded from to_dict())
- Minimum password length: 6 characters

Business rules:
- Email must be valid and unique
- First name and last name are required
- Default role is regular user (is_admin=False)
- Deleting a user cascades to delete all their places and reviews
"""

from app import db, bcrypt
from app.models.BaseModel import BaseModel
from sqlalchemy.orm import validates
from email_validator import validate_email, EmailNotValidError


class User(BaseModel):
    """
    User model representing application users (owners and reviewers).
    
    Inherits from BaseModel which provides:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    
    Attributes:
        first_name (str): User's first name (max 255 characters)
        last_name (str): User's last name (max 255 characters)
        email (str): User's email address (unique, max 255 characters)
        password (str): Bcrypt hashed password (60 characters)
        is_admin (bool): Administrative privileges flag (default: False)
        
    Relationships:
        places (List[Place]): Places owned by this user (One-to-Many, cascade delete)
        reviews (List[Review]): Reviews written by this user (One-to-Many, cascade delete)
        owned_amenities (List[Amenity]): Amenities created by this user (One-to-Many)
    """
    
    __tablename__ = 'users'
    
    # -----------------------
    # Database Columns
    # -----------------------
    
    # User's first name (required, max 255 characters)
    first_name = db.Column(db.String(255), nullable=False)
    
    # User's last name (required, max 255 characters)
    last_name = db.Column(db.String(255), nullable=False)
    
    # Email address (required, unique, indexed for fast lookups)
    # index=True enables fast queries like "find user by email" (used in login)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Bcrypt hashed password (required, max 255 but bcrypt produces 60 chars)
    # NEVER store plain text passwords!
    password = db.Column(db.String(255), nullable=False)
    
    # Admin flag (default=False means regular user)
    # Admins can delete users, update any user, etc.
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # -----------------------
    # Relationships
    # -----------------------
    
    # One-to-Many: User can own multiple places
    # back_populates='owner' creates bidirectional relationship with Place.owner
    # cascade='all, delete-orphan' deletes all places when user is deleted
    # lazy=True loads places only when accessed (on-demand loading)
    places = db.relationship('Place', back_populates='owner', lazy=True, cascade='all, delete-orphan')
    
    # One-to-Many: User can write multiple reviews
    # backref='user' creates User.reviews attribute and Review.user attribute
    # cascade='all, delete-orphan' deletes all reviews when user is deleted
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, first_name=None, last_name=None, email=None, password=None, is_admin=False, **kwargs):
        """
        Initialize a new User instance.
        
        Args:
            first_name (str, optional): User's first name
            last_name (str, optional): User's last name
            email (str, optional): User's email address
            password (str, optional): Plain text password (will be hashed)
            is_admin (bool, optional): Admin privileges flag (default: False)
            **kwargs: Additional arguments passed to BaseModel (id, created_at, etc.)
            
        Raises:
            ValueError: If validation fails for any field
            
        Security note:
            The password parameter should be plain text - it will be
            automatically hashed using bcrypt before storage.
        """
        # Call parent constructor to initialize id, created_at, updated_at
        super().__init__(**kwargs)
        
        # Set user-specific attributes if provided
        # Each setter triggers the corresponding @validates decorator
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if email:
            self.email = email
        if is_admin is not None:
            self.is_admin = is_admin
        
        # Hash password if provided (NEVER store plain text!)
        if password:
            self.hash_password(password)

    def hash_password(self, password):
        """
        Hash a plain text password using bcrypt before storing it.
        
        This method is called automatically during user creation and
        when an admin updates a user's password.
        
        Bcrypt features:
        - Adaptive hashing (configurable work factor)
        - Built-in salt generation
        - Resistant to rainbow table attacks
        - Produces 60-character hash string
        
        Args:
            password (str): Plain text password to hash
            
        Raises:
            ValueError: If password is None, empty, or less than 6 characters
            
        Security:
            - Minimum length: 6 characters (enforced here)
            - Maximum length: No limit (bcrypt handles it)
            - Work factor: Default from bcrypt configuration
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        # Generate bcrypt hash and decode to UTF-8 string for database storage
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """
        Verify a plain text password against the stored bcrypt hash.
        
        This method is used during:
        - Login authentication
        - User profile updates (requires current password)
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
            
        Security:
            - Constant-time comparison (prevents timing attacks)
            - Automatically handles salt extraction from hash
            
        Usage:
            >>> user = User.query.filter_by(email='john@example.com').first()
            >>> if user.verify_password('userPassword123'):
            >>>     print("Login successful")
        """
        return bcrypt.check_password_hash(self.password, password)

    # -----------------------
    # SQLAlchemy Validators
    # -----------------------

    @validates('first_name')
    def validate_first_name(self, key, value):
        """
        Validate first name before saving to database.
        
        Validation rules:
        - Must not be None or empty string
        - Must be a string type
        - Must contain at least one non-whitespace character
        - Must be 255 characters or less
        
        Args:
            key (str): Attribute name ('first_name')
            value (str): Proposed first name value
            
        Returns:
            str: Validated and cleaned first name (whitespace stripped)
            
        Raises:
            ValueError: If validation fails
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("first_name must be a non-empty string")
        if len(value) > 255:
            raise ValueError("first_name must be less than 255 characters")
        return value.strip()

    @validates('last_name')
    def validate_last_name(self, key, value):
        """
        Validate last name before saving to database.
        
        Validation rules:
        - Must not be None or empty string
        - Must be a string type
        - Must contain at least one non-whitespace character
        - Must be 255 characters or less
        
        Args:
            key (str): Attribute name ('last_name')
            value (str): Proposed last name value
            
        Returns:
            str: Validated and cleaned last name (whitespace stripped)
            
        Raises:
            ValueError: If validation fails
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("last_name must be a non-empty string")
        if len(value) > 255:
            raise ValueError("last_name must be less than 255 characters")
        return value.strip()

    @validates('email')
    def validate_email_field(self, key, value):
        """
        Validate email format before saving to database.
        
        This validator uses the email-validator library to perform:
        - Syntax validation (RFC 5322)
        - Domain validation (optional, disabled here)
        - Email normalization (lowercase, etc.)
        
        Validation rules:
        - Must not be None or empty string
        - Must be a valid email format
        - Will be normalized (e.g., "John@Example.COM" → "john@example.com")
        
        Args:
            key (str): Attribute name ('email')
            value (str): Proposed email value
            
        Returns:
            str: Normalized and validated email address
            
        Raises:
            ValueError: If email is invalid or empty
            
        Examples:
            >>> user.email = "john@example.com"      # Valid
            >>> user.email = "John@Example.COM"      # Valid, normalized to "john@example.com"
            >>> user.email = "invalid-email"         # ValueError
            >>> user.email = "@example.com"          # ValueError
        """
        if not value or not isinstance(value, str):
            raise ValueError("Email must be a non-empty string")
        
        try:
            # Validate email format (check_deliverability=False skips DNS lookup)
            emailinfo = validate_email(value, check_deliverability=False)
            # Return normalized email (lowercase, etc.)
            return emailinfo.normalized
        except EmailNotValidError as e:
            # Re-raise with descriptive error message
            raise ValueError(f"Invalid email: {str(e)}")

    def to_dict(self, **kwargs):
        """
        Convert the User instance to a dictionary for JSON serialization.
        
        This method is used by Flask-RESTX to serialize user objects
        for API responses. It EXCLUDES the password hash for security.
        
        The dictionary includes:
        - id: Unique identifier (UUID)
        - first_name: User's first name
        - last_name: User's last name
        - email: User's email address
        - is_admin: Admin privileges flag
        - created_at: ISO 8601 timestamp
        - updated_at: ISO 8601 timestamp
        
        Excluded fields:
        - password: NEVER expose password hashes in API responses
        - places: Relationship (to prevent circular references)
        - reviews: Relationship (to prevent circular references)
        
        Args:
            **kwargs: Additional arguments passed to BaseModel.to_dict()
            
        Returns:
            dict: User data WITHOUT password hash
            
        Security:
            This is CRITICAL for security - password hashes must NEVER
            be included in API responses, even if hashed.
            
        Example output:
            {
                'id': 'abc-123-def-456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'is_admin': False,
                'created_at': '2023-11-09T10:30:00',
                'updated_at': '2023-11-09T10:30:00'
            }
        """
        # Get base dictionary from BaseModel (includes all columns)
        data = super().to_dict(**kwargs)
        
        # CRITICAL SECURITY: Remove password hash from response
        # Never expose password hashes in API responses
        data.pop('password', None)
        
        return data

    def __repr__(self):
        """
        Return a string representation of the User for debugging.
        
        Returns:
            str: Human-readable representation
                 Format: <User email>
                 Example: <User john@example.com>
        """
        return f"<User {self.email}>"