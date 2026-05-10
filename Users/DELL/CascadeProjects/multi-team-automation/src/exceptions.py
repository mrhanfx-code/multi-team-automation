#!/usr/bin/env python3
"""
MFM Corporation - Custom Exception Classes
Defines specific exception types for better error handling and debugging
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_API = "external_api"
    FILE_OPERATION = "file_operation"
    CONFIGURATION = "configuration"

class MFMException(Exception):
    """Base exception for MFM Corporation system"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 category: ErrorCategory = ErrorCategory.SYSTEM, 
                 context: Optional[Dict[str, Any]] = None, 
                 cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.error_id = self._generate_error_id()
        
        # Log the exception
        self._log_exception()
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _log_exception(self):
        """Log the exception with appropriate level"""
        log_message = f"[{self.error_id}] {self.message}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=self.cause)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=self.cause)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, exc_info=self.cause)
        else:
            logger.info(log_message, exc_info=self.cause)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            'error_id': self.error_id,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'cause': str(self.cause) if self.cause else None
        }

# =============================================================================
# SYSTEM EXCEPTIONS
# =============================================================================

class SystemException(MFMException):
    """System-level exceptions"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context, cause)

class ConfigurationException(MFMException):
    """Configuration-related exceptions"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.CONFIGURATION, context, cause)

class InitializationException(MFMException):
    """Initialization failures"""
    
    def __init__(self, component: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['component'] = component
        super().__init__(f"Failed to initialize {component}: {message}", ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context, cause)

# =============================================================================
# NETWORK EXCEPTIONS
# =============================================================================

class NetworkException(MFMException):
    """Network-related exceptions"""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None, 
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if url:
            context['url'] = url
        if status_code:
            context['status_code'] = status_code
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.NETWORK, context, cause)

