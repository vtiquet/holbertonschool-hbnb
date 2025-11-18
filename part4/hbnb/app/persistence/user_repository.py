#!/usr/bin/python3
"""
User-specific repository for database operations.
Extends SQLAlchemyRepository with user-specific queries:
- get_user_by_email(): Find user by email (used for login/authentication)
- get_user_by_attribute(): Find user by any attribute (backward compatibility)
"""

from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """
    Repository for User-specific database operations.
    Inherits: get(id), get_all(), add(), update(id, data), delete(id)
    User-specific: get_user_by_email(), get_user_by_attribute()
    """
    
    def __init__(self):
        """Initialize UserRepository with User model"""
        super().__init__(User)
    
    def get_user_by_email(self, email):
        """
        Get a user by email address (used for login/authentication).
        Args: email (str): User's email address
        Returns: User: User object if found, None otherwise
        Use cases: Login authentication, email uniqueness validation
        Note: Email is unique and indexed for fast lookups
        """
        return self.model.query.filter_by(email=email).first()
    
    def get_user_by_attribute(self, attr_name, attr_value):
        """
        Get a user by any attribute (backward compatibility method).
        Args: attr_name (str): Attribute name (e.g., 'first_name'), attr_value: Attribute value
        Returns: User: User object if found, None otherwise
        Use cases: Generic search, backward compatibility with legacy code
        """
        return self.model.query.filter_by(**{attr_name: attr_value}).first()