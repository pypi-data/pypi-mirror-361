# APIProtector 🛡️

A comprehensive and lightweight API protection library for Python that provides rate limiting, authentication, request validation, and security scanning capabilities. Works with any Python web framework including Flask, Django, FastAPI, and more.

## Features

- **Rate Limiting**: Configurable rate limiting with sliding window algorithm
- **Authentication**: Support for API keys and JWT tokens
- **Security Scanning**: Detects SQL injection, XSS, and path traversal attacks
- **Request Validation**: JSON schema validation and field validation
- **IP Blocking/Whitelisting**: Block malicious IPs and whitelist trusted ones
- **Framework Agnostic**: Works with Flask, Django, FastAPI, Pyramid, Tornado, and more
- **Thread-Safe**: Built for concurrent applications
- **Logging**: Comprehensive request logging and monitoring
- **Zero Dependencies**: Pure Python implementation with no external dependencies

## Installation

```bash
pip install apiprotector
```

## Quick Start

### Basic Usage

```python
from apiprotector import APIProtector

# Create protector instance
protector = APIProtector({
    'rate_limit': 100,  # 100 requests per hour
    'window': 3600,     # 1 hour window
    'api_keys': {'your-api-key': 'user1'},
    'enable_security_scan': True
})

# Use as decorator
@protector.protect(rate_limit=50, require_auth=True)
def your_api_endpoint():
    return {"message": "Protected endpoint"}
```

### Flask Integration

```python
from flask import Flask, request
from apiprotector import APIProtector

app = Flask(__name__)
protector = APIProtector({
    'rate_limit': 100,
    'api_keys': {'secret-key-123': 'user1'},
    'blocked_ips': ['192.168.1.100'],
    'whitelisted_ips': ['192.168.1.1']
})

@app.route('/api/data')
@protector.protect(rate_limit=50, require_auth=True, auth_type='api_key')
def get_data():
    return {"data": "This is protected data"}

@app.route('/api/users', methods=['POST'])
@protector.protect(
    rate_limit=20,
    require_auth=True,
    validate_schema={'name': str, 'email': str},
    required_fields=['name', 'email'],
    field_limits={'name': 50, 'email': 100}
)
def create_user():
    return {"message": "User created"}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request
from apiprotector import APIProtector

app = FastAPI()
protector = APIProtector({
    'rate_limit': 100,
    'jwt_secret': 'your-jwt-secret-key',
    'enable_security_scan': True
})

@app.get("/api/protected")
@protector.protect(rate_limit=30, require_auth=True, auth_type='jwt')
async def protected_endpoint(request: Request):
    return {"message": "JWT Protected endpoint"}

@app.post("/api/validate")
@protector.protect(
    rate_limit=10,
    validate_schema={'username': str, 'password': str},
    required_fields=['username', 'password'],
    enable_security_scan=True
)
async def validate_data(request: Request):
    return {"message": "Data validated"}
```

### Django Integration

```python
from django.http import JsonResponse
from apiprotector import APIProtector

protector = APIProtector({
    'rate_limit': 100,
    'api_keys': {'django-api-key': 'user1'}
})

@protector.protect(rate_limit=25, require_auth=True)
def django_api_view(request):
    return JsonResponse({"message": "Django protected view"})
```

## Configuration Options

```python
config = {
    # Rate limiting
    'rate_limit': 100,          # Default requests per window
    'window': 3600,             # Time window in seconds
    
    # Authentication
    'api_keys': {               # API key to user mapping
        'key1': 'user1',
        'key2': 'user2'
    },
    'jwt_secret': 'secret',     # JWT secret key
    
    # Security
    'enable_security_scan': True,
    'blocked_ips': ['1.2.3.4'],
    'whitelisted_ips': ['192.168.1.1'],
    'blocked_user_agents': ['BadBot/1.0'],
    
    # Logging
    'enable_logging': True,
}

protector = APIProtector(config)
```

## Decorator Parameters

```python
@protector.protect(
    rate_limit=50,                    # Override default rate limit
    window=1800,                      # Override default window (30 min)
    require_auth=True,                # Require authentication
    auth_type='api_key',              # 'api_key' or 'jwt'
    validate_schema={                 # JSON schema validation
        'name': str,
        'age': int
    },
    required_fields=['name'],         # Required fields list
    field_limits={                    # Field length limits
        'name': 100,
        'description': 500
    },
    enable_security_scan=True         # Enable security scanning
)
def your_endpoint():
    pass
```

## Security Features

### SQL Injection Detection
```python
# These patterns are automatically detected:
# - UNION SELECT statements
# - INSERT INTO statements
# - DELETE FROM statements
# - DROP TABLE statements
# - EXEC statements
```

### XSS Protection
```python
# Detects various XSS patterns:
# - <script> tags
# - javascript: URLs
# - Event handlers (onclick, onload, etc.)
# - iframe, object, embed tags
```

### Path Traversal Protection
```python
# Detects directory traversal attempts:
# - ../../../etc/passwd
# - ..%2f..%2f..%2fetc%2fpasswd
# - Various encoding variations
```

## Authentication Methods

