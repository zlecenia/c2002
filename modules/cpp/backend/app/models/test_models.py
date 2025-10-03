"""
Test-related database models for Connect++ (CPP)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, ARRAY, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..db.base import Base


class TestSession(Base):
    """Test session tracking"""
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("test_scenarios.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    workshop_id = Column(Integer, ForeignKey("workshops.id"))
    
    status = Column(String(50), nullable=False)  # initialized, in_progress, completed, aborted, failed
    
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    estimated_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)
    
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)
    
    result = Column(String(50))  # PASSED, FAILED, WARNING
    
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="test_sessions")
    scenario = relationship("TestScenario", back_populates="test_sessions")
    operator = relationship("User", back_populates="test_sessions")
    step_results = relationship("TestStepResult", back_populates="test_session", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="test_session", cascade="all, delete-orphan")


class TestStepResult(Base):
    """Individual test step results"""
    __tablename__ = "test_step_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    step_id = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    status = Column(String(50))  # pending, in_progress, completed, skipped, failed
    result = Column(String(50))  # PASSED, FAILED, WARNING, N/A
    
    automatic = Column(Boolean, default=False)
    operator_participation = Column(Boolean, default=True)
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # seconds
    
    measurements = Column(JSON)
    operator_checks = Column(JSON)
    operator_notes = Column(Text)
    photos = Column(ARRAY(Text))  # array of photo URLs
    
    criteria = Column(JSON)
    criteria_met = Column(Boolean)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    test_session = relationship("TestSession", back_populates="step_results")


class SensorReading(Base):
    """Time-series sensor data"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False, index=True)
    step_id = Column(Integer)
    
    sensor_type = Column(String(50))  # pressure_low, pressure_medium, pressure_high, flow, temperature
    sensor_id = Column(String(100))
    
    value = Column(DECIMAL(10, 3))
    unit = Column(String(20))
    
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    metadata = Column(JSON)
    
    # Relationships
    test_session = relationship("TestSession", back_populates="sensor_readings")


class Workshop(Base):
    """Workshop/facility information"""
    __tablename__ = "workshops"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    address = Column(Text)
    contact_info = Column(JSON)
    
    capacity = Column(Integer)
    active_devices = Column(Integer, default=0)
    
    configuration = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    equipment = relationship("EquipmentInventory", back_populates="workshop")
    spare_parts = relationship("SparePart", back_populates="workshop")


class EquipmentInventory(Base):
    """Equipment tracking and maintenance schedule"""
    __tablename__ = "equipment_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    status = Column(String(50), index=True)  # active, warning, expired, maintenance, retired
    location = Column(String(255))
    
    last_test_date = Column(DateTime)
    next_test_date = Column(DateTime, index=True)
    test_interval = Column(Integer)  # days
    
    maintenance_notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    workshop = relationship("Workshop", back_populates="equipment")
    device = relationship("Device", back_populates="equipment_records")


class SparePart(Base):
    """Spare parts inventory"""
    __tablename__ = "spare_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False)
    
    part_name = Column(String(255), nullable=False)
    part_number = Column(String(100), unique=True, nullable=False)
    sku = Column(String(100))
    
    category = Column(String(100))
    compatible_devices = Column(ARRAY(Text))  # array of device types
    
    stock_quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=10)
    unit_price = Column(DECIMAL(10, 2))
    currency = Column(String(3), default='PLN')
    
    supplier_info = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    workshop = relationship("Workshop", back_populates="spare_parts")
