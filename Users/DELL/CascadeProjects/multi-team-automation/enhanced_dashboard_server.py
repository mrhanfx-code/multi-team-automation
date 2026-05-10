#!/usr/bin/env python3
"""
MFM Corporation - Enhanced Online Dashboard Server
Full-featured dashboard with remote monitoring and control capabilities
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import websockets

# Add src to path
import sys
sys.path.append('src')
sys.path.append('.')

from unified_system import MultiTeamAutomationSystem
from src.supabase_client import get_supabase_manager
from src.exceptions import MFMException
from src.config_validator import validate_environment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# FastAPI app
app = FastAPI(
    title="MFM Corporation Dashboard",
    description="Multi-Team Automation System Remote Dashboard",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
automation_system = None
supabase_manager = None
active_connections: List[WebSocket] = []

# Pydantic models
class TeamStatus(BaseModel):
    name: str
    status: str
    active_tasks: int
    completed_tasks: int
    performance_score: float
    last_activity: str

class WorkflowRequest(BaseModel):
    name: str
    description: str
    team: str
    priority: int = 1
    parameters: Dict[str, Any] = {}

class ControlCommand(BaseModel):
    command: str
    target: str
    parameters: Dict[str, Any] = {}

class SystemMetrics(BaseModel):
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    total_tasks: int
    active_tasks: int
    system_health: str
    uptime: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the dashboard server"""
    global automation_system, supabase_manager
    
    try:
        logger.info("🚀 Starting MFM Corporation Dashboard Server")
        
        # Validate environment
        validation_results = validate_environment()
        if not validation_results["valid"]:
            logger.error("❌ Environment validation failed")
            return
        
        # Initialize Supabase
        try:
            supabase_manager = await get_supabase_manager()
            logger.info("✅ Supabase manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
        
        # Initialize automation system
        try:
            automation_system = MultiTeamAutomationSystem()
            await automation_system.initialize()
            logger.info("✅ Automation system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize automation system: {e}")
        
        logger.info("🎯 Dashboard server ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global automation_system, supabase_manager
    
    try:
        if automation_system:
            logger.info("🔄 Shutting down automation system")
            # Add cleanup if needed
        
        if supabase_manager:
            await supabase_manager.close()
        
        logger.info("🔌 Dashboard server shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        # For now, just validate token format
        if not credentials.credentials:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # In production, validate JWT token here
        return {"user_id": "demo_user", "username": "admin"}
        
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Main dashboard page"""
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MFM Corporation Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .team-card { transition: all 0.3s ease; }
        .team-card:hover { transform: translateY(-2px); }
        .status-online { background-color: #10b981; }
        .status-busy { background-color: #f59e0b; }
        .status-offline { background-color: #ef4444; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <header class="bg-white rounded-lg shadow-md p-6 mb-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold text-gray-800">MFM Corporation Dashboard</h1>
                    <p class="text-gray-600">Multi-Team Automation System v3.0.0</p>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-500">System Status</div>
                    <div id="system-status" class="text-lg font-semibold text-green-600">Online</div>
                </div>
            </div>
        </header>

        <!-- System Overview -->
        <section class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">System Overview</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <div class="text-2xl font-bold text-blue-600" id="total-workflows">0</div>
                    <div class="text-sm text-gray-600">Total Workflows</div>
                </div>
                <div class="bg-green-50 p-4 rounded-lg">
                    <div class="text-2xl font-bold text-green-600" id="active-workflows">0</div>
                    <div class="text-sm text-gray-600">Active Workflows</div>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <div class="text-2xl font-bold text-yellow-600" id="total-tasks">0</div>
                    <div class="text-sm text-gray-600">Total Tasks</div>
                </div>
                <div class="bg-purple-50 p-4 rounded-lg">
                    <div class="text-2xl font-bold text-purple-600" id="system-health">100%</div>
                    <div class="text-sm text-gray-600">System Health</div>
                </div>
            </div>
        </section>

        <!-- Teams Status -->
        <section class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Teams Status</h2>
            <div id="teams-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Team cards will be inserted here -->
            </div>
        </section>

        <!-- Control Panel -->
        <section class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Control Panel</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h3 class="font-semibold mb-2">Start Workflow</h3>
                    <select id="workflow-team" class="w-full p-2 border rounded mb-2">
                        <option value="">Select Team</option>
                        <option value="research">Research Team</option>
                        <option value="planning">Planning Team</option>
                        <option value="development">Development Team</option>
                        <option value="management">Management Team</option>
                        <option value="legal">Legal Team</option>
                        <option value="operations">Operations Manager</option>
                    </select>
                    <input type="text" id="workflow-name" placeholder="Workflow Name" class="w-full p-2 border rounded mb-2">
                    <textarea id="workflow-description" placeholder="Description" class="w-full p-2 border rounded mb-2"></textarea>
                    <button onclick="startWorkflow()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Start Workflow</button>
                </div>
                <div>
                    <h3 class="font-semibold mb-2">System Controls</h3>
                    <button onclick="refreshData()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mr-2">Refresh Data</button>
                    <button onclick="getSystemMetrics()" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 mr-2">System Metrics</button>
                    <button onclick="emergencyStop()" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Emergency Stop</button>
                </div>
            </div>
        </section>

        <!-- Real-time Logs -->
        <section class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4">Real-time Activity</h2>
            <div id="logs-container" class="bg-gray-50 p-4 rounded-lg h-64 overflow-y-auto font-mono text-sm">
                <!-- Logs will appear here -->
            </div>
        </section>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        // API functions
        async function fetchTeamsStatus() {
            try {
                const response = await fetch('/api/teams/status');
                const teams = await response.json();
                displayTeams(teams);
            } catch (error) {
                console.error('Error fetching teams:', error);
            }
        }

        async function fetchSystemMetrics() {
            try {
                const response = await fetch('/api/system/metrics');
                const metrics = await response.json();
                updateSystemOverview(metrics);
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }

        async function startWorkflow() {
            const team = document.getElementById('workflow-team').value;
            const name = document.getElementById('workflow-name').value;
            const description = document.getElementById('workflow-description').value;

            if (!team || !name) {
                alert('Please select a team and enter a workflow name');
                return;
            }

            try {
                const response = await fetch('/api/workflows/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer demo_token'
                    },
                    body: JSON.stringify({
                        name: name,
                        description: description,
                        team: team
                    })
                });

                const result = await response.json();
                if (result.success) {
                    addLog(`✅ Workflow started: ${name}`, 'success');
                    refreshData();
                } else {
                    addLog(`❌ Failed to start workflow: ${result.error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ Error starting workflow: ${error}`, 'error');
            }
        }

        async function refreshData() {
            addLog('🔄 Refreshing dashboard data...', 'info');
            await fetchTeamsStatus();
            await fetchSystemMetrics();
        }

        async function getSystemMetrics() {
            const metrics = await fetchSystemMetrics();
            addLog('📊 System metrics retrieved', 'info');
        }

        async function emergencyStop() {
            if (confirm('Are you sure you want to emergency stop all workflows?')) {
                try {
                    const response = await fetch('/api/system/emergency-stop', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer demo_token'
                        }
                    });

                    const result = await response.json();
                    if (result.success) {
                        addLog('🚨 Emergency stop executed', 'warning');
                    } else {
                        addLog(`❌ Emergency stop failed: ${result.error}`, 'error');
                    }
                } catch (error) {
                    addLog(`❌ Error during emergency stop: ${error}`, 'error');
                }
            }
        }

        // Display functions
        function displayTeams(teams) {
            const container = document.getElementById('teams-container');
            container.innerHTML = '';

            teams.forEach(team => {
                const statusColor = team.status === 'active' ? 'green' : team.status === 'busy' ? 'yellow' : 'red';
                const card = `
                    <div class="team-card bg-gray-50 p-4 rounded-lg border-l-4 border-${statusColor}-500">
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="font-semibold text-lg">${team.name}</h3>
                            <div class="w-3 h-3 bg-${statusColor}-500 rounded-full"></div>
                        </div>
                        <div class="text-sm text-gray-600 space-y-1">
                            <div>Status: ${team.status}</div>
                            <div>Active Tasks: ${team.active_tasks}</div>
                            <div>Completed: ${team.completed_tasks}</div>
                            <div>Performance: ${team.performance_score}%</div>
                            <div>Last Activity: ${team.last_activity}</div>
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            });
        }

        function updateSystemOverview(metrics) {
            document.getElementById('total-workflows').textContent = metrics.total_workflows;
            document.getElementById('active-workflows').textContent = metrics.active_workflows;
            document.getElementById('total-tasks').textContent = metrics.total_tasks;
            document.getElementById('system-health').textContent = metrics.system_health;
        }

        function addLog(message, type = 'info') {
            const container = document.getElementById('logs-container');
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? 'text-red-600' : type === 'success' ? 'text-green-600' : type === 'warning' ? 'text-yellow-600' : 'text-gray-600';
            
            const logEntry = `<div class="${color}">[${timestamp}] ${message}</div>`;
            container.innerHTML = logEntry + container.innerHTML;
            
            // Keep only last 50 entries
            const entries = container.children;
            if (entries.length > 50) {
                container.removeChild(entries[entries.length - 1]);
            }
        }

        function updateDashboard(data) {
            // Handle real-time updates from WebSocket
            addLog(`📡 Real-time update: ${data.type}`, 'info');
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            addLog('🚀 Dashboard initialized', 'success');
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
    """
    return dashboard_html

# API Endpoints

@app.get("/api/teams/status")
async def get_teams_status(current_user: dict = Depends(get_current_user)):
    """Get status of all teams"""
    try:
        if not automation_system:
            raise HTTPException(status_code=503, detail="Automation system not available")
        
        teams_status = []
        teams = [
            {"name": "Research Team", "id": "research"},
            {"name": "Planning Team", "id": "planning"},
            {"name": "Development Team", "id": "development"},
            {"name": "Management Team", "id": "management"},
            {"name": "Legal Team", "id": "legal"},
            {"name": "Operations Manager", "id": "operations"},
            {"name": "Innovation Team", "id": "innovation"},
            {"name": "Marketing Team", "id": "marketing"},
            {"name": "Media Team", "id": "media"},
            {"name": "Technology Team", "id": "technology"},
            {"name": "Market Intelligence", "id": "market_intelligence"},
            {"name": "MCP/LLM Team", "id": "mcp_llm"},
            {"name": "General Manager", "id": "general_manager"}
        ]
        
        for team in teams:
            # Simulate team status (in real implementation, get from system)
            teams_status.append({
                "name": team["name"],
                "status": "active",
                "active_tasks": 2,
                "completed_tasks": 15,
                "performance_score": 95,
                "last_activity": datetime.now().strftime("%H:%M:%S")
            })
        
        return teams_status
        
    except Exception as e:
        logger.error(f"Error getting teams status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/metrics")
async def get_system_metrics(current_user: dict = Depends(get_current_user)):
    """Get system metrics"""
    try:
        # Simulate system metrics (in real implementation, get from system)
        metrics = SystemMetrics(
            total_workflows=25,
            active_workflows=3,
            completed_workflows=20,
            failed_workflows=2,
            total_tasks=150,
            active_tasks=12,
            system_health="98%",
            uptime="2 days, 14 hours"
        )
        
        return metrics.dict()
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/start")
async def start_workflow(workflow: WorkflowRequest, current_user: dict = Depends(get_current_user)):
    """Start a new workflow"""
    try:
        if not automation_system:
            raise HTTPException(status_code=503, detail="Automation system not available")
        
        # In real implementation, start workflow
        logger.info(f"Starting workflow: {workflow.name} for team: {workflow.team}")
        
        return {
            "success": True,
            "workflow_id": f"workflow_{datetime.now().timestamp()}",
            "message": f"Workflow '{workflow.name}' started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/system/emergency-stop")
async def emergency_stop(current_user: dict = Depends(get_current_user)):
    """Emergency stop all workflows"""
    try:
        if not automation_system:
            raise HTTPException(status_code=503, detail="Automation system not available")
        
        # In real implementation, stop all workflows
        logger.warning("🚨 Emergency stop activated!")
        
        return {
            "success": True,
            "message": "Emergency stop executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error during emergency stop: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/control/command")
async def execute_command(command: ControlCommand, current_user: dict = Depends(get_current_user)):
    """Execute control command"""
    try:
        if not automation_system:
            raise HTTPException(status_code=503, detail="Automation system not available")
        
        # In real implementation, execute command
        logger.info(f"Executing command: {command.command} on {command.target}")
        
        return {
            "success": True,
            "message": f"Command '{command.command}' executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "automation_system": automation_system is not None,
        "supabase_connected": supabase_manager is not None
    }

@app.get("/api/logs")
async def get_logs(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Get system logs"""
    try:
        # In real implementation, get logs from system
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Dashboard server running",
                "source": "dashboard"
            }
        ]
        
        return {"logs": logs[:limit]}
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Run server
if __name__ == "__main__":
    print("🚀 Starting MFM Corporation Enhanced Dashboard Server")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("📋 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "enhanced_dashboard_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
