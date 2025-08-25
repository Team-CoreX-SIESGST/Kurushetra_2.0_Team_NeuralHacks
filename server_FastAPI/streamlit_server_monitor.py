#!/usr/bin/env python3
"""
🚀 OmniSearch AI - Streamlit Server Monitor & API Demo
Complete server monitoring and API testing dashboard with live logs.
"""

import streamlit as st
import requests
import json
import time
import subprocess
import threading
import queue
import psutil
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Page configuration
st.set_page_config(
    page_title="OmniSearch AI Monitor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
BASE_URL = "http://127.0.0.1:8000"
SERVER_PROCESS = None
LOG_QUEUE = queue.Queue()

class ServerManager:
    """Manages FastAPI server lifecycle."""
    
    def __init__(self):
        self.process = None
        self.is_running = False
        
    def start_server(self, safe_demo=True, log_queue=None):
        """Start the FastAPI server with optional safe demo mode."""
        if self.is_running:
            return True, "Server is already running"
            
        try:
            # Prepare server command
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--log-level", "info"
            ]
            
            if not safe_demo:
                cmd.append("--reload")
            
            # Start server process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start log monitoring thread
            if log_queue:
                log_thread = threading.Thread(
                    target=self._monitor_logs,
                    args=(self.process.stdout, log_queue),
                    daemon=True
                )
                log_thread.start()
            
            self.is_running = True
            return True, "Server started successfully"
            
        except Exception as e:
            return False, f"Failed to start server: {str(e)}"
    
    def stop_server(self):
        """Stop the FastAPI server."""
        if self.process:
            self.process.terminate()
            self.process = None
            self.is_running = False
            return True, "Server stopped successfully"
        return False, "No server process to stop"
    
    def _monitor_logs(self, stdout, log_queue):
        """Monitor server logs in a separate thread."""
        try:
            for line in iter(stdout.readline, ''):
                if line:
                    log_queue.put({
                        'timestamp': datetime.now(),
                        'message': line.strip()
                    })
        except Exception as e:
            log_queue.put({
                'timestamp': datetime.now(),
                'message': f"Log monitoring error: {str(e)}"
            })

