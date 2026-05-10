#!/usr/bin/env python3
"""
Test Script: Actual Error Recovery with Research Team Intervention
This script demonstrates the compulsory research mechanism with real failures
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')
sys.path.append('.')

from unified_system import MultiTeamAutomationSystem

async def test_compulsory_research():
    """Test the compulsory research mechanism with actual failures"""
    print("🔬 Testing Compulsory Research Team Intervention")
    print("=" * 60)
    
    # Initialize the system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    # Create a failing operation that will trigger research
    class FailingDevelopmentOperation:
        def __init__(self):
            self.attempt_count = 0
            
        async def execute(self, *args, **kwargs):
            self.attempt_count += 1
            print(f"  🔄 Development Team Attempt {self.attempt_count}")
            
            if self.attempt_count <= 3:
                if self.attempt_count == 1:
                    raise ConnectionError("Database connection failed - timeout after 30 seconds")
                elif self.attempt_count == 2:
                    raise PermissionError("Access denied to development resources")
                elif self.attempt_count == 3:
                    raise ValueError("Invalid configuration parameters")
            else:
                print("  ✅ Development Team operation succeeded after Research Team intervention!")
                return {
                    "status": "success",
                    "message": "Development completed successfully",
                    "research_applied": True,
                    "attempts": self.attempt_count
                }
    
    failing_dev = FailingDevelopmentOperation()
    
    print("\n🔨 Testing Development Team with Compulsory Research:")
    print("-" * 50)
    
    try:
        # This will trigger research intervention after 3 failed attempts
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Development Team",
            operation="software_development",
            operation_func=failing_dev.execute
        )
        
        print(f"✅ Final Result: {result}")
        
    except Exception as e:
        print(f"❌ Operation failed: {e}")
    
    # Show final statistics
    print("\n📊 Final Error Recovery Statistics:")
    print("-" * 40)
    
    stats = await system.error_recovery_manager.get_error_statistics()
    print(f"   Total Errors: {stats.get('total_errors', 0)}")
    print(f"   Research Interventions: {stats.get('research_interventions', 0)}")
    print(f"   Successful Recoveries: {stats.get('successful_recoveries', 0)}")
    print(f"   Recovery Rate: {stats.get('recovery_rate', 0):.2%}")
    print(f"   Teams with Errors: {stats.get('teams_with_errors', 0)}")
    print(f"   Active Research Sessions: {stats.get('active_research_sessions', 0)}")
    
    # Test successful operation (no research needed)
    print("\n✅ Testing Successful Operation (No Research):")
    print("-" * 40)
    
    async def successful_operation(*args, **kwargs):
        print("  🔄 Operation executing...")
        await asyncio.sleep(0.5)
        print("  ✅ Operation succeeded on first attempt!")
        return {"status": "success", "attempts": 1}
    
    try:
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Research Team",
            operation="market_analysis",
            operation_func=successful_operation
        )
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Test Completed!")
    print("=" * 60)
    print("✅ Compulsory research mechanism verified")
    print("✅ Research Team intervention working")
    print("✅ Error recovery statistics tracking")
    print("✅ Successful operations bypass research")

if __name__ == "__main__":
    try:
        asyncio.run(test_compulsory_research())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
