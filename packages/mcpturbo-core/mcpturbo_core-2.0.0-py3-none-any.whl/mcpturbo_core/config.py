import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass
class AgentConfig:
    api_key: str = ""
    model: str = ""
    rate_limit: int = 50
    timeout: int = 30
    retry_attempts: int = 3
    failure_threshold: int = 5
    recovery_timeout: int = 60
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MCPConfig:
    # Protocol settings
    max_concurrent_requests: int = 10
    default_timeout: int = 30
    default_retry_attempts: int = 3
    queue_size: int = 1000
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    
    # API Keys from environment
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    claude_api_key: str = field(default_factory=lambda: os.getenv("CLAUDE_API_KEY", ""))
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    
    # Development settings
    debug: bool = field(default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("MCP_LOG_LEVEL", "INFO"))
    
    # Storage
    cache_dir: str = field(default_factory=lambda: os.getenv("MCP_CACHE_DIR", "~/.mcpturbo/cache"))
    config_dir: str = field(default_factory=lambda: os.getenv("MCP_CONFIG_DIR", "~/.mcpturbo"))
    
    def __post_init__(self):
        # Expand user paths
        self.cache_dir = str(Path(self.cache_dir).expanduser())
        self.config_dir = str(Path(self.config_dir).expanduser())
        
        # Create directories if they don't exist
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up default agent configurations
        self._setup_default_agents()
    
    def _setup_default_agents(self):
        """Setup default configurations for standard agents"""
        if "openai" not in self.agents and self.openai_api_key:
            self.agents["openai"] = AgentConfig(
                api_key=self.openai_api_key,
                model="gpt-4",
                rate_limit=60,
                timeout=60,
                custom_settings={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
        
        if "claude" not in self.agents and self.claude_api_key:
            self.agents["claude"] = AgentConfig(
                api_key=self.claude_api_key,
                model="claude-3-sonnet-20240229",
                rate_limit=50,
                timeout=90,
                custom_settings={
                    "max_tokens": 1000
                }
            )
        
        if "deepseek" not in self.agents and self.deepseek_api_key:
            self.agents["deepseek"] = AgentConfig(
                api_key=self.deepseek_api_key,
                model="deepseek-coder",
                rate_limit=100,
                timeout=45,
                custom_settings={
                    "temperature": 0.1
                }
            )
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent"""
        return self.agents.get(agent_id)
    
    def add_agent_config(self, agent_id: str, config: AgentConfig):
        """Add or update agent configuration"""
        self.agents[agent_id] = config
    
    def save_to_file(self, config_path: Optional[str] = None):
        """Save configuration to file"""
        if config_path is None:
            config_path = os.path.join(self.config_dir, "config.json")
        
        # Convert to serializable format
        config_dict = {
            "max_concurrent_requests": self.max_concurrent_requests,
            "default_timeout": self.default_timeout,
            "default_retry_attempts": self.default_retry_attempts,
            "queue_size": self.queue_size,
            "debug": self.debug,
            "log_level": self.log_level,
            "cache_dir": self.cache_dir,
            "config_dir": self.config_dir,
            "agents": {
                agent_id: {
                    "api_key": "***" if config.api_key else "",  # Don't save actual keys
                    "model": config.model,
                    "rate_limit": config.rate_limit,
                    "timeout": config.timeout,
                    "retry_attempts": config.retry_attempts,
                    "failure_threshold": config.failure_threshold,
                    "recovery_timeout": config.recovery_timeout,
                    "custom_settings": config.custom_settings
                }
                for agent_id, config in self.agents.items()
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> 'MCPConfig':
        """Load configuration from file"""
        if config_path is None:
            config_dir = os.path.expanduser(os.getenv("MCP_CONFIG_DIR", "~/.mcpturbo"))
            config_path = os.path.join(config_dir, "config.json")
        
        if not os.path.exists(config_path):
            return cls()  # Return default config
        
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        # Create agent configs
        agents = {}
        for agent_id, agent_data in config_dict.get("agents", {}).items():
            agents[agent_id] = AgentConfig(
                api_key="",  # Will be loaded from env
                model=agent_data.get("model", ""),
                rate_limit=agent_data.get("rate_limit", 50),
                timeout=agent_data.get("timeout", 30),
                retry_attempts=agent_data.get("retry_attempts", 3),
                failure_threshold=agent_data.get("failure_threshold", 5),
                recovery_timeout=agent_data.get("recovery_timeout", 60),
                custom_settings=agent_data.get("custom_settings", {})
            )
        
        return cls(
            max_concurrent_requests=config_dict.get("max_concurrent_requests", 10),
            default_timeout=config_dict.get("default_timeout", 30),
            default_retry_attempts=config_dict.get("default_retry_attempts", 3),
            queue_size=config_dict.get("queue_size", 1000),
            debug=config_dict.get("debug", False),
            log_level=config_dict.get("log_level", "INFO"),
            cache_dir=config_dict.get("cache_dir", "~/.mcpturbo/cache"),
            config_dir=config_dict.get("config_dir", "~/.mcpturbo"),
            agents=agents
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check for required API keys
        if not any([self.openai_api_key, self.claude_api_key, self.deepseek_api_key]):
            issues.append("No API keys configured. Set OPENAI_API_KEY, CLAUDE_API_KEY, or DEEPSEEK_API_KEY environment variables.")
        
        # Validate timeouts
        if self.default_timeout <= 0:
            issues.append("default_timeout must be positive")
        
        if self.max_concurrent_requests <= 0:
            issues.append("max_concurrent_requests must be positive")
        
        # Validate agent configs
        for agent_id, agent_config in self.agents.items():
            if agent_config.rate_limit <= 0:
                issues.append(f"Agent {agent_id}: rate_limit must be positive")
            
            if agent_config.timeout <= 0:
                issues.append(f"Agent {agent_id}: timeout must be positive")
        
        return issues

# Default configuration paths
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.mcpturbo")
DEFAULT_CACHE_DIR = os.path.expanduser("~/.mcpturbo/cache")
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "config.json")

# Global configuration instance
_config: Optional[MCPConfig] = None

def get_config() -> MCPConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = MCPConfig.load_from_file()
    return _config

def set_config(config: MCPConfig):
    """Set global configuration instance"""
    global _config
    _config = config

def load_config(config_path: Optional[str] = None) -> MCPConfig:
    """Load configuration from file and set as global"""
    config = MCPConfig.load_from_file(config_path)
    set_config(config)
    return config

def save_config(config_path: Optional[str] = None):
    """Save current global configuration to file"""
    config = get_config()
    config.save_to_file(config_path)

# Environment variable helpers
def get_env_bool(name: str, default: bool = False) -> bool:
    """Get boolean value from environment variable"""
    value = os.getenv(name, str(default)).lower()
    return value in ("true", "1", "yes", "on")

def get_env_int(name: str, default: int) -> int:
    """Get integer value from environment variable"""
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

# Configuration validation
def validate_environment() -> Dict[str, Any]:
    """Validate environment setup for MCPturbo"""
    validation_result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "api_keys_found": []
    }
    
    # Check API keys
    if os.getenv("OPENAI_API_KEY"):
        validation_result["api_keys_found"].append("OpenAI")
    
    if os.getenv("CLAUDE_API_KEY"):
        validation_result["api_keys_found"].append("Claude")
    
    if os.getenv("DEEPSEEK_API_KEY"):
        validation_result["api_keys_found"].append("DeepSeek")
    
    if not validation_result["api_keys_found"]:
        validation_result["valid"] = False
        validation_result["issues"].append(
            "No API keys found. Please set at least one of: OPENAI_API_KEY, CLAUDE_API_KEY, DEEPSEEK_API_KEY"
        )
    
    # Check config directory
    config_dir = Path(get_config().config_dir)
    if not config_dir.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            validation_result["warnings"].append(f"Created config directory: {config_dir}")
        except Exception as e:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Cannot create config directory: {e}")
    
    # Validate current config
    config_issues = get_config().validate()
    if config_issues:
        validation_result["valid"] = False
        validation_result["issues"].extend(config_issues)
    
    return validation_result