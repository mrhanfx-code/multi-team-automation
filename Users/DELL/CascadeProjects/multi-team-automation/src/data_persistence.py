"""
Data Persistence and State Management for Multi-Team Automation System
"""

import asyncio
import json
import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import hashlib
import pickle

logger = logging.getLogger(__name__)

@dataclass
class WorkflowState:
    """Workflow state data structure"""
    workflow_id: str
    status: str
    current_team: str
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class TaskState:
    """Task state data structure"""
    task_id: str
    workflow_id: str
    team_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result: Dict[str, Any] = None
    error: Optional[str] = None
    retry_count: int = 0

class DatabaseManager:
    """SQLite database manager for persistence"""
    
    def __init__(self, db_path: str = "automation.db"):
        self.db_path = db_path
        self.connection_pool = None
        
    async def initialize(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await db.commit()
        logger.info(f"Database initialized: {self.db_path}")
    
    async def _create_tables(self, db):
        """Create database tables"""
        # Workflows table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                current_team TEXT,
                started_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                data TEXT,
                metadata TEXT
            )
        """)
        
        # Tasks table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                team_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                result TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
            )
        """)
        
        # Notifications table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                action_required BOOLEAN DEFAULT FALSE,
                deadline TIMESTAMP,
                read BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Meetings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                participants TEXT,
                scheduled_time TIMESTAMP NOT NULL,
                duration_minutes INTEGER NOT NULL,
                agenda TEXT,
                status TEXT DEFAULT 'scheduled',
                outcomes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Team reports table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS team_reports (
                id TEXT PRIMARY KEY,
                team_name TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                report_data TEXT NOT NULL,
                workflow_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_workflow ON tasks(workflow_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_team ON tasks(team_name)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_meetings_time ON meetings(scheduled_time)")
    
    async def save_workflow(self, workflow: WorkflowState) -> bool:
        """Save or update workflow state"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO workflows 
                    (workflow_id, status, current_team, started_at, updated_at, completed_at, data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow.workflow_id,
                    workflow.status,
                    workflow.current_team,
                    workflow.started_at.isoformat(),
                    workflow.updated_at.isoformat(),
                    workflow.completed_at.isoformat() if workflow.completed_at else None,
                    json.dumps(workflow.data) if workflow.data else None,
                    json.dumps(workflow.metadata) if workflow.metadata else None
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save workflow {workflow.workflow_id}: {e}")
            return False
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM workflows WHERE workflow_id = ?",
                    (workflow_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return WorkflowState(
                        workflow_id=row['workflow_id'],
                        status=row['status'],
                        current_team=row['current_team'],
                        started_at=datetime.fromisoformat(row['started_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                        data=json.loads(row['data']) if row['data'] else None,
                        metadata=json.loads(row['metadata']) if row['metadata'] else None
                    )
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
        return None
    
    async def save_task(self, task: TaskState) -> bool:
        """Save or update task state"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO tasks 
                    (task_id, workflow_id, team_name, status, created_at, updated_at, completed_at, result, error, retry_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.task_id,
                    task.workflow_id,
                    task.team_name,
                    task.status,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                    task.completed_at.isoformat() if task.completed_at else None,
                    json.dumps(task.result) if task.result else None,
                    task.error,
                    task.retry_count
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save task {task.task_id}: {e}")
            return False
    
    async def get_workflow_tasks(self, workflow_id: str) -> List[TaskState]:
        """Get all tasks for a workflow"""
        tasks = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM tasks WHERE workflow_id = ? ORDER BY created_at",
                    (workflow_id,)
                )
                rows = await cursor.fetchall()
                
                for row in rows:
                    task = TaskState(
                        task_id=row['task_id'],
                        workflow_id=row['workflow_id'],
                        team_name=row['team_name'],
                        status=row['status'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                        result=json.loads(row['result']) if row['result'] else None,
                        error=row['error'],
                        retry_count=row['retry_count']
                    )
                    tasks.append(task)
        except Exception as e:
            logger.error(f"Failed to get tasks for workflow {workflow_id}: {e}")
        return tasks
    
    async def save_notification(self, notification: Dict[str, Any]) -> bool:
        """Save notification"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO notifications 
                    (id, sender, recipient, message, priority, timestamp, action_required, deadline, read)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    notification['id'],
                    notification['sender'],
                    notification['recipient'],
                    notification['message'],
                    notification['priority'],
                    notification['timestamp'].isoformat(),
                    notification.get('action_required', False),
                    notification['deadline'].isoformat() if notification.get('deadline') else None,
                    notification.get('read', False)
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save notification {notification['id']}: {e}")
            return False
    
    async def get_unread_notifications(self, recipient: str) -> List[Dict[str, Any]]:
        """Get unread notifications for recipient"""
        notifications = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM notifications WHERE recipient = ? AND read = FALSE ORDER BY timestamp DESC",
                    (recipient,)
                )
                rows = await cursor.fetchall()
                
                for row in rows:
                    notification = {
                        'id': row['id'],
                        'sender': row['sender'],
                        'recipient': row['recipient'],
                        'message': row['message'],
                        'priority': row['priority'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'action_required': bool(row['action_required']),
                        'deadline': datetime.fromisoformat(row['deadline']) if row['deadline'] else None,
                        'read': bool(row['read'])
                    }
                    notifications.append(notification)
        except Exception as e:
            logger.error(f"Failed to get notifications for {recipient}: {e}")
        return notifications
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Clean up old completed workflows
                await db.execute(
                    "DELETE FROM workflows WHERE completed_at < ? AND status = 'completed'",
                    (cutoff_date.isoformat(),)
                )
                
                # Clean up old read notifications
                await db.execute(
                    "DELETE FROM notifications WHERE read = TRUE AND timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                
                # Clean up old meetings
                await db.execute(
                    "DELETE FROM meetings WHERE scheduled_time < ? AND status = 'completed'",
                    (cutoff_date.isoformat(),)
                )
                
                await db.commit()
                logger.info(f"Cleaned up data older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

class StateManager:
    """High-level state management for the automation system"""
    
    def __init__(self, db_path: str = "automation.db"):
        self.db = DatabaseManager(db_path)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize state manager"""
        await self.db.initialize()
        logger.info("State manager initialized")
    
    async def create_workflow(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> WorkflowState:
        """Create new workflow"""
        workflow = WorkflowState(
            workflow_id=workflow_id,
            status="created",
            current_team="Research Team",
            started_at=datetime.now(),
            updated_at=datetime.now(),
            data=initial_data or {},
            metadata={}
        )
        
        await self.db.save_workflow(workflow)
        self._cache_workflow(workflow)
        return workflow
    
    async def update_workflow(self, workflow_id: str, **updates) -> bool:
        """Update workflow state"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        for key, value in updates.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.now()
        
        success = await self.db.save_workflow(workflow)
        if success:
            self._cache_workflow(workflow)
        return success
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow with caching"""
        # Check cache first
        if workflow_id in self.cache:
            cached_data, timestamp = self.cache[workflow_id]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Load from database
        workflow = await self.db.get_workflow(workflow_id)
        if workflow:
            self._cache_workflow(workflow)
        return workflow
    
    def _cache_workflow(self, workflow: WorkflowState):
        """Cache workflow data"""
        self.cache[workflow.workflow_id] = (workflow, datetime.now())
    
    async def create_task(self, task_id: str, workflow_id: str, team_name: str, **task_data) -> TaskState:
        """Create new task"""
        task = TaskState(
            task_id=task_id,
            workflow_id=workflow_id,
            team_name=team_name,
            status="created",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **task_data
        )
        
        await self.db.save_task(task)
        return task
    
    async def update_task(self, task_id: str, **updates) -> bool:
        """Update task state"""
        # Get current task (would need to implement get_task method)
        # For now, just update in database
        try:
            async with aiosqlite.connect(self.db.db_path) as db:
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['status', 'result', 'error', 'retry_count']:
                        set_clauses.append(f"{key} = ?")
                        if key in ['result']:
                            values.append(json.dumps(value) if value else None)
                        else:
                            values.append(value)
                
                if set_clauses:
                    set_clauses.append("updated_at = ?")
                    values.append(datetime.now().isoformat())
                    values.append(task_id)
                    
                    await db.execute(
                        f"UPDATE tasks SET {', '.join(set_clauses)} WHERE task_id = ?",
                        values
                    )
                    await db.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
        return False
    
    async def get_workflows_by_status(self, status: str) -> List[WorkflowState]:
        """Get workflows by status"""
        workflows = []
        try:
            async with aiosqlite.connect(self.db.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM workflows WHERE status = ? ORDER BY started_at DESC",
                    (status,)
                )
                rows = await cursor.fetchall()
                
                for row in rows:
                    workflow = WorkflowState(
                        workflow_id=row['workflow_id'],
                        status=row['status'],
                        current_team=row['current_team'],
                        started_at=datetime.fromisoformat(row['started_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                        data=json.loads(row['data']) if row['data'] else None,
                        metadata=json.loads(row['metadata']) if row['metadata'] else None
                    )
                    workflows.append(workflow)
        except Exception as e:
            logger.error(f"Failed to get workflows by status {status}: {e}")
        return workflows
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {}
        try:
            async with aiosqlite.connect(self.db.db_path) as db:
                # Workflow statistics
                cursor = await db.execute("SELECT status, COUNT(*) as count FROM workflows GROUP BY status")
                workflow_stats = {row['status']: row['count'] for row in await cursor.fetchall()}
                
                # Task statistics
                cursor = await db.execute("SELECT team_name, status, COUNT(*) as count FROM tasks GROUP BY team_name, status")
                task_stats = {}
                for row in await cursor.fetchall():
                    team = row['team_name']
                    if team not in task_stats:
                        task_stats[team] = {}
                    task_stats[team][row['status']] = row['count']
                
                # Notification statistics
                cursor = await db.execute("SELECT COUNT(*) as total, SUM(CASE WHEN read = FALSE THEN 1 ELSE 0 END) as unread FROM notifications")
                notification_stats = await cursor.fetchone()
                
                stats = {
                    "workflows": workflow_stats,
                    "tasks": task_stats,
                    "notifications": {
                        "total": notification_stats['total'],
                        "unread": notification_stats['unread']
                    },
                    "generated_at": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
        return stats

class BackupManager:
    """Backup and recovery management"""
    
    def __init__(self, db_path: str = "automation.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_backup(self) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"automation_backup_{timestamp}.db"
        
        try:
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Create backup metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "source_file": self.db_path,
                "backup_file": str(backup_path),
                "file_size": backup_path.stat().st_size,
                "checksum": self._calculate_checksum(backup_path)
            }
            
            metadata_path = self.backup_dir / f"backup_metadata_{timestamp}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Verify backup integrity
            checksum = self._calculate_checksum(backup_file)
            
            # Create current backup before restore
            await self.create_backup()
            
            # Restore backup
            import shutil
            shutil.copy2(backup_file, self.db_path)
            
            logger.info(f"Backup restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    async def cleanup_old_backups(self, keep_count: int = 10):
        """Clean up old backups, keeping only the most recent"""
        try:
            backup_files = sorted(self.backup_dir.glob("automation_backup_*.db"), 
                               key=lambda x: x.stat().st_mtime, reverse=True)
            
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                # Also remove corresponding metadata file
                metadata_file = backup_file.parent / f"backup_metadata_{backup_file.stem.split('_')[-1]}.json"
                if metadata_file.exists():
                    metadata_file.unlink()
            
            logger.info(f"Cleaned up old backups, keeping {keep_count} most recent")
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

# Global state manager instance
state_manager = StateManager()
