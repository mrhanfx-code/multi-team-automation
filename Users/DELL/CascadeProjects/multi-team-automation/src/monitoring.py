"""
Monitoring and Alerting System for Multi-Team Automation
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    unit: str = ""

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricsCollector:
    """Collects and manages system metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.timers = {}
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        key = self._make_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value
        
        metric = Metric(
            name=name,
            value=self.counters[key],
            metric_type=MetricType.COUNTER,
            timestamp=datetime.now(),
            labels=labels or {},
            unit="count"
        )
        self._store_metric(metric)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self._store_metric(metric)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        
        # Keep only last 1000 values
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self._store_metric(metric)
    
    def start_timer(self, name: str, labels: Dict[str, str] = None) -> str:
        """Start a timer and return timer ID"""
        timer_id = f"{name}_{int(time.time() * 1000)}"
        key = self._make_key(name, labels)
        self.timers[timer_id] = {
            'name': name,
            'start_time': time.time(),
            'labels': labels or {}
        }
        return timer_id
    
    def end_timer(self, timer_id: str):
        """End a timer and record the duration"""
        if timer_id not in self.timers:
            return
        
        timer = self.timers.pop(timer_id)
        duration = time.time() - timer['start_time']
        
        metric = Metric(
            name=timer['name'],
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=datetime.now(),
            labels=timer['labels'],
            unit="seconds"
        )
        self._store_metric(metric)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for metric with labels"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _store_metric(self, metric: Metric):
        """Store metric in time-series data"""
        if metric.name not in self.metrics:
            self.metrics[metric.name] = []
        self.metrics[metric.name].append(metric)
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[metric.name]) > 1000:
            self.metrics[metric.name] = self.metrics[metric.name][-1000:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'counters': self.counters,
            'gauges': self.gauges,
            'histograms': {},
            'timers': {}
        }
        
        # Calculate histogram statistics
        for key, values in self.histograms.items():
            if values:
                summary['histograms'][key] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        # Calculate timer statistics from recent metrics
        for name, metric_list in self.metrics.items():
            timer_metrics = [m for m in metric_list if m.metric_type == MetricType.TIMER]
            if timer_metrics:
                values = [m.value for m in timer_metrics[-100:]]  # Last 100 timer values
                summary['timers'][name] = {
                    'count': len(values),
                    'avg': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
        
        return summary

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts = {}
        self.alert_rules = []
        self.notification_channels = []
        self.alert_history = []
        
    def add_alert_rule(self, name: str, condition: Callable, level: AlertLevel, 
                      message_template: str, cooldown_minutes: int = 5):
        """Add an alert rule"""
        rule = {
            'name': name,
            'condition': condition,
            'level': level,
            'message_template': message_template,
            'cooldown_minutes': cooldown_minutes,
            'last_triggered': None
        }
        self.alert_rules.append(rule)
    
    def add_notification_channel(self, channel_type: str, config: Dict[str, Any]):
        """Add a notification channel"""
        self.notification_channels.append({
            'type': channel_type,
            'config': config
        })
    
    async def check_alerts(self, metrics_collector: MetricsCollector):
        """Check all alert rules against current metrics"""
        metrics_summary = metrics_collector.get_metrics_summary()
        
        for rule in self.alert_rules:
            try:
                # Check cooldown period
                if rule['last_triggered']:
                    time_since_last = datetime.now() - rule['last_triggered']
                    if time_since_last < timedelta(minutes=rule['cooldown_minutes']):
                        continue
                
                # Evaluate condition
                if rule['condition'](metrics_summary):
                    await self._trigger_alert(rule, metrics_summary)
                    rule['last_triggered'] = datetime.now()
                    
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {e}")
    
    async def _trigger_alert(self, rule: Dict[str, Any], metrics: Dict[str, Any]):
        """Trigger an alert"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        
        # Format message
        message = rule['message_template'].format(**metrics)
        
        alert = Alert(
            id=alert_id,
            level=rule['level'],
            message=message,
            source=rule['name'],
            timestamp=datetime.now(),
            metadata={'rule': rule['name'], 'metrics': metrics}
        )
        
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        logger.warning(f"Alert triggered: {rule['level'].value.upper()} - {message}")
    
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications through all channels"""
        for channel in self.notification_channels:
            try:
                if channel['type'] == 'email':
                    await self._send_email_notification(alert, channel['config'])
                elif channel['type'] == 'webhook':
                    await self._send_webhook_notification(alert, channel['config'])
                elif channel['type'] == 'log':
                    await self._send_log_notification(alert, channel['config'])
            except Exception as e:
                logger.error(f"Failed to send notification via {channel['type']}: {e}")
    
    async def _send_email_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send email notification"""
        try:
            msg = MimeMultipart()
            msg['From'] = config['sender']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.source}"
            
            body = f"""
Alert Details:
- Level: {alert.level.value.upper()}
- Source: {alert.source}
- Time: {alert.timestamp}
- Message: {alert.message}

Metadata:
{json.dumps(alert.metadata, indent=2)}
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            if config.get('use_tls'):
                server.starttls()
            if config.get('username') and config.get('password'):
                server.login(config['username'], config['password'])
            
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send webhook notification"""
        import aiohttp
        
        payload = {
            'alert_id': alert.id,
            'level': alert.level.value,
            'message': alert.message,
            'source': alert.source,
            'timestamp': alert.timestamp.isoformat(),
            'metadata': alert.metadata
        }
        
        headers = config.get('headers', {})
        if 'authorization' in config:
            headers['Authorization'] = config['authorization']
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config['url'], json=payload, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Webhook notification failed: {response.status}")
    
    async def _send_log_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send log notification"""
        log_message = f"[ALERT] {alert.level.value.upper()} - {alert.message}"
        if alert.level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif alert.level == AlertLevel.ERROR:
            logger.error(log_message)
        elif alert.level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"Alert resolved: {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        active_alerts = self.get_active_alerts()
        
        return {
            'total_alerts': len(self.alert_history),
            'active_alerts': len(active_alerts),
            'alerts_by_level': {
                level.value: len([a for a in active_alerts if a.level == level])
                for level in AlertLevel
            },
            'recent_alerts': [
                {
                    'id': alert.id,
                    'level': alert.level.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.alert_history[-10:]
            ]
        }

class PerformanceMonitor:
    """Monitor system performance and team productivity"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics = metrics_collector
        self.alerts = alert_manager
        self.monitoring_active = False
        
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        
        # Set up default alert rules
        self._setup_default_alerts()
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")
    
    def _setup_default_alerts(self):
        """Set up default alert rules"""
        
        # High error rate alert
        self.alerts.add_alert_rule(
            name="high_error_rate",
            condition=lambda metrics: metrics.get('counters', {}).get('errors', 0) > 10,
            level=AlertLevel.WARNING,
            message_template="High error rate detected: {counters[errors]} errors"
        )
        
        # Low workflow completion rate
        self.alerts.add_alert_rule(
            name="low_completion_rate",
            condition=lambda metrics: False,  # Would need more complex calculation
            level=AlertLevel.WARNING,
            message_template="Low workflow completion rate detected"
        )
        
        # System resource alerts
        self.alerts.add_alert_rule(
            name="high_memory_usage",
            condition=lambda metrics: metrics.get('gauges', {}).get('memory_usage_percent', 0) > 80,
            level=AlertLevel.ERROR,
            message_template="High memory usage: {gauges[memory_usage_percent]}%"
        )
        
        # Team productivity alerts
        self.alerts.add_alert_rule(
            name="team_productivity_low",
            condition=lambda metrics: False,  # Would need team-specific metrics
            level=AlertLevel.WARNING,
            message_template="Team productivity below threshold"
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Check alerts
                await self.alerts.check_alerts(self.metrics)
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("cpu_usage_percent", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("memory_usage_percent", memory.percent)
            self.metrics.set_gauge("memory_available_bytes", memory.available)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.set_gauge("disk_usage_percent", (disk.used / disk.total) * 100)
            self.metrics.set_gauge("disk_free_bytes", disk.free)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metrics.increment_counter("network_bytes_sent", network.bytes_sent)
            self.metrics.increment_counter("network_bytes_recv", network.bytes_recv)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def record_workflow_start(self, workflow_id: str, team_name: str):
        """Record workflow start"""
        self.metrics.increment_counter("workflows_started", labels={"team": team_name})
        self.metrics.set_gauge("active_workflows", 
                              self.metrics.counters.get("workflows_started", 0) - 
                              self.metrics.counters.get("workflows_completed", 0))
    
    def record_workflow_completion(self, workflow_id: str, team_name: str, duration_seconds: float):
        """Record workflow completion"""
        self.metrics.increment_counter("workflows_completed", labels={"team": team_name})
        self.metrics.record_histogram("workflow_duration_seconds", duration_seconds, 
                                    labels={"team": team_name})
        self.metrics.set_gauge("active_workflows", 
                              self.metrics.counters.get("workflows_started", 0) - 
                              self.metrics.counters.get("workflows_completed", 0))
    
    def record_task_completion(self, task_id: str, team_name: str, success: bool):
        """Record task completion"""
        if success:
            self.metrics.increment_counter("tasks_completed", labels={"team": team_name})
        else:
            self.metrics.increment_counter("tasks_failed", labels={"team": team_name})
            self.metrics.increment_counter("errors")
    
    def record_team_interaction(self, from_team: str, to_team: str, interaction_type: str):
        """Record team interaction"""
        self.metrics.increment_counter("team_interactions", 
                                    labels={"from": from_team, "to": to_team, "type": interaction_type})
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        metrics_summary = self.metrics.get_metrics_summary()
        alert_summary = self.alerts.get_alert_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics_summary,
            "alerts": alert_summary,
            "system_health": {
                "status": "healthy" if alert_summary['active_alerts'] == 0 else "degraded",
                "active_alerts": alert_summary['active_alerts'],
                "critical_alerts": alert_summary['alerts_by_level'].get('critical', 0)
            },
            "productivity_metrics": {
                "workflows_completed": metrics_summary.get('counters', {}).get('workflows_completed', 0),
                "tasks_completed": metrics_summary.get('counters', {}).get('tasks_completed', 0),
                "tasks_failed": metrics_summary.get('counters', {}).get('tasks_failed', 0),
                "error_rate": self._calculate_error_rate(metrics_summary)
            }
        }
    
    def _calculate_error_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate error rate"""
        tasks_completed = metrics.get('counters', {}).get('tasks_completed', 0)
        tasks_failed = metrics.get('counters', {}).get('tasks_failed', 0)
        total_tasks = tasks_completed + tasks_failed
        
        if total_tasks == 0:
            return 0.0
        
        return (tasks_failed / total_tasks) * 100

# Global instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
performance_monitor = PerformanceMonitor(metrics_collector, alert_manager)
