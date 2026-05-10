"""
Error Handling and Retry Mechanisms for Multi-Team Automation System
"""

import asyncio
import logging
import functools
from typing import Callable, Any, Optional, Type, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AutomationException(Exception):
    """Base exception for automation system"""
    def __init__(self, message: str, error_code: str = None, retry_after: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.retry_after = retry_after
        self.timestamp = datetime.now()

class TeamException(AutomationException):
    """Team-specific exceptions"""
    pass

class NetworkException(AutomationException):
    """Network-related exceptions"""
    pass

class SecurityException(AutomationException):
    """Security-related exceptions"""
    pass

class RetryConfig:
    """Configuration for retry mechanisms"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures"""
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise AutomationException("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

def retry(
    retry_config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """Retry decorator for async functions"""
    if retry_config is None:
        retry_config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {retry_config.max_attempts} attempts: {e}")
                        raise AutomationException(
                            f"Max retry attempts exceeded for {func.__name__}",
                            error_code="MAX_RETRIES_EXCEEDED"
                        ) from e
                    
                    delay = _calculate_delay(attempt, retry_config)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def _calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt"""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        import random
        delay *= (0.5 + random.random() * 0.5)
    
    return delay

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_file: str = "automation_errors.log"):
        self.log_file = log_file
        self.error_counts = {}
        self.error_history = []
        
    async def handle_error(
        self,
        error: Exception,
        context: str = "",
        severity: str = "ERROR",
        team_name: str = None
    ):
        """Handle and log errors with context"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "severity": severity,
            "team_name": team_name,
            "error_code": getattr(error, 'error_code', None)
        }
        
        # Log error
        logger.error(f"Error in {context}: {error}")
        
        # Store error history
        self.error_history.append(error_info)
        
        # Update error counts
        error_key = f"{type(error).__name__}_{context}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Write to file
        await self._write_error_to_file(error_info)
        
        # Check if escalation needed
        await self._check_escalation(error_info)
    
    async def _write_error_to_file(self, error_info: dict):
        """Write error information to log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(error_info) + '\n')
        except Exception as e:
            logger.error(f"Failed to write error to file: {e}")
    
    async def _check_escalation(self, error_info: dict):
        """Check if error requires escalation"""
        error_key = f"{error_info['error_type']}_{error_info['context']}"
        
        # Escalate if same error occurs multiple times
        if self.error_counts[error_key] >= 3:
            await self._escalate_error(error_info)
    
    async def _escalate_error(self, error_info: dict):
        """Escalate error to management team"""
        logger.critical(f"ESCALATION NEEDED: Repeated error - {error_info}")
        # Implementation would send notification to management team
    
    def get_error_summary(self) -> dict:
        """Get summary of all errors"""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }

class HealthChecker:
    """Health check system for monitoring component status"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
    
    def register_check(self, name: str, check_func: Callable, interval: float = 60.0):
        """Register a health check"""
        self.checks[name] = {
            "func": check_func,
            "interval": interval,
            "last_run": None
        }
    
    async def run_check(self, name: str) -> dict:
        """Run a specific health check"""
        if name not in self.checks:
            raise ValueError(f"Health check '{name}' not registered")
        
        check = self.checks[name]
        start_time = datetime.now()
        
        try:
            result = await check["func"]()
            duration = (datetime.now() - start_time).total_seconds()
            
            health_result = {
                "name": name,
                "status": "HEALTHY",
                "timestamp": start_time.isoformat(),
                "duration": duration,
                "result": result
            }
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            health_result = {
                "name": name,
                "status": "UNHEALTHY",
                "timestamp": start_time.isoformat(),
                "duration": duration,
                "error": str(e)
            }
        
        self.last_results[name] = health_result
        return health_result
    
    async def run_all_checks(self) -> dict:
        """Run all registered health checks"""
        results = {}
        tasks = []
        
        for name in self.checks:
            task = asyncio.create_task(self.run_check(name))
            tasks.append((name, task))
        
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                results[name] = {
                    "name": name,
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def get_system_health(self) -> dict:
        """Get overall system health status"""
        if not self.last_results:
            return {"status": "UNKNOWN", "message": "No health checks run"}
        
        healthy_count = sum(1 for r in self.last_results.values() if r["status"] == "HEALTHY")
        total_count = len(self.last_results)
        
        if healthy_count == total_count:
            status = "HEALTHY"
        elif healthy_count > total_count / 2:
            status = "DEGRADED"
        else:
            status = "UNHEALTHY"
        
        return {
            "status": status,
            "healthy_checks": healthy_count,
            "total_checks": total_count,
            "last_updated": max(r["timestamp"] for r in self.last_results.values())
        }

# Global instances
error_handler = ErrorHandler()
health_checker = HealthChecker()

# Example health check functions
async def check_database_connection() -> dict:
    """Check database connectivity"""
    # Implementation would check actual database
    return {"connected": True, "response_time_ms": 50}

async def check_external_apis() -> dict:
    """Check external API availability"""
    # Implementation would check actual APIs
    return {"github_api": "OK", "notification_service": "OK"}

async def check_system_resources() -> dict:
    """Check system resource usage"""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

# Register default health checks
health_checker.register_check("database", check_database_connection, 30.0)
health_checker.register_check("external_apis", check_external_apis, 60.0)
health_checker.register_check("system_resources", check_system_resources, 120.0)
