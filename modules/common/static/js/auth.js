/**
 * Fleet Management System - Authentication & Authorization
 * Common auth functions shared across all modules
 */

// Token management
function getAuthToken() {
    return localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function clearAuthToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRoles');
}

function getUserRole() {
    return localStorage.getItem('userRole');
}

function getUserName() {
    return localStorage.getItem('userName');
}

function getUserRoles() {
    const rolesStr = localStorage.getItem('userRoles');
    return rolesStr ? JSON.parse(rolesStr) : [];
}

// API request with authentication
async function makeAuthenticatedRequest(url, options = {}) {
    const token = getAuthToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, {
        ...options,
        headers
    });
}

// Login function
async function login(username, password) {
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            setAuthToken(data.access_token);
            localStorage.setItem('userRole', data.role);
            localStorage.setItem('userName', data.username);
            
            // Handle multi-role users
            if (data.available_roles && data.available_roles.length > 1) {
                localStorage.setItem('userRoles', JSON.stringify(data.available_roles));
            }
            
            return { success: true, data };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail || 'Login failed' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Logout function
function logout() {
    clearAuthToken();
    updateAuthUI();
    window.location.reload();
}

// Switch role (for multi-role users)
async function switchRole(newRole) {
    try {
        const response = await makeAuthenticatedRequest('/api/v1/auth/switch-role', {
            method: 'POST',
            body: JSON.stringify({ new_role: newRole })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('userRole', data.role);
            window.location.reload();
            return { success: true };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Update auth UI
function updateAuthUI() {
    const token = getAuthToken();
    const userName = getUserName();
    const userRole = getUserRole();
    const userRoles = getUserRoles();
    
    // Update login form visibility
    const loginForm = document.getElementById('login-form');
    const userInfo = document.getElementById('user-info');
    const authStatus = document.getElementById('auth-status');
    
    if (token && userName) {
        // User is logged in
        if (loginForm) loginForm.style.display = 'none';
        if (userInfo) {
            userInfo.style.display = 'block';
            userInfo.innerHTML = `
                <p><strong>👤 ${userName}</strong></p>
                <p>Rola: <span style="color: #3498db;">${userRole}</span></p>
                ${userRoles.length > 1 ? `
                    <select id="role-switcher" onchange="switchRole(this.value)" style="width: 100%; padding: 5px; margin-top: 10px; background: #374151; color: white; border: 1px solid #4b5563; border-radius: 4px;">
                        ${userRoles.map(r => `<option value="${r}" ${r === userRole ? 'selected' : ''}>${r}</option>`).join('')}
                    </select>
                ` : ''}
                <button onclick="logout()" class="btn-logout">Wyloguj</button>
            `;
        }
        if (authStatus) {
            authStatus.className = 'auth-status logged-in';
            authStatus.textContent = '✅ Zalogowany';
        }
    } else {
        // User is not logged in
        if (loginForm) loginForm.style.display = 'block';
        if (userInfo) userInfo.style.display = 'none';
        if (authStatus) {
            authStatus.className = 'auth-status not-logged-in';
            authStatus.textContent = '❌ Niezalogowany';
        }
    }
}

// Handle login form submission
async function handleLogin(event) {
    if (event) event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const resultDiv = document.getElementById('login-result');
    
    if (!username || !password) {
        if (resultDiv) {
            resultDiv.innerHTML = '<div class="result error">Wypełnij wszystkie pola</div>';
        }
        return;
    }
    
    const result = await login(username, password);
    
    if (result.success) {
        if (resultDiv) {
            resultDiv.innerHTML = '<div class="result">✅ Zalogowano pomyślnie!</div>';
        }
        updateAuthUI();
        // Refresh page data
        if (typeof loadDashboard === 'function') loadDashboard();
        if (typeof loadData === 'function') loadData();
    } else {
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="result error">❌ ${result.error}</div>`;
        }
    }
}

// Initialize auth UI on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
});
