# 📝 Changelog

All notable changes to Fleet Management System project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Coming Soon
- Advanced reporting and analytics
- Email notifications system
- Mobile app (iOS/Android)  
- Real-time WebSocket updates
- FCM module cleanup (optional deprecation)

---

## [2.0.0] - 2025-10-03

### 🎯 **MAJOR MIGRATION COMPLETION**

#### ✅ **Fleet Data Manager → Fleet Workshop Manager Migration**
- **Complete module migration** from FDM to FWM
- **Migrated functionalities:**
  - 📱 **Device Management**: Full CRUD operations with filtering and validation
  - 🏢 **Customer Management**: Complete customer lifecycle management
- **Technical Implementation:**
  - Hash routing support: `#devices`, `#customers`
  - JWT authentication integration
  - API endpoints: `/api/v1/fleet-data/devices`, `/api/v1/fleet-data/customers`
  - Fixed device data structure (added required `device_number` field)
  - All 8/8 API tests passing successfully
- **Production URLs:**
  - Devices: `http://nvidia:5000/fleet-workshop-manager#devices`
  - Customers: `http://nvidia:5000/fleet-workshop-manager#customers`

#### ✅ **Fleet Config Manager → Connect Manager Migration**
- **Complete module migration** from FCM to CM
- **Migrated functionalities:**
  - ⚙️ **System Configuration**: System-wide settings management
  - 📱 **Device Configuration**: Individual device settings
  - 🧪 **Test Scenarios**: Test procedure definitions
  - 📋 **JSON Templates**: Reusable configuration templates
- **Technical Implementation:**
  - **JSON Tree Editor**: Visual JSON editing with type validation
  - **Modal Forms**: Professional overlay forms for all CRUD operations
  - **Hash Routing**: `#system-config`, `#device-config`, `#test-config`, `#json-templates`
  - **API Integration**: `/api/v1/fleet-config/` endpoints
  - **Role-based Access**: Configurator role enforcement
  - **Complete CRUD**: Create, Read, Update, Delete for all configuration types
- **Production URLs:**
  - System Config: `http://nvidia:5000/connect-manager#system-config`
  - Device Config: `http://nvidia:5000/connect-manager#device-config`
  - Test Config: `http://nvidia:5000/connect-manager#test-config`
  - JSON Templates: `http://nvidia:5000/connect-manager#json-templates`

### 🛠️ **Technical Enhancements**

#### **Complete CRUD Implementation**
- **System Configuration Management:**
  - `createSystemConfig()`, `editSystemConfig()`, `updateSystemConfig()`, `deleteSystemConfig()`
- **Test Scenario Management:**
  - `createTestScenario()`, `editTestScenario()`, `updateTestScenario()`, `deleteTestScenario()`
- **Device Configuration Management:**
  - `editDeviceConfig()`, `updateDeviceConfig()`
- **JSON Template Management:**
  - `saveTemplate()`, `editTemplate()`, `deleteTemplate()`

#### **Advanced JSON Tree Editor**
- **Visual JSON Editing**: Point-and-click structure editing
- **Type Management**: String, Number, Boolean, Object, Array support
- **Dynamic Operations**: Add, delete, rename fields in real-time
- **Preview Mode**: Live JSON preview with syntax highlighting
- **Validation**: Client-side validation before API submission

#### **Enhanced User Experience**
- **Hash Routing**: Direct bookmark access to specific sections
- **Modal Management**: Professional overlay forms with proper z-index
- **Error Handling**: User-friendly error messages and feedback
- **Auto-refresh**: Lists automatically update after operations
- **Form Validation**: Client-side validation with clear error messages

### 📚 **Documentation Updates**
- **Updated goals.md**: Complete migration status documentation
- **Created MIGRATION_DOCS.md**: Comprehensive technical migration guide
- **Created API_GUIDE.md**: User-friendly API usage documentation
- **Updated CHANGELOG.md**: Complete migration changelog

### ✅ **Migration Success Metrics**
- **Total Migrations Completed**: 2/2 ✅
- **Migrated Functionalities**: 6 (Devices, Customers, System Config, Device Config, Test Config, JSON Templates)
- **API Endpoints**: Fully integrated and tested ✅
- **Authentication**: JWT + role-based access working ✅
- **Hash Routing**: Implemented across all features ✅
- **Forms & Editors**: All functional ✅
- **Tests**: All passing ✅

### 🎯 **Production Ready Status**
- **Fleet Workshop Manager**: ✅ PRODUCTION READY
- **Connect Manager**: ✅ PRODUCTION READY
- **System Status**: ✅ MIGRATION COMPLETE

---

## [1.1.0] - 2025-09-30

### 🏗️ Major Architectural Refactoring

#### Modular Architecture Implementation
- **Created `modules/` directory structure** - Organized code into modular components
- **Extracted common components** to `modules/common/`:
  - `common.css` (465 lines) - 3-column layout, navigation, auth UI, responsive design
  - `auth.js` (193 lines) - JWT authentication, role switching, token management
  - `utils.js` (88 lines) - API requests, error handling, utilities
  - `base_layout.html` - Reusable template for all modules
- **Pilot modular implementation** - Fleet Software Manager as demonstration module
  - New endpoint: `/fsm-modular`
  - Fully functional with 3-column responsive layout
  - Dashboard with statistics cards
  - Software CRUD operations
  - API test section
- **Module registry pattern** - Prepared infrastructure for all 7 modules (cpp, cd, cm, fdm, fcm, fsm, fwm)
- **Static files mounting** - Changed from `/static/modules` to `/modules` for better organization

#### Backend Refactoring
- **Extracted Fleet Software router** - Moved to `backend/api/fleet_software_router.py`
  - Separated concerns from monolithic main.py
  - Cleaner API structure
  - Improved maintainability

#### Frontend Improvements
- **Consistent 3-column layout** across modular components
  - 15% left sidebar (module menu)
  - 70% main content
  - 15% right sidebar (login/role switcher)
- **Top navigation menu** - Unified module switching interface
- **Shared authentication UI** - Consistent login experience

### 🔧 Fixed
- **Static file loading** - Resolved 404 errors for CSS/JS files
  - Fixed path resolution from `/static/modules/...` to `/modules/...`
  - Proper mounting of modules directory
- **Module navigation** - Improved routing between modules
- **Docker deployment** - Fixed critical Docker startup errors
  - ✅ Resolved `RuntimeError: Directory 'static' does not exist`
  - ✅ Added automatic directory creation in Dockerfile (`/app/static`, `/app/modules`)
  - ✅ Added existence checks for directories before mounting in main.py
  - ✅ Removed obsolete `version` attribute from docker-compose.yml
  - ✅ Created `.gitkeep` file in static/ directory for Git tracking

### 📚 Documentation Updates
- **Updated ARCHITECTURE.md** - Added detailed modular architecture section
- **Updated TODO.md** - Marked completed tasks, added migration checklist
- **Created E2E tests** - Test suite in `tests/` directory
- **Created DOCKER.md** - Comprehensive Docker deployment documentation (600+ lines)
  - Quick start guide
  - Troubleshooting section
  - Production deployment best practices
  - Security hardening guidelines
  - Container monitoring and logging
- **Updated README.md** - Enhanced Docker setup section with fixed issues and links

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
- **Fixed `viewSoftware()` function** in Fleet Software Manager - corrected reference from non-existent `allSoftware` to `softwareList`
- **Verified `deleteSoftware()` function** in Fleet Software Manager - properly deletes software with confirmation dialog
- Enhanced software details display with version count and latest version information

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
