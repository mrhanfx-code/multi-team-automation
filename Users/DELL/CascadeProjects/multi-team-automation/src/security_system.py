#!/usr/bin/env python3
"""
MFM Corporation - Security and Authentication System
Comprehensive security, authentication, and authorization system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets
import jwt
from passlib.context import CryptContext
import bcrypt

logger = logging.getLogger(__name__)

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission(Enum):
    # System permissions
    SYSTEM_ADMIN = "system_admin"
    SYSTEM_CONFIGURE = "system_configure"
    SYSTEM_MONITOR = "system_monitor"
    
    # Team permissions
    TEAM_MANAGE = "team_manage"
    TEAM_VIEW = "team_view"
    TEAM_EXECUTE = "team_execute"
    
    # Workflow permissions
    WORKFLOW_CREATE = "workflow_create"
    WORKFLOW_EXECUTE = "workflow_execute"
    WORKFLOW_MANAGE = "workflow_manage"
    
    # Reporting permissions
    REPORTING_VIEW = "reporting_view"
    REPORTING_CREATE = "reporting_create"
    REPORTING_EXPORT = "reporting_export"
    
    # Meeting permissions
    MEETING_CREATE = "meeting_create"
    MEETING_MANAGE = "meeting_manage"
    MEETING_VIEW = "meeting_view"

class AuthMethod(Enum):
    PASSWORD = "password"
    JWT = "jwt"
    OAUTH = "oauth"
    API_KEY = "api_key"
    SSO = "sso"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class User:
    """User data structure"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    failed_login_attempts: int
    locked_until: Optional[datetime]
    password_hash: str
    mfa_enabled: bool
    mfa_secret: Optional[str]
    api_keys: List[str]

@dataclass
class Session:
    """Session data structure"""
    id: str
    user_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    ip_address: str
    user_agent: str
    is_active: bool

@dataclass
class SecurityEvent:
    """Security event data structure"""
    id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    timestamp: datetime
    description: str
    severity: SecurityLevel
    resolved: bool
    metadata: Dict[str, Any]

@dataclass
class SecurityPolicy:
    """Security policy data structure"""
    id: str
    name: str
    description: str
    rules: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

