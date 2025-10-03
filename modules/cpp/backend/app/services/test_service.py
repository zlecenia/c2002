"""
Test business logic service
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid

from ..models.test_models import TestSession, TestStepResult, SensorReading


class TestService:
    """Service for test session management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_test_id(self) -> str:
        """Generate unique test session ID"""
        return f"TEST-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
    
    def create_test_session(
        self,
        device_serial: str,
        scenario_id: int,
        operator_id: int,
        customer_id: Optional[int],
        device_kind_id: int,
        device_type_id: int,
        test_kind_id: int
    ) -> TestSession:
        """Create new test session"""
        
        # Check if device has active test
        # Note: This assumes Device model exists in the main app
        # from ..models import Device
        # device = self.db.query(Device).filter(
        #     Device.device_number == device_serial
        # ).first()
        # 
        # if not device:
        #     raise ValueError("Device not found")
        
        # Mock device_id for now
        device_id = 1
        
        active_test = self.db.query(TestSession).filter(
            TestSession.device_id == device_id,
            TestSession.status.in_(['initialized', 'in_progress'])
        ).first()
        
        if active_test:
            raise ValueError("Device already has an active test session")
        
        # Get scenario details (mock for now)
        total_steps = self._get_scenario_steps_count(scenario_id)
        estimated_duration = self._calculate_estimated_duration(scenario_id)
        
        # Create test session
        test_session = TestSession(
            session_id=self.generate_test_id(),
            device_id=device_id,
            scenario_id=scenario_id,
            operator_id=operator_id,
            customer_id=customer_id,
            workshop_id=1,  # Default workshop
            status='initialized',
            start_time=datetime.utcnow(),
            estimated_duration=estimated_duration,
            total_steps=total_steps,
            current_step=0,
            meta_data={
                'device_kind_id': device_kind_id,
                'device_type_id': device_type_id,
                'test_kind_id': test_kind_id
            }
        )
        
        self.db.add(test_session)
        self.db.commit()
        self.db.refresh(test_session)
        
        return test_session
    
    def get_test_session(self, session_id: str) -> Optional[TestSession]:
        """Get test session by ID"""
        return self.db.query(TestSession).filter(
            TestSession.session_id == session_id
        ).first()
    
    def submit_step_result(
        self,
        test_session_id: str,
        step_id: int,
        step_name: str,
        result: str,
        measurements: Optional[Dict],
        operator_checks: Optional[Dict],
        operator_notes: Optional[str],
        photos: Optional[List[str]],
        duration: int
    ) -> TestStepResult:
        """Submit test step result"""
        
        session = self.get_test_session(test_session_id)
        if not session:
            raise ValueError("Test session not found")
        
        if session.status not in ['initialized', 'in_progress']:
            raise ValueError("Test session is not active")
        
        # Create step result
        step_result = TestStepResult(
            test_session_id=session.id,
            step_id=step_id,
            step_name=step_name,
            step_order=step_id,
            status='completed',
            result=result,
            measurements=measurements,
            operator_checks=operator_checks,
            operator_notes=operator_notes,
            photos=photos or [],
            duration=duration,
            start_time=datetime.utcnow() - timedelta(seconds=duration),
            end_time=datetime.utcnow()
        )
        
        self.db.add(step_result)
        
        # Update session
        session.current_step = step_id
        session.status = 'in_progress'
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(step_result)
        
        return step_result
    
    def complete_test_session(self, session_id: str) -> TestSession:
        """Complete test session and calculate final result"""
        
        session = self.get_test_session(session_id)
        if not session:
            raise ValueError("Test session not found")
        
        # Get all step results
        steps = self.db.query(TestStepResult).filter(
            TestStepResult.test_session_id == session.id
        ).all()
        
        # Calculate final result
        failed_steps = [s for s in steps if s.result == 'FAILED']
        warning_steps = [s for s in steps if s.result == 'WARNING']
        
        if failed_steps:
            final_result = 'FAILED'
        elif warning_steps:
            final_result = 'WARNING'
        else:
            final_result = 'PASSED'
        
        # Calculate actual duration
        if session.start_time:
            actual_duration = int((datetime.utcnow() - session.start_time).total_seconds() / 60)
        else:
            actual_duration = 0
        
        # Update session
        session.status = 'completed'
        session.result = final_result
        session.end_time = datetime.utcnow()
        session.actual_duration = actual_duration
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def abort_test_session(self, session_id: str, reason: str = None) -> TestSession:
        """Abort test session"""
        
        session = self.get_test_session(session_id)
        if not session:
            raise ValueError("Test session not found")
        
        session.status = 'aborted'
        session.result = 'ABORTED'
        session.end_time = datetime.utcnow()
        
        if reason:
            if not session.meta_data:
                session.meta_data = {}
            session.meta_data['abort_reason'] = reason
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def _get_scenario_steps_count(self, scenario_id: int) -> int:
        """Get number of steps for scenario (mock)"""
        # This would query TestScenario model
        scenario_steps = {
            1: 7,  # Standard test - 7 steps
            2: 4,  # Quick test - 4 steps
            3: 9,  # Extended test - 9 steps
        }
        return scenario_steps.get(scenario_id, 5)
    
    def _calculate_estimated_duration(self, scenario_id: int) -> int:
        """Calculate estimated test duration in minutes (mock)"""
        scenario_durations = {
            1: 45,  # Standard test - 45 min
            2: 20,  # Quick test - 20 min
            3: 90,  # Extended test - 90 min
        }
        return scenario_durations.get(scenario_id, 30)
