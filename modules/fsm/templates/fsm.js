/**
 * Fleet Software Manager - Frontend Logic
 * Manages software, versions, and installations
 */

let authToken = null;
let currentSoftwareId = null;
let softwareList = [];

// Enhanced auth token management (wrapper for auth.js)
function getAuthTokenLocal() {
    if (!authToken) {
        authToken = getAuthToken(); // from auth.js
    }
    return authToken;
}

function setAuthTokenLocal(token) {
    authToken = token;
    setAuthToken(token); // from auth.js
    updateAuthUI();
}

function clearAuthTokenLocal() {
    authToken = null;
    clearAuthToken(); // from auth.js
    updateAuthUI();
}

// Additional role management functions
function getUserRoles() {
    const token = getAuthTokenLocal();
    if (!token) return [];
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.roles || [];
    } catch (e) {
        return [];
    }
}

function getActiveRole() {
    const token = getAuthTokenLocal();
    if (!token) return '';
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.active_role || payload.role || '';
    } catch (e) {
        return '';
    }
}

// Enhanced switch role with UI updates
async function switchRole() {
    const selectedRole = document.getElementById('role-select').value;
    if (!selectedRole) return;

    try {
        const response = await fetch('/api/v1/auth/switch-role', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthTokenLocal()}`
            },
            body: JSON.stringify({ new_role: selectedRole })
        });

        if (response.ok) {
            const data = await response.json();
            setAuthTokenLocal(data.access_token);
            showMessage('result', `✅ Przełączono na rolę: <strong>${selectedRole}</strong>`, 'success');
            loadDashboard();
        } else {
            const error = await response.json();
            showMessage('result', `❌ Błąd przełączania roli: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('result', `❌ Błąd połączenia: ${error.message}`, 'error');
    }
}

