#!/usr/bin/env python3
"""
MFM Corporation - Dashboard Server
Web server for real-time tracking dashboard
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

# Add src to path
import sys
sys.path.append('src')
sys.path.append('.')

from src.tracking_dashboard import TrackingDashboard
from unified_system import MultiTeamAutomationSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MFM Corporation Dashboard", description="Real-time Multi-Team Automation System Dashboard")

# Global variables
dashboard = None
automation_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize dashboard and automation system"""
    global dashboard, automation_system
    
    logger.info("🚀 Starting MFM Corporation Dashboard Server")
    
    # Initialize automation system
    automation_system = MultiTeamAutomationSystem()
    await automation_system.initialize()
    
    # Initialize tracking dashboard
    dashboard = TrackingDashboard(automation_system.supabase_manager)
    await dashboard.initialize_dashboard()
    
    # Start real-time monitoring
    asyncio.create_task(dashboard.start_real_time_monitoring())
    
    logger.info("✅ Dashboard server started successfully")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    try:
        html_content = await dashboard.generate_real_time_dashboard()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return HTMLResponse(content="<h1>Dashboard Error</h1><p>Unable to load dashboard data</p>")

@app.get("/api/dashboard")
async def get_dashboard_api():
    """Get dashboard data as JSON"""
    try:
        dashboard_data = await dashboard.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {"error": "Unable to load dashboard data"}

@app.get("/api/teams")
async def get_teams():
    """Get all team metrics"""
    try:
        teams_data = {}
        for team_name, metrics in dashboard.team_metrics.items():
            teams_data[team_name] = {
                'status': metrics.status.value,
                'performance_level': metrics.performance_level.value,
                'quality_score': metrics.quality_score,
                'productivity_score': metrics.productivity_score,
                'efficiency_score': metrics.efficiency_score,
                'tasks_completed': metrics.tasks_completed,
                'tasks_in_progress': metrics.tasks_in_progress,
                'error_rate': metrics.error_rate,
                'uptime_percentage': metrics.uptime_percentage,
                'response_time_ms': metrics.response_time_ms,
                'last_activity': metrics.last_activity.isoformat()
            }
        return teams_data
    except Exception as e:
        logger.error(f"Error getting teams data: {e}")
        return {"error": "Unable to load teams data"}

@app.get("/api/system")
async def get_system_metrics():
    """Get system-wide metrics"""
    try:
        return {
            'total_teams': dashboard.system_metrics.total_teams,
            'active_teams': len([t for t in dashboard.team_metrics.values() if t.status.value == 'active']),
            'overall_performance': dashboard.system_metrics.overall_performance,
            'system_uptime': dashboard.system_metrics.system_uptime,
            'error_recovery_rate': dashboard.system_metrics.error_recovery_rate,
            'innovation_index': dashboard.system_metrics.innovation_index,
            'market_alignment_score': dashboard.system_metrics.market_alignment_score,
            'technology_adoption_rate': dashboard.system_metrics.technology_adoption_rate,
            'customer_satisfaction': dashboard.system_metrics.customer_satisfaction,
            'revenue_growth': dashboard.system_metrics.revenue_growth,
            'cost_efficiency': dashboard.system_metrics.cost_efficiency
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {"error": "Unable to load system metrics"}

@app.get("/api/alerts")
async def get_alerts():
    """Get active alerts"""
    try:
        alerts = await dashboard._get_active_alerts()
        return {
            'alerts': alerts,
            'alert_count': len(alerts),
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"error": "Unable to load alerts"}

@app.get("/api/kpi")
async def get_kpi():
    """Get KPI summary"""
    try:
        kpi_data = await dashboard._get_kpi_summary()
        return kpi_data
    except Exception as e:
        logger.error(f"Error getting KPI data: {e}")
        return {"error": "Unable to load KPI data"}

@app.post("/api/teams/{team_name}/update")
async def update_team_metrics(team_name: str, metrics: Dict[str, Any]):
    """Update metrics for a specific team"""
    try:
        success = await dashboard.update_team_metrics(team_name, metrics)
        if success:
            return {"success": True, "message": f"Updated metrics for {team_name}"}
        else:
            return {"success": False, "message": f"Failed to update metrics for {team_name}"}
    except Exception as e:
        logger.error(f"Error updating team metrics: {e}")
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dashboard_initialized": dashboard is not None,
        "automation_system_initialized": automation_system is not None
    }

if __name__ == "__main__":
    print("🚀 Starting MFM Corporation Dashboard Server")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔧 API endpoints available at: http://localhost:8000/docs")
    
    # Run the server
    uvicorn.run(
        "dashboard_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
