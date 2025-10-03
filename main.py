from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import get_db, engine
from backend.models.models import (
    Base,
    User,
    Device,
    Customer,
    TestScenario,
    TestStep,
    Software,
    SoftwareVersion,
    DeviceSoftware,
    Configuration,
    TestReport,
    SystemLog,
    Repair,
    Maintenance,
    Part,
)
from backend.api.auth_router import router as auth_router
from backend.api.users_router import router as users_router
from backend.auth.auth import get_password_hash, generate_qr_code
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.project_name, openapi_url=f"{settings.api_v1_str}/openapi.json")

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

# Import and include fleet workshop router
from backend.api.fleet_workshop_router import router as fleet_workshop_router

app.include_router(fleet_workshop_router, prefix=settings.api_v1_str)

# Import and include module routes
from modules.routes import include_module_routes

include_module_routes(app)
# Mount static files (check directory exists first)
import os

if os.path.exists("static") and os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Backward-compatibility mounts for common static assets used by docs/tests
    if os.path.exists("static/common") and os.path.isdir("static/common"):
        # Legacy direct path
        app.mount("/common/static", StaticFiles(directory="static/common"), name="legacy-common-static")
        # Compatibility for tests expecting /modules/common/static/...
        app.mount(
            "/modules/common/static",
            StaticFiles(directory="static/common"),
            name="compat-modules-common-static",
        )

# FSM module compatibility mounts for legacy frontend paths
if os.path.exists("modules/fsm/templates") and os.path.isdir("modules/fsm/templates"):
    # Legacy direct path
    app.mount("/fsm/frontend", StaticFiles(directory="modules/fsm/templates"), name="legacy-fsm-frontend")
    # Compatibility for tests expecting /modules/fsm/frontend/...
    app.mount(
        "/modules/fsm/frontend",
        StaticFiles(directory="modules/fsm/templates"),
        name="compat-modules-fsm-frontend",
    )

