from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    role = Column(String(50), nullable=False)  # operator, admin, superuser, developer
    qr_code = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    created_scenarios = relationship("TestScenario", back_populates="creator")
    test_reports = relationship("TestReport", back_populates="operator")
    system_logs = relationship("SystemLog", back_populates="user")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    devices = relationship("Device", back_populates="customer")
    test_reports = relationship("TestReport", back_populates="customer")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_number = Column(String(100), unique=True, nullable=False, index=True)
    device_type = Column(String(100), nullable=False)
    kind_of_device = Column(String(100))
    serial_number = Column(String(100))
    status = Column(String(50), default='active')
    customer_id = Column(Integer, ForeignKey("customers.id"))
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="devices")
    test_reports = relationship("TestReport", back_populates="device")

class TestScenario(Base):
    __tablename__ = "test_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    device_type = Column(String(100))
    test_flow = Column(JSON)  # Structure of test steps
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_scenarios")
    test_steps = relationship("TestStep", back_populates="scenario")
    test_reports = relationship("TestReport", back_populates="test_scenario")

class TestStep(Base):
    __tablename__ = "test_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("test_scenarios.id"))
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    description = Column(Text)
    parameters = Column(JSON)
    criteria = Column(JSON)
    auto_test = Column(Boolean, default=False)
    operator_participation = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scenario = relationship("TestScenario", back_populates="test_steps")

class TestReport(Base):
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    test_scenario_id = Column(Integer, ForeignKey("test_scenarios.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    operator_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    status = Column(String(50))  # pending, in_progress, completed, failed
    results = Column(JSON)
    pressure_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    test_scenario = relationship("TestScenario", back_populates="test_reports")
    device = relationship("Device", back_populates="test_reports")
    operator = relationship("User", back_populates="test_reports")
    customer = relationship("Customer", back_populates="test_reports")

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String(50))  # INFO, WARNING, ERROR, HELP
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="system_logs")

class Configuration(Base):
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    component = Column(String(50))  # CPP, CM, FDM, FCM, FSM
    updated_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False)
    language = Column(String(10), nullable=False)
    value = Column(Text, nullable=False)
    component = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())