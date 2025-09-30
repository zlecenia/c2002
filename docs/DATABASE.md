# 💾 Database Documentation - Fleet Management System

## 📋 Table of Contents

- [Overview](#overview)
- [Database Schema](#database-schema)
- [Core Tables](#core-tables)
- [Relationships](#relationships)
- [JSON Fields](#json-fields)
- [Backup & Restore](#backup--restore)

---

## 🎯 Overview

Fleet Management System uses **PostgreSQL 15** with **SQLAlchemy 2.0** ORM.

### Database Characteristics

- **RDBMS:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Automatic table creation via SQLAlchemy
- **Connection Pooling:** 5-20 connections
- **JSON Support:** Native JSON columns

### Connection String

```
postgresql://username:password@host:port/database
```

**Development Example:**
```
postgresql://fleetuser:fleetpass@localhost:5432/fleet_management
```

---

## 🗃️ Database Schema

The system consists of **14 tables**:

### User Management
- **`users`** - User accounts with authentication and multi-role support

### Fleet Data
- **`customers`** - Customer information with JSON contact details
- **`devices`** - Device inventory with status tracking

### Software Management
- **`software`** - Software packages catalog
- **`software_versions`** - Version history per package
- **`software_installations`** - Installation tracking and history
- **`device_software`** - Device-software mapping table

### Configuration
- **`configurations`** - System and device configuration settings
- **`json_templates`** - Reusable JSON configuration templates
- **`translations`** - Multi-language translation keys

### Testing
- **`test_scenarios`** - Test scenario definitions with JSON test_flow
- **`test_steps`** - Individual test steps (legacy, now using JSON)
- **`test_reports`** - Test execution results

### System
- **`system_logs`** - System activity and audit logs

---

## 📊 Core Tables

### users

User accounts with multi-role authentication system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | User ID |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Username for login |
| email | VARCHAR(255) | UNIQUE | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| role | VARCHAR(50) | NOT NULL | Primary role (backward compat) |
| **roles** | **JSON** | - | **Array of all user roles** |
| qr_code | VARCHAR(255) | UNIQUE | QR code for quick login |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update time |

**Key Feature:** `roles` JSON field allows multi-role users like maker1 with all 6 roles.

**Example:**
```json
{
  "username": "maker1",
  "roles": ["maker", "operator", "admin", "superuser", "manager", "configurator"]
}
```

---

### customers

Customer information with flexible JSON contact details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Customer ID |
| name | VARCHAR(255) | NOT NULL | Customer name |
| **contact_info** | **JSON** | - | **Contact details (flexible structure)** |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

**contact_info Structure:**
```json
{
  "phone": "+48 123 456 789",
  "email": "contact@example.com",
  "address": "Warsaw, Poland",
  "company": "Example Corp",
  "notes": "VIP customer"
}
```

**Relationships:**
- `customers` (1) → (N) `devices`
- `customers` (1) → (N) `test_reports`

---

### devices

Device inventory with status tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Device ID |
| **device_number** | VARCHAR(100) | UNIQUE, NOT NULL | **Device number (unique identifier)** |
| device_type | VARCHAR(100) | NOT NULL | Type (mask_tester, pressure_sensor, etc.) |
| kind_of_device | VARCHAR(100) | - | Device kind/category |
| serial_number | VARCHAR(100) | - | Manufacturer serial number |
| status | VARCHAR(50) | DEFAULT 'active' | Status (active, inactive, maintenance) |
| customer_id | INTEGER | FOREIGN KEY | Assigned customer |
| **configuration** | **JSON** | - | **Device-specific configuration** |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update time |

**Device Types:**
- `mask_tester` - Mask testing equipment
- `pressure_sensor` - Pressure measurement
- `flow_meter` - Flow measurement
- `temperature_sensor` - Temperature measurement
- `humidity_sensor` - Humidity measurement

**Relationships:**
- `devices` (N) → (1) `customers`
- `devices` (1) → (N) `test_reports`
- `devices` (1) → (N) `device_software`
- `devices` (1) → (N) `software_installations`

---

### software

Software packages catalog.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Software ID |
| name | VARCHAR(255) | NOT NULL | Software name |
| description | TEXT | - | Description |
| vendor | VARCHAR(255) | - | Vendor/manufacturer |
| category | VARCHAR(100) | - | Category (firmware, application, driver, tool) |
| platform | VARCHAR(100) | - | Platform compatibility |
| license_type | VARCHAR(100) | - | License type |
| repository_url | VARCHAR(500) | - | Repository URL |
| documentation_url | VARCHAR(500) | - | Documentation URL |
| created_by | INTEGER | FOREIGN KEY | Creator user ID |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update time |

**Relationships:**
- `software` (1) → (N) `software_versions` (CASCADE DELETE)
- `software` (1) → (N) `device_software`

---

### software_versions

Version history for software packages.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Version ID |
| software_id | INTEGER | FOREIGN KEY | Parent software |
| version_number | VARCHAR(50) | NOT NULL | Version (e.g., "2.5.0") |
| release_notes | TEXT | - | Release notes |
| changelog | TEXT | - | Changelog |
| file_path | VARCHAR(500) | - | File path |
| file_size | INTEGER | - | Size in bytes |
| checksum | VARCHAR(64) | - | SHA-256 checksum |
| download_url | VARCHAR(500) | - | Download URL |
| is_stable | BOOLEAN | DEFAULT TRUE | Stable release |
| is_beta | BOOLEAN | DEFAULT FALSE | Beta release |
| requires_reboot | BOOLEAN | DEFAULT FALSE | Requires reboot |
| **compatibility** | **JSON** | - | **Device compatibility info** |
| created_by | INTEGER | FOREIGN KEY | Creator user ID |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| released_at | TIMESTAMP | - | Release date |

**Cascading Delete:** When software is deleted, all versions are automatically deleted.

**Relationships:**
- `software_versions` (N) → (1) `software`
- `software_versions` (1) → (N) `software_installations`

---

### software_installations

Installation tracking and history.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Installation ID |
| device_id | INTEGER | FOREIGN KEY | Target device |
| version_id | INTEGER | FOREIGN KEY | Installed version |
| action | VARCHAR(50) | NOT NULL | Action (install, update, uninstall, rollback) |
| status | VARCHAR(50) | DEFAULT 'pending' | Status (pending, in_progress, completed, failed) |
| initiated_by | INTEGER | FOREIGN KEY | Initiator user ID |
| started_at | TIMESTAMP | DEFAULT NOW() | Start time |
| completed_at | TIMESTAMP | - | Completion time |
| error_message | TEXT | - | Error message if failed |
| installation_log | TEXT | - | Installation log |
| previous_version | VARCHAR(50) | - | Previous version |
| new_version | VARCHAR(50) | - | New version |
| **rollback_point** | **JSON** | - | **Rollback data** |

**Relationships:**
- `software_installations` (N) → (1) `devices`
- `software_installations` (N) → (1) `software_versions`
- `software_installations` (N) → (1) `users` (initiator)

---

### device_software

Device-software mapping table (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Mapping ID |
| device_id | INTEGER | FOREIGN KEY | Device |
| software_id | INTEGER | FOREIGN KEY | Software |
| version_id | INTEGER | FOREIGN KEY | Installed version |
| installed_version | VARCHAR(50) | - | Version string |
| installation_status | VARCHAR(50) | DEFAULT 'not_installed' | Status |
| installation_date | TIMESTAMP | - | Installation date |
| last_updated | TIMESTAMP | ON UPDATE NOW() | Last update |
| **configuration** | **JSON** | - | **Software-specific config** |
| notes | TEXT | - | Notes |

**Installation Status:**
- `not_installed` - Not installed
- `installing` - Installation in progress
- `installed` - Installed successfully
- `failed` - Installation failed
- `outdated` - Outdated version

---

### configurations

System and device configuration settings (unified table).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Config ID |
| config_key | VARCHAR(100) | UNIQUE, NOT NULL | Configuration key |
| **config_value** | **JSON** | NOT NULL | **Configuration value** |
| component | VARCHAR(50) | - | Component (CPP, CM, FDM, FCM, FSM) |
| updated_by | INTEGER | FOREIGN KEY | Last updater |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Component Values:**
- `CPP` - Connect++
- `CM` - Connect Manager
- `FDM` - Fleet Data Manager
- `FCM` - Fleet Config Manager
- `FSM` - Fleet Software Manager

**Example:**
```json
{
  "config_key": "api_timeout",
  "config_value": {
    "timeout": 30,
    "retry": 3
  },
  "component": "FDM"
}
```

---

### json_templates

Reusable JSON configuration templates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Template ID |
| name | VARCHAR(255) | NOT NULL | Template name |
| template_type | VARCHAR(100) | NOT NULL | Type (scenario, test_flow, device_config, etc.) |
| category | VARCHAR(100) | - | Category (mask_tester, pressure_sensor, etc.) |
| **schema** | **JSON** | NOT NULL | **JSON schema definition** |
| **default_values** | **JSON** | NOT NULL | **Default JSON values** |
| description | TEXT | - | Description |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_by | INTEGER | FOREIGN KEY | Creator user ID |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update time |

**Template Types:**
- `test_flow` - Test flow configuration
- `device_config` - Device configuration
- `software_config` - Software configuration
- `scenario` - Test scenario

**Example:**
```sql
INSERT INTO json_templates (name, template_type, category, schema, default_values) VALUES
  ('Mask Tester Flow', 'test_flow', 'mask_tester', 
   '{}'::json,
   '{"test_pressure": 100, "test_duration": 60, "calibration_enabled": true}'::json);
```

---

### test_scenarios

Test scenario definitions with JSON test flow.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Scenario ID |
| name | VARCHAR(255) | NOT NULL | Scenario name |
| description | TEXT | - | Description |
| device_type | VARCHAR(100) | - | Target device type |
| **test_flow** | **JSON** | - | **Test flow structure** |
| created_by | INTEGER | FOREIGN KEY | Creator user ID |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update time |

**test_flow Structure:**
```json
{
  "steps": [
    {
      "step": 1,
      "action": "initialize",
      "params": {}
    },
    {
      "step": 2,
      "action": "calibrate",
      "params": {"pressure": 100}
    },
    {
      "step": 3,
      "action": "test",
      "params": {"duration": 60}
    }
  ]
}
```

**Relationships:**
- `test_scenarios` (1) → (N) `test_steps`
- `test_scenarios` (1) → (N) `test_reports`

---

### test_steps

Individual test steps (legacy table, now using test_flow JSON).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Step ID |
| scenario_id | INTEGER | FOREIGN KEY | Parent scenario |
| step_order | INTEGER | NOT NULL | Step order |
| step_name | VARCHAR(255) | NOT NULL | Step name |
| description | TEXT | - | Description |
| **parameters** | **JSON** | - | **Step parameters** |
| **criteria** | **JSON** | - | **Success criteria** |
| auto_test | BOOLEAN | DEFAULT FALSE | Automated test |
| operator_participation | BOOLEAN | DEFAULT TRUE | Requires operator |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

**Note:** This table is legacy. New scenarios use `test_flow` JSON field in `test_scenarios` table.

---

### test_reports

Test execution results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Report ID |
| test_scenario_id | INTEGER | FOREIGN KEY | Test scenario |
| device_id | INTEGER | FOREIGN KEY | Tested device |
| operator_id | INTEGER | FOREIGN KEY | Operator user |
| customer_id | INTEGER | FOREIGN KEY | Customer |
| start_time | TIMESTAMP | NOT NULL | Test start time |
| end_time | TIMESTAMP | - | Test end time |
| status | VARCHAR(50) | - | Status (pending, in_progress, completed, failed) |
| **results** | **JSON** | - | **Test results** |
| **pressure_data** | **JSON** | - | **Pressure measurement data** |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

**Relationships:**
- `test_reports` (N) → (1) `test_scenarios`
- `test_reports` (N) → (1) `devices`
- `test_reports` (N) → (1) `users` (operator)
- `test_reports` (N) → (1) `customers`

---

### system_logs

System activity and audit logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Log ID |
| log_level | VARCHAR(50) | - | Level (INFO, WARNING, ERROR, HELP) |
| user_id | INTEGER | FOREIGN KEY | Related user |
| action | VARCHAR(255) | - | Action performed |
| **details** | **JSON** | - | **Additional details** |
| ip_address | VARCHAR(45) | - | IP address |
| timestamp | TIMESTAMP | DEFAULT NOW() | Log timestamp |

**Relationships:**
- `system_logs` (N) → (1) `users`

---

### translations

Multi-language translation keys (future feature).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Translation ID |
| key | VARCHAR(255) | NOT NULL | Translation key |
| language | VARCHAR(10) | NOT NULL | Language code (en, pl, etc.) |
| value | TEXT | NOT NULL | Translated text |
| component | VARCHAR(50) | - | Component (CPP, CM, FDM, etc.) |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

---

## 🔗 Relationships

### Entity-Relationship Diagram

```
users (1) ───< (N) test_scenarios [created_by]
users (1) ───< (N) software [created_by]
users (1) ───< (N) software_versions [created_by]
users (1) ───< (N) software_installations [initiated_by]
users (1) ───< (N) test_reports [operator_id]
users (1) ───< (N) system_logs [user_id]
users (1) ───< (N) json_templates [created_by]
users (1) ───< (N) configurations [updated_by]

customers (1) ───< (N) devices [customer_id]
customers (1) ───< (N) test_reports [customer_id]

devices (1) ───< (N) device_software [device_id]
devices (1) ───< (N) software_installations [device_id]
devices (1) ───< (N) test_reports [device_id]

software (1) ───< (N) software_versions [software_id] CASCADE
software (1) ───< (N) device_software [software_id]

software_versions (1) ───< (N) software_installations [version_id]
software_versions (1) ───< (N) device_software [version_id]

test_scenarios (1) ───< (N) test_steps [scenario_id]
test_scenarios (1) ───< (N) test_reports [test_scenario_id]
```

### Cascading Deletes

- **software → software_versions**: DELETE CASCADE
  - When software is deleted, all versions are automatically deleted

---

## 📦 JSON Fields

The system uses JSON columns extensively for flexibility:

| Table | Column | Purpose | Editable via UI |
|-------|--------|---------|-----------------|
| users | roles | Multi-role array | No (code only) |
| customers | contact_info | Contact details | **Yes (visual editor)** |
| devices | configuration | Device config | No |
| software_versions | compatibility | Compatibility info | No |
| software_installations | rollback_point | Rollback data | No |
| device_software | configuration | Software config | No |
| configurations | config_value | Config data | **Yes (visual editor)** |
| json_templates | schema | JSON schema | No |
| json_templates | default_values | Template values | **Yes (visual editor)** |
| test_scenarios | test_flow | Test flow | **Yes (visual editor)** |
| test_steps | parameters | Step params | No |
| test_steps | criteria | Success criteria | No |
| test_reports | results | Test results | No |
| test_reports | pressure_data | Pressure data | No |
| system_logs | details | Log details | No |

**Visual JSON Editors:** Fleet Data Manager, Fleet Config Manager, and Connect Manager modules provide interactive tree-based JSON editors for relevant fields, eliminating manual JSON syntax errors.

---

## 💾 Backup & Restore

### Manual Backup (PostgreSQL)

```bash
# Full database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Schema only
pg_dump --schema-only $DATABASE_URL > schema.sql

# Data only
pg_dump --data-only $DATABASE_URL > data.sql
```

### Manual Restore

```bash
# Restore from backup
psql $DATABASE_URL < backup_20250930_120000.sql
```

### Application Backup

Fleet Config Manager provides backup/restore functionality via API:

```bash
# Create backup
curl -X POST http://localhost:5000/api/v1/fleet-config/backup \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backup_name": "Daily_Backup_2025-09-30", "backup_data": {...}}'

# Restore from backup
curl -X POST http://localhost:5000/api/v1/fleet-config/restore \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"restore_data": {...}}'
```

---

**Last Updated:** September 30, 2025  
**Version:** 1.0.0  
**Database Tables:** 14  
**Total API Endpoints:** 58

**Note:** This documentation reflects the actual implementation in `backend/models/models.py`. For API documentation, see [docs/API.md](API.md).
