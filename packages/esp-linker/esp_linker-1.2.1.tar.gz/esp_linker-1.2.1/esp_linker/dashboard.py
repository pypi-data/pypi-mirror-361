"""
ESP-Linker Web Dashboard
(c) 2025 SK Raihan / SKR Electronics Lab

Simple web dashboard for monitoring and controlling ESP-Linker devices.
"""

import json
import threading
import webbrowser
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from .device_manager import get_device_manager
from .espboard import ESPBoard


class Dashboard:
    """Simple web dashboard for ESP-Linker devices"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.app = None
        self.manager = get_device_manager()
        
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for the dashboard. Install with: pip install flask")
    
    def create_app(self):
        """Create Flask application"""
        self.app = Flask(__name__)
        
        # Main dashboard page
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML)
        
        # API endpoints
        @self.app.route('/api/devices')
        def api_devices():
            devices = self.manager.list_devices()
            return jsonify([device.to_dict() for device in devices])
        
        @self.app.route('/api/devices/discover', methods=['POST'])
        def api_discover():
            try:
                new_devices = self.manager.discover_and_add_devices()
                return jsonify({
                    'success': True,
                    'new_devices': len(new_devices),
                    'devices': [device.to_dict() for device in new_devices]
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/devices/<device_ip>/status')
        def api_device_status(device_ip):
            try:
                device = self.manager.get_device(device_ip)
                if not device:
                    return jsonify({'error': 'Device not found'}), 404
                
                board = ESPBoard(ip=device.ip, timeout=3)
                status = board.status()
                board.close()
                
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/devices/<device_ip>/gpio', methods=['POST'])
        def api_gpio_control(device_ip):
            try:
                device = self.manager.get_device(device_ip)
                if not device:
                    return jsonify({'error': 'Device not found'}), 404
                
                data = request.json
                action = data.get('action')
                pin = data.get('pin')
                value = data.get('value')
                
                board = ESPBoard(ip=device.ip, timeout=3)
                
                if action == 'write':
                    board.write(pin, value)
                elif action == 'read':
                    value = board.read(pin)
                elif action == 'pwm':
                    board.pwm(pin, value)
                
                board.close()
                
                return jsonify({'success': True, 'value': value})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/statistics')
        def api_statistics():
            stats = self.manager.get_statistics()
            return jsonify(stats)
        
        return self.app
    
    def run(self, debug: bool = False, open_browser: bool = True):
        """Run the dashboard server"""
        if not self.app:
            self.create_app()
        
        if open_browser:
            # Open browser after a short delay
            def open_browser_delayed():
                import time
                time.sleep(1)
                webbrowser.open(f'http://{self.host}:{self.port}')
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        print(f"[*] ESP-Linker Dashboard starting at http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop the dashboard")
        
        try:
            self.app.run(host=self.host, port=self.port, debug=debug)
        except KeyboardInterrupt:
            print("\n[!] Dashboard stopped")


# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP-Linker Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .device-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .device-card { border-left: 4px solid #3498db; }
        .device-card.online { border-left-color: #27ae60; }
        .device-card.offline { border-left-color: #e74c3c; }
        .status-badge { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .status-online { background: #27ae60; color: white; }
        .status-offline { background: #e74c3c; color: white; }
        .btn { background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-card { text-align: center; padding: 20px; background: linear-gradient(135deg, #3498db, #2980b9); color: white; border-radius: 8px; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .gpio-controls { margin-top: 15px; }
        .gpio-control { margin: 5px 0; }
        .loading { text-align: center; padding: 20px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>[*] ESP-Linker Dashboard</h1>
        <p>Monitor and control your ESP8266 devices</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>[=] Statistics</h2>
            <div id="statistics" class="stats">
                <div class="loading">Loading statistics...</div>
            </div>
        </div>
        
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>[#] Devices</h2>
                <button class="btn btn-success" onclick="discoverDevices()">[?] Discover Devices</button>
            </div>
            <div id="devices" class="device-grid">
                <div class="loading">Loading devices...</div>
            </div>
        </div>
    </div>
    
    <script>
        let devices = [];
        
        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const stats = await response.json();
                
                document.getElementById('statistics').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_devices}</div>
                        <div>Total Devices</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.online_devices}</div>
                        <div>Online</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.offline_devices}</div>
                        <div>Offline</div>
                    </div>
                `;
            } catch (error) {
                document.getElementById('statistics').innerHTML = '<div class="loading">Error loading statistics</div>';
            }
        }
        
        async function loadDevices() {
            try {
                const response = await fetch('/api/devices');
                devices = await response.json();
                
                if (devices.length === 0) {
                    document.getElementById('devices').innerHTML = '<div class="loading">No devices found. Click "Discover Devices" to find ESP-Linker devices.</div>';
                    return;
                }
                
                const devicesHtml = devices.map(device => `
                    <div class="device-card ${device.status}">
                        <h3>${device.name}</h3>
                        <p><strong>IP:</strong> ${device.ip}</p>
                        <p><strong>Firmware:</strong> ${device.firmware_name} v${device.firmware_version}</p>
                        <p><strong>Status:</strong> <span class="status-badge status-${device.status}">${device.status.toUpperCase()}</span></p>
                        <p><strong>Last Seen:</strong> ${new Date(device.last_seen).toLocaleString()}</p>
                        
                        <div class="gpio-controls">
                            <h4>Quick GPIO Control</h4>
                            <div class="gpio-control">
                                <button class="btn" onclick="toggleLED('${device.ip}')">[i] Toggle LED (Pin 2)</button>
                            </div>
                            <div class="gpio-control">
                                <button class="btn" onclick="getStatus('${device.ip}')">[=] Get Status</button>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                document.getElementById('devices').innerHTML = devicesHtml;
            } catch (error) {
                document.getElementById('devices').innerHTML = '<div class="loading">Error loading devices</div>';
            }
        }
        
        async function discoverDevices() {
            const button = event.target;
            button.disabled = true;
            button.textContent = '[?] Discovering...';
            
            try {
                const response = await fetch('/api/devices/discover', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    alert(`Discovery complete! Found ${result.new_devices} new device(s).`);
                    await loadDevices();
                    await loadStatistics();
                } else {
                    alert(`Discovery failed: ${result.error}`);
                }
            } catch (error) {
                alert(`Discovery error: ${error.message}`);
            } finally {
                button.disabled = false;
                button.textContent = '[?] Discover Devices';
            }
        }
        
        async function toggleLED(deviceIP) {
            try {
                // First set pin mode to OUTPUT
                await fetch(`/api/devices/${deviceIP}/gpio`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'set_mode', pin: 2, mode: 'OUTPUT' })
                });
                
                // Toggle LED (built-in LED is inverted)
                const response = await fetch(`/api/devices/${deviceIP}/gpio`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'write', pin: 2, value: Math.random() > 0.5 ? 0 : 1 })
                });
                
                if (response.ok) {
                    alert('LED toggled!');
                } else {
                    alert('Failed to toggle LED');
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }
        
        async function getStatus(deviceIP) {
            try {
                const response = await fetch(`/api/devices/${deviceIP}/status`);
                const status = await response.json();
                
                if (response.ok) {
                    alert(`Device Status:\\nUptime: ${status.uptime/1000} seconds\\nFree Heap: ${status.free_heap} bytes\\nWiFi: ${status.wifi_ssid}`);
                } else {
                    alert(`Error: ${status.error}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }
        
        // Load data on page load
        window.addEventListener('load', () => {
            loadStatistics();
            loadDevices();
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                loadStatistics();
                loadDevices();
            }, 30000);
        });
    </script>
</body>
</html>
"""


def run_dashboard(host: str = 'localhost', port: int = 8080, debug: bool = False):
    """
    Run the ESP-Linker web dashboard.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    dashboard = Dashboard(host, port)
    dashboard.run(debug=debug)
