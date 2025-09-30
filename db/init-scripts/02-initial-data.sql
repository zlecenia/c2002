-- Fleet Management System - Initial Data
-- User accounts, configurations, and test data
-- Generated: September 30, 2025

-- Insert default users with various roles
-- Password hash for 'password123' (use bcrypt in production)
INSERT INTO users (username, email, password_hash, role, roles, is_active) VALUES
-- Super admin with all roles
('maker1', 'maker1@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'superuser', 
 '["maker", "operator", "admin", "superuser", "manager", "configurator"]'::json, true),

-- Admin users
('admin1', 'admin1@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'admin', 
 '["admin", "configurator"]'::json, true),

-- Manager
('manager1', 'manager1@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'manager', 
 '["manager", "operator"]'::json, true),

-- Operators
('operator1', 'operator1@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'operator', 
 '["operator"]'::json, true),
('operator2', 'operator2@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'operator', 
 '["operator"]'::json, true),

-- Configurators
('configurator1', 'config1@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'configurator', 
 '["configurator", "operator"]'::json, true),

-- Test user (inactive)
('testuser', 'test@fleet.com', '$2b$12$LQv3c1yqBwLFNXMO9GQ5YezjRUuLzQj.9k8EE.uYx5QqM8QjGsNDa', 'operator', 
 '["operator"]'::json, false);

-- Insert default customers
INSERT INTO customers (name, contact_info) VALUES
('ACME Manufacturing', '{
  "phone": "+48 123 456 789",
  "email": "contact@acme.com", 
  "address": "Warsaw, Poland",
  "company": "ACME Manufacturing Ltd",
  "notes": "Main customer - priority support"
}'::json),

('TechCorp Solutions', '{
  "phone": "+48 987 654 321",
  "email": "info@techcorp.com",
  "address": "Krakow, Poland", 
  "company": "TechCorp Solutions Sp. z o.o.",
  "notes": "Enterprise client"
}'::json),

('MedDevice Inc', '{
  "phone": "+1 555 123 4567",
  "email": "support@meddevice.com",
  "address": "Boston, MA, USA",
  "company": "MedDevice Inc.",
  "notes": "Medical equipment manufacturer"
}'::json);

-- Insert default devices
INSERT INTO devices (device_number, device_type, kind_of_device, serial_number, status, customer_id, configuration) VALUES
('MT-001', 'mask_tester', 'Medical Testing Equipment', 'SN-MT001-2025', 'active', 1, '{
  "calibration_pressure": 100,
  "test_duration": 60,
  "auto_calibration": true,
  "measurement_units": "mmHg"
}'::json),

('PS-002', 'pressure_sensor', 'Pressure Measurement', 'SN-PS002-2025', 'active', 1, '{
  "range_min": 0,
  "range_max": 500,
  "accuracy": 0.1,
  "units": "bar"
}'::json),

('FM-003', 'flow_meter', 'Flow Measurement', 'SN-FM003-2025', 'active', 2, '{
  "flow_range": "0-1000 L/min",
  "accuracy": "±1%",
  "temperature_compensation": true
}'::json),

('TS-004', 'temperature_sensor', 'Temperature Monitoring', 'SN-TS004-2025', 'maintenance', 2, '{
  "range": "-40 to 150°C",
  "accuracy": "±0.5°C",
  "response_time": "1s"
}'::json),

('HS-005', 'humidity_sensor', 'Humidity Monitoring', 'SN-HS005-2025', 'active', 3, '{
  "range": "0-100% RH",
  "accuracy": "±2% RH",
  "temperature_range": "-20 to 80°C"
}'::json);

-- Insert default software
INSERT INTO software (name, description, vendor, category, platform, license_type, created_by, is_active) VALUES
('FleetOS Firmware', 'Main operating system firmware for fleet devices', 'Fleet Systems Ltd', 'firmware', 'ARM Cortex-M', 'Proprietary', 1, true),
('Calibration Suite', 'Device calibration and configuration software', 'Fleet Systems Ltd', 'application', 'Cross-platform', 'Proprietary', 1, true),
('Diagnostic Tools', 'Hardware diagnostic and testing utilities', 'Fleet Systems Ltd', 'tool', 'Windows/Linux', 'GPL v3', 1, true),
('Device Driver Pack', 'Universal device drivers for fleet hardware', 'Fleet Systems Ltd', 'driver', 'Windows', 'MIT', 1, true);

-- Insert software versions
INSERT INTO software_versions (software_id, version_number, release_notes, is_stable, is_beta, requires_reboot, compatibility, created_by, released_at) VALUES
(1, '2.5.0', 'Stable release with improved mask testing algorithms', true, false, true, '{
  "devices": ["mask_tester", "pressure_sensor"],
  "min_hardware_version": "1.2"
}'::json, 1, NOW()),

(1, '2.6.0-beta', 'Beta release with new flow measurement features', false, true, true, '{
  "devices": ["mask_tester", "flow_meter"], 
  "min_hardware_version": "1.3"
}'::json, 1, NOW()),

(2, '1.8.2', 'Bug fixes and performance improvements', true, false, false, '{
  "devices": ["mask_tester", "pressure_sensor", "flow_meter"],
  "os_requirements": ["Windows 10+", "Ubuntu 20.04+"]
}'::json, 1, NOW()),

(3, '3.1.0', 'New diagnostic features for pressure sensors', true, false, false, '{
  "devices": ["pressure_sensor", "temperature_sensor"],
  "os_requirements": ["Windows 10+", "Linux"]
}'::json, 1, NOW()),

