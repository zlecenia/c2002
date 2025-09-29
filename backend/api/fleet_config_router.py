from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from backend.db.base import get_db
from backend.models.models import Device, TestScenario, User, Configuration
from backend.auth.auth import require_role, get_current_user

router = APIRouter(prefix="/fleet-config", tags=["Fleet Configuration Management"])

# Pydantic models for Configuration management
class SystemConfigCreate(BaseModel):
    config_name: str = Field(..., min_length=1, max_length=255)
    config_type: str = Field(..., min_length=1, max_length=100)
    config_value: Dict[str, Any] = Field(...)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)

    @validator('config_name')
    def validate_config_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Configuration name cannot be empty')
        return v.strip()

    @validator('config_type')
    def validate_config_type(cls, v):
        allowed_types = ['device_settings', 'test_parameters', 'system_limits', 'network_config', 'security_config']
        if v not in allowed_types:
            raise ValueError(f'Config type must be one of: {allowed_types}')
        return v

class SystemConfigUpdate(BaseModel):
    config_name: Optional[str] = Field(None, min_length=1, max_length=255)
    config_type: Optional[str] = Field(None, min_length=1, max_length=100)
    config_value: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class SystemConfigResponse(BaseModel):
    id: int
    config_name: str
    config_type: str
    config_value: Dict[str, Any]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeviceConfigUpdate(BaseModel):
    device_id: int
    configuration: Dict[str, Any] = Field(...)
    
    @validator('configuration')
    def validate_configuration(cls, v):
        if not v:
            raise ValueError('Configuration cannot be empty')
        return v

class TestScenarioConfigCreate(BaseModel):
    scenario_name: str = Field(..., min_length=1, max_length=255)
    test_type: str = Field(..., min_length=1, max_length=100)
    parameters: Dict[str, Any] = Field(...)
    expected_results: Optional[Dict[str, Any]] = None
    is_active: bool = Field(default=True)

    @validator('scenario_name')
    def validate_scenario_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Scenario name cannot be empty')
        return v.strip()

class TestScenarioConfigUpdate(BaseModel):
    scenario_name: Optional[str] = Field(None, min_length=1, max_length=255)
    test_type: Optional[str] = Field(None, min_length=1, max_length=100)
    parameters: Optional[Dict[str, Any]] = None
    expected_results: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

