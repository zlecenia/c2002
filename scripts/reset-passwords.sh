#!/bin/bash

# Fleet Management System - Password Reset Script
# Changes all user passwords to a specified password
# Usage: ./reset-passwords.sh [new_password]

set -e

# Configuration
DEFAULT_PASSWORD="password123"
NEW_PASSWORD="${1:-$DEFAULT_PASSWORD}"
DB_CONTAINER="fleet_management_db"
DB_USER="fleetuser"
DB_NAME="fleet_management"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Fleet Management System - Password Reset Tool${NC}"
echo -e "${BLUE}===================================================${NC}"

# Check if Docker container is running
if ! docker-compose ps | grep -q "fleet_management_db.*Up"; then
    echo -e "${RED}❌ Error: Database container is not running${NC}"
    echo -e "${YELLOW}💡 Run: docker-compose up -d${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Current users in database:${NC}"
docker-compose exec -T db psql -U $DB_USER -d $DB_NAME -c "
SELECT username, role, is_active 
FROM users 
ORDER BY username;" 2>/dev/null

echo ""
echo -e "${YELLOW}⚠️  This will change passwords for ALL users to: ${GREEN}$NEW_PASSWORD${NC}"
echo -e "${YELLOW}⚠️  Current database: ${GREEN}$DB_NAME${NC}"
echo ""

# Confirmation prompt
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚫 Operation cancelled${NC}"
    exit 0
fi

echo -e "${BLUE}🔄 Generating password hash...${NC}"

# Generate bcrypt hash using Python (same method as FastAPI)
HASHED_PASSWORD=$(python3 -c "
import bcrypt
password = '$NEW_PASSWORD'.encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode('utf-8'))
")

if [ -z "$HASHED_PASSWORD" ]; then
    echo -e "${RED}❌ Error: Failed to generate password hash${NC}"
    echo -e "${YELLOW}💡 Make sure Python3 and bcrypt are installed: pip install bcrypt${NC}"
    exit 1
fi

echo -e "${BLUE}🔄 Updating passwords in database...${NC}"

# Update all user passwords
docker-compose exec -T db psql -U $DB_USER -d $DB_NAME << EOF
-- Update all user passwords
UPDATE users 
SET password_hash = '$HASHED_PASSWORD',
    updated_at = NOW()
WHERE is_active = true;

-- Show updated users
SELECT 
    username, 
    role, 
    is_active,
    CASE 
        WHEN password_hash = '$HASHED_PASSWORD' THEN '✅ Updated'
        ELSE '❌ Not updated'
    END as password_status,
    updated_at
FROM users 
ORDER BY username;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Password reset completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Login credentials for all active users:${NC}"
    echo -e "${GREEN}Username: maker1, admin1, manager1, operator1, operator2, configurator1${NC}"
    echo -e "${GREEN}Password: $NEW_PASSWORD${NC}"
    echo ""
    echo -e "${YELLOW}💡 Test login at: http://localhost:5000/api/v1/auth/login${NC}"
    echo -e "${YELLOW}💡 Example curl command:${NC}"
    echo "curl -X POST http://localhost:5000/api/v1/auth/login \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"username\": \"maker1\", \"password\": \"$NEW_PASSWORD\"}'"
else
    echo -e "${RED}❌ Error: Failed to update passwords${NC}"
    exit 1
fi
