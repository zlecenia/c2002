"""
Fleet Workshop Manager API Router
Handles repairs, maintenance, and parts management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from backend.db.base import get_db
from backend.models.models import Repair, Maintenance, Part, Device, User
from backend.auth.auth import get_current_user

router = APIRouter(prefix="/api/v1/fleet-workshop", tags=["Fleet Workshop Manager"])

# Pydantic Models for Request/Response

class RepairCreate(BaseModel):
    device_id: int
    repair_type: str  # corrective, preventive, upgrade
    priority: str = "medium"  # low, medium, high, critical
    description: str
    problem_description: Optional[str] = None
    parts_used: Optional[dict] = None
    cost_estimate: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None

class RepairUpdate(BaseModel):
    repair_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    problem_description: Optional[str] = None
    solution_description: Optional[str] = None
    parts_used: Optional[dict] = None
    labor_hours: Optional[int] = None
    cost_estimate: Optional[int] = None
    actual_cost: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

class MaintenanceCreate(BaseModel):
    device_id: int
    maintenance_type: str  # routine, scheduled, condition_based, predictive
    schedule_type: Optional[str] = None
    frequency_value: Optional[int] = None
    title: str
    description: Optional[str] = None
    checklist: Optional[dict] = None
    parts_required: Optional[dict] = None
    estimated_duration: Optional[int] = None
    technician_id: Optional[int] = None
    next_due: Optional[datetime] = None

class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    schedule_type: Optional[str] = None
    frequency_value: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    checklist: Optional[dict] = None
    parts_required: Optional[dict] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    technician_id: Optional[int] = None
    last_performed: Optional[datetime] = None
    next_due: Optional[datetime] = None
    completion_notes: Optional[str] = None

class PartCreate(BaseModel):
    part_number: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    supplier: Optional[str] = None
    unit_price: Optional[int] = None
    currency: str = "PLN"
    stock_quantity: int = 0
    min_stock_level: int = 0
    max_stock_level: Optional[int] = None
    location: Optional[str] = None
    compatible_devices: Optional[dict] = None
    specifications: Optional[dict] = None
    datasheet_url: Optional[str] = None
    barcode: Optional[str] = None
    notes: Optional[str] = None

class PartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    supplier: Optional[str] = None
    unit_price: Optional[int] = None
    currency: Optional[str] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    max_stock_level: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None
    compatible_devices: Optional[dict] = None
    specifications: Optional[dict] = None
    datasheet_url: Optional[str] = None
    barcode: Optional[str] = None
    notes: Optional[str] = None

# Dashboard and Statistics

@router.get("/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get workshop dashboard statistics"""
    
    # Count repairs by status
    pending_repairs = db.query(Repair).filter(Repair.status == 'pending').count()
    in_progress_repairs = db.query(Repair).filter(Repair.status == 'in_progress').count()
    completed_repairs = db.query(Repair).filter(Repair.status == 'completed').count()
    
    # Count maintenance by status
    scheduled_maintenance = db.query(Maintenance).filter(Maintenance.status == 'scheduled').count()
    overdue_maintenance = db.query(Maintenance).filter(Maintenance.status == 'overdue').count()
    completed_maintenance = db.query(Maintenance).filter(Maintenance.status == 'completed').count()
    
    # Parts statistics
    total_parts = db.query(Part).filter(Part.status == 'active').count()
    low_stock_parts = db.query(Part).filter(
        and_(Part.status == 'active', Part.stock_quantity <= Part.min_stock_level)
    ).count()
    
    # Recent activity
    recent_repairs = db.query(Repair).order_by(Repair.created_at.desc()).limit(5).all()
    recent_maintenance = db.query(Maintenance).order_by(Maintenance.created_at.desc()).limit(5).all()
    
    return {
        "repairs": {
            "pending": pending_repairs,
            "in_progress": in_progress_repairs,
            "completed": completed_repairs,
            "recent": [
                {
                    "id": r.id,
                    "device_id": r.device_id,
                    "description": r.description,
                    "priority": r.priority,
                    "status": r.status,
                    "created_at": r.created_at
                } for r in recent_repairs
            ]
        },
        "maintenance": {
            "scheduled": scheduled_maintenance,
            "overdue": overdue_maintenance,
            "completed": completed_maintenance,
            "recent": [
                {
                    "id": m.id,
                    "device_id": m.device_id,
                    "title": m.title,
                    "status": m.status,
                    "next_due": m.next_due,
                    "created_at": m.created_at
                } for m in recent_maintenance
            ]
        },
        "parts": {
            "total": total_parts,
            "low_stock": low_stock_parts
        }
    }

# Repairs Endpoints

