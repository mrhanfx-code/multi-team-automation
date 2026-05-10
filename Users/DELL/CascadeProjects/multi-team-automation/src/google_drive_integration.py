"""
Google Drive Integration for Multi-Team Automation System
Provides file storage, synchronization, and organization capabilities
"""

import asyncio
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class DriveFile:
    """Google Drive file metadata"""
    id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    parents: List[str]
    md5_checksum: Optional[str] = None
    local_path: Optional[str] = None

class GoogleDriveManager:
    """Manages Google Drive integration for file storage and organization"""
    
    def __init__(self, credentials_path: str = "credentials.json", 
                 token_path: str = "token.pickle",
                 local_sync_path: str = "google_drive_sync"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.local_sync_path = Path(local_sync_path)
        self.local_sync_path.mkdir(exist_ok=True)
        
        self.service = None
        self.file_cache = {}
        self.sync_queue = []
        self.folder_structure = {}
        
    async def initialize(self):
        """Initialize Google Drive service"""
        try:
            await self._authenticate()
            await self._setup_folder_structure()
            await self._initial_sync()
            logger.info("Google Drive integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive: {e}")
            raise
    
    async def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            
            # If modifying these scopes, delete the file token.pickle.
            SCOPES = ['https://www.googleapis.com/auth/drive']
            
            creds = None
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive authentication successful")
            
        except ImportError:
            logger.error("Google Drive libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            raise
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            raise
    
    async def _setup_folder_structure(self):
        """Create organized folder structure in Google Drive"""
        folder_config = {
            "Multi-Team Automation": {
                "description": "Root folder for multi-team automation system",
                "subfolders": {
                    "01_Research": {
                        "description": "Research team outputs and reports",
                        "subfolders": {
                            "Market_Research": {},
                            "Technical_Research": {},
                            "Competitive_Analysis": {},
                            "User_Research": {},
                            "Industry_Analysis": {}
                        }
                    },
                    "02_Planning": {
                        "description": "Planning team documents and plans",
                        "subfolders": {
                            "Project_Plans": {},
                            "Resource_Plans": {},
                            "Strategic_Plans": {},
                            "Timeline_Plans": {},
                            "Budget_Plans": {},
                            "Risk_Plans": {}
                        }
                    },
                    "03_Development": {
                        "description": "Development team outputs and code",
                        "subfolders": {
                            "Source_Code": {},
                            "Documentation": {},
                            "Tests": {},
                            "Deployments": {},
                            "Prototypes": {}
                        }
                    },
                    "04_Management": {
                        "description": "Management team reports and decisions",
                        "subfolders": {
                            "Reviews": {},
                            "Decisions": {},
                            "Quality_Assurance": {},
                            "Security_Reports": {},
                            "Performance_Reports": {}
                        }
                    },
                    "05_General_Manager": {
                        "description": "General manager reports and approvals",
                        "subfolders": {
                            "Final_Reports": {},
                            "Executive_Summaries": {},
                            "Approvals": {},
                            "Strategic_Overview": {}
                        }
                    },
                    "06_Workflows": {
                        "description": "Complete workflow executions and archives",
                        "subfolders": {
                            "Active": {},
                            "Completed": {},
                            "Archived": {},
                            "Templates": {}
                        }
                    },
                    "07_Meetings": {
                        "description": "Meeting records and materials",
                        "subfolders": {
                            "Schedules": {},
                            "Minutes": {},
                            "Materials": {},
                            "Action_Items": {}
                        }
                    },
                    "08_Notifications": {
                        "description": "Notification logs and communications",
                        "subfolders": {
                            "Team_Notifications": {},
                            "Escalations": {},
                            "Alerts": {},
                            "Reports": {}
                        }
                    },
                    "09_Backups": {
                        "description": "System backups and archives",
                        "subfolders": {
                            "Daily": {},
                            "Weekly": {},
                            "Monthly": {},
                            "Emergency": {}
                        }
                    },
                    "10_Configuration": {
                        "description": "Configuration files and settings",
                        "subfolders": {
                            "Team_Settings": {},
                            "Workflow_Templates": {},
                            "API_Configs": {},
                            "Environment_Settings": {}
                        }
                    }
                }
            }
        }
        
        await self._create_folder_structure(folder_config)
    
    async def _create_folder_structure(self, config: Dict[str, Any], parent_id: str = None):
        """Recursively create folder structure"""
        for folder_name, folder_info in config.items():
            try:
                # Check if folder already exists
                folder_id = await self._find_folder_by_name(folder_name, parent_id)
                
                if not folder_id:
                    # Create new folder
                    folder_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [parent_id] if parent_id else [],
                        'description': folder_info.get('description', '')
                    }
                    
                    folder = self.service.files().create(
                        body=folder_metadata,
                        fields='id'
                    ).execute()
                    
                    folder_id = folder.get('id')
                    logger.info(f"Created folder: {folder_name}")
                
                # Store in folder structure
                self.folder_structure[folder_name] = {
                    'id': folder_id,
                    'parent_id': parent_id,
                    'path': self._get_folder_path(folder_name, parent_id)
                }
                
                # Create subfolders
                if 'subfolders' in folder_info:
                    await self._create_folder_structure(folder_info['subfolders'], folder_id)
                    
            except Exception as e:
                logger.error(f"Failed to create folder {folder_name}: {e}")
    
    async def _find_folder_by_name(self, name: str, parent_id: str = None) -> Optional[str]:
        """Find folder by name and parent"""
        try:
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields='files(id, name, parents)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
                
        except Exception as e:
            logger.error(f"Error finding folder {name}: {e}")
        
        return None
    
    def _get_folder_path(self, folder_name: str, parent_id: str = None) -> str:
        """Get full path for folder"""
        if parent_id:
            # Find parent folder name
            for name, info in self.folder_structure.items():
                if info['id'] == parent_id:
                    return f"{info['path']}/{folder_name}"
        return folder_name
    
    async def _initial_sync(self):
        """Perform initial synchronization"""
        try:
            # Sync local project files to Google Drive
            await self.sync_project_files()
            
            # Create initial backup
            await self.create_system_backup("initial_setup")
            
            logger.info("Initial sync completed")
            
        except Exception as e:
            logger.error(f"Initial sync failed: {e}")
    
    async def sync_project_files(self):
        """Sync project files to Google Drive"""
        project_root = Path.cwd().parent
        
        # Define file mappings to Google Drive folders
        file_mappings = {
            "src": "10_Configuration/Team_Settings",
            "requirements.txt": "10_Configuration/Environment_Settings", 
            "README.md": "10_Configuration",
            ".github": "10_Configuration/API_Configs",
            "reports": "06_Workflows/Active",
            "backups": "09_Backups/Daily",
            "logs": "08_Notifications/Reports"
        }
        
        for local_path, drive_folder in file_mappings.items():
            local_full_path = project_root / local_path
            
            if local_full_path.exists():
                await self._sync_directory(local_full_path, drive_folder)
    
    async def _sync_directory(self, local_dir: Path, drive_folder_id: str):
        """Sync a directory to Google Drive"""
        try:
            # Get drive folder ID from folder structure
            folder_id = None
            for name, info in self.folder_structure.items():
                if drive_folder_id in info['path']:
                    folder_id = info['id']
                    break
            
            if not folder_id:
                logger.warning(f"Drive folder not found: {drive_folder_id}")
                return
            
            # Sync files
            for file_path in local_dir.rglob('*'):
                if file_path.is_file():
                    await self._upload_file(file_path, folder_id)
                    
        except Exception as e:
            logger.error(f"Failed to sync directory {local_dir}: {e}")
    
    async def _upload_file(self, local_file: Path, parent_folder_id: str):
        """Upload file to Google Drive"""
        try:
            # Check if file already exists
            file_id = await self._find_file_by_name(local_file.name, parent_folder_id)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(local_file)
            
            # Check if file needs updating
            if file_id:
                drive_file = await self._get_file_metadata(file_id)
                if drive_file and drive_file.md5_checksum == file_hash:
                    return  # File hasn't changed
            
            # Prepare file metadata
            file_metadata = {
                'name': local_file.name,
                'parents': [parent_folder_id]
            }
            
            # Upload file
            media = MediaFileUpload(str(local_file), resumable=True)
            
            if file_id:
                # Update existing file
                file = self.service.files().update(
                    fileId=file_id,
                    body=file_metadata,
                    media_body=media
                ).execute()
                logger.info(f"Updated file: {local_file.name}")
            else:
                # Create new file
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Uploaded file: {local_file.name}")
                
        except Exception as e:
            logger.error(f"Failed to upload file {local_file}: {e}")
    
    async def _find_file_by_name(self, name: str, parent_id: str) -> Optional[str]:
        """Find file by name and parent folder"""
        try:
            query = f"name='{name}' and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields='files(id, name, md5Checksum)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
                
        except Exception as e:
            logger.error(f"Error finding file {name}: {e}")
        
        return None
    
    async def _get_file_metadata(self, file_id: str) -> Optional[DriveFile]:
        """Get file metadata from Google Drive"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,createdTime,modifiedTime,parents,md5Checksum'
            ).execute()
            
            return DriveFile(
                id=file['id'],
                name=file['name'],
                mime_type=file['mimeType'],
                size=int(file.get('size', 0)),
                created_time=datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00')),
                modified_time=datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')),
                parents=file.get('parents', []),
                md5_checksum=file.get('md5Checksum')
            )
            
        except Exception as e:
            logger.error(f"Error getting file metadata for {file_id}: {e}")
        
        return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def save_team_output(self, team_name: str, output_data: Dict[str, Any], 
                              output_type: str = "report"):
        """Save team output to Google Drive"""
        try:
            # Determine target folder based on team and output type
            team_folder_mapping = {
                "Research Team": "01_Research",
                "Planning Team": "02_Planning", 
                "Development Team": "03_Development",
                "Management Team": "04_Management",
                "General Manager": "05_General_Manager"
            }
            
            team_folder = team_folder_mapping.get(team_name, "06_Workflows")
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{team_name}_{output_type}_{timestamp}.json"
            
            # Prepare file content
            file_content = {
                "team": team_name,
                "type": output_type,
                "timestamp": datetime.now().isoformat(),
                "data": output_data
            }
            
            # Save locally first
            local_file = self.local_sync_path / filename
            with open(local_file, 'w') as f:
                json.dump(file_content, f, indent=2, default=str)
            
            # Upload to Google Drive
            folder_id = self.folder_structure.get(team_folder, {}).get('id')
            if folder_id:
                await self._upload_file(local_file, folder_id)
            
            logger.info(f"Saved {output_type} for {team_name} to Google Drive")
            
        except Exception as e:
            logger.error(f"Failed to save team output: {e}")
    
    async def create_workflow_backup(self, workflow_id: str, workflow_data: Dict[str, Any]):
        """Create backup of complete workflow"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_backup_{workflow_id}_{timestamp}.json"
            
            # Prepare backup data
            backup_data = {
                "workflow_id": workflow_id,
                "backup_timestamp": datetime.now().isoformat(),
                "workflow_data": workflow_data,
                "backup_type": "workflow_complete"
            }
            
            # Save locally
            local_file = self.local_sync_path / filename
            with open(local_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # Upload to backups folder
            backup_folder_id = self.folder_structure.get("09_Backups", {}).get('id')
            if backup_folder_id:
                await self._upload_file(local_file, backup_folder_id)
            
            logger.info(f"Created workflow backup: {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to create workflow backup: {e}")
    
    async def create_system_backup(self, backup_type: str = "scheduled"):
        """Create complete system backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_backup_{backup_type}_{timestamp}.tar.gz"
            
            # Create backup archive
            import tarfile
            
            backup_path = self.local_sync_path / filename
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Add project files
                project_root = Path.cwd().parent
                tar.add(project_root / "src", arcname="src")
                tar.add(project_root / "requirements.txt", arcname="requirements.txt")
                tar.add(project_root / "README.md", arcname="README.md")
                
                # Add database if exists
                db_file = project_root / "automation.db"
                if db_file.exists():
                    tar.add(db_file, arcname="automation.db")
            
            # Upload to appropriate backup folder
            backup_folder_id = self.folder_structure.get("09_Backups", {}).get('id')
            if backup_folder_id:
                await self._upload_file(backup_path, backup_folder_id)
            
            logger.info(f"Created system backup: {backup_type}")
            
        except Exception as e:
            logger.error(f"Failed to create system backup: {e}")
    
    async def get_drive_statistics(self) -> Dict[str, Any]:
        """Get Google Drive storage and usage statistics"""
        try:
            # Get storage quota
            about = self.service.about().get(fields='storageQuota').execute()
            quota = about.get('storageQuota', {})
            
            # Count files in each folder
            folder_stats = {}
            for folder_name, folder_info in self.folder_structure.items():
                file_count = await self._count_files_in_folder(folder_info['id'])
                folder_stats[folder_name] = file_count
            
            return {
                "storage_usage": {
                    "limit": quota.get('limit', 0),
                    "usage": quota.get('usage', 0),
                    "usage_in_drive": quota.get('usageInDrive', 0),
                    "usage_in_drive_trash": quota.get('usageInDriveTrash', 0)
                },
                "folder_statistics": folder_stats,
                "total_folders": len(self.folder_structure),
                "last_sync": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get Drive statistics: {e}")
            return {}
    
    async def _count_files_in_folder(self, folder_id: str) -> int:
        """Count files in a folder"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields='files(id)',
                pageSize=1000
            ).execute()
            
            return len(results.get('files', []))
            
        except Exception as e:
            logger.error(f"Error counting files in folder {folder_id}: {e}")
            return 0
    
    async def schedule_regular_syncs(self):
        """Schedule regular file synchronization"""
        try:
            while True:
                # Sync every hour
                await asyncio.sleep(3600)
                await self.sync_project_files()
                logger.info("Scheduled sync completed")
                
        except Exception as e:
            logger.error(f"Scheduled sync error: {e}")

# Import required Google Drive libraries
try:
    from googleapiclient.http import MediaFileUpload
except ImportError:
    logger.warning("Google Drive libraries not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    MediaFileUpload = None

# Global instance
drive_manager = GoogleDriveManager()
