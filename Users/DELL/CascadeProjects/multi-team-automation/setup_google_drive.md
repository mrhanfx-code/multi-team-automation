# Google Drive Setup Guide

## Overview
This guide will help you set up Google Drive integration for your multi-team automation system to ensure all project files are properly organized, backed up, and accessible.

## Prerequisites

### 1. Google Cloud Project Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 2. Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as application type
4. Give it a name (e.g., "Multi-Team Automation")
5. Click "Create"

### 3. Download Credentials
1. After creating credentials, click the download icon
2. Save the JSON file as `credentials.json` in your project root
3. **Important**: Keep this file secure and never commit it to Git

## Installation

### Install Required Packages
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

The requirements.txt file already includes these packages.

## First-Time Setup

### 1. Place Credentials File
```bash
# Place credentials.json in your project root
C:\Users\DELL\CascadeProjects\multi-team-automation\credentials.json
```

### 2. Initial Authentication
Run this one-time setup script:

```python
import asyncio
from src.google_drive_integration import drive_manager

async def setup_drive():
    try:
        await drive_manager.initialize()
        print("✅ Google Drive setup completed successfully!")
        print("📁 Folder structure created in your Google Drive")
        print("🔄 Automatic sync is now active")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("📋 Make sure credentials.json is in the correct location")

asyncio.run(setup_drive())
```

Save this as `setup_drive.py` and run it once.

## Google Drive Folder Structure

The system will automatically create this organized structure:

```
📁 Multi-Team Automation/
├── 📁 01_Research/
│   ├── 📁 Market_Research/
│   ├── 📁 Technical_Research/
│   ├── 📁 Competitive_Analysis/
│   ├── 📁 User_Research/
│   └── 📁 Industry_Analysis/
├── 📁 02_Planning/
│   ├── 📁 Project_Plans/
│   ├── 📁 Resource_Plans/
│   ├── 📁 Strategic_Plans/
│   ├── 📁 Timeline_Plans/
│   ├── 📁 Budget_Plans/
│   └── 📁 Risk_Plans/
├── 📁 03_Development/
│   ├── 📁 Source_Code/
│   ├── 📁 Documentation/
│   ├── 📁 Tests/
│   ├── 📁 Deployments/
│   └── 📁 Prototypes/
├── 📁 04_Management/
│   ├── 📁 Reviews/
│   ├── 📁 Decisions/
│   ├── 📁 Quality_Assurance/
│   ├── 📁 Security_Reports/
│   └── 📁 Performance_Reports/
├── 📁 05_General_Manager/
│   ├── 📁 Final_Reports/
│   ├── 📁 Executive_Summaries/
│   ├── 📁 Approvals/
│   └── 📁 Strategic_Overview/
├── 📁 06_Workflows/
│   ├── 📁 Active/
│   ├── 📁 Completed/
│   ├── 📁 Archived/
│   └── 📁 Templates/
├── 📁 07_Meetings/
│   ├── 📁 Schedules/
│   ├── 📁 Minutes/
│   ├── 📁 Materials/
│   └── 📁 Action_Items/
├── 📁 08_Notifications/
│   ├── 📁 Team_Notifications/
│   ├── 📁 Escalations/
│   ├── 📁 Alerts/
│   └── 📁 Reports/
├── 📁 09_Backups/
│   ├── 📁 Daily/
│   ├── 📁 Weekly/
│   ├── 📁 Monthly/
│   └── 📁 Emergency/
└── 📁 10_Configuration/
    ├── 📁 Team_Settings/
    ├── 📁 Workflow_Templates/
    ├── 📁 API_Configs/
    └── 📁 Environment_Settings/
```

## Integration with Automation System

### Automatic File Synchronization
The system automatically syncs:
- **Team outputs** → Appropriate team folders
- **Workflow data** → Workflow folders
- **System backups** → Backup folders
- **Configuration files** → Configuration folders
- **Meeting records** → Meeting folders

### Usage Examples

#### Save Team Output
```python
# Automatically saves research team output to Google Drive
await drive_manager.save_team_output(
    team_name="Research Team",
    output_data=research_results,
    output_type="market_research"
)
```

#### Create Workflow Backup
```python
# Creates complete workflow backup
await drive_manager.create_workflow_backup(
    workflow_id="workflow_20240510_143000",
    workflow_data=complete_workflow_data
)
```

#### System Backup
```python
# Creates full system backup
await drive_manager.create_system_backup("daily")
```

## Monitoring and Management

### Check Drive Statistics
```python
stats = await drive_manager.get_drive_statistics()
print(f"Storage used: {stats['storage_usage']['usage']} bytes")
print(f"Total files: {sum(stats['folder_statistics'].values())}")
```

### Manual Sync
```python
# Force sync all project files
await drive_manager.sync_project_files()
```

## Security Best Practices

### 1. Protect Credentials
- Never commit `credentials.json` to Git
- Store it in a secure location
- Use environment variables in production

### 2. Limited Scopes
The system only requests necessary permissions:
- Read/write access to Google Drive files
- No access to other Google services

### 3. Regular Backups
- System creates automatic daily backups
- Manual backups available anytime
- Backup retention configurable

## Troubleshooting

### Common Issues

#### "Credentials file not found"
**Solution**: Ensure `credentials.json` is in the project root directory

#### "Authentication failed"
**Solution**: 
1. Delete `token.pickle` if it exists
2. Re-run the setup script
3. Complete the OAuth flow in browser

#### "Insufficient permissions"
**Solution**: 
1. Check Google Cloud Console
2. Ensure Drive API is enabled
3. Verify OAuth scopes are correct

#### "Upload failed"
**Solution**:
1. Check internet connection
2. Verify Google Drive storage space
3. Check file size limits

### Error Recovery
```python
# Reset authentication
import os
if os.path.exists('token.pickle'):
    os.remove('token.pickle')
    
# Re-initialize
await drive_manager.initialize()
```

## Configuration Options

### Sync Frequency
```python
# Default: Every hour
# Can be customized in the integration settings
```

### Backup Retention
```python
# Default: 30 days for daily backups
# Default: 12 weeks for weekly backups
# Default: 12 months for monthly backups
```

### File Exclusions
```python
# Automatically excludes:
# - Temporary files (*.tmp, *.temp)
# - Cache directories (.cache, __pycache__)
# - Large binaries (>100MB)
```

## Next Steps

1. **Complete initial setup** using this guide
2. **Test the integration** with sample data
3. **Configure backup schedule** if needed
4. **Monitor storage usage** regularly
5. **Set up alerts** for storage limits

## Support

For issues with:
- **Google API**: Check Google Cloud Console documentation
- **Authentication**: Review OAuth setup steps
- **File sync**: Check local file permissions
- **Storage**: Monitor Google Drive storage limits

---

**Ready to connect your Google Drive! 🚀**

Once set up, your multi-team automation system will automatically maintain a perfectly organized, backed-up copy of all project files and outputs.
