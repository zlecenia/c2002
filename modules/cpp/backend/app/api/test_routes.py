"""
Test management API endpoints for Connect++ (CPP)
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from ..db.database import get_db
from ..models.test_models import TestSession, TestStepResult, SensorReading
from ..core.security import get_current_user
from ..services.test_service import TestService
from pydantic import BaseModel, Field


router = APIRouter(prefix="/tests", tags=["Tests"])


# Pydantic Models
class TestInitialize(BaseModel):
    device_kind_id: int
    device_type_id: int
    test_kind_id: int
    scenario_id: int
    device_serial: str
    customer_id: Optional[int] = None


class TestStepData(BaseModel):
    step_id: int
    step_name: str
    result: str = Field(..., pattern="^(PASSED|FAILED|WARNING|N/A)$")
    operator_checks: Optional[dict] = None
    operator_notes: Optional[str] = None
    photos: Optional[List[str]] = None
    measurements: Optional[dict] = None
    duration: int


class SensorUpdate(BaseModel):
    sensor_type: str
    value: float
    unit: str
    sensor_id: Optional[str] = None


# System Endpoints
@router.post("/system/start")
async def start_system(
    device_ip: str,
    autostart: bool = True,
    db: Session = Depends(get_db)
):
    """
    Initialize system startup sequence (10s)
    """
    return {
        "status": "starting",
        "progress": 0,
        "estimated_time": 10,
        "message": "System starting in progress...",
        "device_ip": device_ip
    }


@router.post("/system/diagnostic")
async def run_diagnostic(db: Session = Depends(get_db)):
    """
    Run system autodiagnostic (6s)
    Tests: pressure sensors, pneumatic system, communication, hardware
    """
    # Simulated diagnostic results
    results = {
        "status": "completed",
        "duration": 6.2,
        "results": {
            "pressure_sensors": {
                "low": {"status": "ok", "value": -10, "unit": "mbar"},
                "medium": {"status": "ok", "value": 20, "unit": "bar"},
                "high": {"status": "ok", "value": 30, "unit": "bar"}
            },
            "pneumatic": {"status": "ok", "leak_rate": 0.1},
            "communication": {
                "status": "ok",
                "usb_scanner": True,
                "network": True,
                "database": True
            },
            "hardware": {
                "status": "ok",
                "display": True,
                "touch": True,
                "leds": True
            }
        },
        "issues": []
    }
    return results


# Test Session Endpoints
@router.post("/initialize")
async def initialize_test(
    test_data: TestInitialize,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Initialize a new test session
    """
    test_service = TestService(db)
    
    try:
        test_session = test_service.create_test_session(
            device_serial=test_data.device_serial,
            scenario_id=test_data.scenario_id,
            operator_id=current_user.id,
            customer_id=test_data.customer_id,
            device_kind_id=test_data.device_kind_id,
            device_type_id=test_data.device_type_id,
            test_kind_id=test_data.test_kind_id
        )
        
        return {
            "test_session_id": test_session.session_id,
            "status": "initialized",
            "estimated_duration": test_session.estimated_duration,
            "total_steps": test_session.total_steps,
            "current_step": 0,
            "device": {
                "id": test_session.device_id,
                "serial": test_data.device_serial
            },
            "required_tools": [
                "Czujnik ciśnienia",
                "Manometr",
                "Klucz montażowy 8mm"
            ],
            "safety_notes": [
                "Sprawdź połączenia pneumatyczne",
                "Upewnij się że zawór jest zamknięty",
                "Załóż rękawice ochronne"
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{test_session_id}")
async def get_test_session(
    test_session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get test session details
    """
    test_service = TestService(db)
    session = test_service.get_test_session(test_session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    return {
        "test_session_id": session.session_id,
        "status": session.status,
        "current_step": session.current_step,
        "total_steps": session.total_steps,
        "result": session.result,
        "start_time": session.start_time.isoformat(),
        "device_id": session.device_id,
        "operator_id": session.operator_id
    }


@router.post("/{test_session_id}/step/{step_id}")
async def submit_test_step(
    test_session_id: str,
    step_id: int,
    step_data: TestStepData,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit test step results
    """
    test_service = TestService(db)
    
    try:
        step_result = test_service.submit_step_result(
            test_session_id=test_session_id,
            step_id=step_id,
            step_name=step_data.step_name,
            result=step_data.result,
            measurements=step_data.measurements,
            operator_checks=step_data.operator_checks,
            operator_notes=step_data.operator_notes,
            photos=step_data.photos,
            duration=step_data.duration
        )
        
        return {
            "status": "success",
            "step_id": step_id,
            "result": step_data.result,
            "next_step": step_id + 1
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{test_session_id}/complete")
async def complete_test(
    test_session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Complete test session
    """
    test_service = TestService(db)
    
    try:
        session = test_service.complete_test_session(test_session_id)
        
        return {
            "test_session_id": session.session_id,
            "status": "completed",
            "result": session.result,
            "duration": session.actual_duration,
            "next_test_date": (datetime.utcnow() + timedelta(days=365)).date().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{test_session_id}/report")
async def get_test_report(
    test_session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate test report
    """
    test_service = TestService(db)
    session = test_service.get_test_session(test_session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    steps = db.query(TestStepResult).filter(
        TestStepResult.test_session_id == session.id
    ).order_by(TestStepResult.step_order).all()
    
    return {
        "test_session_id": session.session_id,
        "result": session.result,
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "duration": session.actual_duration,
        "steps": [
            {
                "step_id": step.step_id,
                "step_name": step.step_name,
                "result": step.result,
                "duration": step.duration,
                "measurements": step.measurements
            }
            for step in steps
        ]
    }


# WebSocket for real-time updates
@router.websocket("/ws/{test_session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    test_session_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket connection for real-time sensor data and test updates
    """
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "sensor_reading":
                # Store sensor reading
                sensor_data = SensorUpdate(**message.get("data", {}))
                
                # Get test session
                test_service = TestService(db)
                session = test_service.get_test_session(test_session_id)
                
                if session:
                    reading = SensorReading(
                        test_session_id=session.id,
                        step_id=message.get("step_id"),
                        sensor_type=sensor_data.sensor_type,
                        value=sensor_data.value,
                        unit=sensor_data.unit,
                        sensor_id=sensor_data.sensor_id
                    )
                    db.add(reading)
                    db.commit()
                
                # Echo back to client
                await websocket.send_json({
                    "type": "sensor_update_confirmed",
                    "test_session_id": test_session_id,
                    "data": sensor_data.dict()
                })
    
    except WebSocketDisconnect:
        print(f"Client disconnected from test session {test_session_id}")
