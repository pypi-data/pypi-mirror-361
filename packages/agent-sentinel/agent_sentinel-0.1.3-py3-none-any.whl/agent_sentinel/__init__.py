"""
AgentSentinel - A lightweight, pluggable security monitoring SDK for AI agents.

This package provides real-time threat detection, comprehensive logging,
and intuitive visualization for AI agents during MCP tool interactions
and agent-to-agent communications.
"""

from typing import TYPE_CHECKING

# Version information
__version__ = "0.1.0"
__author__ = "AgentSentinel Team"
__email__ = "team@agentsentinel.dev"
__license__ = "MIT"

# Import main classes for public API
if TYPE_CHECKING:
    from .core.sentinel import AgentSentinel
    from .wrappers.agent_wrapper import AgentWrapper, sentinel
    from .wrappers.decorators import monitor
    from .wrappers.communication_wrapper import secure_communication, secure_send, secure_receive
    from .wrappers.mcp_wrapper import secure_mcp_tool, secure_tool_call

# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy import for better performance and circular dependency avoidance."""
    if name == "AgentSentinel":
        from .core.sentinel import AgentSentinel
        return AgentSentinel
    elif name == "AgentWrapper":
        from .wrappers.agent_wrapper import AgentWrapper
        return AgentWrapper
    elif name == "sentinel":
        from .wrappers.agent_wrapper import sentinel
        return sentinel
    elif name == "monitor":
        from .wrappers.decorators import monitor
        return monitor
    elif name == "secure_communication":
        from .wrappers.communication_wrapper import secure_communication
        return secure_communication
    elif name == "secure_send":
        from .wrappers.communication_wrapper import secure_send
        return secure_send
    elif name == "secure_receive":
        from .wrappers.communication_wrapper import secure_receive
        return secure_receive
    elif name == "secure_mcp_tool":
        from .wrappers.mcp_wrapper import secure_mcp_tool
        return secure_mcp_tool
    elif name == "secure_tool_call":
        from .wrappers.mcp_wrapper import secure_tool_call
        return secure_tool_call
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Public API
__all__ = [
    "__version__",
    "AgentSentinel",
    "AgentWrapper",
    "sentinel",
    "monitor",
    "secure_communication",
    "secure_send",
    "secure_receive",
    "secure_mcp_tool",
    "secure_tool_call",
] 