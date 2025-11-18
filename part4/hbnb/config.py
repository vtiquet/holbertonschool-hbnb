#!/usr/bin/python3
"""
Flask configuration classes for different environments.
Provides base config (Config) and environment-specific configs (DevelopmentConfig, ProductionConfig).
Uses environment variables for sensitive data (SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL).
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class (inherited by all environments).
    Contains common settings: secret keys, JWT expiration, SQLAlchemy settings.
    """
    # Flask secret key for session management and CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    
    # JWT secret key for signing and verifying tokens
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
    
    # JWT token expiration time (30 days)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database URI (defaults to SQLite in development)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hbnb_dev.db')
    
    # Disable SQLAlchemy event system (saves memory, prevents deprecation warnings)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Debug mode (disabled by default, enabled in DevelopmentConfig)
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    Enables debug mode and SQL query logging (SQLALCHEMY_ECHO).
    """
    DEBUG = True  # Enable Flask debug mode (detailed error pages, auto-reload)
    SQLALCHEMY_ECHO = True  # Print all SQL queries to console (for debugging)


# Configuration dictionary (maps environment name to config class)
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}