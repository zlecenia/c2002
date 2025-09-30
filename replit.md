# Fleet Management System

## Overview
Comprehensive Fleet Management System based on Polish technical specifications, transformed from minimal GitHub repository (https://github.com/zlecenia/02) into a full-featured enterprise application for testing device masks and fleet operations.

## Recent Changes
- **September 30, 2025**: URL Hash Navigation & Visual JSON Editors in Fleet Config Manager
  - **Added URL hash tracking to all 3 multi-tab modules** (Fleet Config Manager, Fleet Data Manager, Fleet Software Manager)
  - Browser URL now reflects current tab (e.g., `/fleet-config-manager#system-config`)
  - Users can bookmark specific tabs and share direct links to module sections
  - Browser back/forward buttons work correctly with tab navigation
  - Hash changes automatically switch to corresponding tab
  - **Visual JSON Editors in Fleet Config Manager**: Replaced ALL textarea-based JSON editing with interactive visual tree editors
  - System Config form: `config-value` now uses visual JSON tree editor
  - Test Scenario form: `test-parameters` and `expected-results` use visual JSON tree editors
  - Backup/Restore: `restore-data` uses visual JSON tree editor
  - All editors properly reset to default values when forms are closed or after successful operations
  - Eliminates JSON syntax errors with intuitive form-based interface
  - Architect-validated implementation with proper state management

- **September 30, 2025**: Global Navigation Menu - Seamless Module Switching
  - **Added unified navigation menu to all 5 webGUI modules**
  - Top navigation bar with all modules: Home, Connect++, Commands Manager, Fleet Data Manager, Fleet Config Manager, Fleet Software Manager, API Docs
  - Active module highlighted with color-coded theme matching each module's design
  - Responsive design with icons and labels for each module
  - One-click navigation between modules without returning to home page
  - Consistent user experience across entire application
  - Mobile-friendly horizontal menu with flex-wrap support

- **September 30, 2025**: Universal JSON Tree Editor - Interactive Form-Based JSON Editing
  - **Replaced ALL textarea-based JSON editing with interactive visual tree editors**
  - Created reusable `JSONTreeEditor` JavaScript class supporting all JSON types (string, number, boolean, object, array)
  - Dynamic form rendering with type-specific input fields (text, number, checkbox)
  - Interactive tree structure with expandable/collapsible nested objects and arrays
  - Real-time field management: add/remove fields, rename keys, change types
  - JSON preview toggle for verification
  - **Commands Manager**: Scenarios now use visual JSON tree editor for test_flow configurations
  - **Fleet Config Manager**: JSON Templates tab now uses visual JSON tree editor for default_values
  - Eliminated manual JSON syntax errors with intuitive form-based interface
  - Consistent UX across all modules with copy-paste JSON eliminated

- **September 30, 2025**: JSON Templates Visual Editor in Fleet Config Manager
  - Added new "📋 Szablony JSON" tab to Fleet Config Manager with full CRUD interface
  - Complete template management: create, read, update, delete, view
  - Filtering by template type (test_flow, device_config, system_config) and category
  - Schema field now optional for flexibility
  - Beautiful table view with action buttons (👁️ Podgląd, ✏️ Edytuj, 🗑️ Usuń)
  - All CRUD operations tested and working perfectly

- **September 30, 2025**: JSON Templates System & Visual Editor Implementation
  - Added JSON Templates database table with 5 predefiniowane szablony for different device types
  - Implemented complete CRUD API for JSON templates in Fleet Config Manager
  - Created visual JSON editor in Commands Manager with template selection
  - Templates automatically filter by device type (mask_tester, pressure_sensor, flow_meter)
  - Auto-fill JSON configuration from templates with inline editing capability
  - Scenarios now support test_flow JSON configurations
  - Fixed Pydantic validation errors in Fleet Config and Fleet Software APIs
  - All modules tested and validated successfully

- **September 30, 2025**: Professional Landing Page Implementation
  - Created responsive HTML landing page for root "/" endpoint
  - Beautiful gradient design with module cards and responsive layout
  - Mobile-optimized interface with all 5 modules accessible from home
  - Fixed deployment configuration for Autoscale publication
  - System ready for production deployment
  
- **September 29, 2025**: Complete Fleet Management System implementation
  - Built from scratch: Python FastAPI + PostgreSQL + JWT authentication
  - Implemented all 5 webGUI modules according to Polish technical specifications
  - Created comprehensive REST API with 50+ endpoints
  - Added JWT + QR code authentication system
  - Configured role-based access control (operator, admin, superuser, manager, configurator, maker)
  - Set up deployment configuration for production autoscale
  - **COMPLETED**: All 5 modules fully operational and architect-validated

## Project Architecture
- **Backend**: Python FastAPI with SQLAlchemy ORM running on port 5000
- **Database**: PostgreSQL with 14 tables (Users, Devices, Software, Installations, JSON Templates, etc.)
- **Authentication**: JWT tokens + QR code login system with role-based access
- **API**: REST API with 50+ endpoints and OpenAPI 3.1 documentation
- **Frontend**: 5 specialized webGUI modules for different user roles
- **Deployment**: Production-ready autoscale configuration

## Key Features
- JWT + QR code authentication system
- Role-based access control (6 roles: operator, admin, superuser, manager, configurator, maker)
- 5 specialized webGUI modules for comprehensive fleet management
- Comprehensive CRUD API with 50+ endpoints
- PostgreSQL database with full relational schema (13 tables)
- OpenAPI documentation with Swagger UI
- Production deployment configuration

## Modules Implemented (100% Complete)
1. **Connect++** (`/connect-plus`) - Operator - Device testing interface
2. **Commands Manager** (`/commands-manager`) - Superuser - Test scenario management
3. **Fleet Data Manager** (`/fleet-data-manager`) - Manager - Device & customer data
4. **Fleet Config Manager** (`/fleet-config-manager`) - Configurator - System configuration
5. **Fleet Software Manager** (`/fleet-software-manager`) - Maker - Software management
6. **API Documentation** (`/docs`) - Complete Swagger documentation
7. **Authentication System** - JWT + QR code login endpoints

## Structure
```
/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── backend/               # Backend components
│   ├── models/           # SQLAlchemy database models
│   ├── auth/             # Authentication & JWT handling
│   ├── api/              # API routers (auth, users)
│   ├── core/             # Configuration settings
│   └── db/               # Database connection
├── frontend/             # Frontend modules (future expansion)
└── replit.md             # This documentation
```

## API Endpoints (50+ endpoints)
### Authentication
- `POST /api/v1/auth/login` - Username/password authentication
- `POST /api/v1/auth/login/qr` - QR code authentication  
- `GET /api/v1/auth/me` - Current user information

### Fleet Data Management (Manager)
- `GET/POST/PUT/DELETE /api/v1/fleet-data/devices` - Device CRUD operations
- `GET/POST/PUT/DELETE /api/v1/fleet-data/customers` - Customer CRUD operations
- `GET /api/v1/fleet-data/dashboard` - Fleet data statistics

### Fleet Configuration (Configurator)
- `GET/POST/PUT/DELETE /api/v1/fleet-config/system-configs` - System configuration CRUD
- `GET/POST/PUT/DELETE /api/v1/fleet-config/device-configs` - Device configuration CRUD
- `GET/POST/PUT/DELETE /api/v1/fleet-config/json-templates` - JSON templates CRUD with filtering
- `GET /api/v1/fleet-config/test-scenario-configs` - Test scenario configurations
- `POST /api/v1/fleet-config/backup` - Configuration backup
- `POST /api/v1/fleet-config/restore` - Configuration restore

### Fleet Software Management (Maker)
- `GET/POST/PUT/DELETE /api/v1/fleet-software/software` - Software CRUD operations
- `GET/POST /api/v1/fleet-software/software/{id}/versions` - Version management
- `GET/POST /api/v1/fleet-software/installations` - Installation management
- `GET /api/v1/fleet-software/dashboard/stats` - Software statistics

### Test Scenarios (Superuser)
- `GET/POST/PUT/DELETE /api/v1/scenarios/` - Test scenario CRUD operations

## Current State
🎉 **SYSTEM 100% COMPLETE** 🎉

The Fleet Management System is fully implemented according to Polish technical specifications with all 5 modules operational:

✅ **Connect++** - Device testing interface for operators
✅ **Commands Manager** - Test scenario management for superusers  
✅ **Fleet Data Manager** - Device/customer data management for managers
✅ **Fleet Config Manager** - System configuration management for configurators
✅ **Fleet Software Manager** - Software installation management for makers

All modules include:
- Complete CRUD API endpoints with role-based access control
- Professional web interfaces with authentication
- Real database persistence with PostgreSQL
- Dashboard statistics and reporting
- Architect-validated implementation

The system is production-ready for autoscale deployment and optimized for Replit's cloud environment.