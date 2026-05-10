# MFM Corporation Multi-Team Automation System - Setup Guide

## 🚀 Quick Start

This guide will help you set up the MFM Corporation Multi-Team Automation System v3.0.0 with all 13 specialized teams.

### 📋 Prerequisites

- Python 3.8 or higher
- Supabase account (free tier available)
- Git (for version control)
- 4GB+ RAM recommended
- 2GB+ disk space

### ⚡ One-Command Setup

```bash
# Clone and setup the system
git clone <repository-url>
cd multi-team-automation
python setup_system.py --mode complete
```

## 📝 Step-by-Step Setup

### 1. Environment Configuration

#### Option A: Automatic Setup
```bash
python setup_system.py --mode dev
```

#### Option B: Manual Setup
```bash
# Copy environment template
cp .env.example .env

# Edit the configuration file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Security Configuration (REQUIRED)
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# System Configuration
APP_NAME=MFM Corporation Multi-Team Automation
APP_VERSION=3.0.0
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
```

### 2. Supabase Setup

#### Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and anon key
4. Update `.env` file with these values

#### Database Setup
```bash
# Run database migration
python setup_system.py --mode complete
```

Or manually run the SQL:
```bash
# Execute the schema
psql -h your-db-host -U postgres -d postgres -f database/schema.sql
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Verify Setup

```bash
# Check system status
python setup_system.py --mode check
```

Expected output:
```
✅ SETUP SUCCESSFUL
System Status:
  ✅ Environment: configured
  ✅ Dependencies: installed
  ✅ Database: connected
  ✅ System: ready
```

## 🎯 Running the System

### Start the Main System
```bash
python unified_system.py
```

### Run Individual Demos
```bash
# Main expanded system demo
python demo_expanded_system_v2.py

# Individual team demos
python demo_expert_legal_team.py
python demo_operations_manager.py
python demo_notifications_scheduling.py
python demo_meeting_scheduler.py
python demo_reporting_system.py
python demo_security_system.py
```

### Start the Dashboard
```bash
python dashboard_server.py
```
Then visit: http://localhost:8000

## 🔧 Configuration Options

### Environment Variables

#### Required Variables
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `JWT_SECRET_KEY`: Secret key for JWT tokens

#### Optional Variables
- `DEBUG`: Enable debug mode (default: false)
- `MAX_CONCURRENT_WORKFLOWS`: Max concurrent workflows (default: 10)
- `WORKFLOW_TIMEOUT_MINUTES`: Workflow timeout (default: 60)

#### Feature Flags
- `ENABLE_LEGAL_TEAM`: Enable Legal Team (default: true)
- `ENABLE_OPERATIONS_MANAGER`: Enable Operations Manager (default: true)
- `ENABLE_INNOVATION_TEAM`: Enable Innovation Team (default: true)

### Database Configuration

The system uses Supabase as the backend database. The schema includes:
- Users and authentication
- Workflows and tasks
- Team metrics and performance
- Notifications and meetings
- Legal compliance data
- Operations management data

### Team Configuration

The system includes 13 specialized teams:
1. **Research Team** - Research and analysis
2. **Planning Team** - Strategic planning
3. **Development Team** - Software development
4. **Management Team** - Project management
5. **General Manager** - Executive oversight
6. **Innovation Team** - Trends tracking
7. **Market Intelligence Team** - Market analysis
8. **Technology Tracking Team** - Tech monitoring
9. **MCP/LLM Integration Team** - AI integration
10. **Marketing Team** - Marketing automation
11. **Media Team** - Media management
12. **Expert Legal Team** - Malaysian law specialists
13. **Operations Manager** - Agent optimization

## 🚨 Troubleshooting

### Common Issues

#### 1. Supabase Connection Failed
```bash
# Check your Supabase URL and key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('URL:', os.getenv('SUPABASE_URL')); print('Key:', os.getenv('SUPABASE_KEY')[:20] + '...')"
```

**Solution:** Ensure your `.env` file has the correct Supabase URL and anon key.

#### 2. Missing Dependencies
```bash
# Install missing packages
pip install -r requirements.txt
```

#### 3. Database Schema Issues
```bash
# Re-run database migration
python setup_system.py --mode complete
```

#### 4. Port Already in Use
```bash
# Change port in .env
PORT=8001
```

#### 5. Permission Denied
```bash
# Check file permissions
chmod +x setup_system.py
```

### Error Messages

#### "Supabase connection failed"
- Check your internet connection
- Verify Supabase project is active
- Confirm URL and key are correct

#### "Environment validation failed"
- Run: `python setup_system.py --mode dev` to create development config
- Update required variables in `.env`

#### "System initialization failed"
- Check all dependencies are installed
- Verify database connection
- Review error logs in `logs/` directory

### Getting Help

1. **Check System Status**: `python setup_system.py --mode check`
2. **Review Logs**: Check `logs/app.log` for detailed error messages
3. **Validate Configuration**: Run environment validation
4. **Reset Database**: Drop and recreate Supabase tables if needed

## 📊 System Monitoring

### Health Check
```bash
python setup_system.py --mode check
```

### Performance Monitoring
The system includes built-in monitoring:
- Agent performance metrics
- Workflow execution times
- Database query performance
- System resource usage

### Logs
- Application logs: `logs/app.log`
- Error logs: `logs/errors.log`
- Performance logs: `logs/performance.log`

## 🔒 Security Configuration

### JWT Configuration
```env
JWT_SECRET_KEY=your_very_long_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### Database Security
- Row Level Security (RLS) enabled
- User-based access control
- API key authentication

