"""
Simple Supabase Integration for Multi-Team Automation System
Uses direct HTTP requests to avoid complex dependencies
"""

import asyncio
import json
import logging
import os
import base64
import hashlib
import aiohttp
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SupabaseConfig:
    """Supabase configuration"""
    url: str
    key: str
    bucket: str = "multi-team-automation"

class SimpleSupabaseManager:
    """Simplified Supabase manager using HTTP requests"""
    
    def __init__(self, config: SupabaseConfig = None):
        if config:
            self.config = config
        else:
            self.config = SupabaseConfig(
                url=os.getenv('SUPABASE_URL', ''),
                key=os.getenv('SUPABASE_KEY', '')
            )
        
        if not self.config.url or not self.config.key:
            raise ValueError("Supabase URL and key must be provided or set as environment variables")
        
        self.headers = {
            'apikey': self.config.key,
            'Authorization': f'Bearer {self.config.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
    async def initialize(self):
        """Initialize Supabase connection and setup"""
        try:
            # Create SSL context that ignores certificate verification errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Test connection with relaxed SSL
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.url}/rest/v1/",
                    headers=self.headers,
                    ssl=ssl_context
                ) as response:
                    if response.status == 200:
                        logger.info("Supabase connection successful")
                        await self._setup_storage()
                        await self._setup_tables()
                        return True
                    else:
                        logger.error(f"Supabase connection failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            return False
    
    async def _setup_storage(self):
        """Setup storage bucket"""
        try:
            # Check if bucket exists (simplified - assume it does)
            logger.info(f"Using Supabase bucket: {self.config.bucket}")
            return True
        except Exception as e:
            logger.error(f"Failed to setup storage: {e}")
            return False
    
    async def _setup_tables(self):
        """Setup database tables"""
        try:
            # Create tables using simple HTTP requests
            tables = [
                {
                    'name': 'workflows',
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS workflows (
                            id TEXT PRIMARY KEY,
                            status TEXT NOT NULL,
                            current_team TEXT,
                            started_at TIMESTAMP NOT NULL,
                            updated_at TIMESTAMP NOT NULL,
                            completed_at TIMESTAMP,
                            data JSONB,
                            metadata JSONB
                        );
                    '''
                },
                {
                    'name': 'tasks',
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS tasks (
                            id TEXT PRIMARY KEY,
                            workflow_id TEXT NOT NULL,
                            team_name TEXT NOT NULL,
                            status TEXT NOT NULL,
                            created_at TIMESTAMP NOT NULL,
                            updated_at TIMESTAMP NOT NULL,
                            completed_at TIMESTAMP,
                            result JSONB,
                            error TEXT,
                            retry_count INTEGER DEFAULT 0
                        );
                    '''
                },
                {
                    'name': 'team_outputs',
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS team_outputs (
                            id TEXT PRIMARY KEY,
                            team_name TEXT NOT NULL,
                            output_type TEXT NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            data JSONB NOT NULL
                        );
                    '''
                },
                {
                    'name': 'notifications',
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS notifications (
                            id TEXT PRIMARY KEY,
                            sender TEXT NOT NULL,
                            recipient TEXT NOT NULL,
                            message TEXT NOT NULL,
                            priority TEXT NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            action_required BOOLEAN DEFAULT FALSE,
                            deadline TIMESTAMP,
                            read BOOLEAN DEFAULT FALSE,
                            metadata JSONB
                        );
                    '''
                },
                {
                    'name': 'meetings',
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS meetings (
                            id TEXT PRIMARY KEY,
                            title TEXT NOT NULL,
                            participants TEXT[],
                            scheduled_time TIMESTAMP NOT NULL,
                            duration_minutes INTEGER NOT NULL,
                            agenda TEXT,
                            status TEXT DEFAULT 'scheduled',
                            outcomes TEXT,
                            created_at TIMESTAMP DEFAULT NOW(),
                            metadata JSONB
                        );
                    '''
                }
            ]
            
            for table in tables:
                await self._execute_sql(table['sql'])
                logger.info(f"Created table: {table['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup tables: {e}")
            return False
    
    async def _execute_sql(self, sql: str):
        """Execute SQL using Supabase RPC"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.url}/rest/v1/rpc/sql",
                    headers=self.headers,
                    json={'query': sql}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"SQL execution failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            return None
    
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.url}/rest/v1/workflows",
                    headers=self.headers,
                    json=workflow_record
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Saved workflow state: {workflow_id}")
                        return await response.json()
                    else:
                        logger.error(f"Failed to save workflow: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to save workflow state {workflow_id}: {e}")
            return None
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state from database"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.url}/rest/v1/workflows?id=eq.{workflow_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[0] if data else None
                    else:
                        logger.error(f"Failed to get workflow: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to get workflow state {workflow_id}: {e}")
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
            
            async with aiohttp.ClientSession() as session:
                # Database save
                db_response = await session.post(
                    f"{self.config.url}/rest/v1/team_outputs",
                    headers=self.headers,
                    json=output_record
                )
                
                # Storage save
                filename = f"team_outputs/{team_name}/{output_type}/{output_record['id']}.json"
                file_content = json.dumps(output_data, indent=2, default=str)
                
                storage_data = {
                    'file': base64.b64encode(file_content.encode()).decode(),
                    'path': filename
                }
                
                storage_response = await session.post(
                    f"{self.config.url}/rest/v1/storage/upload",
                    headers=self.headers,
                    json=storage_data
                )
                
                if db_response.status in [200, 201] and storage_response.status in [200, 201]:
                    logger.info(f"Saved {output_type} for {team_name} to Supabase")
                    return {
                        'database_result': await db_response.json(),
                        'storage_result': await storage_response.json()
                    }
                else:
                    logger.error(f"Failed to save team output: db={db_response.status}, storage={storage_response.status}")
                    return None
                        
        except Exception as e:
            logger.error(f"Failed to save team output: {e}")
            return None
    
    async def upload_file(self, content: bytes, path: str, content_type: str = 'application/octet-stream',
                       metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Upload file to Supabase storage"""
        try:
            file_hash = hashlib.md5(content).hexdigest()
            
            storage_data = {
                'file': base64.b64encode(content).decode(),
                'path': path,
                'fileOptions': {
                    'contentType': content_type,
                    'upsert': True,
                    'metadata': {
                        **(metadata or {}),
                        'md5': file_hash,
                        'uploaded_at': datetime.now().isoformat()
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.url}/rest/v1/storage/upload",
                    headers=self.headers,
                    json=storage_data
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Uploaded file to Supabase: {path}")
                        return await response.json()
                    else:
                        logger.error(f"Failed to upload file: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to upload file {path}: {e}")
            return None
    
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.url}/rest/v1/notifications",
                    headers=self.headers,
                    json=notification
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Saved notification: {notification['id']}")
                        return await response.json()
                    else:
                        logger.error(f"Failed to save notification: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to save notification: {e}")
            return None
    
    async def get_notifications(self, recipient: str = None, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications from database"""
        try:
            url = f"{self.config.url}/rest/v1/notifications?order=timestamp.desc"
            
            if recipient:
                url += f"&recipient=eq.{recipient}"
            
            if unread_only:
                url += "&read=eq.false"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data or []
                    else:
                        logger.error(f"Failed to get notifications: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
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
            
            # Save backup to storage
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
            
            if storage_result:
                logger.info(f"Created {backup_type} backup: {backup_id}")
                return storage_result
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage and usage statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get bucket info
                async with session.get(
                    f"{self.config.url}/rest/v1/storage/buckets",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        buckets = await response.json()
                        bucket_info = next((b for b in buckets if b['name'] == self.config.bucket), None)
                        
                        # List files
                        files_response = await session.get(
                            f"{self.config.url}/rest/v1/storage/object/list?bucket={self.config.bucket}",
                            headers=self.headers
                        )
                        
                        file_stats = {
                            'total_files': 0,
                            'by_team': {},
                            'by_type': {},
                            'total_size': 0
                        }
                        
                        if files_response.status == 200:
                            files = await files_response.json()
                            file_stats['total_files'] = len(files)
                            
                            for file_data in files:
                                metadata = file_data.get('metadata', {})
                                path_parts = file_data['name'].split('/')
                                
                                # Team-based stats
                                if len(path_parts) >= 2 and path_parts[0] == 'team_outputs':
                                    team = metadata.get('team_name', 'unknown')
                                    file_stats['by_team'][team] = file_stats['by_team'].get(team, 0) + 1
                                
                                # Type-based stats
                                if len(path_parts) >= 3:
                                    file_type = path_parts[1]
                                    file_stats['by_type'][file_type] = file_stats['by_type'].get(file_type, 0) + 1
                                
                                file_stats['total_size'] += file_data.get('size', 0)
                        
                        return {
                            'storage_info': bucket_info,
                            'file_statistics': file_stats,
                            'generated_at': datetime.now().isoformat()
                        }
                    else:
                        logger.error(f"Failed to get bucket info: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return {}

# Global instance (lazy initialization)
supabase_manager = None

def get_supabase_manager():
    """Get or create Supabase manager instance"""
    global supabase_manager
    if supabase_manager is None:
        supabase_manager = SimpleSupabaseManager()
    return supabase_manager
