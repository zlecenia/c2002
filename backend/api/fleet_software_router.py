from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from backend.db.base import get_db
from backend.auth.auth import require_role
from backend.models.models import User, Software, SoftwareVersion, DeviceSoftware, SoftwareInstallation, Device

router = APIRouter(prefix="/fleet-software", tags=["Fleet Software Management"])

# Pydantic models for Software management
class SoftwareCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    vendor: Optional[str] = Field(None, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    license_type: Optional[str] = Field(None, max_length=100)
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Software name cannot be empty')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['firmware', 'application', 'driver', 'tool', 'middleware', 'os']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {allowed_categories}')
        return v

class SoftwareUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    vendor: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    license_type: Optional[str] = Field(None, max_length=100)
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class SoftwareResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    vendor: Optional[str]
    category: str
    platform: Optional[str]
    license_type: Optional[str]
    repository_url: Optional[str]
    documentation_url: Optional[str]
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: bool
    versions_count: int = 0
    latest_version: Optional[str] = None
    
    class Config:
        from_attributes = True

class SoftwareVersionCreate(BaseModel):
    software_id: int
    version_number: str = Field(..., min_length=1, max_length=50)
    release_notes: Optional[str] = None
    changelog: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    checksum: Optional[str] = Field(None, max_length=64)
    download_url: Optional[str] = Field(None, max_length=500)
    is_stable: bool = Field(default=True)
    is_beta: bool = Field(default=False)
    requires_reboot: bool = Field(default=False)
    compatibility: Optional[Dict[str, Any]] = None
    released_at: Optional[datetime] = None

    @validator('version_number')
    def validate_version_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Version number cannot be empty')
        return v.strip()

class SoftwareVersionUpdate(BaseModel):
    version_number: Optional[str] = Field(None, min_length=1, max_length=50)
    release_notes: Optional[str] = None
    changelog: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    checksum: Optional[str] = Field(None, max_length=64)
    download_url: Optional[str] = Field(None, max_length=500)
    is_stable: Optional[bool] = None
    is_beta: Optional[bool] = None
    requires_reboot: Optional[bool] = None
    compatibility: Optional[Dict[str, Any]] = None
    released_at: Optional[datetime] = None

class SoftwareVersionResponse(BaseModel):
    id: int
    software_id: int
    version_number: str
    release_notes: Optional[str]
    changelog: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    checksum: Optional[str]
    download_url: Optional[str]
    is_stable: bool
    is_beta: bool
    requires_reboot: bool
    compatibility: Optional[Dict[str, Any]]
    created_by: Optional[int]
    created_at: Optional[datetime]
    released_at: Optional[datetime]
    software_name: str = ""
    installations_count: int = 0
    
    class Config:
        from_attributes = True

class InstallationRequest(BaseModel):
    device_id: int
    version_id: int
    action: str = Field(..., min_length=1)
    configuration: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['install', 'update', 'uninstall', 'rollback']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {allowed_actions}')
        return v

class InstallationResponse(BaseModel):
    id: int
    device_id: int
    version_id: int
    action: str
    status: str
    initiated_by: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    previous_version: Optional[str]
    new_version: Optional[str]
    device_number: str = ""
    software_name: str = ""
    version_number: str = ""
    
    class Config:
        from_attributes = True

