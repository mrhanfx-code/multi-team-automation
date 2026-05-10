#!/usr/bin/env python3
"""
MFM Corporation - Real-Time Notifications System
Comprehensive notification system for all teams and system events
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    SYSTEM_ALERT = "system_alert"
    TEAM_UPDATE = "team_update"
    PERFORMANCE_ALERT = "performance_alert"

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    DASHBOARD = "dashboard"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    title: str
    message: str
    team_name: Optional[str]
    priority: str  # low, medium, high, urgent
    channels: List[NotificationChannel]
    timestamp: datetime
    metadata: Dict[str, Any]
    is_read: bool = False
    delivered: bool = False

@dataclass
class NotificationRule:
    """Notification rule configuration"""
    id: str
    name: str
    trigger_type: str
    conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    recipients: List[str]
    enabled: bool = True

class NotificationsSystem:
    """Comprehensive real-time notifications system"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.notifications = []
        self.notification_rules = []
        self.subscribers = {}
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',  # Configure with actual credentials
            'password': '',  # Configure with actual credentials
            'from_email': 'notifications@mfmcorporation.com'
        }
        self.webhook_urls = {}
        self.slack_webhook_url = None
        self.notification_handlers = {}
        
    async def initialize(self) -> bool:
        """Initialize the notifications system"""
        logger.info("🔔 Initializing MFM Corporation Notifications System")
        
        try:
            # Load notification rules
            await self._load_notification_rules()
            
            # Load subscribers
            await self._load_subscribers()
            
            # Set up default notification handlers
            self._setup_default_handlers()
            
            # Create default notification rules
            await self._create_default_rules()
            
            logger.info("✅ Notifications System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Notifications System initialization failed: {e}")
            return False
    
    async def send_notification(self, notification_type: NotificationType, 
                              title: str, message: str, 
                              team_name: Optional[str] = None,
                              priority: str = "medium",
                              channels: Optional[List[NotificationChannel]] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a notification"""
        try:
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.notifications)}"
            
            # Determine channels if not specified
            if channels is None:
                channels = self._get_default_channels(notification_type, priority)
            
            notification = Notification(
                id=notification_id,
                type=notification_type,
                title=title,
                message=message,
                team_name=team_name,
                priority=priority,
                channels=channels,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Add to notifications list
            self.notifications.append(notification)
            
            # Process notification through channels
            await self._process_notification(notification)
            
            # Save to Supabase
            await self.supabase_manager.save_notification(asdict(notification))
            
            logger.info(f"✅ Notification sent: {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
            return ""
    
    async def send_team_notification(self, team_name: str, notification_type: NotificationType,
                                   title: str, message: str, priority: str = "medium",
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send team-specific notification"""
        return await self.send_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            team_name=team_name,
            priority=priority,
            metadata=metadata
        )
    
    async def send_system_alert(self, alert_type: str, title: str, message: str,
                             severity: str = "medium", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send system alert"""
        notification_type = NotificationType.SYSTEM_ALERT if severity == "critical" else NotificationType.WARNING
        
        return await self.send_notification(
            notification_type=notification_type,
            title=f"🚨 System Alert: {title}",
            message=message,
            priority=severity,
            channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
            metadata={**(metadata or {}), "alert_type": alert_type}
        )
    
    async def send_performance_alert(self, team_name: str, metric_name: str, 
                                    current_value: float, threshold: float,
                                    severity: str = "warning") -> str:
        """Send performance alert"""
        title = f"Performance Alert: {team_name}"
        message = f"{metric_name} is {current_value:.2%} (threshold: {threshold:.2%})"
        
        return await self.send_team_notification(
            team_name=team_name,
            notification_type=NotificationType.PERFORMANCE_ALERT,
            title=title,
            message=message,
            priority=severity,
            metadata={
                "metric_name": metric_name,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity
            }
        )
    
    async def send_workflow_notification(self, workflow_id: str, status: str, 
                                       team_name: Optional[str] = None,
                                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send workflow notification"""
        if status == "started":
            notification_type = NotificationType.WORKFLOW_STARTED
            title = f"Workflow Started: {workflow_id}"
            message = f"Workflow {workflow_id} has been initiated"
        elif status == "completed":
            notification_type = NotificationType.WORKFLOW_COMPLETED
            title = f"Workflow Completed: {workflow_id}"
            message = f"Workflow {workflow_id} has been completed successfully"
        else:
            notification_type = NotificationType.INFO
            title = f"Workflow Update: {workflow_id}"
            message = f"Workflow {workflow_id} status: {status}"
        
        return await self.send_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            team_name=team_name,
            priority="medium",
            metadata={**metadata or {}, "workflow_id": workflow_id, "status": status}
        )
    
    async def get_notifications(self, team_name: Optional[str] = None, 
                              unread_only: bool = False,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications with optional filters"""
        filtered_notifications = self.notifications
        
        if team_name:
            filtered_notifications = [n for n in filtered_notifications if n.team_name == team_name]
        
        if unread_only:
            filtered_notifications = [n for n in filtered_notifications if not n.is_read]
        
        # Sort by timestamp (newest first)
        filtered_notifications.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        filtered_notifications = filtered_notifications[:limit]
        
        return [asdict(n) for n in filtered_notifications]
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            for notification in self.notifications:
                if notification.id == notification_id:
                    notification.is_read = True
                    await self.supabase_manager.update_notification_read_status(notification_id, True)
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    async def create_notification_rule(self, rule: NotificationRule) -> bool:
        """Create a new notification rule"""
        try:
            self.notification_rules.append(rule)
            await self.supabase_manager.save_notification_rule(asdict(rule))
            logger.info(f"✅ Notification rule created: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create notification rule: {e}")
            return False
    
    async def _process_notification(self, notification: Notification):
        """Process notification through all configured channels"""
        for channel in notification.channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(notification)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(notification)
                elif channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(notification)
                elif channel == NotificationChannel.DASHBOARD:
                    await self._send_dashboard_notification(notification)
                elif channel == NotificationChannel.IN_APP:
                    await self._send_in_app_notification(notification)
                
                notification.delivered = True
                
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
    
    async def _send_email_notification(self, notification: Notification):
        """Send email notification"""
        if not self.email_config['username']:
            logger.warning("Email configuration not set up")
            return
        
        try:
            # Get recipients for this notification
            recipients = self._get_recipients_for_notification(notification)
            
            if not recipients:
                logger.warning(f"No recipients found for notification: {notification.title}")
                return
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[MFM Corporation] {notification.title}"
            
            # Email body
            body = f"""
            <html>
            <body>
                <h2>{notification.title}</h2>
                <p><strong>Type:</strong> {notification.type.value}</p>
                <p><strong>Priority:</strong> {notification.priority}</p>
                <p><strong>Team:</strong> {notification.team_name or 'System'}</p>
                <p><strong>Time:</strong> {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <p>{notification.message}</p>
                <hr>
                <p><small>This is an automated notification from MFM Corporation Multi-Team Automation System</small></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email (simulation - in production, use actual SMTP)
            logger.info(f"📧 Email notification sent to {len(recipients)} recipients: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, notification: Notification):
        """Send Slack notification"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        try:
            # Create Slack message
            slack_message = {
                "text": notification.title,
                "attachments": [
                    {
                        "color": self._get_slack_color(notification.type),
                        "fields": [
                            {"title": "Type", "value": notification.type.value, "short": True},
                            {"title": "Priority", "value": notification.priority, "short": True},
                            {"title": "Team", "value": notification.team_name or "System", "short": True},
                            {"title": "Time", "value": notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                        ],
                        "text": notification.message
                    }
                ]
            }
            
            # Send to Slack (simulation)
            logger.info(f"💬 Slack notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_webhook_notification(self, notification: Notification):
        """Send webhook notification"""
        webhook_url = self.webhook_urls.get(notification.team_name)
        if not webhook_url:
            logger.warning(f"No webhook URL configured for team: {notification.team_name}")
            return
        
        try:
            # Create webhook payload
            payload = {
                "notification_id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "message": notification.message,
                "team_name": notification.team_name,
                "priority": notification.priority,
                "timestamp": notification.timestamp.isoformat(),
                "metadata": notification.metadata
            }
            
            # Send webhook (simulation)
            logger.info(f"🔗 Webhook notification sent to {notification.team_name}: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_dashboard_notification(self, notification: Notification):
        """Send notification to dashboard"""
        try:
            # This would update the dashboard with the new notification
            logger.info(f"📊 Dashboard notification: {notification.title}")
        except Exception as e:
            logger.error(f"Failed to send dashboard notification: {e}")
    
    async def _send_in_app_notification(self, notification: Notification):
        """Send in-app notification"""
        try:
            # This would trigger in-app notification
            logger.info(f"🔔 In-app notification: {notification.title}")
        except Exception as e:
            logger.error(f"Failed to send in-app notification: {e}")
    
    def _get_default_channels(self, notification_type: NotificationType, priority: str) -> List[NotificationChannel]:
        """Get default channels based on notification type and priority"""
        if priority == "urgent" or notification_type == NotificationType.CRITICAL:
            return [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.DASHBOARD]
        elif priority == "high":
            return [NotificationChannel.EMAIL, NotificationChannel.DASHBOARD]
        elif notification_type in [NotificationType.TASK_COMPLETED, NotificationType.WORKFLOW_COMPLETED]:
            return [NotificationChannel.DASHBOARD, NotificationChannel.IN_APP]
        else:
            return [NotificationChannel.DASHBOARD]
    
    def _get_recipients_for_notification(self, notification: Notification) -> List[str]:
        """Get recipients for a notification based on team and rules"""
        recipients = []
        
        # Get team-specific subscribers
        if notification.team_name:
            team_subscribers = self.subscribers.get(notification.team_name, [])
            recipients.extend(team_subscribers)
        
        # Add system-wide subscribers for high priority notifications
        if notification.priority in ["high", "urgent"]:
            system_subscribers = self.subscribers.get("system", [])
            recipients.extend(system_subscribers)
        
        return list(set(recipients))  # Remove duplicates
    
    def _get_slack_color(self, notification_type: NotificationType) -> str:
        """Get Slack color based on notification type"""
        color_map = {
            NotificationType.SUCCESS: "good",
            NotificationType.INFO: "good",
            NotificationType.WARNING: "warning",
            NotificationType.ERROR: "danger",
            NotificationType.CRITICAL: "danger",
            NotificationType.TASK_COMPLETED: "good",
            NotificationType.TASK_FAILED: "danger",
            NotificationType.WORKFLOW_STARTED: "good",
            NotificationType.WORKFLOW_COMPLETED: "good",
            NotificationType.SYSTEM_ALERT: "danger",
            NotificationType.TEAM_UPDATE: "good",
            NotificationType.PERFORMANCE_ALERT: "warning"
        }
        return color_map.get(notification_type, "good")
    
    async def _load_notification_rules(self):
        """Load notification rules from Supabase"""
        try:
            # Simulate loading rules
            self.notification_rules = []
            logger.info("📋 Notification rules loaded")
        except Exception as e:
            logger.error(f"Failed to load notification rules: {e}")
    
    async def _load_subscribers(self):
        """Load subscribers from Supabase"""
        try:
            # Simulate loading subscribers
            self.subscribers = {
                "Innovation Team": ["innovation@mfmcorporation.com"],
                "Development Team": ["development@mfmcorporation.com"],
                "Marketing Team": ["marketing@mfmcorporation.com"],
                "Media Team": ["media@mfmcorporation.com"],
                "system": ["admin@mfmcorporation.com", "ops@mfmcorporation.com"]
            }
            logger.info("👥 Subscribers loaded")
        except Exception as e:
            logger.error(f"Failed to load subscribers: {e}")
    
    def _setup_default_handlers(self):
        """Set up default notification handlers"""
        self.notification_handlers = {
            "task_completed": self._handle_task_completed,
            "task_failed": self._handle_task_failed,
            "workflow_started": self._handle_workflow_started,
            "workflow_completed": self._handle_workflow_completed,
            "performance_alert": self._handle_performance_alert
        }
    
    async def _create_default_rules(self):
        """Create default notification rules"""
        default_rules = [
            NotificationRule(
                id="rule_1",
                name="High Priority System Alerts",
                trigger_type="system_alert",
                conditions={"priority": "high"},
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                recipients=["admin@mfmcorporation.com"]
            ),
            NotificationRule(
                id="rule_2",
                name="Task Completion Notifications",
                trigger_type="task_completed",
                conditions={},
                channels=[NotificationChannel.DASHBOARD],
                recipients=[]
            ),
            NotificationRule(
                id="rule_3",
                name="Performance Alerts",
                trigger_type="performance_alert",
                conditions={"severity": "warning"},
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                recipients=["ops@mfmcorporation.com"]
            )
        ]
        
        for rule in default_rules:
            self.notification_rules.append(rule)
    
    async def _handle_task_completed(self, notification: Notification):
        """Handle task completed notification"""
        logger.info(f"✅ Task completed: {notification.title}")
    
    async def _handle_task_failed(self, notification: Notification):
        """Handle task failed notification"""
        logger.error(f"❌ Task failed: {notification.title}")
    
    async def _handle_workflow_started(self, notification: Notification):
        """Handle workflow started notification"""
        logger.info(f"🚀 Workflow started: {notification.title}")
    
    async def _handle_workflow_completed(self, notification: Notification):
        """Handle workflow completed notification"""
        logger.info(f"✅ Workflow completed: {notification.title}")
    
    async def _handle_performance_alert(self, notification: Notification):
        """Handle performance alert notification"""
        logger.warning(f"⚠️ Performance alert: {notification.title}")
    
    async def start_notification_monitoring(self):
        """Start continuous notification monitoring"""
        logger.info("🔄 Starting notification monitoring")
        
        while True:
            try:
                # Check for system alerts
                await self._check_system_alerts()
                
                # Clean up old notifications
                await self._cleanup_old_notifications()
                
                # Wait for next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Notification monitoring error: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _check_system_alerts(self):
        """Check for system alerts"""
        # Simulate system alert checking
        pass
    
    async def _cleanup_old_notifications(self):
        """Clean up old notifications (older than 30 days)"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        old_count = len(self.notifications)
        self.notifications = [n for n in self.notifications if n.timestamp > cutoff_date]
        
        if len(self.notifications) < old_count:
            logger.info(f"🧹 Cleaned up {old_count - len(self.notifications)} old notifications")
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        """Configure email settings"""
        self.email_config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_email': from_email
        }
        logger.info("📧 Email configuration updated")
    
    def configure_slack(self, webhook_url: str):
        """Configure Slack webhook"""
        self.slack_webhook_url = webhook_url
        logger.info("💬 Slack webhook configured")
    
    def add_webhook(self, team_name: str, webhook_url: str):
        """Add webhook URL for a team"""
        self.webhook_urls[team_name] = webhook_url
        logger.info(f"🔗 Webhook added for {team_name}")
    
    def add_subscriber(self, team_name: str, email: str):
        """Add subscriber for a team"""
        if team_name not in self.subscribers:
            self.subscribers[team_name] = []
        self.subscribers[team_name].append(email)
        logger.info(f"👥 Subscriber added to {team_name}: {email}")
