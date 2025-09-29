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

# Import and include scenarios router
from backend.api.scenarios_router import router as scenarios_router
app.include_router(scenarios_router, prefix=settings.api_v1_str)

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
                password_hash=get_password_hash("pass"),  # Shorter password
                email="admin@fleetmanagement.com",
                role="superuser",  # Change to superuser for Commands Manager
                qr_code=generate_qr_code(),
                is_active=True
            )
            db.add(admin_user)
        
        # Create sample operator
        operator_user = db.query(User).filter(User.username == "operator1").first()
        if not operator_user:
            operator_user = User(
                username="operator1",
                password_hash=get_password_hash("pass"),  # Shorter password
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
            "Commands_Manager": "/commands-manager", 
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
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #e74c3c; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
            .module-info { background: #ecf0f1; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
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
        </style>
    </head>
    <body>
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

            <div class="auth-section">
                <h4>🔐 Uwierzytelnianie</h4>
                <div id="auth-status">
                    <p>Zaloguj się jako Superuser aby uzyskać dostęp do funkcji:</p>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="login-username" placeholder="Username" style="padding: 5px;">
                        <input type="password" id="login-password" placeholder="Password" style="padding: 5px;">
                        <button class="btn" onclick="login()">Zaloguj</button>
                        <button class="btn btn-secondary" onclick="logout()" style="display: none;" id="logout-btn">Wyloguj</button>
                    </div>
                    <div id="auth-message" style="margin-top: 10px;"></div>
                </div>
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
                            <select id="device-type">
                                <option value="">Wybierz typ urządzenia</option>
                                <option value="mask_tester">Tester masek</option>
                                <option value="pressure_sensor">Czujnik ciśnienia</option>
                                <option value="flow_meter">Przepływomierz</option>
                            </select>
                        </div>
                        <button type="button" class="btn" onclick="createScenario()">Utwórz Scenariusz</button>
                    </form>

                    <h4>🔍 API Endpoints Test</h4>
                    <button class="btn btn-secondary" onclick="testScenariosAPI()">Test /scenarios</button>
                    <button class="btn btn-secondary" onclick="testAuth()">Test Auth</button>
                </div>
            </div>

            <div id="result" style="margin-top: 20px;"></div>
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
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: green;">✅ Zalogowany jako Superuser</span>';
                } else {
                    document.getElementById('auth-message').innerHTML = 
                        '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
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
                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setAuthToken(data.access_token);
                        document.getElementById('login-password').value = '';
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                            ✅ Zalogowano pomyślnie jako ${username}
                            </div>
                        `;
                        loadScenarios(); // Reload scenarios after login
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

            async function createScenario() {
                const name = document.getElementById('scenario-name').value;
                const description = document.getElementById('scenario-description').value;
                const deviceType = document.getElementById('device-type').value;

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
                        </div>
                    `;
                    
                    // Clear form
                    document.getElementById('scenario-form').reset();
                    
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
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)