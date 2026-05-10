#!/usr/bin/env python3
"""
Debug Error Recovery System
Test the error recovery mechanism step by step
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')
sys.path.append('.')

from unified_system import MultiTeamAutomationSystem

async def debug_error_recovery():
    """Debug the error recovery system step by step"""
    print("🔍 Debug Error Recovery System")
    print("=" * 50)
    
    # Initialize the system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    print(f"✅ System initialized: {system.name} v{system.version}")
    
    # Test the error recovery manager directly
    print(f"\n🔧 Testing Error Recovery Manager...")
    print(f"   Error Recovery Manager: {system.error_recovery_manager}")
    print(f"   Max Attempts: {system.error_recovery_manager.max_attempts}")
    
    # Create a simple failing operation
    class SimpleFailingOperation:
        def __init__(self):
            self.call_count = 0
            
        async def fail_three_times(self, *args, **kwargs):
            self.call_count += 1
            print(f"  🔄 Call #{self.call_count}: Attempting operation...")
            
            if self.call_count <= 3:
                raise Exception(f"Failed attempt #{self.call_count}")
            else:
                return {"success": True, "attempts": self.call_count}
    
    failing_op = SimpleFailingOperation()
    
    print(f"\n🧪 Testing error recovery with simple failing operation...")
    
    try:
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Test Team",
            operation="test_operation",
            operation_func=failing_op.fail_three_times
        )
        
        print(f"✅ Success! Result: {result}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print(f"   Operation was called {failing_op.call_count} times")
    
    # Check error history
    print(f"\n📊 Error History:")
    for key, history in system.error_recovery_manager.error_history.items():
        print(f"   {key}: {history}")
    
    # Check statistics
    stats = await system.error_recovery_manager.get_error_statistics()
    print(f"\n📈 Statistics: {stats}")

if __name__ == "__main__":
    try:
        asyncio.run(debug_error_recovery())
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
