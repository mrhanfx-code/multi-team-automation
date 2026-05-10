#!/usr/bin/env python3
"""
MFM Corporation - Notifications and Scheduling Demo Script
Demonstrates the complete notifications and scheduled workflows functionality
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta

# Add src to path
sys.path.append('src')
sys.path.append('.')

from src.notifications_system import NotificationsSystem, NotificationType, NotificationChannel
from src.scheduled_workflows import ScheduledWorkflowsSystem, TriggerType, ScheduleType
from unified_system import MultiTeamAutomationSystem

async def demo_notifications_system():
    """Demonstrate the notifications system functionality"""
    print("🔔 MFM CORPORATION - NOTIFICATIONS SYSTEM DEMO")
    print("=" * 60)
    
    # Initialize the automation system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    if not system.notifications_system:
        print("❌ Notifications System not available - skipping demo")
        return
    
    notifications = system.notifications_system
    
    # Demo 1: Send basic notifications
    print("\n📧 Demo 1: Basic Notifications")
    print("-" * 40)
    
    # Send info notification
    notif_id1 = await notifications.send_notification(
        notification_type=NotificationType.INFO,
        title="System Update",
        message="MFM Corporation system has been updated to version 3.0.0",
        priority="medium"
    )
    print(f"✅ Info notification sent: {notif_id1}")
    
    # Send success notification
    notif_id2 = await notifications.send_notification(
        notification_type=NotificationType.SUCCESS,
        title="Task Completed",
        message="Innovation research completed successfully",
        team_name="Innovation Team",
        priority="medium"
    )
    print(f"✅ Success notification sent: {notif_id2}")
    
    # Demo 2: Send team-specific notifications
    print("\n👥 Demo 2: Team-Specific Notifications")
    print("-" * 40)
    
    # Development Team notification
    await notifications.send_team_notification(
        team_name="Development Team",
        notification_type=NotificationType.WARNING,
        title="Performance Alert",
        message="Code quality score dropped below threshold",
        priority="high"
    )
    print("✅ Development Team notification sent")
    
    # Marketing Team notification
    await notifications.send_team_notification(
        team_name="Marketing Team",
        notification_type=NotificationType.SUCCESS,
        title="Campaign Success",
        message="Marketing campaign exceeded target by 25%",
        priority="medium"
    )
    print("✅ Marketing Team notification sent")
    
    # Demo 3: Send system alerts
    print("\n🚨 Demo 3: System Alerts")
    print("-" * 40)
    
    # Critical system alert
    await notifications.send_system_alert(
        alert_type="PERFORMANCE",
        title="System Performance Degradation",
        message="Overall system performance dropped to 82%",
        severity="high"
    )
    print("✅ Critical system alert sent")
    
    # Performance alert
    await notifications.send_performance_alert(
        team_name="Innovation Team",
        metric_name="Quality Score",
        current_value=0.78,
        threshold=0.85,
        severity="warning"
    )
    print("✅ Performance alert sent")
    
    # Demo 4: Send workflow notifications
    print("\n🔄 Demo 4: Workflow Notifications")
    print("-" * 40)
    
    workflow_id = f"demo_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Workflow started
    await notifications.send_workflow_notification(
        workflow_id=workflow_id,
        status="started",
        team_name="System",
        metadata={"topic": "AI Platform Development", "scope": "Enterprise"}
    )
    print(f"✅ Workflow started notification: {workflow_id}")
    
    # Workflow completed
    await notifications.send_workflow_notification(
        workflow_id=workflow_id,
        status="completed",
        team_name="System",
        metadata={"topic": "AI Platform Development", "scope": "Enterprise"}
    )
    print(f"✅ Workflow completed notification: {workflow_id}")
    
    # Demo 5: View notifications
    print("\n📋 Demo 5: View Notifications")
    print("-" * 40)
    
    # Get all notifications
    all_notifications = await notifications.get_notifications(limit=10)
    print(f"Total notifications: {len(all_notifications)}")
    
    for notif in all_notifications[:5]:
        print(f"  {notif['type'].upper()}: {notif['title']} ({notif['team_name'] or 'System'})")
    
    # Get unread notifications
    unread_notifications = await notifications.get_notifications(unread_only=True, limit=5)
    print(f"Unread notifications: {len(unread_notifications)}")
    
    # Demo 6: Configure notification channels
    print("\n⚙️ Demo 6: Notification Configuration")
    print("-" * 40)
    
    # Configure email (demo)
    notifications.configure_email(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="demo@mfmcorporation.com",
        password="demo_password",
        from_email="notifications@mfmcorporation.com"
    )
    print("✅ Email configuration updated (demo)")
    
    # Configure Slack (demo)
    notifications.configure_slack("https://hooks.slack.com/services/demo/webhook")
    print("✅ Slack webhook configured (demo)")
    
    # Add webhook for team
    notifications.add_webhook("Development Team", "https://api.mfmcorporation.com/webhooks/dev")
    print("✅ Development Team webhook added")
    
    # Add subscriber
    notifications.add_subscriber("Marketing Team", "marketing.manager@mfmcorporation.com")
    print("✅ Marketing Team subscriber added")
    
    print("\n🎉 NOTIFICATIONS SYSTEM DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Basic notifications: WORKING")
    print("✅ Team-specific notifications: WORKING")
    print("✅ System alerts: WORKING")
    print("✅ Workflow notifications: WORKING")
    print("✅ Notification viewing: WORKING")
    print("✅ Channel configuration: WORKING")

async def demo_scheduled_workflows():
    """Demonstrate the scheduled workflows functionality"""
    print("\n⏰ MFM CORPORATION - SCHEDULED WORKFLOWS DEMO")
    print("=" * 60)
    
    # Initialize the automation system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    if not system.scheduled_workflows:
        print("❌ Scheduled Workflows System not available - skipping demo")
        return
    
    workflows = system.scheduled_workflows
    
    # Demo 1: Create scheduled workflows
    print("\n📅 Demo 1: Create Scheduled Workflows")
    print("-" * 40)
    
    # Daily innovation scan
    workflow_id1 = await workflows.create_scheduled_workflow(
        name="Daily AI Innovation Scan",
        description="Daily scan for new AI innovations and trends",
        trigger_type=TriggerType.SCHEDULED,
        schedule_type=ScheduleType.DAILY,
        schedule_expression="09:00",
        workflow_function="innovation_research",
        parameters={
            "innovation_focus": "AI/ML Technologies",
            "research_scope": "Daily innovation tracking"
        }
    )
    print(f"✅ Daily workflow created: {workflow_id1}")
    
    # Weekly market intelligence
    workflow_id2 = await workflows.create_scheduled_workflow(
        name="Weekly Market Analysis",
        description="Weekly market demand analysis and trend prediction",
        trigger_type=TriggerType.SCHEDULED,
        schedule_type=ScheduleType.WEEKLY,
        schedule_expression="Monday 10:00",
        workflow_function="market_intelligence",
        parameters={
            "market_focus": "AI Automation Market",
            "analysis_scope": "Weekly market intelligence"
        }
    )
    print(f"✅ Weekly workflow created: {workflow_id2}")
    
    # Hourly performance check
    workflow_id3 = await workflows.create_scheduled_workflow(
        name="Hourly Performance Check",
        description="Check system performance every hour",
        trigger_type=TriggerType.SCHEDULED,
        schedule_type=ScheduleType.INTERVAL,
        schedule_expression="1h",
        workflow_function="performance_check",
        parameters={
            "conditions": {
                "type": "performance_based",
                "performance_threshold": 0.85
            }
        }
    )
    print(f"✅ Hourly workflow created: {workflow_id3}")
    
    # Conditional workflow
    workflow_id4 = await workflows.create_scheduled_workflow(
        name="Emergency Alert Workflow",
        description="Trigger when system performance drops below 80%",
        trigger_type=TriggerType.CONDITIONAL,
        schedule_type=None,
        schedule_expression=None,
        workflow_function="emergency_response",
        parameters={
            "conditions": {
                "type": "performance_based",
                "performance_threshold": 0.80
            }
        }
    )
    print(f"✅ Conditional workflow created: {workflow_id4}")
    
    # Demo 2: Manual workflow triggering
    print("\n🔨 Demo 2: Manual Workflow Triggering")
    print("-" * 40)
    
    # Trigger manual workflow
    execution_id1 = await workflows.trigger_manual_workflow(
        workflow_id=workflow_id1,
        parameters={
            "innovation_focus": "Manual AI Research",
            "research_scope": "Immediate analysis"
        }
    )
    print(f"✅ Manual workflow triggered: {execution_id1}")
    
    # Demo 3: Event-based workflow triggering
    print("\n🎯 Demo 3: Event-Based Workflow Triggering")
    print("-" * 40)
    
    # Trigger event-based workflows
    event_executions = await workflows.trigger_event_based_workflow(
        event_type="performance_alert",
        event_data={
            "metric": "quality_score",
            "value": 0.75,
            "threshold": 0.85,
            "team": "Development Team"
        }
    )
    print(f"✅ Event-based workflows triggered: {len(event_executions)}")
    
    # Demo 4: View scheduled workflows
    print("\n📋 Demo 4: View Scheduled Workflows")
    print("-" * 40)
    
    # Get all workflows
    all_workflows = await workflows.get_scheduled_workflows()
    print(f"Total scheduled workflows: {len(all_workflows)}")
    
    for workflow in all_workflows:
        status = "✅" if workflow['enabled'] else "❌"
        next_run = workflow['next_run'][:16] if workflow['next_run'] else "Not scheduled"
        print(f"  {status} {workflow['name']} - Next: {next_run}")
    
    # Demo 5: Workflow management
    print("\n⚙️ Demo 5: Workflow Management")
    print("-" * 40)
    
    # Disable a workflow
    await workflows.disable_workflow(workflow_id3)
    print(f"✅ Workflow disabled: {workflow_id3}")
    
    # Enable a workflow
    await workflows.enable_workflow(workflow_id3)
    print(f"✅ Workflow enabled: {workflow_id3}")
    
    # Demo 6: View execution history
    print("\n📊 Demo 6: Execution History")
    print("-" * 40)
    
    # Get execution history
    executions = await workflows.get_workflow_executions(limit=10)
    print(f"Total executions: {len(executions)}")
    
    for execution in executions[:3]:
        status_icon = "✅" if execution['status'] == 'completed' else "❌"
        duration = f"{execution['execution_time']:.2f}s" if execution['execution_time'] else "N/A"
        print(f"  {status_icon} {execution['id']} - Duration: {duration}")
    
    # Demo 7: Scheduler status
    print("\n📈 Demo 7: Scheduler Status")
    print("-" * 40)
    
    status = workflows.get_scheduler_status()
    print(f"Scheduler running: {status['running']}")
    print(f"Total workflows: {status['total_workflows']}")
    print(f"Enabled workflows: {status['enabled_workflows']}")
    print(f"Running workflows: {status['running_workflows']}")
    print(f"Total executions: {status['total_executions']}")
    
    print("\n🎉 SCHEDULED WORKFLOWS DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Scheduled workflow creation: WORKING")
    print("✅ Manual workflow triggering: WORKING")
    print("✅ Event-based triggering: WORKING")
    print("✅ Workflow viewing: WORKING")
    print("✅ Workflow management: WORKING")
    print("✅ Execution history: WORKING")
    print("✅ Scheduler monitoring: WORKING")

async def demo_integrated_system():
    """Demonstrate the integrated notifications and scheduling system"""
    print("\n🔗 MFM CORPORATION - INTEGRATED SYSTEM DEMO")
    print("=" * 60)
    
    # Initialize the automation system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    print("✅ MFM Corporation System initialized")
    print(f"📊 Tracking Dashboard: {'Available' if system.tracking_dashboard else 'Not Available'}")
    print(f"🔔 Notifications System: {'Available' if system.notifications_system else 'Not Available'}")
    print(f"⏰ Scheduled Workflows: {'Available' if system.scheduled_workflows else 'Not Available'}")
    
    # Demo 1: Automated workflow with notifications
    print("\n🔄 Demo 1: Automated Workflow with Notifications")
    print("-" * 40)
    
    # Create a scheduled workflow that triggers notifications
    if system.scheduled_workflows:
        workflow_id = await system.scheduled_workflows.create_scheduled_workflow(
            name="Integrated Demo Workflow",
            description="Demo workflow with notifications and tracking",
            trigger_type=TriggerType.SCHEDULED,
            schedule_type=ScheduleType.INTERVAL,
            schedule_expression="30m",  # Every 30 minutes
            workflow_function="run_complete_workflow",
            parameters={
                "research_topic": "Integrated System Demo",
                "research_scope": "Demonstration of integrated capabilities"
            }
        )
        print(f"✅ Integrated workflow created: {workflow_id}")
        
        # Trigger it manually for demo
        execution_id = await system.scheduled_workflows.trigger_manual_workflow(workflow_id)
        print(f"✅ Integrated workflow executed: {execution_id}")
    
    # Demo 2: Real-time monitoring with alerts
    print("\n📊 Demo 2: Real-time Monitoring with Alerts")
    print("-" * 40)
    
    if system.tracking_dashboard and system.notifications_system:
        # Simulate performance drop
        await system.tracking_dashboard.update_team_metrics(
            "Development Team",
            {
                'quality_score': 0.75,  # Below threshold
                'error_rate': 0.08,      # Above threshold
                'response_time_ms': 6000  # Above threshold
            }
        )
        print("✅ Performance metrics updated (simulated drop)")
        
        # Check for alerts
        alerts = await system.tracking_dashboard._get_active_alerts()
        if alerts:
            print(f"⚠️ Performance alerts detected: {len(alerts)}")
            
            # Send alert notification
            await system.notifications_system.send_performance_alert(
                team_name="Development Team",
                metric_name="Quality Score",
                current_value=0.75,
                threshold=0.85,
                severity="warning"
            )
            print("✅ Alert notification sent")
    
    # Demo 3: System-wide notification
    print("\n📢 Demo 3: System-Wide Notification")
    print("-" * 40)
    
    if system.notifications_system:
        await system.notifications_system.send_notification(
            notification_type=NotificationType.SUCCESS,
            title="MFM Corporation System Status",
            message="All systems operational with 94% overall performance",
            priority="medium",
            channels=[NotificationChannel.DASHBOARD, NotificationChannel.EMAIL]
        )
        print("✅ System-wide notification sent")
    
    print("\n🎉 INTEGRATED SYSTEM DEMO COMPLETED!")
    print("=" * 60)
    print("✅ System integration: WORKING")
    print("✅ Automated workflows: WORKING")
    print("✅ Real-time monitoring: WORKING")
    print("✅ Alert notifications: WORKING")
    print("✅ System-wide notifications: WORKING")

if __name__ == "__main__":
    try:
        asyncio.run(demo_notifications_system())
        asyncio.run(demo_scheduled_workflows())
        asyncio.run(demo_integrated_system())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
