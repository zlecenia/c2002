# Fleet Management System - API Guide

## 🚀 Quick Start Guide

### Access URLs
- **Fleet Workshop Manager**: `http://nvidia:5000/fleet-workshop-manager`
- **Connect Manager**: `http://nvidia:5000/connect-manager`

### Direct Feature Access
```bash
# Workshop Management
http://nvidia:5000/fleet-workshop-manager#devices
http://nvidia:5000/fleet-workshop-manager#customers

# Configuration Management  
http://nvidia:5000/connect-manager#system-config
http://nvidia:5000/connect-manager#device-config
http://nvidia:5000/connect-manager#test-config
http://nvidia:5000/connect-manager#json-templates
```

## 🔐 Authentication

### Login Process
1. Navigate to any module URL
2. Enter credentials in the right sidebar
3. JWT token will be stored automatically
4. Role-based access will be applied

### Required Roles
- **Workshop Operations**: `maker` role
- **Configuration Management**: `configurator` role

## 📊 API Endpoints

### Fleet Workshop Manager APIs

#### Devices Management
```http
GET    /api/v1/fleet-data/devices           # List all devices
POST   /api/v1/fleet-data/devices           # Create new device
PUT    /api/v1/fleet-data/devices/{id}      # Update device
DELETE /api/v1/fleet-data/devices/{id}      # Delete device
```

**Device Data Structure:**
```json
{
  "device_number": "DEV001",        # Required
  "device_type": "mask_tester",     # Required
  "status": "active",               # Required
  "customer_id": 123                # Optional
}
```

#### Customers Management
```http
GET    /api/v1/fleet-data/customers         # List all customers
POST   /api/v1/fleet-data/customers         # Create new customer
PUT    /api/v1/fleet-data/customers/{id}    # Update customer
DELETE /api/v1/fleet-data/customers/{id}    # Delete customer
```

### Connect Manager APIs

#### System Config Management
```http
GET    /api/v1/fleet-config/system-configs           # List system configs
POST   /api/v1/fleet-config/system-configs           # Create system config
PUT    /api/v1/fleet-config/system-configs/{id}      # Update system config
DELETE /api/v1/fleet-config/system-configs/{id}      # Delete system config
```

**System Config Data Structure:**
```json
{
  "config_name": "Production Settings",
  "config_type": "system_limits",
  "config_value": {
    "max_connections": 100,
    "timeout": 30,
    "enabled": true
  },
  "description": "Production environment settings"
}
```

#### Device Config Management
```http
GET    /api/v1/fleet-config/device-configs           # List device configs
PUT    /api/v1/fleet-config/device-configs/{id}      # Update device config
```

#### Test Scenarios Management
```http
GET    /api/v1/fleet-config/test-scenario-configs    # List test scenarios
POST   /api/v1/fleet-config/test-scenario-configs    # Create test scenario
PUT    /api/v1/fleet-config/test-scenario-configs/{id}    # Update test scenario
DELETE /api/v1/fleet-config/test-scenario-configs/{id}    # Delete test scenario
```

**Test Scenario Data Structure:**
```json
{
  "scenario_name": "Mask Leak Test Standard",
  "test_type": "mask_leak_test",
  "parameters": {
    "pressure": 50,
    "duration": 300,
    "tolerance": 2
  },
  "expected_results": {
    "pass_criteria": "leak_rate < 5",
    "units": "L/min"
  }
}
```

#### JSON Templates Management
```http
GET    /api/v1/fleet-config/json-templates           # List JSON templates
POST   /api/v1/fleet-config/json-templates           # Create JSON template
PUT    /api/v1/fleet-config/json-templates/{id}      # Update JSON template
DELETE /api/v1/fleet-config/json-templates/{id}      # Delete JSON template

# With filters
GET    /api/v1/fleet-config/json-templates?template_type=test_flow
GET    /api/v1/fleet-config/json-templates?category=mask_tester
```

**JSON Template Data Structure:**
```json
{
  "name": "Standard Mask Test Template",
  "template_type": "test_flow",
  "category": "mask_tester",
  "description": "Standard template for mask testing procedures",
  "default_values": {
    "test_pressure": 50,
    "duration": 300,
    "pass_threshold": 5
  },
  "schema": {
    "type": "object",
    "properties": {
      "test_pressure": {"type": "number"},
      "duration": {"type": "number"},
      "pass_threshold": {"type": "number"}
    }
  }
}
```

## 🛠️ Frontend Features

### JSON Tree Editor
- **Visual JSON Editing**: Point-and-click JSON structure editing
- **Type Management**: String, Number, Boolean, Object, Array support
- **Field Operations**: Add, delete, rename fields dynamically
- **Preview Mode**: Real-time JSON preview

### Hash Routing
- **Direct Access**: Bookmark specific sections with URL fragments
- **Browser History**: Back/forward navigation support
- **Deep Linking**: Share direct links to specific configuration sections

### Form Management
- **Modal Forms**: Overlay forms with proper z-index management
- **Validation**: Client-side validation before API calls
- **Error Handling**: User-friendly error messages
- **Auto-refresh**: Lists automatically refresh after operations

## 🧪 Testing & Validation

### Manual Testing Checklist
```bash
# 1. Test system startup
docker-compose up -d

# 2. Test page accessibility
curl -s http://localhost:5000/connect-manager | grep -o '<title>.*</title>'

# 3. Test API connectivity (requires auth)
curl -s -X GET http://localhost:5000/api/v1/fleet-config/system-configs

# 4. Test workshop manager
curl -s http://localhost:5000/fleet-workshop-manager | grep -o '<title>.*</title>'
```

### Automated Tests
```bash
# Run FWM tests (8/8 should pass)
cd /home/tom/github/zlecenia/c2002
python -m pytest tests/test_fleet_data_manager.py -v
```

## 📚 Usage Examples

### Creating a System Configuration
1. Navigate to `http://nvidia:5000/connect-manager#system-config`
2. Click "Dodaj konfigurację"
3. Fill form:
   - **Nazwa**: "Production Limits"
   - **Typ**: "system_limits"
   - **Wartości**: Use JSON Tree Editor to add fields
   - **Opis**: Optional description
4. Click "Dodaj konfigurację"

### Managing Device Configurations
1. Navigate to `http://nvidia:5000/connect-manager#device-config`
2. Click "Edytuj" on any device
3. Modify JSON configuration directly
4. Click "Aktualizuj konfigurację"

### Creating Test Scenarios
1. Navigate to `http://nvidia:5000/connect-manager#test-config`
2. Click "Dodaj scenariusz"
3. Configure parameters and expected results using JSON Tree Editor
4. Save scenario for reuse

### Managing JSON Templates
1. Navigate to `http://nvidia:5000/connect-manager#json-templates`
2. Filter by type or category
3. Create templates with default values and optional JSON schema
4. Use templates across different configurations

## 🔧 Troubleshooting

### Common Issues

**1. "Not authenticated" Error**
- Solution: Login using credentials in right sidebar
- Check JWT token in browser localStorage

**2. "Brak autoryzacji" Message**
- Solution: Ensure user has correct role (maker/configurator)
- Use role switcher if multiple roles available

**3. JSON Validation Errors**
- Solution: Use JSON Tree Editor instead of manual editing
- Validate JSON syntax before saving

**4. Hash Routing Not Working**
- Solution: Clear browser cache
- Ensure JavaScript is enabled

---

**API Guide Version**: 1.0  
**Last Updated**: 2025-10-03 08:04  
**System Status**: PRODUCTION READY ✅
