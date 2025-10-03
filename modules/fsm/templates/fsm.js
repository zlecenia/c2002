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
        document.getElementById('auth-message').innerHTML = `<span style="color: #27ae60;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;

        if (userRoles && userRoles.length > 1) {
            const roleSelect = document.getElementById('role-select');
            roleSelect.innerHTML = '<option value="">Wybierz rolę...</option>';
            userRoles.forEach(role => {
                const option = document.createElement('option');
                option.value = role;
                option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                if (role === activeRole) option.selected = true;
                roleSelect.appendChild(option);
            });
            document.getElementById('role-switcher').style.display = 'block';
        } else {
            document.getElementById('role-switcher').style.display = 'none';
        }
        loadDashboard();
    } else {
        document.getElementById('auth-message').innerHTML = '<span style="color: #e74c3c;">❌ Niezalogowany</span>';
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
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getAuthToken()}` },
            body: JSON.stringify({ new_role: selectedRole })
        });
        if (response.ok) {
            const data = await response.json();
            setAuthToken(data.access_token);
            document.getElementById('auth-message').innerHTML = `<span style="color: #27ae60;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
            loadDashboard();
        } else {
            const error = await response.json();
            document.getElementById('auth-message').innerHTML = `<span style="color: #e74c3c;">❌ Błąd: ${error.detail}</span>`;
        }
    } catch (error) {
        document.getElementById('auth-message').innerHTML = `<span style="color: #e74c3c;">❌ Błąd: ${error.message}</span>`;
    }
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
        event.target.classList.add('active');
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    if (!username || !password) { alert('Podaj username i hasło'); return; }

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
            setAuthToken(data.access_token);
            document.getElementById('login-password').value = '';
            document.getElementById('result').innerHTML = `<div class="result">✅ Zalogowano jako ${username}</div>`;
        } else {
            const error = await response.json();
            document.getElementById('auth-message').innerHTML = `<span style="color: #e74c3c;">❌ Błąd: ${error.detail}</span>`;
        }
    } catch (error) {
        document.getElementById('auth-message').innerHTML = `<span style="color: #e74c3c;">❌ Błąd: ${error.message}</span>`;
    }
}

function logout() {
    clearAuthToken();
    document.getElementById('login-username').value = '';
    document.getElementById('login-password').value = '';
    document.getElementById('software-list').innerHTML = '<p>Zaloguj się aby zobaczyć oprogramowanie...</p>';
    document.getElementById('result').innerHTML = '<div class="result">ℹ️ Wylogowano</div>';
}

async function makeAuthenticatedRequest(url, options = {}) {
    const token = getAuthToken();
    try {
        return await fetch(url, {
            ...options,
            headers: { 'Content-Type': 'application/json', ...(token && { 'Authorization': `Bearer ${token}` }), ...options.headers }
        });
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

function showTab(tabId, tabButton) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if (tabButton) tabButton.classList.add('active');
}

async function loadDashboard() {
    if (!getAuthToken()) return;
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
        if (response.status === 401 || response.status === 403) { clearAuthToken(); return; }
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
    if (!getAuthToken()) {
        document.getElementById('software-list').innerHTML = '<div style="color: #95a5a6; padding: 10px;">💡 Zaloguj się</div>';
        return;
    }
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software');
        if (response.status === 401 || response.status === 403) {
            document.getElementById('software-list').innerHTML = '<div style="color: #e74c3c;">❌ Brak autoryzacji</div>';
            clearAuthToken();
            return;
        }
        softwareList = await response.json();
        displaySoftware(softwareList);
        populateSoftwareSelect();
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">Błąd: ${error.message}</div>`;
    }
}

