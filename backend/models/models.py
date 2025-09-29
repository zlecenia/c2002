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
    role = Column(String(50), nullable=False)  # operator, admin, superuser, developer, manager, configurator, maker
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

class Software(Base):
    __tablename__ = "software"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    vendor = Column(String(255))
    category = Column(String(100))  # firmware, application, driver, tool
    platform = Column(String(100))  # device platform compatibility
    license_type = Column(String(100))
    repository_url = Column(String(500))
    documentation_url = Column(String(500))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("SoftwareVersion", back_populates="software", cascade="all, delete-orphan")
    device_installations = relationship("DeviceSoftware", back_populates="software")

class SoftwareVersion(Base):
    __tablename__ = "software_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    version_number = Column(String(50), nullable=False)
    release_notes = Column(Text)
    changelog = Column(Text)
    file_path = Column(String(500))  # path to software file
    file_size = Column(Integer)  # size in bytes
    checksum = Column(String(64))  # SHA-256 checksum
    download_url = Column(String(500))
    is_stable = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    requires_reboot = Column(Boolean, default=False)
    compatibility = Column(JSON)  # device compatibility info
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True))
    
    # Relationships
    software = relationship("Software", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])
    installations = relationship("SoftwareInstallation", back_populates="version")

class DeviceSoftware(Base):
    __tablename__ = "device_software"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("software_versions.id"))
    installed_version = Column(String(50))
    installation_status = Column(String(50), default='not_installed')  # not_installed, installing, installed, failed, outdated
    installation_date = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    configuration = Column(JSON)  # software-specific configuration
    notes = Column(Text)
    
    # Relationships
    device = relationship("Device")
    software = relationship("Software", back_populates="device_installations")
    version = relationship("SoftwareVersion")

class SoftwareInstallation(Base):
    __tablename__ = "software_installations"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("software_versions.id"), nullable=False)
    action = Column(String(50), nullable=False)  # install, update, uninstall, rollback
    status = Column(String(50), default='pending')  # pending, in_progress, completed, failed, cancelled
    initiated_by = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    installation_log = Column(Text)
    previous_version = Column(String(50))
    new_version = Column(String(50))
    rollback_point = Column(JSON)  # data needed for rollback
    
    # Relationships
    device = relationship("Device")
    version = relationship("SoftwareVersion", back_populates="installations")
    initiator = relationship("User", foreign_keys=[initiated_by])