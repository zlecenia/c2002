# 🏗️ Architecture Documentation - Fleet Management System

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Module Architecture](#module-architecture)
- [Authentication Flow](#authentication-flow)
- [Database Architecture](#database-architecture)
- [API Architecture](#api-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)

---

## 🎯 Overview

Fleet Management System is a comprehensive web application designed for managing device testing operations. The system follows a **modular monolithic architecture** with clear separation of concerns between frontend modules, backend API, and database layers.

### Design Principles

1. **Modularity** - 7 independent frontend modules with specialized purposes
2. **Role-Based Access Control** - 6 roles with fine-grained permissions
3. **RESTful API** - Clean, predictable API endpoints
4. **Data Integrity** - PostgreSQL with proper constraints and relationships
5. **Security First** - JWT authentication with bcrypt password hashing
6. **Responsive Design** - Mobile-first approach with breakpoints

---

## 🏛️ System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                        User Browser                        │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐           │
│  │ Connect++  │  │   Connect  │  │ Fleet Data  │  ...      │
│  │  Module    │  │   Manager  │  │  Manager    │           │
│  └─────┬──────┘  └──────┬─────┘  └──────┬──────┘           │
└────────┼────────────────┼───────────────┼──────────────────┘
         │                │               │
         │            HTTP/JSON           │
         │                │               │
┌────────▼────────────────▼───────────────▼──────────────────┐
│                    FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              REST API (50+ Endpoints)                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │   Auth   │  │  Fleet   │  │  Fleet   │  ...       │  │
│  │  │  Router  │  │   Data   │  │  Config  │            │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘            │  │
│  └───────┼─────────────┼─────────────┼──────────────────┘  │
│          │             │             │                     │
│  ┌───────▼─────────────▼─────────────▼──────────────────┐  │
│  │           Business Logic Layer                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │   Auth   │  │  Models  │  │   Core   │            │  │
│  │  │  Module  │  │ (SQLAlch)│  │  Config  │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  └───────────────────┬──────────────────────────────────┘  │
└──────────────────────┼─────────────────────────────────────┘
                       │
                  SQL Queries
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                  PostgreSQL Database                       │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌─────────┐           │
│  │ Users  │  │Devices │  │Software│  │Templates│  ...      │
│  └────────┘  └────────┘  └────────┘  └─────────┘           │
└────────────────────────────────────────────────────────────┘
```

### Component Interaction

1. **User Browser** - Frontend modules rendered as HTML pages with JavaScript
2. **FastAPI Backend** - Python application serving both HTML and REST API
3. **PostgreSQL Database** - Data persistence layer with 14 tables

---

## 🔧 Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0+
- **Database:** PostgreSQL 15+
- **Authentication:** python-jose (JWT), passlib (bcrypt)
- **Server:** Uvicorn (ASGI)
- **Language:** Python 3.11+

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Flexbox, Grid, @media queries
- **JavaScript (ES6+)** - Native JavaScript, no frameworks
- **JSON Tree Editor** - Custom `JSONTreeEditor` class

### Database
- **PostgreSQL 15** - Primary database
- **JSON columns** - For flexible data (roles, contact_info, test_flow)
- **Relations** - Foreign keys with proper constraints

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container setup
- **Replit** - Cloud deployment (Autoscale)

---

## 📦 Module Architecture

### Modular Architecture (New in 2025-09-30)

The system is transitioning to a **modular architecture pattern** for better code organization and maintainability.

#### Directory Structure

```
modules/
├── common/              # Shared components across all modules
│   ├── static/
│   │   ├── css/
│   │   │   └── common.css        (465 lines - 3-column layout, navigation, auth UI)
│   │   └── js/
│   │       ├── auth.js           (193 lines - JWT authentication, role switching)
│   │       └── utils.js          (88 lines - API calls, error handling)
│   ├── templates/
│   │   └── base_layout.html      (Base template for modules)
│   └── __init__.py
├── cpp/                # Connect++ module (Operator)
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
├── cd/                 # Connect Display module (LCD 7.9")
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
├── cm/                 # Connect Manager module (Superuser)
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
├── fdm/                # Fleet Data Manager (Manager)
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
├── fcm/                # Fleet Config Manager (Configurator)
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
├── fsm/                # Fleet Software Manager (Maker) - PILOT MODULE
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   │   ├── index.html            (Modular FSM page)
│   │   ├── fsm.css               (Module-specific styles)
│   │   └── fsm.js                (Module-specific logic)
│   └── __init__.py
├── fwm/                # Fleet Workshop Manager
│   ├── api/
│   ├── backend/
│   ├── frontend/
│   └── __init__.py
└── __init__.py
```

#### Pilot Implementation: Fleet Software Manager

**Status:** Modular FSM is fully functional as a pilot demonstration

**Endpoint:** `/fsm-modular`

**Features:**
- 3-column responsive layout (15% left sidebar + 70% main content + 15% right sidebar)
- Top navigation menu with all modules
- Dashboard with 4 statistic cards
- Software management (CRUD operations)
- API test section in right column
- Shared CSS/JS from `modules/common/`
- Module-specific CSS/JS from `modules/fsm/frontend/`

**Static Files Mounting:**
```python
app.mount("/modules", StaticFiles(directory="modules"), name="modules")
```

**URL Pattern:**
- Common CSS: `/modules/common/static/css/common.css`
- Common JS: `/modules/common/static/js/auth.js`, `/modules/common/static/js/utils.js`
- Module CSS: `/modules/fsm/frontend/fsm.css`
- Module JS: `/modules/fsm/frontend/fsm.js`

#### Common Components

**common.css (465 lines)**
- Global variables and reset styles
- 3-column layout system (`.container`, `.left-sidebar`, `.main-content`, `.right-sidebar`)
- Top navigation bar (`.nav-menu`)
- Authentication UI components
- Card system for dashboards
- Button styles and form controls
- Responsive breakpoints for mobile devices

**auth.js (193 lines)**
- JWT token management (`getAuthToken()`, `setAuthToken()`, `clearAuthToken()`)
- User authentication (`login()`, `logout()`)
- Role switching functionality (`switchRole()`)
- Auth state management (`checkAuthState()`)
- Current user retrieval (`getCurrentUser()`)

**utils.js (88 lines)**
- API request helper (`apiRequest()`)
- Error handling and display
- Response formatting
- Common utility functions

#### Migration Status

**Completed:**
- ✅ Common components infrastructure (`modules/common/`)
- ✅ Pilot modular FSM (`modules/fsm/`)
- ✅ Static file mounting (`/modules`)
- ✅ Module registry pattern (prepared for all 7 modules)

**Pending:**
- 🔄 Connect++ migration
- 🔄 Connect Display migration
- 🔄 Connect Manager migration
- 🔄 Fleet Data Manager migration
- 🔄 Fleet Config Manager migration
- 🔄 Fleet Workshop Manager migration

**Legacy:**
- Existing modules remain in `main.py` (6784 lines) until migration

---

The system consists of 7 independent frontend modules, each with specific responsibilities:

### 1. Connect++ (Operator Module)

**Purpose:** Simple device testing interface for operators

```
┌─────────────────────────────────────────┐
│         Connect++ Module                │
│  ┌───────────────────────────────────┐  │
│  │  Sidebar (15%)                    │  │
│  │  - Login form                     │  │
│  │  - Navigation menu                │  │
│  │  - Role switcher (maker1)         │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Content Area (85%)               │  │
│  │  - API endpoint buttons           │  │
│  │  - Response display               │  │
│  │  - Simple testing interface       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Features:**
- Test API endpoints (users, devices, customers, scenarios)
- Simple click-to-test interface
- Real-time response display

### 2. Connect Manager (Superuser Module)

**Purpose:** Test scenario management with visual JSON editor

```
┌─────────────────────────────────────────┐
│      Connect Manager Module            │
│  ┌───────────────────────────────────┐  │
│  │  Sidebar (15%)                    │  │
│  │  - Login/logout                   │  │
│  │  - Navigation:                    │  │
│  │    • Scenariusze                  │  │
│  │    • Szablony JSON                │  │
│  │  - Role switcher                  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Content Area (85%)               │  │
│  │  - Scenarios table (CRUD)         │  │
│  │  - Visual JSON editor for         │  │
│  │    test_flow configuration        │  │
│  │  - Template selection & auto-fill │  │
│  │  - Filtered by device type        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Features:**
- CRUD operations for test scenarios
- Visual JSON tree editor (no manual JSON syntax)
- JSON template integration
- Device type filtering

### 3. Fleet Data Manager (Manager Module)

**Purpose:** Manage devices and customers with visual editors

```
┌─────────────────────────────────────────┐
│      Fleet Data Manager Module          │
│  ┌───────────────────────────────────┐  │
│  │  Sidebar (15%)                    │  │
│  │  - Login/logout                   │  │
│  │  - Tabs:                          │  │
│  │    • Dashboard                    │  │
│  │    • Urządzenia                   │  │
│  │    • Klienci                      │  │
│  │  - Role switcher                  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Content Area (85%)               │  │
│  │  Tab 1: Dashboard with stats      │  │
│  │  Tab 2: Devices (CRUD + filters)  │  │
│  │  Tab 3: Customers (CRUD)          │  │
│  │    - Visual JSON editor for       │  │
│  │      contact_info field           │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Features:**
- Device management (CRUD)
- Customer management (CRUD)
- Visual JSON editor for contact_info
- Device filtering (type, status, customer)
- Dashboard with statistics

### 4. Fleet Config Manager (Configurator Module)

**Purpose:** System configuration with backup/restore

```
┌─────────────────────────────────────────┐
│    Fleet Config Manager Module          │
│  ┌───────────────────────────────────┐  │
│  │  Sidebar (15%)                    │  │
│  │  - Login/logout                   │  │
│  │  - Tabs (5 total):                │  │
│  │    • Konfiguracja systemu         │  │
│  │    • Konfiguracja urządzeń        │  │
│  │    • Scenariusze testowe          │  │
│  │    • Szablony JSON                │  │
│  │    • Backup/Restore               │  │
│  │  - Role switcher                  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Content Area (85%)               │  │
│  │  - 3 Visual JSON editors:         │  │
│  │    1. System config value         │  │
│  │    2. Test scenario params        │  │
│  │    3. Backup/restore data         │  │
│  │  - JSON templates (CRUD)          │  │
│  │  - Backup/restore functionality   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Features:**
- System configuration management
- Device configuration management
- JSON templates with filtering
- Visual JSON editors (3 locations)
- Backup and restore with JSON editor

### 5. Fleet Software Manager (Maker Module)

**Purpose:** Software package and version management

```
┌─────────────────────────────────────────┐
│   Fleet Software Manager Module         │
│  ┌───────────────────────────────────┐  │
│  │  Sidebar (15%)                    │  │
│  │  - Login/logout                   │  │
│  │  - Sections:                      │  │
│  │    • Dashboard                    │  │
│  │    • Oprogramowanie               │  │
│  │    • Wersje                       │  │
│  │    • Instalacje                   │  │
│  │  - Role switcher                  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Content Area (85%)               │  │
│  │  - Dashboard with stats           │  │
│  │  - Software packages (CRUD)       │  │
│  │  - Version management             │  │
│  │  - Installation tracking          │  │
│  │  - Scroll-to-section navigation   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Key Features:**
- Software package management (CRUD)
- Version management per package
- Installation tracking and history
- Dashboard with statistics
- Sidebar scroll navigation

---

## 🔐 Authentication Flow

### Login Flow

```
┌─────────┐                   ┌─────────┐                 ┌──────────┐
│  User   │                   │ FastAPI │                 │PostgreSQL│
└────┬────┘                   └────┬────┘                 └────┬─────┘
     │                             │                           │
     │ 1. POST /api/v1/auth/login  │                           │
     │    {username, password}     │                           │
     ├────────────────────────────>│                           │
     │                             │ 2. Verify user exists     │
     │                             ├──────────────────────────>│
     │                             │<──────────────────────────┤
     │                             │ 3. User data + password   │
     │                             │                           │
     │                             │ 4. Verify password        │
     │                             │    (bcrypt)               │
     │                             │                           │
     │                             │ 5. Generate JWT token     │
     │                             │    (includes roles)       │
     │                             │                           │
     │ 6. Return JWT + user info   │                           │
     │<────────────────────────────┤                           │
     │                             │                           │
     │ 7. Store JWT in localStorage│                           │
     │                             │                           │
     │ 8. Redirect to module       │                           │
     │                             │                           │
```

### Role Switching Flow (maker1 only)

```
┌─────────┐                   ┌─────────┐                 ┌──────────┐
│  maker1 │                   │ FastAPI │                 │PostgreSQL│
└────┬────┘                   └────┬────┘                 └────┬─────┘
     │                             │                           │
     │ 1. POST /api/v1/auth/       │                           │
     │    switch-role              │                           │
     │    {new_role: "manager"}    │                           │
     │    Authorization: Bearer JWT│                           │
     ├────────────────────────────>│                           │
     │                             │ 2. Verify JWT token       │
     │                             │                           │
     │                             │ 3. Extract user from JWT  │
     │                             │                           │
     │                             │ 4. Check if user has      │
     │                             │    new_role in roles[]    │
     │                             ├──────────────────────────>│
     │                             │<──────────────────────────┤
     │                             │ 5. Roles array            │
     │                             │                           │
     │                             │ 6. Generate new JWT       │
     │                             │    with active_role set   │
     │                             │                           │
     │ 7. Return new JWT + user    │                           │
     │    with updated active_role │                           │
     │<────────────────────────────┤                           │
     │                             │                           │
     │ 8. Update localStorage      │                           │
     │                             │                           │
     │ 9. Refresh current module   │                           │
     │                             │                           │
```

### JWT Token Structure

```json
{
  "sub": "maker1",
  "username": "maker1",
  "role": "maker",
  "active_role": "manager",
  "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
  "exp": 1735589732,
  "iat": 1735587932
}
```

---

## 💾 Database Architecture

See [DATABASE.md](DATABASE.md) for detailed database documentation.

### Key Relationships

```
users (1) ───< (N) devices (via created_by)
customers (1) ───< (N) devices (via customer_id)
software (1) ───< (N) software_versions
software_versions (1) ───< (N) software_installations
devices (1) ───< (N) software_installations
test_scenarios (1) ───< (N) test_scenario_steps
devices (1) ───< (N) test_reports
test_scenarios (1) ───< (N) test_reports
devices (1) ───< (N) device_configurations
```

---

## 🌐 API Architecture

See [API.md](API.md) for detailed API documentation.

### API Design Principles

1. **RESTful conventions** - Standard HTTP methods (GET, POST, PUT, DELETE)
2. **Versioned endpoints** - `/api/v1/...` for future compatibility
3. **Consistent responses** - Standard JSON response format
4. **JWT authentication** - Bearer token in Authorization header
5. **Role-based authorization** - Check active_role for permissions

### API Groups

```
/api/v1/
├── auth/                    # Authentication endpoints
│   ├── login               # POST - Username/password login
│   ├── login/qr            # POST - QR code login
│   ├── switch-role         # POST - Role switching
│   └── me                  # GET - Current user info
│
├── fleet-data/             # Fleet Data Manager (manager)
│   ├── devices             # GET/POST - List/create devices
│   ├── devices/{id}        # GET/PUT/DELETE - Device operations
│   ├── customers           # GET/POST - List/create customers
│   ├── customers/{id}      # GET/PUT/DELETE - Customer operations
│   └── dashboard           # GET - Dashboard statistics
│
├── fleet-config/           # Fleet Config Manager (configurator)
│   ├── system-configs      # GET/POST/PUT/DELETE - System configs
│   ├── device-configs      # GET/POST/PUT/DELETE - Device configs
│   ├── json-templates      # GET/POST/PUT/DELETE - JSON templates
│   ├── test-scenario-configs  # GET - Test scenario configs
│   ├── backup              # POST - Create backup
│   └── restore             # POST - Restore from backup
│
├── fleet-software/         # Fleet Software Manager (maker)
│   ├── software            # GET/POST/PUT/DELETE - Software packages
│   ├── software/{id}/versions  # GET/POST - Version management
│   ├── installations       # GET/POST - Installation tracking
│   └── dashboard/stats     # GET - Software statistics
│
└── scenarios/              # Connect Manager (superuser)
    ├── /                   # GET/POST - List/create scenarios
    ├── /{id}               # GET/PUT/DELETE - Scenario operations
    └── /{id}/steps         # GET/POST - Scenario steps
```

---

## 🎨 Frontend Architecture

### Shared UI Components

All 5 modules share a consistent layout structure:

#### Sidebar (15% width)

```html
<div class="sidebar">
  <div class="sidebar-header">
    <h1>Module Title</h1>
  </div>
  
  <!-- Login Section (shown when not authenticated) -->
  <div class="login-section">
    <input id="login-username" />
    <input id="login-password" type="password" />
    <button onclick="login()">Zaloguj</button>
  </div>
  
  <!-- Auth Info (shown when authenticated) -->
  <div class="auth-section">
    <p id="auth-message">Zalogowany: <span id="auth-username"></span></p>
    <button onclick="logout()">Wyloguj</button>
  </div>
  
  <!-- Role Switcher (maker1 only) -->
  <div class="role-switcher">
    <label>🔄 Przełącz rolę:</label>
    <select id="role-select" onchange="switchRole()">
      <option value="maker">Maker</option>
      <option value="operator">Operator</option>
      ...
    </select>
  </div>
  
  <!-- Navigation Menu -->
  <nav class="sidebar-nav">
    <a href="#tab1" onclick="showTab('tab1')">Tab 1</a>
    <a href="#tab2" onclick="showTab('tab2')">Tab 2</a>
    ...
  </nav>
</div>
```

#### Content Area (85% width)

```html
<div class="content">
  <div id="tab1" class="tab-content active">
    <!-- Tab 1 content -->
  </div>
  <div id="tab2" class="tab-content">
    <!-- Tab 2 content -->
  </div>
  ...
</div>
```

### JSONTreeEditor Class

Reusable JavaScript class for visual JSON editing:

```javascript
class JSONTreeEditor {
  constructor(containerId, initialData = {}) {
    this.container = document.getElementById(containerId);
    this.data = initialData;
    this.render();
  }
  
  render() {
    // Render interactive tree with:
    // - Type-specific inputs (text, number, checkbox)
    // - Add/remove field buttons
    // - Nested object/array support
    // - JSON preview toggle
  }
  
  getData() {
    // Return current JSON data
  }
  
  reset(newData = {}) {
    // Reset editor to new data
  }
}
```

---

## 🔒 Security Architecture

### Authentication

1. **Password Hashing** - bcrypt with salt
2. **JWT Tokens** - HS256 algorithm with 30-minute expiration
3. **Secure Storage** - Tokens stored in localStorage (client-side)

### Authorization

1. **Role-Based Access Control (RBAC)** - 6 roles with specific permissions
2. **JWT Verification** - Every API call validates JWT token
3. **Active Role Check** - API endpoints check active_role field

### Security Best Practices

1. **No plaintext passwords** - All passwords hashed with bcrypt
2. **CORS configuration** - Restrict allowed origins in production
3. **SQL injection prevention** - SQLAlchemy ORM with parameterized queries
4. **XSS prevention** - Input sanitization in frontend
5. **HTTPS recommended** - Use reverse proxy (nginx/caddy) for SSL

---

## 🚀 Deployment Architecture

### Replit Autoscale (Production)

```
User Request
    ↓
Replit Edge Network (CDN)
    ↓
Load Balancer
    ↓
Fleet Management Container (Autoscale)
    ↓
PostgreSQL Database (Neon-backed)
```

### Docker Compose (Development)

```
Docker Host
├── fleet_management_api (Python FastAPI)
│   ├── Port: 5000
│   ├── Depends on: db
│   └── Volumes: ./logs, ./backend, ./main.py
│
└── fleet_management_db (PostgreSQL 15)
    ├── Port: 5432
    └── Volume: postgres_data
```

### Scaling Strategy

1. **Horizontal Scaling** - Multiple API containers behind load balancer
2. **Database Connection Pooling** - SQLAlchemy connection pool
3. **Stateless API** - JWT tokens enable stateless authentication
4. **CDN for static assets** - Offload static files to CDN

---

## 📊 Performance Considerations

### Database Optimization

1. **Indexes** - Primary keys and foreign keys indexed
2. **Connection Pooling** - SQLAlchemy pool (5-20 connections)
3. **Query Optimization** - Eager loading for related data

### API Performance

1. **Response caching** - Cache frequently accessed data
2. **Pagination** - Limit large result sets
3. **Async operations** - FastAPI async/await support

### Frontend Performance

1. **Lazy loading** - Load data on demand
2. **Debouncing** - Delay API calls on user input
3. **Local storage** - Cache JWT tokens and user data

---

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JWT Standard (RFC 7519)](https://datatracker.ietf.org/doc/html/rfc7519)

---

**Last Updated:** September 30, 2025  
**Version:** 1.0.0
