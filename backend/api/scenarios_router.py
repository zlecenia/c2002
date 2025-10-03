from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from backend.db.base import get_db
from backend.models.models import TestScenario, TestStep, User
from backend.auth.auth import require_role, get_current_user

router = APIRouter(prefix="/scenarios", tags=["Test Scenarios"])


# Pydantic models for request/response with validation
class TestFlowStep(BaseModel):
    step_id: str = Field(..., min_length=1, max_length=50)
    step_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    auto_test: bool = False
    required: bool = True


class TestScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    device_type: Optional[str] = Field(None, max_length=100)
    test_flow: Optional[Dict[str, Any]] = None
    is_active: bool = True

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Scenario name cannot be empty")
        return v.strip()

    @validator("device_type")
    def validate_device_type(cls, v):
        if v is not None:
            allowed_types = ["mask_tester", "pressure_sensor", "flow_meter", "generic_device"]
            if v not in allowed_types:
                raise ValueError(f"Device type must be one of: {allowed_types}")
        return v


class TestScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    device_type: Optional[str] = None
    test_flow: Optional[dict] = None
    is_active: Optional[bool] = None


class TestScenarioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    device_type: Optional[str]
    test_flow: Optional[dict]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class TestStepCreate(BaseModel):
    scenario_id: int
    step_order: int = Field(..., ge=1, le=100)
    step_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parameters: Optional[Dict[str, Any]] = None
    criteria: Optional[Dict[str, Any]] = None
    auto_test: bool = False
    operator_participation: bool = True

    @validator("step_name")
    def validate_step_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Step name cannot be empty")
        return v.strip()


class TestStepResponse(BaseModel):
    id: int
    scenario_id: int
    step_order: int
    step_name: str
    description: Optional[str]
    parameters: Optional[dict]
    criteria: Optional[dict]
    auto_test: bool
    operator_participation: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Test Scenarios CRUD Operations
@router.get("/", response_model=List[TestScenarioResponse])
def get_test_scenarios(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Get all test scenarios (Superuser only)."""
    scenarios = db.query(TestScenario).offset(skip).limit(limit).all()
    return scenarios


@router.post("/", response_model=TestScenarioResponse)
def create_test_scenario(
    scenario: TestScenarioCreate,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Create new test scenario (Superuser only)."""
    # Check for duplicate names for this user
    existing = (
        db.query(TestScenario)
        .filter(TestScenario.name == scenario.name, TestScenario.created_by == current_user.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario with name '{scenario.name}' already exists for this user",
        )

    db_scenario = TestScenario(
        name=scenario.name,
        description=scenario.description,
        device_type=scenario.device_type,
        test_flow=scenario.test_flow,
        created_by=current_user.id,
        is_active=scenario.is_active,
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@router.get("/{scenario_id}", response_model=TestScenarioResponse)
def get_test_scenario(
    scenario_id: int,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Get specific test scenario by ID (Superuser only)."""
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test scenario not found")
    return scenario


@router.put("/{scenario_id}", response_model=TestScenarioResponse)
def update_test_scenario(
    scenario_id: int,
    scenario_update: TestScenarioUpdate,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Update test scenario (Superuser only)."""
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test scenario not found")

    update_data = scenario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)

    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}")
def delete_test_scenario(
    scenario_id: int,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Delete test scenario (Superuser only)."""
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test scenario not found")

    db.delete(scenario)
    db.commit()
    return {"message": "Test scenario deleted successfully"}


# Test Steps CRUD Operations
@router.get("/{scenario_id}/steps", response_model=List[TestStepResponse])
def get_test_steps(
    scenario_id: int,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Get all steps for a test scenario (Superuser only)."""
    steps = (
        db.query(TestStep)
        .filter(TestStep.scenario_id == scenario_id)
        .order_by(TestStep.step_order)
        .all()
    )
    return steps


@router.post("/{scenario_id}/steps", response_model=TestStepResponse)
def create_test_step(
    scenario_id: int,
    step: TestStepCreate,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Create new test step for scenario (Superuser only)."""
    # Verify scenario exists
    scenario = db.query(TestScenario).filter(TestScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test scenario not found")

    step.scenario_id = scenario_id  # Ensure consistency
    db_step = TestStep(**step.model_dump())
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


@router.delete("/steps/{step_id}")
def delete_test_step(
    step_id: int,
    current_user: User = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
):
    """Delete test step (Superuser only)."""
    step = db.query(TestStep).filter(TestStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test step not found")

    db.delete(step)
    db.commit()
    return {"message": "Test step deleted successfully"}
