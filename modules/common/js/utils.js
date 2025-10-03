/**
 * Fleet Management System - Common Utility Functions
 */

// Show/hide loading indicator
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div style="text-align: center; padding: 20px;"><p>⏳ Ładowanie...</p></div>';
    }
}

// Display message
function showMessage(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    if (element) {
        const className = type === 'error' ? 'result error' : 'result';
        element.innerHTML = `<div class="${className}">${message}</div>`;
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL');
}

// Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pl-PL');
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Tab management
function showTab(tabId, tabButtonId = null) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.style.display = 'block';
    }
    
    // Add active class to selected button
    if (tabButtonId) {
        const selectedButton = document.getElementById(tabButtonId);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
    }
    
    // Update URL hash
    window.location.hash = tabId;
}

// Initialize tabs from hash
function initTabsFromHash() {
    const hash = window.location.hash.substring(1);
    if (hash) {
        showTab(hash);
    }
}

// Listen for hash changes
window.addEventListener('hashchange', function() {
    const hash = window.location.hash.substring(1);
    if (hash) {
        showTab(hash);
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initTabsFromHash();
});
