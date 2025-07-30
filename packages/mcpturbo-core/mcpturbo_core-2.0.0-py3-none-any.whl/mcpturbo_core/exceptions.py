class MCPError(Exception):
    """Base exception for MCP Protocol errors"""
    def __init__(self, message: str, error_code: str = "MCP_ERROR", details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class TimeoutError(MCPError):
    """Request timeout error"""
    def __init__(self, message: str, timeout: int = None):
        super().__init__(message, "TIMEOUT_ERROR", {"timeout": timeout})

class RateLimitError(MCPError):
    """Rate limit exceeded error"""
    def __init__(self, message: str, limit: int = None, reset_time: int = None):
        super().__init__(message, "RATE_LIMIT_ERROR", {
            "limit": limit,
            "reset_time": reset_time
        })

class CircuitBreakerError(MCPError):
    """Circuit breaker is open error"""
    def __init__(self, message: str, failure_count: int = None):
        super().__init__(message, "CIRCUIT_BREAKER_ERROR", {
            "failure_count": failure_count
        })

class AgentNotFoundError(MCPError):
    """Agent not found error"""
    def __init__(self, agent_id: str):
        super().__init__(f"Agent '{agent_id}' not found", "AGENT_NOT_FOUND", {
            "agent_id": agent_id
        })

class AuthenticationError(MCPError):
    """Authentication failed error"""
    def __init__(self, message: str, provider: str = None):
        super().__init__(message, "AUTHENTICATION_ERROR", {
            "provider": provider
        })

class ValidationError(MCPError):
    """Message validation error"""
    def __init__(self, message: str, field: str = None, value = None):
        super().__init__(message, "VALIDATION_ERROR", {
            "field": field,
            "value": value
        })

class APIError(MCPError):
    """External API error"""
    def __init__(self, message: str, status_code: int = None, provider: str = None):
        super().__init__(message, "API_ERROR", {
            "status_code": status_code,
            "provider": provider
        })

class ConfigurationError(MCPError):
    """Configuration error"""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, "CONFIGURATION_ERROR", {
            "config_key": config_key
        })

class SerializationError(MCPError):
    """Message serialization/deserialization error"""
    def __init__(self, message: str, data_type: str = None):
        super().__init__(message, "SERIALIZATION_ERROR", {
            "data_type": data_type
        })

# Utility functions for error handling

def handle_api_error(response_status: int, response_text: str, provider: str) -> APIError:
    """Create appropriate API error based on status code"""
    if response_status == 401:
        return AuthenticationError(f"Authentication failed: {response_text}", provider)
    elif response_status == 429:
        return RateLimitError(f"Rate limit exceeded: {response_text}")
    elif response_status >= 500:
        return APIError(f"Server error: {response_text}", response_status, provider)
    else:
        return APIError(f"API error: {response_text}", response_status, provider)

def wrap_async_error(func):
    """Decorator to wrap async functions and handle common errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out in {func.__name__}")
        except Exception as e:
            if isinstance(e, MCPError):
                raise
            raise MCPError(f"Unexpected error in {func.__name__}: {str(e)}")
    return wrapper