function displaySoftware(software) {
    const container = document.getElementById('software-list');
    if (software.length === 0) {
        container.innerHTML = '<p>Brak oprogramowania.</p>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Nazwa</th><th>Kategoria</th><th>Dostawca</th><th>Platforma</th><th>Wersje</th><th>Najnowsza</th><th>Akcje</th></tr></thead><tbody>';
    software.forEach(sw => {
        html += `<tr>
                <td><strong>${sw.name}</strong><br><small>${sw.description || ''}</small></td>
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

function showCreateSoftwareForm() { document.getElementById('create-software-form').style.display = 'block'; }
function hideCreateSoftwareForm() {
    document.getElementById('create-software-form').style.display = 'none';
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
    if (!softwareData.name || !softwareData.category) { alert('Podaj nazwę i kategorię'); return; }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software', {
            method: 'POST',
            body: JSON.stringify(softwareData)
        });
        if (response.ok) {
            const result = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">✅ Utworzono '${result.name}'</div>`;
            hideCreateSoftwareForm();
            loadSoftware();
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.message}</div>`;
    }
}

async function viewSoftware(softwareId) {
    const software = softwareList.find(s => s.id === softwareId);
    if (!software) return;
    document.getElementById('result').innerHTML = `
            <div class="result" style="background: #e8f5e9; border-color: #4caf50;">
                <h4>📦 ${software.name}</h4>
                <p><strong>Kategoria:</strong> ${software.category}</p>
                <p><strong>Vendor:</strong> ${software.vendor || 'Brak'}</p>
                <p><strong>Platforma:</strong> ${software.platform || 'Brak'}</p>
                <p><strong>Opis:</strong> ${software.description || 'Brak'}</p>
            </div>
        `;
}

async function deleteSoftware(softwareId) {
    if (!confirm('Czy na pewno chcesz usunąć to oprogramowanie?')) return;
    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${softwareId}`, { method: 'DELETE' });
        if (response.ok) {
            document.getElementById('result').innerHTML = '<div class="result">✅ Usunięto</div>';
            loadSoftware();
            loadDashboard();
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.message}</div>`;
    }
}

async function loadVersions() {
    const softwareId = document.getElementById('version-software-select').value;
    if (!softwareId) {
        document.getElementById('versions-list').innerHTML = '<p>Wybierz oprogramowanie</p>';
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
        document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.message}</div>`;
    }
}

