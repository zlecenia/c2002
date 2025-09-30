# Fleet Management System

## Overview
The Fleet Management System is a comprehensive enterprise application designed for testing device masks and managing fleet operations, based on Polish technical specifications. It aims to provide a full-featured solution for various roles involved in fleet management, from device testing to software and configuration management. The system is built with a focus on scalability and robust data handling.

## User Preferences
I prefer iterative development with clear, concise explanations at each step. Please ask for confirmation before implementing significant changes or architectural shifts. I value code readability and maintainability, so prioritize clean code and well-structured solutions. For any UI/UX suggestions, please provide mockups or detailed descriptions before implementation.

## System Architecture
The system is composed of a Python FastAPI backend running on port 5000, a PostgreSQL database, and multiple specialized web GUI modules for the frontend.

**UI/UX Decisions:**
- **Consistent Layout**: A 3-column layout (15% sidebar + 70% main content + 15% right sidebar for login/role switcher) is used across all modules.
- **Global Navigation**: A unified top navigation bar allows seamless switching between modules.
- **Responsive Design**: The application is designed to be fully responsive, adapting to mobile devices with sidebars stacking vertically and content re-flowing.
- **Visual JSON Editors**: Interactive visual tree editors replace textarea-based JSON inputs across the system for improved user experience and error prevention.
- **Module Theming**: Each module has a color-coded theme.
- **Connect Display**: A dedicated module for LCD IPS 7.9" (1280×400px) touchscreen devices.

**Technical Implementations:**
- **Backend**: Python FastAPI with SQLAlchemy ORM.
- **Authentication**: JWT tokens for session management and QR code login. Includes multi-role authentication with an `/api/v1/auth/switch-role` endpoint.
- **Authorization**: Role-based access control (RBAC) with 6 distinct roles: operator, admin, superuser, manager, configurator, maker.
- **API**: A comprehensive REST API with over 50 endpoints, documented with OpenAPI 3.1.
- **Frontend**: Specialized webGUI modules built with HTML, CSS, and JavaScript. Utilizes URL hash tracking for navigation within multi-tab modules.
- **CRUD Operations**: Full Create, Read, Update, Delete functionality implemented across all modules, with user-friendly Polish language feedback and automatic list refreshes.

**Feature Specifications:**
- **Seven WebGUI Modules**: Connect++, Connect Display, Connect Manager, Fleet Data Manager, Fleet Config Manager, Fleet Software Manager, and Fleet Workshop Manager.
- **Test API Sections**: Integrated into the right column of Fleet Data Manager, Fleet Config Manager, and Connect++.
- **JSON Templates System**: CRUD operations for JSON templates with filtering by type and category, integrated with visual editors.
- **Comprehensive Documentation**: Includes `USERS.md`, `README.md`, `CHANGELOG.md`, `TODO.md`, `Dockerfile`, `docker-compose.yml`, `docs/ARCHITECTURE.md`, `docs/API.md`, and `docs/DATABASE.md`.
- **Professional Landing Page**: A responsive HTML landing page for the root endpoint.

**System Design Choices:**
- **Modular Architecture**: The system is divided into distinct modules, each catering to specific functionalities and user roles.
- **Database Schema**: PostgreSQL with 14 tables, supporting complex relationships and JSON fields.
- **Deployment**: Production-ready autoscale configuration, optimized for Replit's cloud environment.

## External Dependencies
- **PostgreSQL**: Relational database for persistent data storage.
- **FastAPI**: Python web framework for building the backend API.
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper.
- **JWT (JSON Web Tokens)**: For secure authentication and session management.
- **Swagger UI**: For interactive API documentation (via OpenAPI 3.1).
- **Docker/docker-compose**: For development environment setup and containerization.