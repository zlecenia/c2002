let authToken = null;

function getAuthToken() {
    if (!authToken) {
        authToken = localStorage.getItem('jwt_token');
    }
    return authToken;
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabName + '-tab').style.display = 'block';
    event.target.classList.add('active');
}

// Fleet Workshop Manager Functions

async function loadDashboard() {
    try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Musisz być zalogowany aby zobaczyć dashboard</div>';
            return;
        }

        const response = await fetch('/api/v1/fleet-workshop/dashboard', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            displayDashboard(data);
        } else {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd ładowania dashboard</div>';
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

function displayDashboard(data) {
    document.getElementById('result').innerHTML = `
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #1f2937;">📊 Dashboard Warsztat</h3>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="background: #ddd6fe; padding: 15px; border-radius: 6px; border-left: 4px solid #7c3aed;">
                            <h4 style="margin: 0 0 8px 0; color: #5b21b6;">🔧 Naprawy</h4>
                            <p style="margin: 2px 0; font-size: 14px;">Oczekujące: <strong>${data.repairs.pending}</strong></p>
                            <p style="margin: 2px 0; font-size: 14px;">W trakcie: <strong>${data.repairs.in_progress}</strong></p>
                            <p style="margin: 2px 0; font-size: 14px;">Ukończone: <strong>${data.repairs.completed}</strong></p>
                        </div>
                        
                        <div style="background: #dcfce7; padding: 15px; border-radius: 6px; border-left: 4px solid #16a34a;">
                            <h4 style="margin: 0 0 8px 0; color: #15803d;">⚙️ Konserwacja</h4>
                            <p style="margin: 2px 0; font-size: 14px;">Zaplanowane: <strong>${data.maintenance.scheduled}</strong></p>
                            <p style="margin: 2px 0; font-size: 14px;">Przeterminowane: <strong>${data.maintenance.overdue}</strong></p>
                            <p style="margin: 2px 0; font-size: 14px;">Ukończone: <strong>${data.maintenance.completed}</strong></p>
                        </div>
                        
                        <div style="background: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #d97706;">
                            <h4 style="margin: 0 0 8px 0; color: #92400e;">📦 Części</h4>
                            <p style="margin: 2px 0; font-size: 14px;">Wszystkie: <strong>${data.parts.total}</strong></p>
                            <p style="margin: 2px 0; font-size: 14px;">Niski stan: <strong>${data.parts.low_stock}</strong></p>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h4 style="color: #374151;">🔧 Ostatnie naprawy</h4>
                            ${data.repairs.recent.map(repair => `
                                <div style="background: white; padding: 10px; margin-bottom: 8px; border-radius: 4px; border-left: 3px solid #7c3aed;">
                                    <div style="font-weight: bold; font-size: 14px;">${repair.description}</div>
                                    <div style="font-size: 12px; color: #6b7280;">Urządzenie: ${repair.device_id} | Priorytet: ${repair.priority} | Status: ${repair.status}</div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div>
                            <h4 style="color: #374151;">⚙️ Ostatnie konserwacje</h4>
                            ${data.maintenance.recent.map(maintenance => `
                                <div style="background: white; padding: 10px; margin-bottom: 8px; border-radius: 4px; border-left: 3px solid #16a34a;">
                                    <div style="font-weight: bold; font-size: 14px;">${maintenance.title}</div>
                                    <div style="font-size: 12px; color: #6b7280;">Urządzenie: ${maintenance.device_id} | Status: ${maintenance.status}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
}

function addRepair() {
    document.getElementById('result').innerHTML = `
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #1f2937;">🔧 Dodaj nową naprawę</h3>
                    
                    <form onsubmit="submitRepair(event)" style="max-width: 500px;">
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">ID Urządzenia:</label>
                            <input type="number" id="repair-device-id" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Typ naprawy:</label>
                            <select id="repair-type" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                                <option value="">Wybierz typ</option>
                                <option value="corrective">Naprawa korygująca</option>
                                <option value="preventive">Naprawa zapobiegawcza</option>
                                <option value="upgrade">Modernizacja</option>
                            </select>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Priorytet:</label>
                            <select id="repair-priority" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                                <option value="low">Niski</option>
                                <option value="medium" selected>Średni</option>
                                <option value="high">Wysoki</option>
                                <option value="critical">Krytyczny</option>
                            </select>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Opis problemu:</label>
                            <textarea id="repair-description" required rows="3" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Opisz problem wymagający naprawy"></textarea>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Szczegóły problemu:</label>
                            <textarea id="repair-problem" rows="2" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Dodatkowe informacje o problemie"></textarea>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Planowana data:</label>
                            <input type="datetime-local" id="repair-scheduled" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Notatki:</label>
                            <textarea id="repair-notes" rows="2" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Dodatkowe notatki"></textarea>
                        </div>
                        
                        <button type="submit" style="background: #7c3aed; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Dodaj naprawę</button>
                        <button type="button" onclick="loadDashboard()" style="background: #6b7280; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Anuluj</button>
                    </form>
                </div>
            `;
}

function addMaintenance() {
    document.getElementById('result').innerHTML = `
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #1f2937;">⚙️ Dodaj konserwację</h3>
                    
                    <form onsubmit="submitMaintenance(event)" style="max-width: 500px;">
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">ID Urządzenia:</label>
                            <input type="number" id="maintenance-device-id" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Typ konserwacji:</label>
                            <select id="maintenance-type" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                                <option value="">Wybierz typ</option>
                                <option value="routine">Rutynowa</option>
                                <option value="scheduled">Planowa</option>
                                <option value="condition_based">Oparta na stanie</option>
                                <option value="predictive">Predykcyjna</option>
                            </select>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Tytuł:</label>
                            <input type="text" id="maintenance-title" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Krótki tytuł konserwacji">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Opis:</label>
                            <textarea id="maintenance-description" rows="3" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Opisz czynności konserwacyjne"></textarea>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Planowany czas (minuty):</label>
                            <input type="number" id="maintenance-duration" min="1" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="60">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Następna konserwacja:</label>
                            <input type="datetime-local" id="maintenance-next-due" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Harmonogram:</label>
                            <select id="maintenance-schedule" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                                <option value="">Brak harmonogramu</option>
                                <option value="daily">Codziennie</option>
                                <option value="weekly">Tygodniowo</option>
                                <option value="monthly">Miesięcznie</option>
                                <option value="quarterly">Kwartalnie</option>
                                <option value="yearly">Rocznie</option>
                            </select>
                        </div>
                        
                        <button type="submit" style="background: #16a34a; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Dodaj konserwację</button>
                        <button type="button" onclick="loadDashboard()" style="background: #6b7280; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Anuluj</button>
                    </form>
                </div>
            `;
}

function addPart() {
    document.getElementById('result').innerHTML = `
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #1f2937;">📦 Dodaj część</h3>
                    
                    <form onsubmit="submitPart(event)" style="max-width: 500px;">
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Numer części:</label>
                            <input type="text" id="part-number" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="np. MT-001-FLT">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Nazwa:</label>
                            <input type="text" id="part-name" required style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="np. Filtr powietrza">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Kategoria:</label>
                            <select id="part-category" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                                <option value="">Wybierz kategorię</option>
                                <option value="electronic">Elektronika</option>
                                <option value="mechanical">Mechanika</option>
                                <option value="consumable">Materiały eksploatacyjne</option>
                                <option value="tool">Narzędzia</option>
                            </select>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Opis:</label>
                            <textarea id="part-description" rows="3" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Opis części"></textarea>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Producent:</label>
                            <input type="text" id="part-manufacturer" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="np. Bosch">
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Dostawca:</label>
                            <input type="text" id="part-supplier" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="np. TechSupply Ltd">
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Cena (gr):</label>
                                <input type="number" id="part-price" min="0" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="2500">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Stan magazynowy:</label>
                                <input type="number" id="part-stock" min="0" value="0" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Min. stan:</label>
                                <input type="number" id="part-min-stock" min="0" value="0" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Lokalizacja:</label>
                                <input type="text" id="part-location" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Magazyn A-1-2">
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Notatki:</label>
                            <textarea id="part-notes" rows="2" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: white; color: black;" placeholder="Dodatkowe informacje"></textarea>
                        </div>
                        
                        <button type="submit" style="background: #d97706; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Dodaj część</button>
                        <button type="button" onclick="loadDashboard()" style="background: #6b7280; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Anuluj</button>
                    </form>
                </div>
            `;
}

// Submit functions
async function submitRepair(event) {
    event.preventDefault();

    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Musisz być zalogowany');
        return;
    }

    const repairData = {
        device_id: parseInt(document.getElementById('repair-device-id').value),
        repair_type: document.getElementById('repair-type').value,
        priority: document.getElementById('repair-priority').value,
        description: document.getElementById('repair-description').value,
        problem_description: document.getElementById('repair-problem').value || null,
        scheduled_date: document.getElementById('repair-scheduled').value || null,
        notes: document.getElementById('repair-notes').value || null
    };

    try {
        const response = await fetch('/api/v1/fleet-workshop/repairs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(repairData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #dcfce7; border-radius: 4px; color: #166534;">✅ Naprawa została dodana pomyślnie!</div>';
            setTimeout(loadDashboard, 2000);
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        console.error('Error creating repair:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

async function submitMaintenance(event) {
    event.preventDefault();

    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Musisz być zalogowany');
        return;
    }

    const maintenanceData = {
        device_id: parseInt(document.getElementById('maintenance-device-id').value),
        maintenance_type: document.getElementById('maintenance-type').value,
        title: document.getElementById('maintenance-title').value,
        description: document.getElementById('maintenance-description').value || null,
        estimated_duration: parseInt(document.getElementById('maintenance-duration').value) || null,
        next_due: document.getElementById('maintenance-next-due').value || null,
        schedule_type: document.getElementById('maintenance-schedule').value || null
    };

    try {
        const response = await fetch('/api/v1/fleet-workshop/maintenance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(maintenanceData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #dcfce7; border-radius: 4px; color: #166534;">✅ Konserwacja została dodana pomyślnie!</div>';
            setTimeout(loadDashboard, 2000);
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        console.error('Error creating maintenance:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

async function submitPart(event) {
    event.preventDefault();

    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Musisz być zalogowany');
        return;
    }

    const partData = {
        part_number: document.getElementById('part-number').value,
        name: document.getElementById('part-name').value,
        category: document.getElementById('part-category').value || null,
        description: document.getElementById('part-description').value || null,
        manufacturer: document.getElementById('part-manufacturer').value || null,
        supplier: document.getElementById('part-supplier').value || null,
        unit_price: parseInt(document.getElementById('part-price').value) || null,
        stock_quantity: parseInt(document.getElementById('part-stock').value) || 0,
        min_stock_level: parseInt(document.getElementById('part-min-stock').value) || 0,
        location: document.getElementById('part-location').value || null,
        notes: document.getElementById('part-notes').value || null
    };

    try {
        const response = await fetch('/api/v1/fleet-workshop/parts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(partData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #dcfce7; border-radius: 4px; color: #166534;">✅ Część została dodana pomyślnie!</div>';
            setTimeout(loadDashboard, 2000);
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        console.error('Error creating part:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

// Initialize dashboard on successful login
function updateAuthUI() {
    const token = localStorage.getItem('auth_token');
    if (token) {
        loadDashboard();
    } else {
        document.getElementById('result').innerHTML = '<div style="padding: 20px; text-align: center; color: #6b7280;">Zaloguj się aby zobaczyć panel warsztatowy</div>';
    }
}

// Load dashboard on page load if authenticated
document.addEventListener('DOMContentLoaded', updateAuthUI);

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
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('jwt_token', authToken);
            document.getElementById('auth-message').innerHTML = '<span style="color: #34d399;">✅ Zalogowano</span>';
            document.getElementById('login-username').style.display = 'none';
            document.getElementById('login-password').style.display = 'none';
            document.querySelector('button[onclick="login()"]').style.display = 'none';
            document.getElementById('logout-btn').style.display = 'block';
        } else {
            document.getElementById('auth-message').innerHTML = '<span style="color: #fc8181;">❌ Błąd logowania</span>';
        }
    } catch (error) {
        document.getElementById('auth-message').innerHTML = '<span style="color: #fc8181;">❌ Błąd: ' + error.message + '</span>';
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('jwt_token');
    document.getElementById('auth-message').innerHTML = '<span style="color: #a0aec0;">❌ Wylogowano</span>';
    document.getElementById('login-username').style.display = 'block';
    document.getElementById('login-password').style.display = 'block';
    document.querySelector('button[onclick="login()"]').style.display = 'block';
    document.getElementById('logout-btn').style.display = 'none';
}

// Device Management Functions
let devices = [];
let customers = [];
let currentEditingDevice = null;
let currentEditingCustomer = null;

async function loadDevices() {
    try {
        const token = getAuthToken();
        if (!token) {
            document.querySelector('#devices-table tbody').innerHTML =
                '<tr><td colspan="5">Musisz być zalogowany aby zobaczyć urządzenia</td></tr>';
            return;
        }

        const response = await fetch('/api/v1/fleet-data/devices', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            devices = await response.json();
            displayDevices();
        } else {
            document.querySelector('#devices-table tbody').innerHTML =
                '<tr><td colspan="5">Błąd ładowania urządzeń</td></tr>';
        }
    } catch (error) {
        console.error('Error loading devices:', error);
        document.querySelector('#devices-table tbody').innerHTML =
            '<tr><td colspan="5">Błąd połączenia z serwerem</td></tr>';
    }
}

function displayDevices() {
    const tbody = document.querySelector('#devices-table tbody');
    if (!devices || devices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">Brak urządzeń do wyświetlenia</td></tr>';
        return;
    }

    tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>${device.device_number || 'N/A'}</td>
                    <td>${device.device_type || 'N/A'}</td>
                    <td><span class="status-badge status-${device.status || 'inactive'}">${device.status || 'N/A'}</span></td>
                    <td>${device.customer_name || 'Brak przypisania'}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editDevice(${device.id})">Edytuj</button>
                        <button class="btn" style="background: #e74c3c;" onclick="deleteDevice(${device.id})">Usuń</button>
                    </td>
                </tr>
            `).join('');
}

async function loadCustomers() {
    try {
        const token = getAuthToken();
        if (!token) {
            document.querySelector('#customers-table tbody').innerHTML =
                '<tr><td colspan="4">Musisz być zalogowany aby zobaczyć klientów</td></tr>';
            return;
        }

        const response = await fetch('/api/v1/fleet-data/customers', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            customers = await response.json();
            displayCustomers();
            loadCustomersForSelect();
        } else {
            document.querySelector('#customers-table tbody').innerHTML =
                '<tr><td colspan="4">Błąd ładowania klientów</td></tr>';
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        document.querySelector('#customers-table tbody').innerHTML =
            '<tr><td colspan="4">Błąd połączenia z serwerem</td></tr>';
    }
}

function displayCustomers() {
    const tbody = document.querySelector('#customers-table tbody');
    if (!customers || customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">Brak klientów do wyświetlenia</td></tr>';
        return;
    }

    tbody.innerHTML = customers.map(customer => `
                <tr>
                    <td>${customer.name}</td>
                    <td>${customer.contact_info ? JSON.stringify(customer.contact_info).substring(0, 50) + '...' : 'Brak'}</td>
                    <td>${customer.created_at ? new Date(customer.created_at).toLocaleDateString() : 'N/A'}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editCustomer(${customer.id})">Edytuj</button>
                        <button class="btn" style="background: #e74c3c;" onclick="deleteCustomer(${customer.id})">Usuń</button>
                    </td>
                </tr>
            `).join('');
}

function loadCustomersForSelect() {
    const select = document.getElementById('device-customer');
    if (!select) return;

    select.innerHTML = '<option value="">Brak przypisania</option>';
    customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        option.textContent = customer.name;
        select.appendChild(option);
    });
}

function showAddDeviceForm() {
    document.getElementById('add-device-form').style.display = 'block';
    document.getElementById('add-customer-form').style.display = 'none';
    document.getElementById('device-submit-btn').textContent = 'Dodaj urządzenie';
    document.getElementById('form-title').textContent = 'Dodaj urządzenie';
    currentEditingDevice = null;
    clearDeviceForm();
}

function hideDeviceForm() {
    document.getElementById('add-device-form').style.display = 'none';
    clearDeviceForm();
}

function showAddCustomerForm() {
    document.getElementById('add-customer-form').style.display = 'block';
    document.getElementById('add-device-form').style.display = 'none';
    document.getElementById('customer-submit-btn').textContent = 'Dodaj klienta';
    document.getElementById('form-title').textContent = 'Dodaj klienta';
    currentEditingCustomer = null;
    clearCustomerForm();
}

function hideCustomerForm() {
    document.getElementById('add-customer-form').style.display = 'none';
    clearCustomerForm();
}

function clearDeviceForm() {
    document.getElementById('device-number').value = '';
    document.getElementById('device-type').value = '';
    document.getElementById('kind-of-device').value = '';
    document.getElementById('serial-number').value = '';
    document.getElementById('device-status').value = 'active';
    document.getElementById('device-customer').value = '';
}

function clearCustomerForm() {
    document.getElementById('customer-name').value = '';
    document.getElementById('customer-json-editor').innerHTML = '';
}

async function saveDevice() {
    try {
        const token = getAuthToken();
        if (!token) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Musisz być zalogowany</div>';
            return;
        }

        const deviceData = {
            device_number: document.getElementById('device-number').value,
            device_type: document.getElementById('device-type').value,
            kind_of_device: document.getElementById('kind-of-device').value,
            serial_number: document.getElementById('serial-number').value,
            status: document.getElementById('device-status').value,
            customer_id: document.getElementById('device-customer').value || null
        };

        const url = currentEditingDevice
            ? `/api/v1/fleet-data/devices/${currentEditingDevice}`
            : '/api/v1/fleet-data/devices';

        const method = currentEditingDevice ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #d4edda; border-radius: 4px; color: #155724;">Urządzenie zostało zapisane</div>';
            hideDeviceForm();
            loadDevices();
        } else {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd zapisywania urządzenia</div>';
        }
    } catch (error) {
        console.error('Error saving device:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

async function saveCustomer() {
    try {
        const token = getAuthToken();
        if (!token) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Musisz być zalogowany</div>';
            return;
        }

        const customerData = {
            name: document.getElementById('customer-name').value,
            contact_info: getCustomerContactInfo()
        };

        const url = currentEditingCustomer
            ? `/api/v1/fleet-data/customers/${currentEditingCustomer}`
            : '/api/v1/fleet-data/customers';

        const method = currentEditingCustomer ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(customerData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #d4edda; border-radius: 4px; color: #155724;">Klient został zapisany</div>';
            hideCustomerForm();
            loadCustomers();
        } else {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd zapisywania klienta</div>';
        }
    } catch (error) {
        console.error('Error saving customer:', error);
        document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd połączenia z serwerem</div>';
    }
}

function getCustomerContactInfo() {
    // Simple implementation - returns empty object for now
    // TODO: Implement JSON editor functionality
    return {};
}

function clearFilters() {
    document.getElementById('device-type-filter').value = '';
    document.getElementById('device-status-filter').value = '';
    loadDevices();
}

async function editDevice(deviceId) {
    const device = devices.find(d => d.id === deviceId);
    if (!device) return;

    currentEditingDevice = deviceId;
    document.getElementById('device-number').value = device.device_number || '';
    document.getElementById('device-type').value = device.device_type || '';
    document.getElementById('kind-of-device').value = device.kind_of_device || '';
    document.getElementById('serial-number').value = device.serial_number || '';
    document.getElementById('device-status').value = device.status || 'active';
    document.getElementById('device-customer').value = device.customer_id || '';

    document.getElementById('device-submit-btn').textContent = 'Aktualizuj urządzenie';
    document.getElementById('form-title').textContent = 'Edytuj urządzenie';
    document.getElementById('add-device-form').style.display = 'block';
}

async function editCustomer(customerId) {
    const customer = customers.find(c => c.id === customerId);
    if (!customer) return;

    currentEditingCustomer = customerId;
    document.getElementById('customer-name').value = customer.name || '';

    document.getElementById('customer-submit-btn').textContent = 'Aktualizuj klienta';
    document.getElementById('form-title').textContent = 'Edytuj klienta';
    document.getElementById('add-customer-form').style.display = 'block';
}

async function deleteDevice(deviceId) {
    if (!confirm('Czy na pewno chcesz usunąć to urządzenie?')) return;

    try {
        const token = getAuthToken();
        const response = await fetch(`/api/v1/fleet-data/devices/${deviceId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #d4edda; border-radius: 4px; color: #155724;">Urządzenie zostało usunięte</div>';
            loadDevices();
        } else {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd usuwania urządzenia</div>';
        }
    } catch (error) {
        console.error('Error deleting device:', error);
    }
}

async function deleteCustomer(customerId) {
    if (!confirm('Czy na pewno chcesz usunąć tego klienta?')) return;

    try {
        const token = getAuthToken();
        const response = await fetch(`/api/v1/fleet-data/customers/${customerId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #d4edda; border-radius: 4px; color: #155724;">Klient został usunięty</div>';
            loadCustomers();
        } else {
            document.getElementById('result').innerHTML = '<div style="padding: 15px; background: #fee2e2; border-radius: 4px; color: #dc2626;">Błąd usuwania klienta</div>';
        }
    } catch (error) {
        console.error('Error deleting customer:', error);
    }
}

// Initialize data on page load
document.addEventListener('DOMContentLoaded', function() {
    if (getAuthToken()) {
        loadDevices();
        loadCustomers();
    }
});