function displayVersions(versions) {
    const container = document.getElementById('versions-list');
    if (versions.length === 0) {
        container.innerHTML = '<p>Brak wersji.</p>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Wersja</th><th>Typ</th><th>Instalacje</th><th>Utworzono</th><th>Akcje</th></tr></thead><tbody>';
    versions.forEach(version => {
        const badges = [];
        if (version.is_stable) badges.push('<span class="status-badge status-installed">Stabilna</span>');
        if (version.is_beta) badges.push('<span class="status-badge" style="background: #f39c12;">Beta</span>');
        if (version.requires_reboot) badges.push('<span class="status-badge" style="background: #e67e22;">Restart</span>');
        html += `<tr>
                <td><strong>${version.version_number}</strong><br><small>${version.release_notes || ''}</small></td>
                <td>${badges.join(' ')}</td>
                <td>${version.installations_count}</td>
                <td>${new Date(version.created_at).toLocaleDateString()}</td>
                <td><button class="btn btn-secondary" onclick="viewVersion(${version.id})" style="font-size: 10px; padding: 5px;">Zobacz</button></td>
            </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function showCreateVersionForm() {
    if (!currentSoftwareId) { alert('Wybierz oprogramowanie'); return; }
    document.getElementById('create-version-form').style.display = 'block';
}

function hideCreateVersionForm() {
    document.getElementById('create-version-form').style.display = 'none';
    document.getElementById('version-number').value = '';
    document.getElementById('version-release-notes').value = '';
    document.getElementById('version-download-url').value = '';
    document.getElementById('version-stable').checked = true;
    document.getElementById('version-beta').checked = false;
    document.getElementById('version-reboot').checked = false;
}

async function createVersion() {
    if (!currentSoftwareId) { alert('Wybierz oprogramowanie'); return; }
    const versionData = {
        software_id: currentSoftwareId,
        version_number: document.getElementById('version-number').value,
        release_notes: document.getElementById('version-release-notes').value,
        download_url: document.getElementById('version-download-url').value,
        is_stable: document.getElementById('version-stable').checked,
        is_beta: document.getElementById('version-beta').checked,
        requires_reboot: document.getElementById('version-reboot').checked
    };
    if (!versionData.version_number) { alert('Podaj numer wersji'); return; }

    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${currentSoftwareId}/versions`, {
            method: 'POST',
            body: JSON.stringify(versionData)
        });
        if (response.ok) {
            const result = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">✅ Utworzono wersję '${result.version_number}'</div>`;
            hideCreateVersionForm();
            loadVersions();
            loadSoftware();
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.message}</div>`;
    }
}

async function loadInstallations() {
    if (!getAuthToken()) {
        document.getElementById('installations-list').innerHTML = '<div style="color: #95a5a6;">💡 Zaloguj się</div>';
        return;
    }
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations');
        if (response.status === 401 || response.status === 403) {
            document.getElementById('installations-list').innerHTML = '<div style="color: #e74c3c;">❌ Brak autoryzacji</div>';
            clearAuthToken();
            return;
        }
        const installations = await response.json();
        displayInstallations(installations);
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">Błąd: ${error.message}</div>`;
    }
}

function displayInstallations(installations) {
    const container = document.getElementById('installations-list');
    if (installations.length === 0) {
        container.innerHTML = '<p>Brak historii instalacji.</p>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Urządzenie</th><th>Oprogramowanie</th><th>Akcja</th><th>Status</th><th>Data</th></tr></thead><tbody>';
    installations.forEach(installation => {
        const statusClass = installation.status === 'completed' ? 'status-installed' : installation.status === 'pending' ? 'status-pending' : 'status-failed';
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

function showInstallationForm() { document.getElementById('installation-form').style.display = 'block'; }
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
        alert('Wypełnij wszystkie pola');
        return;
    }

    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations', {
            method: 'POST',
            body: JSON.stringify(installationData)
        });
        if (response.ok) {
            const result = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">✅ Instalacja rozpoczęta na ${result.device_number}</div>`;
            hideInstallationForm();
            loadInstallations();
            loadDashboard();
        } else {
            const error = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.detail}</div>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">❌ Błąd: ${error.message}</div>`;
    }
}

// API Testing
async function testSoftwareAPI() {
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software');
        const data = await response.json();
        document.getElementById('result').innerHTML = `<div class="result">Test Software API\nStatus: ${response.status}\n${JSON.stringify(data, null, 2)}</div>`;
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">Error: ${error.message}</div>`;
    }
}

async function testVersionsAPI() {
    if (softwareList.length > 0) {
        const softwareId = softwareList[0].id;
        try {
            const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${softwareId}/versions`);
            const data = await response.json();
            document.getElementById('result').innerHTML = `<div class="result">Test Versions API\nStatus: ${response.status}\n${JSON.stringify(data, null, 2)}</div>`;
        } catch (error) {
            document.getElementById('result').innerHTML = `<div class="result">Error: ${error.message}</div>`;
        }
    } else {
        document.getElementById('result').innerHTML = '<div class="result">❌ Brak oprogramowania</div>';
    }
}

async function testInstallationsAPI() {
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations');
        const data = await response.json();
        document.getElementById('result').innerHTML = `<div class="result">Test Installations API\nStatus: ${response.status}\n${JSON.stringify(data, null, 2)}</div>`;
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">Error: ${error.message}</div>`;
    }
}

async function testDashboard() {
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
        const data = await response.json();
        document.getElementById('result').innerHTML = `<div class="result">Test Dashboard\nStatus: ${response.status}\n${JSON.stringify(data, null, 2)}</div>`;
    } catch (error) {
        document.getElementById('result').innerHTML = `<div class="result">Error: ${error.message}</div>`;
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
});