class ConnectionException(NetworkException):
    """Connection failures"""
    
    def __init__(self, service: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['service'] = service
        super().__init__(f"Connection failed to {service}: {message}", context=context, cause=cause)

class TimeoutException(NetworkException):
    """Timeout exceptions"""
    
    def __init__(self, operation: str, timeout_seconds: int, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['operation'] = operation
        context['timeout_seconds'] = timeout_seconds
        super().__init__(f"Operation '{operation}' timed out after {timeout_seconds} seconds", context=context, cause=cause)

# =============================================================================
# DATABASE EXCEPTIONS
# =============================================================================

class DatabaseException(MFMException):
    """Database-related exceptions"""
    
    def __init__(self, message: str, table: Optional[str] = None, operation: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if table:
            context['table'] = table
        if operation:
            context['operation'] = operation
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.DATABASE, context, cause)

class QueryException(DatabaseException):
    """Query execution failures"""
    
    def __init__(self, query: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['query'] = query
        super().__init__(f"Query failed: {message}", operation='query', context=context, cause=cause)

class ConnectionPoolException(DatabaseException):
    """Connection pool issues"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(f"Connection pool error: {message}", operation='connection_pool', context=context, cause=cause)

# =============================================================================
# AUTHENTICATION EXCEPTIONS
# =============================================================================

class AuthenticationException(MFMException):
    """Authentication failures"""
    
    def __init__(self, message: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if user_id:
            context['user_id'] = user_id
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.AUTHENTICATION, context, cause)

class AuthorizationException(AuthenticationException):
    """Authorization failures"""
    
    def __init__(self, resource: str, action: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['resource'] = resource
        context['action'] = action
        super().__init__(f"Access denied: {action} on {resource}", user_id=user_id, context=context, cause=cause)

class TokenException(AuthenticationException):
    """Token-related issues"""
    
    def __init__(self, message: str, token_type: str = "access_token", context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['token_type'] = token_type
        super().__init__(f"Token error ({token_type}): {message}", context=context, cause=cause)

# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationException(MFMException):
    """Data validation failures"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None,
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.VALIDATION, context, cause)

class RequiredFieldException(ValidationException):
    """Missing required fields"""
    
    def __init__(self, field: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"Required field '{field}' is missing", field=field, context=context)

class InvalidFormatException(ValidationException):
    """Invalid data format"""
    
    def __init__(self, field: str, expected_format: str, actual_value: Any, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"Field '{field}' must be {expected_format}, got: {actual_value}", 
                        field=field, value=actual_value, context=context)

class RangeException(ValidationException):
    """Value out of range"""
    
    def __init__(self, field: str, value: Any, min_value: Any, max_value: Any, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"Field '{field}' value {value} is out of range [{min_value}, {max_value}]", 
                        field=field, value=value, context=context)

# =============================================================================
# BUSINESS LOGIC EXCEPTIONS
# =============================================================================

class BusinessLogicException(MFMException):
    """Business logic violations"""
    
    def __init__(self, message: str, rule: Optional[str] = None, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if rule:
            context['rule'] = rule
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, context, cause)

class WorkflowException(BusinessLogicException):
    """Workflow-related exceptions"""
    
    def __init__(self, workflow_id: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['workflow_id'] = workflow_id
        super().__init__(f"Workflow {workflow_id}: {message}", context=context, cause=cause)

class TaskException(BusinessLogicException):
    """Task-related exceptions"""
    
    def __init__(self, task_id: str, team_name: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['task_id'] = task_id
        context['team_name'] = team_name
        super().__init__(f"Task {task_id} ({team_name}): {message}", context=context, cause=cause)

class TeamException(BusinessLogicException):
    """Team-related exceptions"""
    
    def __init__(self, team_name: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['team_name'] = team_name
        super().__init__(f"Team '{team_name}': {message}", context=context, cause=cause)

class ResourceException(BusinessLogicException):
    """Resource-related exceptions"""
    
    def __init__(self, resource_type: str, resource_id: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['resource_type'] = resource_type
        context['resource_id'] = resource_id
        super().__init__(f"Resource {resource_type} '{resource_id}': {message}", context=context, cause=cause)

# =============================================================================
# EXTERNAL API EXCEPTIONS
# =============================================================================

class ExternalAPIException(MFMException):
    """External API failures"""
    
    def __init__(self, api_name: str, message: str, endpoint: Optional[str] = None, 
                 status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None,
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['api_name'] = api_name
        if endpoint:
            context['endpoint'] = endpoint
        if status_code:
            context['status_code'] = status_code
        if response_data:
            context['response_data'] = response_data
        super().__init__(f"External API ({api_name}): {message}", ErrorSeverity.MEDIUM, ErrorCategory.EXTERNAL_API, context, cause)

class GoogleAPIException(ExternalAPIException):
    """Google API specific exceptions"""
    
    def __init__(self, service: str, message: str, **kwargs):
        super().__init__(f"Google {service}", message, **kwargs)

class SupabaseException(ExternalAPIException):
    """Supabase specific exceptions"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__("Supabase", message, **kwargs)

# =============================================================================
# FILE OPERATION EXCEPTIONS
# =============================================================================

class FileOperationException(MFMException):
    """File operation failures"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if file_path:
            context['file_path'] = file_path
        if operation:
            context['operation'] = operation
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.FILE_OPERATION, context, cause)

class FileNotFoundException(FileOperationException):
    """File not found"""
    
    def __init__(self, file_path: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"File not found: {file_path}", file_path=file_path, operation='read', context=context)

class FilePermissionException(FileOperationException):
    """File permission issues"""
    
    def __init__(self, file_path: str, operation: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"Permission denied for {operation} on {file_path}", file_path=file_path, operation=operation, context=context)

class FileCorruptedException(FileOperationException):
    """File corruption issues"""
    
    def __init__(self, file_path: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"File corrupted: {file_path}", file_path=file_path, operation='read', context=context)

# =============================================================================
# LEGAL TEAM EXCEPTIONS
# =============================================================================

class LegalException(BusinessLogicException):
    """Legal team specific exceptions"""
    
    def __init__(self, message: str, legal_area: Optional[str] = None, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        if legal_area:
            context['legal_area'] = legal_area
        super().__init__(f"Legal Team: {message}", context=context, cause=cause)

class ComplianceException(LegalException):
    """Compliance-related exceptions"""
    
    def __init__(self, regulation: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['regulation'] = regulation
        super().__init__(f"Compliance issue ({regulation}): {message}", legal_area='compliance', context=context, cause=cause)

class DocumentValidationException(LegalException):
    """Legal document validation failures"""
    
    def __init__(self, document_type: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['document_type'] = document_type
        super().__init__(f"Document validation ({document_type}): {message}", context=context, cause=cause)

# =============================================================================
# OPERATIONS MANAGER EXCEPTIONS
# =============================================================================

class OperationsException(BusinessLogicException):
    """Operations manager specific exceptions"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(f"Operations Manager: {message}", context=context, cause=cause)

class AgentException(OperationsException):
    """Agent-related exceptions"""
    
    def __init__(self, agent_id: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['agent_id'] = agent_id
        super().__init__(f"Agent {agent_id}: {message}", context=context, cause=cause)

class OptimizationException(OperationsException):
    """Optimization-related exceptions"""
    
    def __init__(self, optimization_type: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        context = context or {}
        context['optimization_type'] = optimization_type
        super().__init__(f"Optimization ({optimization_type}): {message}", context=context, cause=cause)

# =============================================================================
# ERROR HANDLING UTILITIES
# =============================================================================

class ErrorHandler:
    """Utility class for handling exceptions"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle exception and return structured error response"""
        if isinstance(exception, MFMException):
            error_dict = exception.to_dict()
        else:
            # Convert regular exception to MFMException
            mfm_exception = MFMException(str(exception), ErrorSeverity.MEDIUM, ErrorCategory.SYSTEM, context, exception)
            error_dict = mfm_exception.to_dict()
        
        return {
            'success': False,
            'error': error_dict,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def log_exception(exception: Exception, additional_context: Optional[Dict[str, Any]] = None):
        """Log exception with context"""
        if isinstance(exception, MFMException):
            # Already logged in __init__
            if additional_context:
                logger.info(f"Additional context: {additional_context}")
        else:
            logger.error(f"Unhandled exception: {str(exception)}", exc_info=exception)
            if additional_context:
                logger.info(f"Additional context: {additional_context}")
    
    @staticmethod
    def create_error_response(message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                           category: ErrorCategory = ErrorCategory.SYSTEM, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        exception = MFMException(message, severity, category, context)
        return ErrorHandler.handle_exception(exception, context)

# =============================================================================
# EXCEPTION DECORATORS
# =============================================================================

def handle_exceptions(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                     category: ErrorCategory = ErrorCategory.SYSTEM,
                     return_on_error: Any = None):
    """Decorator to handle exceptions in functions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, MFMException):
                    # Convert to MFMException
                    context = {
                        'function': func.__name__,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                    e = MFMException(str(e), severity, category, context, e)
                
                if return_on_error is not None:
                    return return_on_error
                
                # Re-raise the exception
                raise
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, MFMException):
                    # Convert to MFMException
                    context = {
                        'function': func.__name__,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                    e = MFMException(str(e), severity, category, context, e)
                
                if return_on_error is not None:
                    return return_on_error
                
                # Re-raise the exception
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0,
                      exceptions: tuple = (Exception,)):
    """Decorator to retry functions on exceptions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Max retries reached, raise the exception
                        if not isinstance(e, MFMException):
                            context = {
                                'function': func.__name__,
                                'attempt': attempt + 1,
                                'max_retries': max_retries
                            }
                            e = MFMException(f"Max retries ({max_retries}) exceeded: {str(e)}", 
                                          ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context, e)
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Max retries reached, raise the exception
                        if not isinstance(e, MFMException):
                            context = {
                                'function': func.__name__,
                                'attempt': attempt + 1,
                                'max_retries': max_retries
                            }
                            e = MFMException(f"Max retries ({max_retries}) exceeded: {str(e)}", 
                                          ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context, e)
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
