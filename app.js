// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Current filter for requests
let currentFilter = 'all';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadData();
    
    // Auto-refresh every 5 seconds
    setInterval(loadData, 5000);
});

function initializeApp() {
    console.log('Smart Parking System initialized');
}

function setupEventListeners() {
    // Form submission
    document.getElementById('requestForm').addEventListener('submit', handleRequestSubmit);
    
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            loadRequests();
        });
    });
}

// Load all data
async function loadData() {
    await Promise.all([
        loadSystemState(),
        loadAnalytics()
    ]);
}

// Load system state (zones and requests)
async function loadSystemState() {
    try {
        const response = await fetch(`${API_BASE}/system/state`);
        const data = await response.json();
        
        if (data.success) {
            renderZones(data.data.zones);
            renderRequests(data.data.requests);
            updateQuickStats(data.data);
        }
    } catch (error) {
        console.error('Error loading system state:', error);
    }
}

// Load analytics
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/system/analytics`);
        const data = await response.json();
        
        if (data.success) {
            renderAnalytics(data.data);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Render zones
function renderZones(zones) {
    const container = document.getElementById('zonesContainer');
    
    container.innerHTML = zones.map(zone => `
        <div class="zone-card">
            <div class="zone-header">
                <div class="zone-name">${zone.zone_name}</div>
                <div class="zone-badge">${zone.zone_id}</div>
            </div>
            <div class="zone-stats">
                <span>${zone.available_slots} Available</span>
                <span>${zone.occupied_slots}/${zone.total_slots}</span>
            </div>
            <div class="zone-progress">
                <div class="zone-progress-bar" style="width: ${zone.utilization}%"></div>
            </div>
        </div>
    `).join('');
}

// Render requests
function renderRequests(requests) {
    const container = document.getElementById('requestsContainer');
    
    // Filter requests
    let filteredRequests = requests;
    if (currentFilter !== 'all') {
        filteredRequests = requests.filter(r => r.state === currentFilter);
    }
    
    // Filter out RELEASED and CANCELLED for display
    filteredRequests = filteredRequests.filter(r => 
        r.state !== 'RELEASED' && r.state !== 'CANCELLED'
    );
    
    if (filteredRequests.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                No active requests
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredRequests.map(request => {
        const actions = getRequestActions(request);
        
        return `
            <div class="request-card" data-request-id="${request.request_id}">
                <div class="request-header">
                    <div class="request-id">${request.request_id}</div>
                    <div class="state-badge ${request.state}">${request.state}</div>
                </div>
                <div class="request-info">
                    <div><strong>Vehicle:</strong> ${request.vehicle_id}</div>
                    <div><strong>Requested:</strong> ${request.requested_zone}</div>
                    ${request.allocated_zone ? `<div><strong>Allocated:</strong> ${request.allocated_zone} ${request.is_cross_zone ? '⚠️' : ''}</div>` : ''}
                    ${request.slot_id ? `<div><strong>Slot:</strong> ${request.slot_id}</div>` : ''}
                </div>
                ${actions.length > 0 ? `
                    <div class="request-actions">
                        ${actions.map(action => `
                            <button class="btn-${action.type}" onclick="${action.handler}('${request.request_id}')">
                                ${action.label}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Get available actions for a request based on its state
function getRequestActions(request) {
    const actions = [];
    
    switch (request.state) {
        case 'REQUESTED':
            actions.push({ label: 'Allocate', type: 'primary', handler: 'processRequest' });
            actions.push({ label: 'Cancel', type: 'danger', handler: 'cancelRequest' });
            break;
        case 'ALLOCATED':
            actions.push({ label: 'Occupy', type: 'primary', handler: 'occupySlot' });
            actions.push({ label: 'Cancel', type: 'danger', handler: 'cancelRequest' });
            break;
        case 'OCCUPIED':
            actions.push({ label: 'Release', type: 'secondary', handler: 'releaseSlot' });
            break;
    }
    
    return actions;
}

// Render analytics
function renderAnalytics(analytics) {
    document.getElementById('avgDuration').textContent = 
        analytics.average_parking_duration.toFixed(1);
    document.getElementById('completedRequests').textContent = 
        analytics.completed_requests;
    document.getElementById('cancelledRequests').textContent = 
        analytics.cancelled_requests;
    document.getElementById('crossZone').textContent = 
        analytics.cross_zone_allocations;
    document.getElementById('peakZone').textContent = 
        analytics.peak_usage_zone || '-';
}

// Update quick stats
function updateQuickStats(data) {
    const activeVehicles = data.requests.filter(r => 
        r.state === 'ALLOCATED' || r.state === 'OCCUPIED'
    ).length;
    
    document.getElementById('totalVehicles').textContent = activeVehicles;
    document.getElementById('totalRequests').textContent = data.requests.length;
}

// Handle request form submission
async function handleRequestSubmit(e) {
    e.preventDefault();
    
    const vehicleId = document.getElementById('vehicleId').value;
    const requestedZone = document.getElementById('zoneSelect').value;
    
    try {
        const response = await fetch(`${API_BASE}/request/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vehicle_id: vehicleId, requested_zone: requestedZone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Request created successfully!', 'success');
            document.getElementById('requestForm').reset();
            
            // Auto-process the request
            setTimeout(() => processRequest(data.data.request_id), 500);
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error creating request', 'error');
        console.error(error);
    }
}

// Process a parking request
async function processRequest(requestId) {
    try {
        const response = await fetch(`${API_BASE}/request/process/${requestId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error processing request', 'error');
        console.error(error);
    }
}

// Occupy a parking slot
async function occupySlot(requestId) {
    try {
        const response = await fetch(`${API_BASE}/request/occupy/${requestId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Slot occupied successfully!', 'success');
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error occupying slot', 'error');
        console.error(error);
    }
}

// Release a parking slot
async function releaseSlot(requestId) {
    try {
        const response = await fetch(`${API_BASE}/request/release/${requestId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const duration = data.data.parking_duration;
            showNotification(`Slot released! Duration: ${duration ? duration.toFixed(1) + ' min' : 'N/A'}`, 'success');
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error releasing slot', 'error');
        console.error(error);
    }
}

// Cancel a parking request
async function cancelRequest(requestId) {
    if (!confirm('Are you sure you want to cancel this request?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/cancel/${requestId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Request cancelled successfully!', 'info');
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error cancelling request', 'error');
        console.error(error);
    }
}

// Show rollback modal
function showRollbackModal() {
    document.getElementById('rollbackModal').classList.add('active');
}

// Close rollback modal
function closeRollbackModal() {
    document.getElementById('rollbackModal').classList.remove('active');
}

// Execute rollback
async function executeRollback() {
    const k = parseInt(document.getElementById('rollbackCount').value);
    
    if (!k || k < 1) {
        showNotification('Please enter a valid number', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rollback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ k })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            closeRollbackModal();
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error performing rollback', 'error');
        console.error(error);
    }
}

// Reset system
async function resetSystem() {
    if (!confirm('Are you sure you want to reset the entire system? This will clear all data.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/system/reset`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('System reset successfully!', 'info');
            await loadData();
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        showNotification('Error resetting system', 'error');
        console.error(error);
    }
}

// Refresh data manually
async function refreshData() {
    showNotification('Refreshing data...', 'info');
    await loadData();
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">${message}</div>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Load requests (for filter changes)
async function loadRequests() {
    await loadSystemState();
}