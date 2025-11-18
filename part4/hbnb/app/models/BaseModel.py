#!/usr/bin/python3
"""
BaseModel class for the HBnB application.

This module defines the abstract base class that all entities inherit from.
It provides common functionality shared across all database models:
- Unique identifier (UUID)
- Timestamp tracking (created_at, updated_at)
- CRUD operations (save, delete, update)
- Serialization (to_dict)

All models (User, Place, Review, Amenity) inherit from this class
to ensure consistent behavior and database schema.
"""

from app import db
import uuid
from datetime import datetime


class BaseModel(db.Model):
    """
    Abstract base model for all database entities.
    
    This class provides common columns and methods that all models inherit.
    It is marked as abstract, so SQLAlchemy will NOT create a 'base_model' table.
    
    Common Columns (inherited by all models):
        id (str): Unique identifier using UUID v4 format (36 characters)
        created_at (datetime): Timestamp when the record was created (UTC)
        updated_at (datetime): Timestamp when the record was last modified (UTC)
    
    Common Methods (inherited by all models):
        save(): Persist the instance to the database
        delete(): Remove the instance from the database
        update(data): Update multiple attributes from a dictionary
        to_dict(): Convert the instance to a JSON-serializable dictionary
    
    Child Classes:
        - User: Application users
        - Place: Rental properties/listings
        - Review: User reviews of places
        - Amenity: Features/services available at places
    """
    
    # Mark this class as abstract - SQLAlchemy will not create a table for it
    # Child classes (User, Place, etc.) will each have their own tables
    __abstract__ = True
    
    # -----------------------
    # Common Database Columns
    # -----------------------
    
    # Primary key using UUID v4 format (e.g., "550e8400-e29b-41d4-a716-446655440000")
    # default=lambda: generates a new UUID for each new instance
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Timestamp when the record was created (automatically set on INSERT)
    # Uses UTC to avoid timezone issues
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamp when the record was last modified
    # onupdate=datetime.utcnow automatically updates on every UPDATE
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self):
        """
        Persist the current instance to the database.
        
        This method:
        1. Updates the updated_at timestamp to current UTC time
        2. Adds the instance to the SQLAlchemy session
        3. Commits the transaction to the database
        
        Usage:
            >>> user = User(first_name="John", last_name="Doe")
            >>> user.save()  # INSERT into users table
        
        Note:
            If the instance already exists in the database, this performs an UPDATE.
            If it's a new instance, this performs an INSERT.
        """
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Remove the current instance from the database.
        
        This method:
        1. Marks the instance for deletion in the SQLAlchemy session
        2. Commits the transaction to permanently delete the record
        
        Usage:
            >>> user = User.query.get(user_id)
            >>> user.delete()  # DELETE from users table
        
        Note:
            Cascade rules defined in relationships will handle related records.
            For example, deleting a User will also delete their Places and Reviews.
        """
        db.session.delete(self)
        db.session.commit()

    def update(self, data):
        """
        Update multiple instance attributes from a dictionary.
        
        This method:
        1. Iterates through the provided key-value pairs
        2. Skips protected/immutable fields (id, created_at, __class__)
        3. Updates only attributes that exist on the model
        4. Updates the updated_at timestamp
        5. Commits the changes to the database
        
        Args:
            data (dict): Dictionary of attribute names and new values
                         Example: {'first_name': 'Jane', 'last_name': 'Smith'}
        
        Protected fields (will be ignored):
            - id: Immutable primary key
            - created_at: Immutable creation timestamp
            - __class__: Internal Python attribute
        
        Usage:
            >>> user = User.query.get(user_id)
            >>> user.update({'first_name': 'Jane', 'email': 'jane@example.com'})
            >>> # Only first_name and email are updated, id and created_at remain unchanged
        
        Note:
            This method only updates attributes that already exist on the model.
            Attempting to set non-existent attributes will be silently ignored.
        """
        for key, value in data.items():
            # Skip immutable fields (id, created_at) and internal Python attributes (__class__)
            if key in ['id', 'created_at', '__class__']:
                continue
            # Only update if the attribute exists on the model (prevents typos/injection)
            if hasattr(self, key):
                setattr(self, key, value)
        # Update the modification timestamp
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self, **kwargs):
        """
        Convert the instance to a JSON-serializable dictionary.
        
        This method:
        1. Iterates through all database columns
        2. Retrieves the current value for each column
        3. Converts datetime objects to ISO 8601 strings
        4. Adds a '__class__' field with the model name
        
        Datetime conversion:
            - datetime objects are converted to ISO 8601 format
            - Example: 2023-11-09T10:30:00.123456
        
        Args:
            **kwargs: Reserved for future extensions (currently unused)
        
        Returns:
            dict: Dictionary representation with all column values
                  Example for User:
                  {
                      'id': 'abc-123-def-456',
                      'first_name': 'John',
                      'email': 'john@example.com',
                      'created_at': '2023-11-09T10:30:00',
                      'updated_at': '2023-11-09T10:30:00',
                      '__class__': 'User'
                  }
        
        Usage:
            >>> user = User.query.get(user_id)
            >>> user_dict = user.to_dict()
            >>> return jsonify(user_dict)  # Returns JSON response
        
        Note:
            - Relationships (e.g., user.places) are NOT included to avoid circular references
            - Sensitive fields (e.g., password hashes) should be excluded in child classes
            - The '__class__' field helps identify the model type in API responses
        """
        data = {}
        # Iterate through all database columns defined in the model
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert datetime objects to ISO 8601 string format for JSON compatibility
            if isinstance(value, datetime):
                data[column.name] = value.isoformat()
            else:
                data[column.name] = value
        # Add model class name for type identification
        data['__class__'] = self.__class__.__name__
        return data

    def __repr__(self):
        """
        Return a string representation of the instance for debugging.
        
        This method is called when you print() an instance or view it
        in the Python console/debugger.
        
        Returns:
            str: Human-readable representation
                 Format: <ModelName id>
                 Example: <User abc-123-def-456>
        
        Usage:
            >>> user = User.query.get(user_id)
            >>> print(user)
            <User abc-123-def-456>
            >>> users = User.query.all()
            >>> print(users)
            [<User abc-123>, <User def-456>, <User ghi-789>]
        """
        return f"<{self.__class__.__name__} {self.id}>"