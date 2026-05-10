"""
Multi-Team Automation System

A comprehensive automation system that manages hierarchical team workflows:
Research → Planning → Development → Management → General Manager → User
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import error recovery system components
from .error_recovery_system import (
    ErrorRecoveryManager,
    ResearchTeamIntervention,
    ErrorSeverity,
    ErrorRecord,
)

__all__ = [
    "ErrorRecoveryManager",
    "ResearchTeamIntervention", 
    "ErrorSeverity",
    "ErrorRecord",
]
