# Fleet Management System

## Overview
Comprehensive Fleet Management System based on Polish technical specifications, transformed from minimal GitHub repository (https://github.com/zlecenia/02) into a full-featured enterprise application for testing device masks and fleet operations.

## Recent Changes
- **September 29, 2025**: Complete Fleet Management System implementation
  - Built from scratch: Python FastAPI + PostgreSQL + JWT authentication
  - Implemented Connect++ module for operators with web interface
  - Created comprehensive REST API with 30+ endpoints
  - Added QR code authentication system
  - Configured role-based access control (operator, admin, superuser)
  - Set up deployment configuration for production autoscale

## Project Architecture
- **Backend**: Python FastAPI with SQLAlchemy ORM running on port 5000
- **Database**: PostgreSQL with 9 tables (Users, Devices, Customers, Test Scenarios, etc.)
- **Authentication**: JWT tokens + QR code login system
- **API**: REST API with OpenAPI 3.1 documentation
- **Frontend**: Connect++ Module - HTML/CSS/JS interface for operators
- **Deployment**: Production-ready autoscale configuration

## Key Features
- JWT + QR code authentication system
- Role-based access control (operator/admin/superuser roles)
- Connect++ module for device testing operations
- Comprehensive CRUD API with 30+ endpoints
- PostgreSQL database with full relational schema
- OpenAPI documentation with Swagger UI
- Production deployment configuration

## Modules Implemented
1. **Connect++** (`/connect-plus`) - Operator interface for device testing
2. **API Documentation** (`/docs`) - Complete Swagger documentation  
3. **Authentication System** - JWT + QR code login endpoints
4. **User Management** - CRUD operations with role protection

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

## API Endpoints
- `POST /api/v1/auth/login` - Username/password authentication
- `POST /api/v1/auth/login/qr` - QR code authentication  
- `GET /api/v1/auth/me` - Current user information
- `GET /api/v1/users/` - User management (admin protected)
- `GET /api/v1/devices` - Device listing
- `GET /api/v1/customers` - Customer management
- `GET /api/v1/test-scenarios` - Test scenario management

## Current State
The Fleet Management System is fully functional and ready for production deployment. All core components work end-to-end: authentication, database operations, API endpoints, and the Connect++ operator interface. The system is configured for autoscale deployment and optimized for Replit's cloud environment.