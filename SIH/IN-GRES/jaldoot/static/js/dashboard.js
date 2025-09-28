// JalDoot Dashboard JavaScript

let currentData = [];
let currentFilters = {
    region: '',
    year: '',
    language: 'en'
};

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    setupEventListeners();
    loadInitialData();
    initializeCharts();
}

function setupEventListeners() {
    // Filter controls
    const regionFilter = document.getElementById('regionFilter');
    const yearFilter = document.getElementById('yearFilter');
    
    if (regionFilter) {
        regionFilter.addEventListener('change', handleFilterChange);
    }
    
    if (yearFilter) {
        yearFilter.addEventListener('change', handleFilterChange);
    }
    
    // Language selection
    const languageRadios = document.querySelectorAll('input[name="language"]');
    languageRadios.forEach(radio => {
        radio.addEventListener('change', handleLanguageChange);
    });
    
    // Query interface
    const submitQuery = document.getElementById('submitQuery');
    const queryInput = document.getElementById('queryInput');
    const voiceInput = document.getElementById('voiceInput');
    const clearQuery = document.getElementById('clearQuery');
    
    if (submitQuery) {
        submitQuery.addEventListener('click', handleDashboardQuery);
    }
    
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleDashboardQuery();
            }
        });
    }
    
    if (voiceInput) {
        voiceInput.addEventListener('click', openVoiceModal);
    }
    
    if (clearQuery) {
        clearQuery.addEventListener('click', clearQueryInput);
    }
    
    // View toggles
    const viewTable = document.getElementById('viewTable');
    const viewCharts = document.getElementById('viewCharts');
    
    if (viewTable) {
        viewTable.addEventListener('click', () => toggleView('table'));
    }
    
    if (viewCharts) {
        viewCharts.addEventListener('click', () => toggleView('charts'));
    }
    
    // Quick actions
    const refreshData = document.getElementById('refreshData');
    const exportData = document.getElementById('exportData');
    
    if (refreshData) {
        refreshData.addEventListener('click', loadInitialData);
    }
    
    if (exportData) {
        exportData.addEventListener('click', exportDataToCSV);
    }
    
    // Voice modal
    const startRecording = document.getElementById('startRecording');
    const stopRecording = document.getElementById('stopRecording');
    
    if (startRecording) {
        startRecording.addEventListener('click', startVoiceRecording);
    }
    
    if (stopRecording) {
        stopRecording.addEventListener('click', stopVoiceRecording);
    }
}

