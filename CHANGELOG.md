# 📝 Changelog

All notable changes to Fleet Management System project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Coming Soon
- Additional customer fields management
- Advanced reporting and analytics
- Email notifications system
- Mobile app (iOS/Android)
- Real-time WebSocket updates

---

## [1.0.0] - 2025-09-30

### 🎉 Initial Release

Complete Fleet Management System implementation with 7 webGUI modules.

### 🔧 Fixed - 2025-09-30 (Latest)
- **Eliminated 401 Unauthorized errors** for unauthenticated users before login
- Added JWT token validation before API requests in Fleet Config Manager, Fleet Data Manager, and Fleet Software Manager
- Implemented user-friendly messages: "💡 Zaloguj się aby zobaczyć..." instead of silent errors
- Added clearAuthToken() handling for expired/invalid tokens
- Improved user experience with proper error handling and feedback

### ✨ Added

#### Authentication & Authorization
- JWT token-based authentication system
- QR code login functionality
- Multi-role authentication system (6 roles)
- Role switching without re-login for maker1 user
- `/api/v1/auth/switch-role` endpoint
- Sidebar-based login interface across all modules

#### Frontend - User Interface
- **Sidebar layout** (15% + 85%) across all 5 modules
- **Responsive design** with @media queries for mobile devices
- Global navigation menu with module switching
- Role switcher dropdown for multi-role users
- Color-coded modules for visual distinction
- Hidden legacy elements (.header, .module-info, .auth-section)

#### Module 1: Connect++ (Operator)
- Device testing interface
- API endpoints testing (users, devices, customers, scenarios)
- Simple operator-friendly design
- Real-time API responses

#### Module 2: Connect Manager (Superuser)
- Test scenario creation and management (CRUD)
- **Visual JSON tree editor** for test_flow configurations
- JSON templates integration with device type filtering
- Scenario step management
- Auto-fill from JSON templates
- Smooth scrolling navigation

#### Module 3: Fleet Data Manager (Manager)
- Device management (CRUD operations)
- Customer management (CRUD operations)
- **Visual JSON tree editor** for customer contact_info
- Dashboard with fleet statistics
- Device filtering by type, status, customer
- Device-customer assignment system

#### Module 4: Fleet Config Manager (Configurator)
- System configuration management (CRUD)
- Device configuration management (CRUD)
- JSON templates management with type/category filtering
- Test scenario configurations
- Backup and restore functionality
- **Visual JSON tree editors** in 3 locations:
  - System Config value field
  - Test Scenario parameters and expected results
  - Backup/Restore data field
- URL hash navigation for bookmarkable tabs

#### Module 5: Fleet Software Manager (Maker)
- Software package management (CRUD)
- Version management per software package
- Installation tracking and history
- Dashboard with software statistics
- Scroll-to-section sidebar navigation

#### Backend - API
- FastAPI framework with 50+ REST endpoints
- Authentication group:
  - `POST /api/v1/auth/login` - Username/password login
  - `POST /api/v1/auth/login/qr` - QR code login
  - `POST /api/v1/auth/switch-role` - Role switching
  - `GET /api/v1/auth/me` - Current user info
- Fleet Data group (Manager):
  - Devices CRUD endpoints
  - Customers CRUD endpoints
  - Dashboard statistics endpoint
- Fleet Config group (Configurator):
  - System configs CRUD endpoints
  - Device configs CRUD endpoints
  - JSON templates CRUD with filtering
  - Test scenario configs endpoint
  - Backup/restore endpoints
- Fleet Software group (Maker):
  - Software CRUD endpoints
  - Versions management endpoints
  - Installations endpoints
  - Dashboard statistics endpoint
- Test Scenarios group (Superuser):
  - Scenarios CRUD endpoints

#### Database
- PostgreSQL with SQLAlchemy ORM
- 14 database tables:
  - users (with roles JSON field)
  - customers (with contact_info JSON field)
  - devices
  - software
  - software_versions
  - software_installations
  - test_scenarios
  - test_scenario_steps
  - test_reports
  - device_configurations
  - system_configurations
  - json_templates (with type/category filtering)
  - backup_logs
  - system_logs
- Automated table creation on startup
- Sample data initialization endpoint

