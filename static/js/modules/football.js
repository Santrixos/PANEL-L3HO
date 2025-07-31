// Football Module JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    initializeFootballModule();
});

function initializeFootballModule() {
    setupLeagueSelector();
    setupControlButtons();
    setupTableSearch();
    updateLastUpdateTime();
    
    console.log('Football module initialized');
}

function setupLeagueSelector() {
    const leagueSelector = document.getElementById('leagueSelector');
    const seasonSelector = document.getElementById('seasonSelector');
    const loadButton = document.getElementById('loadLeagueData');
    
    if (loadButton) {
        loadButton.addEventListener('click', function() {
            const league = leagueSelector.value;
            const season = seasonSelector.value;
            
            if (!league) {
                PanelL3HO.showAlert('Por favor selecciona una liga', 'warning');
                return;
            }
            
            loadLeagueTable(league, season);
        });
    }
}

function setupControlButtons() {
    // Refresh Data Button
    const refreshBtn = document.getElementById('refreshData');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const league = document.getElementById('leagueSelector').value;
            const season = document.getElementById('seasonSelector').value;
            
            if (!league) {
                PanelL3HO.showAlert('Primero selecciona una liga', 'warning');
                return;
            }
            
            PanelL3HO.showLoading(this);
            setTimeout(() => {
                PanelL3HO.hideLoading(this);
                PanelL3HO.showAlert('Datos actualizados correctamente', 'success');
                updateLastUpdateTime();
            }, 2000);
        });
    }
    
    // Export CSV Button
    const exportCsvBtn = document.getElementById('exportData');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            exportTableData('csv');
        });
    }
    
    // Export JSON Button
    const exportJsonBtn = document.getElementById('exportJSON');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', function() {
            exportTableData('json');
        });
    }
    
    // View History Button
    const historyBtn = document.getElementById('viewHistory');
    if (historyBtn) {
        historyBtn.addEventListener('click', function() {
            showUpdateHistory();
        });
    }
}

async function loadLeagueTable(league, season) {
    const loadButton = document.getElementById('loadLeagueData');
    const tableBody = document.getElementById('leagueTableBody');
    const tableStatus = document.getElementById('tableStatus');
    
    PanelL3HO.showLoading(loadButton);
    tableStatus.textContent = 'Cargando...';
    tableStatus.className = 'badge bg-warning';
    
    try {
        // Simulate API call - replace with real API integration
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Sample data - replace with real API response
        const sampleData = generateSampleLeagueData(league);
        
        displayLeagueTable(sampleData);
        
        tableStatus.textContent = 'Datos cargados';
        tableStatus.className = 'badge bg-success';
        
        PanelL3HO.showAlert('Tabla de posiciones cargada correctamente', 'success');
        updateStats(sampleData);
        
    } catch (error) {
        console.error('Error loading league data:', error);
        PanelL3HO.showAlert('Error al cargar los datos de la liga', 'danger');
        
        tableStatus.textContent = 'Error';
        tableStatus.className = 'badge bg-danger';
    } finally {
        PanelL3HO.hideLoading(loadButton);
    }
}

function generateSampleLeagueData(league) {
    const teams = {
        'mx': ['América', 'Chivas', 'Cruz Azul', 'Tigres', 'Monterrey', 'León', 'Santos', 'Pachuca'],
        'es': ['Real Madrid', 'Barcelona', 'Atlético Madrid', 'Sevilla', 'Real Sociedad', 'Villarreal', 'Athletic Bilbao', 'Valencia'],
        'en': ['Manchester City', 'Arsenal', 'Liverpool', 'Newcastle', 'Manchester United', 'Tottenham', 'Brighton', 'Aston Villa'],
        'de': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Union Berlin', 'SC Freiburg', 'Eintracht Frankfurt', 'Wolfsburg', 'Mainz'],
        'it': ['Napoli', 'AC Milan', 'Inter Milan', 'Juventus', 'Atalanta', 'Roma', 'Lazio', 'Fiorentina'],
        'fr': ['PSG', 'Marseille', 'Monaco', 'Lens', 'Lille', 'Lyon', 'Nice', 'Montpellier']
    };
    
    const leagueTeams = teams[league] || teams['mx'];
    const data = [];
    
    leagueTeams.forEach((team, index) => {
        const points = Math.max(1, 35 - (index * 4) + Math.floor(Math.random() * 8));
        const played = 20 + Math.floor(Math.random() * 5);
        const won = Math.floor(points / 3) + Math.floor(Math.random() * 3);
        const drawn = Math.max(0, played - won - Math.floor(Math.random() * 5));
        const lost = played - won - drawn;
        const goalsFor = won * 2 + drawn + Math.floor(Math.random() * 10);
        const goalsAgainst = lost * 1.5 + Math.floor(Math.random() * 8);
        
        data.push({
            position: index + 1,
            team: team,
            played: played,
            won: won,
            drawn: drawn,
            lost: lost,
            goalsFor: Math.floor(goalsFor),
            goalsAgainst: Math.floor(goalsAgainst),
            goalDifference: Math.floor(goalsFor) - Math.floor(goalsAgainst),
            points: points
        });
    });
    
    return data.sort((a, b) => b.points - a.points);
}

