"""
Agent Sentinel - Enterprise Security Monitoring SDK

A comprehensive security monitoring solution for AI agents with real-time threat detection,
behavioral analysis, and enterprise-grade reporting capabilities.
"""

from .core.sentinel import AgentSentinel
from .wrappers.decorators import sentinel, monitor
from .wrappers.mcp_wrapper import secure_mcp_method

# Main class with alias for better UX
Sentinel = AgentSentinel

# Nice aliases for better UX
monitor_mcp = secure_mcp_method

# Create a default global instance for decorator compatibility
# This allows users to retrieve events from decorators without agent ID matching issues
default_sentinel = AgentSentinel(agent_id="default")

def get_all_events(*args, **kwargs):
    """
    Convenience function to get all security events from any agent.
    
    This is useful when using decorators that create their own agent IDs.
    
    Returns:
        List of all security events from all agents
    """
    return default_sentinel.get_events(include_all_agents=True, *args, **kwargs)

# Main exports
__all__ = [
    "AgentSentinel",
    "Sentinel",  # Shorter alias for better UX
    "sentinel",
    "monitor", 
    "monitor_mcp",  # Nice alias for MCP monitoring
    "get_all_events",  # Convenience function for getting all events
    "default_sentinel",  # Global instance for decorator compatibility
]

# Version
__version__ = "0.3.0" 