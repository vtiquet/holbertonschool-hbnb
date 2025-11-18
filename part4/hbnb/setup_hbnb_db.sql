-- Drop tables in reverse order of dependencies to avoid foreign key constraints errors
DROP TABLE IF EXISTS place_amenity;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS amenities;
DROP TABLE IF EXISTS users;

-- Set the current timestamp for initial data insertion
-- Note: SQLite does not have a separate DATETIME type, but stores as TEXT, REAL, or INTEGER.
-- We use the ISO 8601 string format (YYYY-MM-DD HH:MM:SS).
-- For production environments (MySQL), you should use UTC_TIMESTAMP().
PRAGMA foreign_keys = ON;

----------------------------------------------------
-- 1. CREATE USERS TABLE
----------------------------------------------------
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL, -- Stores the bcrypt hash
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

----------------------------------------------------
-- 2. CREATE AMENITIES TABLE
----------------------------------------------------
CREATE TABLE amenities (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

----------------------------------------------------
-- 3. CREATE PLACES TABLE
----------------------------------------------------
CREATE TABLE places (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    latitude REAL,
    longitude REAL,
    number_of_rooms INTEGER NOT NULL DEFAULT 1,
    number_of_bathrooms INTEGER NOT NULL DEFAULT 1,
    max_guests INTEGER NOT NULL DEFAULT 1,
    owner_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
);

----------------------------------------------------
-- 4. CREATE REVIEWS TABLE
----------------------------------------------------
CREATE TABLE reviews (
    id VARCHAR(36) PRIMARY KEY,
    text TEXT NOT NULL,
    rating INTEGER NOT NULL,
    place_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

----------------------------------------------------
-- 5. CREATE PLACE_AMENITY ASSOCIATION TABLE (Many-to-Many)
----------------------------------------------------
CREATE TABLE place_amenity (
    place_id VARCHAR(36) NOT NULL,
    amenity_id VARCHAR(36) NOT NULL,
    PRIMARY KEY(place_id, amenity_id),
    FOREIGN KEY(place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY(amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);

----------------------------------------------------
-- 6. INITIAL DATA INSERTION
----------------------------------------------------

-- Insert Administrator User
-- ID: d5f9a6b1-4d3e-4f5c-9c7a-3b1a2c8d7e6f
-- Password: admin1234 (hashed using bcrypt for secure storage)
INSERT INTO users (id, first_name, last_name, email, password, is_admin, created_at, updated_at) VALUES
('d5f9a6b1-4d3e-4f5c-9c7a-3b1a2c8d7e6f', 'Admin', 'User', 'admin@hbnb.com', '$2b$12$6K6NfD9q/j1/0.g1K2H8f.D7i0s1B3g6y0p8t5e2n6c1u0h4j7o8i9s0', 1, DATETIME('now'), DATETIME('now'));


-- Insert Initial Amenities
INSERT INTO amenities (id, name, created_at, updated_at) VALUES
('a0f78c8d-195b-4e89-9a2c-9a4f6d3d9b4c', 'WiFi', DATETIME('now'), DATETIME('now')),
('a1f78c8d-195b-4e89-9a2c-9a4f6d3d9b4c', 'Swimming Pool', DATETIME('now'), DATETIME('now')),
('a3f78c8d-195b-4e89-9a2c-9a4f6d3d9b4c', 'Air Conditioning', DATETIME('now'), DATETIME('now')),