# Mount modules static files (broad catch-all) placed after specific mounts
if os.path.exists("modules") and os.path.isdir("modules"):
    app.mount("/modules", StaticFiles(directory="modules"), name="modules")


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
                is_active=True,
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
                is_active=True,
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
                is_active=True,
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
                is_active=True,
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
                is_active=True,
            )
            db.add(maker_user)

        db.flush()
        counts["users"] = 5

        # 2. CREATE CUSTOMERS
        existing_customers = db.query(Customer).count()
        if existing_customers == 0:
            customers_data = [
                {
                    "name": "Szpital Wojewódzki w Warszawie",
                    "contact_info": {
                        "email": "kontakt@szpital-warszawa.pl",
                        "phone": "+48 22 123 4567",
                        "address": "ul. Szpitalna 1, 00-001 Warszawa",
                    },
                },
                {
                    "name": "Przychodnia Medyczna Poznań",
                    "contact_info": {
                        "email": "recepcja@medyczna-poznan.pl",
                        "phone": "+48 61 234 5678",
                    },
                },
                {
                    "name": "Centrum Zdrowia Kraków",
                    "contact_info": {"email": "info@centrum-krakow.pl", "phone": "+48 12 345 6789"},
                },
                {
                    "name": "Klinika Prywatna Gdańsk",
                    "contact_info": {
                        "email": "kontakt@klinika-gdansk.pl",
                        "phone": "+48 58 456 7890",
                    },
                },
                {
                    "name": "Laboratorium Diagnostyczne Wrocław",
                    "contact_info": {
                        "email": "lab@diagnostyka-wroclaw.pl",
                        "phone": "+48 71 567 8901",
                    },
                },
            ]
            for cust_data in customers_data:
                customer = Customer(**cust_data)
                db.add(customer)
            db.flush()
            counts["customers"] = len(customers_data)

        # 3. CREATE DEVICES
        customers = db.query(Customer).all()
        existing_devices = db.query(Device).count()
        if existing_devices == 0 and customers:
            devices_data = [
                {
                    "device_number": "MT-001",
                    "device_type": "mask_tester",
                    "kind_of_device": "Medical Test Device",
                    "serial_number": "SN2024001",
                    "status": "active",
                    "customer_id": customers[0].id,
                    "configuration": {"test_mode": "automatic", "pressure_range": "0-50 mbar"},
                },
                {
                    "device_number": "MT-002",
                    "device_type": "mask_tester",
                    "kind_of_device": "Medical Test Device",
                    "serial_number": "SN2024002",
                    "status": "active",
                    "customer_id": customers[1].id,
                    "configuration": {"test_mode": "manual", "pressure_range": "0-50 mbar"},
                },
                {
                    "device_number": "PS-001",
                    "device_type": "pressure_sensor",
                    "kind_of_device": "Sensor Device",
                    "serial_number": "SN2024003",
                    "status": "active",
                    "customer_id": customers[2].id,
                    "configuration": {"sensitivity": "high", "calibration_date": "2024-01-15"},
                },
                {
                    "device_number": "FM-001",
                    "device_type": "flow_meter",
                    "kind_of_device": "Flow Measurement",
                    "serial_number": "SN2024004",
                    "status": "maintenance",
                    "customer_id": customers[3].id,
                    "configuration": {"flow_range": "0-100 L/min"},
                },
                {
                    "device_number": "MT-003",
                    "device_type": "mask_tester",
                    "kind_of_device": "Medical Test Device",
                    "serial_number": "SN2024005",
                    "status": "active",
                    "customer_id": customers[4].id,
                    "configuration": {"test_mode": "automatic", "pressure_range": "0-50 mbar"},
                },
            ]
            for dev_data in devices_data:
                device = Device(**dev_data)
                db.add(device)
            db.flush()
            counts["devices"] = len(devices_data)

        # 4. CREATE TEST SCENARIOS WITH STEPS
        existing_scenarios = (
            db.query(TestScenario).filter(TestScenario.created_by == admin_user.id).count()
        )
        if existing_scenarios < 3:
            scenarios_data = [
                {
                    "name": "Test Szczelności Maski Standardowy",
                    "description": "Kompletny test szczelności maski z pomiarem ciśnienia",
                    "device_type": "mask_tester",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "standard", "duration": "300s", "pressure": "30 mbar"},
                    "steps": [
                        {
                            "step_order": 1,
                            "step_name": "Przygotowanie urządzenia",
                            "description": "Sprawdzenie połączeń i kalibracja",
                        },
                        {
                            "step_order": 2,
                            "step_name": "Założenie maski",
                            "description": "Poprawne umieszczenie maski na manekinie",
                        },
                        {
                            "step_order": 3,
                            "step_name": "Test ciśnienia",
                            "description": "Pomiar szczelności przy 30 mbar",
                            "parameters": {"pressure": 30},
                        },
                        {
                            "step_order": 4,
                            "step_name": "Raport końcowy",
                            "description": "Generowanie raportu z wynikami testu",
                        },
                    ],
                },
                {
                    "name": "Kalibracja Czujnika Ciśnienia",
                    "description": "Procedura kalibracji czujników ciśnienia",
                    "device_type": "pressure_sensor",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "calibration", "points": 5},
                    "steps": [
                        {
                            "step_order": 1,
                            "step_name": "Reset urządzenia",
                            "description": "Przywrócenie ustawień fabrycznych",
                            "auto_test": True,
                        },
                        {
                            "step_order": 2,
                            "step_name": "Pomiar punktu zerowego",
                            "description": "Kalibracja przy ciśnieniu atmosferycznym",
                        },
                        {
                            "step_order": 3,
                            "step_name": "Pomiar punktów referencyjnych",
                            "description": "5 punktów kalibracyjnych",
                            "parameters": {"points": [10, 20, 30, 40, 50]},
                        },
                    ],
                },
                {
                    "name": "Test Przepływu Szybki",
                    "description": "Szybki test przepływomierza",
                    "device_type": "flow_meter",
                    "created_by": admin_user.id,
                    "test_flow": {"mode": "quick", "duration": "60s"},
                    "steps": [
                        {
                            "step_order": 1,
                            "step_name": "Uruchomienie przepływu",
                            "description": "Start pomiaru przepływu",
                        },
                        {
                            "step_order": 2,
                            "step_name": "Odczyt wartości",
                            "description": "Pomiar w czasie rzeczywistym",
                            "auto_test": True,
                        },
                    ],
                },
            ]

            for scen_data in scenarios_data:
                steps_data = scen_data.pop("steps")
                scenario = TestScenario(**scen_data)
                db.add(scenario)
                db.flush()

                for step_data in steps_data:
                    step = TestStep(scenario_id=scenario.id, **step_data)
                    db.add(step)

            db.flush()
            counts["scenarios"] = len(scenarios_data)

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
                        {
                            "version_number": "1.0.0",
                            "release_notes": "Pierwsza wersja stabilna",
                            "is_stable": True,
                            "file_path": "/firmware/masktester_v1.0.0.bin",
                        },
                        {
                            "version_number": "1.1.0",
                            "release_notes": "Optymalizacja pomiarów ciśnienia",
                            "is_stable": True,
                            "file_path": "/firmware/masktester_v1.1.0.bin",
                        },
                        {
                            "version_number": "1.2.0-beta",
                            "release_notes": "Nowy interfejs użytkownika (beta)",
                            "is_stable": False,
                            "file_path": "/firmware/masktester_v1.2.0-beta.bin",
                        },
                    ],
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
                        {
                            "version_number": "2.0.1",
                            "release_notes": "Poprawki stabilności",
                            "is_stable": True,
                            "file_path": "/drivers/pressure_sensor_v2.0.1.drv",
                        }
                    ],
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
                        {
                            "version_number": "3.1.0",
                            "release_notes": "Automatyczna kalibracja wielopunktowa",
                            "is_stable": True,
                            "file_path": "/tools/flowmeter_cal_v3.1.0.exe",
                        }
                    ],
                },
            ]

            for soft_data in software_data:
                versions_data = soft_data.pop("versions")
                software = Software(**soft_data)
                db.add(software)
                db.flush()

                for ver_data in versions_data:
                    version = SoftwareVersion(software_id=software.id, **ver_data)
                    db.add(version)

            db.flush()
            counts["software"] = len(software_data)

        # 6. CREATE SYSTEM CONFIGURATIONS
        existing_configs = db.query(Configuration).count()
        if existing_configs == 0:
            configs_data = [
                {
                    "config_key": "cpp_test_timeout",
                    "config_value": {"value": 300, "unit": "seconds"},
                    "component": "CPP",
                    "updated_by": configurator_user.id,
                },
                {
                    "config_key": "cm_max_scenarios",
                    "config_value": {"value": 100},
                    "component": "CM",
                    "updated_by": configurator_user.id,
                },
                {
                    "config_key": "fdm_backup_interval",
                    "config_value": {"value": 24, "unit": "hours"},
                    "component": "FDM",
                    "updated_by": configurator_user.id,
                },
                {
                    "config_key": "fcm_auto_backup",
                    "config_value": {"enabled": True, "retention_days": 30},
                    "component": "FCM",
                    "updated_by": configurator_user.id,
                },
                {
                    "config_key": "fsm_update_channel",
                    "config_value": {"channel": "stable", "auto_update": False},
                    "component": "FSM",
                    "updated_by": configurator_user.id,
                },
            ]

            for conf_data in configs_data:
                config = Configuration(**conf_data)
                db.add(config)

            db.flush()
            counts["configurations"] = len(configs_data)

        db.commit()

        return {"message": "✅ Testowe dane zostały pomyślnie dodane do bazy", "summary": counts}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd inicjalizacji danych: {str(e)}")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


# Public endpoints for Connect++ demo (no auth required)
@app.get("/api/v1/demo/users")
async def get_demo_users(db: Session = Depends(get_db)):
    users = db.query(User).limit(10).all()
    return {
        "users": [{"id": user.id, "username": user.username, "role": user.role} for user in users]
    }


@app.get("/api/v1/devices")
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return {
        "devices": [
            {
                "id": device.id,
                "device_number": device.device_number,
                "device_type": device.device_type,
            }
            for device in devices
        ]
    }


@app.get("/api/v1/customers")
async def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return {"customers": [{"id": customer.id, "name": customer.name} for customer in customers]}


@app.get("/api/v1/test-scenarios")
async def get_test_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(TestScenario).all()
    return {
        "scenarios": [
            {"id": scenario.id, "name": scenario.name, "device_type": scenario.device_type}
            for scenario in scenarios
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
