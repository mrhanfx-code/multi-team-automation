#!/usr/bin/env python3
"""
MFM Corporation - Scheduled Workflow Triggers System
Comprehensive scheduling system for automated workflows
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import schedule
from croniter import croniter

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ScheduleType(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    INTERVAL = "interval"

@dataclass
class ScheduledWorkflow:
    """Scheduled workflow configuration"""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    schedule_type: Optional[ScheduleType]
    schedule_expression: Optional[str]  # cron expression or interval
    workflow_function: str
    parameters: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    status: WorkflowStatus = WorkflowStatus.PENDING

@dataclass
class WorkflowExecution:
    """Workflow execution record"""
    id: str
    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: WorkflowStatus
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: Optional[float]

class ScheduledWorkflowsSystem:
    """Comprehensive scheduled workflows system"""
    
    def __init__(self, supabase_manager, automation_system):
        self.supabase_manager = supabase_manager
        self.automation_system = automation_system
        self.scheduled_workflows = {}
        self.workflow_executions = []
        self.running_workflows = {}
        self.event_handlers = {}
        self.condition_checkers = {}
        self.scheduler_running = False
        
    async def initialize(self) -> bool:
        """Initialize the scheduled workflows system"""
        logger.info("⏰ Initializing MFM Corporation Scheduled Workflows System")
        
        try:
            # Load scheduled workflows
            await self._load_scheduled_workflows()
            
            # Set up default workflows
            await self._setup_default_workflows()
            
            # Start the scheduler
            await self.start_scheduler()
            
            logger.info("✅ Scheduled Workflows System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Scheduled Workflows System initialization failed: {e}")
            return False
    
    async def create_scheduled_workflow(self, name: str, description: str,
                                       trigger_type: TriggerType,
                                       schedule_type: Optional[ScheduleType],
                                       schedule_expression: Optional[str],
                                       workflow_function: str,
                                       parameters: Dict[str, Any],
                                       enabled: bool = True) -> str:
        """Create a new scheduled workflow"""
        try:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.scheduled_workflows)}"
            
            # Calculate next run time
            next_run = None
            if schedule_expression and schedule_type:
                next_run = self._calculate_next_run(schedule_type, schedule_expression)
            
            workflow = ScheduledWorkflow(
                id=workflow_id,
                name=name,
                description=description,
                trigger_type=trigger_type,
                schedule_type=schedule_type,
                schedule_expression=schedule_expression,
                workflow_function=workflow_function,
                parameters=parameters,
                enabled=enabled,
                created_at=datetime.now(),
                next_run=next_run
            )
            
            self.scheduled_workflows[workflow_id] = workflow
            
            # Save to Supabase
            await self.supabase_manager.save_scheduled_workflow(asdict(workflow))
            
            logger.info(f"✅ Scheduled workflow created: {name}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create scheduled workflow: {e}")
            return ""
    
    async def trigger_manual_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Manually trigger a workflow"""
        try:
            if workflow_id not in self.scheduled_workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return ""
            
            workflow = self.scheduled_workflows[workflow_id]
            
            # Override parameters if provided
            exec_params = parameters or workflow.parameters
            
            # Execute workflow
            execution_id = await self._execute_workflow(workflow, exec_params, "manual")
            
            logger.info(f"🔨 Manual workflow triggered: {workflow.name}")
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger manual workflow: {e}")
            return ""
    
    async def trigger_event_based_workflow(self, event_type: str, event_data: Dict[str, Any]) -> List[str]:
        """Trigger workflows based on events"""
        execution_ids = []
        
        try:
            # Find workflows that match this event
            matching_workflows = [
                w for w in self.scheduled_workflows.values()
                if w.trigger_type == TriggerType.EVENT_BASED and w.enabled
            ]
            
            for workflow in matching_workflows:
                # Check if this workflow should handle this event
                if await self._should_handle_event(workflow, event_type, event_data):
                    execution_id = await self._execute_workflow(workflow, event_data, "event")
                    execution_ids.append(execution_id)
            
            logger.info(f"🎯 Event-based workflows triggered: {len(execution_ids)}")
            return execution_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger event-based workflows: {e}")
            return []
    
    async def start_scheduler(self):
        """Start the workflow scheduler"""
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return
        
        self.scheduler_running = True
        logger.info("🔄 Starting workflow scheduler")
        
        # Start scheduler task
        asyncio.create_task(self._scheduler_loop())
    
    async def stop_scheduler(self):
        """Stop the workflow scheduler"""
        self.scheduler_running = False
        logger.info("⏹️ Workflow scheduler stopped")
    
    async def get_scheduled_workflows(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get all scheduled workflows"""
        workflows = list(self.scheduled_workflows.values())
        
        if enabled_only:
            workflows = [w for w in workflows if w.enabled]
        
        return [asdict(w) for w in workflows]
    
    async def get_workflow_executions(self, workflow_id: Optional[str] = None,
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        executions = self.workflow_executions
        
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        
        # Sort by started_at (newest first)
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        # Limit results
        executions = executions[:limit]
        
        return [asdict(e) for e in executions]
    
    async def enable_workflow(self, workflow_id: str) -> bool:
        """Enable a scheduled workflow"""
        try:
            if workflow_id in self.scheduled_workflows:
                self.scheduled_workflows[workflow_id].enabled = True
                await self.supabase_manager.update_workflow_status(workflow_id, True)
                logger.info(f"✅ Workflow enabled: {workflow_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to enable workflow: {e}")
            return False
    
    async def disable_workflow(self, workflow_id: str) -> bool:
        """Disable a scheduled workflow"""
        try:
            if workflow_id in self.scheduled_workflows:
                self.scheduled_workflows[workflow_id].enabled = False
                await self.supabase_manager.update_workflow_status(workflow_id, False)
                logger.info(f"⏸️ Workflow disabled: {workflow_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to disable workflow: {e}")
            return False
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                # Check for scheduled workflows to run
                for workflow in self.scheduled_workflows.values():
                    if (workflow.enabled and 
                        workflow.trigger_type == TriggerType.SCHEDULED and
                        workflow.next_run and
                        workflow.next_run <= current_time):
                        
                        # Execute workflow
                        await self._execute_workflow(workflow, workflow.parameters, "scheduled")
                        
                        # Update next run time
                        workflow.next_run = self._calculate_next_run(
                            workflow.schedule_type, workflow.schedule_expression
                        )
                
                # Check conditional workflows
                await self._check_conditional_workflows()
                
                # Wait for next check (check every minute)
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _execute_workflow(self, workflow: ScheduledWorkflow, parameters: Dict[str, Any], 
                               trigger_source: str) -> str:
        """Execute a workflow"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.workflow_executions)}"
        
        # Create execution record
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow.id,
            started_at=datetime.now(),
            completed_at=None,
            status=WorkflowStatus.RUNNING,
            result=None,
            error_message=None,
            execution_time=None
        )
        
        self.workflow_executions.append(execution)
        self.running_workflows[workflow.id] = execution
        
        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        workflow.last_run = datetime.now()
        workflow.run_count += 1
        
        try:
            start_time = datetime.now()
            
            # Execute the workflow function
            if workflow.workflow_function == "run_complete_workflow":
                result = await self.automation_system.run_complete_workflow(
                    parameters.get("research_topic", "Automated Workflow"),
                    parameters.get("research_scope", "Automated scope")
                )
            elif workflow.workflow_function == "innovation_research":
                result = await self.automation_system.innovation_team.conduct_innovation_research(
                    parameters.get("innovation_focus", "Automated Innovation Research"),
                    parameters.get("research_scope", "Automated scope")
                )
            elif workflow.workflow_function == "market_intelligence":
                result = await self.automation_system.market_intelligence_team.conduct_market_intelligence(
                    parameters.get("market_focus", "Automated Market Analysis"),
                    parameters.get("analysis_scope", "Automated scope")
                )
            else:
                # Default to complete workflow
                result = await self.automation_system.run_complete_workflow(
                    parameters.get("research_topic", "Automated Workflow"),
                    parameters.get("research_scope", "Automated scope")
                )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update execution record
            execution.completed_at = end_time
            execution.status = WorkflowStatus.COMPLETED
            execution.result = result
            execution.execution_time = execution_time
            
            # Update workflow status
            workflow.status = WorkflowStatus.COMPLETED
            
            # Send notification
            if self.automation_system.notifications_system:
                await self.automation_system.notifications_system.send_notification(
                    notification_type=self.automation_system.notifications_system.NotificationType.SUCCESS,
                    title=f"Workflow Completed: {workflow.name}",
                    message=f"Workflow {workflow.name} completed successfully in {execution_time:.2f} seconds",
                    team_name="System",
                    priority="medium"
                )
            
            logger.info(f"✅ Workflow executed: {workflow.name} ({execution_time:.2f}s)")
            
        except Exception as e:
            # Update execution record with error
            execution.completed_at = datetime.now()
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            
            # Update workflow status
            workflow.status = WorkflowStatus.FAILED
            
            # Send error notification
            if self.automation_system.notifications_system:
                await self.automation_system.notifications_system.send_notification(
                    notification_type=self.automation_system.notifications_system.NotificationType.ERROR,
                    title=f"Workflow Failed: {workflow.name}",
                    message=f"Workflow {workflow.name} failed: {str(e)}",
                    team_name="System",
                    priority="high"
                )
            
            logger.error(f"❌ Workflow failed: {workflow.name} - {e}")
        
        finally:
            # Remove from running workflows
            if workflow.id in self.running_workflows:
                del self.running_workflows[workflow.id]
            
            # Save execution to Supabase
            await self.supabase_manager.save_workflow_execution(asdict(execution))
        
        return execution_id
    
    def _calculate_next_run(self, schedule_type: ScheduleType, schedule_expression: str) -> Optional[datetime]:
        """Calculate next run time based on schedule"""
        try:
            if schedule_type == ScheduleType.CRON:
                cron = croniter(schedule_expression, datetime.now())
                return cron.get_next(datetime)
            elif schedule_type == ScheduleType.DAILY:
                return datetime.now() + timedelta(days=1)
            elif schedule_type == ScheduleType.WEEKLY:
                return datetime.now() + timedelta(weeks=1)
            elif schedule_type == ScheduleType.MONTHLY:
                return datetime.now() + timedelta(days=30)
            elif schedule_type == ScheduleType.INTERVAL:
                # Parse interval (e.g., "30m", "2h", "1d")
                interval_str = schedule_expression.lower()
                if interval_str.endswith('m'):
                    minutes = int(interval_str[:-1])
                    return datetime.now() + timedelta(minutes=minutes)
                elif interval_str.endswith('h'):
                    hours = int(interval_str[:-1])
                    return datetime.now() + timedelta(hours=hours)
                elif interval_str.endswith('d'):
                    days = int(interval_str[:-1])
                    return datetime.now() + timedelta(days=days)
            elif schedule_type == ScheduleType.ONCE:
                # Parse specific datetime
                return datetime.strptime(schedule_expression, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Failed to calculate next run time: {e}")
        
        return None
    
    async def _should_handle_event(self, workflow: ScheduledWorkflow, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Check if workflow should handle an event"""
        # Simple event matching - can be extended
        workflow_events = workflow.parameters.get("event_types", [])
        return event_type in workflow_events
    
    async def _check_conditional_workflows(self):
        """Check conditional workflows"""
        for workflow in self.scheduled_workflows.values():
            if (workflow.enabled and 
                workflow.trigger_type == TriggerType.CONDITIONAL and
                workflow.status != WorkflowStatus.RUNNING):
                
                # Check conditions
                if await self._evaluate_conditions(workflow.parameters.get("conditions", {})):
                    await self._execute_workflow(workflow, workflow.parameters, "conditional")
    
    async def _evaluate_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions"""
        try:
            # Simple condition evaluation - can be extended
            condition_type = conditions.get("type", "always")
            
            if condition_type == "always":
                return True
            elif condition_type == "time_based":
                # Check if current time meets conditions
                current_hour = datetime.now().hour
                target_hour = conditions.get("hour")
                return current_hour == target_hour
            elif condition_type == "performance_based":
                # Check system performance
                if self.automation_system.tracking_dashboard:
                    system_health = await self.automation_system.tracking_dashboard._calculate_system_health()
                    threshold = conditions.get("performance_threshold", 0.9)
                    return system_health < threshold
            elif condition_type == "event_based":
                # Check if specific events occurred
                # This would require event tracking
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to evaluate conditions: {e}")
            return False
    
    async def _load_scheduled_workflows(self):
        """Load scheduled workflows from Supabase"""
        try:
            # Simulate loading workflows
            self.scheduled_workflows = {}
            logger.info("📋 Scheduled workflows loaded")
        except Exception as e:
            logger.error(f"Failed to load scheduled workflows: {e}")
    
    async def _setup_default_workflows(self):
        """Set up default scheduled workflows"""
        default_workflows = [
            {
                "name": "Daily Innovation Scan",
                "description": "Daily scan for new innovations and trends",
                "trigger_type": TriggerType.SCHEDULED,
                "schedule_type": ScheduleType.DAILY,
                "schedule_expression": "09:00",
                "workflow_function": "innovation_research",
                "parameters": {
                    "innovation_focus": "Emerging AI Technologies",
                    "research_scope": "Daily trend analysis"
                }
            },
            {
                "name": "Weekly Market Intelligence",
                "description": "Weekly market analysis and demand tracking",
                "trigger_type": TriggerType.SCHEDULED,
                "schedule_type": ScheduleType.WEEKLY,
                "schedule_expression": "Monday 10:00",
                "workflow_function": "market_intelligence",
                "parameters": {
                    "market_focus": "AI Automation Market",
                    "analysis_scope": "Weekly market trends"
                }
            },
            {
                "name": "Monthly Technology Review",
                "description": "Monthly review of latest tools and technologies",
                "trigger_type": TriggerType.SCHEDULED,
                "schedule_type": ScheduleType.MONTHLY,
                "schedule_expression": "1st of month 09:00",
                "workflow_function": "technology_monitoring",
                "parameters": {
                    "monitoring_focus": "Development Tools",
                    "analysis_scope": "Monthly technology review"
                }
            },
            {
                "name": "Performance Alert Check",
                "description": "Check system performance and send alerts if needed",
                "trigger_type": TriggerType.CONDITIONAL,
                "schedule_type": None,
                "schedule_expression": None,
                "workflow_function": "performance_check",
                "parameters": {
                    "conditions": {
                        "type": "performance_based",
                        "performance_threshold": 0.85
                    }
                }
            }
        ]
        
        for workflow_config in default_workflows:
            await self.create_scheduled_workflow(**workflow_config)
        
        logger.info("📋 Default scheduled workflows created")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.scheduler_running,
            "total_workflows": len(self.scheduled_workflows),
            "enabled_workflows": len([w for w in self.scheduled_workflows.values() if w.enabled]),
            "running_workflows": len(self.running_workflows),
            "total_executions": len(self.workflow_executions),
            "last_execution": self.workflow_executions[-1].started_at.isoformat() if self.workflow_executions else None
        }
