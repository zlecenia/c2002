from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import get_db, engine
from backend.models.models import (Base, User, Device, Customer, TestScenario, TestStep, 
                                    Software, SoftwareVersion, DeviceSoftware, Configuration, 
                                    TestReport, SystemLog)
from backend.api.auth_router import router as auth_router
from backend.api.users_router import router as users_router
from backend.auth.auth import get_password_hash, generate_qr_code
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(users_router, prefix=settings.api_v1_str)

# Import and include scenarios router
from backend.api.scenarios_router import router as scenarios_router
app.include_router(scenarios_router, prefix=settings.api_v1_str)

# Import and include fleet data router
from backend.api.fleet_data_router import router as fleet_data_router
app.include_router(fleet_data_router, prefix=settings.api_v1_str)

# Import and include fleet config router
from backend.api.fleet_config_router import router as fleet_config_router
app.include_router(fleet_config_router, prefix=settings.api_v1_str)

# Import and include fleet software router
from backend.api.fleet_software_router import router as fleet_software_router
app.include_router(fleet_software_router, prefix=settings.api_v1_str)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize sample data endpoint
@app.post("/api/v1/init-data")
def initialize_sample_data(db: Session = Depends(get_db)):
    """Initialize database with comprehensive sample data for all modules."""
    try:
        counts = {}
        
        # 1. CREATE USERS
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("pass"),
                email="admin@fleetmanagement.com",
                role="superuser",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(admin_user)
        
        operator_user = db.query(User).filter(User.username == "operator1").first()
        if not operator_user:
            operator_user = User(
                username="operator1",
                password_hash=get_password_hash("pass"),
                email="operator1@fleetmanagement.com",
                role="operator",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(operator_user)
        
        manager_user = db.query(User).filter(User.username == "manager1").first()
        if not manager_user:
            manager_user = User(
                username="manager1",
                password_hash=get_password_hash("pass"),
                email="manager1@fleetmanagement.com",
                role="manager",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(manager_user)
        
        configurator_user = db.query(User).filter(User.username == "configurator1").first()
        if not configurator_user:
            configurator_user = User(
                username="configurator1",
                password_hash=get_password_hash("pass"),
                email="configurator1@fleetmanagement.com",
                role="configurator",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(configurator_user)
        
        maker_user = db.query(User).filter(User.username == "maker1").first()
        if not maker_user:
            maker_user = User(
                username="maker1",
                password_hash=get_password_hash("pass"),
                email="maker1@fleetmanagement.com",
                role="maker",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(maker_user)
        
        db.flush()
        counts['users'] = 5
        
        # 2. CREATE CUSTOMERS
        existing_customers = db.query(Customer).count()
        if existing_customers == 0:
            customers_data = [
                {"name": "Szpital Wojewódzki w Warszawie", "contact_info": {"email": "kontakt@szpital-warszawa.pl", "phone": "+48 22 123 4567", "address": "ul. Szpitalna 1, 00-001 Warszawa"}},
                {"name": "Przychodnia Medyczna Poznań", "contact_info": {"email": "recepcja@medyczna-poznan.pl", "phone": "+48 61 234 5678"}},
                {"name": "Centrum Zdrowia Kraków", "contact_info": {"email": "info@centrum-krakow.pl", "phone": "+48 12 345 6789"}},
                {"name": "Klinika Prywatna Gdańsk", "contact_info": {"email": "kontakt@klinika-gdansk.pl", "phone": "+48 58 456 7890"}},
                {"name": "Laboratorium Diagnostyczne Wrocław", "contact_info": {"email": "lab@diagnostyka-wroclaw.pl", "phone": "+48 71 567 8901"}}
            ]
            for cust_data in customers_data:
                customer = Customer(**cust_data)
                db.add(customer)
            db.flush()
            counts['customers'] = len(customers_data)
        
        # 3. CREATE DEVICES
        customers = db.query(Customer).all()
        existing_devices = db.query(Device).count()
        if existing_devices == 0 and customers:
            devices_data = [
                {"device_number": "MT-001", "device_type": "mask_tester", "kind_of_device": "Medical Test Device", 
                 "serial_number": "SN2024001", "status": "active", "customer_id": customers[0].id,
                 "configuration": {"test_mode": "automatic", "pressure_range": "0-50 mbar"}},
                {"device_number": "MT-002", "device_type": "mask_tester", "kind_of_device": "Medical Test Device",
                 "serial_number": "SN2024002", "status": "active", "customer_id": customers[1].id,
                 "configuration": {"test_mode": "manual", "pressure_range": "0-50 mbar"}},
                {"device_number": "PS-001", "device_type": "pressure_sensor", "kind_of_device": "Sensor Device",
                 "serial_number": "SN2024003", "status": "active", "customer_id": customers[2].id,
                 "configuration": {"sensitivity": "high", "calibration_date": "2024-01-15"}},
                {"device_number": "FM-001", "device_type": "flow_meter", "kind_of_device": "Flow Measurement",
                 "serial_number": "SN2024004", "status": "maintenance", "customer_id": customers[3].id,
                 "configuration": {"flow_range": "0-100 L/min"}},
                {"device_number": "MT-003", "device_type": "mask_tester", "kind_of_device": "Medical Test Device",
                 "serial_number": "SN2024005", "status": "active", "customer_id": customers[4].id,
                 "configuration": {"test_mode": "automatic", "pressure_range": "0-50 mbar"}}
            ]
            for dev_data in devices_data:
                device = Device(**dev_data)
                db.add(device)
            db.flush()
            counts['devices'] = len(devices_data)
        
        # 4. CREATE TEST SCENARIOS WITH STEPS
        existing_scenarios = db.query(TestScenario).filter(TestScenario.created_by == admin_user.id).count()
        if existing_scenarios < 3:
            scenarios_data = [
                {
                    "name": "Test Szczelności Maski Standardowy",
                    "description": "Kompletny test szczelności maski z pomiarem ciśnienia",
                    "device_type": "mask_tester",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "standard", "duration": "300s", "pressure": "30 mbar"},
                    "steps": [
                        {"step_order": 1, "step_name": "Przygotowanie urządzenia", "description": "Sprawdzenie połączeń i kalibracja"},
                        {"step_order": 2, "step_name": "Założenie maski", "description": "Poprawne umieszczenie maski na manekinie"},
                        {"step_order": 3, "step_name": "Test ciśnienia", "description": "Pomiar szczelności przy 30 mbar", "parameters": {"pressure": 30}},
                        {"step_order": 4, "step_name": "Raport końcowy", "description": "Generowanie raportu z wynikami testu"}
                    ]
                },
                {
                    "name": "Kalibracja Czujnika Ciśnienia",
                    "description": "Procedura kalibracji czujników ciśnienia",
                    "device_type": "pressure_sensor",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "calibration", "points": 5},
                    "steps": [
                        {"step_order": 1, "step_name": "Reset urządzenia", "description": "Przywrócenie ustawień fabrycznych", "auto_test": True},
                        {"step_order": 2, "step_name": "Pomiar punktu zerowego", "description": "Kalibracja przy ciśnieniu atmosferycznym"},
                        {"step_order": 3, "step_name": "Pomiar punktów referencyjnych", "description": "5 punktów kalibracyjnych", "parameters": {"points": [10, 20, 30, 40, 50]}}
                    ]
                },
                {
                    "name": "Test Przepływu Szybki",
                    "description": "Szybki test przepływomierza",
                    "device_type": "flow_meter",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "quick", "duration": "60s"},
                    "steps": [
                        {"step_order": 1, "step_name": "Uruchomienie przepływu", "description": "Start pomiaru przepływu"},
                        {"step_order": 2, "step_name": "Odczyt wartości", "description": "Pomiar w czasie rzeczywistym", "auto_test": True}
                    ]
                }
            ]
            
            for scen_data in scenarios_data:
                steps_data = scen_data.pop('steps')
                scenario = TestScenario(**scen_data)
                db.add(scenario)
                db.flush()
                
                for step_data in steps_data:
                    step = TestStep(scenario_id=scenario.id, **step_data)
                    db.add(step)
            
            db.flush()
            counts['scenarios'] = len(scenarios_data)
        
        # 5. CREATE SOFTWARE AND VERSIONS
        existing_software = db.query(Software).count()
        if existing_software == 0:
            software_data = [
                {
                    "name": "MaskTester Firmware",
                    "description": "Oprogramowanie sterujące dla testerów masek",
                    "vendor": "FleetTech Solutions",
                    "category": "firmware",
                    "platform": "mask_tester",
                    "license_type": "Proprietary",
                    "created_by": maker_user.id,
                    "versions": [
                        {"version_number": "1.0.0", "release_notes": "Pierwsza wersja stabilna", "is_stable": True, "file_path": "/firmware/masktester_v1.0.0.bin"},
                        {"version_number": "1.1.0", "release_notes": "Optymalizacja pomiarów ciśnienia", "is_stable": True, "file_path": "/firmware/masktester_v1.1.0.bin"},
                        {"version_number": "1.2.0-beta", "release_notes": "Nowy interfejs użytkownika (beta)", "is_stable": False, "file_path": "/firmware/masktester_v1.2.0-beta.bin"}
                    ]
                },
                {
                    "name": "Pressure Sensor Driver",
                    "description": "Sterownik dla czujników ciśnienia",
                    "vendor": "SensorTech",
                    "category": "driver",
                    "platform": "pressure_sensor",
                    "license_type": "Open Source (MIT)",
                    "created_by": maker_user.id,
                    "versions": [
                        {"version_number": "2.0.1", "release_notes": "Poprawki stabilności", "is_stable": True, "file_path": "/drivers/pressure_sensor_v2.0.1.drv"}
                    ]
                },
                {
                    "name": "Flow Meter Calibration Tool",
                    "description": "Narzędzie do kalibracji przepływomierzy",
                    "vendor": "FleetTech Solutions",
                    "category": "tool",
                    "platform": "flow_meter",
                    "license_type": "Proprietary",
                    "created_by": maker_user.id,
                    "versions": [
                        {"version_number": "3.1.0", "release_notes": "Automatyczna kalibracja wielopunktowa", "is_stable": True, "file_path": "/tools/flowmeter_cal_v3.1.0.exe"}
                    ]
                }
            ]
            
            for soft_data in software_data:
                versions_data = soft_data.pop('versions')
                software = Software(**soft_data)
                db.add(software)
                db.flush()
                
                for ver_data in versions_data:
                    version = SoftwareVersion(software_id=software.id, **ver_data)
                    db.add(version)
            
            db.flush()
            counts['software'] = len(software_data)
        
        # 6. CREATE SYSTEM CONFIGURATIONS
        existing_configs = db.query(Configuration).count()
        if existing_configs == 0:
            configs_data = [
                {"config_key": "cpp_test_timeout", "config_value": {"value": 300, "unit": "seconds"}, "component": "CPP", "updated_by": configurator_user.id},
                {"config_key": "cm_max_scenarios", "config_value": {"value": 100}, "component": "CM", "updated_by": configurator_user.id},
                {"config_key": "fdm_backup_interval", "config_value": {"value": 24, "unit": "hours"}, "component": "FDM", "updated_by": configurator_user.id},
                {"config_key": "fcm_auto_backup", "config_value": {"enabled": True, "retention_days": 30}, "component": "FCM", "updated_by": configurator_user.id},
                {"config_key": "fsm_update_channel", "config_value": {"channel": "stable", "auto_update": False}, "component": "FSM", "updated_by": configurator_user.id}
            ]
            
            for conf_data in configs_data:
                config = Configuration(**conf_data)
                db.add(config)
            
            db.flush()
            counts['configurations'] = len(configs_data)
        
        db.commit()
        
        return {
            "message": "✅ Testowe dane zostały pomyślnie dodane do bazy",
            "summary": counts
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd inicjalizacji danych: {str(e)}")

# Basic API endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fleet Management System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #2c3e50;
                min-height: 100vh;
            }
            .hero {
                text-align: center;
                padding: 60px 20px 40px;
                color: white;
            }
            .hero h1 {
                font-size: 3em;
                margin-bottom: 10px;
                font-weight: 700;
            }
            .hero p {
                font-size: 1.3em;
                opacity: 0.95;
                margin-bottom: 10px;
            }
            .version {
                font-size: 0.9em;
                opacity: 0.8;
                margin-top: 10px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .modules-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 25px;
                margin: 30px 0;
            }
            .module-card {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                text-decoration: none;
                display: block;
                border: 2px solid transparent;
            }
            .module-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.2);
                border-color: #3498db;
            }
            .module-icon {
                font-size: 3em;
                margin-bottom: 15px;
                display: block;
            }
            .module-card h3 {
                color: #2c3e50;
                font-size: 1.5em;
                margin-bottom: 10px;
            }
            .module-card p {
                color: #7f8c8d;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .module-card .role {
                display: inline-block;
                background: #ecf0f1;
                color: #34495e;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 500;
            }
            .api-section {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                text-align: center;
            }
            .api-section h2 {
                color: #2c3e50;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 15px 35px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s ease;
                margin: 10px;
                font-size: 1.1em;
            }
            .btn:hover {
                background: #2980b9;
            }
            .btn-secondary {
                background: #95a5a6;
            }
            .btn-secondary:hover {
                background: #7f8c8d;
            }
            .footer {
                text-align: center;
                padding: 30px;
                color: white;
                opacity: 0.9;
            }
            @media (max-width: 768px) {
                .hero h1 { font-size: 2em; }
                .hero p { font-size: 1.1em; }
                .modules-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>⚙️ Fleet Management System</h1>
            <p>Kompleksowy system zarządzania flotą urządzeń</p>
            <p class="version">Wersja 1.0.0</p>
        </div>

        <div class="container">
            <div class="modules-grid">
                <a href="/connect-plus" class="module-card">
                    <span class="module-icon">🔗</span>
                    <h3>Connect++</h3>
                    <p>Interfejs testowania urządzeń dla operatorów. Obsługa testów i diagnostyka w czasie rzeczywistym.</p>
                    <span class="role">👤 Operator</span>
                </a>

                <a href="/commands-manager" class="module-card">
                    <span class="module-icon">⚙️</span>
                    <h3>Commands Manager</h3>
                    <p>Tworzenie i zarządzanie scenariuszami testowymi. Pełna kontrola nad procedurami testowymi.</p>
                    <span class="role">🔑 Superuser</span>
                </a>

                <a href="/fleet-data-manager" class="module-card">
                    <span class="module-icon">📊</span>
                    <h3>Fleet Data Manager</h3>
                    <p>Zarządzanie danymi urządzeń i klientów. Dashboard analityczny i raporty.</p>
                    <span class="role">📈 Manager</span>
                </a>

                <a href="/fleet-config-manager" class="module-card">
                    <span class="module-icon">🔧</span>
                    <h3>Fleet Config Manager</h3>
                    <p>Konfiguracja systemu i urządzeń. Backup i restore konfiguracji.</p>
                    <span class="role">⚡ Configurator</span>
                </a>

                <a href="/fleet-software-manager" class="module-card">
                    <span class="module-icon">💾</span>
                    <h3>Fleet Software Manager</h3>
                    <p>Zarządzanie oprogramowaniem i wersjami. Instalacja i aktualizacje w całej flocie.</p>
                    <span class="role">🛠️ Maker</span>
                </a>
            </div>

            <div class="api-section">
                <h2>📚 Dokumentacja i API</h2>
                <a href="/docs" class="btn">Dokumentacja API (Swagger)</a>
                <a href="/health" class="btn btn-secondary">Status Systemu</a>
            </div>
        </div>

        <div class="footer">
            <p><strong>Fleet Management System</strong> - Professional Device Fleet Management</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Aby zainicjalizować przykładowe dane: <code>POST /api/v1/init-data</code>
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Public endpoints for Connect++ demo (no auth required)
@app.get("/api/v1/demo/users")
async def get_demo_users(db: Session = Depends(get_db)):
    users = db.query(User).limit(10).all()
    return {"users": [{"id": user.id, "username": user.username, "role": user.role} for user in users]}

@app.get("/api/v1/devices")
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return {"devices": [{"id": device.id, "device_number": device.device_number, "device_type": device.device_type} for device in devices]}

@app.get("/api/v1/customers")
async def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return {"customers": [{"id": customer.id, "name": customer.name} for customer in customers]}

@app.get("/api/v1/test-scenarios")
async def get_test_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(TestScenario).all()
    return {"scenarios": [{"id": scenario.id, "name": scenario.name, "device_type": scenario.device_type} for scenario in scenarios]}

# Connect++ Module (port 8080)
@app.get("/connect-plus", response_class=HTMLResponse)
async def connect_plus():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connect++ - Fleet Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .nav-menu { background: #2c3e50; padding: 0; margin: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; }
            .nav-menu li { margin: 0; }
            .nav-menu a { display: block; padding: 15px 20px; color: white; text-decoration: none; transition: background 0.3s; }
            .nav-menu a:hover { background: #34495e; }
            .nav-menu a.active { background: #3498db; }
            h1 { display: none; }
            .module-info { display: none; }
            .app-container { display: flex; min-height: calc(100vh - 52px); }
            .sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .sidebar .menu-section { margin-top: 20px; }
            .sidebar .menu-item { display: block; padding: 12px; background: #34495e; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 8px; cursor: pointer; transition: background 0.3s; }
            .sidebar .menu-item:hover { background: #7f8c8d; }
            .sidebar .menu-item.active { background: #3498db; font-weight: bold; }
            .main-content-area { width: 70%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
            .right-sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .right-sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .right-sidebar .login-section { background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .right-sidebar .login-section input { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #95a5a6; border-radius: 4px; box-sizing: border-box; }
            .right-sidebar .login-section button { width: 100%; margin-bottom: 5px; }
            .right-sidebar .role-switcher { margin-top: 15px; padding: 10px; background: #34495e; border-radius: 8px; display: none; }
            .right-sidebar .role-switcher select { width: 100%; padding: 8px; border: 1px solid #95a5a6; border-radius: 4px; background: white; }
            .container { max-width: 100%; margin: 0; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .api-test { margin: 20px 0; }
            button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #2980b9; }
            .result { margin: 10px 0; padding: 10px; background: #d5edda; border-radius: 5px; border: 1px solid #c3e6cb; }
            
            @media (max-width: 768px) {
                .app-container { flex-direction: column; }
                .sidebar { width: 100%; height: auto; position: relative; border-bottom: 2px solid #34495e; }
                .main-content-area { width: 100%; }
                .right-sidebar { width: 100%; height: auto; position: relative; border-top: 2px solid #34495e; }
            }
        </style>
    </head>
    <body>
        <nav class="nav-menu">
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/connect-plus" class="active">🔗 Connect++</a></li>
                <li><a href="/commands-manager">⚙️ Commands Manager</a></li>
                <li><a href="/fleet-data-manager">📊 Fleet Data Manager</a></li>
                <li><a href="/fleet-config-manager">🔧 Fleet Config Manager</a></li>
                <li><a href="/fleet-software-manager">💿 Fleet Software Manager</a></li>
                <li><a href="/docs">📚 API Docs</a></li>
            </ul>
        </nav>
        <div class="app-container">
            <div class="sidebar">
                <h3>🔗 Menu Modułu</h3>
                <div class="menu-section">
                    <div class="menu-item active">📊 Test API</div>
                    <div class="menu-item">🔧 Ustawienia</div>
                </div>
            </div>

            <div class="main-content-area">
                <div class="container">
                    <h1>🔗 Connect++ Module</h1>
                    <div class="module-info">
                        <h3>Moduł dla Operatorów</h3>
                        <p><strong>Port:</strong> 5000</p>
                        <p><strong>Rola:</strong> Operator</p>
                        <p><strong>Funkcje:</strong> Obsługa testów urządzeń</p>
                    </div>
                    
                    <div class="api-test">
                        <h3>Test API Endpoints:</h3>
                        <button onclick="testUsers()">Test Users</button>
                        <button onclick="testDevices()">Test Devices</button>
                        <button onclick="testCustomers()">Test Customers</button>
                        <button onclick="testScenarios()">Test Scenarios</button>
                        <div id="result"></div>
                    </div>
                </div>
            </div>

            <div class="right-sidebar">
                <h3>🔐 Logowanie</h3>
                <div class="login-section">
                    <input type="text" id="login-username" placeholder="Username">
                    <input type="password" id="login-password" placeholder="Password">
                    <button onclick="login()">Zaloguj</button>
                    <button onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                    <div id="auth-message" style="margin-top: 10px; font-size: 12px;"></div>
                </div>

                <div class="role-switcher" id="role-switcher">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #ecf0f1;">🔄 Przełącz rolę:</label>
                    <select id="role-select" onchange="switchRole()">
                        <option value="">Wybierz rolę...</option>
                    </select>
                </div>
            </div>
        </div>

        <script>
            let authToken = null;

            function getAuthToken() {
                if (!authToken) {
                    authToken = localStorage.getItem('jwt_token');
                }
                return authToken;
            }

            function setAuthToken(token) {
                authToken = token;
                localStorage.setItem('jwt_token', token);
                updateAuthUI();
            }

            function clearAuthToken() {
                authToken = null;
                localStorage.removeItem('jwt_token');
                updateAuthUI();
            }

            function updateAuthUI() {
                const isLoggedIn = !!getAuthToken();
                document.getElementById('login-username').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('login-password').style.display = isLoggedIn ? 'none' : 'inline';
                document.querySelector('button[onclick="login()"]').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('logout-btn').style.display = isLoggedIn ? 'inline' : 'none';
                
                if (isLoggedIn) {
                    const userRoles = getUserRoles();
                    const activeRole = getActiveRole();
                    
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #3498db;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
                    
                    if (userRoles && userRoles.length > 1) {
                        const roleSelect = document.getElementById('role-select');
                        roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
                        userRoles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                            if (role === activeRole) {
                                option.selected = true;
                            }
                            roleSelect.appendChild(option);
                        });
                        document.getElementById('role-switcher').style.display = 'block';
                    } else {
                        document.getElementById('role-switcher').style.display = 'none';
                    }
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
                    document.getElementById('role-switcher').style.display = 'none';
                }
            }

            function getUserRoles() {
                const token = getAuthToken();
                if (!token) return [];
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.roles || [];
                } catch (e) {
                    return [];
                }
            }

            function getActiveRole() {
                const token = getAuthToken();
                if (!token) return '';
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.active_role || payload.role || '';
                } catch (e) {
                    return '';
                }
            }

            async function switchRole() {
                const selectedRole = document.getElementById('role-select').value;
                if (!selectedRole) return;

                try {
                    const response = await fetch('/api/v1/auth/switch-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify({ new_role: selectedRole })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #3498db;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd przełączania roli: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            async function login() {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    alert('Podaj username i hasło');
                    return;
                }

                try {
                    const formData = new URLSearchParams();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #3498db;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd logowania: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function logout() {
                clearAuthToken();
                document.getElementById('login-username').value = '';
                document.getElementById('login-password').value = '';
            }

            async function testAPI(endpoint, name) {
                try {
                    const response = await fetch('/api/v1/' + endpoint);
                    const data = await response.json();
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                            <strong>${name} API Response:</strong><br>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result" style="background: #f8d7da; border-color: #f5c6cb;">
                            <strong>Error:</strong> ${error.message}
                        </div>
                    `;
                }
            }

            function testUsers() { testAPI('demo/users', 'Users'); }
            function testDevices() { testAPI('devices', 'Devices'); }
            function testCustomers() { testAPI('customers', 'Customers'); }
            function testScenarios() { testAPI('test-scenarios', 'Test Scenarios'); }

            document.addEventListener('DOMContentLoaded', function() {
                updateAuthUI();
            });
        </script>
        </div>
    </body>
    </html>
    """

# Commands Manager Module
@app.get("/commands-manager", response_class=HTMLResponse)
async def commands_manager():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Commands Manager - Fleet Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .nav-menu { background: #2c3e50; padding: 0; margin: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; }
            .nav-menu li { margin: 0; }
            .nav-menu a { display: block; padding: 15px 20px; color: white; text-decoration: none; transition: background 0.3s; }
            .nav-menu a:hover { background: #34495e; }
            .nav-menu a.active { background: #e74c3c; }
            .header { display: none; }
            .module-info { display: none; }
            .auth-section { display: none; }
            .app-container { display: flex; min-height: calc(100vh - 52px); }
            .sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .sidebar .menu-section { margin-top: 20px; }
            .sidebar .menu-item { display: block; padding: 12px; background: #34495e; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 8px; cursor: pointer; transition: background 0.3s; }
            .sidebar .menu-item:hover { background: #7f8c8d; }
            .sidebar .menu-item.active { background: #e74c3c; font-weight: bold; }
            .main-content-area { width: 70%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
            .right-sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .right-sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .right-sidebar .login-section { background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .right-sidebar .login-section input { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #95a5a6; border-radius: 4px; box-sizing: border-box; }
            .right-sidebar .login-section button { width: 100%; margin-bottom: 5px; }
            .right-sidebar .role-switcher { margin-top: 15px; padding: 10px; background: #34495e; border-radius: 8px; display: none; }
            .right-sidebar .role-switcher select { width: 100%; padding: 8px; border: 1px solid #95a5a6; border-radius: 4px; background: white; }
            .container { max-width: 100%; margin: 0; padding: 0; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #c0392b; }
            .btn-secondary { background: #95a5a6; }
            .btn-secondary:hover { background: #7f8c8d; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .scenarios-list { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 10px; }
            .scenario-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
            .scenario-item:hover { background-color: #f8f9fa; }
            .scenario-item.active { background-color: #e74c3c; color: white; }
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; border-left: 4px solid #e74c3c; font-family: monospace; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
            .auth-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
            
            @media (max-width: 768px) {
                .app-container { flex-direction: column; }
                .sidebar { width: 100%; height: auto; position: relative; border-bottom: 2px solid #34495e; }
                .main-content-area { width: 100%; }
                .right-sidebar { width: 100%; height: auto; position: relative; border-top: 2px solid #34495e; }
                .main-content { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <nav class="nav-menu">
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/connect-plus">🔗 Connect++</a></li>
                <li><a href="/commands-manager" class="active">⚙️ Commands Manager</a></li>
                <li><a href="/fleet-data-manager">📊 Fleet Data Manager</a></li>
                <li><a href="/fleet-config-manager">🔧 Fleet Config Manager</a></li>
                <li><a href="/fleet-software-manager">💿 Fleet Software Manager</a></li>
                <li><a href="/docs">📚 API Docs</a></li>
            </ul>
        </nav>
        <div class="app-container">
            <div class="sidebar">
                <h3>⚙️ Menu Modułu</h3>
                <div class="menu-section">
                    <div class="menu-item active" onclick="showScenarios()">📋 Lista Scenariuszy</div>
                    <div class="menu-item" onclick="showCreateForm()">➕ Nowy Scenariusz</div>
                </div>
            </div>

            <div class="main-content-area">
            <div class="container">
            <div class="header">
                <h1>⚙️ Commands Manager</h1>
            </div>
            
            <div class="module-info">
                <h3>Moduł dla Superuser</h3>
                <p><strong>Port:</strong> 5000</p>
                <p><strong>Rola:</strong> Superuser</p>
                <p><strong>Funkcje:</strong> Tworzenie i zarządzanie scenariuszami testowymi</p>
            </div>

            <div class="main-content">
                <div class="section">
                    <h3>📋 Lista Scenariuszy Testowych</h3>
                    <button class="btn" onclick="loadScenarios()">Odśwież listę</button>
                    <div id="scenarios-list" class="scenarios-list">
                        <p>Kliknij "Odśwież listę" aby załadować scenariusze...</p>
                    </div>
                    
                    <h4>🔍 Szczegóły Scenariusza</h4>
                    <div id="scenario-details">
                        <p>Wybierz scenariusz z listy powyżej...</p>
                    </div>
                </div>

                <div class="section">
                    <h3>➕ Tworzenie Nowego Scenariusza</h3>
                    <form id="scenario-form">
                        <div class="form-group">
                            <label>Nazwa scenariusza:</label>
                            <input type="text" id="scenario-name" required>
                        </div>
                        <div class="form-group">
                            <label>Opis:</label>
                            <textarea id="scenario-description" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Typ urządzenia:</label>
                            <select id="device-type" onchange="loadTemplatesForType()">
                                <option value="">Wybierz typ urządzenia</option>
                                <option value="mask_tester">Tester masek</option>
                                <option value="pressure_sensor">Czujnik ciśnienia</option>
                                <option value="flow_meter">Przepływomierz</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>📋 Szablon JSON (opcjonalnie):</label>
                            <button type="button" class="btn btn-secondary" onclick="showTemplates()">🔽 Wybierz szablon JSON</button>
                            <div id="templates-list" style="display: none; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-top: 10px; border-radius: 4px;"></div>
                        </div>

                        <div class="form-group">
                            <label>📝 Konfiguracja test_flow:</label>
                            <div style="margin-bottom: 10px;">
                                <button type="button" class="btn btn-secondary" onclick="jsonTreeEditor.addField()">+ Dodaj pole</button>
                                <button type="button" class="btn btn-secondary" onclick="jsonTreeEditor.clear()">🗑️ Wyczyść</button>
                                <button type="button" class="btn btn-secondary" onclick="toggleJSONView()">👁️ Podgląd JSON</button>
                            </div>
                            <div id="json-tree-editor" style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background: #f8f9fa; max-height: 400px; overflow-y: auto;">
                                <!-- Tree editor będzie tu renderowany -->
                            </div>
                            <div id="json-preview" style="display: none; margin-top: 10px; padding: 10px; background: #2c3e50; color: #ecf0f1; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto;">
                                <!-- JSON preview -->
                            </div>
                            <small style="color: #7f8c8d;">Edytuj konfigurację używając pól powyżej lub wybierz szablon</small>
                        </div>

                        <button type="button" class="btn" onclick="createScenario()">Utwórz Scenariusz</button>
                    </form>
                </div>
            </div>

            <div id="result" style="margin-top: 20px;"></div>
            </div>
            </div>

            <div class="right-sidebar">
                <h3>🔐 Logowanie</h3>
                <div class="login-section">
                    <input type="text" id="login-username" placeholder="Username">
                    <input type="password" id="login-password" placeholder="Password">
                    <button class="btn btn-success" onclick="login()">Zaloguj</button>
                    <button class="btn btn-danger" onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                    <div id="auth-message" style="margin-top: 10px; font-size: 12px;"></div>
                </div>

                <div class="role-switcher" id="role-switcher">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #ecf0f1;">🔄 Przełącz rolę:</label>
                    <select id="role-select" onchange="switchRole()">
                        <option value="">Wybierz rolę...</option>
                    </select>
                </div>

                <div style="margin-top: 20px; padding: 15px; background: #34495e; border-radius: 8px;">
                    <h4 style="margin-top: 0; font-size: 14px; border-bottom: 2px solid #7f8c8d; padding-bottom: 8px;">🔍 API Endpoints Test</h4>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px;" onclick="testScenariosAPI()">Test /scenarios</button>
                    <button class="btn btn-secondary" style="width: 100%;" onclick="testAuth()">Test Auth</button>
                </div>
            </div>
        </div>

        <script>
            let currentScenarioId = null;
            let scenarios = [];

            let authToken = null;

            function getAuthToken() {
                if (!authToken) {
                    authToken = localStorage.getItem('jwt_token');
                }
                return authToken;
            }

            function setAuthToken(token) {
                authToken = token;
                localStorage.setItem('jwt_token', token);
                updateAuthUI();
            }

            function clearAuthToken() {
                authToken = null;
                localStorage.removeItem('jwt_token');
                updateAuthUI();
            }

            function updateAuthUI() {
                const isLoggedIn = !!getAuthToken();
                document.getElementById('login-username').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('login-password').style.display = isLoggedIn ? 'none' : 'inline';
                document.querySelector('button[onclick="login()"]').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('logout-btn').style.display = isLoggedIn ? 'inline' : 'none';
                
                if (isLoggedIn) {
                    const userRoles = getUserRoles();
                    const activeRole = getActiveRole();
                    
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: green;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
                    
                    // Show role switcher if user has multiple roles
                    if (userRoles && userRoles.length > 1) {
                        const roleSelect = document.getElementById('role-select');
                        roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
                        userRoles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                            if (role === activeRole) {
                                option.selected = true;
                            }
                            roleSelect.appendChild(option);
                        });
                        document.getElementById('role-switcher').style.display = 'block';
                    } else {
                        document.getElementById('role-switcher').style.display = 'none';
                    }
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
                    document.getElementById('role-switcher').style.display = 'none';
                }
            }

            function getUserRoles() {
                const token = getAuthToken();
                if (!token) return [];
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.roles || [];
                } catch (e) {
                    return [];
                }
            }

            function getActiveRole() {
                const token = getAuthToken();
                if (!token) return '';
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.active_role || payload.role || '';
                } catch (e) {
                    return '';
                }
            }

            async function switchRole() {
                const selectedRole = document.getElementById('role-select').value;
                if (!selectedRole) return;

                try {
                    const response = await fetch('/api/v1/auth/switch-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify({ new_role: selectedRole })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: green;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
                        
                        // Reload scenarios with new role
                        loadScenarios();
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd przełączania roli: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function showCreateForm() {
                const formSection = document.getElementById('scenario-form');
                if (formSection) {
                    formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }

            function showScenarios() {
                const scenariosSection = document.getElementById('scenarios-list');
                if (scenariosSection) {
                    scenariosSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }

            async function login() {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    alert('Podaj username i hasło');
                    return;
                }

                try {
                    const formData = new URLSearchParams();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: green;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Zalogowano pomyślnie jako ${username} (${data.user.role})
                            </div>
                        `;
                        loadScenarios(); // Reload scenarios after login
                    } else {
                        const error = await response.json();
                        const errorMsg = error.detail || 'Nieznany błąd';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd logowania: ${errorMsg}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function logout() {
                clearAuthToken();
                document.getElementById('login-username').value = '';
                document.getElementById('login-password').value = '';
                document.getElementById('scenarios-list').innerHTML = 
                    '<p>Zaloguj się aby zobaczyć scenariusze...</p>';
                document.getElementById('scenario-details').innerHTML = 
                    '<p>Wybierz scenariusz z listy powyżej...</p>';
                document.getElementById('result').innerHTML = `
                    <div class="result">
                    ℹ️ Wylogowano pomyślnie
                    </div>
                `;
            }

            async function makeAuthenticatedRequest(url, options = {}) {
                const token = getAuthToken();
                
                try {
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` }),
                            ...options.headers
                        }
                    });
                    return response;
                } catch (error) {
                    console.error('Request failed:', error);
                    throw error;
                }
            }

            // ========== UNIVERSAL JSON TREE EDITOR ==========
            class JSONTreeEditor {
                constructor(containerId) {
                    this.container = document.getElementById(containerId);
                    this.data = {};
                    this.fieldCounter = 0;
                }

                init(jsonData = {}) {
                    this.data = jsonData;
                    this.render();
                }

                render() {
                    this.container.innerHTML = '';
                    if (Object.keys(this.data).length === 0) {
                        this.container.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 20px;">Brak pól. Kliknij "+ Dodaj pole" aby rozpocząć</p>';
                        return;
                    }
                    
                    for (const [key, value] of Object.entries(this.data)) {
                        this.renderField(key, value, this.container);
                    }
                }

                renderField(key, value, parentElement, path = '') {
                    const fieldDiv = document.createElement('div');
                    fieldDiv.style.cssText = 'margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; border: 1px solid #ddd;';
                    
                    const currentPath = path ? `${path}.${key}` : key;
                    const type = this.getType(value);
                    
                    // Field header with key name and controls
                    const headerDiv = document.createElement('div');
                    headerDiv.style.cssText = 'display: flex; align-items: center; margin-bottom: 8px; gap: 10px;';
                    
                    const keyInput = document.createElement('input');
                    keyInput.type = 'text';
                    keyInput.value = key;
                    keyInput.style.cssText = 'flex: 0 0 180px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; font-weight: bold;';
                    keyInput.onchange = (e) => this.renameKey(path, key, e.target.value);
                    
                    const typeSelect = document.createElement('select');
                    typeSelect.style.cssText = 'flex: 0 0 100px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;';
                    ['string', 'number', 'boolean', 'object', 'array'].forEach(t => {
                        const option = document.createElement('option');
                        option.value = t;
                        option.textContent = t;
                        option.selected = type === t;
                        typeSelect.appendChild(option);
                    });
                    typeSelect.onchange = (e) => this.changeType(currentPath, e.target.value);
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = '🗑️';
                    deleteBtn.className = 'btn btn-danger';
                    deleteBtn.style.cssText = 'padding: 3px 8px; margin-left: auto;';
                    deleteBtn.onclick = () => this.deleteField(currentPath);
                    
                    headerDiv.appendChild(keyInput);
                    headerDiv.appendChild(typeSelect);
                    headerDiv.appendChild(deleteBtn);
                    fieldDiv.appendChild(headerDiv);
                    
                    // Value input based on type
                    const valueDiv = document.createElement('div');
                    
                    if (type === 'object') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #3498db; margin-top: 10px;';
                        for (const [childKey, childValue] of Object.entries(value)) {
                            this.renderField(childKey, childValue, valueDiv, currentPath);
                        }
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj pole do obiektu';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addFieldToObject(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'array') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #9b59b6; margin-top: 10px;';
                        value.forEach((item, index) => {
                            this.renderField(`[${index}]`, item, valueDiv, currentPath);
                        });
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj element do array';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addArrayElement(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'boolean') {
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.checked = value;
                        checkbox.style.cssText = 'width: 20px; height: 20px;';
                        checkbox.onchange = (e) => this.setValue(currentPath, e.target.checked);
                        valueDiv.appendChild(checkbox);
                    } else if (type === 'number') {
                        const input = document.createElement('input');
                        input.type = 'number';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, parseFloat(e.target.value));
                        valueDiv.appendChild(input);
                    } else {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, e.target.value);
                        valueDiv.appendChild(input);
                    }
                    
                    fieldDiv.appendChild(valueDiv);
                    parentElement.appendChild(fieldDiv);
                }

                getType(value) {
                    if (Array.isArray(value)) return 'array';
                    if (value === null) return 'string';
                    return typeof value;
                }

                setValue(path, value) {
                    const keys = path.split('.').filter(k => k && !k.startsWith('['));
                    const arrayIndices = path.match(/\[(\d+)\]/g);
                    
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = value;
                    this.render();
                }

                addField() {
                    const newKey = `field_${this.fieldCounter++}`;
                    this.data[newKey] = '';
                    this.render();
                }

                addFieldToObject(path) {
                    const obj = this.getValueByPath(path);
                    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                        obj[`field_${this.fieldCounter++}`] = '';
                        this.render();
                    }
                }

                addArrayElement(path) {
                    const arr = this.getValueByPath(path);
                    if (arr && Array.isArray(arr)) {
                        arr.push('');
                        this.render();
                    }
                }

                deleteField(path) {
                    const keys = path.split('.').filter(k => k);
                    if (keys.length === 1) {
                        delete this.data[keys[0]];
                    } else {
                        let current = this.data;
                        for (let i = 0; i < keys.length - 1; i++) {
                            current = current[keys[i]];
                        }
                        delete current[keys[keys.length - 1]];
                    }
                    this.render();
                }

                renameKey(parentPath, oldKey, newKey) {
                    if (oldKey === newKey) return;
                    
                    if (!parentPath) {
                        this.data[newKey] = this.data[oldKey];
                        delete this.data[oldKey];
                    } else {
                        const parent = this.getValueByPath(parentPath);
                        parent[newKey] = parent[oldKey];
                        delete parent[oldKey];
                    }
                    this.render();
                }

                changeType(path, newType) {
                    const defaultValues = {
                        'string': '',
                        'number': 0,
                        'boolean': false,
                        'object': {},
                        'array': []
                    };
                    
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = defaultValues[newType];
                    this.render();
                }

                getValueByPath(path) {
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (const key of keys) {
                        current = current[key];
                    }
                    return current;
                }

                clear() {
                    this.data = {};
                    this.render();
                }

                getJSON() {
                    return this.data;
                }

                setJSON(jsonData) {
                    this.data = jsonData;
                    this.render();
                }
            }

            // Initialize JSON Tree Editor
            const jsonTreeEditor = new JSONTreeEditor('json-tree-editor');
            jsonTreeEditor.init({});

            function toggleJSONView() {
                const preview = document.getElementById('json-preview');
                if (preview.style.display === 'none') {
                    preview.style.display = 'block';
                    preview.textContent = JSON.stringify(jsonTreeEditor.getJSON(), null, 2);
                } else {
                    preview.style.display = 'none';
                }
            }

            async function loadScenarios() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/scenarios/');
                    
                    if (response.status === 401 || response.status === 403) {
                        document.getElementById('scenarios-list').innerHTML = `
                            <div style="color: #e74c3c; padding: 10px;">
                            ❌ Brak autoryzacji. Zaloguj się jako Superuser aby zobaczyć scenariusze.
                            <br><br>
                            Status: ${response.status} - ${response.statusText}
                            </div>
                        `;
                        return;
                    }

                    scenarios = await response.json();
                    displayScenarios(scenarios);
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Błąd ładowania scenariuszy:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            function displayScenarios(scenarios) {
                const container = document.getElementById('scenarios-list');
                if (scenarios.length === 0) {
                    container.innerHTML = '<p>Brak scenariuszy testowych. Utwórz pierwszy scenariusz.</p>';
                    return;
                }

                container.innerHTML = scenarios.map(scenario => 
                    `<div class="scenario-item" onclick="selectScenario(${scenario.id})">
                        <strong>${scenario.name}</strong>
                        <br>
                        <small>Typ: ${scenario.device_type || 'Nie określono'} | Aktywny: ${scenario.is_active ? 'Tak' : 'Nie'}</small>
                    </div>`
                ).join('');
            }

            function selectScenario(scenarioId) {
                currentScenarioId = scenarioId;
                const scenario = scenarios.find(s => s.id === scenarioId);
                
                // Update UI
                document.querySelectorAll('.scenario-item').forEach(item => {
                    item.classList.remove('active');
                });
                event.target.closest('.scenario-item').classList.add('active');

                // Show scenario details
                document.getElementById('scenario-details').innerHTML = `
                    <h5>${scenario.name}</h5>
                    <p><strong>Opis:</strong> ${scenario.description || 'Brak opisu'}</p>
                    <p><strong>Typ urządzenia:</strong> ${scenario.device_type || 'Nie określono'}</p>
                    <p><strong>Utworzono:</strong> ${new Date(scenario.created_at).toLocaleString()}</p>
                    <button class="btn btn-secondary" onclick="deleteScenario(${scenarioId})">Usuń scenariusz</button>
                `;
            }

            let jsonTemplates = [];

            async function loadTemplatesForType() {
                const deviceType = document.getElementById('device-type').value;
                if (!deviceType) {
                    document.getElementById('templates-list').style.display = 'none';
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(
                        `/api/v1/fleet-config/json-templates?template_type=test_flow&category=${deviceType}`
                    );
                    
                    if (response.ok) {
                        jsonTemplates = await response.json();
                        if (jsonTemplates.length > 0) {
                            document.getElementById('templates-list').innerHTML = `
                                <p style="margin-bottom: 10px;"><strong>Dostępne szablony dla ${deviceType}:</strong></p>
                                ${jsonTemplates.map(t => `
                                    <div style="padding: 8px; border-bottom: 1px solid #eee; cursor: pointer;" 
                                         onclick="applyTemplate(${t.id})">
                                        <strong>${t.name}</strong>
                                        <br><small style="color: #7f8c8d;">${t.description || 'Brak opisu'}</small>
                                    </div>
                                `).join('')}
                            `;
                        } else {
                            document.getElementById('templates-list').innerHTML = 
                                '<p style="color: #7f8c8d;">Brak dostępnych szablonów dla tego typu urządzenia</p>';
                        }
                    }
                } catch (error) {
                    console.error('Error loading templates:', error);
                }
            }

            function showTemplates() {
                const templatesList = document.getElementById('templates-list');
                if (templatesList.style.display === 'none') {
                    templatesList.style.display = 'block';
                    loadTemplatesForType();
                } else {
                    templatesList.style.display = 'none';
                }
            }

            function applyTemplate(templateId) {
                const template = jsonTemplates.find(t => t.id === templateId);
                if (template) {
                    jsonTreeEditor.setJSON(template.default_values);
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result" style="background: #d4edda; border-color: #c3e6cb;">
                        ✅ Szablon "${template.name}" zastosowany! Możesz edytować pola poniżej.
                        </div>
                    `;
                    
                    document.getElementById('templates-list').style.display = 'none';
                }
            }

            async function createScenario() {
                const name = document.getElementById('scenario-name').value;
                const description = document.getElementById('scenario-description').value;
                const deviceType = document.getElementById('device-type').value;
                const testFlow = jsonTreeEditor.getJSON();

                if (!name) {
                    alert('Podaj nazwę scenariusza');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/scenarios/', {
                        method: 'POST',
                        body: JSON.stringify({
                            name: name,
                            description: description,
                            device_type: deviceType,
                            test_flow: Object.keys(testFlow).length > 0 ? testFlow : null,
                            is_active: true
                        })
                    });

                    if (response.status === 401 || response.status === 403) {
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Brak autoryzacji. Zaloguj się jako Superuser aby tworzyć scenariusze.
                            Status: ${response.status}
                            </div>
                        `;
                        return;
                    }

                    const result = await response.json();
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Scenariusz utworzony pomyślnie: ${result.name}
                        ${testFlow ? '<br><small>Z konfiguracją JSON</small>' : ''}
                        </div>
                    `;
                    
                    // Clear form
                    document.getElementById('scenario-form').reset();
                    jsonTreeEditor.clear();
                    document.getElementById('templates-list').style.display = 'none';
                    document.getElementById('json-preview').style.display = 'none';
                    
                    // Reload scenarios
                    loadScenarios();
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd tworzenia scenariusza: ${error.message}
                        </div>
                    `;
                }
            }

            async function deleteScenario(scenarioId) {
                if (!confirm('Czy na pewno chcesz usunąć ten scenariusz?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/scenarios/${scenarioId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message || 'Scenariusz został usunięty'}
                            </div>
                        `;
                        loadScenarios();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania scenariusza: ${error.message}
                        </div>
                    `;
                }
            }

            async function testScenariosAPI() {
                try {
                    const response = await fetch('/api/v1/scenarios/');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test /api/v1/scenarios/ Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing scenarios API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            async function testAuth() {
                try {
                    const response = await fetch('/api/v1/auth/me');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Auth Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing auth:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            // Load scenarios on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateAuthUI(); // Check if already logged in
                if (getAuthToken()) {
                    loadScenarios();
                } else {
                    document.getElementById('scenarios-list').innerHTML = 
                        '<p>Zaloguj się aby zobaczyć scenariusze...</p>';
                }
            });
        </script>
            </div>
            </div>
        </div>
    </body>
    </html>
    """

# Fleet Data Manager Module
@app.get("/fleet-data-manager", response_class=HTMLResponse)
async def fleet_data_manager():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fleet Data Manager - Fleet Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .nav-menu { background: #2c3e50; padding: 0; margin: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; }
            .nav-menu li { margin: 0; }
            .nav-menu a { display: block; padding: 15px 20px; color: white; text-decoration: none; transition: background 0.3s; }
            .nav-menu a:hover { background: #34495e; }
            .nav-menu a.active { background: #27ae60; }
            
            /* Hide header, module-info and old auth-section */
            .header { display: none !important; }
            .module-info { display: none !important; }
            .auth-section { display: none !important; }
            
            /* New app layout with sidebar */
            .app-layout { display: flex; min-height: calc(100vh - 50px); }
            .sidebar { width: 15%; min-width: 200px; background: #1f2a37; color: white; padding: 20px; position: sticky; top: 0; height: calc(100vh - 50px); overflow-y: auto; }
            .main-content-wrapper { width: 70%; padding: 20px; overflow-y: auto; }
            .right-sidebar { width: 15%; min-width: 200px; background: #1f2a37; color: white; padding: 20px; position: sticky; top: 0; height: calc(100vh - 50px); overflow-y: auto; }
            
            /* Right sidebar auth section */
            .right-sidebar .sidebar-auth { background: #374151; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #27ae60; }
            .right-sidebar .sidebar-auth h4 { margin-top: 0; font-size: 14px; }
            .right-sidebar .sidebar-auth input { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #4b5563; background: #1f2a37; color: white; border-radius: 4px; box-sizing: border-box; }
            .right-sidebar .sidebar-auth button { width: 100%; }
            .right-sidebar .sidebar-auth #auth-message { font-size: 12px; margin-top: 10px; }
            
            /* Role switcher */
            .right-sidebar .role-switcher { margin-top: 15px; padding: 10px; background: #374151; border-radius: 8px; display: none; }
            .right-sidebar .role-switcher select { width: 100%; padding: 8px; border: 1px solid #4b5563; border-radius: 4px; background: #1f2a37; color: white; }
            
            /* Sidebar module menu */
            .sidebar-menu { margin-top: 20px; }
            .sidebar-menu h4 { font-size: 14px; margin-bottom: 15px; border-bottom: 2px solid #27ae60; padding-bottom: 8px; }
            .sidebar-menu .tab { display: block; width: 100%; background: #374151; color: white; border: none; padding: 12px; text-align: left; cursor: pointer; margin-bottom: 5px; border-radius: 4px; border-left: 3px solid transparent; transition: all 0.3s; }
            .sidebar-menu .tab:hover { background: #4b5563; border-left-color: #27ae60; }
            .sidebar-menu .tab.active { background: #27ae60; border-left-color: #16a34a; font-weight: bold; }
            
            .container { max-width: 100%; margin: 0; padding: 0; }
            .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; color: #27ae60; }
            .stat-label { color: #666; margin-top: 5px; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .tabs { display: flex; margin-bottom: 20px; }
            .tab { padding: 10px 20px; background: #bdc3c7; color: #333; cursor: pointer; border: none; }
            .tab.active { background: #27ae60; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .btn { background: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #229954; }
            .btn-secondary { background: #95a5a6; }
            .btn-secondary:hover { background: #7f8c8d; }
            .btn-danger { background: #e74c3c; }
            .btn-danger:hover { background: #c0392b; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .data-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .data-table th, .data-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            .data-table th { background-color: #f8f9fa; font-weight: bold; }
            .data-table tr:hover { background-color: #f8f9fa; }
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; border-left: 4px solid #27ae60; font-family: monospace; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
            .auth-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
            .filter-section { background: #e8f5e8; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
            
            @media (max-width: 768px) {
                .app-layout { flex-direction: column; }
                .sidebar { width: 100%; height: auto; position: relative; border-right: none; border-bottom: 2px solid #34495e; }
                .main-content-wrapper { width: 100%; }
                .right-sidebar { width: 100%; height: auto; position: relative; border-top: 2px solid #34495e; }
                .main-content { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <nav class="nav-menu">
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/connect-plus">🔗 Connect++</a></li>
                <li><a href="/commands-manager">⚙️ Commands Manager</a></li>
                <li><a href="/fleet-data-manager" class="active">📊 Fleet Data Manager</a></li>
                <li><a href="/fleet-config-manager">🔧 Fleet Config Manager</a></li>
                <li><a href="/fleet-software-manager">💿 Fleet Software Manager</a></li>
                <li><a href="/docs">📚 API Docs</a></li>
            </ul>
        </nav>
        
        <div class="app-layout">
            <!-- Sidebar with module menu -->
            <div class="sidebar">
                <div class="sidebar-menu">
                    <h4>📊 Menu Modułu</h4>
                    <button class="tab active" onclick="showTab('devices')">📱 Urządzenia</button>
                    <button class="tab" onclick="showTab('customers')">👥 Klienci</button>
                </div>
                
                <div style="margin-top: 20px; padding: 10px; background: #374151; border-radius: 8px;">
                    <h4 style="margin-top: 0; font-size: 14px; border-bottom: 2px solid #27ae60; padding-bottom: 8px;">🔍 Test API</h4>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px; font-size: 12px;" onclick="testFleetDataAPI()">Test Fleet Data API</button>
                    <button class="btn btn-secondary" style="width: 100%; font-size: 12px;" onclick="testDashboard()">Test Dashboard</button>
                </div>
            </div>
            
            <!-- Main content area -->
            <div class="main-content-wrapper">
                <div class="container">
                    <div class="header">
                        <h1>📊 Fleet Data Manager</h1>
                    </div>
                    
                    <div class="module-info">
                        <h3>Moduł dla Manager</h3>
                        <p><strong>Port:</strong> 5000</p>
                        <p><strong>Rola:</strong> Manager</p>
                        <p><strong>Funkcje:</strong> Zarządzanie danymi urządzeń i klientów</p>
                    </div>

                    <!-- Dashboard Statistics -->
                    <div id="dashboard-section" style="display: none;">
                        <h3>📈 Dashboard</h3>
                        <div class="dashboard" id="dashboard-stats">
                            <!-- Stats will be loaded here -->
                        </div>
                    </div>

                    <div class="main-content">
                        <div class="section">
                            <div class="tabs" style="display: none;">
                                <button class="tab active" onclick="showTab('devices')">Urządzenia</button>
                                <button class="tab" onclick="showTab('customers')">Klienci</button>
                            </div>

                    <!-- Devices Tab -->
                    <div id="devices-tab" class="tab-content active">
                        <div class="filter-section">
                            <h4>🔍 Filtry</h4>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <select id="device-type-filter">
                                    <option value="">Wszystkie typy</option>
                                    <option value="mask_tester">Tester masek</option>
                                    <option value="pressure_sensor">Czujnik ciśnienia</option>
                                    <option value="flow_meter">Przepływomierz</option>
                                </select>
                                <select id="device-status-filter">
                                    <option value="">Wszystkie statusy</option>
                                    <option value="active">Aktywne</option>
                                    <option value="inactive">Nieaktywne</option>
                                    <option value="maintenance">Konserwacja</option>
                                    <option value="decommissioned">Wycofane</option>
                                </select>
                                <button class="btn" onclick="loadDevices()">Filtruj</button>
                                <button class="btn btn-secondary" onclick="clearFilters()">Wyczyść</button>
                            </div>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4>📱 Lista Urządzeń</h4>
                            <button class="btn" onclick="showAddDeviceForm()">Dodaj urządzenie</button>
                        </div>
                        
                        <table class="data-table" id="devices-table">
                            <thead>
                                <tr>
                                    <th>Numer urządzenia</th>
                                    <th>Typ</th>
                                    <th>Status</th>
                                    <th>Klient</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="5">Zaloguj się aby zobaczyć urządzenia...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Customers Tab -->
                    <div id="customers-tab" class="tab-content">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4>🏢 Lista Klientów</h4>
                            <button class="btn" onclick="showAddCustomerForm()">Dodaj klienta</button>
                        </div>
                        
                        <table class="data-table" id="customers-table">
                            <thead>
                                <tr>
                                    <th>Nazwa</th>
                                    <th>Informacje kontaktowe</th>
                                    <th>Data utworzenia</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="4">Zaloguj się aby zobaczyć klientów...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="section">
                    <h3 id="form-title">Formularz</h3>
                    
                    <!-- Add Device Form -->
                    <div id="add-device-form" style="display: none;">
                        <h4>Dodaj nowe urządzenie</h4>
                        <form id="device-form">
                            <div class="form-group">
                                <label>Numer urządzenia:</label>
                                <input type="text" id="device-number" required>
                            </div>
                            <div class="form-group">
                                <label>Typ urządzenia:</label>
                                <select id="device-type" required>
                                    <option value="">Wybierz typ</option>
                                    <option value="mask_tester">Tester masek</option>
                                    <option value="pressure_sensor">Czujnik ciśnienia</option>
                                    <option value="flow_meter">Przepływomierz</option>
                                    <option value="generic_device">Urządzenie ogólne</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Rodzaj urządzenia:</label>
                                <input type="text" id="kind-of-device">
                            </div>
                            <div class="form-group">
                                <label>Numer seryjny:</label>
                                <input type="text" id="serial-number">
                            </div>
                            <div class="form-group">
                                <label>Status:</label>
                                <select id="device-status">
                                    <option value="active">Aktywne</option>
                                    <option value="inactive">Nieaktywne</option>
                                    <option value="maintenance">Konserwacja</option>
                                    <option value="decommissioned">Wycofane</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Klient:</label>
                                <select id="device-customer">
                                    <option value="">Brak przypisania</option>
                                </select>
                            </div>
                            <button type="button" class="btn" id="device-submit-btn" onclick="saveDevice()">Dodaj urządzenie</button>
                            <button type="button" class="btn btn-secondary" onclick="hideDeviceForm()">Anuluj</button>
                        </form>
                    </div>

                    <!-- Add Customer Form -->
                    <div id="add-customer-form" style="display: none;">
                        <h4>Dodaj nowego klienta</h4>
                        <form id="customer-form">
                            <div class="form-group">
                                <label>Nazwa klienta:</label>
                                <input type="text" id="customer-name" required>
                            </div>
                            <div class="form-group">
                                <label>📋 Informacje kontaktowe (JSON):</label>
                                <div style="margin-bottom: 10px;">
                                    <button type="button" class="btn btn-secondary" onclick="customerJsonEditor.addField()">+ Dodaj pole</button>
                                    <button type="button" class="btn btn-secondary" onclick="customerJsonEditor.clear()">🗑️ Wyczyść</button>
                                    <button type="button" class="btn btn-secondary" onclick="toggleCustomerJSONView()">👁️ Podgląd JSON</button>
                                </div>
                                <div id="customer-json-editor" style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background: #f8f9fa; max-height: 400px; overflow-y: auto;">
                                    <!-- Tree editor -->
                                </div>
                                <div id="customer-json-preview" style="display: none; margin-top: 10px; padding: 10px; background: #2c3e50; color: #ecf0f1; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto;">
                                    <!-- JSON preview -->
                                </div>
                            </div>
                            <button type="button" class="btn" id="customer-submit-btn" onclick="saveCustomer()">Dodaj klienta</button>
                            <button type="button" class="btn btn-secondary" onclick="hideCustomerForm()">Anuluj</button>
                        </form>
                    </div>
                </div>
            </div>

            <div id="result" style="margin-top: 20px;"></div>
                </div>
            </div>

            <!-- Right sidebar with login -->
            <div class="right-sidebar">
                <div class="sidebar-auth">
                    <h4>🔐 Logowanie</h4>
                    <input type="text" id="login-username" placeholder="Username">
                    <input type="password" id="login-password" placeholder="Password">
                    <button class="btn" onclick="login()">Zaloguj</button>
                    <button class="btn btn-secondary" onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                    <div id="auth-message"></div>
                </div>

                <div class="role-switcher" id="role-switcher">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #ecf0f1;">🔄 Przełącz rolę:</label>
                    <select id="role-select" onchange="switchRole()">
                        <option value="">Wybierz rolę...</option>
                    </select>
                </div>
            </div>
        </div>

        <script>
            let authToken = null;
            let devices = [];
            let customers = [];
            let currentEditingDevice = null;
            let currentEditingCustomer = null;

            function getAuthToken() {
                if (!authToken) {
                    authToken = localStorage.getItem('jwt_token');
                }
                return authToken;
            }

            function setAuthToken(token) {
                authToken = token;
                localStorage.setItem('jwt_token', token);
                updateAuthUI();
            }

            function clearAuthToken() {
                authToken = null;
                localStorage.removeItem('jwt_token');
                updateAuthUI();
            }

            function updateAuthUI() {
                const isLoggedIn = !!getAuthToken();
                document.getElementById('login-username').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('login-password').style.display = isLoggedIn ? 'none' : 'inline';
                document.querySelector('button[onclick="login()"]').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('logout-btn').style.display = isLoggedIn ? 'inline' : 'none';
                document.getElementById('dashboard-section').style.display = isLoggedIn ? 'block' : 'none';
                
                if (isLoggedIn) {
                    const userRoles = getUserRoles();
                    const activeRole = getActiveRole();
                    
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #2980b9;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
                    
                    if (userRoles && userRoles.length > 1) {
                        const roleSelect = document.getElementById('role-select');
                        roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
                        userRoles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                            if (role === activeRole) {
                                option.selected = true;
                            }
                            roleSelect.appendChild(option);
                        });
                        document.getElementById('role-switcher').style.display = 'block';
                    } else {
                        document.getElementById('role-switcher').style.display = 'none';
                    }
                    
                    loadDashboard();
                    loadDevices();
                    loadCustomers();
                    loadCustomersForSelect();
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
                    document.getElementById('role-switcher').style.display = 'none';
                    clearTables();
                }
            }

            function getUserRoles() {
                const token = getAuthToken();
                if (!token) return [];
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.roles || [];
                } catch (e) {
                    return [];
                }
            }

            function getActiveRole() {
                const token = getAuthToken();
                if (!token) return '';
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.active_role || payload.role || '';
                } catch (e) {
                    return '';
                }
            }

            async function switchRole() {
                const selectedRole = document.getElementById('role-select').value;
                if (!selectedRole) return;

                try {
                    const response = await fetch('/api/v1/auth/switch-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify({ new_role: selectedRole })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #2980b9;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
                        
                        loadDevices();
                        loadCustomers();
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd przełączania roli: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function clearTables() {
                document.getElementById('devices-table').getElementsByTagName('tbody')[0].innerHTML = 
                    '<tr><td colspan="5">Zaloguj się aby zobaczyć urządzenia...</td></tr>';
                document.getElementById('customers-table').getElementsByTagName('tbody')[0].innerHTML = 
                    '<tr><td colspan="4">Zaloguj się aby zobaczyć klientów...</td></tr>';
            }

            async function login() {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    alert('Podaj username i hasło');
                    return;
                }

                try {
                    const formData = new URLSearchParams();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: green;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Zalogowano pomyślnie jako ${username} (${data.user.role})
                            </div>
                        `;
                    } else {
                        const error = await response.json();
                        const errorMsg = error.detail || 'Nieznany błąd';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd logowania: ${errorMsg}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function logout() {
                clearAuthToken();
                document.getElementById('login-username').value = '';
                document.getElementById('login-password').value = '';
                document.getElementById('result').innerHTML = `
                    <div class="result">
                    ℹ️ Wylogowano pomyślnie
                    </div>
                `;
            }

            async function makeAuthenticatedRequest(url, options = {}) {
                const token = getAuthToken();
                
                try {
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` }),
                            ...options.headers
                        }
                    });
                    return response;
                } catch (error) {
                    console.error('Request failed:', error);
                    throw error;
                }
            }

            // ========== UNIVERSAL JSON TREE EDITOR ==========
            class JSONTreeEditor {
                constructor(containerId) {
                    this.container = document.getElementById(containerId);
                    this.data = {};
                    this.fieldCounter = 0;
                }

                init(jsonData = {}) {
                    this.data = jsonData;
                    this.render();
                }

                render() {
                    this.container.innerHTML = '';
                    if (Object.keys(this.data).length === 0) {
                        this.container.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 20px;">Brak pól. Kliknij "+ Dodaj pole" aby rozpocząć</p>';
                        return;
                    }
                    
                    for (const [key, value] of Object.entries(this.data)) {
                        this.renderField(key, value, this.container);
                    }
                }

                renderField(key, value, parentElement, path = '') {
                    const fieldDiv = document.createElement('div');
                    fieldDiv.style.cssText = 'margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; border: 1px solid #ddd;';
                    
                    const currentPath = path ? `${path}.${key}` : key;
                    const type = this.getType(value);
                    
                    const headerDiv = document.createElement('div');
                    headerDiv.style.cssText = 'display: flex; align-items: center; margin-bottom: 8px; gap: 10px;';
                    
                    const keyInput = document.createElement('input');
                    keyInput.type = 'text';
                    keyInput.value = key;
                    keyInput.style.cssText = 'flex: 0 0 180px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; font-weight: bold;';
                    keyInput.onchange = (e) => this.renameKey(path, key, e.target.value);
                    
                    const typeSelect = document.createElement('select');
                    typeSelect.style.cssText = 'flex: 0 0 100px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;';
                    ['string', 'number', 'boolean', 'object', 'array'].forEach(t => {
                        const option = document.createElement('option');
                        option.value = t;
                        option.textContent = t;
                        option.selected = type === t;
                        typeSelect.appendChild(option);
                    });
                    typeSelect.onchange = (e) => this.changeType(currentPath, e.target.value);
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = '🗑️';
                    deleteBtn.className = 'btn btn-danger';
                    deleteBtn.style.cssText = 'padding: 3px 8px; margin-left: auto;';
                    deleteBtn.onclick = () => this.deleteField(currentPath);
                    
                    headerDiv.appendChild(keyInput);
                    headerDiv.appendChild(typeSelect);
                    headerDiv.appendChild(deleteBtn);
                    fieldDiv.appendChild(headerDiv);
                    
                    const valueDiv = document.createElement('div');
                    
                    if (type === 'object') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #3498db; margin-top: 10px;';
                        for (const [childKey, childValue] of Object.entries(value)) {
                            this.renderField(childKey, childValue, valueDiv, currentPath);
                        }
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj pole do obiektu';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addFieldToObject(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'array') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #9b59b6; margin-top: 10px;';
                        value.forEach((item, index) => {
                            this.renderField(`[${index}]`, item, valueDiv, currentPath);
                        });
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj element do array';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addArrayElement(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'boolean') {
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.checked = value;
                        checkbox.style.cssText = 'width: 20px; height: 20px;';
                        checkbox.onchange = (e) => this.setValue(currentPath, e.target.checked);
                        valueDiv.appendChild(checkbox);
                    } else if (type === 'number') {
                        const input = document.createElement('input');
                        input.type = 'number';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, parseFloat(e.target.value));
                        valueDiv.appendChild(input);
                    } else {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, e.target.value);
                        valueDiv.appendChild(input);
                    }
                    
                    fieldDiv.appendChild(valueDiv);
                    parentElement.appendChild(fieldDiv);
                }

                getType(value) {
                    if (Array.isArray(value)) return 'array';
                    if (value === null) return 'string';
                    return typeof value;
                }

                setValue(path, value) {
                    const keys = path.split('.').filter(k => k && !k.startsWith('['));
                    const arrayIndices = path.match(/\[(\d+)\]/g);
                    
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = value;
                    this.render();
                }

                addField() {
                    const newKey = `field_${this.fieldCounter++}`;
                    this.data[newKey] = '';
                    this.render();
                }

                addFieldToObject(path) {
                    const obj = this.getValueByPath(path);
                    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                        obj[`field_${this.fieldCounter++}`] = '';
                        this.render();
                    }
                }

                addArrayElement(path) {
                    const arr = this.getValueByPath(path);
                    if (arr && Array.isArray(arr)) {
                        arr.push('');
                        this.render();
                    }
                }

                deleteField(path) {
                    const keys = path.split('.').filter(k => k);
                    if (keys.length === 1) {
                        delete this.data[keys[0]];
                    } else {
                        let current = this.data;
                        for (let i = 0; i < keys.length - 1; i++) {
                            current = current[keys[i]];
                        }
                        delete current[keys[keys.length - 1]];
                    }
                    this.render();
                }

                renameKey(parentPath, oldKey, newKey) {
                    if (oldKey === newKey) return;
                    
                    if (!parentPath) {
                        this.data[newKey] = this.data[oldKey];
                        delete this.data[oldKey];
                    } else {
                        const parent = this.getValueByPath(parentPath);
                        parent[newKey] = parent[oldKey];
                        delete parent[oldKey];
                    }
                    this.render();
                }

                changeType(path, newType) {
                    const defaultValues = {
                        'string': '',
                        'number': 0,
                        'boolean': false,
                        'object': {},
                        'array': []
                    };
                    
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = defaultValues[newType];
                    this.render();
                }

                getValueByPath(path) {
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (const key of keys) {
                        current = current[key];
                    }
                    return current;
                }

                clear() {
                    this.data = {};
                    this.render();
                }

                getData() {
                    return this.data;
                }

                setData(jsonData) {
                    this.data = jsonData;
                    this.render();
                }
            }

            let customerJsonEditor;

            function toggleCustomerJSONView() {
                const preview = document.getElementById('customer-json-preview');
                if (preview.style.display === 'none') {
                    preview.style.display = 'block';
                    preview.textContent = JSON.stringify(customerJsonEditor.getData(), null, 2);
                } else {
                    preview.style.display = 'none';
                }
            }

            function showTab(tabName, skipHashUpdate = false) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Find and activate corresponding button
                const buttons = document.querySelectorAll('.tab');
                buttons.forEach(btn => {
                    if (btn.onclick && btn.onclick.toString().includes(tabName)) {
                        btn.classList.add('active');
                    }
                });

                // Hide forms
                hideDeviceForm();
                hideCustomerForm();
                
                // Update URL hash
                if (!skipHashUpdate) {
                    window.location.hash = tabName;
                }
            }
            
            // Handle hash changes
            window.addEventListener('hashchange', function() {
                const hash = window.location.hash.substring(1);
                if (hash) {
                    const tabElement = document.getElementById(hash + '-tab');
                    if (tabElement) {
                        showTab(hash, true);
                    }
                }
            });
            
            // Load tab from hash on page load
            window.addEventListener('DOMContentLoaded', function() {
                customerJsonEditor = new JSONTreeEditor('customer-json-editor');
                customerJsonEditor.setData({
                    phone: '',
                    email: '',
                    address: '',
                    company: '',
                    notes: ''
                });
                
                const hash = window.location.hash.substring(1);
                if (hash) {
                    showTab(hash, true);
                } else {
                    showTab('devices', false);
                }
            });

            async function loadDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/dashboard');
                    
                    if (response.ok) {
                        const data = await response.json();
                        displayDashboard(data);
                    }
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }

            function displayDashboard(data) {
                const container = document.getElementById('dashboard-stats');
                container.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${data.total_devices}</div>
                        <div class="stat-label">Urządzenia</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.active_devices}</div>
                        <div class="stat-label">Aktywne</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.maintenance_devices}</div>
                        <div class="stat-label">Konserwacja</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.total_customers}</div>
                        <div class="stat-label">Klienci</div>
                    </div>
                `;
            }

            async function loadDevices() {
                try {
                    const deviceType = document.getElementById('device-type-filter').value;
                    const status = document.getElementById('device-status-filter').value;
                    
                    let url = '/api/v1/fleet-data/devices?';
                    if (deviceType) url += `device_type=${deviceType}&`;
                    if (status) url += `status=${status}&`;
                    
                    const response = await makeAuthenticatedRequest(url);
                    
                    if (response.ok) {
                        devices = await response.json();
                        displayDevices(devices);
                    } else if (response.status === 401 || response.status === 403) {
                        document.getElementById('devices-table').getElementsByTagName('tbody')[0].innerHTML = 
                            '<tr><td colspan="5" style="color: #e74c3c;">❌ Brak autoryzacji Manager</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania urządzeń: ${error.message}
                        </div>
                    `;
                }
            }

            function displayDevices(devices) {
                const tbody = document.getElementById('devices-table').getElementsByTagName('tbody')[0];
                if (devices.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5">Brak urządzeń do wyświetlenia.</td></tr>';
                    return;
                }

                tbody.innerHTML = devices.map(device => `
                    <tr>
                        <td>${device.device_number}</td>
                        <td>${device.device_type}</td>
                        <td><span style="color: ${getStatusColor(device.status)}">${getStatusLabel(device.status)}</span></td>
                        <td>${device.customer_id ? 'Przypisany' : 'Brak'}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="editDevice(${device.id})">Edytuj</button>
                            <button class="btn btn-danger" onclick="deleteDevice(${device.id})">Usuń</button>
                        </td>
                    </tr>
                `).join('');
            }

            function getStatusColor(status) {
                const colors = {
                    'active': '#27ae60',
                    'inactive': '#95a5a6',
                    'maintenance': '#f39c12',
                    'decommissioned': '#e74c3c'
                };
                return colors[status] || '#333';
            }

            function getStatusLabel(status) {
                const labels = {
                    'active': 'Aktywne',
                    'inactive': 'Nieaktywne',
                    'maintenance': 'Konserwacja',
                    'decommissioned': 'Wycofane'
                };
                return labels[status] || status;
            }

            async function loadCustomers() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/customers');
                    
                    if (response.ok) {
                        customers = await response.json();
                        displayCustomers(customers);
                    } else if (response.status === 401 || response.status === 403) {
                        document.getElementById('customers-table').getElementsByTagName('tbody')[0].innerHTML = 
                            '<tr><td colspan="4" style="color: #e74c3c;">❌ Brak autoryzacji Manager</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania klientów: ${error.message}
                        </div>
                    `;
                }
            }

            function displayCustomers(customers) {
                const tbody = document.getElementById('customers-table').getElementsByTagName('tbody')[0];
                if (customers.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4">Brak klientów do wyświetlenia.</td></tr>';
                    return;
                }

                tbody.innerHTML = customers.map(customer => `
                    <tr>
                        <td>${customer.name}</td>
                        <td>${customer.contact_info ? JSON.stringify(customer.contact_info) : 'Brak'}</td>
                        <td>${new Date(customer.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="editCustomer(${customer.id})">Edytuj</button>
                            <button class="btn btn-danger" onclick="deleteCustomer(${customer.id})">Usuń</button>
                        </td>
                    </tr>
                `).join('');
            }

            async function loadCustomersForSelect() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/customers');
                    
                    if (response.ok) {
                        const customers = await response.json();
                        const select = document.getElementById('device-customer');
                        select.innerHTML = '<option value="">Brak przypisania</option>';
                        customers.forEach(customer => {
                            select.innerHTML += `<option value="${customer.id}">${customer.name}</option>`;
                        });
                    }
                } catch (error) {
                    console.error('Error loading customers for select:', error);
                }
            }

            function showAddDeviceForm() {
                hideCustomerForm();
                document.getElementById('add-device-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Dodaj urządzenie';
                currentEditingDevice = null;
                document.getElementById('device-submit-btn').textContent = 'Dodaj urządzenie';
                loadCustomersForSelect();
            }

            function hideDeviceForm() {
                document.getElementById('add-device-form').style.display = 'none';
                document.getElementById('device-form').reset();
                document.getElementById('form-title').textContent = 'Formularz';
                currentEditingDevice = null;
            }

            function showAddCustomerForm() {
                hideDeviceForm();
                document.getElementById('add-customer-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Dodaj klienta';
                currentEditingCustomer = null;
                document.getElementById('customer-submit-btn').textContent = 'Dodaj klienta';
                
                customerJsonEditor.setData({
                    phone: '',
                    email: '',
                    address: '',
                    company: '',
                    notes: ''
                });
            }

            function hideCustomerForm() {
                document.getElementById('add-customer-form').style.display = 'none';
                document.getElementById('customer-form').reset();
                document.getElementById('form-title').textContent = 'Formularz';
                currentEditingCustomer = null;
            }

            async function saveDevice() {
                if (currentEditingDevice) {
                    await updateDevice();
                } else {
                    await createDevice();
                }
            }

            async function saveCustomer() {
                if (currentEditingCustomer) {
                    await updateCustomer();
                } else {
                    await createCustomer();
                }
            }

            async function createDevice() {
                const deviceData = {
                    device_number: document.getElementById('device-number').value,
                    device_type: document.getElementById('device-type').value,
                    kind_of_device: document.getElementById('kind-of-device').value,
                    serial_number: document.getElementById('serial-number').value,
                    status: document.getElementById('device-status').value,
                    customer_id: document.getElementById('device-customer').value || null
                };

                if (!deviceData.device_number || !deviceData.device_type) {
                    alert('Podaj numer i typ urządzenia');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/devices', {
                        method: 'POST',
                        body: JSON.stringify(deviceData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Urządzenie ${result.device_number} zostało dodane pomyślnie
                            </div>
                        `;
                        hideDeviceForm();
                        loadDevices();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd tworzenia urządzenia: ${error.message}
                        </div>
                    `;
                }
            }

            async function createCustomer() {
                const customerData = {
                    name: document.getElementById('customer-name').value,
                    contact_info: customerJsonEditor.getData()
                };

                if (!customerData.name) {
                    alert('Podaj nazwę klienta');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/customers', {
                        method: 'POST',
                        body: JSON.stringify(customerData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Klient ${result.name} został dodany pomyślnie
                            </div>
                        `;
                        hideCustomerForm();
                        loadCustomers();
                        loadCustomersForSelect();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd tworzenia klienta: ${error.message}
                        </div>
                    `;
                }
            }

            function editDevice(deviceId) {
                const device = devices.find(d => d.id === deviceId);
                if (!device) return;

                hideCustomerForm();
                document.getElementById('add-device-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Edytuj urządzenie';
                currentEditingDevice = deviceId;
                document.getElementById('device-submit-btn').textContent = 'Zaktualizuj urządzenie';

                document.getElementById('device-number').value = device.device_number;
                document.getElementById('device-type').value = device.device_type;
                document.getElementById('kind-of-device').value = device.kind_of_device || '';
                document.getElementById('serial-number').value = device.serial_number || '';
                document.getElementById('device-status').value = device.status;
                document.getElementById('device-customer').value = device.customer_id || '';
                loadCustomersForSelect();
            }

            async function updateDevice() {
                const deviceData = {
                    device_number: document.getElementById('device-number').value,
                    device_type: document.getElementById('device-type').value,
                    kind_of_device: document.getElementById('kind-of-device').value,
                    serial_number: document.getElementById('serial-number').value,
                    status: document.getElementById('device-status').value,
                    customer_id: document.getElementById('device-customer').value || null
                };

                if (!deviceData.device_number || !deviceData.device_type) {
                    alert('Podaj numer i typ urządzenia');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-data/devices/${currentEditingDevice}`, {
                        method: 'PUT',
                        body: JSON.stringify(deviceData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Urządzenie ${result.device_number} zostało zaktualizowane
                            </div>
                        `;
                        hideDeviceForm();
                        loadDevices();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd aktualizacji urządzenia: ${error.message}
                        </div>
                    `;
                }
            }

            function editCustomer(customerId) {
                const customer = customers.find(c => c.id === customerId);
                if (!customer) return;

                hideDeviceForm();
                document.getElementById('add-customer-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Edytuj klienta';
                currentEditingCustomer = customerId;
                document.getElementById('customer-submit-btn').textContent = 'Zaktualizuj klienta';

                document.getElementById('customer-name').value = customer.name;
                customerJsonEditor.setData(customer.contact_info || {});
            }

            async function updateCustomer() {
                const customerData = {
                    name: document.getElementById('customer-name').value,
                    contact_info: customerJsonEditor.getData()
                };

                if (!customerData.name) {
                    alert('Podaj nazwę klienta');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-data/customers/${currentEditingCustomer}`, {
                        method: 'PUT',
                        body: JSON.stringify(customerData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Klient ${result.name} został zaktualizowany
                            </div>
                        `;
                        hideCustomerForm();
                        loadCustomers();
                        loadCustomersForSelect();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd aktualizacji klienta: ${error.message}
                        </div>
                    `;
                }
            }

            async function deleteDevice(deviceId) {
                if (!confirm('Czy na pewno chcesz usunąć to urządzenie?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-data/devices/${deviceId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            </div>
                        `;
                        loadDevices();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania urządzenia: ${error.message}
                        </div>
                    `;
                }
            }

            async function deleteCustomer(customerId) {
                if (!confirm('Czy na pewno chcesz usunąć tego klienta?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-data/customers/${customerId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            </div>
                        `;
                        loadCustomers();
                        loadCustomersForSelect();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania klienta: ${error.message}
                        </div>
                    `;
                }
            }

            function clearFilters() {
                document.getElementById('device-type-filter').value = '';
                document.getElementById('device-status-filter').value = '';
                loadDevices();
            }

            async function testFleetDataAPI() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/devices');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Fleet Data API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Fleet Data API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            async function testDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-data/dashboard');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Dashboard API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Dashboard API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateAuthUI();
            });
        </script>
    </body>
    </html>
    """

# Fleet Config Manager Module
@app.get("/fleet-config-manager", response_class=HTMLResponse)
async def fleet_config_manager():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fleet Config Manager - Fleet Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .nav-menu { background: #2c3e50; padding: 0; margin: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; }
            .nav-menu li { margin: 0; }
            .nav-menu a { display: block; padding: 15px 20px; color: white; text-decoration: none; transition: background 0.3s; }
            .nav-menu a:hover { background: #34495e; }
            .nav-menu a.active { background: #9b59b6; }
            
            /* Hide header, module-info and old auth-section */
            .header { display: none !important; }
            .module-info { display: none !important; }
            .auth-section { display: none !important; }
            
            /* New app layout with sidebar */
            .app-layout { display: flex; min-height: calc(100vh - 50px); }
            .sidebar { width: 15%; min-width: 200px; background: #1f2a37; color: white; padding: 20px; position: sticky; top: 0; height: calc(100vh - 50px); overflow-y: auto; }
            .main-content-wrapper { width: 70%; padding: 20px; overflow-y: auto; }
            .right-sidebar { width: 15%; min-width: 200px; background: #1f2a37; color: white; padding: 20px; position: sticky; top: 0; height: calc(100vh - 50px); overflow-y: auto; }
            
            /* Right sidebar auth section */
            .right-sidebar .sidebar-auth { background: #374151; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #9b59b6; }
            .right-sidebar .sidebar-auth h4 { margin-top: 0; font-size: 14px; }
            .right-sidebar .sidebar-auth input { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #4b5563; background: #1f2a37; color: white; border-radius: 4px; box-sizing: border-box; }
            .right-sidebar .sidebar-auth button { width: 100%; }
            .right-sidebar .sidebar-auth #auth-message { font-size: 12px; margin-top: 10px; }
            
            /* Role switcher */
            .right-sidebar .role-switcher { margin-top: 15px; padding: 10px; background: #374151; border-radius: 8px; display: none; }
            .right-sidebar .role-switcher select { width: 100%; padding: 8px; border: 1px solid #4b5563; border-radius: 4px; background: #1f2a37; color: white; }
            
            /* Sidebar module menu */
            .sidebar-menu { margin-top: 20px; }
            .sidebar-menu h4 { font-size: 14px; margin-bottom: 15px; border-bottom: 2px solid #9b59b6; padding-bottom: 8px; }
            .sidebar-menu .tab { display: block; width: 100%; background: #374151; color: white; border: none; padding: 12px; text-align: left; cursor: pointer; margin-bottom: 5px; border-radius: 4px; border-left: 3px solid transparent; transition: all 0.3s; }
            .sidebar-menu .tab:hover { background: #4b5563; border-left-color: #9b59b6; }
            .sidebar-menu .tab.active { background: #9b59b6; border-left-color: #7c3aed; font-weight: bold; }
            
            .container { max-width: 100%; margin: 0; padding: 0; }
            .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; color: #9b59b6; }
            .stat-label { color: #666; margin-top: 5px; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .tabs { display: flex; margin-bottom: 20px; flex-wrap: wrap; }
            .tab { padding: 8px 15px; background: #bdc3c7; color: #333; cursor: pointer; border: none; margin: 2px; font-size: 12px; }
            .tab.active { background: #9b59b6; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .btn { background: #9b59b6; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #8e44ad; }
            .btn-secondary { background: #95a5a6; }
            .btn-secondary:hover { background: #7f8c8d; }
            .btn-success { background: #27ae60; }
            .btn-success:hover { background: #229954; }
            .btn-danger { background: #e74c3c; }
            .btn-danger:hover { background: #c0392b; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .data-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }
            .data-table th, .data-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            .data-table th { background-color: #f8f9fa; font-weight: bold; }
            .data-table tr:hover { background-color: #f8f9fa; }
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; border-left: 4px solid #9b59b6; font-family: monospace; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
            .auth-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
            .filter-section { background: #e8f5e8; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
            .config-card { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
            .config-header { font-weight: bold; color: #9b59b6; margin-bottom: 10px; }
            .config-value { background: white; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
            .backup-section { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; }
            
            @media (max-width: 768px) {
                .app-layout { flex-direction: column; }
                .sidebar { width: 100%; height: auto; position: relative; border-right: none; border-bottom: 2px solid #34495e; }
                .main-content-wrapper { width: 100%; }
                .right-sidebar { width: 100%; height: auto; position: relative; border-top: 2px solid #34495e; }
                .main-content { grid-template-columns: 1fr; }
                .tabs { flex-direction: column; }
            }
        </style>
    </head>
    <body>
        <nav class="nav-menu">
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/connect-plus">🔗 Connect++</a></li>
                <li><a href="/commands-manager">⚙️ Commands Manager</a></li>
                <li><a href="/fleet-data-manager">📊 Fleet Data Manager</a></li>
                <li><a href="/fleet-config-manager" class="active">🔧 Fleet Config Manager</a></li>
                <li><a href="/fleet-software-manager">💿 Fleet Software Manager</a></li>
                <li><a href="/docs">📚 API Docs</a></li>
            </ul>
        </nav>
        
        <div class="app-layout">
            <!-- Sidebar with module menu -->
            <div class="sidebar">
                <div class="sidebar-menu">
                    <h4>⚙️ Menu Modułu</h4>
                    <button class="tab active" onclick="showTab('system-config')">🔧 Konfiguracja systemu</button>
                    <button class="tab" onclick="showTab('device-config')">📱 Konfiguracja urządzeń</button>
                    <button class="tab" onclick="showTab('test-config')">🧪 Scenariusze testowe</button>
                    <button class="tab" onclick="showTab('json-templates')">📋 Szablony JSON</button>
                    <button class="tab" onclick="showTab('backup')">💾 Backup/Restore</button>
                </div>
                
                <div style="margin-top: 20px; padding: 10px; background: #374151; border-radius: 8px;">
                    <h4 style="margin-top: 0; font-size: 14px; border-bottom: 2px solid #9b59b6; padding-bottom: 8px;">🔍 Test API</h4>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px; font-size: 12px;" onclick="testConfigAPI()">Test Config API</button>
                    <button class="btn btn-secondary" style="width: 100%; font-size: 12px;" onclick="testConfigDashboard()">Test Dashboard</button>
                </div>
            </div>
            
            <!-- Main content area -->
            <div class="main-content-wrapper">
                <div class="container">
                    <div class="header">
                        <h1>⚙️ Fleet Config Manager</h1>
                    </div>
                    
                    <div class="module-info">
                        <h3>Moduł dla Configurator</h3>
                        <p><strong>Port:</strong> 5000</p>
                        <p><strong>Rola:</strong> Configurator</p>
                        <p><strong>Funkcje:</strong> Zarządzanie konfiguracją systemu, urządzeń i scenariuszy testowych</p>
                    </div>

                    <!-- Dashboard Statistics -->
                    <div id="dashboard-section" style="display: none;">
                        <h3>📈 Configuration Dashboard</h3>
                        <div class="dashboard" id="dashboard-stats">
                            <!-- Stats will be loaded here -->
                        </div>
                    </div>

                    <div class="main-content">
                        <div class="section">
                            <div class="tabs" style="display: none;">
                                <button class="tab active" onclick="showTab('system-config')">Konfiguracja systemu</button>
                                <button class="tab" onclick="showTab('device-config')">Konfiguracja urządzeń</button>
                                <button class="tab" onclick="showTab('test-config')">Scenariusze testowe</button>
                                <button class="tab" onclick="showTab('json-templates')">📋 Szablony JSON</button>
                                <button class="tab" onclick="showTab('backup')">Backup/Restore</button>
                            </div>

                    <!-- System Configuration Tab -->
                    <div id="system-config-tab" class="tab-content active">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4>🔧 Konfiguracja systemu</h4>
                            <button class="btn" onclick="showAddSystemConfigForm()">Dodaj konfigurację</button>
                        </div>
                        
                        <div id="system-configs-list">
                            <p>Zaloguj się aby zobaczyć konfigurację systemu...</p>
                        </div>
                    </div>

                    <!-- Device Configuration Tab -->
                    <div id="device-config-tab" class="tab-content">
                        <h4>📱 Konfiguracja urządzeń</h4>
                        
                        <table class="data-table" id="device-configs-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Numer urządzenia</th>
                                    <th>Typ</th>
                                    <th>Status</th>
                                    <th>Konfiguracja</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="6">Zaloguj się aby zobaczyć konfigurację urządzeń...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Test Configuration Tab -->
                    <div id="test-config-tab" class="tab-content">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4>🧪 Scenariusze testowe</h4>
                            <button class="btn" onclick="showAddTestScenarioForm()">Dodaj scenariusz</button>
                        </div>
                        
                        <table class="data-table" id="test-scenarios-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nazwa</th>
                                    <th>Typ testu</th>
                                    <th>Parametry</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="5">Zaloguj się aby zobaczyć scenariusze...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- JSON Templates Tab -->
                    <div id="json-templates-tab" class="tab-content">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4>📋 Szablony JSON</h4>
                            <button class="btn" onclick="showAddTemplateForm()">Dodaj szablon</button>
                        </div>
                        
                        <div style="margin: 20px 0;">
                            <label style="margin-right: 10px;">Filtruj po typie:</label>
                            <select id="template-type-filter" onchange="loadJsonTemplates()" style="padding: 5px; margin-right: 15px;">
                                <option value="">Wszystkie typy</option>
                                <option value="test_flow">Test Flow</option>
                                <option value="device_config">Konfiguracja urządzenia</option>
                                <option value="system_config">Konfiguracja systemu</option>
                            </select>
                            
                            <label style="margin-right: 10px;">Kategoria:</label>
                            <select id="template-category-filter" onchange="loadJsonTemplates()" style="padding: 5px;">
                                <option value="">Wszystkie kategorie</option>
                                <option value="mask_tester">Tester masek</option>
                                <option value="pressure_sensor">Czujnik ciśnienia</option>
                                <option value="flow_meter">Przepływomierz</option>
                            </select>
                        </div>
                        
                        <table class="data-table" id="json-templates-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nazwa</th>
                                    <th>Typ</th>
                                    <th>Kategoria</th>
                                    <th>Opis</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="6">Zaloguj się aby zobaczyć szablony...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Backup/Restore Tab -->
                    <div id="backup-tab" class="tab-content">
                        <h4>💾 Backup i Restore konfiguracji</h4>
                        
                        <div class="backup-section">
                            <h5>Backup konfiguracji</h5>
                            <p>Utwórz kopię zapasową wszystkich konfiguracji systemu:</p>
                            <button class="btn btn-success" onclick="createBackup()">Utwórz Backup</button>
                        </div>

                        <div class="backup-section">
                            <h5>Restore konfiguracji</h5>
                            <p>Przywróć konfigurację z pliku backup:</p>
                            <div id="restore-data-editor" style="margin-bottom: 10px;"></div>
                            <button class="btn btn-danger" onclick="restoreBackup()">Przywróć z Backup</button>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3 id="form-title">Formularz konfiguracji</h3>
                    
                    <!-- Add System Config Form -->
                    <div id="add-system-config-form" style="display: none;">
                        <h4>Dodaj konfigurację systemu</h4>
                        <form id="system-config-form">
                            <div class="form-group">
                                <label>Nazwa konfiguracji:</label>
                                <input type="text" id="config-name" required>
                            </div>
                            <div class="form-group">
                                <label>Typ konfiguracji:</label>
                                <select id="config-type" required>
                                    <option value="">Wybierz typ</option>
                                    <option value="device_settings">Ustawienia urządzeń</option>
                                    <option value="test_parameters">Parametry testów</option>
                                    <option value="system_limits">Limity systemu</option>
                                    <option value="network_config">Konfiguracja sieci</option>
                                    <option value="security_config">Konfiguracja bezpieczeństwa</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Wartości konfiguracji (JSON):</label>
                                <div id="config-value-editor"></div>
                            </div>
                            <div class="form-group">
                                <label>Opis:</label>
                                <textarea id="config-description" rows="3"></textarea>
                            </div>
                            <button type="button" class="btn" onclick="createSystemConfig()">Dodaj konfigurację</button>
                            <button type="button" class="btn btn-secondary" onclick="hideSystemConfigForm()">Anuluj</button>
                        </form>
                    </div>

                    <!-- Add Test Scenario Form -->
                    <div id="add-test-scenario-form" style="display: none;">
                        <h4>Dodaj scenariusz testowy</h4>
                        <form id="test-scenario-form">
                            <div class="form-group">
                                <label>Nazwa scenariusza:</label>
                                <input type="text" id="scenario-name" required>
                            </div>
                            <div class="form-group">
                                <label>Typ testu:</label>
                                <select id="test-type" required>
                                    <option value="">Wybierz typ</option>
                                    <option value="mask_leak_test">Test nieszczelności maski</option>
                                    <option value="pressure_test">Test ciśnienia</option>
                                    <option value="flow_test">Test przepływu</option>
                                    <option value="calibration_test">Test kalibracji</option>
                                    <option value="functional_test">Test funkcjonalny</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Parametry (JSON):</label>
                                <div id="test-parameters-editor"></div>
                            </div>
                            <div class="form-group">
                                <label>Oczekiwane wyniki (JSON):</label>
                                <div id="expected-results-editor"></div>
                            </div>
                            <button type="button" class="btn" onclick="createTestScenario()">Dodaj scenariusz</button>
                            <button type="button" class="btn btn-secondary" onclick="hideTestScenarioForm()">Anuluj</button>
                        </form>
                    </div>

                    <!-- Device Config Form -->
                    <div id="device-config-form" style="display: none;">
                        <h4>Konfiguracja urządzenia</h4>
                        <form id="device-config-edit-form">
                            <div class="form-group">
                                <label>ID urządzenia:</label>
                                <input type="number" id="device-config-id" readonly>
                            </div>
                            <div class="form-group">
                                <label>Konfiguracja (JSON):</label>
                                <textarea id="device-configuration" rows="8" placeholder='{"baudrate": 9600, "timeout": 5}'></textarea>
                            </div>
                            <button type="button" class="btn" onclick="updateDeviceConfig()">Aktualizuj konfigurację</button>
                            <button type="button" class="btn btn-secondary" onclick="hideDeviceConfigForm()">Anuluj</button>
                        </form>
                    </div>

                    <!-- Add/Edit JSON Template Form -->
                    <div id="add-template-form" style="display: none;">
                        <h4 id="template-form-title">Dodaj szablon JSON</h4>
                        <form id="json-template-form">
                            <input type="hidden" id="template-id">
                            
                            <div class="form-group">
                                <label>Nazwa szablonu:</label>
                                <input type="text" id="template-name" required placeholder="np. Test Szczelności Maski">
                            </div>
                            
                            <div class="form-group">
                                <label>Typ szablonu:</label>
                                <select id="template-type" required>
                                    <option value="">Wybierz typ</option>
                                    <option value="test_flow">Test Flow</option>
                                    <option value="device_config">Konfiguracja urządzenia</option>
                                    <option value="system_config">Konfiguracja systemu</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Kategoria:</label>
                                <select id="template-category">
                                    <option value="">Wybierz kategorię (opcjonalnie)</option>
                                    <option value="mask_tester">Tester masek</option>
                                    <option value="pressure_sensor">Czujnik ciśnienia</option>
                                    <option value="flow_meter">Przepływomierz</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Opis:</label>
                                <textarea id="template-description" rows="2" placeholder="Krótki opis szablonu"></textarea>
                            </div>
                            
                            <div class="form-group">
                                <label>📝 Wartości domyślne (JSON):</label>
                                <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
                                    <button type="button" class="btn btn-secondary" onclick="templateJsonEditor.addField()">➕ Dodaj pole</button>
                                    <button type="button" class="btn btn-secondary" onclick="clearTemplateJSON()">🗑️ Wyczyść</button>
                                    <button type="button" class="btn btn-secondary" onclick="toggleTemplateJSONView()">👁️ Podgląd JSON</button>
                                </div>
                                <div id="template-json-tree-editor" style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background: #f8f9fa; max-height: 400px; overflow-y: auto;">
                                    <!-- Tree editor będzie tu renderowany -->
                                </div>
                                <div id="template-json-preview" style="display: none; margin-top: 10px; padding: 10px; background: #2c3e50; color: #ecf0f1; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto;">
                                    <!-- JSON preview -->
                                </div>
                                <small style="color: #7f8c8d;">
                                    Edytuj wartości domyślne używając pól powyżej
                                </small>
                                <div id="json-validation-result" style="margin-top: 5px;"></div>
                            </div>
                            
                            <div class="form-group">
                                <label>Schema JSON (opcjonalnie):</label>
                                <textarea id="template-schema" rows="6" style="font-family: monospace; font-size: 12px;" 
                                    placeholder='{"type": "object", "properties": {...}}'></textarea>
                                <small style="color: #7f8c8d;">
                                    JSON Schema dla walidacji (opcjonalnie)
                                </small>
                            </div>
                            
                            <button type="button" class="btn" onclick="saveTemplate()">💾 Zapisz szablon</button>
                            <button type="button" class="btn btn-secondary" onclick="hideTemplateForm()">Anuluj</button>
                        </form>
                    </div>
                </div>
            </div>

            <div id="result" style="margin-top: 20px;"></div>
                </div>
            </div>
            
            <!-- Right sidebar with login -->
            <div class="right-sidebar">
                <div class="sidebar-auth">
                    <h4>🔐 Logowanie</h4>
                    <input type="text" id="login-username" placeholder="Username">
                    <input type="password" id="login-password" placeholder="Password">
                    <button class="btn" onclick="login()">Zaloguj</button>
                    <button class="btn btn-secondary" onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                    <div id="auth-message"></div>
                </div>

                <div class="role-switcher" id="role-switcher">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #ecf0f1;">🔄 Przełącz rolę:</label>
                    <select id="role-select" onchange="switchRole()">
                        <option value="">Wybierz rolę...</option>
                    </select>
                </div>
            </div>
        </div>

        <script>
            let authToken = null;
            let systemConfigs = [];
            let deviceConfigs = [];
            let testScenarios = [];

            // ========== UNIVERSAL JSON TREE EDITOR ==========
            class JSONTreeEditor {
                constructor(containerId) {
                    this.container = document.getElementById(containerId);
                    this.data = {};
                    this.fieldCounter = 0;
                }

                init(jsonData = {}) {
                    this.data = jsonData;
                    this.render();
                }

                render() {
                    this.container.innerHTML = '';
                    if (Object.keys(this.data).length === 0) {
                        this.container.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 20px;">Brak pól. Kliknij "+ Dodaj pole" aby rozpocząć</p>';
                        return;
                    }
                    
                    for (const [key, value] of Object.entries(this.data)) {
                        this.renderField(key, value, this.container);
                    }
                }

                renderField(key, value, parentElement, path = '') {
                    const fieldDiv = document.createElement('div');
                    fieldDiv.style.cssText = 'margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; border: 1px solid #ddd;';
                    
                    const currentPath = path ? `${path}.${key}` : key;
                    const type = this.getType(value);
                    
                    const headerDiv = document.createElement('div');
                    headerDiv.style.cssText = 'display: flex; align-items: center; margin-bottom: 8px; gap: 10px;';
                    
                    const keyInput = document.createElement('input');
                    keyInput.type = 'text';
                    keyInput.value = key;
                    keyInput.style.cssText = 'flex: 0 0 180px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; font-weight: bold;';
                    keyInput.onchange = (e) => this.renameKey(path, key, e.target.value);
                    
                    const typeSelect = document.createElement('select');
                    typeSelect.style.cssText = 'flex: 0 0 100px; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;';
                    ['string', 'number', 'boolean', 'object', 'array'].forEach(t => {
                        const option = document.createElement('option');
                        option.value = t;
                        option.textContent = t;
                        option.selected = type === t;
                        typeSelect.appendChild(option);
                    });
                    typeSelect.onchange = (e) => this.changeType(currentPath, e.target.value);
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = '🗑️';
                    deleteBtn.className = 'btn btn-danger';
                    deleteBtn.style.cssText = 'padding: 3px 8px; margin-left: auto;';
                    deleteBtn.onclick = () => this.deleteField(currentPath);
                    
                    headerDiv.appendChild(keyInput);
                    headerDiv.appendChild(typeSelect);
                    headerDiv.appendChild(deleteBtn);
                    fieldDiv.appendChild(headerDiv);
                    
                    const valueDiv = document.createElement('div');
                    
                    if (type === 'object') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #3498db; margin-top: 10px;';
                        for (const [childKey, childValue] of Object.entries(value)) {
                            this.renderField(childKey, childValue, valueDiv, currentPath);
                        }
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj pole do obiektu';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addFieldToObject(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'array') {
                        valueDiv.style.cssText = 'padding-left: 20px; border-left: 3px solid #9b59b6; margin-top: 10px;';
                        value.forEach((item, index) => {
                            this.renderField(`[${index}]`, item, valueDiv, currentPath);
                        });
                        const addBtn = document.createElement('button');
                        addBtn.textContent = '+ Dodaj element do array';
                        addBtn.className = 'btn btn-secondary';
                        addBtn.style.cssText = 'margin-top: 5px; font-size: 12px; padding: 3px 10px;';
                        addBtn.onclick = () => this.addArrayElement(currentPath);
                        valueDiv.appendChild(addBtn);
                    } else if (type === 'boolean') {
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.checked = value;
                        checkbox.style.cssText = 'width: 20px; height: 20px;';
                        checkbox.onchange = (e) => this.setValue(currentPath, e.target.checked);
                        valueDiv.appendChild(checkbox);
                    } else if (type === 'number') {
                        const input = document.createElement('input');
                        input.type = 'number';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, parseFloat(e.target.value));
                        valueDiv.appendChild(input);
                    } else {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = value;
                        input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 3px;';
                        input.onchange = (e) => this.setValue(currentPath, e.target.value);
                        valueDiv.appendChild(input);
                    }
                    
                    fieldDiv.appendChild(valueDiv);
                    parentElement.appendChild(fieldDiv);
                }

                getType(value) {
                    if (Array.isArray(value)) return 'array';
                    if (value === null) return 'string';
                    return typeof value;
                }

                setValue(path, value) {
                    const keys = path.split('.').filter(k => k && !k.startsWith('['));
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = value;
                    this.render();
                }

                addField() {
                    const newKey = `field_${this.fieldCounter++}`;
                    this.data[newKey] = '';
                    this.render();
                }

                addFieldToObject(path) {
                    const obj = this.getValueByPath(path);
                    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                        obj[`field_${this.fieldCounter++}`] = '';
                        this.render();
                    }
                }

                addArrayElement(path) {
                    const arr = this.getValueByPath(path);
                    if (arr && Array.isArray(arr)) {
                        arr.push('');
                        this.render();
                    }
                }

                deleteField(path) {
                    const keys = path.split('.').filter(k => k);
                    if (keys.length === 1) {
                        delete this.data[keys[0]];
                    } else {
                        let current = this.data;
                        for (let i = 0; i < keys.length - 1; i++) {
                            current = current[keys[i]];
                        }
                        delete current[keys[keys.length - 1]];
                    }
                    this.render();
                }

                renameKey(parentPath, oldKey, newKey) {
                    if (oldKey === newKey) return;
                    
                    if (!parentPath) {
                        this.data[newKey] = this.data[oldKey];
                        delete this.data[oldKey];
                    } else {
                        const parent = this.getValueByPath(parentPath);
                        parent[newKey] = parent[oldKey];
                        delete parent[oldKey];
                    }
                    this.render();
                }

                changeType(path, newType) {
                    const defaultValues = {
                        'string': '',
                        'number': 0,
                        'boolean': false,
                        'object': {},
                        'array': []
                    };
                    
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (let i = 0; i < keys.length - 1; i++) {
                        current = current[keys[i]];
                    }
                    current[keys[keys.length - 1]] = defaultValues[newType];
                    this.render();
                }

                getValueByPath(path) {
                    const keys = path.split('.').filter(k => k);
                    let current = this.data;
                    for (const key of keys) {
                        current = current[key];
                    }
                    return current;
                }

                clear() {
                    this.data = {};
                    this.render();
                }

                getJSON() {
                    return this.data;
                }

                setJSON(jsonData) {
                    this.data = jsonData;
                    this.render();
                }
            }

            // Initialize JSON Tree Editor for Templates
            const templateJsonEditor = new JSONTreeEditor('template-json-tree-editor');
            templateJsonEditor.init({});

            function toggleTemplateJSONView() {
                const preview = document.getElementById('template-json-preview');
                if (preview.style.display === 'none') {
                    preview.style.display = 'block';
                    preview.textContent = JSON.stringify(templateJsonEditor.getJSON(), null, 2);
                } else {
                    preview.style.display = 'none';
                }
            }

            function getAuthToken() {
                if (!authToken) {
                    authToken = localStorage.getItem('jwt_token');
                }
                return authToken;
            }

            function setAuthToken(token) {
                authToken = token;
                localStorage.setItem('jwt_token', token);
                updateAuthUI();
            }

            function clearAuthToken() {
                authToken = null;
                localStorage.removeItem('jwt_token');
                updateAuthUI();
            }

            function updateAuthUI() {
                const isLoggedIn = !!getAuthToken();
                document.getElementById('login-username').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('login-password').style.display = isLoggedIn ? 'none' : 'inline';
                document.querySelector('button[onclick="login()"]').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('logout-btn').style.display = isLoggedIn ? 'inline' : 'none';
                document.getElementById('dashboard-section').style.display = isLoggedIn ? 'block' : 'none';
                
                if (isLoggedIn) {
                    const userRoles = getUserRoles();
                    const activeRole = getActiveRole();
                    
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #9b59b6;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
                    
                    if (userRoles && userRoles.length > 1) {
                        const roleSelect = document.getElementById('role-select');
                        roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
                        userRoles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                            if (role === activeRole) {
                                option.selected = true;
                            }
                            roleSelect.appendChild(option);
                        });
                        document.getElementById('role-switcher').style.display = 'block';
                    } else {
                        document.getElementById('role-switcher').style.display = 'none';
                    }
                    
                    loadDashboard();
                    loadSystemConfigs();
                    loadDeviceConfigs();
                    loadTestScenarios();
                    loadJsonTemplates();
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
                    document.getElementById('role-switcher').style.display = 'none';
                    clearData();
                }
            }

            function getUserRoles() {
                const token = getAuthToken();
                if (!token) return [];
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.roles || [];
                } catch (e) {
                    return [];
                }
            }

            function getActiveRole() {
                const token = getAuthToken();
                if (!token) return '';
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.active_role || payload.role || '';
                } catch (e) {
                    return '';
                }
            }

            async function switchRole() {
                const selectedRole = document.getElementById('role-select').value;
                if (!selectedRole) return;

                try {
                    const response = await fetch('/api/v1/auth/switch-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify({ new_role: selectedRole })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #9b59b6;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
                        
                        loadSystemConfigs();
                        loadDeviceConfigs();
                        loadTestScenarios();
                        loadJsonTemplates();
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd przełączania roli: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function clearData() {
                document.getElementById('system-configs-list').innerHTML = 
                    '<p>Zaloguj się aby zobaczyć konfigurację systemu...</p>';
                document.getElementById('device-configs-table').getElementsByTagName('tbody')[0].innerHTML = 
                    '<tr><td colspan="6">Zaloguj się aby zobaczyć konfigurację urządzeń...</td></tr>';
                document.getElementById('test-scenarios-table').getElementsByTagName('tbody')[0].innerHTML = 
                    '<tr><td colspan="5">Zaloguj się aby zobaczyć scenariusze...</td></tr>';
            }

            async function login() {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    alert('Podaj username i hasło');
                    return;
                }

                try {
                    const formData = new URLSearchParams();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: green;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Zalogowano pomyślnie jako ${username} (${data.user.role})
                            </div>
                        `;
                    } else {
                        const error = await response.json();
                        const errorMsg = error.detail || 'Nieznany błąd';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd logowania: ${errorMsg}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function logout() {
                clearAuthToken();
                document.getElementById('login-username').value = '';
                document.getElementById('login-password').value = '';
                document.getElementById('result').innerHTML = `
                    <div class="result">
                    ℹ️ Wylogowano pomyślnie
                    </div>
                `;
            }

            async function makeAuthenticatedRequest(url, options = {}) {
                const token = getAuthToken();
                
                try {
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` }),
                            ...options.headers
                        }
                    });
                    return response;
                } catch (error) {
                    console.error('Request failed:', error);
                    throw error;
                }
            }

            function showTab(tabName, skipHashUpdate = false) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Find and activate corresponding button
                const buttons = document.querySelectorAll('.tab');
                buttons.forEach(btn => {
                    if (btn.onclick && btn.onclick.toString().includes(tabName)) {
                        btn.classList.add('active');
                    }
                });

                // Hide all forms
                hideAllForms();
                
                // Initialize restore editor when backup tab is shown
                if (tabName === 'backup' && !restoreDataEditor) {
                    restoreDataEditor = new JSONTreeEditor('restore-data-editor', {
                        system_configs: [],
                        device_configs: [],
                        test_scenarios: []
                    });
                }
                
                // Update URL hash
                if (!skipHashUpdate) {
                    window.location.hash = tabName;
                }
            }
            
            // Handle hash changes
            window.addEventListener('hashchange', function() {
                const hash = window.location.hash.substring(1);
                if (hash) {
                    const tabElement = document.getElementById(hash + '-tab');
                    if (tabElement) {
                        showTab(hash, true);
                    }
                }
            });
            
            // Load tab from hash on page load
            window.addEventListener('DOMContentLoaded', function() {
                const hash = window.location.hash.substring(1);
                if (hash) {
                    showTab(hash, true);
                } else {
                    showTab('system-config', false);
                }
            });

            function hideAllForms() {
                document.getElementById('add-system-config-form').style.display = 'none';
                document.getElementById('add-test-scenario-form').style.display = 'none';
                document.getElementById('device-config-form').style.display = 'none';
                document.getElementById('add-template-form').style.display = 'none';
                document.getElementById('form-title').textContent = 'Formularz konfiguracji';
            }

            async function loadDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/dashboard');
                    
                    if (response.ok) {
                        const data = await response.json();
                        displayDashboard(data);
                    }
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }

            function displayDashboard(data) {
                const container = document.getElementById('dashboard-stats');
                container.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${data.total_devices}</div>
                        <div class="stat-label">Urządzenia</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.configured_devices}</div>
                        <div class="stat-label">Skonfigurowane</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.total_test_scenarios}</div>
                        <div class="stat-label">Scenariusze</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.configuration_coverage}%</div>
                        <div class="stat-label">Pokrycie konfiguracji</div>
                    </div>
                `;
            }

            async function loadSystemConfigs() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/system-configs');
                    
                    if (response.ok) {
                        systemConfigs = await response.json();
                        displaySystemConfigs(systemConfigs);
                    } else if (response.status === 401 || response.status === 403) {
                        document.getElementById('system-configs-list').innerHTML = 
                            '<p style="color: #e74c3c;">❌ Brak autoryzacji Configurator</p>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania konfiguracji systemu: ${error.message}
                        </div>
                    `;
                }
            }

            function displaySystemConfigs(configs) {
                const container = document.getElementById('system-configs-list');
                if (configs.length === 0) {
                    container.innerHTML = '<p>Brak konfiguracji systemu.</p>';
                    return;
                }

                container.innerHTML = configs.map(config => `
                    <div class="config-card">
                        <div class="config-header">${config.config_name} (${config.config_type})</div>
                        <div class="config-value">${JSON.stringify(config.config_value, null, 2)}</div>
                        <div style="margin-top: 10px;">
                            <small>Opis: ${config.description || 'Brak opisu'}</small>
                            <div style="float: right;">
                                <button class="btn btn-secondary" onclick="editSystemConfig(${config.id})">Edytuj</button>
                                <button class="btn btn-danger" onclick="deleteSystemConfig(${config.id})">Usuń</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            async function loadDeviceConfigs() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/device-configs');
                    
                    if (response.ok) {
                        deviceConfigs = await response.json();
                        displayDeviceConfigs(deviceConfigs);
                    } else if (response.status === 401 || response.status === 403) {
                        document.getElementById('device-configs-table').getElementsByTagName('tbody')[0].innerHTML = 
                            '<tr><td colspan="6" style="color: #e74c3c;">❌ Brak autoryzacji Configurator</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania konfiguracji urządzeń: ${error.message}
                        </div>
                    `;
                }
            }

            function displayDeviceConfigs(configs) {
                const tbody = document.getElementById('device-configs-table').getElementsByTagName('tbody')[0];
                if (configs.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6">Brak urządzeń do konfiguracji.</td></tr>';
                    return;
                }

                tbody.innerHTML = configs.map(device => `
                    <tr>
                        <td>${device.device_id}</td>
                        <td>${device.device_number}</td>
                        <td>${device.device_type}</td>
                        <td>${device.status}</td>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                            ${Object.keys(device.configuration).length > 0 ? 'Skonfigurowane' : 'Brak konfiguracji'}
                        </td>
                        <td>
                            <button class="btn btn-secondary" onclick="editDeviceConfig(${device.device_id})">Konfiguruj</button>
                        </td>
                    </tr>
                `).join('');
            }

            async function loadTestScenarios() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/test-scenario-configs');
                    
                    if (response.ok) {
                        testScenarios = await response.json();
                        displayTestScenarios(testScenarios);
                    } else if (response.status === 401 || response.status === 403) {
                        document.getElementById('test-scenarios-table').getElementsByTagName('tbody')[0].innerHTML = 
                            '<tr><td colspan="5" style="color: #e74c3c;">❌ Brak autoryzacji Configurator</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania scenariuszy: ${error.message}
                        </div>
                    `;
                }
            }

            function displayTestScenarios(scenarios) {
                const tbody = document.getElementById('test-scenarios-table').getElementsByTagName('tbody')[0];
                if (scenarios.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5">Brak scenariuszy testowych.</td></tr>';
                    return;
                }

                tbody.innerHTML = scenarios.map(scenario => `
                    <tr>
                        <td>${scenario.scenario_id}</td>
                        <td>${scenario.scenario_name}</td>
                        <td>${scenario.test_type}</td>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                            ${JSON.stringify(scenario.parameters).substring(0, 50)}...
                        </td>
                        <td>
                            <button class="btn btn-secondary" onclick="editTestScenario(${scenario.scenario_id})">Edytuj</button>
                            <button class="btn btn-danger" onclick="deleteTestScenario(${scenario.scenario_id})">Usuń</button>
                        </td>
                    </tr>
                `).join('');
            }

            let configValueEditor = null;

            function showAddSystemConfigForm() {
                hideAllForms();
                document.getElementById('add-system-config-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Dodaj konfigurację systemu';
                
                // Initialize JSON editor for config-value
                if (!configValueEditor) {
                    configValueEditor = new JSONTreeEditor('config-value-editor', {
                        key: "value",
                        setting: 123,
                        enabled: true
                    });
                }
            }

            function hideSystemConfigForm() {
                // Reset JSON editor FIRST before hiding form
                if (configValueEditor) {
                    configValueEditor.setData({
                        key: "value",
                        setting: 123,
                        enabled: true
                    });
                }
                
                document.getElementById('add-system-config-form').style.display = 'none';
                document.getElementById('system-config-form').reset();
                document.getElementById('form-title').textContent = 'Formularz konfiguracji';
            }

            let testParametersEditor = null;
            let expectedResultsEditor = null;

            function showAddTestScenarioForm() {
                hideAllForms();
                document.getElementById('add-test-scenario-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Dodaj scenariusz testowy';
                
                // Initialize JSON editors
                if (!testParametersEditor) {
                    testParametersEditor = new JSONTreeEditor('test-parameters-editor', {
                        duration: 300,
                        pressure: 50,
                        tolerance: 2
                    });
                }
                
                if (!expectedResultsEditor) {
                    expectedResultsEditor = new JSONTreeEditor('expected-results-editor', {
                        pass_criteria: "value < 10",
                        units: "Pa"
                    });
                }
            }

            function hideTestScenarioForm() {
                // Reset JSON editors FIRST before hiding form
                if (testParametersEditor) {
                    testParametersEditor.setData({
                        duration: 300,
                        pressure: 50,
                        tolerance: 2
                    });
                }
                
                if (expectedResultsEditor) {
                    expectedResultsEditor.setData({
                        pass_criteria: "value < 10",
                        units: "Pa"
                    });
                }
                
                document.getElementById('add-test-scenario-form').style.display = 'none';
                document.getElementById('test-scenario-form').reset();
                document.getElementById('form-title').textContent = 'Formularz konfiguracji';
            }

            function hideDeviceConfigForm() {
                document.getElementById('device-config-form').style.display = 'none';
                document.getElementById('device-config-edit-form').reset();
                document.getElementById('form-title').textContent = 'Formularz konfiguracji';
            }

            function editDeviceConfig(deviceId) {
                const device = deviceConfigs.find(d => d.device_id === deviceId);
                if (!device) return;

                hideAllForms();
                document.getElementById('device-config-form').style.display = 'block';
                document.getElementById('form-title').textContent = `Konfiguracja urządzenia ${device.device_number}`;
                document.getElementById('device-config-id').value = deviceId;
                document.getElementById('device-configuration').value = JSON.stringify(device.configuration, null, 2);
            }

            async function updateDeviceConfig() {
                const deviceId = document.getElementById('device-config-id').value;
                const configText = document.getElementById('device-configuration').value;
                
                let configuration;
                try {
                    configuration = JSON.parse(configText);
                } catch (e) {
                    alert('Nieprawidłowy format JSON w konfiguracji');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/device-configs/${deviceId}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            device_id: parseInt(deviceId),
                            configuration: configuration
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            </div>
                        `;
                        hideDeviceConfigForm();
                        loadDeviceConfigs();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd aktualizacji konfiguracji: ${error.message}
                        </div>
                    `;
                }
            }

            async function createSystemConfig() {
                const configData = {
                    config_name: document.getElementById('config-name').value,
                    config_type: document.getElementById('config-type').value,
                    config_value: {},
                    description: document.getElementById('config-description').value
                };

                // Get JSON data from editor
                if (configValueEditor) {
                    configData.config_value = configValueEditor.getData();
                } else {
                    alert('Edytor JSON nie został zainicjalizowany');
                    return;
                }

                if (!configData.config_name || !configData.config_type) {
                    alert('Podaj nazwę i typ konfiguracji');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/system-configs', {
                        method: 'POST',
                        body: JSON.stringify(configData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Konfiguracja ${result.config_name} została dodana pomyślnie
                            </div>
                        `;
                        hideSystemConfigForm();
                        loadSystemConfigs();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd tworzenia konfiguracji: ${error.message}
                        </div>
                    `;
                }
            }

            async function editSystemConfig(configId) {
                const config = systemConfigs.find(c => c.id === configId);
                if (!config) return;

                document.getElementById('add-config-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Edytuj konfigurację systemową';

                document.getElementById('config-name').value = config.config_name;
                document.getElementById('config-type').value = config.config_type;
                document.getElementById('config-description').value = config.description || '';
                
                if (configValueEditor) {
                    configValueEditor.setData(config.config_value || {});
                }
            }

            async function deleteSystemConfig(configId) {
                if (!confirm('Czy na pewno chcesz usunąć tę konfigurację systemową?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/system-configs/${configId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message || 'Konfiguracja została usunięta'}
                            </div>
                        `;
                        loadSystemConfigs();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania konfiguracji: ${error.message}
                        </div>
                    `;
                }
            }

            async function createTestScenario() {
                const scenarioData = {
                    scenario_name: document.getElementById('scenario-name').value,
                    test_type: document.getElementById('test-type').value,
                    parameters: {},
                    expected_results: {}
                };

                // Get JSON data from editors
                if (testParametersEditor) {
                    scenarioData.parameters = testParametersEditor.getData();
                } else {
                    alert('Edytor parametrów nie został zainicjalizowany');
                    return;
                }
                
                if (expectedResultsEditor) {
                    scenarioData.expected_results = expectedResultsEditor.getData();
                }

                if (!scenarioData.scenario_name || !scenarioData.test_type) {
                    alert('Podaj nazwę i typ scenariusza');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/test-scenario-configs', {
                        method: 'POST',
                        body: JSON.stringify(scenarioData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            </div>
                        `;
                        hideTestScenarioForm();
                        loadTestScenarios();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd tworzenia scenariusza: ${error.message}
                        </div>
                    `;
                }
            }

            async function editTestScenario(scenarioId) {
                const scenario = testScenarios.find(s => s.scenario_id === scenarioId);
                if (!scenario) return;

                document.getElementById('add-scenario-form').style.display = 'block';
                document.getElementById('form-title').textContent = 'Edytuj scenariusz testowy';

                document.getElementById('scenario-name').value = scenario.scenario_name;
                document.getElementById('test-type').value = scenario.test_type;

                if (testParametersEditor) {
                    testParametersEditor.setData(scenario.parameters || {});
                }
                if (expectedResultsEditor) {
                    expectedResultsEditor.setData(scenario.expected_results || {});
                }
            }

            async function deleteTestScenario(scenarioId) {
                if (!confirm('Czy na pewno chcesz usunąć ten scenariusz testowy?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/test-scenario-configs/${scenarioId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message || 'Scenariusz został usunięty'}
                            </div>
                        `;
                        loadTestScenarios();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania scenariusza: ${error.message}
                        </div>
                    `;
                }
            }

            async function createBackup() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/backup', {
                        method: 'POST'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            Backup ID: ${result.backup_id}
                            
                            Dane backup:
                            ${JSON.stringify(result.backup_data, null, 2)}
                            </div>
                        `;
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd tworzenia backup: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd backup: ${error.message}
                        </div>
                    `;
                }
            }

            let restoreDataEditor = null;

            async function restoreBackup() {
                // Get data from JSON editor
                if (!restoreDataEditor) {
                    alert('Edytor restore nie został zainicjalizowany');
                    return;
                }
                
                const backupData = restoreDataEditor.getData();
                
                if (!backupData || Object.keys(backupData).length === 0) {
                    alert('Podaj dane backup do przywrócenia');
                    return;
                }

                if (!confirm('Czy na pewno chcesz przywrócić konfigurację z backup? To może nadpisać obecną konfigurację.')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/restore', {
                        method: 'POST',
                        body: JSON.stringify(backupData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message}
                            Przywrócono: ${result.restored_at}
                            </div>
                        `;
                        
                        // Reset restore editor after successful restore
                        if (restoreDataEditor) {
                            restoreDataEditor.setData({
                                system_configs: [],
                                device_configs: [],
                                test_scenarios: []
                            });
                        }
                        
                        // Reload all data
                        loadDashboard();
                        loadSystemConfigs();
                        loadDeviceConfigs();
                        loadTestScenarios();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd przywracania: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd restore: ${error.message}
                        </div>
                    `;
                }
            }

            async function testConfigAPI() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/system-configs');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Fleet Config API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Fleet Config API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            // ========== JSON TEMPLATES FUNCTIONS ==========
            let jsonTemplates = [];
            let editingTemplateId = null;

            async function loadJsonTemplates() {
                const typeFilter = document.getElementById('template-type-filter').value;
                const categoryFilter = document.getElementById('template-category-filter').value;
                
                let url = '/api/v1/fleet-config/json-templates?';
                if (typeFilter) url += `template_type=${typeFilter}&`;
                if (categoryFilter) url += `category=${categoryFilter}&`;
                
                try {
                    const response = await makeAuthenticatedRequest(url);
                    
                    if (response.ok) {
                        jsonTemplates = await response.json();
                        displayJsonTemplates(jsonTemplates);
                    } else if (response.status === 401 || response.status === 403) {
                        document.querySelector('#json-templates-table tbody').innerHTML = 
                            '<tr><td colspan="6" style="color: #e74c3c;">❌ Brak autoryzacji Configurator</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania szablonów JSON: ${error.message}
                        </div>
                    `;
                }
            }

            function displayJsonTemplates(templates) {
                const tbody = document.querySelector('#json-templates-table tbody');
                if (templates.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6">Brak szablonów JSON. Dodaj pierwszy szablon!</td></tr>';
                    return;
                }

                tbody.innerHTML = templates.map(template => `
                    <tr>
                        <td>${template.id}</td>
                        <td><strong>${template.name}</strong></td>
                        <td><span style="background: #3498db; color: white; padding: 2px 8px; border-radius: 3px;">${template.template_type}</span></td>
                        <td>${template.category || '-'}</td>
                        <td>${template.description || '-'}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="viewTemplate(${template.id})">👁️ Podgląd</button>
                            <button class="btn btn-secondary" onclick="editTemplate(${template.id})">✏️ Edytuj</button>
                            <button class="btn btn-danger" onclick="deleteTemplate(${template.id})">🗑️ Usuń</button>
                        </td>
                    </tr>
                `).join('');
            }

            function showAddTemplateForm() {
                hideAllForms();
                editingTemplateId = null;
                document.getElementById('template-form-title').textContent = 'Dodaj szablon JSON';
                document.getElementById('add-template-form').style.display = 'block';
                document.getElementById('json-template-form').reset();
                templateJsonEditor.clear();
                document.getElementById('template-json-preview').style.display = 'none';
                document.getElementById('template-id').value = '';
                document.getElementById('form-title').textContent = 'Nowy szablon JSON';
            }

            function hideTemplateForm() {
                document.getElementById('add-template-form').style.display = 'none';
                document.getElementById('json-template-form').reset();
                templateJsonEditor.clear();
                document.getElementById('template-json-preview').style.display = 'none';
                editingTemplateId = null;
                document.getElementById('form-title').textContent = 'Formularz konfiguracji';
            }

            function viewTemplate(templateId) {
                const template = jsonTemplates.find(t => t.id === templateId);
                if (template) {
                    document.getElementById('result').innerHTML = `
                        <div class="result" style="background: #e8f5e9; border-color: #4caf50;">
                            <h4>📋 ${template.name}</h4>
                            <p><strong>Typ:</strong> ${template.template_type} | <strong>Kategoria:</strong> ${template.category || 'Brak'}</p>
                            <p><strong>Opis:</strong> ${template.description || 'Brak opisu'}</p>
                            <h5>Wartości domyślne:</h5>
                            <pre style="background: white; padding: 15px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(template.default_values, null, 2)}</pre>
                            ${template.schema ? `<h5>Schema:</h5><pre style="background: white; padding: 15px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(template.schema, null, 2)}</pre>` : ''}
                        </div>
                    `;
                }
            }

            function editTemplate(templateId) {
                const template = jsonTemplates.find(t => t.id === templateId);
                if (template) {
                    hideAllForms();
                    editingTemplateId = templateId;
                    document.getElementById('template-form-title').textContent = 'Edytuj szablon JSON';
                    document.getElementById('add-template-form').style.display = 'block';
                    
                    document.getElementById('template-id').value = template.id;
                    document.getElementById('template-name').value = template.name;
                    document.getElementById('template-type').value = template.template_type;
                    document.getElementById('template-category').value = template.category || '';
                    document.getElementById('template-description').value = template.description || '';
                    templateJsonEditor.setJSON(template.default_values);
                    document.getElementById('template-schema').value = template.schema ? JSON.stringify(template.schema, null, 2) : '';
                    document.getElementById('template-json-preview').style.display = 'none';
                    
                    document.getElementById('form-title').textContent = 'Edycja szablonu JSON';
                }
            }

            async function deleteTemplate(templateId) {
                if (!confirm('Czy na pewno chcesz usunąć ten szablon JSON?')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/json-templates/${templateId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Szablon został usunięty
                            </div>
                        `;
                        loadJsonTemplates();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania szablonu: ${error.message}
                        </div>
                    `;
                }
            }

            async function saveTemplate() {
                const templateData = {
                    name: document.getElementById('template-name').value,
                    template_type: document.getElementById('template-type').value,
                    category: document.getElementById('template-category').value || null,
                    description: document.getElementById('template-description').value || null
                };

                // Get JSON from tree editor
                const defaultValues = templateJsonEditor.getJSON();
                if (Object.keys(defaultValues).length === 0) {
                    alert('Wartości domyślne (JSON) są wymagane - dodaj przynajmniej jedno pole');
                    return;
                }
                templateData.default_values = defaultValues;

                // Parse schema JSON (optional)
                try {
                    const schemaText = document.getElementById('template-schema').value;
                    if (schemaText.trim()) {
                        templateData.schema = JSON.parse(schemaText);
                    }
                } catch (e) {
                    alert('Błąd parsowania Schema JSON: ' + e.message);
                    return;
                }

                if (!templateData.name || !templateData.template_type) {
                    alert('Nazwa i typ szablonu są wymagane');
                    return;
                }

                try {
                    let response;
                    if (editingTemplateId) {
                        // Update existing template
                        response = await makeAuthenticatedRequest(`/api/v1/fleet-config/json-templates/${editingTemplateId}`, {
                            method: 'PUT',
                            body: JSON.stringify(templateData)
                        });
                    } else {
                        // Create new template
                        response = await makeAuthenticatedRequest('/api/v1/fleet-config/json-templates', {
                            method: 'POST',
                            body: JSON.stringify(templateData)
                        });
                    }

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Szablon "${result.name}" został ${editingTemplateId ? 'zaktualizowany' : 'utworzony'} pomyślnie
                            </div>
                        `;
                        hideTemplateForm();
                        loadJsonTemplates();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd zapisywania szablonu: ${error.message}
                        </div>
                    `;
                }
            }

            function clearTemplateJSON() {
                if (confirm('Czy na pewno chcesz wyczyścić wszystkie pola JSON?')) {
                    templateJsonEditor.clear();
                    document.getElementById('template-json-preview').style.display = 'none';
                }
            }

            async function testConfigDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-config/dashboard');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Config Dashboard API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Config Dashboard API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateAuthUI();
            });
        </script>
    </body>
    </html>
    """

# Fleet Software Manager Module
@app.get("/fleet-software-manager", response_class=HTMLResponse)
async def fleet_software_manager():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fleet Software Manager - Fleet Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .nav-menu { background: #2c3e50; padding: 0; margin: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; }
            .nav-menu li { margin: 0; }
            .nav-menu a { display: block; padding: 15px 20px; color: white; text-decoration: none; transition: background 0.3s; }
            .nav-menu a:hover { background: #34495e; }
            .nav-menu a.active { background: #34495e; }
            .header { display: none; }
            .module-info { display: none; }
            .auth-section { display: none; }
            .app-layout { display: flex; min-height: calc(100vh - 52px); }
            .sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .sidebar .menu-section { margin-top: 20px; }
            .sidebar .menu-item { display: block; padding: 12px; background: #34495e; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 8px; cursor: pointer; transition: background 0.3s; }
            .sidebar .menu-item:hover { background: #7f8c8d; }
            .sidebar .menu-item.active { background: #27ae60; font-weight: bold; }
            .main-content-wrapper { width: 70%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
            .right-sidebar { width: 15%; background: #2c3e50; color: white; padding: 20px; box-sizing: border-box; position: sticky; top: 0; height: calc(100vh - 52px); overflow-y: auto; }
            .right-sidebar h3 { margin-top: 0; font-size: 16px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
            .right-sidebar .login-section { background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .right-sidebar .login-section input { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #95a5a6; border-radius: 4px; box-sizing: border-box; }
            .right-sidebar .login-section button { width: 100%; margin-bottom: 5px; }
            .right-sidebar .role-switcher { margin-top: 15px; padding: 10px; background: #34495e; border-radius: 8px; display: none; }
            .right-sidebar .role-switcher select { width: 100%; padding: 8px; border: 1px solid #95a5a6; border-radius: 4px; background: white; }
            .container { max-width: 100%; margin: 0; padding: 0; }
            .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; color: #34495e; }
            .stat-label { color: #666; margin-top: 5px; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .tabs { display: flex; margin-bottom: 20px; flex-wrap: wrap; }
            .tab { padding: 8px 15px; background: #bdc3c7; color: #333; cursor: pointer; border: none; margin: 2px; font-size: 12px; }
            .tab.active { background: #34495e; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .btn { background: #34495e; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #2c3e50; }
            .btn-secondary { background: #95a5a6; }
            .btn-secondary:hover { background: #7f8c8d; }
            .btn-success { background: #27ae60; }
            .btn-success:hover { background: #229954; }
            .btn-danger { background: #e74c3c; }
            .btn-danger:hover { background: #c0392b; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .data-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }
            .data-table th, .data-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            .data-table th { background-color: #f8f9fa; font-weight: bold; }
            .data-table tr:hover { background-color: #f5f5f5; }
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; border-left: 4px solid #34495e; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
            .auth-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
            .version-badge { background: #3498db; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; }
            .status-badge { padding: 2px 6px; border-radius: 3px; font-size: 10px; color: white; }
            .status-installed { background: #27ae60; }
            .status-pending { background: #f39c12; }
            .status-failed { background: #e74c3c; }
            .category-badge { background: #9b59b6; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; }
            
            @media (max-width: 768px) {
                .app-layout { flex-direction: column; }
                .sidebar { width: 100%; height: auto; position: relative; border-bottom: 2px solid #34495e; }
                .main-content-wrapper { width: 100%; }
                .right-sidebar { width: 100%; height: auto; position: relative; border-top: 2px solid #34495e; }
                .main-content { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <nav class="nav-menu">
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/connect-plus">🔗 Connect++</a></li>
                <li><a href="/commands-manager">⚙️ Commands Manager</a></li>
                <li><a href="/fleet-data-manager">📊 Fleet Data Manager</a></li>
                <li><a href="/fleet-config-manager">🔧 Fleet Config Manager</a></li>
                <li><a href="/fleet-software-manager" class="active">💿 Fleet Software Manager</a></li>
                <li><a href="/docs">📚 API Docs</a></li>
            </ul>
        </nav>
        <div class="app-layout">
            <div class="sidebar">
                <h3>💿 Menu Modułu</h3>
                <div class="menu-section">
                    <div class="menu-item" onclick="scrollToSection('dashboard')">📊 Dashboard</div>
                    <div class="menu-item active" onclick="showTab('software-tab', this)">📦 Oprogramowanie</div>
                    <div class="menu-item" onclick="showTab('versions-tab', this)">🔢 Wersje</div>
                    <div class="menu-item" onclick="showTab('installations-tab', this)">💾 Instalacje</div>
                </div>
                
                <div style="margin-top: 20px; padding: 10px; background: #374151; border-radius: 8px;">
                    <h4 style="margin-top: 0; font-size: 14px; border-bottom: 2px solid #27ae60; padding-bottom: 8px;">🔍 API Endpoints Test</h4>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px; font-size: 12px;" onclick="testSoftwareAPI()">Test Software API</button>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px; font-size: 12px;" onclick="testVersionsAPI()">Test Versions API</button>
                    <button class="btn btn-secondary" style="width: 100%; margin-bottom: 5px; font-size: 12px;" onclick="testInstallationsAPI()">Test Installations API</button>
                    <button class="btn btn-secondary" style="width: 100%; font-size: 12px;" onclick="testDashboard()">Test Dashboard</button>
                </div>
            </div>

            <div class="main-content-wrapper">
            <div class="container">
            <div class="header">
                <h1>💾 Fleet Software Manager</h1>
            </div>
            
            <div class="module-info">
                <h3>Moduł dla Maker</h3>
                <p><strong>Port:</strong> 5000</p>
                <p><strong>Rola:</strong> Maker</p>
                <p><strong>Funkcje:</strong> Zarządzanie oprogramowaniem urządzeń, instalacje, aktualizacje</p>
            </div>

            <!-- Dashboard Statistics -->
            <div class="dashboard" id="dashboard">
                <div class="stat-card">
                    <div class="stat-value" id="total-software">-</div>
                    <div class="stat-label">Całkowite oprogramowanie</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-versions">-</div>
                    <div class="stat-label">Wersje oprogramowania</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="devices-with-software">-</div>
                    <div class="stat-label">Urządzenia z oprogramowaniem</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="recent-installations">-</div>
                    <div class="stat-label">Dzisiejsze instalacje</div>
                </div>
            </div>

            <div class="main-content">
                <div class="section">
                    <div class="tabs">
                        <button class="tab active" onclick="showTab('software-tab', this)">Oprogramowanie</button>
                        <button class="tab" onclick="showTab('versions-tab', this)">Wersje</button>
                        <button class="tab" onclick="showTab('installations-tab', this)">Instalacje</button>
                    </div>

                    <!-- Software Management Tab -->
                    <div id="software-tab" class="tab-content active">
                        <h3>📦 Zarządzanie Oprogramowaniem</h3>
                        <button class="btn" onclick="loadSoftware()">Odśwież listę</button>
                        <button class="btn btn-success" onclick="showCreateSoftwareForm()">Dodaj oprogramowanie</button>
                        
                        <div id="software-list">
                            <p>Kliknij "Odśwież listę" aby załadować oprogramowanie...</p>
                        </div>

                        <!-- Create Software Form -->
                        <div id="create-software-form" style="display: none; margin-top: 20px; padding: 20px; border: 2px solid #34495e; border-radius: 8px;">
                            <h4>➕ Dodaj nowe oprogramowanie</h4>
                            <div class="form-group">
                                <label>Nazwa oprogramowania:</label>
                                <input type="text" id="software-name" required>
                            </div>
                            <div class="form-group">
                                <label>Opis:</label>
                                <textarea id="software-description" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label>Dostawca:</label>
                                <input type="text" id="software-vendor">
                            </div>
                            <div class="form-group">
                                <label>Kategoria:</label>
                                <select id="software-category">
                                    <option value="">Wybierz kategorię</option>
                                    <option value="firmware">Firmware</option>
                                    <option value="application">Aplikacja</option>
                                    <option value="driver">Driver</option>
                                    <option value="tool">Narzędzie</option>
                                    <option value="middleware">Middleware</option>
                                    <option value="os">System operacyjny</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Platforma:</label>
                                <input type="text" id="software-platform" placeholder="np. ARM, x86, Linux">
                            </div>
                            <div class="form-group">
                                <label>URL repozytorium:</label>
                                <input type="url" id="software-repository">
                            </div>
                            <button class="btn btn-success" onclick="createSoftware()">Utwórz</button>
                            <button class="btn btn-secondary" onclick="hideCreateSoftwareForm()">Anuluj</button>
                        </div>
                    </div>

                    <!-- Versions Management Tab -->
                    <div id="versions-tab" class="tab-content">
                        <h3>🔢 Zarządzanie Wersjami</h3>
                        <div class="form-group">
                            <label>Wybierz oprogramowanie:</label>
                            <select id="version-software-select" onchange="loadVersions()">
                                <option value="">-- Wybierz oprogramowanie --</option>
                            </select>
                        </div>
                        <button class="btn btn-success" onclick="showCreateVersionForm()" id="add-version-btn" style="display: none;">Dodaj wersję</button>
                        
                        <div id="versions-list">
                            <p>Wybierz oprogramowanie aby zobaczyć wersje...</p>
                        </div>

                        <!-- Create Version Form -->
                        <div id="create-version-form" style="display: none; margin-top: 20px; padding: 20px; border: 2px solid #34495e; border-radius: 8px;">
                            <h4>➕ Dodaj nową wersję</h4>
                            <div class="form-group">
                                <label>Numer wersji:</label>
                                <input type="text" id="version-number" required placeholder="np. 1.0.0">
                            </div>
                            <div class="form-group">
                                <label>Notatki wydania:</label>
                                <textarea id="version-release-notes" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label>URL pobierania:</label>
                                <input type="url" id="version-download-url">
                            </div>
                            <div style="display: flex; gap: 20px;">
                                <label><input type="checkbox" id="version-stable" checked> Stabilna</label>
                                <label><input type="checkbox" id="version-beta"> Beta</label>
                                <label><input type="checkbox" id="version-reboot"> Wymaga restart</label>
                            </div>
                            <br>
                            <button class="btn btn-success" onclick="createVersion()">Utwórz wersję</button>
                            <button class="btn btn-secondary" onclick="hideCreateVersionForm()">Anuluj</button>
                        </div>
                    </div>

                    <!-- Installations Tab -->
                    <div id="installations-tab" class="tab-content">
                        <h3>⚙️ Historia Instalacji</h3>
                        <button class="btn" onclick="loadInstallations()">Odśwież listę</button>
                        <button class="btn btn-success" onclick="showInstallationForm()">Nowa instalacja</button>
                        
                        <div id="installations-list">
                            <p>Kliknij "Odśwież listę" aby załadować historię instalacji...</p>
                        </div>

                        <!-- Installation Form -->
                        <div id="installation-form" style="display: none; margin-top: 20px; padding: 20px; border: 2px solid #34495e; border-radius: 8px;">
                            <h4>⚙️ Nowa instalacja oprogramowania</h4>
                            <div class="form-group">
                                <label>Urządzenie:</label>
                                <select id="installation-device" required>
                                    <option value="">-- Wybierz urządzenie --</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Wersja oprogramowania:</label>
                                <select id="installation-version" required>
                                    <option value="">-- Wybierz wersję --</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Akcja:</label>
                                <select id="installation-action" required>
                                    <option value="install">Instaluj</option>
                                    <option value="update">Aktualizuj</option>
                                    <option value="uninstall">Odinstaluj</option>
                                    <option value="rollback">Wycofaj</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Notatki:</label>
                                <textarea id="installation-notes" rows="3"></textarea>
                            </div>
                            <button class="btn btn-success" onclick="createInstallation()">Rozpocznij instalację</button>
                            <button class="btn btn-secondary" onclick="hideInstallationForm()">Anuluj</button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="result" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- Right sidebar with login -->
        <div class="right-sidebar">
            <h3>🔐 Logowanie</h3>
            <div class="login-section">
                <input type="text" id="login-username" placeholder="Username">
                <input type="password" id="login-password" placeholder="Password">
                <button class="btn btn-success" onclick="login()">Zaloguj</button>
                <button class="btn btn-danger" onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                <div id="auth-message" style="margin-top: 10px; font-size: 12px;"></div>
            </div>

            <div class="role-switcher" id="role-switcher">
                <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #ecf0f1;">🔄 Przełącz rolę:</label>
                <select id="role-select" onchange="switchRole()">
                    <option value="">Wybierz rolę...</option>
                </select>
            </div>
        </div>
    </div>

        <script>
            let authToken = null;
            let currentSoftwareId = null;
            let softwareList = [];

            function getAuthToken() {
                if (!authToken) {
                    authToken = localStorage.getItem('jwt_token');
                }
                return authToken;
            }

            function setAuthToken(token) {
                authToken = token;
                localStorage.setItem('jwt_token', token);
                updateAuthUI();
            }

            function clearAuthToken() {
                authToken = null;
                localStorage.removeItem('jwt_token');
                updateAuthUI();
            }

            function updateAuthUI() {
                const isLoggedIn = !!getAuthToken();
                document.getElementById('login-username').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('login-password').style.display = isLoggedIn ? 'none' : 'inline';
                document.querySelector('button[onclick="login()"]').style.display = isLoggedIn ? 'none' : 'inline';
                document.getElementById('logout-btn').style.display = isLoggedIn ? 'inline' : 'none';
                
                if (isLoggedIn) {
                    const userRoles = getUserRoles();
                    const activeRole = getActiveRole();
                    
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #27ae60;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
                    
                    if (userRoles && userRoles.length > 1) {
                        const roleSelect = document.getElementById('role-select');
                        roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
                        userRoles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                            if (role === activeRole) {
                                option.selected = true;
                            }
                            roleSelect.appendChild(option);
                        });
                        document.getElementById('role-switcher').style.display = 'block';
                    } else {
                        document.getElementById('role-switcher').style.display = 'none';
                    }
                    
                    loadDashboard();
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
                    document.getElementById('role-switcher').style.display = 'none';
                }
            }

            function getUserRoles() {
                const token = getAuthToken();
                if (!token) return [];
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.roles || [];
                } catch (e) {
                    return [];
                }
            }

            function getActiveRole() {
                const token = getAuthToken();
                if (!token) return '';
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    return payload.active_role || payload.role || '';
                } catch (e) {
                    return '';
                }
            }

            async function switchRole() {
                const selectedRole = document.getElementById('role-select').value;
                if (!selectedRole) return;

                try {
                    const response = await fetch('/api/v1/auth/switch-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify({ new_role: selectedRole })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #27ae60;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
                        
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd przełączania roli: ${error.detail}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function scrollToSection(sectionId) {
                const section = document.getElementById(sectionId);
                if (section) {
                    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    document.querySelectorAll('.menu-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    event.target.classList.add('active');
                }
            }

            async function login() {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (!username || !password) {
                    alert('Podaj username i hasło');
                    return;
                }

                try {
                    const formData = new URLSearchParams();
                    formData.append('username', username);
                    formData.append('password', password);

                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: green;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Zalogowano pomyślnie jako ${username} (${data.user.role})
                            </div>
                        `;
                    } else {
                        const error = await response.json();
                        const errorMsg = error.detail || 'Nieznany błąd';
                        document.getElementById('auth-message').innerHTML = 
                            `<span style="color: #e74c3c;">❌ Błąd logowania: ${errorMsg}</span>`;
                    }
                } catch (error) {
                    document.getElementById('auth-message').innerHTML = 
                        `<span style="color: #e74c3c;">❌ Błąd połączenia: ${error.message}</span>`;
                }
            }

            function logout() {
                clearAuthToken();
                document.getElementById('login-username').value = '';
                document.getElementById('login-password').value = '';
                document.getElementById('software-list').innerHTML = 
                    '<p>Zaloguj się aby zobaczyć oprogramowanie...</p>';
                document.getElementById('result').innerHTML = `
                    <div class="result">
                    ℹ️ Wylogowano pomyślnie
                    </div>
                `;
            }

            async function makeAuthenticatedRequest(url, options = {}) {
                const token = getAuthToken();
                
                try {
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` }),
                            ...options.headers
                        }
                    });
                    return response;
                } catch (error) {
                    console.error('Request failed:', error);
                    throw error;
                }
            }

            function showTab(tabId, tabButton, skipHashUpdate = false) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Remove active class from all tab buttons
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Remove active class from all menu items
                document.querySelectorAll('.menu-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Show selected tab and mark button as active
                document.getElementById(tabId).classList.add('active');
                if (tabButton) {
                    tabButton.classList.add('active');
                } else {
                    // Find button by onclick attribute
                    const buttons = document.querySelectorAll('.tab');
                    buttons.forEach(btn => {
                        if (btn.onclick && btn.onclick.toString().includes(tabId)) {
                            btn.classList.add('active');
                        }
                    });
                }
                
                // Update URL hash
                if (!skipHashUpdate) {
                    window.location.hash = tabId;
                }
            }
            
            // Handle hash changes
            window.addEventListener('hashchange', function() {
                const hash = window.location.hash.substring(1);
                if (hash) {
                    const tabElement = document.getElementById(hash);
                    if (tabElement && tabElement.classList.contains('tab-content')) {
                        showTab(hash, null, true);
                    }
                }
            });
            
            // Load tab from hash on page load
            window.addEventListener('DOMContentLoaded', function() {
                const hash = window.location.hash.substring(1);
                if (hash) {
                    showTab(hash, null, true);
                }
            });

            async function loadDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
                    
                    if (response.status === 401 || response.status === 403) {
                        return;
                    }

                    const stats = await response.json();
                    
                    document.getElementById('total-software').textContent = stats.total_software || 0;
                    document.getElementById('total-versions').textContent = stats.total_versions || 0;
                    document.getElementById('devices-with-software').textContent = stats.devices_with_software || 0;
                    document.getElementById('recent-installations').textContent = stats.recent_installations || 0;
                    
                } catch (error) {
                    console.error('Failed to load dashboard:', error);
                }
            }

            async function loadSoftware() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software');
                    
                    if (response.status === 401 || response.status === 403) {
                        document.getElementById('software-list').innerHTML = `
                            <div style="color: #e74c3c; padding: 10px;">
                            ❌ Brak autoryzacji. Zaloguj się jako Maker aby zobaczyć oprogramowanie.
                            </div>
                        `;
                        return;
                    }

                    softwareList = await response.json();
                    displaySoftware(softwareList);
                    populateSoftwareSelect();
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Błąd ładowania oprogramowania:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            function displaySoftware(software) {
                const container = document.getElementById('software-list');
                if (software.length === 0) {
                    container.innerHTML = '<p>Brak oprogramowania. Dodaj pierwsze oprogramowanie.</p>';
                    return;
                }

                let html = '<table class="data-table"><thead><tr>';
                html += '<th>Nazwa</th><th>Kategoria</th><th>Dostawca</th><th>Platforma</th>';
                html += '<th>Wersje</th><th>Najnowsza</th><th>Akcje</th></tr></thead><tbody>';
                
                software.forEach(sw => {
                    html += `<tr>
                        <td><strong>${sw.name}</strong><br><small>${sw.description || 'Brak opisu'}</small></td>
                        <td><span class="category-badge">${sw.category}</span></td>
                        <td>${sw.vendor || '-'}</td>
                        <td>${sw.platform || '-'}</td>
                        <td>${sw.versions_count}</td>
                        <td><span class="version-badge">${sw.latest_version || 'Brak'}</span></td>
                        <td>
                            <button class="btn btn-secondary" onclick="viewSoftware(${sw.id})" style="font-size: 10px; padding: 5px;">Zobacz</button>
                            <button class="btn btn-danger" onclick="deleteSoftware(${sw.id})" style="font-size: 10px; padding: 5px;">Usuń</button>
                        </td>
                    </tr>`;
                });
                
                html += '</tbody></table>';
                container.innerHTML = html;
            }

            function populateSoftwareSelect() {
                const select = document.getElementById('version-software-select');
                select.innerHTML = '<option value="">-- Wybierz oprogramowanie --</option>';
                
                softwareList.forEach(sw => {
                    select.innerHTML += `<option value="${sw.id}">${sw.name} (${sw.category})</option>`;
                });

                // Also populate installation device and version selects
                loadDevicesForInstallation();
                loadVersionsForInstallation();
            }

            async function loadDevicesForInstallation() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/devices');
                    const data = await response.json();
                    
                    const select = document.getElementById('installation-device');
                    select.innerHTML = '<option value="">-- Wybierz urządzenie --</option>';
                    
                    if (data.devices) {
                        data.devices.forEach(device => {
                            select.innerHTML += `<option value="${device.id}">${device.device_number} (${device.device_type})</option>`;
                        });
                    }
                } catch (error) {
                    console.error('Failed to load devices:', error);
                }
            }

            async function loadVersionsForInstallation() {
                const select = document.getElementById('installation-version');
                select.innerHTML = '<option value="">-- Wybierz wersję --</option>';
                
                // Load all versions from all software
                for (const sw of softwareList) {
                    try {
                        const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${sw.id}/versions`);
                        const versions = await response.json();
                        
                        versions.forEach(version => {
                            select.innerHTML += `<option value="${version.id}">${sw.name} v${version.version_number}</option>`;
                        });
                    } catch (error) {
                        console.error(`Failed to load versions for ${sw.name}:`, error);
                    }
                }
            }

            function showCreateSoftwareForm() {
                document.getElementById('create-software-form').style.display = 'block';
            }

            function hideCreateSoftwareForm() {
                document.getElementById('create-software-form').style.display = 'none';
                // Clear form
                document.getElementById('software-name').value = '';
                document.getElementById('software-description').value = '';
                document.getElementById('software-vendor').value = '';
                document.getElementById('software-category').value = '';
                document.getElementById('software-platform').value = '';
                document.getElementById('software-repository').value = '';
            }

            async function createSoftware() {
                const softwareData = {
                    name: document.getElementById('software-name').value,
                    description: document.getElementById('software-description').value,
                    vendor: document.getElementById('software-vendor').value,
                    category: document.getElementById('software-category').value,
                    platform: document.getElementById('software-platform').value,
                    repository_url: document.getElementById('software-repository').value,
                    is_active: true
                };

                if (!softwareData.name || !softwareData.category) {
                    alert('Podaj nazwę i kategorię oprogramowania');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software', {
                        method: 'POST',
                        body: JSON.stringify(softwareData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Oprogramowanie '${result.name}' utworzone pomyślnie
                            </div>
                        `;
                        hideCreateSoftwareForm();
                        loadSoftware();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd tworzenia oprogramowania: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd: ${error.message}
                        </div>
                    `;
                }
            }

            async function viewSoftware(softwareId) {
                const software = allSoftware.find(s => s.id === softwareId);
                if (!software) return;

                document.getElementById('result').innerHTML = `
                    <div class="result" style="background: #e8f5e9; border-color: #4caf50;">
                        <h4>📦 ${software.name}</h4>
                        <p><strong>Kategoria:</strong> <span class="category-badge">${software.category}</span></p>
                        <p><strong>Vendor:</strong> ${software.vendor || 'Brak'}</p>
                        <p><strong>Platforma:</strong> ${software.platform || 'Brak'}</p>
                        <p><strong>Opis:</strong> ${software.description || 'Brak opisu'}</p>
                        <p><strong>Repository:</strong> ${software.repository_url ? `<a href="${software.repository_url}" target="_blank">${software.repository_url}</a>` : 'Brak'}</p>
                        <p><strong>Status:</strong> ${software.is_active ? '<span class="status-badge status-installed">Aktywne</span>' : '<span class="status-badge status-failed">Nieaktywne</span>'}</p>
                        <p><strong>Utworzono:</strong> ${new Date(software.created_at).toLocaleDateString()}</p>
                    </div>
                `;
            }

            async function deleteSoftware(softwareId) {
                if (!confirm('Czy na pewno chcesz usunąć to oprogramowanie? Spowoduje to również usunięcie wszystkich wersji i instalacji.')) {
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${softwareId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ ${result.message || 'Oprogramowanie zostało usunięte'}
                            </div>
                        `;
                        loadSoftware();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd usuwania oprogramowania: ${error.message}
                        </div>
                    `;
                }
            }

            async function viewVersion(versionId) {
                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${currentSoftwareId}/versions`);
                    const versions = await response.json();
                    const version = versions.find(v => v.id === versionId);
                    
                    if (!version) {
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Nie znaleziono wersji
                            </div>
                        `;
                        return;
                    }

                    const badges = [];
                    if (version.is_stable) badges.push('<span class="status-badge status-installed">Stabilna</span>');
                    if (version.is_beta) badges.push('<span class="status-badge" style="background: #f39c12;">Beta</span>');
                    if (version.requires_reboot) badges.push('<span class="status-badge" style="background: #e67e22;">Wymaga restartu</span>');

                    document.getElementById('result').innerHTML = `
                        <div class="result" style="background: #e3f2fd; border-color: #2196f3;">
                            <h4>🔢 Wersja ${version.version_number}</h4>
                            <p><strong>Typ:</strong> ${badges.join(' ')}</p>
                            <p><strong>Notatki wydania:</strong> ${version.release_notes || 'Brak notatek'}</p>
                            <p><strong>Ścieżka pobierania:</strong> ${version.download_url || 'Brak'}</p>
                            <p><strong>Rozmiar pliku:</strong> ${version.file_size || 'Nieznany'}</p>
                            <p><strong>Checksum:</strong> ${version.checksum || 'Brak'}</p>
                            <p><strong>Instalacje:</strong> ${version.installations_count}</p>
                            <p><strong>Utworzono:</strong> ${new Date(version.created_at).toLocaleDateString()}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania wersji: ${error.message}
                        </div>
                    `;
                }
            }

            async function loadVersions() {
                const softwareId = document.getElementById('version-software-select').value;
                if (!softwareId) {
                    document.getElementById('versions-list').innerHTML = '<p>Wybierz oprogramowanie aby zobaczyć wersje...</p>';
                    document.getElementById('add-version-btn').style.display = 'none';
                    return;
                }

                currentSoftwareId = softwareId;
                document.getElementById('add-version-btn').style.display = 'inline';

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${softwareId}/versions`);
                    const versions = await response.json();
                    
                    displayVersions(versions);
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd ładowania wersji: ${error.message}
                        </div>
                    `;
                }
            }

            function displayVersions(versions) {
                const container = document.getElementById('versions-list');
                if (versions.length === 0) {
                    container.innerHTML = '<p>Brak wersji dla tego oprogramowania.</p>';
                    return;
                }

                let html = '<table class="data-table"><thead><tr>';
                html += '<th>Wersja</th><th>Typ</th><th>Instalacje</th><th>Utworzono</th><th>Akcje</th></tr></thead><tbody>';
                
                versions.forEach(version => {
                    const badges = [];
                    if (version.is_stable) badges.push('<span class="status-badge status-installed">Stabilna</span>');
                    if (version.is_beta) badges.push('<span class="status-badge" style="background: #f39c12;">Beta</span>');
                    if (version.requires_reboot) badges.push('<span class="status-badge" style="background: #e67e22;">Restart</span>');

                    html += `<tr>
                        <td><strong>${version.version_number}</strong><br><small>${version.release_notes || 'Brak notatek'}</small></td>
                        <td>${badges.join(' ')}</td>
                        <td>${version.installations_count}</td>
                        <td>${new Date(version.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="viewVersion(${version.id})" style="font-size: 10px; padding: 5px;">Zobacz</button>
                        </td>
                    </tr>`;
                });
                
                html += '</tbody></table>';
                container.innerHTML = html;
            }

            function showCreateVersionForm() {
                if (!currentSoftwareId) {
                    alert('Wybierz oprogramowanie');
                    return;
                }
                document.getElementById('create-version-form').style.display = 'block';
            }

            function hideCreateVersionForm() {
                document.getElementById('create-version-form').style.display = 'none';
                // Clear form
                document.getElementById('version-number').value = '';
                document.getElementById('version-release-notes').value = '';
                document.getElementById('version-download-url').value = '';
                document.getElementById('version-stable').checked = true;
                document.getElementById('version-beta').checked = false;
                document.getElementById('version-reboot').checked = false;
            }

            async function createVersion() {
                if (!currentSoftwareId) {
                    alert('Wybierz oprogramowanie');
                    return;
                }

                const versionData = {
                    software_id: currentSoftwareId,
                    version_number: document.getElementById('version-number').value,
                    release_notes: document.getElementById('version-release-notes').value,
                    download_url: document.getElementById('version-download-url').value,
                    is_stable: document.getElementById('version-stable').checked,
                    is_beta: document.getElementById('version-beta').checked,
                    requires_reboot: document.getElementById('version-reboot').checked
                };

                if (!versionData.version_number) {
                    alert('Podaj numer wersji');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${currentSoftwareId}/versions`, {
                        method: 'POST',
                        body: JSON.stringify(versionData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Wersja '${result.version_number}' utworzona pomyślnie
                            </div>
                        `;
                        hideCreateVersionForm();
                        loadVersions();
                        loadSoftware(); // Refresh software list to update version counts
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd tworzenia wersji: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd: ${error.message}
                        </div>
                    `;
                }
            }

            async function loadInstallations() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations');
                    
                    if (response.status === 401 || response.status === 403) {
                        document.getElementById('installations-list').innerHTML = `
                            <div style="color: #e74c3c; padding: 10px;">
                            ❌ Brak autoryzacji. Zaloguj się jako Maker aby zobaczyć instalacje.
                            </div>
                        `;
                        return;
                    }

                    const installations = await response.json();
                    displayInstallations(installations);
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Błąd ładowania instalacji:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            function displayInstallations(installations) {
                const container = document.getElementById('installations-list');
                if (installations.length === 0) {
                    container.innerHTML = '<p>Brak historii instalacji.</p>';
                    return;
                }

                let html = '<table class="data-table"><thead><tr>';
                html += '<th>Urządzenie</th><th>Oprogramowanie</th><th>Akcja</th><th>Status</th><th>Data</th></tr></thead><tbody>';
                
                installations.forEach(installation => {
                    const statusClass = installation.status === 'completed' ? 'status-installed' :
                                       installation.status === 'pending' ? 'status-pending' : 'status-failed';

                    html += `<tr>
                        <td>${installation.device_number}</td>
                        <td><strong>${installation.software_name}</strong><br><small>v${installation.version_number}</small></td>
                        <td>${installation.action}</td>
                        <td><span class="status-badge ${statusClass}">${installation.status}</span></td>
                        <td>${new Date(installation.started_at).toLocaleString()}</td>
                    </tr>`;
                });
                
                html += '</tbody></table>';
                container.innerHTML = html;
            }

            function showInstallationForm() {
                document.getElementById('installation-form').style.display = 'block';
            }

            function hideInstallationForm() {
                document.getElementById('installation-form').style.display = 'none';
                document.getElementById('installation-device').value = '';
                document.getElementById('installation-version').value = '';
                document.getElementById('installation-action').value = 'install';
                document.getElementById('installation-notes').value = '';
            }

            async function createInstallation() {
                const installationData = {
                    device_id: parseInt(document.getElementById('installation-device').value),
                    version_id: parseInt(document.getElementById('installation-version').value),
                    action: document.getElementById('installation-action').value,
                    notes: document.getElementById('installation-notes').value
                };

                if (!installationData.device_id || !installationData.version_id || !installationData.action) {
                    alert('Wypełnij wszystkie wymagane pola');
                    return;
                }

                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations', {
                        method: 'POST',
                        body: JSON.stringify(installationData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Instalacja rozpoczęta pomyślnie na urządzeniu ${result.device_number}
                            Oprogramowanie: ${result.software_name} v${result.version_number}
                            </div>
                        `;
                        hideInstallationForm();
                        loadInstallations();
                        loadDashboard();
                    } else {
                        const error = await response.json();
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ❌ Błąd instalacji: ${error.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Błąd: ${error.message}
                        </div>
                    `;
                }
            }

            // API Testing functions
            async function testSoftwareAPI() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Software API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Software API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            async function testVersionsAPI() {
                if (softwareList.length > 0) {
                    const softwareId = softwareList[0].id;
                    try {
                        const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${softwareId}/versions`);
                        const data = await response.json();
                        
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            <strong>Test Versions API Response:</strong>
                            Status: ${response.status}
                            ${JSON.stringify(data, null, 2)}
                            </div>
                        `;
                    } catch (error) {
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            <strong>Error testing Versions API:</strong>
                            ${error.message}
                            </div>
                        `;
                    }
                } else {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        ❌ Brak oprogramowania do testowania API wersji
                        </div>
                    `;
                }
            }

            async function testInstallationsAPI() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Installations API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Installations API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            async function testDashboard() {
                try {
                    const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
                    const data = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Test Dashboard API Response:</strong>
                        Status: ${response.status}
                        ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                        <strong>Error testing Dashboard API:</strong>
                        ${error.message}
                        </div>
                    `;
                }
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateAuthUI();
            });
        </script>
            </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)