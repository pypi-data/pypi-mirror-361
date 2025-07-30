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
class DetectionConfig:
    """Configuration for threat detection rules."""
    
    enabled: bool = True
    confidence_threshold: float = 0.7
    rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ConfigurationError(
                "Confidence threshold must be between 0.0 and 1.0",
                config_key="detection.confidence_threshold"
            )


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
    """Configuration for Weave integration."""
    
    enabled: bool = False
    project_name: str = "agent-sentinel"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.enabled and not self.project_name:
            raise ConfigurationError(
                "Weave project name is required when Weave is enabled",
                config_key="weave.project_name"
            )


@dataclass
class AlertConfig:
    """Configuration for alert system."""
    
    enabled: bool = True
    webhook_url: Optional[str] = None
    email: Dict[str, Any] = field(default_factory=dict)
    slack: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.enabled and not any([self.webhook_url, self.email.get("enabled"), self.slack.get("enabled")]):
            raise ConfigurationError(
                "At least one alert method must be configured when alerts are enabled",
                config_key="alerts"
            )


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
    """
    Main configuration class for AgentSentinel.
    
    This class handles loading configuration from multiple sources:
    1. YAML files
    2. Environment variables
    3. Programmatic settings
    
    It also provides validation and hot-reloading capabilities.
    """
    
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
            environment: Environment name (development, production, etc.)
        """
        self.config_path = Path(config_path) if config_path else None
        self.last_modified: Optional[datetime] = None
        self._raw_config: Dict[str, Any] = {}
        
        # Load configuration from multiple sources
        self._load_config(config_dict, agent_id, environment)
        
        # Create typed configuration objects
        self._create_config_objects()
    
    def _load_config(
        self,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """Load configuration from multiple sources."""
        # Start with default configuration
        self._raw_config = DEFAULT_CONFIG.copy()
        
        # Load from YAML file if provided
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        # Merge with defaults
                        self._merge_config(self._raw_config, file_config)
                        
                        # Track file modification time for hot-reloading
                        self.last_modified = datetime.fromtimestamp(
                            self.config_path.stat().st_mtime
                        )
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to load configuration from {self.config_path}: {e}",
                    config_path=str(self.config_path)
                )
        
        # Override with dictionary config if provided
        if config_dict:
            self._merge_config(self._raw_config, config_dict)
        
        # Override with environment variables
        self._load_env_vars()
        
        # Override with direct parameters
        if agent_id:
            self._raw_config["agent_id"] = agent_id
        if environment:
            self._raw_config["environment"] = environment
    
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
            "AGENT_SENTINEL_AGENT_ID": ["agent_id"],
            "AGENT_SENTINEL_ENVIRONMENT": ["environment"],
            "AGENT_SENTINEL_LOG_LEVEL": ["logging", "level"],
            "AGENT_SENTINEL_LOG_FILE": ["logging", "file"],
            "AGENT_SENTINEL_WEAVE_PROJECT": ["weave", "project_name"],
            "AGENT_SENTINEL_WEAVE_API_KEY": ["weave", "api_key"],
            "AGENT_SENTINEL_WEBHOOK_URL": ["alerts", "webhook_url"],
            "AGENT_SENTINEL_DASHBOARD_PORT": ["dashboard", "port"],
            "AGENT_SENTINEL_DASHBOARD_HOST": ["dashboard", "host"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Navigate to the nested configuration
                current = self._raw_config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Set the value (with type conversion for special cases)
                final_key = config_path[-1]
                if final_key == "port":
                    current[final_key] = int(value)
                elif value.lower() in ["true", "false"]:
                    current[final_key] = value.lower() == "true"
                else:
                    current[final_key] = value
    
    def _create_config_objects(self) -> None:
        """Create typed configuration objects from raw configuration."""
        try:
            # Extract configuration sections
            config_root = self._raw_config.get("agent_sentinel", self._raw_config)
            
            # Basic properties
            self.agent_id: str = config_root.get("agent_id", "default_agent")
            self.environment: str = config_root.get("environment", "development")
            
            # Typed configuration objects
            self.detection = DetectionConfig(**config_root.get("detection", {}))
            self.logging = LoggingConfig(**config_root.get("logging", {}))
            self.weave = WeaveConfig(**config_root.get("weave", {}))
            self.alerts = AlertConfig(**config_root.get("alerts", {}))
            self.dashboard = DashboardConfig(**config_root.get("dashboard", {}))
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create configuration objects: {e}")
    
    def reload(self) -> bool:
        """
        Reload configuration from file if it has been modified.
        
        Returns:
            bool: True if configuration was reloaded, False otherwise
        """
        if not self.config_path or not self.config_path.exists():
            return False
        
        try:
            current_modified = datetime.fromtimestamp(
                self.config_path.stat().st_mtime
            )
            
            if self.last_modified and current_modified <= self.last_modified:
                return False
            
            # Reload configuration
            self._load_config()
            self._create_config_objects()
            self.last_modified = current_modified
            
            return True
            
        except Exception as e:
            raise ConfigurationError(f"Failed to reload configuration: {e}")
    
    def get_rule_config(self, threat_type: ThreatType) -> Dict[str, Any]:
        """
        Get configuration for a specific threat detection rule.
        
        Args:
            threat_type: Type of threat to get configuration for
            
        Returns:
            Dict containing rule configuration
        """
        rule_name = threat_type.value
        return self.detection.rules.get(rule_name, {
            "enabled": True,
            "severity": "MEDIUM"
        })
    
    def is_rule_enabled(self, threat_type: ThreatType) -> bool:
        """Check if a specific threat detection rule is enabled."""
        rule_config = self.get_rule_config(threat_type)
        return rule_config.get("enabled", True)
    
    def get_rule_severity(self, threat_type: ThreatType) -> SeverityLevel:
        """Get the severity level for a specific threat detection rule."""
        rule_config = self.get_rule_config(threat_type)
        severity_str = rule_config.get("severity", "MEDIUM")
        try:
            return SeverityLevel(severity_str)
        except ValueError:
            return SeverityLevel.MEDIUM
    
    def get_rate_limit(self, tool_name: Optional[str] = None) -> tuple[int, int]:
        """
        Get rate limit configuration for a tool or default.
        
        Args:
            tool_name: Name of the tool to get rate limit for
            
        Returns:
            Tuple of (limit, window_seconds)
        """
        rate_limits = self.detection.rate_limits
        
        if tool_name and tool_name in rate_limits:
            tool_config = rate_limits[tool_name]
            return tool_config.get("limit", 100), tool_config.get("window", 60)
        
        return rate_limits.get("default_limit", 100), rate_limits.get("default_window", 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "agent_id": self.agent_id,
            "environment": self.environment,
            "detection": {
                "enabled": self.detection.enabled,
                "confidence_threshold": self.detection.confidence_threshold,
                "rules": self.detection.rules,
                "rate_limits": self.detection.rate_limits,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_size": self.logging.max_size,
                "backup_count": self.logging.backup_count,
            },
            "weave": {
                "enabled": self.weave.enabled,
                "project_name": self.weave.project_name,
                "api_key": self.weave.api_key,
                "base_url": self.weave.base_url,
            },
            "alerts": {
                "enabled": self.alerts.enabled,
                "webhook_url": self.alerts.webhook_url,
                "email": self.alerts.email,
                "slack": self.alerts.slack,
            },
            "dashboard": {
                "enabled": self.dashboard.enabled,
                "host": self.dashboard.host,
                "port": self.dashboard.port,
                "debug": self.dashboard.debug,
            },
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"AgentSentinel Config (agent_id={self.agent_id}, env={self.environment})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Config(agent_id='{self.agent_id}', environment='{self.environment}')" 