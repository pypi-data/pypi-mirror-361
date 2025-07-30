"""
Agent Sentinel - Enterprise Security Monitoring SDK

A comprehensive security monitoring solution for AI agents with real-time threat detection,
behavioral analysis, and enterprise-grade reporting capabilities.
"""

from .core.sentinel import AgentSentinel
from .wrappers.decorators import sentinel, monitor, secure_function
from .wrappers.mcp_wrapper import secure_mcp_tool, secure_mcp_method
from .wrappers.communication_wrapper import secure_communication

# Main class with alias for better UX
Sentinel = AgentSentinel

# Nice aliases for better UX
monitor_mcp = secure_mcp_method

# Main exports
__all__ = [
    "AgentSentinel",
    "Sentinel",  # Shorter alias for better UX
    "sentinel",
    "monitor", 
    "monitor_mcp",  # Nice alias for MCP monitoring
    "secure_function",
    "secure_mcp_tool",
    "secure_mcp_method",
    "secure_communication",
]

# Version
__version__ = "0.1.6" 