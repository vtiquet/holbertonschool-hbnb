#!/usr/bin/python3
"""
Facade pattern for HBnB application with SQLAlchemy.
Provides a simplified interface to complex subsystem operations (repositories, models).
Centralizes business logic and coordinates interactions between repositories.
"""

from app.persistence.user_repository import UserRepository
from app.persistence.amenity_repository import AmenityRepository
from app.persistence.place_repository import PlaceRepository
from app.persistence.review_repository import ReviewRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app import db


class HBnBFacade:
    """
    Facade class providing simplified interface to HBnB operations.
    Coordinates between repositories and enforces business rules.
    """
    
    def __init__(self):
        """Initialize facade with all repository instances"""
        self.user_repo = UserRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()

    # ======================
    # ===== USERS =====
    # ======================

    def create_user(self, user_data):
        """
        Create a new user with email validation.
        Args: user_data (dict): User attributes (email, password, first_name, last_name)
        Returns: User: Created user object
        Raises: ValueError: If email is missing or already registered
        """
        email = user_data.get('email')
        if not email:
            raise ValueError("Email is required")
        
        if self.user_repo.get_user_by_email(email):
            raise ValueError("Email already registered")

        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Get user by ID. Returns: User or None"""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Get user by email. Returns: User or None"""
        return self.user_repo.get_user_by_email(email)

    def get_all_user(self):
        """Get all users. Returns: list of User objects"""
        return self.user_repo.get_all()

    def update_user(self, user_id, data):
        """
        Update user with validation (cannot update id/created_at, email must be unique).
        Args: user_id (str): User UUID, data (dict): Fields to update
        Returns: Updated User or None if not found
        Raises: ValueError: If trying to update protected fields or duplicate email
        """
        user = self.user_repo.get(user_id)
        if not user:
            return None
        
        # Prevent updating immutable fields
        for field in ['id', 'created_at']:
            if field in data:
                raise ValueError(f"Cannot update '{field}'")
        
        # Validate email uniqueness
        if 'email' in data:
            existing_user = self.user_repo.get_user_by_email(data['email'])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already in use")
        
        # Hash password if provided
        if 'password' in data:
            user.hash_password(data['password'])
            data.pop('password')
        
        user.update(data)
        return user

    def delete_user(self, user_id):
        """
        Delete user (cascade deletes places and reviews via SQLAlchemy).
        Args: user_id (str): User UUID
        Returns: bool: True if deleted, False if not found
        """
        user = self.user_repo.get(user_id)
        if not user:
            return False
        
        # SQLAlchemy cascade will handle deletion of related places and reviews
        self.user_repo.delete(user_id)
        return True

    # ======================
    # ===== AMENITIES =====
    # ======================

    def create_amenity(self, amenity_data):
        """
        Create amenity with optional place/owner validation and association.
        Args: amenity_data (dict): name (required), place_id (optional), owner_id (optional)
        Returns: Amenity: Created amenity object
        Raises: ValueError: If name missing or place/owner not found
        """
        name = amenity_data.get("name")
        if not name:
            raise ValueError("Amenity name is required")
        
        place_id = amenity_data.get("place_id")
        owner_id = amenity_data.get("owner_id")
        
        # Validate place exists if provided
        if place_id:
            place = self.place_repo.get(place_id)
            if not place:
                raise ValueError(f"Place with id '{place_id}' not found")
        
        # Validate owner exists if provided
        if owner_id:
            owner = self.user_repo.get(owner_id)
            if not owner:
                raise ValueError(f"Owner with id '{owner_id}' not found")
        
        amenity = Amenity(
            name=name,
            place_id=place_id,
            owner_id=owner_id
        )
        
        self.amenity_repo.add(amenity)
        
        # Associate amenity with place if place_id provided
        if place_id:
            place = self.place_repo.get(place_id)
            if place and amenity not in place.amenities:
                place.amenities.append(amenity)
                db.session.commit()
        
        return amenity

    def get_amenity(self, amenity_id):
        """Get amenity by ID. Returns: Amenity or None"""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Get all amenities. Returns: list of Amenity objects"""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """
        Update amenity and manage place associations if place_id changes.
        Args: amenity_id (str): Amenity UUID, amenity_data (dict): Fields to update
        Returns: Updated Amenity or None if not found
        Raises: ValueError: If trying to update protected fields
        """
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        
        # Prevent updating immutable fields
        for field in ['id', 'created_at']:
            if field in amenity_data:
                raise ValueError(f"Cannot update '{field}'")
        
        old_place_id = amenity.place_id
        new_place_id = amenity_data.get('place_id')
        
        amenity.update(amenity_data)
        
        # Update place associations if place_id changed
        if new_place_id and new_place_id != old_place_id:
            # Remove from old place
            if old_place_id:
                old_place = self.place_repo.get(old_place_id)
                if old_place and amenity in old_place.amenities:
                    old_place.amenities.remove(amenity)
            
            # Add to new place
            new_place = self.place_repo.get(new_place_id)
            if new_place and amenity not in new_place.amenities:
                new_place.amenities.append(amenity)
            
            db.session.commit()
        
        return amenity

    def delete_amenity(self, amenity_id):
        """
        Delete amenity and remove from place associations.
        Args: amenity_id (str): Amenity UUID
        Returns: bool: True if deleted, False if not found
        """
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return False
        
        # Remove amenity from place if associated
        if amenity.place_id:
            place = self.place_repo.get(amenity.place_id)
            if place and amenity in place.amenities:
                place.amenities.remove(amenity)
                db.session.commit()
        
        self.amenity_repo.delete(amenity_id)
        return True

    # ======================
    # ===== PLACES =====
    # ======================

    def create_place(self, place_data):
        """
        Create place with owner validation and amenity associations.
        Args: place_data (dict): title, price, latitude, longitude, owner_id, amenities (list of IDs)
        Returns: Place: Created place object
        Raises: ValueError: If owner not found or amenity ID invalid
        """
        owner = self.user_repo.get(place_data.get("owner_id"))
        if not owner:
            raise ValueError("Owner not found")

        # Retrieve amenity objects from IDs
        amenity_ids = place_data.get("amenities", [])
        amenities = []
        if amenity_ids:
            for a_id in amenity_ids:
                amenity = self.amenity_repo.get(a_id)
                if not amenity:
                    raise ValueError(f"Amenity ID '{a_id}' not found")
                amenities.append(amenity)

        place = Place(
            title=place_data["title"],
            description=place_data.get("description", ""),
            price=place_data["price"],
            latitude=place_data["latitude"],
            longitude=place_data["longitude"],
            owner_id=owner.id,
            amenities=amenities
        )
        
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """Get place by ID. Returns: Place or None"""
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Get all places. Returns: list of Place objects"""
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update place with validation (cannot update id/owner_id/created_at).
        Args: place_id (str): Place UUID, place_data (dict): Fields to update
        Returns: Updated Place or None if not found
        Raises: ValueError: If trying to update protected fields or invalid amenity ID
        """
        place = self.place_repo.get(place_id)
        if not place:
            return None
        
        # Prevent updating immutable fields
        for field in ['id', 'owner_id', 'created_at']:
            if field in place_data:
                raise ValueError(f"Cannot update '{field}'")
        
        update_data = {}
        for key, value in place_data.items():
            if key == "amenities":
                # Validate and retrieve amenity objects
                new_amenities = []
                for a_id in value:
                    amenity = self.amenity_repo.get(a_id)
                    if not amenity:
                        raise ValueError(f"Amenity ID '{a_id}' not found")
                    new_amenities.append(amenity)
                update_data["amenities"] = new_amenities
            elif hasattr(place, key):
                update_data[key] = value

        place.update(update_data)
        return place

    def delete_place(self, place_id):
        """
        Delete place (cascade deletes reviews via SQLAlchemy).
        Args: place_id (str): Place UUID
        Returns: bool: True if deleted, False if not found
        """
        place = self.place_repo.get(place_id)
        if not place:
            return False
        
        # SQLAlchemy cascade will handle deletion of related reviews
        self.place_repo.delete(place_id)
        return True

    # ======================
    # ===== REVIEWS =====
    # ======================
    
    def create_review(self, review_data):
        """
        Create review with user/place validation.
        Args: review_data (dict): text, rating, user_id, place_id
        Returns: Review: Created review object
        Raises: ValueError: If user_id or place_id invalid/missing
        """
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')

        if not user_id or not self.user_repo.get(user_id):
            raise ValueError("Invalid or missing user_id")
        if not place_id or not self.place_repo.get(place_id):
            raise ValueError("Invalid or missing place_id")

        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """Get review by ID. Returns: Review or None"""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Get all reviews. Returns: list of Review objects"""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Get all reviews for a place.
        Args: place_id (str): Place UUID
        Returns: list of Review objects (empty if place not found)
        """
        if not self.place_repo.get(place_id):
            return []
        return self.review_repo.get_reviews_by_place(place_id)

    def user_has_reviewed_place(self, user_id, place_id):
        """
        Check if user has already reviewed a place.
        Args: user_id (str): User UUID, place_id (str): Place UUID
        Returns: bool: True if user has reviewed place
        """
        reviews = self.get_reviews_by_place(place_id)
        for review in reviews:
            if review.user_id == user_id:
                return True
        return False

    def update_review(self, review_id, review_data):
        """
        Update review (cannot update id/user_id/place_id/created_at).
        Args: review_id (str): Review UUID, review_data (dict): Fields to update
        Returns: Updated Review or None if not found
        Raises: ValueError: If trying to update protected fields
        """
        review = self.review_repo.get(review_id)
        if not review:
            return None

        # Prevent updating immutable fields
        for field in ['id', 'user_id', 'place_id', 'created_at']:
            if field in review_data:
                raise ValueError(f"Cannot update '{field}'")
        
        review.update(review_data)
        return review

    def delete_review(self, review_id):
        """
        Delete review.
        Args: review_id (str): Review UUID
        Returns: bool: True if deleted, False if not found
        """
        review = self.review_repo.get(review_id)
        if not review:
            return False
        return self.review_repo.delete(review_id)