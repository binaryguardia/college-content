// JalDoot Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize voice functionality
    initializeVoiceFeatures();
    
    // Set up sample query handlers
    setupSampleQueries();
    
    // Initialize language detection
    initializeLanguageDetection();
}

function setupEventListeners() {
    // Submit button
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', handleQuerySubmit);
    }
    
    // Voice button
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleVoiceRecording);
    }
    
    // Query input enter key
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleQuerySubmit();
            }
        });
    }
    
    // Language selection
    const languageRadios = document.querySelectorAll('input[name="language"]');
    languageRadios.forEach(radio => {
        radio.addEventListener('change', handleLanguageChange);
    });
}

function setupSampleQueries() {
    const sampleQueryBtns = document.querySelectorAll('.sample-query');
    sampleQueryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            const queryInput = document.getElementById('queryInput');
            if (queryInput) {
                queryInput.value = query;
                handleQuerySubmit();
            }
        });
    });
}

function initializeLanguageDetection() {
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.addEventListener('input', function() {
            // Auto-detect language as user types
            const text = this.value.trim();
            if (text.length > 10) {
                detectLanguage(text);
            }
        });
    }
}

function initializeVoiceFeatures() {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.style.display = 'inline-block';
        }
    } else {
        console.log('Speech recognition not supported in this browser');
    }
}

async function handleQuerySubmit() {
    const queryInput = document.getElementById('queryInput');
    const language = getSelectedLanguage();
    
    if (!queryInput || !queryInput.value.trim()) {
        showAlert('Please enter a query', 'warning');
        return;
    }
    
    const query = queryInput.value.trim();
    
    // Show loading state
    showLoading(true);
    hideResults();
    
    try {
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
            displayResults(data);
        } else {
            showAlert(data.error || 'An error occurred', 'danger');
        }
    } catch (error) {
        console.error('Query error:', error);
        showAlert('Network error. Please try again.', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const aiResponseDiv = document.getElementById('aiResponse');
    const visualizationsDiv = document.getElementById('visualizations');
    
    if (!resultsDiv || !aiResponseDiv || !visualizationsDiv) return;
    
    // Display AI response
    aiResponseDiv.innerHTML = `
        <div class="alert alert-info">
            <h6><i class="fas fa-robot me-2"></i>JalDoot Response</h6>
            <p class="mb-0">${data.ai_response || 'No response generated'}</p>
        </div>
    `;
    
    // Display visualizations
    if (data.visualizations) {
        visualizationsDiv.innerHTML = '';
        
        // Groundwater levels chart
        if (data.visualizations.groundwater_levels) {
            const chartDiv = createChartContainer('Groundwater Levels', data.visualizations.groundwater_levels);
            visualizationsDiv.appendChild(chartDiv);
        }
        
        // Aquifer types chart
        if (data.visualizations.aquifer_types) {
            const chartDiv = createChartContainer('Aquifer Types Distribution', data.visualizations.aquifer_types);
            visualizationsDiv.appendChild(chartDiv);
        }
        
        // Well types chart
        if (data.visualizations.well_types) {
            const chartDiv = createChartContainer('Well Types Distribution', data.visualizations.well_types);
            visualizationsDiv.appendChild(chartDiv);
        }
        
        // Data quality chart
        if (data.visualizations.data_quality) {
            const chartDiv = createChartContainer('Data Quality Distribution', data.visualizations.data_quality);
            visualizationsDiv.appendChild(chartDiv);
        }
        
        // Summary statistics
        if (data.visualizations.summary_stats) {
            const chartDiv = createChartContainer('Summary Statistics', data.visualizations.summary_stats);
            visualizationsDiv.appendChild(chartDiv);
        }
    }
    
    // Show results with animation
    resultsDiv.style.display = 'block';
    resultsDiv.classList.add('fade-in');
}

function createChartContainer(title, chartData) {
    const colDiv = document.createElement('div');
    colDiv.className = 'col-lg-6 mb-4';
    
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    
    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';
    cardHeader.innerHTML = `<h6 class="m-0 font-weight-bold text-primary">${title}</h6>`;
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    
    const img = document.createElement('img');
    img.src = chartData;
    img.className = 'img-fluid';
    img.style.width = '100%';
    img.style.height = 'auto';
    
    cardBody.appendChild(img);
    cardDiv.appendChild(cardHeader);
    cardDiv.appendChild(cardBody);
    colDiv.appendChild(cardDiv);
    
    return colDiv;
}

function toggleVoiceRecording() {
    const voiceBtn = document.getElementById('voiceBtn');
    const queryInput = document.getElementById('queryInput');
    
    if (!voiceBtn || !queryInput) return;
    
    if (voiceBtn.classList.contains('recording')) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

function startVoiceRecording() {
    const voiceBtn = document.getElementById('voiceBtn');
    const queryInput = document.getElementById('queryInput');
    
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
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        queryInput.placeholder = 'Listening...';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        queryInput.value = transcript;
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        queryInput.placeholder = 'Ask about groundwater data...';
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        queryInput.placeholder = 'Ask about groundwater data...';
        showAlert('Speech recognition error: ' + event.error, 'danger');
    };
    
    recognition.onend = function() {
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        queryInput.placeholder = 'Ask about groundwater data...';
    };
    
    recognition.start();
}

function stopVoiceRecording() {
    // This will be handled by the recognition.onend event
}

function getSelectedLanguage() {
    const languageRadios = document.querySelectorAll('input[name="language"]:checked');
    return languageRadios.length > 0 ? languageRadios[0].value : 'en';
}

function handleLanguageChange() {
    const language = getSelectedLanguage();
    const queryInput = document.getElementById('queryInput');
    
    if (queryInput) {
        // Update placeholder based on language
        const placeholders = {
            'en': 'Ask about groundwater data...',
            'hi': 'भूजल डेटा के बारे में पूछें...',
            'hinglish': 'Groundwater data ke baare mein pucho...'
        };
        queryInput.placeholder = placeholders[language] || placeholders['en'];
    }
}

async function detectLanguage(text) {
    try {
        const response = await fetch('/api/language/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (response.ok && data.detected_language) {
            // Auto-select detected language
            const languageRadio = document.getElementById(`lang-${data.detected_language}`);
            if (languageRadio) {
                languageRadio.checked = true;
            }
        }
    } catch (error) {
        console.error('Language detection error:', error);
    }
}

function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    const submitBtn = document.getElementById('submitBtn');
    
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
    
    if (submitBtn) {
        submitBtn.disabled = show;
        if (show) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        } else {
            submitBtn.innerHTML = '<i class="fas fa-search"></i> Search';
        }
    }
}

function hideResults() {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
        resultsDiv.classList.remove('fade-in');
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the demo section
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.insertBefore(alertDiv, demoSection.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Export functions for global access
window.JalDoot = {
    handleQuerySubmit,
    toggleVoiceRecording,
    showAlert,
    formatNumber,
    formatDate
};