@router.get("/repairs")
async def get_repairs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    device_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of repairs with optional filtering"""
    
    query = db.query(Repair)
    
    if status:
        query = query.filter(Repair.status == status)
    if priority:
        query = query.filter(Repair.priority == priority)
    if device_id:
        query = query.filter(Repair.device_id == device_id)
    
    repairs = query.offset(skip).limit(limit).all()
    
    return {"repairs": repairs}

@router.post("/repairs", status_code=status.HTTP_201_CREATED)
async def create_repair(
    repair: RepairCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new repair"""
    
    # Verify device exists
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Create repair
    db_repair = Repair(
        **repair.dict(),
        reported_by=current_user.id
    )
    
    db.add(db_repair)
    db.commit()
    db.refresh(db_repair)
    
    return {"message": "Repair created successfully", "repair": db_repair}

@router.get("/repairs/{repair_id}")
async def get_repair(
    repair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific repair details"""
    
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    
    return {"repair": repair}

@router.put("/repairs/{repair_id}")
async def update_repair(
    repair_id: int,
    repair_update: RepairUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update repair details"""
    
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    
    # Update fields
    for field, value in repair_update.dict(exclude_unset=True).items():
        setattr(repair, field, value)
    
    # Auto-set timestamps based on status changes
    if repair_update.status == 'in_progress' and not repair.started_at:
        repair.started_at = datetime.utcnow()
    elif repair_update.status == 'completed' and not repair.completed_at:
        repair.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(repair)
    
    return {"message": "Repair updated successfully", "repair": repair}

# Maintenance Endpoints

@router.get("/maintenance")
async def get_maintenance(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    device_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of maintenance items with optional filtering"""
    
    query = db.query(Maintenance)
    
    if status:
        query = query.filter(Maintenance.status == status)
    if maintenance_type:
        query = query.filter(Maintenance.maintenance_type == maintenance_type)
    if device_id:
        query = query.filter(Maintenance.device_id == device_id)
    
    maintenance_items = query.offset(skip).limit(limit).all()
    
    return {"maintenance": maintenance_items}

@router.post("/maintenance", status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance: MaintenanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new maintenance task"""
    
    # Verify device exists
    device = db.query(Device).filter(Device.id == maintenance.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Create maintenance
    db_maintenance = Maintenance(
        **maintenance.dict(),
        created_by=current_user.id
    )
    
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    
    return {"message": "Maintenance created successfully", "maintenance": db_maintenance}

@router.put("/maintenance/{maintenance_id}")
async def update_maintenance(
    maintenance_id: int,
    maintenance_update: MaintenanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update maintenance details"""
    
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    
    # Update fields
    for field, value in maintenance_update.dict(exclude_unset=True).items():
        setattr(maintenance, field, value)
    
    # Auto-calculate next due date if completed
    if maintenance_update.status == 'completed' and maintenance.schedule_type and maintenance.frequency_value:
        if maintenance.schedule_type == 'days':
            maintenance.next_due = datetime.utcnow() + timedelta(days=maintenance.frequency_value)
        elif maintenance.schedule_type == 'weeks':
            maintenance.next_due = datetime.utcnow() + timedelta(weeks=maintenance.frequency_value)
        elif maintenance.schedule_type == 'months':
            maintenance.next_due = datetime.utcnow() + timedelta(days=maintenance.frequency_value * 30)
        
        maintenance.last_performed = datetime.utcnow()
    
    db.commit()
    db.refresh(maintenance)
    
    return {"message": "Maintenance updated successfully", "maintenance": maintenance}

# Parts Endpoints

@router.get("/parts")
async def get_parts(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    low_stock: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of parts with optional filtering"""
    
    query = db.query(Part)
    
    if category:
        query = query.filter(Part.category == category)
    if status:
        query = query.filter(Part.status == status)
    if low_stock:
        query = query.filter(Part.stock_quantity <= Part.min_stock_level)
    if search:
        query = query.filter(
            or_(
                Part.name.ilike(f"%{search}%"),
                Part.part_number.ilike(f"%{search}%"),
                Part.description.ilike(f"%{search}%")
            )
        )
    
    parts = query.offset(skip).limit(limit).all()
    
    return {"parts": parts}

@router.post("/parts", status_code=status.HTTP_201_CREATED)
async def create_part(
    part: PartCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new part"""
    
    # Check if part number already exists
    existing_part = db.query(Part).filter(Part.part_number == part.part_number).first()
    if existing_part:
        raise HTTPException(status_code=400, detail="Part number already exists")
    
    # Create part
    db_part = Part(
        **part.dict(),
        created_by=current_user.id
    )
    
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    
    return {"message": "Part created successfully", "part": db_part}

@router.get("/parts/{part_id}")
async def get_part(
    part_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific part details"""
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    return {"part": part}

@router.put("/parts/{part_id}")
async def update_part(
    part_id: int,
    part_update: PartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update part details"""
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Update fields
    for field, value in part_update.dict(exclude_unset=True).items():
        setattr(part, field, value)
    
    db.commit()
    db.refresh(part)
    
    return {"message": "Part updated successfully", "part": part}

@router.delete("/parts/{part_id}")
async def delete_part(
    part_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a part (soft delete by setting status to inactive)"""
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    part.status = 'inactive'
    db.commit()
    
    return {"message": "Part deleted successfully"}
