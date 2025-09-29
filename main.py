from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import get_db, engine
from backend.models.models import Base, User, Device, Customer, TestScenario
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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize sample data endpoint
@app.post("/api/v1/init-data")
def initialize_sample_data(db: Session = Depends(get_db)):
    """Initialize database with sample data."""
    try:
        # Check if admin user exists, create if not
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin"),
                email="admin@fleetmanagement.com",
                role="admin",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(admin_user)
        
        # Create sample operator
        operator_user = db.query(User).filter(User.username == "operator1").first()
        if not operator_user:
            operator_user = User(
                username="operator1",
                password_hash=get_password_hash("test"),
                email="operator1@fleetmanagement.com",
                role="operator",
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(operator_user)
        
        db.commit()
        return {"message": "Sample data initialized successfully", "users_created": 2}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error initializing data: {str(e)}")

# Basic API endpoints
@app.get("/")
async def root():
    return {
        "message": "Fleet Management System API", 
        "version": "1.0.0",
        "modules": {
            "Connect++": "/connect-plus",
            "API_Documentation": "/docs",
            "Initialize_Sample_Data": "/api/v1/init-data (POST)"
        }
    }

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
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .module-info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .api-test { margin: 20px 0; }
            button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #2980b9; }
            .result { margin: 10px 0; padding: 10px; background: #d5edda; border-radius: 5px; border: 1px solid #c3e6cb; }
        </style>
    </head>
    <body>
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

        <script>
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
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)