# 📡 API Documentation - Fleet Management System

## 📋 Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Common Responses](#common-responses)
- [Authentication Endpoints](#authentication-endpoints)
- [Fleet Data Endpoints](#fleet-data-endpoints)
- [Fleet Config Endpoints](#fleet-config-endpoints)
- [Fleet Software Endpoints](#fleet-software-endpoints)
- [Test Scenarios Endpoints](#test-scenarios-endpoints)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)

---

## 🌐 Overview

The Fleet Management System API is a RESTful API built with FastAPI. It provides **58 endpoints** for managing devices, customers, software, configurations, and test scenarios.

### API Characteristics

- **Protocol:** HTTP/HTTPS
- **Data Format:** JSON
- **Authentication:** JWT Bearer Token
- **Authorization:** Role-Based Access Control (RBAC)
- **Versioning:** `/api/v1/` prefix
- **Documentation:** OpenAPI 3.1 (Swagger UI at `/docs`)

### Endpoint Count by Router

| Router | Endpoints | Description |
|--------|-----------|-------------|
| **Authentication** | 5 | Login, QR auth, role switching, user info |
| **Fleet Config** | 19 | System configs, device configs, templates, backup/restore |
| **Fleet Data** | 11 | Devices, customers, dashboard statistics |
| **Fleet Software** | 10 | Software packages, versions, installations, stats |
| **Test Scenarios** | 8 | Test scenarios CRUD operations |
| **Users** | 5 | User management operations |
| **TOTAL** | **58** | Complete REST API coverage |

---

## 🔗 Base URL

### Development
```
http://localhost:5000
```

### Production (Replit)
```
https://your-repl-name.replit.app
```

### API Version Prefix
```
/api/v1/
```

Full example:
```
http://localhost:5000/api/v1/auth/login
```

---

## 🔐 Authentication

### Authentication Methods

1. **Username/Password** - Standard login
2. **QR Code** - Quick login via QR code scan
3. **Role Switching** - Switch roles without re-login (maker1 only)

### JWT Token

After successful authentication, you receive a JWT token:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "maker1",
    "email": "maker1@fleetmanagement.com",
    "role": "maker",
    "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
    "active_role": "maker"
  }
}
```

### Using the Token

Include the JWT token in the `Authorization` header for all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- **Lifetime:** 30 minutes
- **Renewal:** Login again to get a new token
- **Error:** 401 Unauthorized when expired

---

## 📊 Common Responses

### Success Response

```json
{
  "id": 1,
  "name": "Device Name",
  "status": "active",
  "created_at": "2025-09-30T12:00:00Z"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### List Response

```json
[
  {"id": 1, "name": "Item 1"},
  {"id": 2, "name": "Item 2"}
]
```

---

## 🔑 Authentication Endpoints

### POST /api/v1/auth/login

Login with username and password.

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=maker1&password=pass
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "maker1",
    "email": "maker1@fleetmanagement.com",
    "role": "maker",
    "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
    "active_role": "maker"
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Missing username or password

---

### POST /api/v1/auth/login/qr

Login with QR code.

**Request:**
```json
POST /api/v1/auth/login/qr
Content-Type: application/json

{
  "qr_code": "QR_CODE_STRING"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "maker1",
    "email": "maker1@fleetmanagement.com",
    "role": "maker",
    "roles": ["maker"],
    "active_role": "maker"
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid QR code
- `422 Unprocessable Entity` - Missing qr_code field

---

### POST /api/v1/auth/switch-role

Switch active role (multi-role users only).

**Request:**
```json
POST /api/v1/auth/switch-role
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "new_role": "manager"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "maker1",
    "email": "maker1@fleetmanagement.com",
    "role": "maker",
    "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
    "active_role": "manager"
  }
}
```

**Errors:**
- `400 Bad Request` - User doesn't have the requested role
- `401 Unauthorized` - Invalid or expired JWT token

---

### GET /api/v1/auth/me

Get current authenticated user information.

**Request:**
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
{
  "id": 5,
  "username": "maker1",
  "email": "maker1@fleetmanagement.com",
  "role": "maker",
  "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"],
  "active_role": "manager",
  "is_active": true,
  "created_at": "2025-09-29T10:00:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired JWT token

---

## 📊 Fleet Data Endpoints

**Required Role:** `manager`

### GET /api/v1/fleet-data/devices

Get list of all devices.

**Request:**
```http
GET /api/v1/fleet-data/devices
Authorization: Bearer eyJhbGci...
```

**Query Parameters:**
- `device_type` (optional) - Filter by device type (mask_tester, pressure_sensor, etc.)
- `status` (optional) - Filter by status (active, inactive, maintenance)
- `customer_id` (optional) - Filter by customer ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "serial_number": "MT-2025-001",
    "device_type": "mask_tester",
    "status": "active",
    "customer_id": 1,
    "customer_name": "Medical Corp",
    "calibration_date": "2025-09-15",
    "last_maintenance": "2025-09-20",
    "created_at": "2025-09-01T00:00:00Z",
    "created_by": 5
  }
]
```

---

### POST /api/v1/fleet-data/devices

Create a new device.

**Request:**
```json
POST /api/v1/fleet-data/devices
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "serial_number": "MT-2025-002",
  "device_type": "mask_tester",
  "status": "active",
  "customer_id": 1,
  "calibration_date": "2025-09-30",
  "last_maintenance": "2025-09-30"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "serial_number": "MT-2025-002",
  "device_type": "mask_tester",
  "status": "active",
  "customer_id": 1,
  "calibration_date": "2025-09-30",
  "last_maintenance": "2025-09-30",
  "created_at": "2025-09-30T12:00:00Z",
  "created_by": 5
}
```

**Errors:**
- `400 Bad Request` - Duplicate serial number
- `422 Unprocessable Entity` - Invalid field values

---

### PUT /api/v1/fleet-data/devices/{id}

Update an existing device.

**Request:**
```json
PUT /api/v1/fleet-data/devices/2
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "status": "maintenance",
  "last_maintenance": "2025-09-30"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "serial_number": "MT-2025-002",
  "device_type": "mask_tester",
  "status": "maintenance",
  "customer_id": 1,
  "calibration_date": "2025-09-30",
  "last_maintenance": "2025-09-30",
  "created_at": "2025-09-30T12:00:00Z",
  "created_by": 5
}
```

**Errors:**
- `404 Not Found` - Device not found

---

### DELETE /api/v1/fleet-data/devices/{id}

Delete a device.

**Request:**
```http
DELETE /api/v1/fleet-data/devices/2
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
{
  "message": "Urządzenie usunięte pomyślnie"
}
```

**Errors:**
- `404 Not Found` - Device not found

---

### GET /api/v1/fleet-data/customers

Get list of all customers.

**Request:**
```http
GET /api/v1/fleet-data/customers
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Medical Corp",
    "contact_info": {
      "phone": "+48 123 456 789",
      "email": "contact@medicalcorp.com",
      "address": "Warsaw, Poland",
      "company": "Medical Corp Sp. z o.o.",
      "notes": "VIP customer"
    },
    "created_at": "2025-09-01T00:00:00Z"
  }
]
```

---

### POST /api/v1/fleet-data/customers

Create a new customer.

**Request:**
```json
POST /api/v1/fleet-data/customers
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "name": "Health Systems Inc",
  "contact_info": {
    "phone": "+48 987 654 321",
    "email": "info@healthsystems.com",
    "address": "Krakow, Poland",
    "company": "Health Systems Inc.",
    "notes": "New customer"
  }
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "Health Systems Inc",
  "contact_info": {
    "phone": "+48 987 654 321",
    "email": "info@healthsystems.com",
    "address": "Krakow, Poland",
    "company": "Health Systems Inc.",
    "notes": "New customer"
  },
  "created_at": "2025-09-30T12:00:00Z"
}
```

---

### GET /api/v1/fleet-data/dashboard

Get fleet dashboard statistics.

**Request:**
```http
GET /api/v1/fleet-data/dashboard
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
{
  "total_devices": 10,
  "active_devices": 8,
  "maintenance_devices": 2,
  "inactive_devices": 0,
  "total_customers": 5,
  "device_types": {
    "mask_tester": 6,
    "pressure_sensor": 3,
    "flow_meter": 1
  }
}
```

---

## 🔧 Fleet Config Endpoints

**Required Role:** `configurator`

### GET /api/v1/fleet-config/system-configs

Get all system configurations.

**Request:**
```http
GET /api/v1/fleet-config/system-configs
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "config_key": "api_timeout",
    "config_value": {"timeout": 30, "retry": 3},
    "description": "API timeout configuration",
    "created_at": "2025-09-01T00:00:00Z"
  }
]
```

---

### POST /api/v1/fleet-config/system-configs

Create a system configuration.

**Request:**
```json
POST /api/v1/fleet-config/system-configs
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "config_key": "notification_settings",
  "config_value": {
    "email_enabled": true,
    "slack_enabled": false
  },
  "description": "Notification settings"
}
```

---

### GET /api/v1/fleet-config/json-templates

Get JSON templates with filtering.

**Request:**
```http
GET /api/v1/fleet-config/json-templates?type=test_flow&category=mask_tester
Authorization: Bearer eyJhbGci...
```

**Query Parameters:**
- `type` (optional) - Filter by template type (test_flow, device_config, system_config)
- `category` (optional) - Filter by category (mask_tester, pressure_sensor, etc.)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Mask Tester Flow",
    "template_type": "test_flow",
    "category": "mask_tester",
    "default_values": {
      "test_pressure": 100,
      "test_duration": 60
    },
    "schema": {...},
    "description": "Standard mask testing flow",
    "created_at": "2025-09-01T00:00:00Z"
  }
]
```

---

### POST /api/v1/fleet-config/backup

Create configuration backup.

**Request:**
```json
POST /api/v1/fleet-config/backup
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "backup_name": "Backup_2025-09-30",
  "backup_data": {
    "system_configs": [...],
    "device_configs": [...]
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Backup utworzony pomyślnie",
  "backup_id": 1,
  "created_at": "2025-09-30T12:00:00Z"
}
```

---

## 💾 Fleet Software Endpoints

**Required Role:** `maker`

### GET /api/v1/fleet-software/software

Get all software packages.

**Request:**
```http
GET /api/v1/fleet-software/software
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Mask Tester Firmware",
    "description": "Main firmware for mask testing devices",
    "current_version": "2.5.0",
    "total_versions": 5,
    "total_installations": 12,
    "created_at": "2025-09-01T00:00:00Z"
  }
]
```

---

### GET /api/v1/fleet-software/software/{id}/versions

Get versions for a software package.

**Request:**
```http
GET /api/v1/fleet-software/software/1/versions
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
[
  {
    "id": 5,
    "software_id": 1,
    "version_number": "2.5.0",
    "release_date": "2025-09-30",
    "release_notes": "Bug fixes and performance improvements",
    "is_stable": true,
    "created_at": "2025-09-30T00:00:00Z"
  }
]
```

---

### GET /api/v1/fleet-software/dashboard/stats

Get software dashboard statistics.

**Request:**
```http
GET /api/v1/fleet-software/dashboard/stats
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
{
  "total_software": 5,
  "total_versions": 23,
  "total_installations": 45,
  "recent_releases": [
    {
      "software_name": "Mask Tester Firmware",
      "version": "2.5.0",
      "release_date": "2025-09-30"
    }
  ]
}
```

---

## 🧪 Test Scenarios Endpoints

**Required Role:** `superuser`

### GET /api/v1/scenarios/

Get all test scenarios.

**Request:**
```http
GET /api/v1/scenarios/
Authorization: Bearer eyJhbGci...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Full Mask Test",
    "device_type": "mask_tester",
    "test_flow": {
      "steps": [
        {"step": 1, "action": "calibrate"},
        {"step": 2, "action": "test_pressure"}
      ]
    },
    "created_at": "2025-09-01T00:00:00Z",
    "created_by": 1
  }
]
```

---

### POST /api/v1/scenarios/

Create a test scenario.

**Request:**
```json
POST /api/v1/scenarios/
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "name": "Quick Pressure Test",
  "device_type": "pressure_sensor",
  "test_flow": {
    "steps": [
      {"step": 1, "action": "initialize"},
      {"step": 2, "action": "measure"}
    ]
  }
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "Quick Pressure Test",
  "device_type": "pressure_sensor",
  "test_flow": {...},
  "created_at": "2025-09-30T12:00:00Z",
  "created_by": 1
}
```

---

## ❌ Error Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Invalid request data, business logic error |
| 401 | Unauthorized | Missing/invalid JWT token, expired token |
| 403 | Forbidden | Insufficient permissions for operation |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error, missing required fields |
| 500 | Internal Server Error | Server-side error (check logs) |

---

## ⏱️ Rate Limiting

**Current Status:** Not implemented

**Planned:**
- 100 requests per minute per IP
- 1000 requests per hour per JWT token
- Burst allowance: 20 requests

---

## 📚 Interactive Documentation

Visit the interactive API documentation:

**Swagger UI:** `http://localhost:5000/docs`

Features:
- Try out all endpoints
- See request/response schemas
- Copy curl commands
- OAuth2 JWT authentication

---

**Last Updated:** September 30, 2025  
**Version:** 1.0.0
