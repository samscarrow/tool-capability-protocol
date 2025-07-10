#!/usr/bin/env python3
"""
TCP Web Dashboard - Browser-based progress monitoring for consortium
Provides real-time web interface for tracking TCP analysis progress
"""

import os
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
from typing import Dict, Any

class TCPDashboardHandler(BaseHTTPRequestHandler):
    def __init__(self, progress_monitor, *args, **kwargs):
        self.progress_monitor = progress_monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/progress':
            self.serve_progress_api()
        elif parsed_path.path == '/api/live':
            self.serve_live_data()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve main dashboard HTML"""
        html = self.generate_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_progress_api(self):
        """Serve progress data as JSON API"""
        report = self.progress_monitor.generate_progress_report()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(report, indent=2).encode())
    
    def serve_live_data(self):
        """Serve live data for real-time updates"""
        progress, quality = self.progress_monitor.calculate_metrics()
        
        live_data = {
            "timestamp": datetime.now().isoformat(),
            "completion_percentage": (progress.analyzed_commands / progress.total_commands) * 100,
            "analyzed_commands": progress.analyzed_commands,
            "total_commands": progress.total_commands,
            "processing_rate": progress.processing_rate,
            "accuracy_rate": progress.accuracy_rate,
            "eta_hours": progress.eta_hours,
            "risk_distribution": dict(quality.risk_distribution)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(live_data).encode())
    
    def generate_dashboard_html(self) -> str:
        """Generate comprehensive dashboard HTML"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TCP Consortium Progress Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .progress-bar {
            width: 100%;
            height: 25px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #81C784);
            border-radius: 15px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #B0BEC5;
        }
        
        .metric-value {
            font-weight: bold;
            color: white;
        }
        
        .risk-chart {
            display: grid;
            gap: 8px;
            margin-top: 15px;
        }
        
        .risk-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }
        
        .risk-critical { border-left: 4px solid #F44336; }
        .risk-high_risk { border-left: 4px solid #FF9800; }
        .risk-medium_risk { border-left: 4px solid #FFC107; }
        .risk-low_risk { border-left: 4px solid #4CAF50; }
        .risk-safe { border-left: 4px solid #2196F3; }
        .risk-unknown { border-left: 4px solid #9E9E9E; }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
            margin-right: 10px;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .large-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #FFD700;
            text-align: center;
            margin: 10px 0;
        }
        
        .update-time {
            text-align: center;
            color: #B0BEC5;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        .refresh-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px;
            transition: transform 0.2s;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 TCP Consortium Progress Dashboard</h1>
            <p>Real-time monitoring of Tool Capability Protocol analysis</p>
            <div>
                <div class="status-indicator"></div>
                <span>Live Monitoring Active</span>
            </div>
        </div>
        
        <div class="grid">
            <!-- Overall Progress -->
            <div class="card">
                <h3>📊 Overall Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="main-progress" style="width: 0%">0%</div>
                </div>
                <div class="metric">
                    <span class="metric-label">Analyzed Commands</span>
                    <span class="metric-value" id="analyzed-count">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Commands</span>
                    <span class="metric-value" id="total-count">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Remaining</span>
                    <span class="metric-value" id="remaining-count">-</span>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h3>⚡ Performance</h3>
                <div class="large-number" id="processing-rate">-</div>
                <p style="text-align: center; color: #B0BEC5;">commands/minute</p>
                <div class="metric">
                    <span class="metric-label">ETA</span>
                    <span class="metric-value" id="eta">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Accuracy Rate</span>
                    <span class="metric-value" id="accuracy">-</span>
                </div>
            </div>
            
            <!-- Risk Distribution -->
            <div class="card">
                <h3>⚠️ Risk Distribution</h3>
                <div class="risk-chart" id="risk-chart">
                    <!-- Risk items will be populated by JavaScript -->
                </div>
            </div>
            
            <!-- System Status -->
            <div class="card">
                <h3>🔧 System Status</h3>
                <div class="metric">
                    <span class="metric-label">Last Update</span>
                    <span class="metric-value" id="last-update">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Monitoring Duration</span>
                    <span class="metric-value" id="monitoring-duration">-</span>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Now</button>
                    <button class="refresh-btn" onclick="downloadReport()">📊 Download Report</button>
                </div>
            </div>
        </div>
        
        <div class="update-time" id="update-status">
            Connecting to live data...
        </div>
    </div>

    <script>
        let updateInterval;
        
        function formatNumber(num) {
            return num.toLocaleString();
        }
        
        function formatDuration(hours) {
            if (hours < 1) {
                return Math.round(hours * 60) + ' minutes';
            } else if (hours < 24) {
                return hours.toFixed(1) + ' hours';
            } else {
                return Math.round(hours / 24) + ' days';
            }
        }
        
        function updateDashboard(data) {
            // Progress
            const completion = data.completion_percentage || 0;
            document.getElementById('main-progress').style.width = completion + '%';
            document.getElementById('main-progress').textContent = completion.toFixed(1) + '%';
            
            document.getElementById('analyzed-count').textContent = formatNumber(data.analyzed_commands || 0);
            document.getElementById('total-count').textContent = formatNumber(data.total_commands || 0);
            document.getElementById('remaining-count').textContent = formatNumber((data.total_commands || 0) - (data.analyzed_commands || 0));
            
            // Performance
            document.getElementById('processing-rate').textContent = (data.processing_rate || 0).toFixed(1);
            document.getElementById('eta').textContent = data.eta_hours < 100 ? formatDuration(data.eta_hours) : 'TBD';
            document.getElementById('accuracy').textContent = (data.accuracy_rate || 0).toFixed(1) + '%';
            
            // Risk Distribution
            const riskChart = document.getElementById('risk-chart');
            riskChart.innerHTML = '';
            
            const riskData = data.risk_distribution || {};
            const riskOrder = ['CRITICAL', 'HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK', 'SAFE', 'UNKNOWN'];
            
            riskOrder.forEach(risk => {
                const count = riskData[risk] || 0;
                if (count > 0) {
                    const percentage = ((count / (data.analyzed_commands || 1)) * 100).toFixed(1);
                    const riskItem = document.createElement('div');
                    riskItem.className = `risk-item risk-${risk.toLowerCase()}`;
                    riskItem.innerHTML = `
                        <span>${risk.replace('_', ' ')}</span>
                        <span>${formatNumber(count)} (${percentage}%)</span>
                    `;
                    riskChart.appendChild(riskItem);
                }
            });
            
            // Status
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            document.getElementById('update-status').textContent = 
                `Last updated: ${new Date().toLocaleString()} | Auto-refresh every 30s`;
        }
        
        function refreshData() {
            fetch('/api/live')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('update-status').textContent = 
                        'Error connecting to server - retrying...';
                });
        }
        
        function downloadReport() {
            window.open('/api/progress', '_blank');
        }
        
        // Start auto-refresh
        function startAutoRefresh() {
            refreshData(); // Initial load
            updateInterval = setInterval(refreshData, 30000); // Every 30 seconds
        }
        
        // Start when page loads
        document.addEventListener('DOMContentLoaded', startAutoRefresh);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
        '''
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass

class TCPWebDashboard:
    def __init__(self, progress_monitor, port=8080):
        self.progress_monitor = progress_monitor
        self.port = port
        self.server = None
        
    def create_handler(self):
        """Create request handler with progress monitor"""
        def handler(*args, **kwargs):
            return TCPDashboardHandler(self.progress_monitor, *args, **kwargs)
        return handler
    
    def start_server(self):
        """Start the web dashboard server"""
        handler = self.create_handler()
        self.server = HTTPServer(('localhost', self.port), handler)
        
        print(f"🌐 TCP Web Dashboard starting on http://localhost:{self.port}")
        print("🔬 Dashboard features:")
        print("   • Real-time progress monitoring")
        print("   • Live performance metrics")
        print("   • Risk distribution visualization")
        print("   • JSON API endpoints")
        print(f"📊 API endpoints:")
        print(f"   • http://localhost:{self.port}/api/progress")
        print(f"   • http://localhost:{self.port}/api/live")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Web dashboard stopped")
            self.server.shutdown()

def main():
    import argparse
    from tcp_progress_monitor import TCPProgressMonitor
    
    parser = argparse.ArgumentParser(description="TCP Web Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Web server port")
    parser.add_argument("--data-dir", default="data", help="Analysis data directory")
    parser.add_argument("--host", default="localhost", help="Server host")
    
    args = parser.parse_args()
    
    # Create progress monitor
    monitor = TCPProgressMonitor(args.data_dir)
    
    # Create and start web dashboard
    dashboard = TCPWebDashboard(monitor, args.port)
    dashboard.start_server()

if __name__ == "__main__":
    main()