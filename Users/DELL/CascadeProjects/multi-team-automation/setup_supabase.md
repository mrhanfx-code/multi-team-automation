# Supabase Setup Guide

## Overview
This guide will help you set up Supabase integration for your multi-team automation system to replace Google Drive with a more powerful database and storage solution.

## Why Supabase Over Google Drive?

### **Advantages of Supabase**
- **PostgreSQL Database** - Full SQL database vs file storage only
- **Real-time Capabilities** - Live updates and notifications
- **File Storage** - Structured storage with metadata
- **Authentication Built-in** - User management and security
- **REST API** - Easy integration and management
- **Free Tier** - 500MB database, 1GB storage, 50k MAU
- **No OAuth Setup** - Simple API key authentication

### **Comparison**
| Feature | Google Drive | Supabase |
|----------|-------------|----------|
| Database | No | PostgreSQL |
| Real-time | No | Yes |
| File Organization | Manual | Structured |
| Authentication | OAuth Complex | API Key Simple |
| Free Tier | 15GB | 500MB DB + 1GB Storage |
| API Access | Complex | REST API |

## Prerequisites

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up/login with your Google/GitHub account
4. **Project name**: `Multi-Team Automation`
5. **Database password**: Create a strong password
6. Click **"Create new project"**
7. Wait for project to be created (2-3 minutes)

### 2. Get API Credentials
1. In your Supabase project dashboard
2. Go to **Settings** → **API**
3. Find **Project URL** and **API Key**
4. Copy both values

### 3. Install Required Packages
```bash
pip install aiohttp
```
(The requirements.txt already includes aiohttp)

## Setup Process

### **Step 1: Environment Variables**
Create `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### **Step 2: Test Connection**
Run this test script:

```python
import asyncio
import os
from dotenv import load_dotenv
from src.supabase_simple import SimpleSupabaseManager, SupabaseConfig

async def test_supabase():
    # Load environment variables
    load_dotenv()
    
    # Create manager
    config = SupabaseConfig(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )
    
    manager = SimpleSupabaseManager(config)
    
    # Test initialization
    success = await manager.initialize()
    
    if success:
        print("✅ Supabase connection successful!")
        print("📊 Database tables created")
        print("📁 Storage bucket ready")
        print("🔄 Real-time capabilities enabled")
    else:
        print("❌ Supabase connection failed")

asyncio.run(test_supabase())
```

### **Step 3: Update Automation System**
Replace Google Drive integration with Supabase in your team classes:

```python
# Instead of:
# from src.google_drive_integration import drive_manager

# Use:
from src.supabase_simple import supabase_manager

# Save team outputs:
await supabase_manager.save_team_output(
    team_name="Research Team",
    output_data=research_results,
    output_type="market_research"
)

