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

// ========== CONFIGURATION MANAGEMENT FUNCTIONS FROM FCM ==========
let systemConfigs = [];
let deviceConfigs = [];
let testScenarios = [];
let jsonTemplates = [];

// JSON Editors for forms
let configValueEditor = null;
let testParametersEditor = null;
let expectedResultsEditor = null;
let templateJsonEditor = null;

// Initialize template JSON editor
templateJsonEditor = new JSONTreeEditor('template-json-tree-editor');
templateJsonEditor.init({});

// Tab navigation and routing
function showTab(tabName) {
    // Hide all tabs
    const tabs = ['system-config-tab', 'device-config-tab', 'test-config-tab', 'json-templates-tab'];
    tabs.forEach(tab => {
        const element = document.getElementById(tab);
        if (element) element.style.display = 'none';
    });

    // Hide scenario sections
    const scenarioSections = document.querySelectorAll('.section');
    scenarioSections.forEach(section => {
        if (!tabs.some(tab => section.id === tab)) {
            section.style.display = 'none';
        }
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.style.display = 'block';

        // Load data for the tab
        switch(tabName) {
            case 'system-config':
                loadSystemConfigs();
                break;
            case 'device-config':
                loadDeviceConfigs();
                break;
            case 'test-config':
                loadTestScenarios();
                break;
            case 'json-templates':
                loadJsonTemplates();
                break;
        }
    }

    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update URL hash
    window.location.hash = tabName;
}

// Show all scenarios (default)
function showScenarios() {
    // Hide config tabs
    const tabs = ['system-config-tab', 'device-config-tab', 'test-config-tab', 'json-templates-tab'];
    tabs.forEach(tab => {
        const element = document.getElementById(tab);
        if (element) element.style.display = 'none';
    });

    // Show scenario sections
    const scenarioSections = document.querySelectorAll('.section');
    scenarioSections.forEach(section => {
        if (!tabs.some(tab => section.id === tab)) {
            section.style.display = 'block';
        }
    });

    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector('[onclick="showScenarios()"]').classList.add('active');

    window.location.hash = 'scenarios';
}

// Form management functions
function hideAllConfigForms() {
    document.getElementById('config-forms').style.display = 'none';
    document.getElementById('add-system-config-form').style.display = 'none';
    document.getElementById('add-test-scenario-form').style.display = 'none';
    document.getElementById('device-config-form').style.display = 'none';
    document.getElementById('add-template-form').style.display = 'none';
}

function showAddSystemConfigForm() {
    hideAllConfigForms();
    document.getElementById('config-forms').style.display = 'block';
    document.getElementById('add-system-config-form').style.display = 'block';
    document.getElementById('form-title').textContent = 'Dodaj konfigurację systemu';

    // Initialize JSON editor for config-value
    if (!configValueEditor) {
        configValueEditor = new JSONTreeEditor('config-value-editor');
        configValueEditor.init({
            setting: "example_value",
            enabled: true,
            timeout: 30
        });
    }
}

function showAddTestScenarioForm() {
    hideAllConfigForms();
    document.getElementById('config-forms').style.display = 'block';
    document.getElementById('add-test-scenario-form').style.display = 'block';
    document.getElementById('form-title').textContent = 'Dodaj scenariusz testowy';

    // Initialize JSON editors
    if (!testParametersEditor) {
        testParametersEditor = new JSONTreeEditor('test-parameters-editor');
        testParametersEditor.init({
            duration: 300,
            pressure: 50,
            tolerance: 2
        });
    }

    if (!expectedResultsEditor) {
        expectedResultsEditor = new JSONTreeEditor('expected-results-editor');
        expectedResultsEditor.init({
            pass_criteria: "value < 10",
            units: "Pa"
        });
    }
}

function showAddTemplateForm() {
    hideAllConfigForms();
    document.getElementById('config-forms').style.display = 'block';
    document.getElementById('add-template-form').style.display = 'block';
    document.getElementById('form-title').textContent = 'Dodaj szablon JSON';
    document.getElementById('template-form-title').textContent = 'Dodaj szablon JSON';
    document.getElementById('template-id').value = '';
}

// Load configuration data functions
async function loadSystemConfigs() {
    if (!getAuthToken()) {
        document.getElementById('system-configs-list').innerHTML =
            '<p>Zaloguj się aby zobaczyć konfigurację systemu...</p>';
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
                <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 4px; background: #f8f9fa;">
                    <h4>${config.config_name} (${config.config_type})</h4>
                    <p><strong>ID:</strong> ${config.config_id}</p>
                    <p><strong>Opis:</strong> ${config.description || 'Brak opisu'}</p>
                    <p><strong>Wartości:</strong> <pre style="background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 3px; font-size: 11px;">${JSON.stringify(config.config_value, null, 2)}</pre></p>
                    <button class="btn btn-secondary" onclick="editSystemConfig(${config.config_id})">Edytuj</button>
                    <button class="btn btn-danger" onclick="deleteSystemConfig(${config.config_id})">Usuń</button>
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
        tbody.innerHTML = '<tr><td colspan="6">Brak konfiguracji urządzeń.</td></tr>';
        return;
    }

    tbody.innerHTML = configs.map(config => `
                <tr>
                    <td>${config.device_id}</td>
                    <td>${config.device_number}</td>
                    <td>${config.device_type}</td>
                    <td>${config.status}</td>
                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                        ${config.configuration ? JSON.stringify(config.configuration).substring(0, 50) + '...' : 'Brak konfiguracji'}
                    </td>
                    <td>
                        <button class="btn btn-secondary" onclick="editDeviceConfig(${config.device_id})">Edytuj</button>
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
                        ${scenario.parameters ? JSON.stringify(scenario.parameters).substring(0, 50) + '...' : 'Brak parametrów'}
                    </td>
                    <td>
                        <button class="btn btn-secondary" onclick="editTestScenario(${scenario.scenario_id})">Edytuj</button>
                        <button class="btn btn-danger" onclick="deleteTestScenario(${scenario.scenario_id})">Usuń</button>
                    </td>
                </tr>
            `).join('');
}

async function loadJsonTemplates() {
    if (!getAuthToken()) {
        document.getElementById('json-templates-table').getElementsByTagName('tbody')[0].innerHTML =
            '<tr><td colspan="6" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć szablony...</td></tr>';
        return;
    }

    try {
        const typeFilter = document.getElementById('template-type-filter').value;
        const categoryFilter = document.getElementById('template-category-filter').value;

        let url = '/api/v1/fleet-config/json-templates';
        const params = new URLSearchParams();
        if (typeFilter) params.append('template_type', typeFilter);
        if (categoryFilter) params.append('category', categoryFilter);
        if (params.toString()) url += '?' + params.toString();

        const response = await makeAuthenticatedRequest(url);

        if (response.ok) {
            jsonTemplates = await response.json();
            displayJsonTemplates(jsonTemplates);
        } else if (response.status === 401 || response.status === 403) {
            document.getElementById('json-templates-table').getElementsByTagName('tbody')[0].innerHTML =
                '<tr><td colspan="6" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Configurator</td></tr>';
            clearAuthToken();
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd ładowania szablonów: ${error.message}
                    </div>
                `;
    }
}

function displayJsonTemplates(templates) {
    const tbody = document.getElementById('json-templates-table').getElementsByTagName('tbody')[0];
    if (templates.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">Brak szablonów JSON.</td></tr>';
        return;
    }

    tbody.innerHTML = templates.map(template => `
                <tr>
                    <td>${template.template_id}</td>
                    <td>${template.name}</td>
                    <td>${template.template_type}</td>
                    <td>${template.category || 'N/A'}</td>
                    <td>${template.description || 'Brak opisu'}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editTemplate(${template.template_id})">Edytuj</button>
                        <button class="btn btn-danger" onclick="deleteTemplate(${template.template_id})">Usuń</button>
                    </td>
                </tr>
            `).join('');
}

// CRUD functions - Complete implementation
async function createSystemConfig() {
    const name = document.getElementById('config-name').value;
    const type = document.getElementById('config-type').value;
    const description = document.getElementById('config-description').value;
    const configValue = configValueEditor ? configValueEditor.getJSON() : {};

    if (!name || !type) {
        alert('Wypełnij wymagane pola: nazwa i typ konfiguracji');
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/system-configs', {
            method: 'POST',
            body: JSON.stringify({
                config_name: name,
                config_type: type,
                config_value: configValue,
                description: description
            })
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Konfiguracja systemu została dodana pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadSystemConfigs();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd dodawania konfiguracji: ${error.message}
                    </div>
                `;
    }
}

async function createTestScenario() {
    const name = document.getElementById('test-scenario-name').value;
    const type = document.getElementById('test-type').value;
    const parameters = testParametersEditor ? testParametersEditor.getJSON() : {};
    const expectedResults = expectedResultsEditor ? expectedResultsEditor.getJSON() : {};

    if (!name || !type) {
        alert('Wypełnij wymagane pola: nazwa scenariusza i typ testu');
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-config/test-scenario-configs', {
            method: 'POST',
            body: JSON.stringify({
                scenario_name: name,
                test_type: type,
                parameters: parameters,
                expected_results: expectedResults
            })
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Scenariusz testowy został dodany pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadTestScenarios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd dodawania scenariusza: ${error.message}
                    </div>
                `;
    }
}

async function editSystemConfig(configId) {
    const config = systemConfigs.find(c => c.config_id === configId);
    if (!config) return;

    showAddSystemConfigForm();
    document.getElementById('form-title').textContent = `Edytuj konfigurację: ${config.config_name}`;
    document.getElementById('config-name').value = config.config_name;
    document.getElementById('config-type').value = config.config_type;
    document.getElementById('config-description').value = config.description || '';

    if (configValueEditor) {
        configValueEditor.setJSON(config.config_value);
    }

    // Change button text and function
    const button = document.querySelector('#system-config-form button[onclick="createSystemConfig()"]');
    if (button) {
        button.textContent = 'Aktualizuj konfigurację';
        button.setAttribute('onclick', `updateSystemConfig(${configId})`);
    }
}

async function updateSystemConfig(configId) {
    const name = document.getElementById('config-name').value;
    const type = document.getElementById('config-type').value;
    const description = document.getElementById('config-description').value;
    const configValue = configValueEditor ? configValueEditor.getJSON() : {};

    if (!name || !type) {
        alert('Wypełnij wymagane pola: nazwa i typ konfiguracji');
        return;
    }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/system-configs/${configId}`, {
            method: 'PUT',
            body: JSON.stringify({
                config_name: name,
                config_type: type,
                config_value: configValue,
                description: description
            })
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Konfiguracja systemu została zaktualizowana pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadSystemConfigs();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd aktualizacji konfiguracji: ${error.message}
                    </div>
                `;
    }
}

async function deleteSystemConfig(configId) {
    const config = systemConfigs.find(c => c.config_id === configId);
    if (!config) return;

    if (!confirm(`Czy na pewno chcesz usunąć konfigurację "${config.config_name}"?`)) {
        return;
    }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/system-configs/${configId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Konfiguracja systemu została usunięta pomyślnie
                        </div>
                    `;
            loadSystemConfigs();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd usuwania konfiguracji: ${error.message}
                    </div>
                `;
    }
}

function editDeviceConfig(deviceId) {
    const device = deviceConfigs.find(d => d.device_id === deviceId);
    if (!device) return;

    hideAllConfigForms();
    document.getElementById('config-forms').style.display = 'block';
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
                configuration: configuration
            })
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Konfiguracja urządzenia została zaktualizowana pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadDeviceConfigs();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd aktualizacji konfiguracji urządzenia: ${error.message}
                    </div>
                `;
    }
}

function hideSystemConfigForm() {
    hideAllConfigForms();
    // Reset button
    const button = document.querySelector('#system-config-form button[onclick*="ystemConfig"]');
    if (button) {
        button.textContent = 'Dodaj konfigurację';
        button.setAttribute('onclick', 'createSystemConfig()');
    }
}

function hideTestScenarioForm() {
    hideAllConfigForms();
}

function hideDeviceConfigForm() {
    hideAllConfigForms();
}

async function saveTemplate() {
    const templateId = document.getElementById('template-id').value;
    const name = document.getElementById('template-name').value;
    const type = document.getElementById('template-type').value;
    const category = document.getElementById('template-category').value;
    const description = document.getElementById('template-description').value;
    const defaultValues = templateJsonEditor ? templateJsonEditor.getJSON() : {};
    const schema = document.getElementById('template-schema').value;

    if (!name || !type) {
        alert('Wypełnij wymagane pola: nazwa i typ szablonu');
        return;
    }

    let schemaObj = null;
    if (schema.trim()) {
        try {
            schemaObj = JSON.parse(schema);
        } catch (e) {
            alert('Nieprawidłowy format JSON w schemacie');
            return;
        }
    }

    const templateData = {
        name: name,
        template_type: type,
        category: category || null,
        description: description || null,
        default_values: defaultValues,
        schema: schemaObj
    };

    try {
        const url = templateId ?
            `/api/v1/fleet-config/json-templates/${templateId}` :
            '/api/v1/fleet-config/json-templates';
        const method = templateId ? 'PUT' : 'POST';

        const response = await makeAuthenticatedRequest(url, {
            method: method,
            body: JSON.stringify(templateData)
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Szablon JSON został ${templateId ? 'zaktualizowany' : 'dodany'} pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadJsonTemplates();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd zapisu szablonu: ${error.message}
                    </div>
                `;
    }
}

function editTemplate(templateId) {
    const template = jsonTemplates.find(t => t.template_id === templateId);
    if (!template) return;

    showAddTemplateForm();
    document.getElementById('form-title').textContent = `Edytuj szablon: ${template.name}`;
    document.getElementById('template-form-title').textContent = 'Edytuj szablon JSON';
    document.getElementById('template-id').value = templateId;
    document.getElementById('template-name').value = template.name;
    document.getElementById('template-type').value = template.template_type;
    document.getElementById('template-category').value = template.category || '';
    document.getElementById('template-description').value = template.description || '';
    document.getElementById('template-schema').value = template.schema ? JSON.stringify(template.schema, null, 2) : '';

    if (templateJsonEditor && template.default_values) {
        templateJsonEditor.setJSON(template.default_values);
    }
}

async function deleteTemplate(templateId) {
    const template = jsonTemplates.find(t => t.template_id === templateId);
    if (!template) return;

    if (!confirm(`Czy na pewno chcesz usunąć szablon "${template.name}"?`)) {
        return;
    }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/json-templates/${templateId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Szablon JSON został usunięty pomyślnie
                        </div>
                    `;
            loadJsonTemplates();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd usuwania szablonu: ${error.message}
                    </div>
                `;
    }
}

function hideTemplateForm() {
    hideAllConfigForms();
    // Reset form
    document.getElementById('template-id').value = '';
    document.getElementById('json-template-form').reset();
    if (templateJsonEditor) {
        templateJsonEditor.clear();
    }
}

function editTestScenario(scenarioId) {
    const scenario = testScenarios.find(s => s.scenario_id === scenarioId);
    if (!scenario) return;

    showAddTestScenarioForm();
    document.getElementById('form-title').textContent = `Edytuj scenariusz: ${scenario.scenario_name}`;
    document.getElementById('test-scenario-name').value = scenario.scenario_name;
    document.getElementById('test-type').value = scenario.test_type;

    if (testParametersEditor && scenario.parameters) {
        testParametersEditor.setJSON(scenario.parameters);
    }
    if (expectedResultsEditor && scenario.expected_results) {
        expectedResultsEditor.setJSON(scenario.expected_results);
    }

    // Change button text and function
    const button = document.querySelector('#test-scenario-form button[onclick="createTestScenario()"]');
    if (button) {
        button.textContent = 'Aktualizuj scenariusz';
        button.setAttribute('onclick', `updateTestScenario(${scenarioId})`);
    }
}

async function updateTestScenario(scenarioId) {
    const name = document.getElementById('test-scenario-name').value;
    const type = document.getElementById('test-type').value;
    const parameters = testParametersEditor ? testParametersEditor.getJSON() : {};
    const expectedResults = expectedResultsEditor ? expectedResultsEditor.getJSON() : {};

    if (!name || !type) {
        alert('Wypełnij wymagane pola: nazwa scenariusza i typ testu');
        return;
    }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/test-scenario-configs/${scenarioId}`, {
            method: 'PUT',
            body: JSON.stringify({
                scenario_name: name,
                test_type: type,
                parameters: parameters,
                expected_results: expectedResults
            })
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Scenariusz testowy został zaktualizowany pomyślnie
                        </div>
                    `;
            hideAllConfigForms();
            loadTestScenarios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd aktualizacji scenariusza: ${error.message}
                    </div>
                `;
    }
}

async function deleteTestScenario(scenarioId) {
    const scenario = testScenarios.find(s => s.scenario_id === scenarioId);
    if (!scenario) return;

    if (!confirm(`Czy na pewno chcesz usunąć scenariusz "${scenario.scenario_name}"?`)) {
        return;
    }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-config/test-scenario-configs/${scenarioId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            document.getElementById('result').innerHTML = `
                        <div class="result">
                        ✅ Scenariusz testowy został usunięty pomyślnie
                        </div>
                    `;
            loadTestScenarios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Nieznany błąd');
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
                    <div class="result">
                    ❌ Błąd usuwania scenariusza: ${error.message}
                    </div>
                `;
    }
}

// Template JSON editor helper functions
function clearTemplateJSON() {
    if (templateJsonEditor) {
        templateJsonEditor.clear();
    }
}

function toggleTemplateJSONView() {
    const preview = document.getElementById('template-json-preview');
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        preview.textContent = JSON.stringify(templateJsonEditor.getJSON(), null, 2);
    } else {
        preview.style.display = 'none';
    }
}

// Hash routing support
function handleHashChange() {
    const hash = window.location.hash.substring(1);
    if (hash && ['system-config', 'device-config', 'test-config', 'json-templates'].includes(hash)) {
        // Simulate click on appropriate menu item
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            if (item.onclick && item.onclick.toString().includes(hash)) {
                item.click();
            }
        });
    } else if (hash === 'scenarios' || !hash) {
        showScenarios();
    }
}

window.addEventListener('hashchange', handleHashChange);

// Load scenarios on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI(); // Check if already logged in
    if (getAuthToken()) {
        loadScenarios();
    } else {
        document.getElementById('scenarios-list').innerHTML =
            '<p>Zaloguj się aby zobaczyć scenariusze...</p>';
    }

    // Handle initial hash
    handleHashChange();
});