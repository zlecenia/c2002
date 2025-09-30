-- Fleet Management System - Database Schema Creation
-- PostgreSQL 15+ compatible
-- Generated: September 30, 2025

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table - User accounts with multi-role authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- Primary role for backward compatibility
    roles JSON DEFAULT '[]'::json, -- Array of all roles
    qr_code VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers table - Customer information with JSON contact details
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info JSON, -- Flexible contact structure
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Devices table - Device inventory with status tracking
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_number VARCHAR(100) UNIQUE NOT NULL,
    device_type VARCHAR(100) NOT NULL, -- mask_tester, pressure_sensor, etc.
    kind_of_device VARCHAR(100),
    serial_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, maintenance
    customer_id INTEGER REFERENCES customers(id),
    configuration JSON, -- Device-specific configuration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Software table - Software packages catalog
CREATE TABLE software (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    vendor VARCHAR(255),
    category VARCHAR(100), -- firmware, application, driver, tool
    platform VARCHAR(100), -- device platform compatibility
    license_type VARCHAR(100),
    repository_url VARCHAR(500),
    documentation_url VARCHAR(500),
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Software versions table - Version history per package
CREATE TABLE software_versions (
    id SERIAL PRIMARY KEY,
    software_id INTEGER REFERENCES software(id) ON DELETE CASCADE,
    version_number VARCHAR(50) NOT NULL,
    release_notes TEXT,
    changelog TEXT,
    file_path VARCHAR(500),
    file_size INTEGER,
    checksum VARCHAR(64), -- SHA-256 checksum
    download_url VARCHAR(500),
    is_stable BOOLEAN DEFAULT TRUE,
    is_beta BOOLEAN DEFAULT FALSE,
    requires_reboot BOOLEAN DEFAULT FALSE,
    compatibility JSON, -- Device compatibility info
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    released_at TIMESTAMP WITH TIME ZONE
);

-- Device software mapping table (many-to-many)
CREATE TABLE device_software (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    software_id INTEGER REFERENCES software(id),
    version_id INTEGER REFERENCES software_versions(id),
    installed_version VARCHAR(50),
    installation_status VARCHAR(50) DEFAULT 'not_installed', -- not_installed, installing, installed, failed, outdated
    installation_date TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    configuration JSON, -- Software-specific configuration
    notes TEXT
);

-- Software installations table - Installation tracking and history
CREATE TABLE software_installations (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    version_id INTEGER REFERENCES software_versions(id),
    action VARCHAR(50) NOT NULL, -- install, update, uninstall, rollback
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    initiated_by INTEGER REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    installation_log TEXT,
    previous_version VARCHAR(50),
    new_version VARCHAR(50),
    rollback_point JSON -- Rollback data
);

-- Configurations table - System and device configuration settings
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSON NOT NULL, -- Configuration value
    component VARCHAR(50), -- CPP, CM, FDM, FCM, FSM
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- JSON templates table - Reusable JSON configuration templates
CREATE TABLE json_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    template_type VARCHAR(100) NOT NULL, -- scenario, test_flow, device_config, etc.
    category VARCHAR(100), -- mask_tester, pressure_sensor, etc.
    schema JSON NOT NULL, -- JSON schema definition
    default_values JSON NOT NULL, -- Default JSON values
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test scenarios table - Test scenario definitions with JSON test flow
CREATE TABLE test_scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    device_type VARCHAR(100),
    test_flow JSON, -- Test flow structure
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test steps table - Individual test steps (legacy, now using JSON)
CREATE TABLE test_steps (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES test_scenarios(id),
    step_order INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSON, -- Step parameters
    criteria JSON, -- Success criteria
    auto_test BOOLEAN DEFAULT FALSE,
    operator_participation BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test reports table - Test execution results
CREATE TABLE test_reports (
    id SERIAL PRIMARY KEY,
    test_scenario_id INTEGER REFERENCES test_scenarios(id),
    device_id INTEGER REFERENCES devices(id),
    operator_id INTEGER REFERENCES users(id),
    customer_id INTEGER REFERENCES customers(id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50), -- pending, in_progress, completed, failed
    results JSON, -- Test results
    pressure_data JSON, -- Pressure measurement data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System logs table - System activity and audit logs
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(50), -- INFO, WARNING, ERROR, HELP
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255),
    details JSON, -- Additional details
    ip_address VARCHAR(45),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Translations table - Multi-language translation keys
CREATE TABLE translations (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL, -- en, pl, etc.
    value TEXT NOT NULL,
    component VARCHAR(50), -- CPP, CM, FDM, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_devices_number ON devices(device_number);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_customer ON devices(customer_id);
CREATE INDEX idx_software_name ON software(name);
CREATE INDEX idx_software_active ON software(is_active);
CREATE INDEX idx_test_reports_device ON test_reports(device_id);
CREATE INDEX idx_test_reports_operator ON test_reports(operator_id);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_level ON system_logs(log_level);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_software_updated_at BEFORE UPDATE ON software 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_test_scenarios_updated_at BEFORE UPDATE ON test_scenarios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_json_templates_updated_at BEFORE UPDATE ON json_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
