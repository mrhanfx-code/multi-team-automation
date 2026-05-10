#!/usr/bin/env python3
"""
One-time Google Drive setup script for Multi-Team Automation System
Run this script once to initialize Google Drive integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from google_drive_integration import drive_manager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Make sure Google Drive libraries are installed:")
    print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

async def setup_drive():
    """Initialize Google Drive integration"""
    print("🚀 Starting Google Drive setup for Multi-Team Automation System...")
    print()
    
    # Check if credentials file exists
    credentials_path = Path("credentials.json")
    if not credentials_path.exists():
        print("❌ Credentials file not found!")
        print("📋 Please complete these steps first:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable Google Drive API")
        print("   3. Create OAuth credentials (Desktop app)")
        print("   4. Download credentials.json to this directory")
        print()
        print("📖 See setup_google_drive.md for detailed instructions")
        return False
    
    print("✅ Credentials file found")
    print("🔐 Starting authentication...")
    
    try:
        # Initialize the drive manager
        await drive_manager.initialize()
        
        print()
        print("🎉 Google Drive setup completed successfully!")
        print()
        print("📁 What was created:")
        print("   • Organized folder structure in your Google Drive")
        print("   • Automatic file synchronization enabled")
        print("   • Backup system configured")
        print()
        print("📂 Folder structure created:")
        print("   Multi-Team Automation/")
        print("   ├── 01_Research/ (Market, Technical, Competitive, etc.)")
        print("   ├── 02_Planning/ (Projects, Resources, Strategic, etc.)")
        print("   ├── 03_Development/ (Code, Docs, Tests, etc.)")
        print("   ├── 04_Management/ (Reviews, Decisions, QA, etc.)")
        print("   ├── 05_General_Manager/ (Reports, Approvals, etc.)")
        print("   ├── 06_Workflows/ (Active, Completed, Archived)")
        print("   ├── 07_Meetings/ (Schedules, Minutes, Materials)")
        print("   ├── 08_Notifications/ (Team, Escalations, Alerts)")
        print("   ├── 09_Backups/ (Daily, Weekly, Monthly)")
        print("   └── 10_Configuration/ (Settings, Templates, API configs)")
        print()
        print("🔄 What happens now:")
        print("   • All team outputs automatically sync to appropriate folders")
        print("   • System backups created regularly")
        print("   • Project files organized by team and type")
        print("   • Real-time file synchronization")
        print()
        print("⚙️ Next steps:")
        print("   1. Test the integration with your automation system")
        print("   2. Check your Google Drive for the folder structure")
        print("   3. Monitor storage usage (15GB free tier)")
        print("   4. Configure backup schedule if needed")
        print()
        print("✨ Your multi-team automation system is now cloud-ready!")
        
        return True
        
    except FileNotFoundError:
        print("❌ Setup failed: Missing credentials.json")
        print("📋 Make sure credentials.json is in the project root directory")
        return False
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Delete token.pickle if it exists and try again")
        print("   2. Check internet connection")
        print("   3. Verify Google Drive API is enabled")
        print("   4. Ensure OAuth credentials are correct")
        print()
        print("📖 See setup_google_drive.md for troubleshooting guide")
        return False

async def check_setup():
    """Check if Google Drive is already set up"""
    print("🔍 Checking existing Google Drive setup...")
    
    # Check for credentials
    if not Path("credentials.json").exists():
        print("❌ No credentials.json found")
        return False
    
    # Check for token
    if not Path("token.pickle").exists():
        print("❌ No token.pickle found - needs authentication")
        return False
    
    try:
        # Try to get drive statistics
        stats = await drive_manager.get_drive_statistics()
        if stats:
            print("✅ Google Drive is already set up and connected!")
            print(f"📊 Storage used: {stats.get('storage_usage', {}).get('usage', 0)} bytes")
            print(f"📁 Total folders: {stats.get('total_folders', 0)}")
            return True
    except Exception as e:
        print(f"❌ Connection check failed: {e}")
        return False
    
    return False

async def reset_setup():
    """Reset Google Drive setup"""
    print("🔄 Resetting Google Drive setup...")
    
    # Remove token file
    token_path = Path("token.pickle")
    if token_path.exists():
        token_path.unlink()
        print("✅ Token file removed")
    
    # Remove sync directory
    sync_path = Path("google_drive_sync")
    if sync_path.exists():
        import shutil
        shutil.rmtree(sync_path)
        print("✅ Sync directory cleaned")
    
    print("🔄 Setup reset complete. Run setup again to re-authenticate.")

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            asyncio.run(check_setup())
        elif command == "reset":
            asyncio.run(reset_setup())
        elif command == "help":
            print("Google Drive Setup Script")
            print()
            print("Usage:")
            print("  python setup_drive.py          - Run initial setup")
            print("  python setup_drive.py check    - Check existing setup")
            print("  python setup_drive.py reset    - Reset authentication")
            print("  python setup_drive.py help     - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python setup_drive.py help' for usage")
    else:
        # Default: run setup
        success = asyncio.run(setup_drive())
        if success:
            print("\n🎯 Setup successful! Your system is ready to use.")
        else:
            print("\n❌ Setup failed. Please fix the issues and try again.")
            sys.exit(1)

if __name__ == "__main__":
    main()