# Software CRUD endpoints
@router.get("/software", response_model=List[SoftwareResponse])
def get_software_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Get software list with filtering (Maker only)."""
    query = db.query(Software).filter(Software.is_active == True)
    
    # Apply filters
    if category:
        query = query.filter(Software.category == category)
    if platform:
        query = query.filter(Software.platform.like(f"%{platform}%"))
    if search:
        query = query.filter(
            or_(
                Software.name.like(f"%{search}%"),
                Software.description.like(f"%{search}%"),
                Software.vendor.like(f"%{search}%")
            )
        )
    
    software_list = query.offset(skip).limit(limit).all()
    
    # Add version count and latest version for each software
    result = []
    for software in software_list:
        versions_count = db.query(func.count(SoftwareVersion.id)).filter(
            SoftwareVersion.software_id == software.id
        ).scalar()
        
        latest_version = db.query(SoftwareVersion.version_number).filter(
            SoftwareVersion.software_id == software.id
        ).order_by(desc(SoftwareVersion.created_at)).first()
        
        software_dict = {
            "id": software.id,
            "name": software.name,
            "description": software.description,
            "vendor": software.vendor,
            "category": software.category,
            "platform": software.platform,
            "license_type": software.license_type,
            "repository_url": software.repository_url,
            "documentation_url": software.documentation_url,
            "created_by": software.created_by,
            "created_at": software.created_at,
            "updated_at": software.updated_at,
            "is_active": software.is_active,
            "versions_count": versions_count,
            "latest_version": latest_version[0] if latest_version else None
        }
        result.append(software_dict)
    
    return result

@router.post("/software", response_model=SoftwareResponse)
def create_software(
    software: SoftwareCreate,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Create new software entry (Maker only)."""
    # Check for duplicate software name
    existing = db.query(Software).filter(Software.name == software.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Software with name '{software.name}' already exists"
        )
    
    # Create new software
    db_software = Software(
        name=software.name,
        description=software.description,
        vendor=software.vendor,
        category=software.category,
        platform=software.platform,
        license_type=software.license_type,
        repository_url=software.repository_url,
        documentation_url=software.documentation_url,
        created_by=current_user.id,
        is_active=software.is_active
    )
    
    db.add(db_software)
    db.commit()
    db.refresh(db_software)
    
    return {
        "id": db_software.id,
        "name": db_software.name,
        "description": db_software.description,
        "vendor": db_software.vendor,
        "category": db_software.category,
        "platform": db_software.platform,
        "license_type": db_software.license_type,
        "repository_url": db_software.repository_url,
        "documentation_url": db_software.documentation_url,
        "created_by": db_software.created_by,
        "created_at": db_software.created_at,
        "updated_at": db_software.updated_at,
        "is_active": db_software.is_active,
        "versions_count": 0,
        "latest_version": None
    }

