"""
Core module for AgentSentinel.

This module contains the main SDK classes and core functionality.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sentinel import AgentSentinel
    from .config import Config
    from .exceptions import (
        AgentSentinelError,
        ConfigurationError,
        SecurityError,
        DetectionError,
    )

__all__ = [
    "AgentSentinel",
    "Config",
    "AgentSentinelError",
    "ConfigurationError",
    "SecurityError",
    "DetectionError",
] 