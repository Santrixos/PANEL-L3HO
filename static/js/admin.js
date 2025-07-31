// Panel L3HO - Admin Panel JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
});

function initializeAdmin() {
    setupApiForm();
    setupWebsiteForm();
    setupStatusSelectors();
    setupDeleteButtons();
    
    console.log('Admin panel initialized');
}

function setupApiForm() {
    const apiForm = document.getElementById('apiForm');
    if (!apiForm) return;
    
    apiForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        PanelL3HO.showLoading(submitBtn);
        
        try {
            const formData = new FormData(this);
            const response = await fetch('/admin/api/add', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                PanelL3HO.showAlert(result.message, 'success');
                this.reset();
                refreshApiTable();
            } else {
                PanelL3HO.showAlert(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error adding API:', error);
            PanelL3HO.showAlert('Error al agregar la API', 'danger');
        } finally {
            PanelL3HO.hideLoading(submitBtn);
        }
    });
}

function setupWebsiteForm() {
    const websiteForm = document.getElementById('websiteForm');
    if (!websiteForm) return;
    
    websiteForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        PanelL3HO.showLoading(submitBtn);
        
        try {
            const formData = new FormData(this);
            const response = await fetch('/admin/website/add', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                PanelL3HO.showAlert(result.message, 'success');
                this.reset();
                refreshWebsiteTable();
            } else {
                PanelL3HO.showAlert(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error adding website:', error);
            PanelL3HO.showAlert('Error al agregar el sitio web', 'danger');
        } finally {
            PanelL3HO.hideLoading(submitBtn);
        }
    });
}

function setupStatusSelectors() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', async function() {
            const websiteId = this.dataset.websiteId;
            const newStatus = this.value;
            const originalValue = this.dataset.originalValue || this.value;
            
            try {
                const response = await fetch(`/admin/website/status/${websiteId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ status: newStatus })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    PanelL3HO.showAlert(result.message, 'success');
                    this.dataset.originalValue = newStatus;
                    
                    // Update row styling based on status
                    updateRowStatus(this.closest('tr'), newStatus);
                } else {
                    PanelL3HO.showAlert(result.message, 'danger');
                    this.value = originalValue; // Revert to original value
                }
            } catch (error) {
                console.error('Error updating status:', error);
                PanelL3HO.showAlert('Error al actualizar el estado', 'danger');
                this.value = originalValue; // Revert to original value
            }
        });
        
        // Store original value
        select.dataset.originalValue = select.value;
    });
}

function updateRowStatus(row, status) {
    // Remove existing status classes
    row.classList.remove('status-active', 'status-inactive', 'status-maintenance');
    
    // Add new status class
    row.classList.add(`status-${status}`);
    
    // Update visual indicators if needed
    const statusBadge = row.querySelector('.status-badge');
    if (statusBadge) {
        statusBadge.className = `badge bg-${getStatusColor(status)}`;
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'active': return 'success';
        case 'inactive': return 'danger';
        case 'maintenance': return 'warning';
        default: return 'secondary';
    }
}

function setupDeleteButtons() {
    // API delete buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('button[onclick*="deleteApi"]')) {
            e.preventDefault();
            const button = e.target.closest('button');
            const apiId = button.getAttribute('onclick').match(/\d+/)[0];
            deleteApi(apiId);
        }
        
        if (e.target.closest('button[onclick*="deleteWebsite"]')) {
            e.preventDefault();
            const button = e.target.closest('button');
            const websiteId = button.getAttribute('onclick').match(/\d+/)[0];
            deleteWebsite(websiteId);
        }
    });
}

async function deleteApi(apiId) {
    const confirmed = confirm('¿Está seguro de que desea eliminar esta API?');
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/admin/api/delete/${apiId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            PanelL3HO.showAlert(result.message, 'success');
            refreshApiTable();
        } else {
            PanelL3HO.showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error deleting API:', error);
        PanelL3HO.showAlert('Error al eliminar la API', 'danger');
    }
}

async function deleteWebsite(websiteId) {
    const confirmed = confirm('¿Está seguro de que desea eliminar este sitio web?');
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/admin/website/delete/${websiteId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            PanelL3HO.showAlert(result.message, 'success');
            refreshWebsiteTable();
        } else {
            PanelL3HO.showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error deleting website:', error);
        PanelL3HO.showAlert('Error al eliminar el sitio web', 'danger');
    }
}

function refreshApiTable() {
    // Reload the APIs tab content
    const currentTab = document.querySelector('#nav-apis-tab');
    if (currentTab && currentTab.classList.contains('active')) {
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
}

function refreshWebsiteTable() {
    // Reload the websites tab content
    const currentTab = document.querySelector('#nav-websites-tab');
    if (currentTab && currentTab.classList.contains('active')) {
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
}

// Test API connection
async function testApiConnection(apiId) {
    const button = document.querySelector(`[data-api-id="${apiId}"] .test-btn`);
    if (button) {
        PanelL3HO.showLoading(button);
    }
    
    try {
        const response = await fetch(`/admin/api/test/${apiId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            PanelL3HO.showAlert('Conexión exitosa con la API', 'success');
        } else {
            PanelL3HO.showAlert(`Error de conexión: ${result.message}`, 'warning');
        }
    } catch (error) {
        console.error('Error testing API:', error);
        PanelL3HO.showAlert('Error al probar la conexión', 'danger');
    } finally {
        if (button) {
            PanelL3HO.hideLoading(button);
        }
    }
}

// Bulk operations
function selectAllItems(checkbox) {
    const table = checkbox.closest('table');
    const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
    
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    
    updateBulkActions();
}

function updateBulkActions() {
    const selectedItems = document.querySelectorAll('tbody input[type="checkbox"]:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        if (selectedItems.length > 0) {
            bulkActions.style.display = 'block';
            bulkActions.querySelector('.selected-count').textContent = selectedItems.length;
        } else {
            bulkActions.style.display = 'none';
        }
    }
}

// Export/Import functions
function exportData(type) {
    const url = `/admin/export/${type}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `panel_l3ho_${type}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function importData(type) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = async function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`/admin/import/${type}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                PanelL3HO.showAlert(result.message, 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                PanelL3HO.showAlert(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error importing data:', error);
            PanelL3HO.showAlert('Error al importar los datos', 'danger');
        }
    };
    
    input.click();
}

// Search and filter functions
function setupSearch() {
    const searchInputs = document.querySelectorAll('.table-search');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Initialize advanced features
function initializeAdvancedFeatures() {
    setupSearch();
    
    // Add any additional advanced features here
    console.log('Advanced admin features initialized');
}

// Call advanced features initialization
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeAdvancedFeatures, 500);
});

// Make functions available globally
window.AdminPanel = {
    deleteApi,
    deleteWebsite,
    testApiConnection,
    selectAllItems,
    updateBulkActions,
    exportData,
    importData
};