// Custom login function for FSM
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showMessage('login-result', 'Podaj username i hasło', 'error');
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
            setAuthTokenLocal(data.access_token);
            document.getElementById('password').value = '';
            showMessage('result', `✅ Zalogowano pomyślnie jako ${username} (${data.user.role})`, 'success');
        } else {
            const error = await response.json();
            const errorMsg = error.detail || 'Nieznany błąd';
            showMessage('login-result', `❌ Błąd logowania: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showMessage('login-result', `❌ Błąd połączenia: ${error.message}`, 'error');
    }
}

// Tab navigation with hash support
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
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
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

// Initialize module
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    loadDashboard();
});

// Load dashboard statistics
async function loadDashboard() {
    if (!getAuthTokenLocal()) {
        return; // Don't send request if not authenticated
    }
    
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
        
        if (response.status === 401 || response.status === 403) {
            clearAuthTokenLocal();
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

// Load software list
async function loadSoftware() {
    if (!getAuthTokenLocal()) {
        document.getElementById('software-list').innerHTML = `
            <div style="color: #95a5a6; padding: 10px;">
            💡 Zaloguj się aby zobaczyć oprogramowanie...
            </div>
        `;
        return;
    }
    
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/software');
        
        if (response.status === 401 || response.status === 403) {
            document.getElementById('software-list').innerHTML = `
                <div style="color: #e74c3c; padding: 10px;">
                ❌ Brak autoryzacji - wymagana rola Maker
                </div>
            `;
            clearAuthTokenLocal();
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

// Display software in table
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

// View software details
async function viewSoftware(softwareId) {
    const software = softwareList.find(s => s.id === softwareId);
    if (!software) {
        document.getElementById('result').innerHTML = `
            <div class="result">
            ❌ Nie znaleziono oprogramowania o ID: ${softwareId}
            </div>
        `;
        return;
    }

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
            <p><strong>Liczba wersji:</strong> ${software.versions_count || 0}</p>
            <p><strong>Najnowsza wersja:</strong> <span class="version-badge">${software.latest_version || 'Brak'}</span></p>
        </div>
    `;
}

// Delete software
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

// Show/hide forms
function showCreateSoftwareForm() {
    document.getElementById('create-software-form').style.display = 'block';
}

function hideCreateSoftwareForm() {
    document.getElementById('create-software-form').style.display = 'none';
    // Reset form
    document.getElementById('software-name').value = '';
    document.getElementById('software-description').value = '';
    document.getElementById('software-vendor').value = '';
    document.getElementById('software-category').value = '';
    document.getElementById('software-platform').value = '';
    document.getElementById('software-repository').value = '';
}

// Create software
async function createSoftware() {
    const softwareData = {
        name: document.getElementById('software-name').value,
        description: document.getElementById('software-description').value,
        vendor: document.getElementById('software-vendor').value,
        category: document.getElementById('software-category').value,
        platform: document.getElementById('software-platform').value,
        repository_url: document.getElementById('software-repository').value
    };

    if (!softwareData.name || !softwareData.category) {
        alert('Wypełnij wymagane pola (Nazwa, Kategoria)');
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

// Populate software select for versions
function populateSoftwareSelect() {
    const select = document.getElementById('version-software-select');
    if (!select) return;
    
    select.innerHTML = '<option value="">-- Wybierz oprogramowanie --</option>';
    softwareList.forEach(sw => {
        const option = document.createElement('option');
        option.value = sw.id;
        option.textContent = `${sw.name} (${sw.versions_count} wersji)`;
        select.appendChild(option);
    });
}

// Load installations
async function loadInstallations() {
    if (!getAuthTokenLocal()) {
        document.getElementById('installations-list').innerHTML = `
            <div style="color: #95a5a6; padding: 10px;">
            💡 Zaloguj się aby zobaczyć historię instalacji...
            </div>
        `;
        return;
    }
    
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/installations');
        
        if (response.status === 401 || response.status === 403) {
            document.getElementById('installations-list').innerHTML = `
                <div style="color: #e74c3c; padding: 10px;">
                ❌ Brak autoryzacji - wymagana rola Maker
                </div>
            `;
            clearAuthTokenLocal();
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

// Display installations
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

// API Test functions
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

// ========== VERSION MANAGEMENT FUNCTIONS ==========

// Load versions for selected software
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
        showMessage('result', `❌ Błąd ładowania wersji: ${error.message}`, 'error');
    }
}

// Display versions in table
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
            <td>${formatDate(version.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewVersion(${version.id})" style="font-size: 10px; padding: 5px;">Zobacz</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// View version details
async function viewVersion(versionId) {
    try {
        const response = await makeAuthenticatedRequest(`/api/v1/fleet-software/software/${currentSoftwareId}/versions`);
        const versions = await response.json();
        const version = versions.find(v => v.id === versionId);
        
        if (!version) {
            showMessage('result', '❌ Nie znaleziono wersji', 'error');
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
                <p><strong>Utworzono:</strong> ${formatDate(version.created_at)}</p>
            </div>
        `;
    } catch (error) {
        showMessage('result', `❌ Błąd ładowania wersji: ${error.message}`, 'error');
    }
}

// Show/hide version form
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

// Create version
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
            showMessage('result', `✅ Wersja '${result.version_number}' utworzona pomyślnie`, 'success');
            hideCreateVersionForm();
            loadVersions();
            loadSoftware(); // Refresh software list to update version counts
        } else {
            const error = await response.json();
            showMessage('result', `❌ Błąd tworzenia wersji: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('result', `❌ Błąd: ${error.message}`, 'error');
    }
}

// ========== INSTALLATION MANAGEMENT FUNCTIONS ==========

// Load devices for installation
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

// Load versions for installation
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

// Show/hide installation form
function showInstallationForm() {
    document.getElementById('installation-form').style.display = 'block';
    loadDevicesForInstallation();
    loadVersionsForInstallation();
}

function hideInstallationForm() {
    document.getElementById('installation-form').style.display = 'none';
    document.getElementById('installation-device').value = '';
    document.getElementById('installation-version').value = '';
    document.getElementById('installation-action').value = 'install';
    document.getElementById('installation-notes').value = '';
}

// Create installation
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
            showMessage('result', `✅ Instalacja rozpoczęta pomyślnie na urządzeniu ${result.device_number}\nOprogramowanie: ${result.software_name} v${result.version_number}`, 'success');
            hideInstallationForm();
            loadInstallations();
            loadDashboard();
        } else {
            const error = await response.json();
            showMessage('result', `❌ Błąd instalacji: ${error.detail}`, 'error');
        }
    } catch (error) {
        showMessage('result', `❌ Błąd: ${error.message}`, 'error');
    }
}

// ========== ADDITIONAL API TESTING FUNCTIONS ==========

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
            showMessage('result', `❌ Error testing Versions API: ${error.message}`, 'error');
        }
    } else {
        showMessage('result', '❌ Brak oprogramowania do testowania API wersji', 'error');
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
        showMessage('result', `❌ Error testing Installations API: ${error.message}`, 'error');
    }
}
