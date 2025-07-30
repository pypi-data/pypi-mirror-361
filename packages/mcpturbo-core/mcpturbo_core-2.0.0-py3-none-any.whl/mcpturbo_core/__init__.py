"""
MCPturbo Core - Multi-agent Communication Protocol v2

Core components for intelligent agent orchestration with external AI services.
"""

__version__ = "2.0.0"
__author__ = "Federico Monfasani"

# Core protocol and configuration
from .protocol import MCPProtocol, protocol
from .config import MCPConfig, get_config, load_config, save_config, validate_environment
from .exceptions import (
    MCPError, TimeoutError, RateLimitError, CircuitBreakerError,
    AgentNotFoundError, AuthenticationError, ValidationError, APIError,
    ConfigurationError, SerializationError
)

# Message types
from .messages import (
    Message, Request, Response, Event, AIRequest, AIResponse,
    MessageType, Priority,
    create_request, create_ai_request, create_response, create_event
)

# Main exports
__all__ = [
    # Core classes
    "MCPProtocol",
    "MCPConfig", 
    
    # Global instances
    "protocol",
    
    # Configuration functions
    "get_config",
    "load_config", 
    "save_config",
    "validate_environment",
    
    # Message types
    "Message",
    "Request",
    "Response", 
    "Event",
    "AIRequest",
    "AIResponse",
    "MessageType",
    "Priority",
    
    # Message factories
    "create_request",
    "create_ai_request",
    "create_response",
    "create_event",
    
    # Exceptions
    "MCPError",
    "TimeoutError",
    "RateLimitError", 
    "CircuitBreakerError",
    "AgentNotFoundError",
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "ConfigurationError",
    "SerializationError",
    
    # Metadata
    "__version__",
    "__author__"
]

# Initialize global protocol
async def initialize():
    """Initialize MCPturbo core components"""
    await protocol.start()

async def cleanup():
    """Cleanup MCPturbo core components"""
    await protocol.stop()

# Quick setup function
def quick_setup(openai_key: str = None, claude_key: str = None, deepseek_key: str = None) -> MCPConfig:
    """
    Quick setup for MCPturbo with API keys
    
    Args:
        openai_key: OpenAI API key
        claude_key: Claude API key  
        deepseek_key: DeepSeek API key
        
    Returns:
        Configured MCPConfig instance
    """
    import os
    
    # Set environment variables if provided
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if claude_key:
        os.environ["CLAUDE_API_KEY"] = claude_key
    if deepseek_key:
        os.environ["DEEPSEEK_API_KEY"] = deepseek_key
    
    # Load configuration
    config = load_config()
    
    # Validate setup
    validation = validate_environment()
    if not validation["valid"]:
        raise MCPError(f"Setup validation failed: {validation['issues']}")
    
    return config