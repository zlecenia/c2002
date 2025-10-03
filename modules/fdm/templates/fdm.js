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
        if (!getAuthToken()) {
            return; // Don't send request if not authenticated
        }

        try {
            const response = await makeAuthenticatedRequest('/api/v1/fleet-data/dashboard');

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
        if (!getAuthToken()) {
            document.getElementById('devices-table').getElementsByTagName('tbody')[0].innerHTML =
                '<tr><td colspan="5" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć urządzenia...</td></tr>';
            return;
        }

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
                    '<tr><td colspan="5" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Manager</td></tr>';
                clearAuthToken();
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
        if (!getAuthToken()) {
            document.getElementById('customers-table').getElementsByTagName('tbody')[0].innerHTML =
                '<tr><td colspan="4" style="color: #95a5a6;">💡 Zaloguj się aby zobaczyć klientów...</td></tr>';
            return;
        }

        try {
            const response = await makeAuthenticatedRequest('/api/v1/fleet-data/customers');

            if (response.ok) {
                customers = await response.json();
                displayCustomers(customers);
            } else if (response.status === 401 || response.status === 403) {
                document.getElementById('customers-table').getElementsByTagName('tbody')[0].innerHTML =
                    '<tr><td colspan="4" style="color: #e74c3c;">❌ Brak autoryzacji - wymagana rola Manager</td></tr>';
                clearAuthToken();
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
