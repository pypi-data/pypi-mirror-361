"""
Configuration management for AgentSentinel.

This module handles loading, validation, and management of configuration
from YAML files, environment variables, and programmatic settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

from .constants import DEFAULT_CONFIG, SeverityLevel, ThreatType
from .exceptions import ConfigurationError


@dataclass
class ServiceConfig:
    """Configuration for AgentSentinel service."""
    
    # Core SDK - no external API dependencies
    # AI-powered analysis handled externally
    
    def is_fully_configured(self) -> bool:
        """Core SDK is always fully configured."""
        return True
    
    def get_missing_apis(self) -> list[str]:
        """No APIs required for core SDK."""
        return []


@dataclass
class DetectionConfig:
    """Configuration for threat detection rules."""
    
    enabled: bool = True
    confidence_threshold: float = 0.7
    rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Clamp confidence threshold to valid range instead of raising error
        if self.confidence_threshold < 0.0:
            self.confidence_threshold = 0.0
        elif self.confidence_threshold > 1.0:
            self.confidence_threshold = 1.0


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/agent_sentinel.log"
    max_size: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 5
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level: {self.level}. Must be one of {valid_levels}",
                config_key="logging.level"
            )
        
        valid_formats = ["json", "text"]
        if self.format not in valid_formats:
            raise ConfigurationError(
                f"Invalid log format: {self.format}. Must be one of {valid_formats}",
                config_key="logging.format"
            )


@dataclass
class WeaveConfig:
    """Configuration for Weave LLM tracing and monitoring (development only)."""
    
    enabled: bool = False
    project_name: str = "agent-sentinel"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    # Tracing configuration
    trace_llm_calls: bool = True
    trace_intelligence_ops: bool = True
    trace_report_generation: bool = True
    
    # Security and Privacy Controls
    redact_pii: bool = True
    redact_api_keys: bool = True
    redact_user_data: bool = True
    allowed_domains: Optional[list] = None
    disable_code_capture: bool = True
    disable_system_info: bool = True
    max_payload_size: int = 1024 * 1024  # 1MB limit
    
    # Performance configuration
    max_trace_size: int = 10 * 1024 * 1024  # 10MB
    trace_timeout: float = 30.0
    batch_size: int = 100
    flush_interval: float = 5.0
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Sampling configuration
    sampling_rate: float = 1.0  # 100% sampling by default
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Auto-enable only in development mode
        dev_mode = os.getenv('AGENT_SENTINEL_DEV_MODE', '').lower() == 'true'
        if dev_mode and os.getenv('WEAVE_API_KEY'):
            self.enabled = True
            self.api_key = os.getenv('WEAVE_API_KEY')
        
        if self.enabled and not self.project_name:
            raise ConfigurationError(
                "Weave project name is required when Weave is enabled",
                config_key="weave.project_name"
            )
        
        if not 0.0 <= self.sampling_rate <= 1.0:
            raise ConfigurationError(
                "Weave sampling rate must be between 0.0 and 1.0",
                config_key="weave.sampling_rate"
            )


@dataclass
class AlertConfig:
    """Configuration for alert system."""
    
    enabled: bool = False  # Disabled by default for easier setup
    webhook_url: Optional[str] = None
    email: Dict[str, Any] = field(default_factory=dict)
    slack: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardConfig:
    """Configuration for web dashboard."""
    
    enabled: bool = False
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.port <= 65535:
            raise ConfigurationError(
                f"Port must be between 1 and 65535, got {self.port}",
                config_key="dashboard.port"
            )


class Config:
    """Main configuration class for AgentSentinel."""
    
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Dictionary configuration (overrides file)
            agent_id: Agent identifier
            environment: Environment name (dev, staging, prod)
        """
        self.config_path = Path(config_path) if config_path else None
        self.raw_config: Dict[str, Any] = {}
        
        # Load and merge configuration
        self._load_config(config_dict, agent_id, environment)
        
        # Create configuration objects
        self._create_config_objects()
    
    def _load_config(
        self,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """Load configuration from file, dict, and environment variables."""
        # Start with default configuration
        self.raw_config = DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                self._merge_config(self.raw_config, file_config)
            except Exception as e:
                raise ConfigurationError(f"Failed to load config file: {e}")
        
        # Override with dictionary config
        if config_dict:
            self._merge_config(self.raw_config, config_dict)
        
        # Set agent_id and environment
        if agent_id:
            self.raw_config['agent_id'] = agent_id
        if environment:
            self.raw_config['environment'] = environment
        
        # Load environment variables
        self._load_env_vars()
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'AGENT_SENTINEL_AGENT_ID': 'agent_id',
            'AGENT_SENTINEL_ENVIRONMENT': 'environment',
            'AGENT_SENTINEL_LOG_LEVEL': 'logging.level',
            'AGENT_SENTINEL_LOG_FORMAT': 'logging.format',
            'AGENT_SENTINEL_LOG_FILE': 'logging.file',
            'AGENT_SENTINEL_DETECTION_ENABLED': 'detection.enabled',
            'AGENT_SENTINEL_DETECTION_THRESHOLD': 'detection.confidence_threshold',
            'AGENT_SENTINEL_ALERTS_ENABLED': 'alerts.enabled',
            'AGENT_SENTINEL_ALERTS_WEBHOOK': 'alerts.webhook_url',
            'AGENT_SENTINEL_DASHBOARD_ENABLED': 'dashboard.enabled',
            'AGENT_SENTINEL_DASHBOARD_HOST': 'dashboard.host',
            'AGENT_SENTINEL_DASHBOARD_PORT': 'dashboard.port',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to nested key
                keys = config_key.split('.')
                current = self.raw_config
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif '.' in value and value.replace('.', '').isdigit():
                    value = float(value)
                
                current[keys[-1]] = value
    
    def _create_config_objects(self) -> None:
        """Create configuration objects from raw configuration."""
        try:
            self.service = ServiceConfig()
            self.detection = DetectionConfig(**self.raw_config.get('detection', {}))
            self.logging = LoggingConfig(**self.raw_config.get('logging', {}))
            self.weave = WeaveConfig(**self.raw_config.get('weave', {}))
            self.alerts = AlertConfig(**self.raw_config.get('alerts', {}))
            self.dashboard = DashboardConfig(**self.raw_config.get('dashboard', {}))
            
            # Set basic properties
            self.agent_id = self.raw_config.get('agent_id', 'default-agent')
            self.environment = self.raw_config.get('environment', 'development')
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create configuration objects: {e}")
    
    def reload(self) -> bool:
        """Reload configuration from file."""
        try:
            old_config = self.raw_config.copy()
            self._load_config()
            self._create_config_objects()
            return old_config != self.raw_config
        except Exception as e:
            raise ConfigurationError(f"Failed to reload configuration: {e}")
    
    def get_rule_config(self, threat_type: ThreatType) -> Dict[str, Any]:
        """Get configuration for a specific threat detection rule."""
        return self.detection.rules.get(threat_type.value, {})
    
    def is_rule_enabled(self, threat_type: ThreatType) -> bool:
        """Check if a specific threat detection rule is enabled."""
        rule_config = self.get_rule_config(threat_type)
        return rule_config.get('enabled', True)
    
    def get_rule_severity(self, threat_type: ThreatType) -> SeverityLevel:
        """Get severity level for a specific threat type."""
        rule_config = self.get_rule_config(threat_type)
        severity_str = rule_config.get('severity', 'MEDIUM')
        try:
            return SeverityLevel(severity_str.upper())
        except ValueError:
            return SeverityLevel.MEDIUM
    
    def get_rate_limit(self, tool_name: Optional[str] = None) -> tuple[int, int]:
        """Get rate limit configuration (requests, window_seconds)."""
        if tool_name and tool_name in self.detection.rate_limits:
            limit_config = self.detection.rate_limits[tool_name]
        else:
            limit_config = self.detection.rate_limits.get('default', {'requests': 100, 'window': 60})
        
        return limit_config.get('requests', 100), limit_config.get('window', 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'agent_id': self.agent_id,
            'environment': self.environment,
            'service': {
                'core_sdk': True,
            },
            'detection': {
                'enabled': self.detection.enabled,
                'confidence_threshold': self.detection.confidence_threshold,
                'rules': self.detection.rules,
                'rate_limits': self.detection.rate_limits,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count,
            },
            'weave': {
                'enabled': self.weave.enabled,
                'project_name': self.weave.project_name,
                'trace_llm_calls': self.weave.trace_llm_calls,
                'trace_intelligence_ops': self.weave.trace_intelligence_ops,
                'trace_report_generation': self.weave.trace_report_generation,
            },
            'alerts': {
                'enabled': self.alerts.enabled,
                'webhook_url': self.alerts.webhook_url,
                'email': self.alerts.email,
                'slack': self.alerts.slack,
            },
            'dashboard': {
                'enabled': self.dashboard.enabled,
                'host': self.dashboard.host,
                'port': self.dashboard.port,
                'debug': self.dashboard.debug,
            },
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"Config(agent_id={self.agent_id}, environment={self.environment})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Config(agent_id={self.agent_id}, environment={self.environment}, core_sdk=True)" 