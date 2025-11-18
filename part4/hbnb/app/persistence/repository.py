#!/usr/bin/python3
"""
Repository pattern implementation for data persistence.

This module defines the Repository pattern using abstract base classes
and provides two concrete implementations:
- InMemoryRepository: For testing and development (data in RAM)
- SQLAlchemyRepository: For production (data in database)

The Repository pattern provides:
- Abstraction over data storage (can swap implementations)
- Consistent interface for CRUD operations
- Easier testing (can use in-memory for unit tests)
- Separation of concerns (business logic vs data access)

All repositories implement the Repository interface:
- add(obj): Create a new object
- get(obj_id): Retrieve object by ID
- get_all(): Retrieve all objects
- update(obj_id, data): Update object by ID
- delete(obj_id): Delete object by ID
- get_by_attribute(attr_name, attr_value): Find by attribute
"""

from abc import ABC, abstractmethod


class Repository(ABC):
    """
    Abstract base class defining the repository interface.
    
    This class defines the contract that all repository implementations
    must follow. It uses Python's ABC (Abstract Base Class) to enforce
    that child classes implement all abstract methods.
    
    Methods that MUST be implemented by child classes:
    - add(obj): Add object to storage
    - get(obj_id): Retrieve object by ID
    - get_all(): Retrieve all objects
    - update(obj_id, data): Update object
    - delete(obj_id): Remove object
    - get_by_attribute(attr_name, attr_value): Find by attribute
    """
    
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    """
    In-memory implementation of Repository (for testing/development).
    
    This implementation stores objects in a Python dictionary (RAM).
    Data is NOT persisted between application restarts.
    
    Use cases:
    - Unit testing (fast, no database required)
    - Development/prototyping
    - Temporary data storage
    
    Storage:
    - Uses a dictionary: {obj_id: obj}
    - Fast O(1) lookups by ID
    - No persistence (data lost on restart)
    """
    
    def __init__(self):
        """
        Initialize the in-memory storage.
        
        Creates an empty dictionary to store objects by their ID.
        """
        # Dictionary to store objects: {obj_id: obj}
        self._storage = {}

    def add(self, obj):
        """
        Add an object to in-memory storage.
        
        Args:
            obj: Object to add (must have an 'id' attribute)
            
        Note:
            If an object with the same ID exists, it will be overwritten.
        """
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """
        Retrieve an object by ID from memory.
        
        Args:
            obj_id (str): UUID of the object
            
        Returns:
            Object if found, None otherwise
        """
        return self._storage.get(obj_id)

    def get_all(self):
        """
        Retrieve all objects from memory.
        
        Returns:
            list: List of all stored objects (not ordered)
        """
        return list(self._storage.values())

    def update(self, obj_id, data):
        """
        Update an object in memory.
        
        Args:
            obj_id (str): UUID of the object to update
            data (dict): Dictionary of attributes to update
            
        Note:
            Calls the object's update() method (from BaseModel)
        """
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        """
        Delete an object from memory.
        
        Args:
            obj_id (str): UUID of the object to delete
            
        Note:
            Silently does nothing if object doesn't exist
        """
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        """
        Find the first object matching a specific attribute.
        
        Args:
            attr_name (str): Name of the attribute (e.g., 'email')
            attr_value: Value to search for
            
        Returns:
            First matching object, or None if not found
            
        Performance:
            O(n) linear search through all objects
        """
        return next(
            (obj for obj in self._storage.values() if getattr(obj, attr_name, None) == attr_value),
            None
        )


# ========== SQLAlchemy Repository (Production Implementation) ==========

from app import db


class SQLAlchemyRepository(Repository):
    """
    SQLAlchemy implementation of Repository (for production).
    
    This implementation uses SQLAlchemy ORM to persist objects
    to a relational database (PostgreSQL, MySQL, SQLite, etc.).
    
    Features:
    - ACID transactions (Atomicity, Consistency, Isolation, Durability)
    - Data persistence across application restarts
    - Relationship management (foreign keys, joins)
    - Query optimization (indexes, lazy loading)
    
    Use cases:
    - Production environment
    - Data that must be persisted
    - Complex queries and relationships
    """
    
    def __init__(self, model):
        """
        Initialize repository with a SQLAlchemy model.
        
        Args:
            model: SQLAlchemy model class (e.g., User, Place, Review, Amenity)
            
        Usage:
            >>> from app.models.user import User
            >>> user_repo = SQLAlchemyRepository(User)
        """
        # Store the model class for query operations
        self.model = model
    
    def add(self, obj):
        """
        Add an object to the database.
        
        Args:
            obj: SQLAlchemy model instance to add
            
        Returns:
            The added object (with ID populated after commit)
            
        Database operations:
        1. db.session.add(obj) - Stage object for insertion
        2. db.session.commit() - Execute INSERT query
        """
        db.session.add(obj)
        db.session.commit()
        return obj
    
    def get(self, obj_id):
        """
        Retrieve an object by ID from database.
        
        Args:
            obj_id (str): UUID of the object
            
        Returns:
            Object if found, None otherwise
            
        SQL equivalent:
            SELECT * FROM table WHERE id = obj_id LIMIT 1
        """
        return self.model.query.get(obj_id)
    
    def get_all(self):
        """
        Retrieve all objects of this model from database.
        
        Returns:
            list: List of all objects (not ordered by default)
            
        SQL equivalent:
            SELECT * FROM table
        """
        return self.model.query.all()
    
    def update(self, obj_id, data):
        """
        Update an object in the database.
        
        Args:
            obj_id (str): UUID of the object to update
            data (dict): Dictionary of attributes to update
            
        Returns:
            Updated object if found, None otherwise
            
        Database operations:
        1. Retrieve object by ID
        2. Call obj.update(data) - Updates attributes and commits
        """
        obj = self.get(obj_id)
        if obj:
            # obj.update() is from BaseModel (updates attributes + commits)
            obj.update(data)
            return obj
        return None
    
    def delete(self, obj_id):
        """
        Delete an object from the database.
        
        Args:
            obj_id (str): UUID of the object to delete
            
        Returns:
            bool: True if deleted, False if not found
            
        Database operations:
        1. Retrieve object by ID
        2. db.session.delete(obj) - Stage for deletion
        3. db.session.commit() - Execute DELETE query
        
        Note:
            Cascade rules (e.g., cascade='all, delete-orphan') are
            automatically handled by SQLAlchemy relationships.
        """
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False
    
    def get_by_attribute(self, attr_name, attr_value):
        """
        Find an object by a specific attribute (generic method).
        
        Args:
            attr_name (str): Name of the attribute (e.g., 'email', 'name')
            attr_value: Value to search for
            
        Returns:
            First matching object, or None if not found
            
        SQL equivalent:
            SELECT * FROM table WHERE attr_name = attr_value LIMIT 1
            
        Usage:
            >>> user = repo.get_by_attribute('email', 'john@example.com')
            >>> amenity = repo.get_by_attribute('name', 'WiFi')
        """
        return self.model.query.filter_by(**{attr_name: attr_value}).first()