class SecuritySystem:
    """Comprehensive security and authentication system"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.users = {}
        self.sessions = {}
        self.security_events = []
        self.security_policies = {}
        self.api_keys = {}
        
        # Password hashing
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            default="bcrypt",
            bcrypt__rounds=12
        )
        
        # JWT configuration
        self.jwt_secret = secrets.token_urlsafe(32)
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = timedelta(hours=24)
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=8)
        
    async def initialize(self) -> bool:
        """Initialize the security system"""
        logger.info("🔐 Initializing MFM Corporation Security System")
        
        try:
            # Load security policies
            await self._load_security_policies()
            
            # Set up default policies
            await self._setup_default_policies()
            
            # Create default admin user
            await self._create_default_admin()
            
            # Start security monitoring
            await self._start_security_monitoring()
            
            logger.info("✅ Security System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Security System initialization failed: {e}")
            return False
    
    async def create_user(self, username: str, email: str, full_name: str,
                         password: str, role: UserRole,
                         permissions: Optional[List[Permission]] = None) -> str:
        """Create a new user"""
        try:
            # Check if user already exists
            if any(user.username == username or user.email == email 
                   for user in self.users.values()):
                logger.error(f"User with username {username} or email {email} already exists")
                return ""
            
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.users)}"
            
            # Hash password
            password_hash = self.pwd_context.hash(password)
            
            # Set default permissions based on role
            if permissions is None:
                permissions = self._get_default_permissions(role)
            
            # Create user
            user = User(
                id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                permissions=permissions,
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
                last_login=None,
                failed_login_attempts=0,
                locked_until=None,
                password_hash=password_hash,
                mfa_enabled=False,
                mfa_secret=None,
                api_keys=[]
            )
            
            self.users[user_id] = user
            
            # Save to Supabase
            await self.supabase_manager.save_user(asdict(user))
            
            # Log security event
            await self._log_security_event(
                "user_created",
                user_id,
                "system",
                f"User {username} created with role {role.value}",
                SecurityLevel.LOW
            )
            
            logger.info(f"✅ User created: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return ""
    
    async def authenticate_user(self, username: str, password: str,
                             ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                await self._log_security_event(
                    "login_failed",
                    None,
                    ip_address,
                    f"Login attempt for non-existent user: {username}",
                    SecurityLevel.MEDIUM
                )
                return None
            
            # Check if user is locked
            if user.locked_until and user.locked_until > datetime.now():
                await self._log_security_event(
                    "login_blocked",
                    user.id,
                    ip_address,
                    f"Login attempt for locked user: {username}",
                    SecurityLevel.HIGH
                )
                return None
            
            # Check if user is active
            if not user.is_active:
                await self._log_security_event(
                    "login_failed",
                    user.id,
                    ip_address,
                    f"Login attempt for inactive user: {username}",
                    SecurityLevel.MEDIUM
                )
                return None
            
            # Verify password
            if not self.pwd_context.verify(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Check if user should be locked
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now() + self.lockout_duration
                    
                    await self._log_security_event(
                        "user_locked",
                        user.id,
                        ip_address,
                        f"User {username} locked due to failed attempts",
                        SecurityLevel.HIGH
                    )
                else:
                    await self._log_security_event(
                        "login_failed",
                        user.id,
                        ip_address,
                        f"Failed login attempt for user: {username}",
                        SecurityLevel.MEDIUM
                    )
                
                return None
            
            # Successful authentication
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            # Create session
            session_id = await self._create_session(user.id, ip_address, user_agent)
            
            # Generate JWT token
            token = self._generate_jwt_token(user)
            
            # Log successful login
            await self._log_security_event(
                "login_success",
                user.id,
                ip_address,
                f"User {username} logged in successfully",
                SecurityLevel.LOW
            )
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "token": token,
                "session_id": session_id,
                "expires_at": (datetime.now() + self.jwt_expiration).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            user_id = payload.get("user_id")
            if not user_id or user_id not in self.users:
                return None
            
            user = self.users[user_id]
            
            # Check if user is still active
            if not user.is_active:
                return None
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions]
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            
            # Super admin has all permissions
            if user.role == UserRole.SUPER_ADMIN:
                return True
            
            # Check specific permission
            return permission in user.permissions
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def create_api_key(self, user_id: str, name: str, 
                           expires_in: Optional[timedelta] = None) -> str:
        """Create API key for user"""
        try:
            if user_id not in self.users:
                logger.error(f"User {user_id} not found")
                return ""
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Store API key
            api_key_data = {
                "id": f"apikey_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "name": name,
                "key_hash": api_key_hash,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + (expires_in or timedelta(days=365)),
                "last_used": None,
                "is_active": True
            }
            
            self.api_keys[api_key_hash] = api_key_data
            
            # Add to user's API keys
            self.users[user_id].api_keys.append(api_key_hash)
            
            # Log security event
            await self._log_security_event(
                "api_key_created",
                user_id,
                "system",
                f"API key '{name}' created for user",
                SecurityLevel.MEDIUM
            )
            
            logger.info(f"✅ API key created for user {user_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Failed to create API key: {e}")
            return ""
    
    async def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key"""
        try:
            # Hash the provided key
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check if API key exists
            if api_key_hash not in self.api_keys:
                return None
            
            key_data = self.api_keys[api_key_hash]
            
            # Check if key is active
            if not key_data["is_active"]:
                return None
            
            # Check if key has expired
            if key_data["expires_at"] and key_data["expires_at"] < datetime.now():
                return None
            
            # Get user
            user_id = key_data["user_id"]
            if user_id not in self.users:
                return None
            
            user = self.users[user_id]
            
            # Update last used
            key_data["last_used"] = datetime.now()
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "key_name": key_data["name"]
            }
            
        except Exception as e:
            logger.error(f"API key verification failed: {e}")
            return None
    
    async def revoke_api_key(self, user_id: str, api_key_hash: str) -> bool:
        """Revoke API key"""
        try:
            if api_key_hash not in self.api_keys:
                return False
            
            key_data = self.api_keys[api_key_hash]
            
            # Check ownership
            if key_data["user_id"] != user_id:
                return False
            
            # Deactivate key
            key_data["is_active"] = False
            
            # Remove from user's API keys
            if user_id in self.users:
                self.users[user_id].api_keys = [
                    k for k in self.users[user_id].api_keys if k != api_key_hash
                ]
            
            # Log security event
            await self._log_security_event(
                "api_key_revoked",
                user_id,
                "system",
                f"API key '{key_data['name']}' revoked",
                SecurityLevel.MEDIUM
            )
            
            logger.info(f"✅ API key revoked for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to revoke API key: {e}")
            return False
    
    async def logout_user(self, session_id: str) -> bool:
        """Logout user"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            user_id = session.user_id
            
            # Remove session
            del self.sessions[session_id]
            
            # Log security event
            await self._log_security_event(
                "logout",
                user_id,
                session.ip_address,
                f"User logged out from session {session_id}",
                SecurityLevel.LOW
            )
            
            logger.info(f"✅ User logged out: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to logout user: {e}")
            return False
    
    async def change_password(self, user_id: str, old_password: str, 
                            new_password: str) -> bool:
        """Change user password"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            
            # Verify old password
            if not self.pwd_context.verify(old_password, user.password_hash):
                await self._log_security_event(
                    "password_change_failed",
                    user_id,
                    "system",
                    "Failed password change attempt - invalid old password",
                    SecurityLevel.MEDIUM
                )
                return False
            
            # Hash new password
            new_password_hash = self.pwd_context.hash(new_password)
            user.password_hash = new_password_hash
            
            # Log security event
            await self._log_security_event(
                "password_changed",
                user_id,
                "system",
                "User password changed successfully",
                SecurityLevel.LOW
            )
            
            logger.info(f"✅ Password changed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to change password: {e}")
            return False
    
    async def get_security_events(self, user_id: Optional[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 severity: Optional[SecurityLevel] = None) -> List[Dict[str, Any]]:
        """Get security events"""
        try:
            events = self.security_events
            
            # Apply filters
            if user_id:
                events = [e for e in events if e.user_id == user_id]
            
            if start_date:
                events = [e for e in events if e.timestamp >= start_date]
            
            if end_date:
                events = [e for e in events if e.timestamp <= end_date]
            
            if severity:
                events = [e for e in events if e.severity == severity]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return [asdict(e) for e in events]
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        try:
            if user_id not in self.users:
                return []
            
            user = self.users[user_id]
            return [permission.value for permission in user.permissions]
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    async def update_user_role(self, user_id: str, new_role: UserRole,
                            admin_user_id: str) -> bool:
        """Update user role"""
        try:
            if user_id not in self.users or admin_user_id not in self.users:
                return False
            
            # Check if admin has permission
            admin_user = self.users[admin_user_id]
            if not await self.check_permission(admin_user_id, Permission.TEAM_MANAGE):
                return False
            
            user = self.users[user_id]
            old_role = user.role
            user.role = new_role
            user.permissions = self._get_default_permissions(new_role)
            
            # Log security event
            await self._log_security_event(
                "role_changed",
                user_id,
                "system",
                f"User role changed from {old_role.value} to {new_role.value}",
                SecurityLevel.MEDIUM
            )
            
            logger.info(f"✅ User role updated: {user_id} -> {new_role.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update user role: {e}")
            return False
    
    def _get_default_permissions(self, role: UserRole) -> List[Permission]:
        """Get default permissions for role"""
        permission_map = {
            UserRole.SUPER_ADMIN: list(Permission),
            UserRole.ADMIN: [
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_CONFIGURE,
                Permission.SYSTEM_MONITOR,
                Permission.TEAM_MANAGE,
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_MANAGE,
                Permission.REPORTING_CREATE,
                Permission.REPORTING_EXPORT,
                Permission.MEETING_MANAGE
            ],
            UserRole.MANAGER: [
                Permission.TEAM_MANAGE,
                Permission.TEAM_VIEW,
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_EXECUTE,
                Permission.REPORTING_VIEW,
                Permission.REPORTING_CREATE,
                Permission.MEETING_CREATE,
                Permission.MEETING_MANAGE
            ],
            UserRole.TEAM_LEAD: [
                Permission.TEAM_VIEW,
                Permission.TEAM_EXECUTE,
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_EXECUTE,
                Permission.REPORTING_VIEW,
                Permission.MEETING_CREATE
            ],
            UserRole.DEVELOPER: [
                Permission.TEAM_VIEW,
                Permission.WORKFLOW_EXECUTE,
                Permission.REPORTING_VIEW
            ],
            UserRole.ANALYST: [
                Permission.TEAM_VIEW,
                Permission.REPORTING_VIEW,
                Permission.REPORTING_CREATE
            ],
            UserRole.VIEWER: [
                Permission.TEAM_VIEW,
                Permission.REPORTING_VIEW
            ],
            UserRole.GUEST: [
                Permission.TEAM_VIEW
            ]
        }
        
        return permission_map.get(role, [])
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "iat": datetime.now(),
            "exp": datetime.now() + self.jwt_expiration
        }
        
        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )
    
    async def _create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create user session"""
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.sessions)}"
            
            session = Session(
                id=session_id,
                user_id=user_id,
                token=secrets.token_urlsafe(32),
                created_at=datetime.now(),
                expires_at=datetime.now() + self.session_timeout,
                last_accessed=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True
            )
            
            self.sessions[session_id] = session
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return ""
    
    async def _log_security_event(self, event_type: str, user_id: Optional[str],
                                 ip_address: str, description: str,
                                 severity: SecurityLevel):
        """Log security event"""
        try:
            event = SecurityEvent(
                id=f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.security_events)}",
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=datetime.now(),
                description=description,
                severity=severity,
                resolved=False,
                metadata={}
            )
            
            self.security_events.append(event)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def _load_security_policies(self):
        """Load security policies from Supabase"""
        try:
            # Simulate loading policies
            self.security_policies = {}
            logger.info("📋 Security policies loaded")
        except Exception as e:
            logger.error(f"Failed to load security policies: {e}")
    
    async def _setup_default_policies(self):
        """Set up default security policies"""
        try:
            # Password policy
            password_policy = SecurityPolicy(
                id="password_policy",
                name="Password Policy",
                description="Password complexity and expiration requirements",
                rules={
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90,
                    "history_count": 5
                },
                enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Session policy
            session_policy = SecurityPolicy(
                id="session_policy",
                name="Session Policy",
                description="Session timeout and security requirements",
                rules={
                    "timeout_hours": 8,
                    "max_concurrent_sessions": 3,
                    "require_ip_validation": True,
                    "require_user_agent_validation": True
                },
                enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # API key policy
            api_key_policy = SecurityPolicy(
                id="api_key_policy",
                name="API Key Policy",
                description="API key generation and management requirements",
                rules={
                    "key_length": 32,
                    "max_keys_per_user": 5,
                    "default_expiration_days": 365,
                    "require_rotation": True,
                    "rotation_days": 90
                },
                enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.security_policies = {
                "password_policy": password_policy,
                "session_policy": session_policy,
                "api_key_policy": api_key_policy
            }
            
            logger.info("📋 Default security policies created")
        except Exception as e:
            logger.error(f"Failed to setup default policies: {e}")
    
    async def _create_default_admin(self):
        """Create default admin user"""
        try:
            # Check if admin already exists
            if any(user.role == UserRole.SUPER_ADMIN for user in self.users.values()):
                logger.info("👤 Super admin user already exists")
                return
            
            # Create default admin
            admin_id = await self.create_user(
                username="admin",
                email="admin@mfmcorporation.com",
                full_name="System Administrator",
                password="MFM@Admin2024!",
                role=UserRole.SUPER_ADMIN
            )
            
            if admin_id:
                # Verify admin user
                self.users[admin_id].is_verified = True
                logger.info("👤 Default super admin user created")
            
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")
    
    async def _start_security_monitoring(self):
        """Start security monitoring"""
        try:
            # Start background task for security monitoring
            asyncio.create_task(self._security_monitoring_loop())
            logger.info("🔒 Security monitoring started")
        except Exception as e:
            logger.error(f"Failed to start security monitoring: {e}")
    
    async def _security_monitoring_loop(self):
        """Security monitoring loop"""
        while True:
            try:
                # Clean up expired sessions
                await self._cleanup_expired_sessions()
                
                # Clean up expired API keys
                await self._cleanup_expired_api_keys()
                
                # Check for security anomalies
                await self._check_security_anomalies()
                
                # Wait for next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Security monitoring loop error: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if session.expires_at <= current_time or not session.is_active
            ]
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            if expired_sessions:
                logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    async def _cleanup_expired_api_keys(self):
        """Clean up expired API keys"""
        try:
            current_time = datetime.now()
            expired_keys = [
                key_hash for key_hash, key_data in self.api_keys.items()
                if key_data["expires_at"] and key_data["expires_at"] <= current_time
            ]
            
            for key_hash in expired_keys:
                del self.api_keys[key_hash]
                
                # Remove from users
                for user in self.users.values():
                    user.api_keys = [k for k in user.api_keys if k != key_hash]
            
            if expired_keys:
                logger.info(f"🧹 Cleaned up {len(expired_keys)} expired API keys")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired API keys: {e}")
    
    async def _check_security_anomalies(self):
        """Check for security anomalies"""
        try:
            # Check for multiple failed logins
            recent_events = [
                e for e in self.security_events
                if e.event_type == "login_failed" and 
                e.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            # Group by IP address
            ip_failures = {}
            for event in recent_events:
                ip = event.ip_address
                ip_failures[ip] = ip_failures.get(ip, 0) + 1
            
            # Alert on suspicious IPs
            for ip, count in ip_failures.items():
                if count >= 10:
                    await self._log_security_event(
                        "suspicious_activity",
                        None,
                        ip,
                        f"Suspicious activity detected: {count} failed login attempts from IP {ip}",
                        SecurityLevel.HIGH
                    )
            
        except Exception as e:
            logger.error(f"Failed to check security anomalies: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security system status"""
        try:
            return {
                "total_users": len(self.users),
                "active_users": len([u for u in self.users.values() if u.is_active]),
                "total_sessions": len(self.sessions),
                "active_sessions": len([s for s in self.sessions.values() if s.is_active]),
                "total_api_keys": len(self.api_keys),
                "active_api_keys": len([k for k in self.api_keys.values() if k["is_active"]]),
                "security_events": len(self.security_events),
                "unresolved_events": len([e for e in self.security_events if not e.resolved]),
                "security_policies": len(self.security_policies),
                "enabled_policies": len([p for p in self.security_policies.values() if p.enabled])
            }
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {}
