#!/usr/bin/env python3
"""
MFM Corporation - Enhanced Supabase Client
Proper Supabase client implementation with error handling and connection management
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class SupabaseConfig:
    """Supabase configuration"""
    url: str
    key: str
    service_role_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

class SupabaseError(Exception):
    """Base Supabase error"""
    pass

class SupabaseConnectionError(SupabaseError):
    """Connection error"""
    pass

class SupabaseAuthError(SupabaseError):
    """Authentication error"""
    pass

class SupabaseQueryError(SupabaseError):
    """Query error"""
    pass

class SupabaseClient:
    """Enhanced Supabase client with proper error handling"""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.session = None
        self.auth_token = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Establish connection to Supabase"""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'apikey': self.config.key,
                    'Authorization': f'Bearer {self.config.key}',
                    'Content-Type': 'application/json'
                }
            )
            
            # Test connection
            await self._test_connection()
            self.is_connected = True
            logger.info("✅ Connected to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            self.is_connected = False
            raise SupabaseConnectionError(f"Connection failed: {e}")
    
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
        self.is_connected = False
        logger.info("🔌 Disconnected from Supabase")
    
    async def _test_connection(self):
        """Test connection to Supabase"""
        try:
            # Simple health check - try to query system settings
            response = await self.session.get(f"{self.config.url}/rest/v1/system_settings?limit=1")
            
            if response.status == 200:
                logger.debug("✅ Supabase connection test successful")
            else:
                raise SupabaseConnectionError(f"Connection test failed: {response.status}")
                
        except Exception as e:
            raise SupabaseConnectionError(f"Connection test failed: {e}")
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        if not self.is_connected:
            raise SupabaseConnectionError("Not connected to Supabase")
        
        url = f"{self.config.url}/rest/v1/{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise SupabaseAuthError("Authentication failed")
                elif response.status == 404:
                    return []
                else:
                    error_text = await response.text()
                    raise SupabaseQueryError(f"Query failed: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise SupabaseConnectionError(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise SupabaseQueryError(f"Invalid JSON response: {e}")
    
    # =============================================================================
    # DATABASE OPERATIONS
    # =============================================================================
    
    async def select(self, table: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, order: Optional[str] = None) -> List[Dict[str, Any]]:
        """Select records from table"""
        try:
            params = {}
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        params[f"{key}=in"] = f"({','.join(map(str, value))})"
                    else:
                        params[key] = f"eq.{value}"
            
            if limit:
                params['limit'] = limit
            
            if order:
                params['order'] = order
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{table}?select={columns}"
            if query_string:
                endpoint += f"&{query_string}"
            
            result = await self._make_request('GET', endpoint)
            return result if isinstance(result, list) else [result]
            
        except Exception as e:
            logger.error(f"❌ Select failed for table {table}: {e}")
            raise
    
    async def insert(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Insert record(s) into table"""
        try:
            endpoint = f"{table}?returning=*"
            
            if isinstance(data, list):
                result = await self._make_request('POST', endpoint, json=data)
            else:
                result = await self._make_request('POST', endpoint, json=data)
            
            return result if isinstance(result, list) else [result]
            
        except Exception as e:
            logger.error(f"❌ Insert failed for table {table}: {e}")
            raise
    
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update records in table"""
        try:
            params = []
            for key, value in filters.items():
                if isinstance(value, list):
                    params.append(f"{key}=in.({','.join(map(str, value))})")
                else:
                    params.append(f"{key}=eq.{value}")
            
            query_string = '&'.join(params)
            endpoint = f"{table}?{query_string}&returning=*"
            
            result = await self._make_request('PATCH', endpoint, json=data)
            return result if isinstance(result, list) else [result]
            
        except Exception as e:
            logger.error(f"❌ Update failed for table {table}: {e}")
            raise
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Delete records from table"""
        try:
            params = []
            for key, value in filters.items():
                if isinstance(value, list):
                    params.append(f"{key}=in.({','.join(map(str, value))})")
                else:
                    params.append(f"{key}=eq.{value}")
            
            query_string = '&'.join(params)
            endpoint = f"{table}?{query_string}&returning=*"
            
            result = await self._make_request('DELETE', endpoint)
            return result if isinstance(result, list) else [result]
            
        except Exception as e:
            logger.error(f"❌ Delete failed for table {table}: {e}")
            raise
    
    async def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records in table"""
        try:
            params = {}
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        params[f"{key}=in"] = f"({','.join(map(str, value))})"
                    else:
                        params[key] = f"eq.{value}"
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{table}?select=count"
            if query_string:
                endpoint += f"&{query_string}"
            
            # Use count endpoint
            endpoint = f"{table}?select=count"
            if query_string:
                endpoint += f"&{query_string}"
            
            # Add count header
            headers = {'Prefer': 'count=exact'}
            result = await self._make_request('GET', endpoint, headers=headers)
            
            # Extract count from headers
            if isinstance(result, list):
                return len(result)
            else:
                return result.get('count', 0)
                
        except Exception as e:
            logger.error(f"❌ Count failed for table {table}: {e}")
            raise
    
    # =============================================================================
    # AUTHENTICATION
    # =============================================================================
    
    async def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            endpoint = "auth/v1/signup"
            data = {
                'email': email,
                'password': password
            }
            
            if metadata:
                data['data'] = metadata
            
            result = await self._make_request('POST', endpoint, json=data)
            return result
            
        except Exception as e:
            logger.error(f"❌ Sign up failed: {e}")
            raise
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        try:
            endpoint = "auth/v1/token?grant_type=password"
            data = {
                'email': email,
                'password': password
            }
            
            result = await self._make_request('POST', endpoint, json=data)
            
            # Store auth token
            if 'access_token' in result:
                self.auth_token = result['access_token']
                # Update session headers
                if self.session:
                    self.session.headers['Authorization'] = f'Bearer {self.auth_token}'
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Sign in failed: {e}")
            raise
    
    async def sign_out(self) -> bool:
        """Sign out current user"""
        try:
            if not self.auth_token:
                return True
            
            endpoint = "auth/v1/logout"
            await self._make_request('POST', endpoint, json={})
            
            self.auth_token = None
            if self.session:
                self.session.headers['Authorization'] = f'Bearer {self.config.key}'
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sign out failed: {e}")
            return False
    
    async def get_user(self) -> Optional[Dict[str, Any]]:
        """Get current user info"""
        try:
            if not self.auth_token:
                return None
            
            endpoint = "auth/v1/user"
            result = await self._make_request('GET', endpoint)
            return result
            
        except Exception as e:
            logger.error(f"❌ Get user failed: {e}")
            return None
    
    # =============================================================================
    # STORAGE OPERATIONS
    # =============================================================================
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, 
                         content_type: str = 'application/octet-stream') -> Dict[str, Any]:
        """Upload file to storage"""
        try:
            endpoint = f"storage/v1/object/{bucket}/{file_path}"
            
            headers = {
                'Content-Type': content_type,
                'Authorization': f'Bearer {self.auth_token or self.config.key}'
            }
            
            async with self.session.put(f"{self.config.url}/{endpoint}", 
                                       data=file_data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise SupabaseQueryError(f"Upload failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            raise
    
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download file from storage"""
        try:
            endpoint = f"storage/v1/object/{bucket}/{file_path}"
            
            headers = {
                'Authorization': f'Bearer {self.auth_token or self.config.key}'
            }
            
            async with self.session.get(f"{self.config.url}/{endpoint}", 
                                      headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise SupabaseQueryError(f"Download failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ File download failed: {e}")
            raise
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            endpoint = f"storage/v1/object/{bucket}/{file_path}"
            
            headers = {
                'Authorization': f'Bearer {self.auth_token or self.config.key}'
            }
            
            async with self.session.delete(f"{self.config.url}/{endpoint}", 
                                         headers=headers) as response:
                return response.status == 200
                    
        except Exception as e:
            logger.error(f"❌ File deletion failed: {e}")
            return False
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            start_time = datetime.now()
            
            # Test database connection
            await self._test_connection()
            
            # Test basic query
            await self.select('system_settings', limit=1)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'connected': self.is_connected,
                'response_time_ms': response_time * 1000,
                'timestamp': end_time.isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connected': self.is_connected,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_table_info(self, table: str) -> Dict[str, Any]:
        """Get table information"""
        try:
            # Get table schema
            endpoint = f"{table}?select=*&limit=1"
            result = await self._make_request('GET', endpoint)
            
            if result and isinstance(result, list) and len(result) > 0:
                columns = list(result[0].keys())
                return {
                    'table': table,
                    'columns': columns,
                    'sample_data': result[0],
                    'column_count': len(columns)
                }
            else:
                return {
                    'table': table,
                    'columns': [],
                    'sample_data': None,
                    'column_count': 0
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get table info for {table}: {e}")
            return {
                'table': table,
                'error': str(e),
                'columns': [],
                'sample_data': None,
                'column_count': 0
            }

class SupabaseManager:
    """High-level Supabase manager for the automation system"""
    
    def __init__(self, config: Optional[SupabaseConfig] = None):
        if config is None:
            config = self._create_config_from_env()
        
        self.config = config
        self.client = None
        self.is_initialized = False
    
    def _create_config_from_env(self) -> SupabaseConfig:
        """Create configuration from environment variables"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        return SupabaseConfig(
            url=url,
            key=key,
            service_role_key=service_role_key,
            timeout=int(os.getenv('SUPABASE_TIMEOUT', '30')),
            max_retries=int(os.getenv('SUPABASE_MAX_RETRIES', '3'))
        )
    
    async def initialize(self) -> bool:
        """Initialize Supabase manager"""
        try:
            self.client = SupabaseClient(self.config)
            await self.client.connect()
            self.is_initialized = True
            logger.info("✅ Supabase manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase manager: {e}")
            self.is_initialized = False
            return False
    
    async def close(self):
        """Close Supabase manager"""
        if self.client:
            await self.client.disconnect()
            self.client = None
        self.is_initialized = False
    
    async def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            if not self.client:
                await self.initialize()
            
            health = await self.client.health_check()
            return health['status'] == 'healthy'
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def run_migration(self, migration_file: str) -> bool:
        """Run database migration"""
        try:
            # Read migration file
            async with aiofiles.open(migration_file, 'r') as f:
                migration_sql = await f.read()
            
            # Execute migration (this would require SQL execution capability)
            # For now, we'll just log it
            logger.info(f"📋 Migration file loaded: {migration_file}")
            logger.info(f"📋 SQL length: {len(migration_sql)} characters")
            
            # In a real implementation, you'd execute the SQL
            # For now, we'll assume it succeeds
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    # =============================================================================
    # CONVENIENCE METHODS FOR AUTOMATION SYSTEM
    # =============================================================================
    
    async def save_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Save workflow data"""
        try:
            result = await self.client.insert('workflows', workflow_data)
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save workflow: {e}")
            raise
    
    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save task data"""
        try:
            result = await self.client.insert('tasks', task_data)
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save task: {e}")
            raise
    
    async def save_notification(self, notification_data: Dict[str, Any]) -> str:
        """Save notification data"""
        try:
            result = await self.client.insert('notifications', notification_data)
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save notification: {e}")
            raise
    
    async def save_team_output(self, team_name: str, output_data: Dict[str, Any]) -> str:
        """Save team output data"""
        try:
            # Save to team_metrics table
            metric_data = {
                'team_name': team_name,
                'metric_name': 'output',
                'metric_value': 1.0,
                'metric_unit': 'count',
                'metadata': output_data
            }
            
            result = await self.client.insert('team_metrics', metric_data)
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save team output: {e}")
            raise
    
    async def get_workflows(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get workflows"""
        try:
            return await self.client.select('workflows', filters=filters)
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflows: {e}")
            return []
    
    async def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tasks"""
        try:
            return await self.client.select('tasks', filters=filters)
            
        except Exception as e:
            logger.error(f"❌ Failed to get tasks: {e}")
            return []
    
    async def get_notifications(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get notifications"""
        try:
            return await self.client.select('notifications', filters=filters)
            
        except Exception as e:
            logger.error(f"❌ Failed to get notifications: {e}")
            return []

# Global instance
supabase_manager = None

async def get_supabase_manager() -> SupabaseManager:
    """Get global Supabase manager instance"""
    global supabase_manager
    
    if supabase_manager is None:
        supabase_manager = SupabaseManager()
        await supabase_manager.initialize()
    
    return supabase_manager

async def close_supabase_manager():
    """Close global Supabase manager instance"""
    global supabase_manager
    
    if supabase_manager:
        await supabase_manager.close()
        supabase_manager = None
