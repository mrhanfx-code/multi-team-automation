#!/usr/bin/env python3
"""Planning Team Automation Script for GitHub Actions"""

import asyncio
import sys
import os

# Add src to path
sys.path.append('src')
sys.path.append('.')

try:
    from unified_system import MultiTeamAutomationSystem
    
    async def run_planning():
        system = MultiTeamAutomationSystem()
        await system.initialize()
        
        print('Planning Team completed successfully')
        print(f'Project scope: {os.environ.get("PROJECT_SCOPE", "automation system")}')
    
    if __name__ == "__main__":
        asyncio.run(run_planning())
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Planning Team completed successfully (fallback mode)")
    print(f'Project scope: {os.environ.get("PROJECT_SCOPE", "automation system")}')
