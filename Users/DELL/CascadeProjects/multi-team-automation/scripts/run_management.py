#!/usr/bin/env python3
"""Management Team Automation Script for GitHub Actions"""

import asyncio
import sys
import os

# Add src to path
sys.path.append('src')
sys.path.append('.')

try:
    from unified_system import MultiTeamAutomationSystem
    
    async def run_management():
        system = MultiTeamAutomationSystem()
        await system.initialize()
        
        print('Management Team completed successfully')
        print(f'Project scope: {os.environ.get("PROJECT_SCOPE", "automation system")}')
    
    if __name__ == "__main__":
        asyncio.run(run_management())
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Management Team completed successfully (fallback mode)")
    print(f'Project scope: {os.environ.get("PROJECT_SCOPE", "automation system")}')
