#!/usr/bin/env python3
"""
MFM Corporation - System Setup Script
Automated setup and configuration for the Multi-Team Automation System
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Add src to path
sys.path.append('src')
sys.path.append('.')

from src.config_validator import ConfigValidator, validate_environment, setup_environment, check_environment_setup
from src.supabase_client import SupabaseManager, SupabaseConfig
from src.exceptions import MFMException, ConfigurationException, SystemException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSetup:
    """Complete system setup manager"""
    
    def __init__(self):
        self.config_validator = ConfigValidator()
        self.supabase_manager = None
        self.setup_steps = [
            "validate_environment",
            "setup_database", 
            "create_directories",
            "install_dependencies",
            "test_connections",
            "initialize_system"
        ]
        
    async def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete system setup"""
        logger.info("🚀 Starting MFM Corporation Multi-Team Automation System Setup")
        
        setup_results = {
            "success": True,
            "completed_steps": [],
            "failed_steps": [],
            "warnings": [],
            "errors": [],
            "summary": {}
        }
        
        for step in self.setup_steps:
            try:
                logger.info(f"🔄 Running setup step: {step}")
                result = await self._run_setup_step(step)
                
                if result["success"]:
                    setup_results["completed_steps"].append(step)
                    logger.info(f"✅ Step '{step}' completed successfully")
                else:
                    setup_results["failed_steps"].append(step)
                    setup_results["errors"].extend(result.get("errors", []))
                    setup_results["success"] = False
                    logger.error(f"❌ Step '{step}' failed: {result.get('errors', [])}")
                    
            except Exception as e:
                setup_results["failed_steps"].append(step)
                setup_results["errors"].append(f"Step '{step}' failed with exception: {str(e)}")
                setup_results["success"] = False
                logger.error(f"❌ Step '{step}' failed with exception: {e}")
        
        # Generate summary
        setup_results["summary"] = self._generate_setup_summary(setup_results)
        
        # Log final results
        self._log_setup_results(setup_results)
        
        return setup_results
    
    async def _run_setup_step(self, step: str) -> Dict[str, Any]:
        """Run individual setup step"""
        try:
            if step == "validate_environment":
                return await self._validate_environment_setup()
            elif step == "setup_database":
                return await self._setup_database()
            elif step == "create_directories":
                return await self._create_directories()
            elif step == "install_dependencies":
                return await self._install_dependencies()
            elif step == "test_connections":
                return await self._test_connections()
            elif step == "initialize_system":
                return await self._initialize_system()
            else:
                return {"success": False, "errors": [f"Unknown setup step: {step}"]}
                
        except Exception as e:
            return {"success": False, "errors": [str(e)]}
    
    async def _validate_environment_setup(self) -> Dict[str, Any]:
        """Validate environment configuration"""
        try:
            logger.info("🔍 Validating environment configuration")
            
            # Check if .env file exists
            if not self.config_validator.check_env_file_exists():
                logger.info("📝 Creating .env file from template")
                if not self.config_validator.create_env_file():
                    return {"success": False, "errors": ["Failed to create .env file"]}
            
            # Validate environment variables
            validation_results = validate_environment()
            
            if not validation_results["valid"]:
                errors = [error.message for error in validation_results["errors"]]
                warnings = [warning.message for warning in validation_results["warnings"]]
                
                return {
                    "success": False,
                    "errors": errors,
                    "warnings": warnings,
                    "missing_vars": [var.variable for var in validation_results["missing"] if var.is_critical]
                }
            
            return {
                "success": True,
                "message": "Environment configuration is valid",
                "warnings": [warning.message for warning in validation_results["warnings"]]
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Environment validation failed: {str(e)}"]}
    
    async def _setup_database(self) -> Dict[str, Any]:
        """Setup Supabase database"""
        try:
            logger.info("🗄️ Setting up Supabase database")
            
            # Create Supabase manager
            try:
                self.supabase_manager = SupabaseManager()
                await self.supabase_manager.initialize()
            except Exception as e:
                return {"success": False, "errors": [f"Failed to initialize Supabase manager: {str(e)}"]}
            
            # Test connection
            if not await self.supabase_manager.test_connection():
                return {"success": False, "errors": ["Supabase connection test failed"]}
            
            # Run database migration
            migration_file = "database/migrations/001_initial_schema.sql"
            if os.path.exists(migration_file):
                if await self.supabase_manager.run_migration(migration_file):
                    logger.info("✅ Database migration completed")
                else:
                    return {"success": False, "errors": ["Database migration failed"]}
            else:
                logger.warning("⚠️ Migration file not found, skipping database setup")
            
            return {"success": True, "message": "Database setup completed successfully"}
            
        except Exception as e:
            return {"success": False, "errors": [f"Database setup failed: {str(e)}"]}
    
    async def _create_directories(self) -> Dict[str, Any]:
        """Create necessary directories"""
        try:
            logger.info("📁 Creating system directories")
            
            directories = [
                "logs",
                "uploads",
                "backups",
                "temp",
                "exports",
                "reports",
                "certificates"
            ]
            
            created_dirs = []
            failed_dirs = []
            
            for directory in directories:
                try:
                    Path(directory).mkdir(exist_ok=True)
                    created_dirs.append(directory)
                except Exception as e:
                    failed_dirs.append(f"{directory}: {str(e)}")
            
            if failed_dirs:
                return {"success": False, "errors": failed_dirs, "created": created_dirs}
            
            return {"success": True, "message": f"Created {len(created_dirs)} directories", "created": created_dirs}
            
        except Exception as e:
            return {"success": False, "errors": [f"Directory creation failed: {str(e)}"]}
    
    async def _install_dependencies(self) -> Dict[str, Any]:
        """Install Python dependencies"""
        try:
            logger.info("📦 Installing Python dependencies")
            
            # Check if requirements.txt exists
            if not os.path.exists("requirements.txt"):
                return {"success": False, "errors": ["requirements.txt file not found"]}
            
            # Install dependencies
            import subprocess
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    return {"success": True, "message": "Dependencies installed successfully"}
                else:
                    return {"success": False, "errors": [f"pip install failed: {result.stderr}"]}
                    
            except subprocess.TimeoutExpired:
                return {"success": False, "errors": ["Dependency installation timed out"]}
            except Exception as e:
                return {"success": False, "errors": [f"Failed to run pip install: {str(e)}"]}
            
        except Exception as e:
            return {"success": False, "errors": [f"Dependency installation failed: {str(e)}"]}
    
    async def _test_connections(self) -> Dict[str, Any]:
        """Test all system connections"""
        try:
            logger.info("🔗 Testing system connections")
            
            test_results = {}
            
            # Test Supabase connection
            if self.supabase_manager:
                test_results["supabase"] = await self.supabase_manager.test_connection()
            else:
                test_results["supabase"] = False
            
            # Test basic imports
            try:
                from unified_system import MultiTeamAutomationSystem
                test_results["imports"] = True
            except Exception as e:
                test_results["imports"] = False
                logger.warning(f"Import test failed: {e}")
            
            # Test configuration loading
            try:
                from dotenv import load_dotenv
                load_dotenv()
                test_results["config"] = True
            except Exception:
                test_results["config"] = False
            
            # Check if all critical tests passed
            critical_tests = ["supabase", "imports"]
            all_critical_passed = all(test_results.get(test, False) for test in critical_tests)
            
            if not all_critical_passed:
                failed_tests = [test for test in critical_tests if not test_results.get(test, False)]
                return {"success": False, "errors": [f"Critical connection tests failed: {failed_tests}"], "results": test_results}
            
            return {"success": True, "message": "All connection tests passed", "results": test_results}
            
        except Exception as e:
            return {"success": False, "errors": [f"Connection testing failed: {str(e)}"]}
    
    async def _initialize_system(self) -> Dict[str, Any]:
        """Initialize the automation system"""
        try:
            logger.info("🎯 Initializing automation system")
            
            # Import and initialize the system
            from unified_system import MultiTeamAutomationSystem
            
            system = MultiTeamAutomationSystem()
            
            # Initialize all components
            if await system.initialize():
                return {"success": True, "message": "System initialized successfully"}
            else:
                return {"success": False, "errors": ["System initialization failed"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"System initialization failed: {str(e)}"]}
    
    def _generate_setup_summary(self, setup_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate setup summary"""
        return {
            "total_steps": len(self.setup_steps),
            "completed_steps": len(setup_results["completed_steps"]),
            "failed_steps": len(setup_results["failed_steps"]),
            "success_rate": len(setup_results["completed_steps"]) / len(self.setup_steps) * 100,
            "overall_success": setup_results["success"],
            "warnings_count": len(setup_results["warnings"]),
            "errors_count": len(setup_results["errors"])
        }
    
    def _log_setup_results(self, setup_results: Dict[str, Any]):
        """Log setup results"""
        summary = setup_results["summary"]
        
        logger.info("📊 Setup Summary:")
        logger.info(f"   Total Steps: {summary['total_steps']}")
        logger.info(f"   Completed: {summary['completed_steps']}")
        logger.info(f"   Failed: {summary['failed_steps']}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Overall Success: {'✅' if summary['overall_success'] else '❌'}")
        
        if setup_results["warnings"]:
            logger.warning(f"⚠️ Warnings ({len(setup_results['warnings'])}):")
            for warning in setup_results["warnings"][:5]:
                logger.warning(f"   • {warning}")
        
        if setup_results["errors"]:
            logger.error(f"❌ Errors ({len(setup_results['errors'])}):")
            for error in setup_results["errors"][:5]:
                logger.error(f"   • {error}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.supabase_manager:
            await self.supabase_manager.close()

class QuickSetup:
    """Quick setup for common scenarios"""
    
    @staticmethod
    async def setup_development():
        """Setup for development environment"""
        logger.info("🛠️ Setting up development environment")
        
        # Create basic .env for development
        env_content = """
# Development Environment Configuration
APP_NAME=MFM Corporation Multi-Team Automation
APP_VERSION=3.0.0
DEBUG=true
ENVIRONMENT=development

# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Security Configuration
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Team Configuration
MAX_CONCURRENT_WORKFLOWS=5
WORKFLOW_TIMEOUT_MINUTES=30

# Feature Flags
ENABLE_LEGAL_TEAM=true
ENABLE_OPERATIONS_MANAGER=true
ENABLE_INNOVATION_TEAM=true
"""
        
        with open(".env", "w") as f:
            f.write(env_content.strip())
        
        logger.info("✅ Development .env file created")
        logger.info("📝 Please update SUPABASE_URL and SUPABASE_KEY with your actual values")
        
        return {"success": True, "message": "Development environment setup completed"}
    
    @staticmethod
    async def setup_production():
        """Setup for production environment"""
        logger.info("🚀 Setting up production environment")
        
        # Check if .env exists
        if not os.path.exists(".env"):
            logger.error("❌ .env file not found. Please create it from .env.example")
            return {"success": False, "errors": [".env file not found"]}
        
        # Validate production settings
        validation_results = validate_environment()
        
        if not validation_results["valid"]:
            return {"success": False, "errors": validation_results["errors"]}
        
        logger.info("✅ Production environment is properly configured")
        return {"success": True, "message": "Production environment validated"}
    
    @staticmethod
    async def check_system():
        """Check system status"""
        logger.info("🔍 Checking system status")
        
        status = {
            "environment": "unknown",
            "dependencies": "unknown",
            "database": "unknown",
            "system": "unknown"
        }
        
        # Check environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
            status["environment"] = "configured"
        except Exception:
            status["environment"] = "not_configured"
        
        # Check dependencies
        try:
            import aiohttp
            import supabase
            import pydantic
            status["dependencies"] = "installed"
        except ImportError as e:
            status["dependencies"] = f"missing: {e}"
        
        # Check database
        try:
            from src.supabase_client import get_supabase_manager
            manager = await get_supabase_manager()
            if await manager.test_connection():
                status["database"] = "connected"
            else:
                status["database"] = "connection_failed"
        except Exception as e:
            status["database"] = f"error: {e}"
        
        # Check system
        try:
            from unified_system import MultiTeamAutomationSystem
            system = MultiTeamAutomationSystem()
            if await system.initialize():
                status["system"] = "ready"
            else:
                status["system"] = "initialization_failed"
        except Exception as e:
            status["system"] = f"error: {e}"
        
        return {"success": True, "status": status}

async def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MFM Corporation Multi-Team Automation System Setup")
    parser.add_argument("--mode", choices=["complete", "dev", "prod", "check"], 
                       default="complete", help="Setup mode")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_manager = SystemSetup()
    
    try:
        if args.mode == "complete":
            results = await setup_manager.run_complete_setup()
        elif args.mode == "dev":
            results = await QuickSetup.setup_development()
        elif args.mode == "prod":
            results = await QuickSetup.setup_production()
        elif args.mode == "check":
            results = await QuickSetup.check_system()
        
        # Print results
        print("\n" + "="*60)
        print("MFM CORPORATION - SETUP RESULTS")
        print("="*60)
        
        if results["success"]:
            print("✅ SETUP SUCCESSFUL")
        else:
            print("❌ SETUP FAILED")
        
        if "message" in results:
            print(f"\nMessage: {results['message']}")
        
        if "errors" in results and results["errors"]:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  • {error}")
        
        if "warnings" in results and results["warnings"]:
            print(f"\nWarnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                print(f"  • {warning}")
        
        if "status" in results:
            print(f"\nSystem Status:")
            for component, status in results["status"].items():
                status_icon = "✅" if status in ["configured", "installed", "connected", "ready"] else "❌"
                print(f"  {status_icon} {component.title()}: {status}")
        
        if "summary" in results:
            summary = results["summary"]
            print(f"\nSummary:")
            print(f"  Steps Completed: {summary['completed_steps']}/{summary['total_steps']}")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        print("="*60)
        
        # Return appropriate exit code
        sys.exit(0 if results["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with exception: {e}")
        sys.exit(1)
    finally:
        await setup_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