(4, '4.2.1', 'Driver updates for latest hardware revisions', true, false, false, '{
  "devices": ["mask_tester", "pressure_sensor", "flow_meter", "temperature_sensor", "humidity_sensor"],
  "os_requirements": ["Windows 10+", "Windows 11"]
}'::json, 1, NOW());

-- Insert default configurations
INSERT INTO configurations (config_key, config_value, component, updated_by) VALUES
('api_timeout', '{"timeout": 30, "retry": 3, "backoff": "exponential"}'::json, 'FDM', 1),
('database_pool', '{"min_connections": 5, "max_connections": 20, "idle_timeout": 300}'::json, 'FDM', 1),
('jwt_settings', '{"expire_minutes": 30, "refresh_expire_days": 7, "algorithm": "HS256"}'::json, 'CM', 1),
('logging_level', '{"level": "INFO", "file_rotation": "daily", "max_files": 30}'::json, 'ALL', 1),
('device_defaults', '{"status": "active", "auto_discovery": true, "heartbeat_interval": 60}'::json, 'FDM', 1),
('test_settings', '{"default_duration": 60, "max_pressure": 500, "calibration_required": true}'::json, 'CPP', 1);

-- Insert JSON templates
INSERT INTO json_templates (name, template_type, category, schema, default_values, description, created_by) VALUES
('Mask Tester Configuration', 'device_config', 'mask_tester', '{
  "type": "object",
  "properties": {
    "calibration_pressure": {"type": "number", "minimum": 0, "maximum": 1000},
    "test_duration": {"type": "number", "minimum": 10, "maximum": 300},
    "auto_calibration": {"type": "boolean"},
    "measurement_units": {"type": "string", "enum": ["mmHg", "bar", "psi"]}
  },
  "required": ["calibration_pressure", "test_duration"]
}'::json, '{
  "calibration_pressure": 100,
  "test_duration": 60,
  "auto_calibration": true,
  "measurement_units": "mmHg"
}'::json, 'Default configuration template for mask testing devices', 1),

('Basic Test Flow', 'test_flow', 'mask_tester', '{
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "step": {"type": "number"},
          "action": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    }
  }
}'::json, '{
  "steps": [
    {"step": 1, "action": "initialize", "params": {}},
    {"step": 2, "action": "calibrate", "params": {"pressure": 100}},
    {"step": 3, "action": "test", "params": {"duration": 60}},
    {"step": 4, "action": "validate", "params": {"tolerance": 5}},
    {"step": 5, "action": "finalize", "params": {}}
  ]
}'::json, 'Standard test flow for mask testing', 1);

-- Insert test scenarios
INSERT INTO test_scenarios (name, description, device_type, test_flow, created_by, is_active) VALUES
('Standard Mask Test', 'Basic mask integrity and pressure testing', 'mask_tester', '{
  "steps": [
    {"step": 1, "action": "initialize", "params": {"warm_up_time": 30}},
    {"step": 2, "action": "calibrate", "params": {"pressure": 100, "tolerance": 2}},
    {"step": 3, "action": "seal_test", "params": {"duration": 60, "pressure": 100}},
    {"step": 4, "action": "leak_detection", "params": {"threshold": 5}},
    {"step": 5, "action": "generate_report", "params": {"format": "pdf"}}
  ],
  "metadata": {
    "estimated_duration": 300,
    "required_operator": true,
    "automated": false
  }
}'::json, 1, true),

('Pressure Calibration', 'Pressure sensor calibration and validation', 'pressure_sensor', '{
  "steps": [
    {"step": 1, "action": "zero_calibration", "params": {}},
    {"step": 2, "action": "span_calibration", "params": {"reference_pressure": 500}},
    {"step": 3, "action": "linearity_test", "params": {"points": [0, 100, 200, 300, 400, 500]}},
    {"step": 4, "action": "accuracy_validation", "params": {"tolerance": 0.1}},
    {"step": 5, "action": "save_calibration", "params": {}}
  ],
  "metadata": {
    "estimated_duration": 600,
    "required_operator": true,
    "automated": true
  }
}'::json, 1, true);

-- Insert system configuration logs
INSERT INTO system_logs (log_level, user_id, action, details, ip_address) VALUES
('INFO', 1, 'database_initialized', '{"tables_created": 14, "initial_users": 7, "initial_devices": 5}'::json, '127.0.0.1'),
('INFO', 1, 'default_config_loaded', '{"config_keys": 6, "templates": 2, "scenarios": 2}'::json, '127.0.0.1');

-- Insert basic translations (English and Polish)
INSERT INTO translations (key, language, value, component) VALUES
('login.welcome', 'en', 'Welcome to Fleet Management System', 'CM'),
('login.welcome', 'pl', 'Witamy w Systemie Zarządzania Flotą', 'CM'),
('device.status.active', 'en', 'Active', 'FDM'),
('device.status.active', 'pl', 'Aktywny', 'FDM'),
('device.status.maintenance', 'en', 'Maintenance', 'FDM'),
('device.status.maintenance', 'pl', 'Konserwacja', 'FDM'),
('test.start', 'en', 'Start Test', 'CPP'),
('test.start', 'pl', 'Rozpocznij Test', 'CPP'),
('config.saved', 'en', 'Configuration saved successfully', 'FCM'),
('config.saved', 'pl', 'Konfiguracja zapisana pomyślnie', 'FCM');

COMMIT;