#### Developer Experience
- Comprehensive documentation:
  - README.md with setup instructions
  - USERS.md with authentication guide
  - CHANGELOG.md (this file)
  - TODO.md with future tasks
  - docs/ARCHITECTURE.md
  - docs/API.md  
  - docs/DATABASE.md
- Docker support:
  - Dockerfile for API container
  - docker-compose.yml with PostgreSQL
- Replit deployment configuration (autoscale)
- OpenAPI 3.1 documentation (Swagger UI)
- Interactive API testing at `/docs`

### 🔐 Security
- JWT token with 30-minute expiration
- Password hashing with bcrypt
- Role-based access control (RBAC)
- QR code authentication support
- CORS configuration for production

### 📦 Dependencies
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Python 3.11+
- Uvicorn (ASGI server)

### 🐛 Bug Fixes
- Fixed Pydantic validation errors in Fleet Config and Fleet Software APIs
- Fixed CSS layout issues in sidebar implementation
- Fixed JavaScript errors (showCreateForm, scrollToSection)
- Fixed responsive design breakpoints for mobile devices
- Fixed JSON editor state management and reset functionality

### 🎨 UI/UX Improvements
- Visual JSON tree editors eliminate manual JSON syntax errors
- Sidebar navigation with module-specific menu items
- Active role display in auth message
- Smooth scrolling for section navigation
- Consistent color themes across modules
- Mobile-first responsive design

### ⚡ Performance
- Optimized database queries with proper indexing
- Efficient JSON handling in PostgreSQL
- Lazy loading for large datasets
- Connection pooling for database

### 🧪 Testing
- Sample data initialization for testing
- API endpoint testing interface in Connect++
- Pre-configured test users with all roles

---

## Default Users (v1.0.0)

| Username | Password | Roles | Description |
|----------|----------|-------|-------------|
| maker1 | pass | All 6 roles | Super user with role switching |
| admin | pass | superuser | Admin access |
| operator1 | pass | operator | Operator role |
| manager1 | pass | manager | Manager role |
| configurator | pass | configurator | Configurator role |

**⚠️ WARNING:** Change all default passwords in production!

---

## Database Schema Changes

### v1.0.0
- Initial schema with 14 tables
- Added `roles` JSON field to users table
- Added `contact_info` JSON field to customers table
- Added `test_flow` JSON field to test_scenarios table
- Added `default_values` JSON field to json_templates table

---

## API Changes

### v1.0.0
- Initial API with 50+ endpoints
- Added `/api/v1/auth/switch-role` for multi-role users
- Added JSON templates filtering by type and category
- Added dashboard statistics endpoints

---

## Known Issues

### v1.0.0

#### Fleet Software Manager - Partial Implementation
- **Missing Functions:**
  - `viewSoftware(id)` - Cannot view individual software details in modal
  - `deleteSoftware(id)` - Cannot delete software packages
- **Working Features:**
  - CREATE software (fully functional)
  - LIST software (fully functional)
  - UPDATE software (fully functional via form)
  - Versions management (READ operations functional)
  - Installations tracking (READ operations functional)
  - Dashboard statistics (fully functional)
- **Impact:** Medium - Core CRUD operations work, but detail view and delete are missing
- **Workaround:** Use API directly at `/docs` for delete operations
- **Planned Fix:** Q4 2025 (see TODO.md)

#### UI/UX Minor Issues
- Legacy auth sections still present in HTML (hidden via CSS, no functionality impact)
- Browser console warnings about password fields not in forms (cosmetic, harmless)
- Sidebar navigation errors in some modules (non-blocking)

#### Documentation
- Database schema documentation (docs/DATABASE.md) has been corrected to match actual implementation
- All 14 tables documented with correct field names and relationships

---

## Migration Guide

### Upgrading from minimal repository

This is the initial release built from scratch. No migration needed.

### Future versions

Migration guides will be provided for breaking changes.

---

## Contributors

- Development Team - Initial implementation
- Architecture Team - System design
- QA Team - Testing and validation

---

## Links

- [Repository](https://github.com/your-org/fleet-management)
- [Documentation](docs/)
- [API Docs](http://localhost:5000/docs)
- [Issues](https://github.com/your-org/fleet-management/issues)

---

[Unreleased]: https://github.com/your-org/fleet-management/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/fleet-management/releases/tag/v1.0.0
