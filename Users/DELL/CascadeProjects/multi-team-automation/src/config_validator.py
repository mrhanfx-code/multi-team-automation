#!/usr/bin/env python3
"""
MFM Corporation - Environment Configuration Validator
Validates and manages environment configuration for the automation system
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"

@dataclass
class ValidationResult:
    """Result of environment variable validation"""
    variable: str
    status: ValidationStatus
    value: Optional[str]
    message: str
    is_critical: bool

class ConfigValidator:
    """Validates environment configuration"""
    
    def __init__(self):
        self.required_vars = self._get_required_variables()
        self.optional_vars = self._get_optional_variables()
        self.validation_rules = self._get_validation_rules()
        
    def validate_all(self, env_file: str = ".env") -> Dict[str, Any]:
        """Validate all environment variables"""
        logger.info("🔍 Validating environment configuration")
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing": [],
            "validations": [],
            "summary": {}
        }
        
        # Load environment variables
        env_vars = self._load_env_file(env_file)
        
        # Validate required variables
        required_results = self._validate_required_vars(env_vars)
        results["validations"].extend(required_results)
        
        # Validate optional variables
        optional_results = self._validate_optional_vars(env_vars)
        results["validations"].extend(optional_results)
        
        # Categorize results
        for validation in results["validations"]:
            if validation.status == ValidationStatus.ERROR:
                results["errors"].append(validation)
                results["valid"] = False
            elif validation.status == ValidationStatus.WARNING:
                results["warnings"].append(validation)
            elif validation.status == ValidationStatus.MISSING:
                results["missing"].append(validation)
                if validation.is_critical:
                    results["valid"] = False
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        # Log results
        self._log_validation_results(results)
        
        return results
    
    def _load_env_file(self, env_file: str) -> Dict[str, str]:
        """Load environment variables from file"""
        env_vars = {}
        
        if not os.path.exists(env_file):
            logger.warning(f"Environment file {env_file} not found")
            return env_vars
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            logger.error(f"Failed to load environment file {env_file}: {e}")
        
        return env_vars
    
    def _validate_required_vars(self, env_vars: Dict[str, str]) -> List[ValidationResult]:
        """Validate required environment variables"""
        results = []
        
        for var_name in self.required_vars:
            value = env_vars.get(var_name)
            rule = self.validation_rules.get(var_name, {})
            
            if not value:
                results.append(ValidationResult(
                    variable=var_name,
                    status=ValidationStatus.MISSING,
                    value=None,
                    message=f"Required environment variable {var_name} is missing",
                    is_critical=True
                ))
            else:
                validation_result = self._validate_variable(var_name, value, rule, critical=True)
                results.append(validation_result)
        
        return results
    
    def _validate_optional_vars(self, env_vars: Dict[str, str]) -> List[ValidationResult]:
        """Validate optional environment variables"""
        results = []
        
        for var_name in self.optional_vars:
            value = env_vars.get(var_name)
            rule = self.validation_rules.get(var_name, {})
            
            if not value:
                results.append(ValidationResult(
                    variable=var_name,
                    status=ValidationStatus.MISSING,
                    value=None,
                    message=f"Optional environment variable {var_name} is not set",
                    is_critical=False
                ))
            else:
                validation_result = self._validate_variable(var_name, value, rule, critical=False)
                results.append(validation_result)
        
        return results
    
    def _validate_variable(self, var_name: str, value: str, rule: Dict[str, Any], critical: bool) -> ValidationResult:
        """Validate a single environment variable"""
        try:
            # Check type
            if "type" in rule:
                type_result = self._validate_type(var_name, value, rule["type"])
                if not type_result[0]:
                    return ValidationResult(
                        variable=var_name,
                        status=ValidationStatus.ERROR,
                        value=value,
                        message=type_result[1],
                        is_critical=critical
                    )
            
            # Check format/pattern
            if "pattern" in rule:
                pattern_result = self._validate_pattern(var_name, value, rule["pattern"])
                if not pattern_result[0]:
                    return ValidationResult(
                        variable=var_name,
                        status=ValidationStatus.ERROR,
                        value=value,
                        message=pattern_result[1],
                        is_critical=critical
                    )
            
            # Check range
            if "min_value" in rule or "max_value" in rule:
                range_result = self._validate_range(var_name, value, rule.get("min_value"), rule.get("max_value"))
                if not range_result[0]:
                    return ValidationResult(
                        variable=var_name,
                        status=ValidationStatus.WARNING,
                        value=value,
                        message=range_result[1],
                        is_critical=critical
                    )
            
            # Check allowed values
            if "allowed_values" in rule:
                allowed_result = self._validate_allowed_values(var_name, value, rule["allowed_values"])
                if not allowed_result[0]:
                    return ValidationResult(
                        variable=var_name,
                        status=ValidationStatus.ERROR,
                        value=value,
                        message=allowed_result[1],
                        is_critical=critical
                    )
            
            # Check file existence
            if "file_exists" in rule and rule["file_exists"]:
                file_result = self._validate_file_exists(var_name, value)
                if not file_result[0]:
                    return ValidationResult(
                        variable=var_name,
                        status=ValidationStatus.ERROR,
                        value=value,
                        message=file_result[1],
                        is_critical=critical
                    )
            
            return ValidationResult(
                variable=var_name,
                status=ValidationStatus.VALID,
                value=value,
                message=f"Environment variable {var_name} is valid",
                is_critical=critical
            )
            
        except Exception as e:
            return ValidationResult(
                variable=var_name,
                status=ValidationStatus.ERROR,
                value=value,
                message=f"Validation failed: {e}",
                is_critical=critical
            )
    
    def _validate_type(self, var_name: str, value: str, expected_type: str) -> Tuple[bool, str]:
        """Validate variable type"""
        try:
            if expected_type == "url":
                # Basic URL validation
                if not (value.startswith("http://") or value.startswith("https://")):
                    return False, f"{var_name} must be a valid URL starting with http:// or https://"
            elif expected_type == "email":
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    return False, f"{var_name} must be a valid email address"
            elif expected_type == "port":
                port = int(value)
                if port < 1 or port > 65535:
                    return False, f"{var_name} must be between 1 and 65535"
            elif expected_type == "boolean":
                if value.lower() not in ["true", "false"]:
                    return False, f"{var_name} must be 'true' or 'false'"
            elif expected_type == "integer":
                int(value)  # Just check if it can be parsed
            elif expected_type == "float":
                float(value)  # Just check if it can be parsed
            
            return True, "Type validation passed"
        except ValueError:
            return False, f"{var_name} must be a valid {expected_type}"
    
    def _validate_pattern(self, var_name: str, value: str, pattern: str) -> Tuple[bool, str]:
        """Validate variable against regex pattern"""
        try:
            if not re.match(pattern, value):
                return False, f"{var_name} does not match required pattern"
            return True, "Pattern validation passed"
        except re.error:
            return False, f"Invalid pattern for {var_name}"
    
    def _validate_range(self, var_name: str, value: str, min_val: Optional[float], max_val: Optional[float]) -> Tuple[bool, str]:
        """Validate numeric range"""
        try:
            num_value = float(value)
            
            if min_val is not None and num_value < min_val:
                return False, f"{var_name} must be at least {min_val}"
            
            if max_val is not None and num_value > max_val:
                return False, f"{var_name} must be at most {max_val}"
            
            return True, "Range validation passed"
        except ValueError:
            return False, f"{var_name} must be a numeric value"
    
    def _validate_allowed_values(self, var_name: str, value: str, allowed_values: List[str]) -> Tuple[bool, str]:
        """Validate against allowed values"""
        if value not in allowed_values:
            return False, f"{var_name} must be one of: {', '.join(allowed_values)}"
        return True, "Allowed values validation passed"
    
    def _validate_file_exists(self, var_name: str, file_path: str) -> Tuple[bool, str]:
        """Validate file existence"""
        if not os.path.exists(file_path):
            return False, f"File specified in {var_name} does not exist: {file_path}"
        return True, "File exists validation passed"
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        total_vars = len(results["validations"])
        valid_count = len([v for v in results["validations"] if v.status == ValidationStatus.VALID])
        error_count = len(results["errors"])
        warning_count = len(results["warnings"])
        missing_count = len(results["missing"])
        
        return {
            "total_variables": total_vars,
            "valid": valid_count,
            "errors": error_count,
            "warnings": warning_count,
            "missing": missing_count,
            "overall_status": "valid" if results["valid"] else "invalid",
            "critical_issues": len([v for v in results["validations"] if v.is_critical and v.status != ValidationStatus.VALID])
        }
    
    def _log_validation_results(self, results: Dict[str, Any]):
        """Log validation results"""
        summary = results["summary"]
        
        logger.info(f"📊 Configuration Validation Summary:")
        logger.info(f"   Total Variables: {summary['total_variables']}")
        logger.info(f"   Valid: {summary['valid']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Warnings: {summary['warnings']}")
        logger.info(f"   Missing: {summary['missing']}")
        logger.info(f"   Overall Status: {summary['overall_status']}")
        
        if results["errors"]:
            logger.error("❌ Configuration Errors:")
            for error in results["errors"]:
                logger.error(f"   {error.variable}: {error.message}")
        
        if results["warnings"]:
            logger.warning("⚠️ Configuration Warnings:")
            for warning in results["warnings"]:
                logger.warning(f"   {warning.variable}: {warning.message}")
        
        if results["missing"]:
            logger.info("ℹ️ Missing Variables:")
            for missing in results["missing"]:
                logger.info(f"   {missing.variable}: {missing.message}")
    
    def _get_required_variables(self) -> List[str]:
        """Get list of required environment variables"""
        return [
            # Supabase Configuration
            "SUPABASE_URL",
            "SUPABASE_KEY",
            
            # Security Configuration
            "JWT_SECRET_KEY",
            
            # System Configuration
            "APP_NAME",
            "APP_VERSION",
            "ENVIRONMENT",
            
            # Server Configuration
            "HOST",
            "PORT"
        ]
    
    def _get_optional_variables(self) -> List[str]:
        """Get list of optional environment variables"""
        return [
            # Database Configuration
            "DATABASE_URL",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
            
            # Security Configuration
            "JWT_ALGORITHM",
            "JWT_EXPIRE_MINUTES",
            "BCRYPT_ROUNDS",
            "SESSION_SECRET_KEY",
            
            # Google Services
            "GOOGLE_DRIVE_CREDENTIALS_FILE",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            
            # Notification Configuration
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            
            # System Configuration
            "DEBUG",
            "LOG_LEVEL",
            "LOG_FILE",
            
            # Team Configuration
            "MAX_CONCURRENT_WORKFLOWS",
            "WORKFLOW_TIMEOUT_MINUTES",
            
            # Feature Flags
            "ENABLE_LEGAL_TEAM",
            "ENABLE_OPERATIONS_MANAGER",
            "ENABLE_INNOVATION_TEAM"
        ]
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for environment variables"""
        return {
            # Supabase Configuration
            "SUPABASE_URL": {
                "type": "url",
                "pattern": r"^https://[a-zA-Z0-9.-]+\.supabase\.co$"
            },
            "SUPABASE_KEY": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9._-]+$"
            },
            
            # Security Configuration
            "JWT_SECRET_KEY": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9._-]{32,}$"
            },
            "JWT_ALGORITHM": {
                "type": "string",
                "allowed_values": ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
            },
            "JWT_EXPIRE_MINUTES": {
                "type": "integer",
                "min_value": 1,
                "max_value": 10080  # 7 days
            },
            "BCRYPT_ROUNDS": {
                "type": "integer",
                "min_value": 4,
                "max_value": 31
            },
            
            # Server Configuration
            "HOST": {
                "type": "string",
                "allowed_values": ["0.0.0.0", "127.0.0.1", "localhost"]
            },
            "PORT": {
                "type": "port",
                "min_value": 1,
                "max_value": 65535
            },
            
            # System Configuration
            "DEBUG": {
                "type": "boolean"
            },
            "ENVIRONMENT": {
                "type": "string",
                "allowed_values": ["development", "testing", "staging", "production"]
            },
            "LOG_LEVEL": {
                "type": "string",
                "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            },
            
            # Team Configuration
            "MAX_CONCURRENT_WORKFLOWS": {
                "type": "integer",
                "min_value": 1,
                "max_value": 100
            },
            "WORKFLOW_TIMEOUT_MINUTES": {
                "type": "integer",
                "min_value": 5,
                "max_value": 1440  # 24 hours
            },
            
            # File Configuration
            "GOOGLE_DRIVE_CREDENTIALS_FILE": {
                "type": "string",
                "file_exists": True
            },
            
            # Email Configuration
            "SMTP_PORT": {
                "type": "port",
                "allowed_values": ["25", "465", "587", "2525"]
            },
            "SMTP_USE_TLS": {
                "type": "boolean"
            },
            
            # Feature Flags
            "ENABLE_LEGAL_TEAM": {
                "type": "boolean"
            },
            "ENABLE_OPERATIONS_MANAGER": {
                "type": "boolean"
            },
            "ENABLE_INNOVATION_TEAM": {
                "type": "boolean"
            }
        }
    
    def create_env_file(self, target_file: str = ".env") -> bool:
        """Create .env file from template"""
        try:
            template_file = ".env.example"
            
            if not os.path.exists(template_file):
                logger.error(f"Template file {template_file} not found")
                return False
            
            if os.path.exists(target_file):
                logger.warning(f"Target file {target_file} already exists")
                return False
            
            # Copy template to .env
            import shutil
            shutil.copy2(template_file, target_file)
            
            logger.info(f"✅ Created {target_file} from template")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create {target_file}: {e}")
            return False
    
    def check_env_file_exists(self, env_file: str = ".env") -> bool:
        """Check if .env file exists"""
        return os.path.exists(env_file)
    
    def get_missing_critical_vars(self, env_file: str = ".env") -> List[str]:
        """Get list of missing critical environment variables"""
        env_vars = self._load_env_file(env_file)
        missing = []
        
        for var_name in self.required_vars:
            if var_name not in env_vars:
                missing.append(var_name)
        
        return missing
    
    def generate_setup_instructions(self, env_file: str = ".env") -> str:
        """Generate setup instructions for environment configuration"""
        missing_vars = self.get_missing_critical_vars(env_file)
        
        instructions = f"""
# MFM Corporation - Environment Setup Instructions

## Status: {'✅ Configured' if not missing_vars else '❌ Setup Required'}

## Required Environment Variables: {len(self.required_vars)}
## Configured: {len(self.required_vars) - len(missing_vars)}
## Missing: {len(missing_vars)}

"""
        
        if missing_vars:
            instructions += "## Missing Critical Variables:\n"
            for var in missing_vars:
                instructions += f"- {var}\n"
            
            instructions += "\n## Setup Steps:\n"
            instructions += "1. Copy the template file:\n"
            instructions += "   cp .env.example .env\n\n"
            instructions += "2. Edit the .env file and set the missing variables:\n"
            instructions += "   nano .env\n\n"
            instructions += "3. Set the following required values:\n"
            
            for var in missing_vars:
                if "SUPABASE" in var:
                    instructions += f"   - {var}: Get from your Supabase project settings\n"
                elif "JWT" in var:
                    instructions += f"   - {var}: Generate a secure secret key\n"
                elif var in ["HOST", "PORT"]:
                    instructions += f"   - {var}: Set your server host and port\n"
                else:
                    instructions += f"   - {var}: Set appropriate value\n"
            
            instructions += "\n4. Restart the application:\n"
            instructions += "   python unified_system.py\n"
        else:
            instructions += "✅ All required environment variables are configured!\n"
            instructions += "You can now run the application with: python unified_system.py"
        
        return instructions.strip()

# Global validator instance
config_validator = ConfigValidator()

def validate_environment(env_file: str = ".env") -> Dict[str, Any]:
    """Convenience function to validate environment"""
    return config_validator.validate_all(env_file)

def setup_environment(env_file: str = ".env") -> bool:
    """Convenience function to set up environment"""
    return config_validator.create_env_file(env_file)

def check_environment_setup(env_file: str = ".env") -> str:
    """Convenience function to check environment setup"""
    return config_validator.generate_setup_instructions(env_file)
