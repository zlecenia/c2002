-- Initialize Connect++ (CPP) Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cppdb TO cppuser;

-- Note: Tables will be created by Alembic migrations
-- This script is for initial database setup only

-- Insert initial data (optional)
-- This will be handled by seeders after Alembic migrations
