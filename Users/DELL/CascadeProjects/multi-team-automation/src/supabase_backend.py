#!/usr/bin/env python3
"""
MFM Corporation - Supabase Backend System
Complete backend system using Supabase as primary data store
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import os

logger = logging.getLogger(__name__)

class BackendStatus(Enum):
    LOCAL_ONLY = "local_only"
    SUPABASE_ONLY = "supabase_only"
    HYBRID = "hybrid"
    MIGRATING = "migrating"
    FAILED = "failed"

class DataSyncStatus(Enum):
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    ERROR = "error"

@dataclass
class SyncRecord:
    """Data synchronization record"""
    id: str
    data_type: str
    record_id: str
    local_hash: str
    supabase_hash: str
    status: DataSyncStatus
    last_sync: datetime
    conflict_data: Optional[Dict[str, Any]]

class SupabaseBackendSystem:
    """Complete Supabase backend system"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.backend_status = BackendStatus.LOCAL_ONLY
        self.sync_records = {}
        self.local_cache = {}
        self.sync_enabled = True
        self.conflict_resolution = "supabase_wins"  # or "local_wins" or "manual"
        
    async def initialize(self) -> bool:
        """Initialize the Supabase backend system"""
        logger.info("🗄️ Initializing MFM Corporation Supabase Backend System")
        
        try:
            # Test Supabase connection
            if not await self.supabase_manager.test_connection():
                logger.error("❌ Supabase connection failed")
                return False
            
            # Check existing data
            await self._check_existing_data()
            
            # Set up sync tables
            await self._setup_sync_tables()
            
            # Initialize sync records
            await self._initialize_sync_records()
            
            # Determine backend status
            await self._determine_backend_status()
            
            logger.info("✅ Supabase Backend System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Supabase Backend System initialization failed: {e}")
            return False
    
    async def switch_to_supabase_backend(self, force: bool = False) -> bool:
        """Switch to Supabase as primary backend"""
        try:
            logger.info("🔄 Switching to Supabase backend")
            
            if not force and self.backend_status != BackendStatus.LOCAL_ONLY:
                logger.warning("⚠️ Backend is not in local-only mode. Use force=True to override.")
                return False
            
            # Verify Supabase is ready
            if not await self._verify_supabase_readiness():
                logger.error("❌ Supabase is not ready for backend switch")
                return False
            
            # Migrate data if needed
            if not await self._ensure_data_migration():
                logger.error("❌ Data migration failed")
                return False
            
            # Update system configuration
            self.backend_status = BackendStatus.SUPABASE_ONLY
            
            # Test backend functionality
            if not await self._test_backend_functionality():
                logger.error("❌ Backend functionality test failed")
                self.backend_status = BackendStatus.FAILED
                return False
            
            logger.info("✅ Successfully switched to Supabase backend")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to switch to Supabase backend: {e}")
            self.backend_status = BackendStatus.FAILED
            return False
    
    async def enable_hybrid_backend(self) -> bool:
        """Enable hybrid backend (local + Supabase)"""
        try:
            logger.info("🔀 Enabling hybrid backend")
            
            # Verify both backends are working
            local_working = await self._test_local_backend()
            supabase_working = await self._test_supabase_backend()
            
            if not local_working or not supabase_working:
                logger.error("❌ One or both backends are not working")
                return False
            
            # Set up sync configuration
            await self._setup_sync_configuration()
            
            # Update status
            self.backend_status = BackendStatus.HYBRID
            
            logger.info("✅ Hybrid backend enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enable hybrid backend: {e}")
            return False
    
    async def sync_data(self, data_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Sync data between local and Supabase"""
        try:
            if not self.sync_enabled or self.backend_status not in [BackendStatus.HYBRID, BackendStatus.MIGRATING]:
                return True  # No sync needed
            
            # Calculate hashes
            local_hash = self._calculate_hash(data)
            
            # Get Supabase data
            supabase_data = await self._get_supabase_data(data_type, record_id)
            supabase_hash = self._calculate_hash(supabase_data) if supabase_data else ""
            
            # Check if sync is needed
            if local_hash == supabase_hash:
                await self._update_sync_record(data_type, record_id, local_hash, supabase_hash, DataSyncStatus.SYNCED)
                return True
            
            # Handle conflict
            if supabase_data and local_hash != supabase_hash:
                return await self._handle_sync_conflict(data_type, record_id, data, supabase_data)
            
            # No conflict, sync to Supabase
            success = await self._sync_to_supabase(data_type, record_id, data)
            
            if success:
                await self._update_sync_record(data_type, record_id, local_hash, supabase_hash, DataSyncStatus.SYNCED)
            else:
                await self._update_sync_record(data_type, record_id, local_hash, supabase_hash, DataSyncStatus.ERROR)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Data sync failed: {e}")
            return False
    
    async def get_data(self, data_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get data from appropriate backend"""
        try:
            if self.backend_status == BackendStatus.SUPABASE_ONLY:
                return await self._get_supabase_data(data_type, record_id)
            elif self.backend_status == BackendStatus.LOCAL_ONLY:
                return await self._get_local_data(data_type, record_id)
            elif self.backend_status == BackendStatus.HYBRID:
                # Try Supabase first, fallback to local
                data = await self._get_supabase_data(data_type, record_id)
                if not data:
                    data = await self._get_local_data(data_type, record_id)
                return data
            else:
                return await self._get_local_data(data_type, record_id)
                
        except Exception as e:
            logger.error(f"❌ Failed to get data: {e}")
            return None
    
    async def save_data(self, data_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Save data to appropriate backend(s)"""
        try:
            if self.backend_status == BackendStatus.SUPABASE_ONLY:
                return await self._save_supabase_data(data_type, record_id, data)
            elif self.backend_status == BackendStatus.LOCAL_ONLY:
                return await self._save_local_data(data_type, record_id, data)
            elif self.backend_status == BackendStatus.HYBRID:
                # Save to both and sync
                local_success = await self._save_local_data(data_type, record_id, data)
                supabase_success = await self._save_supabase_data(data_type, record_id, data)
                
                if local_success and supabase_success:
                    await self._update_sync_record(data_type, record_id, 
                                                self._calculate_hash(data), 
                                                self._calculate_hash(data), 
                                                DataSyncStatus.SYNCED)
                
                return local_success or supabase_success
            else:
                return await self._save_local_data(data_type, record_id, data)
                
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}")
            return False
    
    async def delete_data(self, data_type: str, record_id: str) -> bool:
        """Delete data from appropriate backend(s)"""
        try:
            if self.backend_status == BackendStatus.SUPABASE_ONLY:
                return await self._delete_supabase_data(data_type, record_id)
            elif self.backend_status == BackendStatus.LOCAL_ONLY:
                return await self._delete_local_data(data_type, record_id)
            elif self.backend_status == BackendStatus.HYBRID:
                # Delete from both
                local_success = await self._delete_local_data(data_type, record_id)
                supabase_success = await self._delete_supabase_data(data_type, record_id)
                
                # Remove sync record
                sync_id = f"{data_type}_{record_id}"
                if sync_id in self.sync_records:
                    del self.sync_records[sync_id]
                
                return local_success or supabase_success
            else:
                return await self._delete_local_data(data_type, record_id)
                
        except Exception as e:
            logger.error(f"❌ Failed to delete data: {e}")
            return False
    
    async def get_backend_status(self) -> Dict[str, Any]:
        """Get current backend status"""
        try:
            return {
                "backend_status": self.backend_status.value,
                "sync_enabled": self.sync_enabled,
                "sync_records": len(self.sync_records),
                "synced_records": len([r for r in self.sync_records.values() if r.status == DataSyncStatus.SYNCED]),
                "pending_syncs": len([r for r in self.sync_records.values() if r.status == DataSyncStatus.PENDING]),
                "conflicts": len([r for r in self.sync_records.values() if r.status == DataSyncStatus.CONFLICT]),
                "errors": len([r for r in self.sync_records.values() if r.status == DataSyncStatus.ERROR]),
                "conflict_resolution": self.conflict_resolution,
                "supabase_connected": await self._test_supabase_backend(),
                "local_working": await self._test_local_backend()
            }
        except Exception as e:
            logger.error(f"Failed to get backend status: {e}")
            return {}
    
    # Private methods
    
    async def _check_existing_data(self):
        """Check existing data in Supabase"""
        try:
            # Check if Supabase has existing data
            tables = ["workflow_states", "team_metrics", "system_metrics", "meetings", "notifications"]
            existing_data = {}
            
            for table in tables:
                count = await self.supabase_manager.count_records(table)
                existing_data[table] = count
            
            logger.info(f"📊 Existing Supabase data: {existing_data}")
            
        except Exception as e:
            logger.error(f"Failed to check existing data: {e}")
    
    async def _setup_sync_tables(self):
        """Set up synchronization tables"""
        try:
            # Create sync tracking table
            await self.supabase_manager.create_table_if_not_exists("data_sync")
            
            logger.info("🗄️ Sync tables configured")
            
        except Exception as e:
            logger.error(f"Failed to setup sync tables: {e}")
    
    async def _initialize_sync_records(self):
        """Initialize sync records"""
        try:
            # Load existing sync records from Supabase
            existing_syncs = await self.supabase_manager.get_data_sync_records()
            
            for sync_record in existing_syncs:
                sync_id = f"{sync_record['data_type']}_{sync_record['record_id']}"
                self.sync_records[sync_id] = SyncRecord(
                    id=sync_record['id'],
                    data_type=sync_record['data_type'],
                    record_id=sync_record['record_id'],
                    local_hash=sync_record['local_hash'],
                    supabase_hash=sync_record['supabase_hash'],
                    status=DataSyncStatus(sync_record['status']),
                    last_sync=datetime.fromisoformat(sync_record['last_sync']),
                    conflict_data=sync_record.get('conflict_data')
                )
            
            logger.info(f"📋 Loaded {len(self.sync_records)} sync records")
            
        except Exception as e:
            logger.error(f"Failed to initialize sync records: {e}")
    
    async def _determine_backend_status(self):
        """Determine current backend status"""
        try:
            supabase_working = await self._test_supabase_backend()
            local_working = await self._test_local_backend()
            
            if supabase_working and local_working:
                self.backend_status = BackendStatus.HYBRID
            elif supabase_working:
                self.backend_status = BackendStatus.SUPABASE_ONLY
            elif local_working:
                self.backend_status = BackendStatus.LOCAL_ONLY
            else:
                self.backend_status = BackendStatus.FAILED
            
            logger.info(f"🔧 Backend status: {self.backend_status.value}")
            
        except Exception as e:
            logger.error(f"Failed to determine backend status: {e}")
            self.backend_status = BackendStatus.FAILED
    
    async def _verify_supabase_readiness(self) -> bool:
        """Verify Supabase is ready for backend switch"""
        try:
            # Test connection
            if not await self.supabase_manager.test_connection():
                return False
            
            # Test table existence
            required_tables = ["workflow_states", "team_metrics", "system_metrics", "meetings", "notifications"]
            for table in required_tables:
                if not await self.supabase_manager.table_exists(table):
                    logger.warning(f"Table {table} does not exist")
                    return False
            
            # Test basic operations
            test_data = {"test": True, "timestamp": datetime.now().isoformat()}
            await self.supabase_manager.save_system_metrics(test_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Supabase readiness check failed: {e}")
            return False
    
    async def _ensure_data_migration(self) -> bool:
        """Ensure data is migrated to Supabase"""
        try:
            # Check if migration is needed
            existing_data = await self.supabase_manager.count_records("workflow_states")
            
            if existing_data > 0:
                logger.info("📊 Data already exists in Supabase")
                return True
            
            # Run migration
            from src.supabase_migration import SupabaseMigrationSystem
            migration_system = SupabaseMigrationSystem(self.supabase_manager)
            
            if await migration_system.initialize():
                results = await migration_system.run_full_migration()
                return results.get("success", False)
            
            return False
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            return False
    
    async def _test_backend_functionality(self) -> bool:
        """Test backend functionality"""
        try:
            # Test save and retrieve
            test_data = {
                "test_id": "backend_test",
                "timestamp": datetime.now().isoformat(),
                "data": {"test": True}
            }
            
            # Save test data
            save_success = await self.save_data("test", "backend_test", test_data)
            if not save_success:
                return False
            
            # Retrieve test data
            retrieved_data = await self.get_data("test", "backend_test")
            if not retrieved_data or retrieved_data.get("test_id") != "backend_test":
                return False
            
            # Clean up
            await self.delete_data("test", "backend_test")
            
            return True
            
        except Exception as e:
            logger.error(f"Backend functionality test failed: {e}")
            return False
    
    async def _test_local_backend(self) -> bool:
        """Test local backend functionality"""
        try:
            # Simulate local backend test
            test_key = "local_backend_test"
            test_data = {"test": True, "timestamp": datetime.now().isoformat()}
            
            # Test local cache
            self.local_cache[test_key] = test_data
            
            # Verify
            retrieved = self.local_cache.get(test_key)
            if not retrieved or retrieved.get("test") != True:
                return False
            
            # Clean up
            del self.local_cache[test_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Local backend test failed: {e}")
            return False
    
    async def _test_supabase_backend(self) -> bool:
        """Test Supabase backend functionality"""
        try:
            return await self.supabase_manager.test_connection()
        except Exception as e:
            logger.error(f"Supabase backend test failed: {e}")
            return False
    
    async def _setup_sync_configuration(self):
        """Set up sync configuration"""
        try:
            # Configure sync settings
            self.sync_enabled = True
            self.conflict_resolution = "supabase_wins"
            
            logger.info("⚙️ Sync configuration updated")
            
        except Exception as e:
            logger.error(f"Failed to setup sync configuration: {e}")
    
    def _calculate_hash(self, data: Any) -> str:
        """Calculate hash of data"""
        try:
            if isinstance(data, dict):
                # Sort keys for consistent hashing
                sorted_data = json.dumps(data, sort_keys=True)
            else:
                sorted_data = str(data)
            
            return hashlib.sha256(sorted_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate hash: {e}")
            return ""
    
    async def _get_supabase_data(self, data_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get data from Supabase"""
        try:
            if data_type == "workflow_states":
                return await self.supabase_manager.get_workflow_state(record_id)
            elif data_type == "team_metrics":
                return await self.supabase_manager.get_team_metrics(record_id)
            elif data_type == "system_metrics":
                return await self.supabase_manager.get_system_metrics()
            elif data_type == "meetings":
                return await self.supabase_manager.get_meeting(record_id)
            elif data_type == "notifications":
                return await self.supabase_manager.get_notification(record_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get Supabase data: {e}")
            return None
    
    async def _get_local_data(self, data_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get data from local cache"""
        try:
            key = f"{data_type}_{record_id}"
            return self.local_cache.get(key)
        except Exception as e:
            logger.error(f"Failed to get local data: {e}")
            return None
    
    async def _save_supabase_data(self, data_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Save data to Supabase"""
        try:
            if data_type == "workflow_states":
                await self.supabase_manager.save_workflow_state(record_id, data)
            elif data_type == "team_metrics":
                await self.supabase_manager.save_team_metrics(record_id, data)
            elif data_type == "system_metrics":
                await self.supabase_manager.save_system_metrics(data)
            elif data_type == "meetings":
                await self.supabase_manager.save_meeting(data)
            elif data_type == "notifications":
                await self.supabase_manager.save_notification(data)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Supabase data: {e}")
            return False
    
    async def _save_local_data(self, data_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Save data to local cache"""
        try:
            key = f"{data_type}_{record_id}"
            self.local_cache[key] = data
            return True
        except Exception as e:
            logger.error(f"Failed to save local data: {e}")
            return False
    
    async def _delete_supabase_data(self, data_type: str, record_id: str) -> bool:
        """Delete data from Supabase"""
        try:
            if data_type == "workflow_states":
                await self.supabase_manager.delete_workflow_state(record_id)
            elif data_type == "team_metrics":
                await self.supabase_manager.delete_team_metrics(record_id)
            elif data_type == "system_metrics":
                # System metrics are not individually deletable
                return False
            elif data_type == "meetings":
                await self.supabase_manager.delete_meeting(record_id)
            elif data_type == "notifications":
                await self.supabase_manager.delete_notification(record_id)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Supabase data: {e}")
            return False
    
    async def _delete_local_data(self, data_type: str, record_id: str) -> bool:
        """Delete data from local cache"""
        try:
            key = f"{data_type}_{record_id}"
            if key in self.local_cache:
                del self.local_cache[key]
            return True
        except Exception as e:
            logger.error(f"Failed to delete local data: {e}")
            return False
    
    async def _sync_to_supabase(self, data_type: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Sync data to Supabase"""
        try:
            return await self._save_supabase_data(data_type, record_id, data)
        except Exception as e:
            logger.error(f"Failed to sync to Supabase: {e}")
            return False
    
    async def _handle_sync_conflict(self, data_type: str, record_id: str, local_data: Dict[str, Any], supabase_data: Dict[str, Any]) -> bool:
        """Handle sync conflict"""
        try:
            logger.warning(f"⚠️ Sync conflict for {data_type}:{record_id}")
            
            if self.conflict_resolution == "supabase_wins":
                # Keep Supabase data, update local
                await self._save_local_data(data_type, record_id, supabase_data)
                return True
            elif self.conflict_resolution == "local_wins":
                # Keep local data, update Supabase
                await self._save_supabase_data(data_type, record_id, local_data)
                return True
            else:  # manual
                # Record conflict for manual resolution
                sync_id = f"{data_type}_{record_id}"
                await self._update_sync_record(data_type, record_id, 
                                            self._calculate_hash(local_data), 
                                            self._calculate_hash(supabase_data), 
                                            DataSyncStatus.CONFLICT)
                
                # Store conflict data
                if sync_id in self.sync_records:
                    self.sync_records[sync_id].conflict_data = {
                        "local": local_data,
                        "supabase": supabase_data
                    }
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to handle sync conflict: {e}")
            return False
    
    async def _update_sync_record(self, data_type: str, record_id: str, local_hash: str, supabase_hash: str, status: DataSyncStatus):
        """Update sync record"""
        try:
            sync_id = f"{data_type}_{record_id}"
            
            if sync_id not in self.sync_records:
                self.sync_records[sync_id] = SyncRecord(
                    id=sync_id,
                    data_type=data_type,
                    record_id=record_id,
                    local_hash=local_hash,
                    supabase_hash=supabase_hash,
                    status=status,
                    last_sync=datetime.now(),
                    conflict_data=None
                )
            else:
                self.sync_records[sync_id].local_hash = local_hash
                self.sync_records[sync_id].supabase_hash = supabase_hash
                self.sync_records[sync_id].status = status
                self.sync_records[sync_id].last_sync = datetime.now()
            
            # Save to Supabase
            await self.supabase_manager.save_data_sync_record({
                "id": sync_id,
                "data_type": data_type,
                "record_id": record_id,
                "local_hash": local_hash,
                "supabase_hash": supabase_hash,
                "status": status.value,
                "last_sync": self.sync_records[sync_id].last_sync.isoformat(),
                "conflict_data": self.sync_records[sync_id].conflict_data
            })
            
        except Exception as e:
            logger.error(f"Failed to update sync record: {e}")
