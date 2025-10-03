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
    if (!getAuthToken()) {
        return; // Don't send request if not authenticated
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/dashboard');

        if (response.ok) {
            const data = await response.json();
            displayDashboard(data);
        } else if (response.status === 401) {
            console.log('Unauthorized - please login');
            clearAuthToken();
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
    if (!getAuthToken()) {
        document.getElementById('system-configs-list').innerHTML =
            '<p style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć konfigurację systemu...</p>';
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/system-configs');

        if (response.ok) {
            systemConfigs = await response.json();
            displaySystemConfigs(systemConfigs);
        } else if (response.status === 401 || response.status === 403) {
            document.getElementById('system-configs-list').innerHTML =
                '<p style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Configurator</p>';
            clearAuthToken();
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
    if (!getAuthToken()) {
        document.getElementById('device-configs-table').getElementsByTagName('tbody')[0].innerHTML =
            '<tr><td colspan="6" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć konfigurację urządzeń...</td></tr>';
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/device-configs');

        if (response.ok) {
            deviceConfigs = await response.json();
            displayDeviceConfigs(deviceConfigs);
        } else if (response.status === 401 || response.status === 403) {
            document.getElementById('device-configs-table').getElementsByTagName('tbody')[0].innerHTML =
                '<tr><td colspan="6" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Configurator</td></tr>';
            clearAuthToken();
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
    if (!getAuthToken()) {
        document.getElementById('test-scenarios-table').getElementsByTagName('tbody')[0].innerHTML =
            '<tr><td colspan="5" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć scenariusze testowe...</td></tr>';
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/test-scenario-configs');

        if (response.ok) {
            testScenarios = await response.json();
            displayTestScenarios(testScenarios);
        } else if (response.status === 401 || response.status === 403) {
            document.getElementById('test-scenarios-table').getElementsByTagName('tbody')[0].innerHTML =
                '<tr><td colspan="5" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Configurator</td></tr>';
            clearAuthToken();
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
    if (!getAuthToken()) {
        document.querySelector('#json-templates-table tbody').innerHTML =
            '<tr><td colspan="6" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć szablony JSON...</td></tr>';
        return;
    }

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
                '<tr><td colspan="6" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Configurator</td></tr>';
            clearAuthToken();
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