### Network Security
- HTTPS recommended for production
- CORS configuration
- Rate limiting enabled

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment
python setup_system.py --mode prod
```

### Production Configuration
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### Deployment Options
1. **Docker**: Use provided Dockerfile
2. **Cloud**: Deploy to VPS or cloud platform
3. **Server**: Dedicated server deployment

### Performance Optimization
- Enable caching
- Configure connection pooling
- Set up load balancing
- Monitor resource usage

## 📚 API Documentation

### Authentication
```python
# Sign in
POST /auth/signin
{
  "email": "user@example.com",
  "password": "password"
}
```

### Workflows
```python
# Create workflow
POST /workflows
{
  "name": "Research Project",
  "description": "Market research for new product"
}
```

### Teams
```python
# Get team status
GET /teams/{team_name}/status
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_teams.py
```

### Integration Tests
```bash
# Test system integration
python test_integration.py
```

### Demo Testing
```bash
# Run all demos
python run_all_demos.py
```

## 📈 Performance Tuning

### Database Optimization
- Add indexes for frequently queried columns
- Optimize query patterns
- Use connection pooling

### Application Optimization
- Enable async operations
- Use caching for frequently accessed data
- Optimize agent allocation

### Resource Management
- Monitor memory usage
- Optimize agent utilization
- Scale resources as needed

## 🔧 Advanced Configuration

### Custom Teams
Add new teams by:
1. Creating team class in `src/`
2. Implementing required methods
3. Registering team in `unified_system.py`

### Custom Workflows
Create custom workflows:
1. Define workflow in `workflows/`
2. Configure triggers
3. Set up monitoring

### External Integrations
Connect external services:
1. Update configuration
2. Implement API client
3. Add authentication

## 📞 Support

### Documentation
- [API Documentation](docs/API.md)
- [Team Guides](docs/TEAMS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share experiences
- Wiki: Community-maintained documentation

### Getting Help
1. Check this guide first
2. Review troubleshooting section
3. Search existing issues
4. Create new issue with details

---

## 🎉 You're Ready!

Once setup is complete, you can:
- Run the main automation system
- Use the web dashboard
- Execute individual team demos
- Monitor system performance
- Scale as needed

**Happy Automating! 🚀**
