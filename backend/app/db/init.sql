-- PostgreSQL DB initialization script for Sparta AI
CREATE USER sparta WITH ENCRYPTED PASSWORD 'sparta_pass';
CREATE DATABASE sparta_db OWNER sparta;
GRANT ALL PRIVILEGES ON DATABASE sparta_db TO sparta;
-- Example table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
