-- Migration 001: Initial Schema
-- Creates the complete database schema for MFM Corporation Multi-Team Automation System
-- This file should be run first when setting up a new database

-- Run the main schema file
\i schema.sql

-- Record migration
CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO migrations (filename) VALUES ('001_initial_schema.sql');
