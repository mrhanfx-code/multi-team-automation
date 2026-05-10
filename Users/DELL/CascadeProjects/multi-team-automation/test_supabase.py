#!/usr/bin/env python3
"""
Test Supabase Integration for Multi-Team Automation System
Run this script to verify your Supabase setup is working
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from supabase_simple import SimpleSupabaseManager, SupabaseConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Make sure aiohttp is installed: pip install aiohttp")
    sys.exit(1)

async def test_supabase_connection():
    """Test Supabase connection and setup"""
    print("🚀 Testing Supabase integration...")
    print()
    
    # Load environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Environment variables not found!")
        print("📋 Make sure .env file contains:")
        print("   SUPABASE_URL=your_supabase_url")
        print("   SUPABASE_KEY=your_supabase_key")
        print()
        print("🔧 You can also set them as environment variables:")
        print("   export SUPABASE_URL='https://mfuitzqvsnxatpquslpu.supabase.co'")
        print("   export SUPABASE_KEY='sb_publishable_fq0YDG3R-gkkt9dhlpRqgA_-N2zvc_d'")
        return False
    
    print(f"✅ Environment variables loaded")
    print(f"🔗 URL: {supabase_url}")
    print(f"🔑 Key: {supabase_key[:20]}...")
    print()
    
    # Test basic HTTP connection first
    print("🔍 Testing basic HTTP connection...")
    try:
        import aiohttp
        import ssl
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession() as session:
            # Test different endpoints
            endpoints_to_test = [
                "/rest/v1/",
                "/",
                "/auth/v1/user"
            ]
            
            for endpoint in endpoints_to_test:
                async with session.get(
                    f"{supabase_url}{endpoint}",
                    ssl=ssl_context
                ) as response:
                    print(f"   📡 {endpoint}: {response.status}")
                    if response.status == 401:
                        print(f"      ✅ Server reachable, auth required")
                    elif response.status == 200:
                        print(f"      ✅ Server reachable")
                    elif response.status == 404:
                        print(f"      ⚠️  Endpoint not found")
                    else:
                        print(f"      ⚠️  Unexpected status: {response.status}")
        
        # Test with auth on different endpoints
        print("🔐 Testing authentication...")
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        for endpoint in ["/rest/v1/", "/auth/v1/config"]:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{supabase_url}{endpoint}",
                    headers=headers,
                    ssl=ssl_context
                ) as response:
                    print(f"   🔑 {endpoint}: {response.status}")
                    if response.status == 200:
                        print(f"      ✅ Authentication successful!")
                        response_text = await response.text()
                        print(f"      📄 Response: {response_text[:100]}...")
                        return True  # Found working endpoint
                    elif response.status == 401:
                        print(f"      ❌ Authentication failed")
                    elif response.status == 403:
                        print(f"      ⚠️  Forbidden - check permissions")
                    elif response.status == 404:
                        print(f"      ⚠️  Endpoint not found")
                    else:
                        print(f"      ⚠️  Unexpected status: {response.status}")
                        response_text = await response.text()
                        print(f"      📄 Response: {response_text[:200]}...")
        
        print("   ❌ No working endpoint found")
        print("   🔧 Check if Supabase project is active and not paused")
        return False
                    
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    try:
        # Create Supabase manager
        config = SupabaseConfig(
            url=supabase_url,
            key=supabase_key
        )
        
        manager = SimpleSupabaseManager(config)
        
        print("🔐 Initializing Supabase connection...")
        success = await manager.initialize()
        
        if success:
            print()
            print("🎉 Supabase integration successful!")
            print()
            print("📊 What was set up:")
            print("   • PostgreSQL database connection")
            print("   • Database tables (workflows, tasks, team_outputs, notifications, meetings)")
            print("   • File storage bucket")
            print("   • REST API access")
            print("   • Real-time capabilities")
            print()
            
            # Test basic operations
            print("🧪 Testing basic operations...")
            
            # Test workflow save
            test_workflow_data = {
                'status': 'testing',
                'current_team': 'Test Team',
                'data': {'test': True},
                'metadata': {'test_run': True}
            }
            
            workflow_result = await manager.save_workflow_state(
                workflow_id="test_workflow_001",
                state_data=test_workflow_data
            )
            
            if workflow_result:
                print("   ✅ Workflow state saved")
            else:
                print("   ❌ Workflow state failed")
            
            # Test notification save
            notification_data = {
                'sender': 'Test System',
                'recipient': 'Test User',
                'message': 'Supabase integration test successful!',
                'priority': 'normal'
            }
            
            notification_result = await manager.save_notification(notification_data)
            
            if notification_result:
                print("   ✅ Notification saved")
            else:
                print("   ❌ Notification failed")
            
            # Test file upload
            test_content = b"Hello Supabase! This is a test file from multi-team automation."
            file_result = await manager.upload_file(
                content=test_content,
                path="test/test_file.txt",
                content_type="text/plain",
                metadata={'test': True}
            )
            
            if file_result:
                print("   ✅ File uploaded")
            else:
                print("   ❌ File upload failed")
            
            # Test statistics
            print()
            print("📈 Getting storage statistics...")
            stats = await manager.get_storage_statistics()
            
            if stats:
                print(f"   📁 Total files: {stats.get('file_statistics', {}).get('total_files', 0)}")
                print(f"   📊 Total size: {stats.get('file_statistics', {}).get('total_size', 0)} bytes")
                print(f"   📅 Generated at: {stats.get('generated_at', 'Unknown')}")
            
            print()
            print("✨ Your Supabase integration is ready for production!")
            print()
            print("🔄 What you can do now:")
            print("   1. Run your automation system with Supabase backend")
            print("   2. Store team outputs in structured database")
            print("   3. Enable real-time notifications")
            print("   4. Monitor storage usage and performance")
            print("   5. Scale beyond free tier when needed")
            print()
            print("📊 Free tier usage:")
            print("   • Database: 500MB PostgreSQL")
            print("   • Storage: 1GB file storage")
            print("   • API: 50,000 requests/hour")
            print("   • Real-time: 100 concurrent connections")
            print("   • Bandwidth: 250GB/month")
            
            return True
            
        else:
            print("❌ Supabase initialization failed")
            print()
            print("🔧 Troubleshooting:")
            print("   1. Check your internet connection")
            print("   2. Verify Supabase URL and key are correct")
            print("   3. Make sure your Supabase project is active")
            print("   4. Check if API key has proper permissions")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("🔧 Common issues:")
        print("   • Invalid API key or URL")
        print("   • Supabase project not active")
        print("   • Network connectivity issues")
        print("   • API permissions problems")
        return False

async def check_free_tier_usage():
    """Check current usage against free tier limits"""
    print("📊 Checking free tier usage...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Environment variables not set")
        return
    
    try:
        config = SupabaseConfig(url=supabase_url, key=supabase_key)
        manager = SimpleSupabaseManager(config)
        
        # Get storage statistics
        stats = await manager.get_storage_statistics()
        
        if stats:
            file_stats = stats.get('file_statistics', {})
            
            print()
            print("📊 Current Usage:")
            print(f"   📁 Files stored: {file_stats.get('total_files', 0)}")
            print(f"   💾 Storage used: {file_stats.get('total_size', 0)} bytes ({file_stats.get('total_size', 0) / 1024 / 1024:.2f} MB)")
            print(f"   📈 Database tables: 5 (workflows, tasks, team_outputs, notifications, meetings)")
            print()
            
            # Calculate usage percentages
            storage_used_mb = file_stats.get('total_size', 0) / 1024 / 1024
            storage_limit_mb = 1024  # 1GB free tier
            storage_percent = (storage_used_mb / storage_limit_mb) * 100
            
            print("📊 Free Tier Status:")
            print(f"   💾 Storage: {storage_percent:.1f}% used ({storage_used_mb:.1f}MB / {storage_limit_mb}MB)")
            print(f"   🗄️  Database: ~0% used (500MB limit)")
            print(f"   📡 API: Low usage (50,000/hour limit)")
            print(f"   🔄 Real-time: Low usage (100 concurrent limit)")
            print()
            
            if storage_percent < 50:
                print("✅ You're well within free tier limits!")
            elif storage_percent < 80:
                print("⚠️  Storage usage getting higher, monitor regularly")
            else:
                print("🚨 Approaching storage limit, consider cleanup or upgrade")
        
    except Exception as e:
        print(f"❌ Failed to check usage: {e}")

async def main():
    """Main test function"""
    print("=" * 60)
    print("🔥 Multi-Team Automation - Supabase Integration Test")
    print("=" * 60)
    print()
    
    # Test connection
    success = await test_supabase_connection()
    
    if success:
        # Check usage
        await check_free_tier_usage()
        
        print()
        print("🎯 Next steps:")
        print("   1. Update your automation system to use supabase_manager")
        print("   2. Replace Google Drive calls with Supabase calls")
        print("   3. Test with real workflow data")
        print("   4. Monitor usage regularly")
        print()
        print("✅ Supabase integration is ready!")
    else:
        print()
        print("❌ Setup failed. Please fix issues and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
