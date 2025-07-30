"""
APIProtector - A comprehensive API protection library for Python
Author: Kodukulla Phani Kumar
Email: phanikumark715@gmail.com
"""

import time
import hashlib
import hmac
import json
import re
import threading
from typing import Dict, List, Optional, Callable, Any, Union
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import logging

__version__ = "1.0.0"
__author__ = "Kodukulla Phani Kumar"
__email__ = "phanikumark715@gmail.com"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIProtectorError(Exception):
    """Base exception for APIProtector"""
    pass


class RateLimitExceeded(APIProtectorError):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationFailed(APIProtectorError):
    """Raised when authentication fails"""
    pass


class ValidationError(APIProtectorError):
    """Raised when request validation fails"""
    pass


class SecurityThreat(APIProtectorError):
    """Raised when security threat is detected"""
    pass


class RateLimiter:
    """Thread-safe rate limiter implementation"""
    
    def __init__(self):
        self.clients = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str, limit: int, window: int) -> bool:
        """Check if client is within rate limit"""
        with self.lock:
            now = time.time()
            # Clean old requests
            self.clients[client_id] = [
                req_time for req_time in self.clients[client_id]
                if now - req_time < window
            ]
            
            if len(self.clients[client_id]) >= limit:
                return False
            
            self.clients[client_id].append(now)
            return True
    
    def get_remaining_requests(self, client_id: str, limit: int, window: int) -> int:
        """Get remaining requests for client"""
        with self.lock:
            now = time.time()
            self.clients[client_id] = [
                req_time for req_time in self.clients[client_id]
                if now - req_time < window
            ]
            return max(0, limit - len(self.clients[client_id]))