function displayLeagueTable(data) {
    const tableBody = document.getElementById('leagueTableBody');
    
    tableBody.innerHTML = data.map(team => `
        <tr class="${getPositionClass(team.position)}">
            <td><strong>${team.position}</strong></td>
            <td>
                <div class="team-info">
                    <strong>${team.team}</strong>
                </div>
            </td>
            <td>${team.played}</td>
            <td>${team.won}</td>
            <td>${team.drawn}</td>
            <td>${team.lost}</td>
            <td>${team.goalsFor}</td>
            <td>${team.goalsAgainst}</td>
            <td class="${team.goalDifference >= 0 ? 'text-success' : 'text-danger'}">
                ${team.goalDifference > 0 ? '+' : ''}${team.goalDifference}
            </td>
            <td><strong class="text-primary">${team.points}</strong></td>
        </tr>
    `).join('');
}

function getPositionClass(position) {
    if (position <= 4) return 'table-success';
    if (position <= 6) return 'table-info';
    if (position >= 18) return 'table-danger';
    return '';
}

function updateStats(data) {
    const totalTeams = document.getElementById('totalTeams');
    const matchesWeek = document.getElementById('matchesWeek');
    
    if (totalTeams) {
        totalTeams.textContent = data.length;
    }
    
    if (matchesWeek) {
        matchesWeek.textContent = Math.floor(data.length / 2);
    }
}

function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('lastUpdate');
    if (lastUpdate) {
        const now = new Date();
        lastUpdate.textContent = now.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

function exportTableData(format) {
    const tableBody = document.getElementById('leagueTableBody');
    const rows = tableBody.querySelectorAll('tr');
    
    if (rows.length === 0 || rows[0].cells.length === 1) {
        PanelL3HO.showAlert('No hay datos para exportar', 'warning');
        return;
    }
    
    const data = [];
    rows.forEach(row => {
        if (row.cells.length > 1) {
            data.push({
                position: row.cells[0].textContent.trim(),
                team: row.cells[1].textContent.trim(),
                played: row.cells[2].textContent.trim(),
                won: row.cells[3].textContent.trim(),
                drawn: row.cells[4].textContent.trim(),
                lost: row.cells[5].textContent.trim(),
                goalsFor: row.cells[6].textContent.trim(),
                goalsAgainst: row.cells[7].textContent.trim(),
                goalDifference: row.cells[8].textContent.trim(),
                points: row.cells[9].textContent.trim()
            });
        }
    });
    
    if (format === 'csv') {
        exportToCSV(data);
    } else if (format === 'json') {
        exportToJSON(data);
    }
}

function exportToCSV(data) {
    const headers = ['Posición', 'Equipo', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'DG', 'Pts'];
    const csvContent = [
        headers.join(','),
        ...data.map(row => Object.values(row).join(','))
    ].join('\n');
    
    downloadFile(csvContent, 'tabla_posiciones.csv', 'text/csv');
    PanelL3HO.showAlert('Tabla exportada en formato CSV', 'success');
}

function exportToJSON(data) {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, 'tabla_posiciones.json', 'application/json');
    PanelL3HO.showAlert('Tabla exportada en formato JSON', 'success');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

function showUpdateHistory() {
    const historyContainer = document.getElementById('updateHistory');
    
    // Sample history data
    const history = [
        { date: new Date(), action: 'Tabla actualizada', league: 'Liga MX' },
        { date: new Date(Date.now() - 3600000), action: 'Datos exportados', league: 'LaLiga' },
        { date: new Date(Date.now() - 7200000), action: 'API sincronizada', league: 'Premier League' }
    ];
    
    historyContainer.innerHTML = history.map(item => `
        <div class="timeline-item">
            <div class="timeline-marker bg-primary"></div>
            <div class="timeline-content">
                <h6 class="mb-1">${item.action}</h6>
                <p class="mb-1 text-muted">${item.league}</p>
                <small class="text-muted">${item.date.toLocaleString('es-ES')}</small>
            </div>
        </div>
    `).join('');
}

function setupTableSearch() {
    // Add search functionality if needed
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Buscar equipo...';
    searchInput.id = 'teamSearch';
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('#leagueTableBody tr');
        
        rows.forEach(row => {
            const teamName = row.cells[1]?.textContent.toLowerCase();
            if (teamName && teamName.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
    
    // Add search input to table card header
    const tableCard = document.querySelector('#leagueTable').closest('.card');
    const cardBody = tableCard.querySelector('.card-body');
    if (cardBody && !document.getElementById('teamSearch')) {
        cardBody.insertBefore(searchInput, cardBody.firstChild);
    }
}

// Auto-refresh functionality
setInterval(function() {
    const league = document.getElementById('leagueSelector').value;
    if (league) {
        updateLastUpdateTime();
    }
}, 60000); // Update every minute

// Make functions available globally
window.FootballModule = {
    loadLeagueTable,
    exportTableData,
    showUpdateHistory
};