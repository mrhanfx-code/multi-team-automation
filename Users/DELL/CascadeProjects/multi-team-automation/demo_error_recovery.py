#!/usr/bin/env python3
"""
Demo Script: Compulsory Research Team Error Recovery System
Shows how Research Team automatically intervenes after 3 failed attempts
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')
sys.path.append('.')

from unified_system import MultiTeamAutomationSystem

class FailingOperation:
    """Simulates operations that fail to trigger research intervention"""
    
    def __init__(self, fail_count=3, team_name="Demo Team"):
        self.fail_count = fail_count
        self.team_name = team_name
        self.attempt = 0
        
    async def simulate_failing_operation(self, *args, **kwargs):
        """Simulate an operation that fails multiple times"""
        self.attempt += 1
        print(f"  🔄 Attempt {self.attempt}: {self.team_name} operation")
        
        if self.attempt <= self.fail_count:
            # Simulate different types of errors
            if self.attempt == 1:
                raise ConnectionError("Network connection timeout")
            elif self.attempt == 2:
                raise PermissionError("Access denied to resource")
            elif self.attempt == 3:
                raise ValueError("Invalid data format received")
            else:
                raise RuntimeError("Unexpected system error")
        else:
            # Success after research intervention
            print(f"  ✅ {self.team_name} operation succeeded after research intervention!")
            return {"status": "success", "message": "Operation completed successfully"}

async def demo_error_recovery():
    """Demonstrate the compulsory research team error recovery system"""
    print("🚀 Demo: Compulsory Research Team Error Recovery System")
    print("=" * 60)
    
    # Initialize the system
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    print("\n📊 System Status:")
    status = await system.get_system_status()
    print(f"   Name: {status['system_name']}")
    print(f"   Version: {status['version']}")
    print(f"   Error Recovery: ✅ Enabled")
    
    # Demo 1: Development Team with simulated errors
    print("\n🔨 Demo 1: Development Team Error Recovery")
    print("-" * 40)
    
    failing_dev = FailingOperation(fail_count=3, team_name="Development Team")
    
    try:
        # This will trigger research intervention after 3 failed attempts
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Development Team",
            operation="software_development",
            operation_func=failing_dev.simulate_failing_operation
        )
        print(f"   ✅ Final Result: {result}")
    except Exception as e:
        print(f"   ❌ Final Error: {e}")
    
    # Demo 2: Management Team with different error patterns
    print("\n📈 Demo 2: Management Team Error Recovery")
    print("-" * 40)
    
    failing_mgmt = FailingOperation(fail_count=3, team_name="Management Team")
    
    try:
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Management Team",
            operation="comprehensive_review",
            operation_func=failing_mgmt.simulate_failing_operation
        )
        print(f"   ✅ Final Result: {result}")
    except Exception as e:
        print(f"   ❌ Final Error: {e}")
    
    # Demo 3: General Team with critical errors
    print("\n🎯 Demo 3: General Manager Error Recovery")
    print("-" * 40)
    
    failing_gm = FailingOperation(fail_count=3, team_name="General Manager")
    
    try:
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="General Manager",
            operation="executive_review",
            operation_func=failing_gm.simulate_failing_operation
        )
        print(f"   ✅ Final Result: {result}")
    except Exception as e:
        print(f"   ❌ Final Error: {e}")
    
    # Show error recovery statistics
    print("\n📊 Error Recovery Statistics:")
    print("-" * 40)
    
    stats = await system.error_recovery_manager.get_error_statistics()
    print(f"   Total Errors: {stats.get('total_errors', 0)}")
    print(f"   Research Interventions: {stats.get('research_interventions', 0)}")
    print(f"   Successful Recoveries: {stats.get('successful_recoveries', 0)}")
    print(f"   Recovery Rate: {stats.get('recovery_rate', 0):.2%}")
    print(f"   Teams with Errors: {stats.get('teams_with_errors', 0)}")
    print(f"   Active Research Sessions: {stats.get('active_research_sessions', 0)}")
    
    # Demo 4: Show what happens with successful operations (no research needed)
    print("\n✅ Demo 4: Successful Operation (No Research Needed)")
    print("-" * 40)
    
    async def successful_operation(*args, **kwargs):
        print("  🔄 Attempt 1: Operation executing...")
        await asyncio.sleep(0.5)
        print("  ✅ Operation succeeded on first attempt!")
        return {"status": "success", "attempts": 1}
    
    try:
        result = await system.error_recovery_manager.execute_with_recovery(
            team_name="Research Team",
            operation="market_analysis",
            operation_func=successful_operation
        )
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 Demo Completed!")
    print("=" * 60)
    print("Key Features Demonstrated:")
    print("  ✅ Compulsory research after 3 failed attempts")
    print("  ✅ Automatic error categorization and analysis")
    print("  ✅ Research Team intervention with solutions")
    print("  ✅ Error recovery statistics and monitoring")
    print("  ✅ Fallback mechanisms for all teams")

async def demo_complete_workflow_with_errors():
    """Demo complete workflow with simulated errors"""
    print("\n🚀 Demo: Complete Workflow with Error Recovery")
    print("=" * 60)
    
    system = MultiTeamAutomationSystem()
    await system.initialize()
    
    print("Running complete workflow with error recovery enabled...")
    
    try:
        # This will use the error recovery system for all team operations
        result = await system.run_complete_workflow(
            "AI-Powered Error Recovery Platform",
            "Enterprise implementation with compulsory research"
        )
        
        print(f"✅ Workflow Completed Successfully!")
        print(f"📊 Overall Performance: {result['overall_performance']['overall_score']:.2%}")
        print(f"🎯 Performance Level: {result['overall_performance']['performance_level']}")
        
    except Exception as e:
        print(f"⚠️  Workflow encountered issues: {e}")
        print("Research Team interventions were triggered to resolve issues")

if __name__ == "__main__":
    print("🔬 Research Team Error Recovery System Demo")
    print("=" * 60)
    print("This demo shows the compulsory research mechanism where")
    print("the Research Team automatically intervenes after 3 failed attempts.")
    print("")
    
    try:
        asyncio.run(demo_error_recovery())
        asyncio.run(demo_complete_workflow_with_errors())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
