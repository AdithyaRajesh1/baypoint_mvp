// Configuration
const API_BASE_URL = window.location.origin;
const API_URL = `${API_BASE_URL}/analyze`;
const HEALTH_URL = `${API_BASE_URL}/health`;

// DOM Elements
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const fileName = document.getElementById('file-name');
const analyzeBtn = document.getElementById('analyze-btn');
const uploadForm = document.getElementById('upload-form');
const loadingStatus = document.getElementById('loading-status');
const realEstateContent = document.getElementById('real-estate-content');
const financialContent = document.getElementById('financial-content');
const marketContent = document.getElementById('market-content');
const legalContent = document.getElementById('legal-content');
const orchestratorContent = document.getElementById('orchestrator-content');
const newAnalysisBtn = document.getElementById('new-analysis-btn');
const retryBtn = document.getElementById('retry-btn');
const downloadAllBtn = document.getElementById('download-all-btn');

let currentResults = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    setupEventListeners();
});

// Check if server is running
async function checkServerHealth() {
    try {
        const response = await fetch(HEALTH_URL);
        if (!response.ok) {
            showError('Server is not responding. Please make sure the Flask server is running.');
        }
    } catch (error) {
        showError('Cannot connect to server. Please make sure the Flask server is running on ' + API_BASE_URL);
    }
}

// Setup event listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // Form submit
    uploadForm.addEventListener('submit', handleSubmit);
    
    // New analysis button
    newAnalysisBtn.addEventListener('click', resetForm);
    
    // Retry button
    retryBtn.addEventListener('click', () => {
        errorSection.style.display = 'none';
        uploadSection.style.display = 'block';
    });
    
    // Download buttons
    downloadAllBtn.addEventListener('click', downloadAllReports);
    
    // Use event delegation for download buttons (they're in the results section)
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('download-btn')) {
            const reportType = e.target.getAttribute('data-report');
            downloadReport(reportType);
        }
    });
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        updateFileDisplay(file);
    }
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file) {
        if (isValidFile(file)) {
            fileInput.files = e.dataTransfer.files;
            updateFileDisplay(file);
        } else {
            showError('Invalid file type. Please upload TXT, PDF, DOC, DOCX, or MD files.');
        }
    }
}

// Check if file is valid
function isValidFile(file) {
    const validExtensions = ['.txt', '.pdf', '.doc', '.docx', '.md'];
    const fileName = file.name.toLowerCase();
    return validExtensions.some(ext => fileName.endsWith(ext));
}

// Update file display
function updateFileDisplay(file) {
    fileName.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    analyzeBtn.disabled = false;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Handle form submit
async function handleSubmit(e) {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a file first.');
        return;
    }
    
    // Show loading, hide upload
    uploadSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Reset progress steps
    resetProgressSteps();
    
    // Upload and analyze
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        updateLoadingStatus('Uploading file...');
        
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error occurred' }));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        updateLoadingStatus('Analyzing property fundamentals...');
        updateProgressStep('step-real-estate', 'active');
        await delay(2000);
        updateProgressStep('step-real-estate', 'completed');
        
        updateLoadingStatus('Performing financial modeling...');
        updateProgressStep('step-financial', 'active');
        await delay(2000);
        updateProgressStep('step-financial', 'completed');
        
        updateLoadingStatus('Analyzing market conditions...');
        updateProgressStep('step-market', 'active');
        await delay(2000);
        updateProgressStep('step-market', 'completed');
        
        updateLoadingStatus('Analyzing legal and compliance...');
        updateProgressStep('step-legal', 'active');
        await delay(2000);
        updateProgressStep('step-legal', 'completed');
        
        updateLoadingStatus('Synthesizing final recommendation...');
        updateProgressStep('step-orchestrator', 'active');
        await delay(2000);
        updateProgressStep('step-orchestrator', 'completed');
        
        updateLoadingStatus('Finalizing...');
        
        const result = await response.json();
        
        // Store results
        currentResults = result;
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while analyzing the file.');
    }
}

// Update loading status
function updateLoadingStatus(status) {
    loadingStatus.textContent = status;
}

// Update progress step
function updateProgressStep(stepId, state) {
    const step = document.getElementById(stepId);
    step.className = `step ${state}`;
    
    const icon = step.querySelector('.step-icon');
    if (state === 'active') {
        icon.textContent = '...';
    } else if (state === 'completed') {
        icon.textContent = 'OK';
    }
}

// Reset progress steps
function resetProgressSteps() {
    ['step-real-estate', 'step-financial', 'step-market', 'step-legal', 'step-orchestrator'].forEach(stepId => {
        const step = document.getElementById(stepId);
        if (step) {
            step.className = 'step';
            step.querySelector('.step-icon').textContent = '...';
        }
    });
}

// Display results
function displayResults(result) {
    realEstateContent.textContent = result.real_estate_report || 'No real estate analysis available.';
    financialContent.textContent = result.financial_modeling_report || 'No financial modeling analysis available.';
    marketContent.textContent = result.market_analysis_report || 'No market analysis available.';
    legalContent.textContent = result.legal_report || 'No legal analysis available.';
    orchestratorContent.textContent = result.orchestrator_report || 'No orchestrator report available.';
    
    // Show results, hide loading
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
}

// Show error
function showError(message) {
    document.getElementById('error-message').textContent = message;
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';
}

// Reset form
function resetForm() {
    fileInput.value = '';
    fileName.textContent = '';
    analyzeBtn.disabled = true;
    currentResults = null;
    
    uploadSection.style.display = 'block';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// Download report
function downloadReport(reportType) {
    if (!currentResults) return;
    
    // Map report types to result keys
    const reportKeyMap = {
        'real_estate': 'real_estate_report',
        'financial_modeling': 'financial_modeling_report',
        'market_analysis': 'market_analysis_report',
        'legal': 'legal_report',
        'orchestrator': 'orchestrator_report'
    };
    
    const reportKey = reportKeyMap[reportType];
    const reportContent = currentResults[reportKey];
    const reportId = currentResults.report_id;
    
    if (!reportContent) {
        showError(`No ${reportType} report available.`);
        return;
    }
    
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportId}_${reportType}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Download all reports
function downloadAllReports() {
    if (!currentResults) return;
    
    ['real_estate', 'financial_modeling', 'market_analysis', 'legal', 'orchestrator'].forEach((type, index) => {
        setTimeout(() => downloadReport(type), index * 300);
    });
}

// Utility: Delay function
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