class APITester:
    """Comprehensive API testing functionality."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.test_results = {}
        
    def test_endpoint(self, method: str, endpoint: str, data: dict = None, 
                     headers: dict = None, timeout: int = 10) -> Tuple[bool, dict]:
        """Test a single API endpoint."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            response_time = time.time() - start_time
            
            return True, {
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code < 400,
                "response_data": response.text[:500],  # Truncate long responses
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection Error - Server may not be running"}
        except requests.exceptions.Timeout:
            return False, {"error": "Timeout Error"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_all_endpoints(self) -> Dict[str, List[Tuple]]:
        """Get all API endpoints organized by category."""
        return {
            "Basic": [
                ("GET", "/", "Root endpoint"),
                ("GET", "/health", "Health check"),
                ("GET", "/docs", "API documentation"),
                ("GET", "/redoc", "Alternative API docs"),
            ],
            "Search": [
                ("POST", "/api/v1/search", "Full search with Gemini"),
                ("GET", "/api/v1/search/simple?q=test", "Simple search"),
                ("GET", "/api/v1/search/stats/demo-workspace", "Search statistics"),
                ("POST", "/api/v1/search/advanced", "Advanced search"),
            ],
            "Files": [
                ("GET", "/api/v1/files/demo-workspace", "List workspace files"),
                ("GET", "/api/v1/file/test-file-id", "Get file info"),
                ("GET", "/api/v1/file/test-file-id/download", "Download file"),
                ("GET", "/api/v1/file/test-file-id/metadata", "Get file metadata"),
            ],
            "Uploads": [
                ("GET", "/api/v1/uploads/demo-workspace", "List workspace uploads"),
                ("GET", "/api/v1/upload/status/test-file-id", "Get upload status"),
            ],
            "Enhanced Documents": [
                ("GET", "/api/v1/enhanced-documents/", "Enhanced documents info"),
                ("GET", "/api/v1/enhanced-documents/health", "Enhanced documents health"),
                ("GET", "/api/v1/enhanced-documents/formats/supported", "Supported formats"),
            ],
            "Users": [
                ("GET", "/api/users", "List users"),
                ("GET", "/api/users/profile", "Get user profile"),
            ]
        }
    
    def run_all_tests(self, progress_callback=None) -> Dict:
        """Run all API tests and return comprehensive results."""
        all_endpoints = self.get_all_endpoints()
        results = {}
        total_tests = sum(len(endpoints) for endpoints in all_endpoints.values())
        current_test = 0
        
        for category, endpoints in all_endpoints.items():
            results[category] = []
            
            for method, endpoint, description in endpoints:
                current_test += 1
                if progress_callback:
                    progress_callback(current_test / total_tests, f"Testing {description}")
                
                # Prepare test data for POST requests
                data = None
                if method == "POST":
                    if "search" in endpoint.lower():
                        data = {"workspace_id": "demo", "query": "test query", "top_k": 5}
                    elif "advanced" in endpoint.lower():
                        data = {"query": "test", "filters": {}, "workspace_id": "demo"}
                
                success, result = self.test_endpoint(method, endpoint, data=data)
                
                results[category].append({
                    "method": method,
                    "endpoint": endpoint,
                    "description": description,
                    "success": success,
                    "result": result
                })
        
        return results

def get_system_stats():
    """Get current system resource usage."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available": psutil.virtual_memory().available / (1024**3),  # GB
        "disk_usage": psutil.disk_usage('.').percent,
        "timestamp": datetime.now()
    }

def main():
    """Main Streamlit application."""
    
    # Initialize session state
    if 'server_manager' not in st.session_state:
        st.session_state.server_manager = ServerManager()
    
    if 'api_tester' not in st.session_state:
        st.session_state.api_tester = APITester(BASE_URL)
    
    if 'system_stats' not in st.session_state:
        st.session_state.system_stats = []
    
    if 'server_logs' not in st.session_state:
        st.session_state.server_logs = []
    
    if 'last_test_results' not in st.session_state:
        st.session_state.last_test_results = None
    
    # Header
    st.title("🚀 OmniSearch AI - Server Monitor & API Demo")
    st.markdown("Complete FastAPI server monitoring and API testing dashboard")
    
    # Sidebar - Server Controls
    with st.sidebar:
        st.header("🎛️ Server Controls")
        
        # Server status
        server_running = st.session_state.server_manager.is_running
        status_color = "🟢" if server_running else "🔴"
        st.markdown(f"**Server Status:** {status_color} {'Running' if server_running else 'Stopped'}")
        
        # Server control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Server", disabled=server_running):
                safe_demo = st.checkbox("Safe Demo Mode", value=True, key="safe_demo_start")
                success, message = st.session_state.server_manager.start_server(
                    safe_demo=safe_demo,
                    log_queue=LOG_QUEUE
                )
                if success:
                    st.success(message)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("🛑 Stop Server", disabled=not server_running):
                success, message = st.session_state.server_manager.stop_server()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.divider()
        
        # System Resources
        st.header("📊 System Resources")
        current_stats = get_system_stats()
        st.session_state.system_stats.append(current_stats)
        
        # Keep only last 50 measurements
        if len(st.session_state.system_stats) > 50:
            st.session_state.system_stats = st.session_state.system_stats[-50:]
        
        # Display current stats
        st.metric("CPU Usage", f"{current_stats['cpu_percent']:.1f}%")
        st.metric("Memory Usage", f"{current_stats['memory_percent']:.1f}%")
        st.metric("Available RAM", f"{current_stats['memory_available']:.1f}GB")
        st.metric("Disk Usage", f"{current_stats['disk_usage']:.1f}%")
        
        st.divider()
        
        # Auto-refresh controls
        st.header("🔄 Auto-refresh")
        auto_refresh = st.checkbox("Enable auto-refresh", value=True)
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh interval",
                [5, 10, 15, 30, 60],
                index=1,
                format_func=lambda x: f"{x} seconds"
            )
            time.sleep(refresh_interval)
            st.rerun()
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🧪 API Testing", "📋 Server Logs", "📈 Monitoring"])
    
    with tab1:
        st.header("🎯 Dashboard Overview")
        
        # Quick status cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Server Status",
                "🟢 Online" if server_running else "🔴 Offline",
                delta="Running" if server_running else "Stopped"
            )
        
        with col2:
            # Try to get server health
            if server_running:
                try:
                    response = requests.get(f"{BASE_URL}/health", timeout=5)
                    health_status = "✅ Healthy" if response.status_code == 200 else "⚠️ Issues"
                except:
                    health_status = "❌ Unreachable"
            else:
                health_status = "⭕ N/A"
            
            st.metric("API Health", health_status)
        
        with col3:
            st.metric("CPU", f"{current_stats['cpu_percent']:.1f}%")
        
        with col4:
            st.metric("Memory", f"{current_stats['memory_percent']:.1f}%")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌐 Open API Docs"):
                if server_running:
                    st.markdown(f"[Open API Documentation]({BASE_URL}/docs)")
                else:
                    st.warning("Please start the server first")
        
        with col2:
            if st.button("📖 Open ReDoc"):
                if server_running:
                    st.markdown(f"[Open ReDoc Documentation]({BASE_URL}/redoc)")
                else:
                    st.warning("Please start the server first")
        
        with col3:
            if st.button("🔍 Quick API Test"):
                if server_running:
                    try:
                        response = requests.get(f"{BASE_URL}/", timeout=5)
                        st.success(f"✅ API responding: {response.status_code}")
                        st.json(response.json())
                    except Exception as e:
                        st.error(f"❌ API test failed: {str(e)}")
                else:
                    st.warning("Please start the server first")
    
    with tab2:
        st.header("🧪 API Testing Suite")
        
        if not server_running:
            st.warning("⚠️ Server is not running. Please start the server to run API tests.")
            return
        
        # Test controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Run All API Tests", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                # Run tests
                results = st.session_state.api_tester.run_all_tests(update_progress)
                st.session_state.last_test_results = results
                
                progress_bar.empty()
                status_text.empty()
                st.success("🎉 All API tests completed!")
        
        with col2:
            if st.button("📊 Test Summary Only"):
                if st.session_state.last_test_results:
                    # Show summary without running tests again
                    st.info("Showing last test results")
                else:
                    st.warning("No test results available. Run tests first.")
        
        # Display test results
        if st.session_state.last_test_results:
            st.subheader("📋 Test Results")
            
            # Overall summary
            total_tests = 0
            passed_tests = 0
            failed_tests = 0
            
            for category, tests in st.session_state.last_test_results.items():
                total_tests += len(tests)
                for test in tests:
                    if test['success'] and test['result'].get('success', False):
                        passed_tests += 1
                    else:
                        failed_tests += 1
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tests", total_tests)
            with col2:
                st.metric("✅ Passed", passed_tests)
            with col3:
                st.metric("❌ Failed", failed_tests)
            with col4:
                success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Detailed results by category
            for category, tests in st.session_state.last_test_results.items():
                with st.expander(f"📂 {category} ({len(tests)} tests)"):
                    for test in tests:
                        status_icon = "✅" if (test['success'] and test['result'].get('success', False)) else "❌"
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"{status_icon} **{test['description']}**")
                            st.code(f"{test['method']} {test['endpoint']}")
                        
                        with col2:
                            if test['success']:
                                status_code = test['result'].get('status_code', 'Unknown')
                                response_time = test['result'].get('response_time', 0)
                                st.write(f"Status: {status_code}")
                                st.write(f"Time: {response_time:.3f}s")
                            else:
                                st.write("❌ Failed")
                        
                        # Show response details
                        if test['success'] and st.checkbox(f"Show details - {test['description']}", key=f"details_{category}_{test['endpoint']}"):
                            st.json(test['result'])
    
    with tab3:
        st.header("📋 Server Logs")
        
        # Collect logs from queue
        while not LOG_QUEUE.empty():
            try:
                log_entry = LOG_QUEUE.get_nowait()
                st.session_state.server_logs.append(log_entry)
            except queue.Empty:
                break
        
        # Keep only last 100 log entries
        if len(st.session_state.server_logs) > 100:
            st.session_state.server_logs = st.session_state.server_logs[-100:]
        
        # Log controls
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🗑️ Clear Logs"):
                st.session_state.server_logs = []
                st.success("Logs cleared")
        
        with col2:
            auto_scroll = st.checkbox("Auto-scroll", value=True)
        
        with col3:
            log_filter = st.selectbox(
                "Filter logs",
                ["All", "ERROR", "WARNING", "INFO", "DEBUG"],
                index=0
            )
        
        # Display logs
        if st.session_state.server_logs:
            st.subheader(f"📜 Recent Logs ({len(st.session_state.server_logs)} entries)")
            
            # Filter logs
            filtered_logs = st.session_state.server_logs
            if log_filter != "All":
                filtered_logs = [
                    log for log in st.session_state.server_logs
                    if log_filter.lower() in log['message'].lower()
                ]
            
            # Display in reverse chronological order
            log_container = st.container()
            with log_container:
                for log_entry in reversed(filtered_logs[-50:]):  # Show last 50 filtered logs
                    timestamp = log_entry['timestamp'].strftime("%H:%M:%S")
                    message = log_entry['message']
                    
                    # Color code based on log level
                    if "ERROR" in message.upper():
                        st.error(f"[{timestamp}] {message}")
                    elif "WARNING" in message.upper():
                        st.warning(f"[{timestamp}] {message}")
                    elif "INFO" in message.upper():
                        st.info(f"[{timestamp}] {message}")
                    else:
                        st.text(f"[{timestamp}] {message}")
        else:
            st.info("No logs available. Start the server to see logs.")
    
    with tab4:
        st.header("📈 System Monitoring")
        
        if len(st.session_state.system_stats) > 1:
            # Create monitoring charts
            df = pd.DataFrame(st.session_state.system_stats)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # CPU and Memory usage over time
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('CPU Usage (%)', 'Memory Usage (%)'),
                vertical_spacing=0.1
            )
            
            # CPU chart
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['cpu_percent'],
                    mode='lines+markers',
                    name='CPU',
                    line=dict(color='#FF6B6B')
                ),
                row=1, col=1
            )
            
            # Memory chart
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['memory_percent'],
                    mode='lines+markers',
                    name='Memory',
                    line=dict(color='#4ECDC4')
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                title_text="System Resource Usage Over Time"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Resource usage statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 CPU Statistics")
                st.metric("Average CPU", f"{df['cpu_percent'].mean():.1f}%")
                st.metric("Max CPU", f"{df['cpu_percent'].max():.1f}%")
                st.metric("Min CPU", f"{df['cpu_percent'].min():.1f}%")
            
            with col2:
                st.subheader("💾 Memory Statistics")
                st.metric("Average Memory", f"{df['memory_percent'].mean():.1f}%")
                st.metric("Max Memory", f"{df['memory_percent'].max():.1f}%")
                st.metric("Min Available RAM", f"{df['memory_available'].min():.1f}GB")
        else:
            st.info("Collecting system data... Please wait a few seconds.")

if __name__ == "__main__":
    main()
