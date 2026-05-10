"""
Supabase Integration for Multi-Team Automation System
Provides database, file storage, authentication, and real-time capabilities
"""

import asyncio
import json
import logging
import os
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SupabaseFile:
    """Supabase file metadata"""
    id: str
    name: str
    bucket: str
    size: int
    created_at: datetime
    updated_at: datetime
    path: str
    metadata: Dict[str, Any] = None
    local_path: Optional[str] = None

class SupabaseManager:
    """Manages Supabase integration for database, storage, and real-time features"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be provided or set as environment variables")
        
        self.client = None
        self.file_cache = {}
        self.bucket_name = "multi-team-automation"
        
    async def initialize(self):
        """Initialize Supabase client and setup"""
        try:
            from supabase import create_client, Client
            
            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_key
            )
            
            # Create bucket if it doesn't exist
            await self._setup_storage_bucket()
            
            # Initialize database tables
            await self._setup_database_tables()
            
            logger.info("Supabase integration initialized successfully")
            
        except ImportError:
            logger.error("Supabase library not installed. Install with: pip install supabase")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            raise
    
    async def _setup_storage_bucket(self):
        """Setup storage bucket for file storage"""
        try:
            # Check if bucket exists
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(b['name'] == self.bucket_name for b in buckets)
            
            if not bucket_exists:
                # Create bucket
                self.client.storage.create_bucket(
                    bucket_id=self.bucket_name,
                    options={
                        'public': False,
                        'file_size_limit': 52428800,  # 50MB per file
                        'allowed_mime_types': ['*']
                    }
                )
                logger.info(f"Created Supabase bucket: {self.bucket_name}")
            
            # Set up bucket policies
            await self._setup_bucket_policies()
            
        except Exception as e:
            logger.error(f"Failed to setup storage bucket: {e}")
    
    async def _setup_bucket_policies(self):
        """Setup bucket access policies"""
        try:
            # Policies for team-based access
            policies = [
                {
                    'id': 'team-read-access',
                    'name': 'Team Read Access',
                    'definition': {
                        'actions': ['SELECT'],
                        'effect': 'ALLOW',
                        'principal': {
                            'type': 'role',
                            'value': 'authenticated'
                        },
                        'resource': {
                            'type': 'bucket',
                            'value': self.bucket_name
                        },
                        'condition': {
                            'key': 'path',
                            'match': {
                                'type': 'starts_with',
                                'value': 'team-'
                            }
                        }
                    }
                },
                {
                    'id': 'team-write-access',
                    'name': 'Team Write Access',
                    'definition': {
                        'actions': ['INSERT', 'UPDATE'],
                        'effect': 'ALLOW',
                        'principal': {
                            'type': 'role',
                            'value': 'authenticated'
                        },
                        'resource': {
                            'type': 'bucket',
                            'value': self.bucket_name
                        },
                        'condition': {
                            'key': 'path',
                            'match': {
                                'type': 'starts_with',
                                'value': 'team-'
                            }
                        }
                    }
                }
            ]
            
            for policy in policies:
                try:
                    self.client.storage.create_policy(
                        bucket_id=self.bucket_name,
                        policy=policy
                    )
                except Exception as e:
                    # Policy might already exist
                    logger.debug(f"Policy creation failed (may exist): {e}")
                    
        except Exception as e:
            logger.error(f"Failed to setup bucket policies: {e}")
    
    async def _setup_database_tables(self):
        """Setup database tables for automation system"""
        try:
            # Workflows table
            await self.client.table('workflows').upsert({
                'id': 'schema_check',
                'created_at': datetime.now().isoformat()
            }, on_conflict='ignore').execute()
            
            # Tasks table
            await self.client.table('tasks').upsert({
                'id': 'schema_check',
                'created_at': datetime.now().isoformat()
            }, on_conflict='ignore').execute()
            
            # Team outputs table
            await self.client.table('team_outputs').upsert({
                'id': 'schema_check',
                'created_at': datetime.now().isoformat()
            }, on_conflict='ignore').execute()
            
            # Notifications table
            await self.client.table('notifications').upsert({
                'id': 'schema_check',
                'created_at': datetime.now().isoformat()
            }, on_conflict='ignore').execute()
            
            # Meetings table
            await self.client.table('meetings').upsert({
                'id': 'schema_check',
                'created_at': datetime.now().isoformat()
            }, on_conflict='ignore').execute()
            
            logger.info("Database tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup database tables: {e}")
    
    async def save_workflow_state(self, workflow_id: str, state_data: Dict[str, Any]):
        """Save workflow state to database"""
        try:
            workflow_record = {
                'id': workflow_id,
                'status': state_data.get('status', 'created'),
                'current_team': state_data.get('current_team', 'Research Team'),
                'started_at': state_data.get('started_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'completed_at': state_data.get('completed_at'),
                'data': state_data.get('data', {}),
                'metadata': state_data.get('metadata', {})
            }
            
            result = self.client.table('workflows').upsert(
                workflow_record,
                on_conflict='id'
            ).execute()
            
            logger.info(f"Saved workflow state: {workflow_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to save workflow state {workflow_id}: {e}")
            return None
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state from database"""
        try:
            result = self.client.table('workflows').select('*').eq('id', workflow_id).execute()
            
            if result.data:
                return result.data[0]
                
        except Exception as e:
            logger.error(f"Failed to get workflow state {workflow_id}: {e}")
        
        return None
    
    async def save_task_state(self, task_id: str, task_data: Dict[str, Any]):
        """Save task state to database"""
        try:
            task_record = {
                'id': task_id,
                'workflow_id': task_data.get('workflow_id'),
                'team_name': task_data.get('team_name'),
                'status': task_data.get('status', 'created'),
                'created_at': task_data.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'completed_at': task_data.get('completed_at'),
                'result': task_data.get('result'),
                'error': task_data.get('error'),
                'retry_count': task_data.get('retry_count', 0)
            }
            
            result = self.client.table('tasks').upsert(
                task_record,
                on_conflict='id'
            ).execute()
            
            logger.info(f"Saved task state: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to save task state {task_id}: {e}")
            return None
    
    async def save_team_output(self, team_name: str, output_data: Dict[str, Any], 
                              output_type: str = "report"):
        """Save team output to Supabase storage and database"""
        try:
            # Save to database
            output_record = {
                'id': f"{team_name}_{output_type}_{int(datetime.now().timestamp())}",
                'team_name': team_name,
                'output_type': output_type,
                'timestamp': datetime.now().isoformat(),
                'data': output_data
            }
            
            db_result = self.client.table('team_outputs').insert(output_record).execute()
            
            # Save to storage as JSON file
            filename = f"team_outputs/{team_name}/{output_type}/{output_record['id']}.json"
            file_content = json.dumps(output_data, indent=2, default=str)
            
            storage_result = await self.upload_file(
                content=file_content.encode(),
                path=filename,
                content_type='application/json',
                metadata={
                    'team_name': team_name,
                    'output_type': output_type,
                    'workflow_id': output_data.get('workflow_id'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Saved {output_type} for {team_name} to Supabase")
            return {
                'database_result': db_result,
                'storage_result': storage_result
            }
            
        except Exception as e:
            logger.error(f"Failed to save team output: {e}")
            return None
    
    async def upload_file(self, content: bytes, path: str, content_type: str = 'application/octet-stream',
                       metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Upload file to Supabase storage"""
        try:
            # Calculate file hash
            file_hash = hashlib.md5(content).hexdigest()
            
            # Check if file already exists
            existing_files = self.client.storage.from_(self.bucket_name).list(
                path=path.rsplit('/', 1)[0] if '/' in path else ''
            ).execute()
            
            file_exists = any(f['name'] == path.rsplit('/', 1)[1] for f in existing_files)
            
            if file_exists:
                # Get existing file metadata
                existing_file = next(f for f in existing_files if f['name'] == path.rsplit('/', 1)[1])
                if existing_file and existing_file.get('metadata', {}).get('md5') == file_hash:
                    logger.info(f"File already exists and unchanged: {path}")
                    return existing_file
            
            # Upload file
            result = self.client.storage.from_(self.bucket_name).upload(
                content,
                path=path,
                file_options={
                    'content-type': content_type,
                    'upsert': True,
                    'metadata': {
                        **(metadata or {}),
                        'md5': file_hash,
                        'uploaded_at': datetime.now().isoformat()
                    }
                }
            )
            
            logger.info(f"Uploaded file to Supabase: {path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload file {path}: {e}")
            return None
    
    async def download_file(self, path: str) -> Optional[bytes]:
        """Download file from Supabase storage"""
        try:
            result = self.client.storage.from_(self.bucket_name).download(path).execute()
            
            if result:
                logger.info(f"Downloaded file from Supabase: {path}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to download file {path}: {e}")
        
        return None
    
    async def list_files(self, path: str = "", team_filter: str = None) -> List[Dict[str, Any]]:
        """List files in Supabase storage"""
        try:
            result = self.client.storage.from_(self.bucket_name).list(path=path).execute()
            
            files = []
            for file_data in result:
                # Apply team filter if specified
                if team_filter:
                    file_team = file_data.get('metadata', {}).get('team_name')
                    if file_team != team_filter:
                        continue
                
                files.append({
                    'id': file_data.get('id'),
                    'name': file_data.get('name'),
                    'path': f"{path}/{file_data['name']}" if path else file_data['name'],
                    'size': file_data.get('size', 0),
                    'created_at': file_data.get('created_at'),
                    'metadata': file_data.get('metadata', {}),
                    'bucket': self.bucket_name
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            return []
    
    async def save_notification(self, notification_data: Dict[str, Any]):
        """Save notification to database"""
        try:
            notification = {
                'id': notification_data.get('id', f"notif_{int(datetime.now().timestamp())}"),
                'sender': notification_data.get('sender'),
                'recipient': notification_data.get('recipient'),
                'message': notification_data.get('message'),
                'priority': notification_data.get('priority', 'normal'),
                'timestamp': notification_data.get('timestamp', datetime.now().isoformat()),
                'action_required': notification_data.get('action_required', False),
                'deadline': notification_data.get('deadline'),
                'read': False,
                'metadata': notification_data.get('metadata', {})
            }
            
            result = self.client.table('notifications').insert(notification).execute()
            
            # Trigger real-time notification
            await self._trigger_realtime_notification(notification)
            
            logger.info(f"Saved notification: {notification['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to save notification: {e}")
            return None
    
    async def _trigger_realtime_notification(self, notification: Dict[str, Any]):
        """Trigger real-time notification via Supabase"""
        try:
            # Supabase handles real-time automatically
            # This could be enhanced with webhooks if needed
            pass
        except Exception as e:
            logger.error(f"Failed to trigger realtime notification: {e}")
    
    async def get_notifications(self, recipient: str = None, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications from database"""
        try:
            query = self.client.table('notifications').select('*').order('timestamp.desc')
            
            if recipient:
                query = query.eq('recipient', recipient)
            
            if unread_only:
                query = query.eq('read', False)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return []
    
    async def save_meeting(self, meeting_data: Dict[str, Any]):
        """Save meeting to database"""
        try:
            meeting = {
                'id': meeting_data.get('id', f"meeting_{int(datetime.now().timestamp())}"),
                'title': meeting_data.get('title'),
                'participants': meeting_data.get('participants', []),
                'scheduled_time': meeting_data.get('scheduled_time'),
                'duration_minutes': meeting_data.get('duration_minutes', 60),
                'agenda': meeting_data.get('agenda'),
                'status': meeting_data.get('status', 'scheduled'),
                'outcomes': meeting_data.get('outcomes'),
                'created_at': datetime.now().isoformat(),
                'metadata': meeting_data.get('metadata', {})
            }
            
            result = self.client.table('meetings').insert(meeting).execute()
            
            logger.info(f"Saved meeting: {meeting['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to save meeting: {e}")
            return None
    
    async def get_workflows_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get workflows by status"""
        try:
            result = self.client.table('workflows').select('*').eq('status', status).order('started_at.desc').execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to get workflows by status {status}: {e}")
            return []
    
    async def get_team_outputs(self, team_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get team outputs"""
        try:
            query = self.client.table('team_outputs').select('*').order('timestamp.desc').limit(limit)
            
            if team_name:
                query = query.eq('team_name', team_name)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to get team outputs for {team_name}: {e}")
            return []
    
    async def create_backup(self, backup_type: str = "scheduled", data: Dict[str, Any] = None):
        """Create system backup"""
        try:
            backup_id = f"backup_{backup_type}_{int(datetime.now().timestamp())}"
            
            backup_data = {
                'id': backup_id,
                'backup_type': backup_type,
                'timestamp': datetime.now().isoformat(),
                'data': data or {},
                'metadata': {
                    'version': '1.0.0',
                    'created_by': 'multi-team-automation-system'
                }
            }
            
            # Save to database
            db_result = self.client.table('backups').insert(backup_data).execute()
            
            # Save to storage
            backup_json = json.dumps(backup_data, indent=2, default=str)
            storage_result = await self.upload_file(
                content=backup_json.encode(),
                path=f"backups/{backup_type}/{backup_id}.json",
                content_type='application/json',
                metadata={
                    'backup_type': backup_type,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Created {backup_type} backup: {backup_id}")
            return {
                'database_result': db_result,
                'storage_result': storage_result
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage and usage statistics"""
        try:
            # Get bucket info
            buckets = self.client.storage.list_buckets()
            bucket_info = next((b for b in buckets if b['name'] == self.bucket_name), None)
            
            # Count files by type
            all_files = await self.list_files()
            
            file_stats = {
                'total_files': len(all_files),
                'by_team': {},
                'by_type': {},
                'total_size': sum(f['size'] for f in all_files)
            }
            
            for file_data in all_files:
                metadata = file_data.get('metadata', {})
                
                # Count by team
                team = metadata.get('team_name', 'unknown')
                file_stats['by_team'][team] = file_stats['by_team'].get(team, 0) + 1
                
                # Count by type
                file_type = metadata.get('output_type', 'unknown')
                file_stats['by_type'][file_type] = file_stats['by_type'].get(file_type, 0) + 1
            
            return {
                'storage_info': bucket_info,
                'file_statistics': file_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return {}
    
    async def setup_realtime_subscriptions(self):
        """Setup real-time subscriptions for live updates"""
        try:
            # Subscribe to notifications
            notifications_channel = self.client.channel('notifications').on_postgres_changes(
                schema='public',
                table='notifications',
                event='INSERT'
            ).subscribe()
            
            # Subscribe to workflow updates
            workflows_channel = self.client.channel('workflows').on_postgres_changes(
                schema='public',
                table='workflows',
                event='UPDATE'
            ).subscribe()
            
            logger.info("Real-time subscriptions setup completed")
            
            return {
                'notifications': notifications_channel,
                'workflows': workflows_channel
            }
            
        except Exception as e:
            logger.error(f"Failed to setup real-time subscriptions: {e}")
            return None

# Global instance
supabase_manager = SupabaseManager()