class SecurityScanner:
    """Security threat detection"""
    
    def __init__(self):
        self.sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bexec\b.*\b)",
            r"(\bscript\b.*\>)",
            r"(\<.*\bscript\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        self.path_traversal_patterns = [
            r"\.\.[\\/]",
            r"[\\/]\.\.[\\/]",
            r"\.\.%2f",
            r"%2e%2e%2f",
        ]
    
    def scan_sql_injection(self, text: str) -> bool:
        """Detect SQL injection attempts"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) 
                  for pattern in self.sql_patterns)
    
    def scan_xss(self, text: str) -> bool:
        """Detect XSS attempts"""
        return any(re.search(pattern, text, re.IGNORECASE) 
                  for pattern in self.xss_patterns)
    
    def scan_path_traversal(self, text: str) -> bool:
        """Detect path traversal attempts"""
        return any(re.search(pattern, text, re.IGNORECASE) 
                  for pattern in self.path_traversal_patterns)
    
    def scan_all(self, data: Union[str, dict]) -> List[str]:
        """Scan for all security threats"""
        threats = []
        
        if isinstance(data, dict):
            text = json.dumps(data)
        else:
            text = str(data)
        
        if self.scan_sql_injection(text):
            threats.append("SQL Injection")
        
        if self.scan_xss(text):
            threats.append("XSS")
        
        if self.scan_path_traversal(text):
            threats.append("Path Traversal")
        
        return threats


class RequestValidator:
    """Request validation utilities"""
    
    @staticmethod
    def validate_json_schema(data: dict, schema: dict) -> bool:
        """Basic JSON schema validation"""
        try:
            for field, field_type in schema.items():
                if field not in data:
                    return False
                if not isinstance(data[field], field_type):
                    return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: List[str]) -> bool:
        """Validate required fields are present"""
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_field_length(data: dict, field_limits: Dict[str, int]) -> bool:
        """Validate field length limits"""
        for field, max_length in field_limits.items():
            if field in data and len(str(data[field])) > max_length:
                return False
        return True


class APIProtector:
    """Main API protection class"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rate_limiter = RateLimiter()
        self.security_scanner = SecurityScanner()
        self.request_validator = RequestValidator()
        
        # Default configuration
        self.default_rate_limit = self.config.get('rate_limit', 100)
        self.default_window = self.config.get('window', 3600)  # 1 hour
        self.enable_security_scan = self.config.get('enable_security_scan', True)
        self.enable_logging = self.config.get('enable_logging', True)
        self.api_keys = self.config.get('api_keys', {})
        self.jwt_secret = self.config.get('jwt_secret', 'default_secret_change_me')
        
        # Blocked IPs and user agents
        self.blocked_ips = set(self.config.get('blocked_ips', []))
        self.blocked_user_agents = set(self.config.get('blocked_user_agents', []))
        
        # Whitelist
        self.whitelisted_ips = set(self.config.get('whitelisted_ips', []))
    
    def get_client_id(self, request_data: dict) -> str:
        """Extract client identifier from request"""
        # Try to get IP from various headers
        ip = (request_data.get('remote_addr') or 
              request_data.get('x_forwarded_for', '').split(',')[0].strip() or
              request_data.get('x_real_ip') or
              'unknown')
        
        # Include user agent for more specific identification
        user_agent = request_data.get('user_agent', '')
        return f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        if not self.api_keys:
            return True  # No API keys configured, allow all
        
        return api_key in self.api_keys
    
    def validate_jwt_token(self, token: str) -> bool:
        """Basic JWT token validation"""
        try:
            # Simple JWT validation (in production, use a proper JWT library)
            parts = token.split('.')
            if len(parts) != 3:
                return False
            
            header, payload, signature = parts
            
            # Verify signature
            expected_signature = hmac.new(
                self.jwt_secret.encode(),
                f"{header}.{payload}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def is_blocked(self, request_data: dict) -> bool:
        """Check if request should be blocked"""
        ip = request_data.get('remote_addr', '')
        user_agent = request_data.get('user_agent', '')
        
        # Check IP whitelist first
        if ip in self.whitelisted_ips:
            return False
        
        # Check blocked IPs
        if ip in self.blocked_ips:
            return True
        
        # Check blocked user agents
        if any(blocked_ua in user_agent for blocked_ua in self.blocked_user_agents):
            return True
        
        return False
    
    def log_request(self, request_data: dict, status: str, message: str = ""):
        """Log request details"""
        if not self.enable_logging:
            return
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip': request_data.get('remote_addr', 'unknown'),
            'method': request_data.get('method', 'unknown'),
            'path': request_data.get('path', 'unknown'),
            'user_agent': request_data.get('user_agent', 'unknown'),
            'status': status,
            'message': message
        }
        
        logger.info(f"APIProtector: {json.dumps(log_entry)}")
    
    def protect(self, 
                rate_limit: Optional[int] = None,
                window: Optional[int] = None,
                require_auth: bool = False,
                auth_type: str = 'api_key',
                validate_schema: Optional[dict] = None,
                required_fields: Optional[List[str]] = None,
                field_limits: Optional[Dict[str, int]] = None,
                enable_security_scan: Optional[bool] = None):
        """
        Decorator for protecting API endpoints
        
        Args:
            rate_limit: Maximum requests per window
            window: Time window in seconds
            require_auth: Whether authentication is required
            auth_type: Type of authentication ('api_key' or 'jwt')
            validate_schema: JSON schema for validation
            required_fields: List of required fields
            field_limits: Dictionary of field length limits
            enable_security_scan: Whether to enable security scanning
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract request data from different framework formats
                request_data = self._extract_request_data(args, kwargs)
                
                try:
                    # Check if request is blocked
                    if self.is_blocked(request_data):
                        self.log_request(request_data, "BLOCKED", "IP or User Agent blocked")
                        raise SecurityThreat("Request blocked")
                    
                    # Rate limiting
                    client_id = self.get_client_id(request_data)
                    limit = rate_limit or self.default_rate_limit
                    win = window or self.default_window
                    
                    if not self.rate_limiter.is_allowed(client_id, limit, win):
                        self.log_request(request_data, "RATE_LIMITED")
                        raise RateLimitExceeded("Rate limit exceeded")
                    
                    # Authentication
                    if require_auth:
                        if auth_type == 'api_key':
                            api_key = request_data.get('api_key') or request_data.get('x_api_key')
                            if not api_key or not self.validate_api_key(api_key):
                                self.log_request(request_data, "AUTH_FAILED", "Invalid API key")
                                raise AuthenticationFailed("Invalid API key")
                        
                        elif auth_type == 'jwt':
                            auth_header = request_data.get('authorization', '')
                            if not auth_header.startswith('Bearer '):
                                self.log_request(request_data, "AUTH_FAILED", "Missing Bearer token")
                                raise AuthenticationFailed("Missing Bearer token")
                            
                            token = auth_header[7:]  # Remove 'Bearer ' prefix
                            if not self.validate_jwt_token(token):
                                self.log_request(request_data, "AUTH_FAILED", "Invalid JWT token")
                                raise AuthenticationFailed("Invalid JWT token")
                    
                    # Request validation
                    if hasattr(request_data, 'json') and request_data.json:
                        json_data = request_data.json
                        
                        # Schema validation
                        if validate_schema and not self.request_validator.validate_json_schema(json_data, validate_schema):
                            self.log_request(request_data, "VALIDATION_FAILED", "Schema validation failed")
                            raise ValidationError("Schema validation failed")
                        
                        # Required fields validation
                        if required_fields and not self.request_validator.validate_required_fields(json_data, required_fields):
                            self.log_request(request_data, "VALIDATION_FAILED", "Required fields missing")
                            raise ValidationError("Required fields missing")
                        
                        # Field length validation
                        if field_limits and not self.request_validator.validate_field_length(json_data, field_limits):
                            self.log_request(request_data, "VALIDATION_FAILED", "Field length limit exceeded")
                            raise ValidationError("Field length limit exceeded")
                    
                    # Security scanning
                    scan_enabled = enable_security_scan if enable_security_scan is not None else self.enable_security_scan
                    if scan_enabled:
                        scan_data = request_data.get('json', {})
                        scan_data.update(request_data.get('args', {}))
                        scan_data.update(request_data.get('form', {}))
                        
                        threats = self.security_scanner.scan_all(scan_data)
                        if threats:
                            self.log_request(request_data, "SECURITY_THREAT", f"Threats detected: {', '.join(threats)}")
                            raise SecurityThreat(f"Security threats detected: {', '.join(threats)}")
                    
                    # Log successful request
                    self.log_request(request_data, "ALLOWED")
                    
                    # Call the original function
                    return func(*args, **kwargs)
                
                except APIProtectorError:
                    raise
                except Exception as e:
                    self.log_request(request_data, "ERROR", str(e))
                    raise
            
            return wrapper
        return decorator
    
    def _extract_request_data(self, args, kwargs) -> dict:
        """Extract request data from different framework formats"""
        request_data = {}
        
        # Try to find request object in args
        for arg in args:
            if hasattr(arg, 'method') and hasattr(arg, 'path'):
                # Flask/FastAPI request-like object
                request_data = {
                    'method': getattr(arg, 'method', 'GET'),
                    'path': getattr(arg, 'path', '/'),
                    'remote_addr': getattr(arg, 'remote_addr', ''),
                    'user_agent': getattr(arg.headers, 'get', lambda x: '')('User-Agent') if hasattr(arg, 'headers') else '',
                    'api_key': getattr(arg.headers, 'get', lambda x: '')('X-API-Key') if hasattr(arg, 'headers') else '',
                    'x_api_key': getattr(arg.headers, 'get', lambda x: '')('X-API-Key') if hasattr(arg, 'headers') else '',
                    'authorization': getattr(arg.headers, 'get', lambda x: '')('Authorization') if hasattr(arg, 'headers') else '',
                    'x_forwarded_for': getattr(arg.headers, 'get', lambda x: '')('X-Forwarded-For') if hasattr(arg, 'headers') else '',
                    'x_real_ip': getattr(arg.headers, 'get', lambda x: '')('X-Real-IP') if hasattr(arg, 'headers') else '',
                    'json': getattr(arg, 'json', {}) if hasattr(arg, 'json') else {},
                    'args': getattr(arg, 'args', {}) if hasattr(arg, 'args') else {},
                    'form': getattr(arg, 'form', {}) if hasattr(arg, 'form') else {},
                }
                break
        
        # Fallback to kwargs if no request object found
        if not request_data:
            request_data = kwargs
        
        return request_data
    
    def middleware(self, app):
        """Middleware for frameworks like Flask"""
        def middleware_func(environ, start_response):
            # Basic middleware implementation
            return app(environ, start_response)
        
        return middleware_func
    
    def get_stats(self) -> dict:
        """Get protection statistics"""
        return {
            'active_clients': len(self.rate_limiter.clients),
            'total_requests': sum(len(reqs) for reqs in self.rate_limiter.clients.values()),
            'blocked_ips_count': len(self.blocked_ips),
            'whitelisted_ips_count': len(self.whitelisted_ips),
            'api_keys_count': len(self.api_keys),
        }
    
    def add_blocked_ip(self, ip: str):
        """Add IP to blocklist"""
        self.blocked_ips.add(ip)
    
    def remove_blocked_ip(self, ip: str):
        """Remove IP from blocklist"""
        self.blocked_ips.discard(ip)
    
    def add_whitelisted_ip(self, ip: str):
        """Add IP to whitelist"""
        self.whitelisted_ips.add(ip)
    
    def remove_whitelisted_ip(self, ip: str):
        """Remove IP from whitelist"""
        self.whitelisted_ips.discard(ip)


# Convenience functions for quick setup
def create_protector(config: Optional[Dict] = None) -> APIProtector:
    """Create an APIProtector instance"""
    return APIProtector(config)


def quick_protect(rate_limit: int = 100, window: int = 3600, require_auth: bool = False):
    """Quick protection decorator with minimal configuration"""
    protector = APIProtector()
    return protector.protect(rate_limit=rate_limit, window=window, require_auth=require_auth)


# Export main classes and functions
__all__ = [
    'APIProtector',
    'APIProtectorError',
    'RateLimitExceeded',
    'AuthenticationFailed',
    'ValidationError',
    'SecurityThreat',
    'RateLimiter',
    'SecurityScanner',
    'RequestValidator',
    'create_protector',
    'quick_protect',
]