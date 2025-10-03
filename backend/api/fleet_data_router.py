from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from backend.db.base import get_db
from backend.models.models import Device, Customer, User
from backend.auth.auth import require_role, get_current_user

router = APIRouter(prefix="/fleet-data", tags=["Fleet Data Management"])


# Pydantic models for Device management
class DeviceCreate(BaseModel):
    device_number: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=100)
    kind_of_device: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", max_length=50)
    customer_id: Optional[int] = None
    configuration: Optional[Dict[str, Any]] = None

    @validator("device_number")
    def validate_device_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Device number cannot be empty")
        return v.strip()

    @validator("status")
    def validate_status(cls, v):
        allowed_statuses = ["active", "inactive", "maintenance", "decommissioned"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


class DeviceUpdate(BaseModel):
    device_number: Optional[str] = Field(None, min_length=1, max_length=100)
    device_type: Optional[str] = Field(None, min_length=1, max_length=100)
    kind_of_device: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    customer_id: Optional[int] = None
    configuration: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    id: int
    device_number: str
    device_type: str
    kind_of_device: Optional[str]
    serial_number: Optional[str]
    status: str
    customer_id: Optional[int]
    configuration: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Pydantic models for Customer management
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_info: Optional[Dict[str, Any]] = None

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Customer name cannot be empty")
        return v.strip()


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_info: Optional[Dict[str, Any]] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    contact_info: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Device Management Endpoints
@router.get("/devices", response_model=List[DeviceResponse])
def get_devices(
    skip: int = 0,
    limit: int = 100,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Get all devices with optional filtering.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        device_type: Filter by device type
        status: Filter by device status
        current_user: Current authenticated user (must be manager)
        db: Database session

    Returns:
        List of device records
    """
    query = db.query(Device)

    if device_type:
        query = query.filter(Device.device_type == device_type)
    if status:
        query = query.filter(Device.status == status)

    devices = query.offset(skip).limit(limit).all()
    return devices


@router.post("/devices", response_model=DeviceResponse)
def create_device(
    device: DeviceCreate,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Create a new device.

    Args:
        device: Device data to create
        current_user: Current authenticated user (must be manager)
        db: Database session

    Returns:
        Created device record

    Raises:
        HTTPException: If device number already exists
    """
    # Check for duplicate device number
    existing = db.query(Device).filter(Device.device_number == device.device_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with number '{device.device_number}' already exists",
        )

    # Verify customer exists if provided
    if device.customer_id:
        customer = db.query(Customer).filter(Customer.id == device.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Get specific device by ID (Manager only)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Update device (Manager only)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    # Check for duplicate device number if updating
    if device_update.device_number and device_update.device_number != device.device_number:
        existing = (
            db.query(Device).filter(Device.device_number == device_update.device_number).first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device with number '{device_update.device_number}' already exists",
            )

    # Validate status if updating
    if device_update.status:
        allowed_statuses = ["active", "inactive", "maintenance", "decommissioned"]
        if device_update.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {allowed_statuses}",
            )

    # Verify customer exists if updating customer assignment
    if device_update.customer_id:
        customer = db.query(Customer).filter(Customer.id == device_update.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    update_data = device_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: int,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Delete device (Manager only)."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}


# Customer Management Endpoints
@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Get all customers with pagination.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        current_user: Current authenticated user (must be manager)
        db: Database session

    Returns:
        List of customer records
    """
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers


@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Create new customer (Manager only)."""
    # Check for duplicate name
    existing = db.query(Customer).filter(Customer.name == customer.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with name '{customer.name}' already exists",
        )

    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Get specific customer by ID (Manager only)."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Update customer (Manager only)."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Check for duplicate name if updating
    if customer_update.name and customer_update.name != customer.name:
        existing = db.query(Customer).filter(Customer.name == customer_update.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with name '{customer_update.name}' already exists",
            )

    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_role("manager")),
    db: Session = Depends(get_db),
):
    """Delete customer (Manager only)."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Check if customer has devices
    devices = db.query(Device).filter(Device.customer_id == customer_id).first()
    if devices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer that has associated devices",
        )

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


# Dashboard Statistics
@router.get("/dashboard")
def get_dashboard_stats(
    current_user: User = Depends(require_role("manager")), db: Session = Depends(get_db)
):
    """Get dashboard statistics for fleet data.

    Args:
        current_user: Current authenticated user (must be manager)
        db: Database session

    Returns:
        Dictionary with device and customer statistics
    """
    total_devices = db.query(Device).count()
    active_devices = db.query(Device).filter(Device.status == "active").count()
    inactive_devices = db.query(Device).filter(Device.status == "inactive").count()
    maintenance_devices = db.query(Device).filter(Device.status == "maintenance").count()
    total_customers = db.query(Customer).count()

    # Device types breakdown
    device_types = db.execute(
        text("SELECT device_type, COUNT(*) as count FROM devices GROUP BY device_type")
    ).fetchall()

    return {
        "total_devices": total_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "maintenance_devices": maintenance_devices,
        "total_customers": total_customers,
        "device_types": [{"type": row[0], "count": row[1]} for row in device_types],
    }