async function loadInitialData() {
    try {
        showLoading(true);
        
        // Load all regions data
        const response = await fetch('/regions');
        const data = await response.json();
        
        if (response.ok) {
            currentData = data.regions || [];
            updateStatsCards();
            updateCharts();
            updateDataTable();
        } else {
            showAlert('Failed to load data: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showAlert('Network error while loading data', 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleFilterChange() {
    const region = document.getElementById('regionFilter')?.value || '';
    const year = document.getElementById('yearFilter')?.value || '';
    
    currentFilters.region = region;
    currentFilters.year = year;
    
    if (region && year) {
        await loadFilteredData(region, year);
    } else {
        loadInitialData();
    }
}

async function loadFilteredData(region, year) {
    try {
        showLoading(true);
        
        const response = await fetch(`/data/${region}/${year}`);
        const data = await response.json();
        
        if (response.ok) {
            currentData = data.data || [];
            updateStatsCards();
            updateCharts();
            updateDataTable();
        } else {
            showAlert('Failed to load filtered data: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error loading filtered data:', error);
        showAlert('Network error while loading filtered data', 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleDashboardQuery() {
    const queryInput = document.getElementById('queryInput');
    const language = getSelectedLanguage();
    
    if (!queryInput || !queryInput.value.trim()) {
        showAlert('Please enter a query', 'warning');
        return;
    }
    
    const query = queryInput.value.trim();
    
    try {
        showLoading(true);
        
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                language: language
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayQueryResults(data);
        } else {
            showAlert(data.error || 'Query failed', 'danger');
        }
    } catch (error) {
        console.error('Query error:', error);
        showAlert('Network error during query', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayQueryResults(data) {
    const aiResponseSection = document.getElementById('aiResponseSection');
    const aiResponse = document.getElementById('aiResponse');
    
    if (aiResponseSection && aiResponse) {
        aiResponse.innerHTML = `
            <div class="alert alert-info">
                <h6><i class="fas fa-robot me-2"></i>JalDoot Response</h6>
                <p class="mb-0">${data.ai_response || 'No response generated'}</p>
            </div>
        `;
        
        aiResponseSection.style.display = 'block';
        aiResponseSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Update data if new data is available
    if (data.data && data.data.length > 0) {
        currentData = data.data;
        updateStatsCards();
        updateCharts();
        updateDataTable();
    }
}

function updateStatsCards() {
    if (!currentData || currentData.length === 0) {
        document.getElementById('totalRecords').textContent = '0';
        document.getElementById('avgLevel').textContent = '0.0m';
        document.getElementById('totalRegions').textContent = '0';
        document.getElementById('dataQuality').textContent = 'N/A';
        return;
    }
    
    // Calculate statistics
    const measurements = currentData
        .filter(d => d.measurement !== null && d.measurement !== undefined)
        .map(d => d.measurement);
    
    const totalRecords = currentData.length;
    const avgLevel = measurements.length > 0 ? 
        (measurements.reduce((a, b) => a + b, 0) / measurements.length).toFixed(1) : 0;
    
    const uniqueRegions = new Set(currentData.map(d => d.region)).size;
    
    const qualityCounts = currentData.reduce((acc, d) => {
        const quality = d.data_quality || 'Unknown';
        acc[quality] = (acc[quality] || 0) + 1;
        return acc;
    }, {});
    
    const dominantQuality = Object.keys(qualityCounts).reduce((a, b) => 
        qualityCounts[a] > qualityCounts[b] ? a : b, 'Unknown');
    
    // Update DOM
    document.getElementById('totalRecords').textContent = totalRecords;
    document.getElementById('avgLevel').textContent = avgLevel + 'm';
    document.getElementById('totalRegions').textContent = uniqueRegions;
    document.getElementById('dataQuality').textContent = dominantQuality;
}

function initializeCharts() {
    // Initialize empty charts
    updateCharts();
}

function updateCharts() {
    if (!currentData || currentData.length === 0) {
        clearCharts();
        return;
    }
    
    updateGroundwaterChart();
    updateRegionalChart();
    updateAquiferChart();
    updateWellTypeChart();
}

function updateGroundwaterChart() {
    const chartDiv = document.getElementById('groundwaterChart');
    if (!chartDiv) return;
    
    // Group data by month if available
    const monthlyData = currentData.reduce((acc, d) => {
        const month = d.month || 'Unknown';
        if (!acc[month]) {
            acc[month] = [];
        }
        if (d.measurement !== null && d.measurement !== undefined) {
            acc[month].push(d.measurement);
        }
        return acc;
    }, {});
    
    const months = Object.keys(monthlyData).sort((a, b) => {
        if (a === 'Unknown') return 1;
        if (b === 'Unknown') return -1;
        return parseInt(a) - parseInt(b);
    });
    
    const avgLevels = months.map(month => {
        const values = monthlyData[month];
        return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    });
    
    const trace = {
        x: months,
        y: avgLevels,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Groundwater Level',
        line: { color: '#2E86AB', width: 3 },
        marker: { size: 8 }
    };
    
    const layout = {
        title: 'Groundwater Levels Over Time',
        xaxis: { title: 'Month' },
        yaxis: { title: 'Level (m)' },
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };
    
    Plotly.newPlot(chartDiv, [trace], layout, {responsive: true});
}

function updateRegionalChart() {
    const chartDiv = document.getElementById('regionalChart');
    if (!chartDiv) return;
    
    // Group by region
    const regionalData = currentData.reduce((acc, d) => {
        const region = d.region || 'Unknown';
        if (!acc[region]) {
            acc[region] = [];
        }
        if (d.measurement !== null && d.measurement !== undefined) {
            acc[region].push(d.measurement);
        }
        return acc;
    }, {});
    
    const regions = Object.keys(regionalData);
    const avgLevels = regions.map(region => {
        const values = regionalData[region];
        return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    });
    
    const trace = {
        x: avgLevels,
        y: regions,
        type: 'bar',
        orientation: 'h',
        name: 'Average Level',
        marker: { color: '#A23B72' }
    };
    
    const layout = {
        title: 'Regional Comparison',
        xaxis: { title: 'Average Level (m)' },
        yaxis: { title: 'Region' },
        margin: { t: 50, b: 50, l: 100, r: 50 }
    };
    
    Plotly.newPlot(chartDiv, [trace], layout, {responsive: true});
}

function updateAquiferChart() {
    const chartDiv = document.getElementById('aquiferChart');
    if (!chartDiv) return;
    
    // Count aquifer types
    const aquiferCounts = currentData.reduce((acc, d) => {
        const type = d.aquifer_type || 'Unknown';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {});
    
    const labels = Object.keys(aquiferCounts);
    const values = Object.values(aquiferCounts);
    
    const trace = {
        labels: labels,
        values: values,
        type: 'pie',
        marker: {
            colors: ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#FFD23F']
        }
    };
    
    const layout = {
        title: 'Aquifer Types Distribution',
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };
    
    Plotly.newPlot(chartDiv, [trace], layout, {responsive: true});
}

function updateWellTypeChart() {
    const chartDiv = document.getElementById('wellTypeChart');
    if (!chartDiv) return;
    
    // Count well types
    const wellCounts = currentData.reduce((acc, d) => {
        const type = d.well_type || 'Unknown';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {});
    
    const labels = Object.keys(wellCounts);
    const values = Object.values(wellCounts);
    
    const trace = {
        x: labels,
        y: values,
        type: 'bar',
        name: 'Well Count',
        marker: { color: '#F18F01' }
    };
    
    const layout = {
        title: 'Well Types Distribution',
        xaxis: { title: 'Well Type' },
        yaxis: { title: 'Count' },
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };
    
    Plotly.newPlot(chartDiv, [trace], layout, {responsive: true});
}

function clearCharts() {
    const chartIds = ['groundwaterChart', 'regionalChart', 'aquiferChart', 'wellTypeChart'];
    chartIds.forEach(id => {
        const chartDiv = document.getElementById(id);
        if (chartDiv) {
            Plotly.purge(chartDiv);
            chartDiv.innerHTML = '<p class="text-muted text-center">No data available</p>';
        }
    });
}

function updateDataTable() {
    const tableBody = document.getElementById('dataTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (!currentData || currentData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No data available</td></tr>';
        return;
    }
    
    currentData.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.region || 'N/A'}</td>
            <td>${record.district || 'N/A'}</td>
            <td>${record.state || 'N/A'}</td>
            <td>${record.year || 'N/A'}</td>
            <td>${record.month || 'N/A'}</td>
            <td>${record.measurement !== null ? record.measurement.toFixed(2) : 'N/A'}</td>
            <td>${record.well_type || 'N/A'}</td>
            <td>${record.aquifer_type || 'N/A'}</td>
            <td>
                <span class="badge bg-${getQualityBadgeColor(record.data_quality)}">
                    ${record.data_quality || 'Unknown'}
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function getQualityBadgeColor(quality) {
    switch (quality?.toLowerCase()) {
        case 'high': return 'success';
        case 'medium': return 'warning';
        case 'low': return 'danger';
        default: return 'secondary';
    }
}

function toggleView(view) {
    const chartsSection = document.getElementById('chartsSection');
    const tableSection = document.getElementById('tableSection');
    const viewTable = document.getElementById('viewTable');
    const viewCharts = document.getElementById('viewCharts');
    
    if (view === 'table') {
        chartsSection.style.display = 'none';
        tableSection.style.display = 'block';
        viewTable.classList.add('active');
        viewCharts.classList.remove('active');
    } else {
        chartsSection.style.display = 'block';
        tableSection.style.display = 'none';
        viewCharts.classList.add('active');
        viewTable.classList.remove('active');
    }
}

function openVoiceModal() {
    const voiceModal = new bootstrap.Modal(document.getElementById('voiceModal'));
    voiceModal.show();
}

function startVoiceRecording() {
    const startBtn = document.getElementById('startRecording');
    const stopBtn = document.getElementById('stopRecording');
    const voiceStatus = document.getElementById('voiceStatus');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showAlert('Speech recognition not supported in this browser', 'warning');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    const language = getSelectedLanguage();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        voiceStatus.innerHTML = `
            <i class="fas fa-microphone fa-3x text-danger"></i>
            <p class="mt-2">Recording... Click stop when done</p>
        `;
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const queryInput = document.getElementById('queryInput');
        if (queryInput) {
            queryInput.value = transcript;
        }
        stopVoiceRecording();
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        stopVoiceRecording();
        showAlert('Speech recognition error: ' + event.error, 'danger');
    };
    
    recognition.onend = function() {
        stopVoiceRecording();
    };
    
    recognition.start();
}

function stopVoiceRecording() {
    const startBtn = document.getElementById('startRecording');
    const stopBtn = document.getElementById('stopRecording');
    const voiceStatus = document.getElementById('voiceStatus');
    
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    voiceStatus.innerHTML = `
        <i class="fas fa-microphone fa-3x text-primary"></i>
        <p class="mt-2">Click to start recording</p>
    `;
}

function clearQueryInput() {
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = '';
    }
}

function getSelectedLanguage() {
    const languageRadios = document.querySelectorAll('input[name="language"]:checked');
    return languageRadios.length > 0 ? languageRadios[0].value : 'en';
}

function handleLanguageChange() {
    const language = getSelectedLanguage();
    const queryInput = document.getElementById('queryInput');
    
    if (queryInput) {
        const placeholders = {
            'en': 'Ask about groundwater data...',
            'hi': 'भूजल डेटा के बारे में पूछें...',
            'hinglish': 'Groundwater data ke baare mein pucho...'
        };
        queryInput.placeholder = placeholders[language] || placeholders['en'];
    }
}

function exportDataToCSV() {
    if (!currentData || currentData.length === 0) {
        showAlert('No data to export', 'warning');
        return;
    }
    
    const headers = ['Region', 'District', 'State', 'Year', 'Month', 'Measurement', 'Unit', 'Well Type', 'Aquifer Type', 'Data Quality'];
    const csvContent = [
        headers.join(','),
        ...currentData.map(record => [
            record.region || '',
            record.district || '',
            record.state || '',
            record.year || '',
            record.month || '',
            record.measurement || '',
            record.unit || '',
            record.well_type || '',
            record.aquifer_type || '',
            record.data_quality || ''
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jaldoot_data_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function showLoading(show) {
    const loadingElements = document.querySelectorAll('.spinner-border');
    loadingElements.forEach(el => {
        el.style.display = show ? 'inline-block' : 'none';
    });
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 1050; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Export functions for global access
window.Dashboard = {
    loadInitialData,
    handleFilterChange,
    handleDashboardQuery,
    toggleView,
    exportDataToCSV
};