### API Key Authentication
```python
# Request headers:
# X-API-Key: your-api-key
# or
# Authorization: Bearer your-api-key

@protector.protect(require_auth=True, auth_type='api_key')
def protected_endpoint():
    pass
```

### JWT Authentication
```python
# Request headers:
# Authorization: Bearer jwt-token-here

@protector.protect(require_auth=True, auth_type='jwt')
def jwt_protected_endpoint():
    pass
```

## Management Methods

```python
# Get protection statistics
stats = protector.get_stats()
print(stats)

# Manage blocked IPs
protector.add_blocked_ip('192.168.1.100')
protector.remove_blocked_ip('192.168.1.100')

# Manage whitelisted IPs
protector.add_whitelisted_ip('192.168.1.1')
protector.remove_whitelisted_ip('192.168.1.1')
```

## Error Handling

```python
from apiprotector import (
    APIProtectorError,
    RateLimitExceeded,
    AuthenticationFailed,
    ValidationError,
    SecurityThreat
)

try:
    # Your protected endpoint
    pass
except RateLimitExceeded:
    return {"error": "Rate limit exceeded"}, 429
except AuthenticationFailed:
    return {"error": "Authentication failed"}, 401
except ValidationError:
    return {"error": "Validation failed"}, 400
except SecurityThreat:
    return {"error": "Security threat detected"}, 403
except APIProtectorError:
    return {"error": "API protection error"}, 500
```

## Quick Protection Helper

For simple use cases, use the quick protection helper:

```python
from apiprotector import quick_protect

@quick_protect(rate_limit=50, window=3600, require_auth=True)
def simple_endpoint():
    return {"message": "Simply protected"}
```

## Logging

APIProtector provides comprehensive logging of all requests:

```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "ip": "192.168.1.100",
    "method": "POST",
    "path": "/api/users",
    "user_agent": "Mozilla/5.0...",
    "status": "ALLOWED",
    "message": ""
}
```

Log statuses:
- `ALLOWED`: Request passed all checks
- `BLOCKED`: Request blocked (IP/User-Agent)
- `RATE_LIMITED`: Rate limit exceeded
- `AUTH_FAILED`: Authentication failed
- `VALIDATION_FAILED`: Request validation failed
- `SECURITY_THREAT`: Security threat detected
- `ERROR`: Internal error occurred

## Advanced Usage

### Custom Security Scanning

```python
from apiprotector import SecurityScanner

scanner = SecurityScanner()

# Check for specific threats
data = {"query": "SELECT * FROM users WHERE id = 1"}
threats = scanner.scan_all(data)
if threats:
    print(f"Threats detected: {threats}")
```

### Custom Rate Limiting

```python
from apiprotector import RateLimiter

limiter = RateLimiter()

# Check if client is within limits
if limiter.is_allowed("client_id", limit=10, window=60):
    print("Request allowed")
else:
    print("Rate limit exceeded")

# Get remaining requests
remaining = limiter.get_remaining_requests("client_id", limit=10, window=60)
print(f"Remaining requests: {remaining}")
```

### Framework-Specific Examples

#### Tornado

```python
import tornado.web
from apiprotector import APIProtector

protector = APIProtector({'rate_limit': 100})

class MainHandler(tornado.web.RequestHandler):
    @protector.protect(rate_limit=20)
    def get(self):
        self.write({"message": "Tornado protected"})

app = tornado.web.Application([
    (r"/", MainHandler),
])
```

#### Pyramid

```python
from pyramid.config import Configurator
from pyramid.response import Response
from apiprotector import APIProtector

protector = APIProtector({'rate_limit': 100})

@protector.protect(rate_limit=30)
def hello_world(request):
    return Response('Pyramid protected!')

config = Configurator()
config.add_route('hello', '/')
config.add_view(hello_world, route_name='hello')
```

## Best Practices

1. **Use Environment Variables**: Store API keys and JWT secrets in environment variables
2. **Configure Appropriate Limits**: Set rate limits based on your API capacity
3. **Enable Security Scanning**: Always enable security scanning for public APIs
4. **Monitor Logs**: Regularly monitor protection logs for suspicious activity
5. **Update IP Lists**: Keep blocked and whitelisted IP lists updated
6. **Use HTTPS**: Always use HTTPS in production
7. **Validate All Input**: Use schema validation for all user inputs

## Performance Considerations

- **Thread-Safe**: All operations are thread-safe
- **Memory Usage**: Rate limiting data is stored in memory
- **Cleanup**: Old rate limit data is automatically cleaned up
- **Scalability**: For high-traffic applications, consider using Redis for rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/phanikumar715/apiprotector/issues)
- Email: phanikumark715@gmail.com

## Changelog

### Version 1.0.0
- Initial release
- Rate limiting with sliding window
- API key and JWT authentication
- Security scanning (SQL injection, XSS, path traversal)
- Request validation
- IP blocking/whitelisting
- Framework-agnostic design
- Comprehensive logging

## Examples Repository

For more examples and use cases, check out the [examples repository](https://github.com/phanikumar715/apiprotector-examples).

---

Made with ❤️ by Kodukulla Phani Kumar