// JavaScript for the Digital Fraud Detection System Web Interface

class FraudDetectionApp {
    constructor() {
        this.apiBase = '/api';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Form submissions
        document.getElementById('text-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeText();
        });

        document.getElementById('audio-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeAudio();
        });

        document.getElementById('video-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeVideo();
        });

        document.getElementById('batch-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeBatch();
        });

        // Threshold sliders
        document.getElementById('text-threshold').addEventListener('input', (e) => {
            document.getElementById('text-threshold-value').textContent = e.target.value;
        });

        document.getElementById('audio-threshold').addEventListener('input', (e) => {
            document.getElementById('audio-threshold-value').textContent = e.target.value;
        });

        document.getElementById('video-threshold').addEventListener('input', (e) => {
            document.getElementById('video-threshold-value').textContent = e.target.value;
        });
    }

    async loadDashboard() {
        try {
            const [statsResponse, alertsResponse] = await Promise.all([
                fetch(`${this.apiBase}/statistics`),
                fetch(`${this.apiBase}/alerts`)
            ]);

            const stats = await statsResponse.json();
            const alerts = await alertsResponse.json();

            if (stats.success) {
                this.updateDashboard(stats.statistics);
            }

            if (alerts.success) {
                this.updateAlerts(alerts.alerts);
                this.updateAlertCount(alerts.count);
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    updateDashboard(stats) {
        // Update stat cards
        document.getElementById('total-processed').textContent = stats.system_stats.total_processed;
        document.getElementById('scams-detected').textContent = stats.system_stats.scams_detected;
        document.getElementById('active-alerts').textContent = stats.alert_stats.active_alerts;
        
        // Update uptime
        const uptimeHours = Math.floor(stats.uptime_seconds / 3600);
        document.getElementById('system-uptime').textContent = `${uptimeHours}h`;

        // Update recent alerts
        this.updateRecentAlerts(stats.alert_stats);

        // Update system status
        this.updateSystemStatus(stats.model_status);
    }

    updateRecentAlerts(alertStats) {
        const recentAlertsDiv = document.getElementById('recent-alerts');
        
        if (alertStats.active_alerts === 0) {
            recentAlertsDiv.innerHTML = '<p class="text-muted">No recent alerts</p>';
            return;
        }

        // This would normally show actual recent alerts
        recentAlertsDiv.innerHTML = `
            <div class="alert alert-warning">
                <strong>${alertStats.active_alerts}</strong> active alerts require attention
            </div>
        `;
    }

    updateSystemStatus(modelStatus) {
        const statusDiv = document.getElementById('system-status');
        statusDiv.innerHTML = `
            <div class="d-flex justify-content-between">
                <span>Text Analysis</span>
                <span class="badge ${modelStatus.text_trained ? 'bg-success' : 'bg-warning'}">
                    ${modelStatus.text_trained ? 'Trained' : 'Not Trained'}
                </span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Audio Analysis</span>
                <span class="badge ${modelStatus.audio_trained ? 'bg-success' : 'bg-warning'}">
                    ${modelStatus.audio_trained ? 'Trained' : 'Not Trained'}
                </span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Video Analysis</span>
                <span class="badge ${modelStatus.video_trained ? 'bg-success' : 'bg-warning'}">
                    ${modelStatus.video_trained ? 'Trained' : 'Not Trained'}
                </span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Alert System</span>
                <span class="badge bg-success">Active</span>
            </div>
        `;
    }

    updateAlerts(alerts) {
        const alertsList = document.getElementById('alerts-list');
        
        if (alerts.length === 0) {
            alertsList.innerHTML = '<p class="text-muted">No active alerts</p>';
            return;
        }

        alertsList.innerHTML = alerts.map(alert => this.createAlertCard(alert)).join('');
    }

    createAlertCard(alert) {
        const levelClass = alert.level.toLowerCase();
        const timeAgo = this.getTimeAgo(new Date(alert.timestamp));
        
        return `
            <div class="alert-card ${levelClass}">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="card-title">${alert.title}</h6>
                                <p class="card-text">${alert.message}</p>
                                <small class="text-muted">
                                    <i class="fas fa-clock"></i> ${timeAgo} | 
                                    <i class="fas fa-user"></i> ${alert.source} | 
                                    <i class="fas fa-broadcast-tower"></i> ${alert.channel}
                                </small>
                            </div>
                            <div class="text-end">
                                <span class="risk-badge ${alert.level.toLowerCase()}">${alert.level}</span>
                                <div class="mt-2">
                                    <button class="btn btn-sm btn-outline-primary" onclick="acknowledgeAlert('${alert.id}')">
                                        <i class="fas fa-check"></i> Acknowledge
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" onclick="resolveAlert('${alert.id}')">
                                        <i class="fas fa-times"></i> Resolve
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h6>Recommendations:</h6>
                            ${alert.recommendations.map(rec => `
                                <div class="recommendation">
                                    <i class="fas fa-lightbulb"></i> ${rec}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateAlertCount(count) {
        const alertCountBadge = document.getElementById('alert-count');
        alertCountBadge.textContent = count;
        alertCountBadge.style.display = count > 0 ? 'inline' : 'none';
    }

    async analyzeText() {
        const text = document.getElementById('text-content').value;
        const sender = document.getElementById('text-sender').value;
        const channel = document.getElementById('text-channel').value;

        if (!text.trim()) {
            this.showError('Please enter text to analyze');
            return;
        }

        this.showLoading('text-result');

        try {
            const response = await fetch(`${this.apiBase}/analyze/text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, sender, channel })
            });

            const result = await response.json();
            this.displayAnalysisResult('text-result', result);
        } catch (error) {
            this.showError('Error analyzing text: ' + error.message);
        }
    }

    async analyzeAudio() {
        const callerId = document.getElementById('audio-caller').value;
        const duration = document.getElementById('audio-duration').value;
        const audioFile = document.getElementById('audio-file').files[0];

        this.showLoading('audio-result');

        try {
            const response = await fetch(`${this.apiBase}/analyze/audio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ caller_id: callerId, duration: duration })
            });

            const result = await response.json();
            this.displayAnalysisResult('audio-result', result);
        } catch (error) {
            this.showError('Error analyzing audio: ' + error.message);
        }
    }

    async analyzeVideo() {
        const callerId = document.getElementById('video-caller').value;
        const duration = document.getElementById('video-duration').value;
        const videoFile = document.getElementById('video-file').files[0];

        this.showLoading('video-result');

        try {
            const response = await fetch(`${this.apiBase}/analyze/video`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ caller_id: callerId, duration: duration })
            });

            const result = await response.json();
            this.displayAnalysisResult('video-result', result);
        } catch (error) {
            this.showError('Error analyzing video: ' + error.message);
        }
    }

    async analyzeBatch() {
        const file = document.getElementById('batch-file').files[0];
        
        if (!file) {
            this.showError('Please select a CSV file');
            return;
        }

        this.showLoading('batch-result');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiBase}/data/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.displayBatchResult('batch-result', result);
        } catch (error) {
            this.showError('Error analyzing batch: ' + error.message);
        }
    }

    displayAnalysisResult(containerId, result) {
        const container = document.getElementById(containerId);
        
        if (!result.success) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error: ${result.error}
                </div>
            `;
            return;
        }

        const analysis = result.analysis;
        const isScam = analysis.is_scam;
        const riskLevel = analysis.risk_level;
        
        container.innerHTML = `
            <div class="analysis-result ${isScam ? 'scam' : 'safe'}">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5>
                        <i class="fas fa-${isScam ? 'exclamation-triangle' : 'check-circle'}"></i>
                        Analysis Result
                    </h5>
                    <span class="risk-badge ${riskLevel.toLowerCase()}">${riskLevel} RISK</span>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6>Scam Score: ${(analysis.scam_score * 100).toFixed(1)}%</h6>
                        <div class="progress mb-3">
                            <div class="progress-bar ${isScam ? 'bg-danger' : 'bg-success'}" 
                                 style="width: ${analysis.scam_score * 100}%"></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        ${analysis.deepfake_score !== undefined ? `
                            <h6>Deepfake Score: ${(analysis.deepfake_score * 100).toFixed(1)}%</h6>
                            <div class="progress mb-3">
                                <div class="progress-bar bg-warning" 
                                     style="width: ${analysis.deepfake_score * 100}%"></div>
                            </div>
                        ` : ''}
                    </div>
                </div>

                ${analysis.explanation ? `
                    <div class="mb-3">
                        <h6>Explanation:</h6>
                        <p>${analysis.explanation}</p>
                    </div>
                ` : ''}

                ${analysis.recommendations && analysis.recommendations.length > 0 ? `
                    <div class="mb-3">
                        <h6>Recommendations:</h6>
                        ${analysis.recommendations.map(rec => `
                            <div class="recommendation">
                                <i class="fas fa-lightbulb"></i> ${rec}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}

                ${analysis.found_scam_keywords && analysis.found_scam_keywords.length > 0 ? `
                    <div class="mb-3">
                        <h6>Detected Keywords:</h6>
                        ${analysis.found_scam_keywords.map(keyword => `
                            <span class="keyword-highlight">${keyword}</span>
                        `).join(' ')}
                    </div>
                ` : ''}

                <small class="text-muted">
                    <i class="fas fa-clock"></i> Analyzed at ${new Date(result.timestamp).toLocaleString()}
                </small>
            </div>
        `;
    }

    displayBatchResult(containerId, result) {
        const container = document.getElementById(containerId);
        
        if (!result.success) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error: ${result.error}
                </div>
            `;
            return;
        }

        const totalProcessed = result.total_processed;
        const results = result.results;
        const scamCount = results.filter(r => r.success && r.analysis && r.analysis.is_scam).length;
        
        container.innerHTML = `
            <div class="alert alert-info">
                <h5><i class="fas fa-chart-bar"></i> Batch Analysis Complete</h5>
                <p>Processed ${totalProcessed} communications</p>
                <p>Detected ${scamCount} potential scams</p>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Source</th>
                            <th>Scam Score</th>
                            <th>Risk Level</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(r => `
                            <tr>
                                <td>${r.type}</td>
                                <td>${r.analysis ? (r.analysis.source || 'Unknown') : 'Error'}</td>
                                <td>${r.analysis ? (r.analysis.scam_score * 100).toFixed(1) + '%' : 'N/A'}</td>
                                <td>
                                    ${r.analysis ? `
                                        <span class="risk-badge ${r.analysis.risk_level.toLowerCase()}">
                                            ${r.analysis.risk_level}
                                        </span>
                                    ` : 'Error'}
                                </td>
                                <td>
                                    ${r.success ? 
                                        '<span class="badge bg-success">Success</span>' : 
                                        '<span class="badge bg-danger">Error</span>'
                                    }
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    showLoading(containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Analyzing...</span>
                </div>
                <p class="mt-2">Analyzing communication...</p>
            </div>
        `;
    }

    showError(message) {
        // Create a temporary error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    startAutoRefresh() {
        // Refresh dashboard every 30 seconds
        setInterval(() => {
            this.loadDashboard();
        }, 30000);
    }

    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            const result = await response.json();
            
            if (result.success) {
                this.updateCharts(result.statistics);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateCharts(stats) {
        // Processing chart
        const processingCtx = document.getElementById('processing-chart');
        if (processingCtx && !this.charts.processing) {
            this.charts.processing = new Chart(processingCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Text', 'Audio', 'Video'],
                    datasets: [{
                        data: [
                            stats.system_stats.text_processed,
                            stats.system_stats.audio_processed,
                            stats.system_stats.video_processed
                        ],
                        backgroundColor: ['#667eea', '#f093fb', '#4facfe']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Alert distribution chart
        const alertCtx = document.getElementById('alert-chart');
        if (alertCtx && !this.charts.alerts) {
            this.charts.alerts = new Chart(alertCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(stats.alert_stats.level_distribution),
                    datasets: [{
                        label: 'Alerts',
                        data: Object.values(stats.alert_stats.level_distribution),
                        backgroundColor: ['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1']
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
}

// Global functions for button clicks
async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/acknowledge`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            app.loadDashboard();
        } else {
            app.showError('Failed to acknowledge alert');
        }
    } catch (error) {
        app.showError('Error acknowledging alert: ' + error.message);
    }
}

async function resolveAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/resolve`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            app.loadDashboard();
        } else {
            app.showError('Failed to resolve alert');
        }
    } catch (error) {
        app.showError('Error resolving alert: ' + error.message);
    }
}

async function refreshAlerts() {
    await app.loadDashboard();
}

async function trainModels() {
    try {
        const response = await fetch('/api/models/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data_dir: 'data' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            app.showError('Models trained successfully!');
            app.loadDashboard();
        } else {
            app.showError('Failed to train models: ' + result.error);
        }
    } catch (error) {
        app.showError('Error training models: ' + error.message);
    }
}

async function generateData() {
    try {
        const response = await fetch('/api/data/generate', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            app.showError('Mock data generated successfully!');
        } else {
            app.showError('Failed to generate data: ' + result.error);
        }
    } catch (error) {
        app.showError('Error generating data: ' + error.message);
    }
}

function exportData() {
    // This would export statistics to CSV
    app.showError('Export functionality not implemented yet');
}

// Initialize the app when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new FraudDetectionApp();
    
    // Load statistics when statistics tab is shown
    document.getElementById('statistics').addEventListener('shown.bs.tab', () => {
        app.loadStatistics();
    });
});