# Save workflow state:
await supabase_manager.save_workflow_state(
    workflow_id="workflow_123",
    state_data={"status": "active", "current_team": "Research Team"}
)
```

## Database Schema

### **Tables Created Automatically**

#### **workflows**
```sql
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    current_team TEXT,
    started_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    data JSONB,
    metadata JSONB
);
```

#### **tasks**
```sql
CREATE TABLE tasks (
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
```

#### **team_outputs**
```sql
CREATE TABLE team_outputs (
    id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    output_type TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    data JSONB NOT NULL
);
```

#### **notifications**
```sql
CREATE TABLE notifications (
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
```

#### **meetings**
```sql
CREATE TABLE meetings (
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
```

## Storage Structure

### **File Organization**
```
📁 multi-team-automation-bucket/
├── 📁 team_outputs/
│   ├── 📁 Research_Team/
│   │   ├── 📁 market_research/
│   │   ├── 📁 technical_research/
│   │   └── 📁 competitive_analysis/
│   ├── 📁 Planning_Team/
│   │   ├── 📁 project_plans/
│   │   └── 📁 resource_plans/
│   ├── 📁 Development_Team/
│   │   ├── 📁 source_code/
│   │   └── 📁 documentation/
│   ├── 📁 Management_Team/
│   │   ├── 📁 reviews/
│   │   └── 📁 decisions/
│   └── 📁 General_Manager/
│       ├── 📁 final_reports/
│       └── 📁 approvals/
├── 📁 backups/
│   ├── 📁 daily/
│   ├── 📁 weekly/
│   └── 📁 monthly/
└── 📁 system/
    ├── 📁 configurations/
    └── 📁 logs/
```

## Real-time Capabilities

### **Live Updates**
- **Workflow status changes** - Real-time updates to all connected clients
- **New notifications** - Instant delivery to team members
- **Task completions** - Live progress tracking
- **Meeting schedules** - Real-time calendar updates

### **Setup Real-time**
```python
# Enable real-time subscriptions
subscriptions = await supabase_manager.setup_realtime_subscriptions()

# Listen for workflow updates
subscriptions['workflows'].on_change(lambda payload: 
    print(f"Workflow {payload['record']['id']} updated")
)

# Listen for new notifications
subscriptions['notifications'].on_change(lambda payload:
    print(f"New notification: {payload['record']['message']}")
)
```

## Migration from Google Drive

### **Data Migration**
If you have existing Google Drive data:

```python
async def migrate_from_google_drive():
    # Export from Google Drive
    google_data = await export_google_drive_data()
    
    # Import to Supabase
    for workflow in google_data.get('workflows', []):
        await supabase_manager.save_workflow_state(
            workflow_id=workflow['id'],
            state_data=workflow
        )
    
    for file_data in google_data.get('files', []):
        await supabase_manager.upload_file(
            content=file_data['content'],
            path=file_data['path'],
            metadata=file_data['metadata']
        )
```

## Benefits for Your System

### **Performance Improvements**
- **Query Speed**: PostgreSQL vs file parsing
- **Concurrent Access**: Multiple users can access simultaneously
- **Data Integrity**: ACID compliance and transactions
- **Scalability**: Built for production workloads

### **Feature Enhancements**
- **Advanced Queries**: SQL filtering, sorting, aggregation
- **Relationships**: Foreign keys and joins between tables
- **Indexing**: Automatic performance optimization
- **Backup Automation**: Automated database backups

### **Security Improvements**
- **Row Level Security**: Team-based access control
- **API Key Management**: Rotate and manage access
- **Audit Trail**: Built-in change tracking
- **Encryption**: Data encrypted at rest and in transit

## Free Tier Limitations

### **What's Included**
- **Database**: 500MB PostgreSQL
- **Storage**: 1GB file storage
- **API Requests**: 50,000 per hour
- **Real-time Connections**: 100 concurrent
- **Bandwidth**: 250GB per month

### **Monitoring Usage**
```python
# Check storage statistics
stats = await supabase_manager.get_storage_statistics()
print(f"Storage used: {stats['file_statistics']['total_size']} bytes")
print(f"Total files: {stats['file_statistics']['total_files']}")

# Monitor by team
for team, count in stats['file_statistics']['by_team'].items():
    print(f"{team}: {count} files")
```

## Next Steps

### **1. Setup Supabase Project**
- Create account and project
- Get URL and API key
- Set environment variables

### **2. Test Integration**
- Run connection test
- Verify table creation
- Test file upload/download

### **3. Update Automation System**
- Replace Google Drive calls with Supabase
- Update team classes to use new backend
- Test complete workflow

### **4. Enable Real-time Features**
- Setup subscriptions for live updates
- Implement real-time notifications
- Add live progress tracking

## Troubleshooting

### **Common Issues**

#### "Connection failed"
**Solution**: Check URL and API key in environment variables

#### "Table creation failed"
**Solution**: Verify API key has admin permissions

#### "File upload failed"
**Solution**: Check file size limits (50MB per file on free tier)

#### "Real-time not working"
**Solution**: Check internet connection and subscription setup

### **Error Recovery**
```python
# Reset connection
await supabase_manager.initialize()

# Clear cache
supabase_manager.file_cache.clear()

# Verify setup
stats = await supabase_manager.get_storage_statistics()
if stats:
    print("✅ Supabase connection restored")
```

## Production Considerations

### **Scaling Beyond Free Tier**
- **Database**: $25/month for 8GB
- **Storage**: $5/month for 100GB
- **Bandwidth**: $0.09/GB beyond 250GB
- **Real-time**: $5/month for 500 connections

### **Backup Strategy**
- **Automated Backups**: Enable Supabase daily backups
- **Point-in-Time Recovery**: 30-day retention
- **Export Capability**: Regular data exports
- **Multi-region**: Consider regional replication

---

**Ready to switch to Supabase! 🚀**

Your multi-team automation system will be more powerful, scalable, and feature-rich with Supabase as the backend.
