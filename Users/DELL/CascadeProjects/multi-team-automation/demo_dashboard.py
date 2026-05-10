#!/usr/bin/env python3
"""
MFM Corporation - Dashboard Demo Script
Demonstrates the complete tracking dashboard functionality
"""

import asyncio
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append('src')
sys.path.append('.')

from src.tracking_dashboard import TrackingDashboard
from unified_system import MultiTeamAutomationSystem

async def demo_dashboard():
    """Demonstrate the tracking dashboard functionality"""
    print("🎯 MFM CORPORATION - TRACKING DASHBOARD DEMO")
    print("=" * 60)
    
    # Initialize the automation system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    print(f"✅ MFM Corporation System initialized")
    print(f"📊 Tracking Dashboard: {'Available' if system.tracking_dashboard else 'Not Available'}")
    
    if not system.tracking_dashboard:
        print("❌ Tracking Dashboard not available - skipping demo")
        return
    
    dashboard = system.tracking_dashboard
    
    # Initialize dashboard
    print("\n🔧 Initializing Tracking Dashboard...")
    await dashboard.initialize_dashboard()
    print("✅ Dashboard initialized successfully")
    
    # Demo 1: Show initial dashboard data
    print("\n📊 Demo 1: Initial Dashboard Data")
    print("-" * 40)
    
    dashboard_data = await dashboard.get_dashboard_data()
    
    print(f"Total Teams: {dashboard_data['system_overview']['total_teams']}")
    print(f"Active Teams: {dashboard_data['system_overview']['active_teams']}")
    print(f"Overall Performance: {dashboard_data['system_overview']['overall_performance']:.1%}")
    print(f"System Health: {dashboard_data['system_overview']['system_health']:.1%}")
    print(f"Innovation Index: {dashboard_data['system_metrics']['innovation_index']:.1%}")
    print(f"Market Alignment: {dashboard_data['system_metrics']['market_alignment_score']:.1%}")
    
    # Demo 2: Show team performance
    print("\n👥 Demo 2: Team Performance Overview")
    print("-" * 40)
    
    for team_name, team_data in dashboard_data['team_performance'].items():
        print(f"\n{team_name}:")
        print(f"  Status: {team_data['status'].upper()}")
        print(f"  Performance: {team_data['performance_level'].upper()}")
        print(f"  Quality Score: {team_data['quality_score']:.1%}")
        print(f"  Productivity: {team_data['productivity_score']:.1%}")
        print(f"  Efficiency: {team_data['efficiency_score']:.1%}")
        print(f"  Tasks Completed: {team_data['tasks_completed']}")
        print(f"  Response Time: {team_data['response_time_ms']:.0f}ms")
    
    # Demo 3: Simulate team activity updates
    print("\n🔄 Demo 3: Simulating Team Activity Updates")
    print("-" * 40)
    
    # Simulate Innovation Team activity
    print("🔬 Updating Innovation Team metrics...")
    await dashboard.update_team_metrics("Innovation Team", {
        'quality_score': 0.94,
        'productivity_score': 0.91,
        'tasks_completed': 15,
        'response_time_ms': 220
    })
    
    # Simulate Development Team activity
    print("🔨 Updating Development Team metrics...")
    await dashboard.update_team_metrics("Development Team", {
        'quality_score': 0.92,
        'efficiency_score': 0.95,
        'tasks_completed': 25,
        'response_time_ms': 180
    })
    
    # Simulate Marketing Team activity
    print("📈 Updating Marketing Team metrics...")
    await dashboard.update_team_metrics("Marketing Team", {
        'productivity_score': 0.89,
        'tasks_completed': 8,
        'response_time_ms': 250
    })
    
    print("✅ Team metrics updated")
    
    # Demo 4: Show updated dashboard
    print("\n📊 Demo 4: Updated Dashboard Data")
    print("-" * 40)
    
    updated_data = await dashboard.get_dashboard_data()
    
    print(f"Innovation Team Quality: {updated_data['team_performance']['Innovation Team']['quality_score']:.1%}")
    print(f"Development Team Efficiency: {updated_data['team_performance']['Development Team']['efficiency_score']:.1%}")
    print(f"Marketing Team Productivity: {updated_data['team_performance']['Marketing Team']['productivity_score']:.1%}")
    
    # Demo 5: Show alerts
    print("\n🚨 Demo 5: Alert System")
    print("-" * 40)
    
    alerts = updated_data.get('alerts', [])
    if alerts:
        print(f"Active Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"  ⚠️ {alert}")
    else:
        print("✅ No active alerts - All systems performing optimally")
    
    # Demo 6: Show KPI summary
    print("\n📈 Demo 6: KPI Summary")
    print("-" * 40)
    
    kpi_data = updated_data.get('kpi_summary', {})
    for kpi, value in kpi_data.items():
        print(f"  {kpi.replace('_', ' ').title()}: {value}")
    
    # Demo 7: Generate HTML dashboard
    print("\n🌐 Demo 7: HTML Dashboard Generation")
    print("-" * 40)
    
    html_dashboard = await dashboard.generate_real_time_dashboard()
    
    # Save HTML dashboard to file
    with open('dashboard_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_dashboard)
    
    print("✅ HTML dashboard saved to 'dashboard_demo.html'")
    print("📂 Open this file in your browser to see the interactive dashboard")
    
    # Demo 8: Show system metrics trends
    print("\n📊 Demo 8: System Metrics Trends")
    print("-" * 40)
    
    system_metrics = updated_data['system_metrics']
    print(f"Innovation Index: {system_metrics['innovation_index']:.1%}")
    print(f"Market Alignment: {system_metrics['market_alignment_score']:.1%}")
    print(f"Technology Adoption: {system_metrics['technology_adoption_rate']:.1%}")
    print(f"Customer Satisfaction: {system_metrics['customer_satisfaction']:.1%}")
    print(f"Revenue Growth: {system_metrics['revenue_growth']:.1%}")
    print(f"Cost Efficiency: {system_metrics['cost_efficiency']:.1%}")
    
    # Demo 9: Real-time monitoring simulation
    print("\n🔄 Demo 9: Real-time Monitoring Simulation")
    print("-" * 40)
    
    print("Simulating real-time updates for 10 seconds...")
    
    for i in range(5):
        await asyncio.sleep(2)
        
        # Random team update
        teams = ["Innovation Team", "Development Team", "Marketing Team", "Media Team"]
        team = teams[i % len(teams)]
        
        # Simulate metric changes
        await dashboard.update_team_metrics(team, {
            'quality_score': 0.85 + (i * 0.02),
            'productivity_score': 0.80 + (i * 0.03),
            'tasks_completed': 10 + i,
            'response_time_ms': 300 - (i * 10)
        })
        
        current_data = await dashboard.get_dashboard_data()
        print(f"  Update {i+1}: {team} - Quality: {current_data['team_performance'][team]['quality_score']:.1%}")
    
    print("✅ Real-time monitoring simulation complete")
    
    # Final Summary
    print("\n🎉 TRACKING DASHBOARD DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Dashboard initialization: SUCCESS")
    print("✅ Team metrics tracking: ACTIVE")
    print("✅ Real-time updates: FUNCTIONAL")
    print("✅ Alert system: OPERATIONAL")
    print("✅ KPI monitoring: ACTIVE")
    print("✅ HTML dashboard generation: WORKING")
    print("✅ System health monitoring: ACTIVE")
    
    print(f"\n📊 Final Dashboard Status:")
    final_data = await dashboard.get_dashboard_data()
    print(f"   Overall Performance: {final_data['system_overview']['overall_performance']:.1%}")
    print(f"   System Health: {final_data['system_overview']['system_health']:.1%}")
    print(f"   Active Teams: {final_data['system_overview']['active_teams']}/{final_data['system_overview']['total_teams']}")
    print(f"   Active Alerts: {len(final_data.get('alerts', []))}")
    
    print(f"\n🌐 To view the interactive dashboard:")
    print(f"   1. Open 'dashboard_demo.html' in your browser")
    print(f"   2. Or run: python dashboard_server.py")
    print(f"   3. Then navigate to: http://localhost:8000")
    
    print(f"\n🚀 MFM Corporation Tracking Dashboard is ready for production!")

async def demo_dashboard_server():
    """Demonstrate the dashboard server functionality"""
    print("\n🌐 DASHBOARD SERVER DEMO")
    print("=" * 40)
    
    print("To start the dashboard server:")
    print("1. Run: python dashboard_server.py")
    print("2. Open: http://localhost:8000")
    print("3. View: Interactive real-time dashboard")
    print("4. API: http://localhost:8000/docs")
    
    print("\nAvailable API endpoints:")
    print("  GET /                    - Main dashboard (HTML)")
    print("  GET /api/dashboard       - Dashboard data (JSON)")
    print("  GET /api/teams           - Team metrics (JSON)")
    print("  GET /api/system          - System metrics (JSON)")
    print("  GET /api/alerts          - Active alerts (JSON)")
    print("  GET /api/kpi             - KPI summary (JSON)")
    print("  GET /health              - Health check")
    print("  POST /api/teams/{{team}}/update - Update team metrics")

if __name__ == "__main__":
    try:
        asyncio.run(demo_dashboard())
        asyncio.run(demo_dashboard_server())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