# System Configuration Endpoints
@router.get("/system-configs", response_model=List[SystemConfigResponse])
def get_system_configs(
    skip: int = 0,
    limit: int = 100,
    config_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Get all system configurations with optional filtering (Configurator only)."""
    query = db.query(Configuration).filter(Configuration.component == "FCM")
    
    if config_type:
        # Filter by config_key pattern for config_type
        query = query.filter(Configuration.config_key.like(f"{config_type}%"))
    
    configs = query.offset(skip).limit(limit).all()
    
    # Transform Configuration model to SystemConfigResponse format
    result = []
    for config in configs:
        # Parse config_key to determine config_type, status, and config_name
        key_parts = config.config_key.split(".")
        if len(key_parts) >= 3:
            config_type_extracted = key_parts[0]
            status_part = key_parts[1]
            config_name_extracted = ".".join(key_parts[2:])
            is_active = status_part == "active"
        else:
            config_type_extracted = key_parts[0] if len(key_parts) > 0 else "system"
            config_name_extracted = ".".join(key_parts[1:]) if len(key_parts) > 1 else config.config_key
            is_active = True
        
        # Extract metadata from config_value if it's structured
        if isinstance(config.config_value, dict) and "metadata" in config.config_value:
            config_data = config.config_value.get("data", {})
            metadata = config.config_value.get("metadata", {})
            description = metadata.get("description", "")
            is_active = metadata.get("is_active", is_active)
            created_at = metadata.get("created_at", config.updated_at)
        else:
            config_data = config.config_value
            description = f"Configuration managed by FCM (Key: {config.config_key})"
            created_at = config.updated_at
        
        result.append({
            "id": config.id,
            "config_name": config_name_extracted,
            "config_type": config_type_extracted,
            "config_value": config_data,
            "description": description,
            "is_active": is_active,
            "created_at": created_at,
            "updated_at": config.updated_at
        })
    
    return result

@router.post("/system-configs", response_model=SystemConfigResponse)
def create_system_config(
    config: SystemConfigCreate,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Create new system configuration (Configurator only)."""
    # Create config_key from config_type and config_name
    status_prefix = "active" if config.is_active else "inactive"
    config_key = f"{config.config_type}.{status_prefix}.{config.config_name}"
    
    # Check for duplicate config_key
    existing = db.query(Configuration).filter(
        Configuration.config_key == config_key,
        Configuration.component == "FCM"
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration with key '{config_key}' already exists"
        )
    
    # Embed metadata in config_value to work with existing Configuration model
    enhanced_config_value = {
        "data": config.config_value,
        "metadata": {
            "description": config.description,
            "is_active": config.is_active,
            "created_by": current_user.id,
            "created_at": datetime.now().isoformat()
        }
    }
    
    # Create new configuration
    db_config = Configuration(
        config_key=config_key,
        config_value=enhanced_config_value,
        component="FCM",
        updated_by=current_user.id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return {
        "id": db_config.id,
        "config_name": config.config_name,
        "config_type": config.config_type,
        "config_value": db_config.config_value.get("data", {}),
        "description": db_config.config_value.get("metadata", {}).get("description", ""),
        "is_active": db_config.config_value.get("metadata", {}).get("is_active", True),
        "created_at": db_config.config_value.get("metadata", {}).get("created_at", db_config.updated_at),
        "updated_at": db_config.updated_at
    }

@router.get("/system-configs/{config_id}", response_model=SystemConfigResponse)
def get_system_config(
    config_id: int,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Get specific system configuration by ID (Configurator only)."""
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.component == "FCM"
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    # Parse config_key to determine config_type, status, and config_name
    key_parts = config.config_key.split(".")
    if len(key_parts) >= 3:
        config_type_extracted = key_parts[0]
        status_part = key_parts[1]
        config_name_extracted = ".".join(key_parts[2:])
        is_active = status_part == "active"
    else:
        config_type_extracted = key_parts[0] if len(key_parts) > 0 else "system"
        config_name_extracted = ".".join(key_parts[1:]) if len(key_parts) > 1 else config.config_key
        is_active = True
    
    # Extract metadata from config_value if it's structured
    if isinstance(config.config_value, dict) and "metadata" in config.config_value:
        config_data = config.config_value.get("data", {})
        metadata = config.config_value.get("metadata", {})
        description = metadata.get("description", "")
        is_active = metadata.get("is_active", is_active)
        created_at = metadata.get("created_at", config.updated_at)
    else:
        config_data = config.config_value
        description = f"Configuration managed by FCM (Key: {config.config_key})"
        created_at = config.updated_at
    
    return {
        "id": config.id,
        "config_name": config_name_extracted,
        "config_type": config_type_extracted,
        "config_value": config_data,
        "description": description,
        "is_active": is_active,
        "created_at": created_at,
        "updated_at": config.updated_at
    }

@router.put("/system-configs/{config_id}", response_model=SystemConfigResponse)
def update_system_config(
    config_id: int,
    config_update: SystemConfigUpdate,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Update system configuration (Configurator only)."""
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.component == "FCM"
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    # Get current metadata
    current_config_value = config.config_value
    if isinstance(current_config_value, dict) and "metadata" in current_config_value:
        current_data = current_config_value.get("data", {})
        current_metadata = current_config_value.get("metadata", {})
    else:
        current_data = current_config_value
        current_metadata = {"is_active": True, "description": "", "created_at": config.updated_at.isoformat()}
    
    # Update configuration data and metadata
    new_data = config_update.config_value if config_update.config_value is not None else current_data
    new_metadata = current_metadata.copy()
    
    if config_update.description is not None:
        new_metadata["description"] = config_update.description
    if config_update.is_active is not None:
        new_metadata["is_active"] = config_update.is_active
    
    enhanced_config_value = {
        "data": new_data,
        "metadata": new_metadata
    }
    
    setattr(config, 'config_value', enhanced_config_value)
    
    # Update config_key if config_type, config_name, or is_active changed
    current_key_parts = config.config_key.split(".")
    if len(current_key_parts) >= 3:
        current_type = current_key_parts[0]
        current_status = current_key_parts[1]
        current_name = ".".join(current_key_parts[2:])
    else:
        current_type = current_key_parts[0] if len(current_key_parts) > 0 else "system"
        current_status = "active"
        current_name = ".".join(current_key_parts[1:]) if len(current_key_parts) > 1 else config.config_key
    
    new_type = config_update.config_type or current_type
    new_name = config_update.config_name or current_name
    new_status = "active" if new_metadata["is_active"] else "inactive"
    new_key = f"{new_type}.{new_status}.{new_name}"
    
    # Check for duplicate if key changed
    if new_key != config.config_key:
        existing = db.query(Configuration).filter(
            Configuration.config_key == new_key,
            Configuration.component == "FCM"
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration with key '{new_key}' already exists"
            )
        setattr(config, 'config_key', new_key)
    
    setattr(config, 'updated_by', current_user.id)
    
    db.commit()
    db.refresh(config)
    
    # Parse updated config_key and return proper structure
    key_parts = config.config_key.split(".")
    if len(key_parts) >= 3:
        config_type_extracted = key_parts[0]
        config_name_extracted = ".".join(key_parts[2:])
    else:
        config_type_extracted = key_parts[0] if len(key_parts) > 0 else "system"
        config_name_extracted = ".".join(key_parts[1:]) if len(key_parts) > 1 else config.config_key
    
    # Get final metadata from updated config_value
    final_config_value = config.config_value
    if isinstance(final_config_value, dict) and "metadata" in final_config_value:
        config_data = final_config_value.get("data", {})
        metadata = final_config_value.get("metadata", {})
        description = metadata.get("description", "")
        is_active = metadata.get("is_active", True)
        created_at = metadata.get("created_at", config.updated_at)
    else:
        config_data = final_config_value
        description = "Configuration managed by FCM"
        is_active = True
        created_at = config.updated_at
    
    return {
        "id": config.id,
        "config_name": config_name_extracted,
        "config_type": config_type_extracted,
        "config_value": config_data,
        "description": description,
        "is_active": is_active,
        "created_at": created_at,
        "updated_at": config.updated_at
    }

@router.delete("/system-configs/{config_id}")
def delete_system_config(
    config_id: int,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Delete system configuration (Configurator only)."""
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.component == "FCM"
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return {"message": "System configuration deleted successfully"}

# Device Configuration Management
@router.get("/device-configs")
def get_device_configs(
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Get all device configurations (Configurator only)."""
    devices = db.query(Device).all()
    device_configs = []
    
    for device in devices:
        device_configs.append({
            "device_id": device.id,
            "device_number": device.device_number,
            "device_type": device.device_type,
            "configuration": device.configuration if device.configuration is not None else {},
            "status": device.status,
            "last_updated": device.updated_at
        })
    
    return device_configs

@router.put("/device-configs/{device_id}")
def update_device_config(
    device_id: int,
    config_update: DeviceConfigUpdate,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Update device configuration (Configurator only)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update device configuration using setattr to avoid SQLAlchemy issues
    setattr(device, 'configuration', config_update.configuration)
    db.commit()
    db.refresh(device)
    
    return {
        "message": "Device configuration updated successfully",
        "device_id": device_id,
        "configuration": device.configuration
    }

# Test Scenario Configuration Management
@router.get("/test-scenario-configs")
def get_test_scenario_configs(
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Get all test scenario configurations (Configurator only)."""
    scenarios = db.query(TestScenario).all()
    scenario_configs = []
    
    for scenario in scenarios:
        scenario_configs.append({
            "scenario_id": scenario.id,
            "scenario_name": scenario.scenario_name,
            "test_type": scenario.test_type,
            "parameters": scenario.parameters or {},
            "expected_results": scenario.expected_results or {},
            "is_active": True,  # Assuming scenarios are active by default
            "created_at": scenario.created_at,
            "updated_at": scenario.updated_at
        })
    
    return scenario_configs

@router.post("/test-scenario-configs")
def create_test_scenario_config(
    scenario_config: TestScenarioConfigCreate,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Create new test scenario configuration (Configurator only)."""
    # Check for duplicate scenario name
    existing = db.query(TestScenario).filter(TestScenario.scenario_name == scenario_config.scenario_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Test scenario with name '{scenario_config.scenario_name}' already exists"
        )
    
    db_scenario = TestScenario(
        scenario_name=scenario_config.scenario_name,
        test_type=scenario_config.test_type,
        parameters=scenario_config.parameters,
        expected_results=scenario_config.expected_results
    )
    
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    
    return {
        "message": "Test scenario configuration created successfully",
        "scenario_id": db_scenario.id,
        "scenario_name": db_scenario.scenario_name
    }

@router.put("/test-scenario-configs/{scenario_id}")
def update_test_scenario_config(
    scenario_id: int,
    scenario_update: TestScenarioConfigUpdate,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Update test scenario configuration (Configurator only)."""
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test scenario not found"
        )
    
    # Check for duplicate name if updating
    if scenario_update.scenario_name and scenario_update.scenario_name != scenario.scenario_name:
        existing = db.query(TestScenario).filter(TestScenario.scenario_name == scenario_update.scenario_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Test scenario with name '{scenario_update.scenario_name}' already exists"
            )
    
    update_data = scenario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)
    
    db.commit()
    db.refresh(scenario)
    
    return {
        "message": "Test scenario configuration updated successfully",
        "scenario_id": scenario_id,
        "scenario_name": scenario.scenario_name
    }

@router.delete("/test-scenario-configs/{scenario_id}")
def delete_test_scenario_config(
    scenario_id: int,
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Delete test scenario configuration (Configurator only)."""
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test scenario not found"
        )
    
    db.delete(scenario)
    db.commit()
    
    return {"message": "Test scenario configuration deleted successfully"}

# Dashboard and Statistics
@router.get("/dashboard")
def get_config_dashboard(
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Get configuration dashboard statistics (Configurator only)."""
    total_devices = db.query(Device).count()
    configured_devices = db.query(Device).filter(Device.configuration != None).count()
    total_scenarios = db.query(TestScenario).count()
    
    # Device types and their configurations
    device_types = db.execute(
        text("SELECT device_type, COUNT(*) as count FROM devices GROUP BY device_type")
    ).fetchall()
    
    # System configuration summary from real data
    active_configs = db.query(Configuration).filter(Configuration.component == "FCM").count()
    
    return {
        "total_devices": total_devices,
        "configured_devices": configured_devices,
        "unconfigured_devices": total_devices - configured_devices,
        "total_test_scenarios": total_scenarios,
        "active_system_configs": active_configs,
        "device_type_breakdown": [{"type": row[0], "count": row[1]} for row in device_types],
        "configuration_coverage": round((configured_devices / total_devices * 100) if total_devices > 0 else 0, 2)
    }

# Configuration Backup and Restore
@router.post("/backup")
def backup_configurations(
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Create backup of all configurations (Configurator only)."""
    # Get all device configurations
    devices = db.query(Device).all()
    device_configs = [{"id": d.id, "configuration": d.configuration if d.configuration is not None else {}} for d in devices]
    
    # Get all test scenario configurations
    scenarios = db.query(TestScenario).all()
    scenario_configs = [{"id": s.id, "parameters": s.parameters or {}, "expected_results": s.expected_results or {}} for s in scenarios]
    
    # Get all system configurations from Configuration table
    system_configs = db.query(Configuration).filter(Configuration.component == "FCM").all()
    system_configs_data = [{"id": c.id, "config_key": c.config_key, "config_value": c.config_value} for c in system_configs]
    
    backup_data = {
        "backup_timestamp": datetime.now().isoformat(),
        "device_configurations": device_configs,
        "test_scenario_configurations": scenario_configs,
        "system_configurations": system_configs_data
    }
    
    return {
        "message": "Configuration backup created successfully",
        "backup_id": f"backup_{int(datetime.now().timestamp())}",
        "backup_data": backup_data
    }

@router.post("/restore")
def restore_configurations(
    backup_data: Dict[str, Any],
    current_user: User = Depends(require_role("configurator")),
    db: Session = Depends(get_db)
):
    """Restore configurations from backup (Configurator only)."""
    try:
        # Restore device configurations
        if "device_configurations" in backup_data:
            for device_config in backup_data["device_configurations"]:
                device = db.query(Device).filter(Device.id == device_config["id"]).first()
                if device:
                    setattr(device, 'configuration', device_config["configuration"])
        
        # Restore test scenario configurations
        if "test_scenario_configurations" in backup_data:
            for scenario_config in backup_data["test_scenario_configurations"]:
                scenario = db.query(TestScenario).filter(TestScenario.id == scenario_config["id"]).first()
                if scenario:
                    scenario.parameters = scenario_config["parameters"]
                    scenario.expected_results = scenario_config["expected_results"]
        
        # Restore system configurations
        if "system_configurations" in backup_data:
            for system_config in backup_data["system_configurations"]:
                config = db.query(Configuration).filter(
                    Configuration.id == system_config["id"],
                    Configuration.component == "FCM"
                ).first()
                if config:
                    # Restore both config_value and config_key for complete state recovery
                    setattr(config, 'config_value', system_config["config_value"])
                    if "config_key" in system_config:
                        setattr(config, 'config_key', system_config["config_key"])
                    setattr(config, 'updated_by', current_user.id)
        
        db.commit()
        
        return {
            "message": "Configurations restored successfully",
            "restored_at": datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring configurations: {str(e)}"
        )