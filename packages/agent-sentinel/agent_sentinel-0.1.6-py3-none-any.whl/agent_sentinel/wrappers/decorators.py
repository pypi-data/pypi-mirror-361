"""
Simplified decorators for Agent Sentinel

Provides clean, simple decorators for monitoring AI agents with proper type hints
and correct signatures.
"""

import functools
from contextlib import contextmanager
from typing import Callable, Optional, Generator, Any

from .agent_wrapper import AgentWrapper
from ..logging.structured_logger import SecurityLogger


def sentinel(cls):
    """
    Simple decorator to monitor an entire agent class
    
    This decorator automatically wraps all public methods of a class
    with security monitoring.
    
    Usage:
        @sentinel
        class MyAgent:
            def process_data(self, data: str) -> str:
                return data.upper()
    """
    # Create wrapper instance
    wrapper_instance = AgentWrapper(
        agent_id=getattr(cls, '__name__', 'UnknownClass'),
        enable_input_validation=True,
        strict_validation=False,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True
    )
    
    # Store original methods
    original_methods = {}
    
    # Wrap all public methods
    for attr_name in dir(cls):
        if not attr_name.startswith('_'):
            attr = getattr(cls, attr_name)
            if callable(attr):
                # Store original method
                original_methods[attr_name] = attr
                # Wrap with security
                wrapped_method = wrapper_instance.monitor()(attr)
                setattr(cls, attr_name, wrapped_method)
    
    # Add wrapper instance to class
    setattr(cls, '_agent_wrapper', wrapper_instance)
    setattr(cls, '_original_methods', original_methods)
    
    # Add utility methods to class
    setattr(cls, 'get_security_stats', lambda self: wrapper_instance.get_agent_stats())
    setattr(cls, 'get_session_info', lambda self, session_id: wrapper_instance.get_session_info(session_id))
    
    return cls


def monitor(func):
    """
    Simple decorator to monitor individual methods
    
    This decorator can be used to monitor individual methods.
    
    Usage:
        @monitor
        def process_data(self, data: str) -> str:
            return data.upper()
    """
    # Create a wrapper instance for this method
    wrapper_instance = AgentWrapper(
        agent_id=f"{getattr(func, '__module__', 'unknown')}.{getattr(func, '__name__', 'unknown')}"
    )
    
    # Apply the monitor decorator
    return wrapper_instance.monitor()(func)


def secure_function(func):
    """
    Simple decorator to secure standalone functions
    
    This decorator can be used to secure standalone functions.
    
    Usage:
        @secure_function
        def process_data(data: str) -> str:
            return data.upper()
    """
    # Create a wrapper instance for this function
    wrapper_instance = AgentWrapper(
        agent_id=f"{getattr(func, '__module__', 'unknown')}.{getattr(func, '__name__', 'unknown')}"
    )
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Use the wrapper's secure method functionality
        secured_func = wrapper_instance.monitor()(func)
        return secured_func(*args, **kwargs)
    
    # Add wrapper instance to function for accessing stats
    setattr(wrapper, '_agent_wrapper', wrapper_instance)
    setattr(wrapper, 'get_security_stats', lambda: wrapper_instance.get_agent_stats())
    
    return wrapper


@contextmanager
def monitor_agent_session(
    agent_id: str,
    session_name: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Generator[AgentWrapper, None, None]:
    """
    Context manager for monitoring agent sessions
    
    This context manager creates a temporary agent wrapper for monitoring
    a specific session or block of code.
    
    Args:
        agent_id: Unique identifier for the agent
        session_name: Optional name for the session
        logger: Security logger instance
    
    Usage:
        with monitor_agent_session("my_agent", "data_processing") as wrapper:
            # Your code here
            result = my_function()
    """
    wrapper = AgentWrapper(
        agent_id=agent_id,
        logger=logger,
        enable_input_validation=True,
        strict_validation=False
    )
    
    with wrapper.monitor_session(session_name) as session_id:
        # Add session_id to wrapper for easy access
        setattr(wrapper, 'current_session_id', session_id)
        yield wrapper


class SecurityContext:
    """
    Context manager for security monitoring
    
    Provides a simple way to monitor code blocks with security features.
    """
    
    def __init__(
        self,
        agent_id: str,
        strict_validation: bool = False,
        enable_input_validation: bool = True,
        enable_performance_monitoring: bool = True,
        logger: Optional[SecurityLogger] = None
    ):
        self.agent_id = agent_id
        self.strict_validation = strict_validation
        self.enable_input_validation = enable_input_validation
        self.enable_performance_monitoring = enable_performance_monitoring
        self.logger = logger
        self.wrapper: Optional[AgentWrapper] = None
    
    def __enter__(self) -> AgentWrapper:
        """Enter the security context."""
        self.wrapper = AgentWrapper(
            agent_id=self.agent_id,
            logger=self.logger,
            enable_input_validation=self.enable_input_validation,
            strict_validation=self.strict_validation,
            enable_performance_monitoring=self.enable_performance_monitoring
        )
        return self.wrapper
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the security context."""
        if self.wrapper:
            # Clean up any resources
            pass


def get_agent_wrapper(obj: Any) -> Optional[AgentWrapper]:
    """Get the agent wrapper from an object if it exists."""
    return getattr(obj, '_agent_wrapper', None)


def is_secured(obj: Any) -> bool:
    """Check if an object is secured with Agent Sentinel."""
    return hasattr(obj, '_agent_wrapper')


def get_security_stats(obj: Any) -> Optional[dict]:
    """Get security statistics from an object if available."""
    wrapper = get_agent_wrapper(obj)
    return wrapper.get_agent_stats() if wrapper else None 