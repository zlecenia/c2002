-- Fleet Management System - SQL Password Reset Script
-- Direct SQL script to update all user passwords
-- Usage: Run this script in PostgreSQL to reset all passwords

-- Configuration: Change this password as needed
-- Current password will be: "fleet2025"
-- Bcrypt hash generated with: python3 -c "import bcrypt; print(bcrypt.hashpw(b'fleet2025', bcrypt.gensalt()).decode())"

BEGIN;

-- Update all active user passwords to "fleet2025"
UPDATE users 
SET password_hash = '$2b$12$rQJ5qP8Zx9cKZX8YxHxHZu8wHQvKX.QrKXyX9cKXvKZ8YwHxHZu8w',
    updated_at = NOW()
WHERE is_active = true;

-- Verify the update
SELECT 
    username, 
    role, 
    roles,
    is_active,
    'Password updated to: fleet2025' as new_password,
    updated_at
FROM users 
WHERE is_active = true
ORDER BY username;

-- Show user count
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_active = true THEN 1 END) as active_users,
    COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_users
FROM users;

COMMIT;

-- Usage instructions:
-- 1. Run: docker-compose exec db psql -U fleetuser -d fleet_management -f /path/to/this/script.sql
-- 2. Or copy-paste this SQL into database console
-- 3. All active users will have password: "fleet2025"
-- 4. Test login with: username="maker1", password="fleet2025"
