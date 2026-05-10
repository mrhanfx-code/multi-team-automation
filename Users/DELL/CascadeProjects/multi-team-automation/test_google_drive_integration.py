#!/usr/bin/env python3
"""
MFM Corporation - Google Drive Integration Test Script
Comprehensive testing for Google Drive integration with user credentials
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path
sys.path.append('src')
sys.path.append('.')

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from googleapiclient.http import MediaIoBaseDownload
    from io import BytesIO
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False
    print("⚠️ Google APIs not installed. Install with: pip install google-api-python-client google-auth google-auth-oauthlib")

class GoogleDriveIntegrationTester:
    """Comprehensive Google Drive integration tester"""
    
    def __init__(self):
        self.service_account_key = None
        self.oauth_credentials = None
        self.drive_service = None
        self.test_results = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Google Drive integration tests"""
        print("🔍 MFM CORPORATION - GOOGLE DRIVE INTEGRATION TESTS")
        print("=" * 60)
        
        if not GOOGLE_APIS_AVAILABLE:
            print("❌ Google APIs not available - install required packages")
            return {"success": False, "error": "Google APIs not installed"}
        
        results = {
            "service_account_auth": False,
            "oauth_flow": False,
            "drive_api_access": False,
            "file_operations": False,
            "folder_operations": False,
            "sharing_operations": False,
            "search_operations": False,
            "permissions_check": False,
            "quota_check": False,
            "overall_success": False
        }
        
        try:
            # Test 1: Service Account Authentication
            print("\n🔐 Test 1: Service Account Authentication")
            print("-" * 40)
            results["service_account_auth"] = await self.test_service_account_auth()
            
            # Test 2: OAuth Flow Setup
            print("\n🔑 Test 2: OAuth Flow Setup")
            print("-" == 40)
            results["oauth_flow"] = await self.test_oauth_flow_setup()
            
            # Test 3: Drive API Access
            print("\n📁 Test 3: Drive API Access")
            print("-" == 40)
            results["drive_api_access"] = await self.test_drive_api_access()
            
            # Test 4: File Operations
            print("\n📄 Test 4: File Operations")
            print("-" == 40)
            results["file_operations"] = await self.test_file_operations()
            
            # Test 5: Folder Operations
            print("\n📂 Test 5: Folder Operations")
            print("-" == 40)
            results["folder_operations"] = await self.test_folder_operations()
            
            # Test 6: Sharing Operations
            print("\n🔗 Test 6: Sharing Operations")
            print("-" == 40)
            results["sharing_operations"] = await self.test_sharing_operations()
            
            # Test 7: Search Operations
            print("\n🔍 Test 7: Search Operations")
            print("-" == 40)
            results["search_operations"] = await self.test_search_operations()
            
            # Test 8: Permissions Check
            print("\n🛡️ Test 8: Permissions Check")
            print("-" == 40)
            results["permissions_check"] = await self.test_permissions_check()
            
            # Test 9: Quota Check
            print("\n📊 Test 9: Quota Check")
            print("-" == 40)
            results["quota_check"] = await self.test_quota_check()
            
            # Calculate overall success
            passed_tests = sum(1 for result in results.values() if result)
            total_tests = len(results) - 1  # Exclude overall_success
            results["overall_success"] = passed_tests == total_tests
            
            # Summary
            print("\n📋 TEST SUMMARY")
            print("=" * 60)
            print(f"Tests Passed: {passed_tests}/{total_tests}")
            print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
            
            for test_name, result in results.items():
                if test_name != "overall_success":
                    status = "✅" if result else "❌"
                    print(f"  {test_name}: {status}")
            
            return results
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_service_account_auth(self) -> bool:
        """Test service account authentication"""
        try:
            # Check for service account key file
            key_file = "service-account-key.json"
            if not os.path.exists(key_file):
                print(f"❌ Service account key file not found: {key_file}")
                return False
            
            # Load service account credentials
            self.service_account_key = service_account.Credentials.from_service_account_file(
                key_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build Drive service
            self.drive_service = build('drive', 'v3', credentials=self.service_account_key)
            
            # Test authentication
            about = self.drive_service.about().get(fields="user").execute()
            user_info = about.get('user', {})
            
            print(f"✅ Service account authenticated successfully")
            print(f"   Email: {user_info.get('emailAddress', 'N/A')}")
            print(f"   Name: {user_info.get('displayName', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Service account authentication failed: {e}")
            return False
    
    async def test_oauth_flow_setup(self) -> bool:
        """Test OAuth flow setup"""
        try:
            # Check for OAuth client secrets file
            secrets_file = "client-secret.json"
            if not os.path.exists(secrets_file):
                print(f"❌ OAuth client secrets file not found: {secrets_file}")
                print("   Create OAuth credentials in Google Cloud Console")
                return False
            
            # Load OAuth configuration
            with open(secrets_file, 'r') as f:
                client_config = json.load(f)
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                client_config,
                scopes=['https://www.googleapis.com/auth/drive'],
                redirect_uri='http://localhost:8000/auth/callback'
            )
            
            # Generate authorization URL
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            print("✅ OAuth flow configured successfully")
            print(f"   Authorization URL: {auth_url[:50]}...")
            print(f"   State: {state}")
            print("   Note: Complete OAuth flow in browser for full testing")
            
            return True
            
        except Exception as e:
            print(f"❌ OAuth flow setup failed: {e}")
            return False
    
    async def test_drive_api_access(self) -> bool:
        """Test Drive API access"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Test basic API access
            results = self.drive_service.files().list(
                pageSize=10,
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ Drive API access successful")
            print(f"   Found {len(files)} files/folders")
            
            return True
            
        except Exception as e:
            print(f"❌ Drive API access failed: {e}")
            return False
    
    async def test_file_operations(self) -> bool:
        """Test file operations"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Create test file
            file_metadata = {
                'name': f'MFM_Test_File_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                'parents': []  # Root folder
            }
            
            media_content = MediaIoBaseUpload(
                b'This is a test file for MFM Corporation Google Drive integration.',
                mimetype='text/plain'
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media_content,
                fields='id,name,size'
            ).execute()
            
            file_id = file.get('id')
            file_name = file.get('name')
            file_size = file.get('size')
            
            print(f"✅ File created successfully")
            print(f"   ID: {file_id}")
            print(f"   Name: {file_name}")
            print(f"   Size: {file_size} bytes")
            
            # Test file download
            request = self.drive_service.files().get_media(fileId=file_id)
            file_content = BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue().decode('utf-8')
            print(f"✅ File downloaded successfully")
            print(f"   Content: {content[:50]}...")
            
            # Clean up - delete test file
            self.drive_service.files().delete(fileId=file_id).execute()
            print(f"✅ Test file deleted successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ File operations test failed: {e}")
            return False
    
    async def test_folder_operations(self) -> bool:
        """Test folder operations"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Create test folder
            folder_metadata = {
                'name': f'MFM_Test_Folder_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id,name'
            ).execute()
            
            folder_id = folder.get('id')
            folder_name = folder.get('name')
            
            print(f"✅ Folder created successfully")
            print(f"   ID: {folder_id}")
            print(f"   Name: {folder_name}")
            
            # Create file in folder
            file_metadata = {
                'name': 'test_in_folder.txt',
                'parents': [folder_id]
            }
            
            media_content = MediaIoBaseUpload(
                b'Test file in MFM Corporation folder.',
                mimetype='text/plain'
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media_content,
                fields='id,name'
            ).execute()
            
            print(f"✅ File created in folder successfully")
            print(f"   File ID: {file.get('id')}")
            
            # List folder contents
            results = self.drive_service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id,name,mimeType)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ Folder contents listed successfully")
            print(f"   Items in folder: {len(files)}")
            
            # Clean up
            self.drive_service.files().delete(fileId=file.get('id')).execute()
            self.drive_service.files().delete(fileId=folder_id).execute()
            print(f"✅ Test folder and file deleted successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Folder operations test failed: {e}")
            return False
    
    async def test_sharing_operations(self) -> bool:
        """Test sharing operations"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Create test file for sharing
            file_metadata = {
                'name': f'MFM_Share_Test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                'parents': []
            }
            
            media_content = MediaIoBaseUpload(
                b'Test file for sharing operations.',
                mimetype='text/plain'
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media_content,
                fields='id,name'
            ).execute()
            
            file_id = file.get('id')
            
            # Test sharing permissions
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id,type,role'
            ).execute()
            
            print(f"✅ File shared successfully")
            print(f"   File ID: {file_id}")
            print(f"   Permission: Anyone with link can view")
            
            # Get sharing link
            file_info = self.drive_service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            view_link = file_info.get('webViewLink')
            print(f"   View link: {view_link}")
            
            # Clean up
            self.drive_service.files().delete(fileId=file_id).execute()
            print(f"✅ Test file deleted successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Sharing operations test failed: {e}")
            return False
    
    async def test_search_operations(self) -> bool:
        """Test search operations"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Search for files
            results = self.drive_service.files().list(
                q="name contains 'test'",
                fields="files(id,name,mimeType,size)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ Search operations successful")
            print(f"   Found {len(files)} files matching 'test'")
            
            # Search by file type
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.folder'",
                fields="files(id,name)"
            ).execute()
            
            folders = results.get('files', [])
            print(f"   Found {len(folders)} folders")
            
            return True
            
        except Exception as e:
            print(f"❌ Search operations test failed: {e}")
            return False
    
    async def test_permissions_check(self) -> bool:
        """Test permissions check"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Get about information
            about = self.drive_service.about().get(
                fields="user,storageQuota"
            ).execute()
            
            user_info = about.get('user', {})
            storage_quota = about.get('storageQuota', {})
            
            print(f"✅ Permissions check successful")
            print(f"   User email: {user_info.get('emailAddress', 'N/A')}")
            print(f"   User name: {user_info.get('displayName', 'N/A')}")
            print(f"   Permission ID: {user_info.get('permissionId', 'N/A')}")
            
            # Check storage quota
            limit = storage_quota.get('limit', 0)
            usage = storage_quota.get('usage', 0)
            
            if limit > 0:
                usage_percent = (usage / limit) * 100
                print(f"   Storage usage: {usage_percent:.1f}% ({usage:,}/{limit:,} bytes)")
            else:
                print(f"   Storage usage: {usage:,} bytes (unlimited)")
            
            return True
            
        except Exception as e:
            print(f"❌ Permissions check failed: {e}")
            return False
    
    async def test_quota_check(self) -> bool:
        """Test quota and limits"""
        try:
            if not self.drive_service:
                print("❌ Drive service not initialized")
                return False
            
            # Check current usage
            about = self.drive_service.about().get(
                fields="storageQuota"
            ).execute()
            
            storage_quota = about.get('storageQuota', {})
            
            print(f"✅ Quota check successful")
            
            # Display quota information
            limit = storage_quota.get('limit', 0)
            usage = storage_quota.get('usage', 0)
            usage_in_drive = storage_quota.get('usageInDrive', 0)
            usage_in_drive_trash = storage_quota.get('usageInDriveTrash', 0)
            
            print(f"   Total quota: {limit:,} bytes")
            print(f"   Total used: {usage:,} bytes")
            print(f"   Drive usage: {usage_in_drive:,} bytes")
            print(f"   Drive trash: {usage_in_drive_trash:,} bytes")
            
            if limit > 0:
                available = limit - usage
                available_percent = (available / limit) * 100
                print(f"   Available: {available:,} bytes ({available_percent:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Quota check failed: {e}")
            return False
    
    def generate_setup_instructions(self) -> str:
        """Generate setup instructions for user"""
        instructions = """
📋 GOOGLE DRIVE SETUP INSTRUCTIONS
===============================

To complete the Google Drive integration setup:

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create new project: "mfm-corporation-automation"
   - Enable billing

2. **Enable APIs**
   - Google Drive API
   - Google Sheets API
   - Google Calendar API

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create service account: "mfm-automation-service"
   - Assign "Editor" role
   - Download JSON key file as "service-account-key.json"

4. **Create OAuth Credentials**
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Download client secrets as "client-secret.json"

5. **Configure OAuth Consent Screen**
   - Add required scopes
   - Add test users

6. **Share Drive Access**
   - Create folder: "MFM Corporation Automation"
   - Share with service account email
   - Grant "Editor" permissions

7. **Environment Setup**
   - Place key files in project root
   - Install required packages:
     pip install google-api-python-client google-auth google-auth-oauthlib

8. **Run Tests**
   - python test_google_drive_integration.py

For detailed instructions, see: docs/GOOGLE_CLOUD_SETUP_GUIDE.md
        """
        
        return instructions.strip()

async def main():
    """Main test execution"""
    tester = GoogleDriveIntegrationTester()
    
    # Generate setup instructions
    print(tester.generate_setup_instructions())
    
    # Run tests
    results = await tester.run_all_tests()
    
    # Final recommendations
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    if results["overall_success"]:
        print("✅ All tests passed! Google Drive integration is ready.")
        print("   You can now use Google Drive with the MFM Corporation system.")
    else:
        print("❌ Some tests failed. Please review the setup instructions above.")
        print("   Common issues:")
        print("   - Missing or incorrect service account key file")
        print("   - Insufficient permissions in Google Cloud Console")
        print("   - Required APIs not enabled")
        print("   - OAuth credentials not properly configured")
    
    return results

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
