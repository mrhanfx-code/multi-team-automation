#!/usr/bin/env python3
"""
Simple Supabase Connection Test
"""

import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_supabase_simple():
    """Test basic Supabase connection"""
    print("🔍 Testing Supabase Connection...")
    print()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    print(f"🔗 URL: {url}")
    print(f"🔑 Key: {key[:30]}...")
    print()
    
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        # Test project info endpoint
        print("📊 Testing project info...")
        try:
            async with session.get(
                f"{url}/rest/v1/",
                headers=headers,
                ssl=ssl_context
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Project accessible!")
                    data = await response.text()
                    print(f"   Data: {data[:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test auth config
        print("🔐 Testing auth config...")
        try:
            async with session.get(
                f"{url}/auth/v1/settings",
                headers=headers,
                ssl=ssl_context
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Auth config accessible!")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test health endpoint
        print("💓 Testing health endpoint...")
        try:
            async with session.get(
                f"{url}/health",
                ssl=ssl_context
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Health check passed!")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False

async def main():
    success = await test_supabase_simple()
    
    if success:
        print()
        print("🎉 Supabase connection successful!")
        print("✅ Ready to integrate with multi-team automation")
    else:
        print()
        print("❌ Supabase connection failed")
        print("🔧 Possible issues:")
        print("   • Project not active/paused")
        print("   • API key incorrect")
        print("   • Project URL incorrect")
        print("   • Network connectivity issues")

if __name__ == "__main__":
    asyncio.run(main())