@router.get("/software/{software_id}", response_model=SoftwareResponse)
def get_software(
    software_id: int,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Get software by ID (Maker only)."""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    # Get version count and latest version
    versions_count = db.query(func.count(SoftwareVersion.id)).filter(
        SoftwareVersion.software_id == software.id
    ).scalar()
    
    latest_version = db.query(SoftwareVersion.version_number).filter(
        SoftwareVersion.software_id == software.id
    ).order_by(desc(SoftwareVersion.created_at)).first()
    
    return {
        "id": software.id,
        "name": software.name,
        "description": software.description,
        "vendor": software.vendor,
        "category": software.category,
        "platform": software.platform,
        "license_type": software.license_type,
        "repository_url": software.repository_url,
        "documentation_url": software.documentation_url,
        "created_by": software.created_by,
        "created_at": software.created_at,
        "updated_at": software.updated_at,
        "is_active": software.is_active,
        "versions_count": versions_count,
        "latest_version": latest_version[0] if latest_version else None
    }

@router.put("/software/{software_id}", response_model=SoftwareResponse)
def update_software(
    software_id: int,
    software_update: SoftwareUpdate,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Update software by ID (Maker only)."""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    # Check for duplicate name if name is being updated
    if software_update.name and software_update.name != software.name:
        existing = db.query(Software).filter(Software.name == software_update.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Software with name '{software_update.name}' already exists"
            )
    
    # Update software fields
    update_data = software_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(software, field, value)
    
    db.commit()
    db.refresh(software)
    
    # Get updated counts
    versions_count = db.query(func.count(SoftwareVersion.id)).filter(
        SoftwareVersion.software_id == software.id
    ).scalar()
    
    latest_version = db.query(SoftwareVersion.version_number).filter(
        SoftwareVersion.software_id == software.id
    ).order_by(desc(SoftwareVersion.created_at)).first()
    
    return {
        "id": software.id,
        "name": software.name,
        "description": software.description,
        "vendor": software.vendor,
        "category": software.category,
        "platform": software.platform,
        "license_type": software.license_type,
        "repository_url": software.repository_url,
        "documentation_url": software.documentation_url,
        "created_by": software.created_by,
        "created_at": software.created_at,
        "updated_at": software.updated_at,
        "is_active": software.is_active,
        "versions_count": versions_count,
        "latest_version": latest_version[0] if latest_version else None
    }

@router.delete("/software/{software_id}")
def delete_software(
    software_id: int,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Soft delete software by ID (Maker only)."""
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    # Soft delete - set is_active to False
    setattr(software, 'is_active', False)
    db.commit()
    
    return {"message": f"Software '{software.name}' deactivated successfully"}

# Software Version endpoints
@router.get("/software/{software_id}/versions", response_model=List[SoftwareVersionResponse])
def get_software_versions(
    software_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Get versions for a software (Maker only)."""
    # Verify software exists
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    versions = db.query(SoftwareVersion).filter(
        SoftwareVersion.software_id == software_id
    ).order_by(desc(SoftwareVersion.created_at)).offset(skip).limit(limit).all()
    
    # Add additional info for each version
    result = []
    for version in versions:
        installations_count = db.query(func.count(SoftwareInstallation.id)).filter(
            SoftwareInstallation.version_id == version.id
        ).scalar()
        
        version_dict = {
            "id": version.id,
            "software_id": version.software_id,
            "version_number": version.version_number,
            "release_notes": version.release_notes,
            "changelog": version.changelog,
            "file_path": version.file_path,
            "file_size": version.file_size,
            "checksum": version.checksum,
            "download_url": version.download_url,
            "is_stable": version.is_stable,
            "is_beta": version.is_beta,
            "requires_reboot": version.requires_reboot,
            "compatibility": version.compatibility,
            "created_by": version.created_by,
            "created_at": version.created_at,
            "released_at": version.released_at,
            "software_name": software.name,
            "installations_count": installations_count
        }
        result.append(version_dict)
    
    return result

@router.post("/software/{software_id}/versions", response_model=SoftwareVersionResponse)
def create_software_version(
    software_id: int,
    version: SoftwareVersionCreate,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Create new software version (Maker only)."""
    # Verify software exists
    software = db.query(Software).filter(Software.id == software_id).first()
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    # Check for duplicate version number
    existing = db.query(SoftwareVersion).filter(
        and_(
            SoftwareVersion.software_id == software_id,
            SoftwareVersion.version_number == version.version_number
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Version '{version.version_number}' already exists for this software"
        )
    
    # Create new version
    db_version = SoftwareVersion(
        software_id=software_id,
        version_number=version.version_number,
        release_notes=version.release_notes,
        changelog=version.changelog,
        file_path=version.file_path,
        file_size=version.file_size,
        checksum=version.checksum,
        download_url=version.download_url,
        is_stable=version.is_stable,
        is_beta=version.is_beta,
        requires_reboot=version.requires_reboot,
        compatibility=version.compatibility,
        created_by=current_user.id,
        released_at=version.released_at
    )
    
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    return {
        "id": db_version.id,
        "software_id": db_version.software_id,
        "version_number": db_version.version_number,
        "release_notes": db_version.release_notes,
        "changelog": db_version.changelog,
        "file_path": db_version.file_path,
        "file_size": db_version.file_size,
        "checksum": db_version.checksum,
        "download_url": db_version.download_url,
        "is_stable": db_version.is_stable,
        "is_beta": db_version.is_beta,
        "requires_reboot": db_version.requires_reboot,
        "compatibility": db_version.compatibility,
        "created_by": db_version.created_by,
        "created_at": db_version.created_at,
        "released_at": db_version.released_at,
        "software_name": software.name,
        "installations_count": 0
    }

# Installation endpoints
@router.post("/installations", response_model=InstallationResponse)
def create_installation(
    installation: InstallationRequest,
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Create new software installation/update request (Maker only)."""
    # Verify device exists
    device = db.query(Device).filter(Device.id == installation.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Verify version exists
    version = db.query(SoftwareVersion).options(
        joinedload(SoftwareVersion.software)
    ).filter(SoftwareVersion.id == installation.version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software version not found"
        )
    
    # Get current installation status
    current_installation = db.query(DeviceSoftware).filter(
        and_(
            DeviceSoftware.device_id == installation.device_id,
            DeviceSoftware.software_id == version.software_id
        )
    ).first()
    
    previous_version = None
    if current_installation:
        previous_version = current_installation.installed_version
    
    # Create installation record
    db_installation = SoftwareInstallation(
        device_id=installation.device_id,
        version_id=installation.version_id,
        action=installation.action,
        status="pending",
        initiated_by=current_user.id,
        previous_version=previous_version,
        new_version=version.version_number
    )
    
    db.add(db_installation)
    db.commit()
    db.refresh(db_installation)
    
    # Update or create device software record
    if installation.action in ["install", "update"]:
        if current_installation:
            setattr(current_installation, 'version_id', installation.version_id)
            setattr(current_installation, 'installed_version', version.version_number)
            setattr(current_installation, 'installation_status', "installing")
            setattr(current_installation, 'installation_date', datetime.now())
            setattr(current_installation, 'configuration', installation.configuration)
            setattr(current_installation, 'notes', installation.notes)
        else:
            new_device_software = DeviceSoftware(
                device_id=installation.device_id,
                software_id=version.software_id,
                version_id=installation.version_id,
                installed_version=version.version_number,
                installation_status="installing",
                installation_date=datetime.now(),
                configuration=installation.configuration,
                notes=installation.notes
            )
            db.add(new_device_software)
    
    db.commit()
    
    return {
        "id": db_installation.id,
        "device_id": db_installation.device_id,
        "version_id": db_installation.version_id,
        "action": db_installation.action,
        "status": db_installation.status,
        "initiated_by": db_installation.initiated_by,
        "started_at": db_installation.started_at,
        "completed_at": db_installation.completed_at,
        "error_message": db_installation.error_message,
        "previous_version": db_installation.previous_version,
        "new_version": db_installation.new_version,
        "device_number": device.device_number,
        "software_name": version.software.name,
        "version_number": version.version_number
    }

@router.get("/installations", response_model=List[InstallationResponse])
def get_installations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    device_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Get installation history with filtering (Maker only)."""
    query = db.query(SoftwareInstallation).options(
        joinedload(SoftwareInstallation.device),
        joinedload(SoftwareInstallation.version).joinedload(SoftwareVersion.software)
    )
    
    # Apply filters
    if device_id:
        query = query.filter(SoftwareInstallation.device_id == device_id)
    if status:
        query = query.filter(SoftwareInstallation.status == status)
    if action:
        query = query.filter(SoftwareInstallation.action == action)
    
    installations = query.order_by(desc(SoftwareInstallation.started_at)).offset(skip).limit(limit).all()
    
    result = []
    for installation in installations:
        result.append({
            "id": installation.id,
            "device_id": installation.device_id,
            "version_id": installation.version_id,
            "action": installation.action,
            "status": installation.status,
            "initiated_by": installation.initiated_by,
            "started_at": installation.started_at,
            "completed_at": installation.completed_at,
            "error_message": installation.error_message,
            "previous_version": installation.previous_version,
            "new_version": installation.new_version,
            "device_number": installation.device.device_number,
            "software_name": installation.version.software.name,
            "version_number": installation.version.version_number
        })
    
    return result

@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: User = Depends(require_role("maker")),
    db: Session = Depends(get_db)
):
    """Get Fleet Software Manager dashboard statistics (Maker only)."""
    # Count software by category
    software_by_category = db.query(
        Software.category,
        func.count(Software.id).label('count')
    ).filter(Software.is_active == True).group_by(Software.category).all()
    
    # Count installations by status
    installations_by_status = db.query(
        SoftwareInstallation.status,
        func.count(SoftwareInstallation.id).label('count')
    ).group_by(SoftwareInstallation.status).all()
    
    # Count devices with software installed
    devices_with_software = db.query(func.count(func.distinct(DeviceSoftware.device_id))).scalar()
    
    # Total software and versions
    total_software = db.query(func.count(Software.id)).filter(Software.is_active == True).scalar()
    total_versions = db.query(func.count(SoftwareVersion.id)).scalar()
    
    # Recent installations
    recent_installations = db.query(func.count(SoftwareInstallation.id)).filter(
        SoftwareInstallation.started_at >= func.date_trunc('day', func.now())
    ).scalar()
    
    return {
        "total_software": total_software,
        "total_versions": total_versions,
        "devices_with_software": devices_with_software,
        "recent_installations": recent_installations,
        "software_by_category": [{"category": row[0], "count": row[1]} for row in software_by_category],
        "installations_by_status": [{"status": row[0], "count": row[1]} for row in installations_by_status]
    }