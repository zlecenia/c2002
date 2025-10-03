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
            `<span style="color: #3498db;">✅ Zalogowany jako <strong>${activeRole}</strong></span>`;
        
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
                `<span style="color: #3498db;">✅ Przełączono na rolę: <strong>${selectedRole}</strong></span>`;
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
                `<span style="color: #3498db;">✅ Zalogowano jako ${data.user.role}: ${username}</span>`;
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
}

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

document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
});
