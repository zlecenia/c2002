/**
 * Fleet Software Manager - Frontend Logic
 * Manages software, versions, and installations
 */

let currentSoftwareId = null;
let softwareList = [];

// Initialize module
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    loadDashboard();
});

// Load dashboard statistics
async function loadDashboard() {
    if (!getAuthToken()) {
        return; // Don't send request if not authenticated
    }
    
    try {
        const response = await makeAuthenticatedRequest('/api/v1/fleet-software/dashboard/stats');
        
        if (response.status === 401 || response.status === 403) {
            clearAuthToken();
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
    if (!getAuthToken()) {
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
            clearAuthToken();
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
    if (!getAuthToken()) {
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
            clearAuthToken();
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
