"""
Decorators for Agent Wrapper

Provides convenient decorators for monitoring AI agents including
@sentinel decorator and context manager utilities.
"""

import functools
from contextlib import contextmanager
from typing import Callable, Optional, Generator

from .agent_wrapper import AgentWrapper
from ..logging.structured_logger import SecurityLogger


def sentinel(
    agent_id: Optional[str] = None,
    enable_input_validation: bool = True,
    strict_validation: bool = False,
    logger: Optional[SecurityLogger] = None,
    enable_behavior_analysis: bool = True,
    enable_performance_monitoring: bool = True
) -> Callable:
    """
    Decorator to monitor an entire agent class
    
    This decorator automatically wraps all public methods of a class
    with security monitoring and validation.
    
    Args:
        agent_id: Unique identifier for the agent
        enable_input_validation: Enable input validation
        strict_validation: Use strict validation mode
        logger: Security logger instance
        enable_behavior_analysis: Enable behavior analysis
        enable_performance_monitoring: Enable performance monitoring
    
    Usage:
        @sentinel(agent_id="my_agent")
        class MyAgent:
            def process_data(self, data: str) -> str:
                return data.upper()
    """
    def decorator(cls):
        # Create wrapper instance
        wrapper_instance = AgentWrapper(
            agent_id=agent_id or cls.__name__,
            logger=logger,
            enable_input_validation=enable_input_validation,
            strict_validation=strict_validation,
            enable_behavior_analysis=enable_behavior_analysis,
            enable_performance_monitoring=enable_performance_monitoring
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
        cls._agent_wrapper = wrapper_instance
        cls._original_methods = original_methods
        
        # Add utility methods to class
        cls.get_security_stats = lambda self: wrapper_instance.get_agent_stats()
        cls.get_session_info = lambda self, session_id: wrapper_instance.get_session_info(session_id)
        
        return cls
    
    return decorator


def monitor(
    validate_inputs: bool = True,
    validate_outputs: bool = False,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to monitor individual methods
    
    This decorator can be used to monitor individual methods without
    wrapping the entire class.
    
    Args:
        validate_inputs: Whether to validate method inputs
        validate_outputs: Whether to validate method outputs
        agent_id: Agent identifier for logging
        logger: Security logger instance
    
    Usage:
        @monitor(validate_inputs=True, validate_outputs=True)
        def process_data(self, data: str) -> str:
            return data.upper()
    """
    def decorator(func):
        # Create a wrapper instance for this method
        wrapper_instance = AgentWrapper(
            agent_id=agent_id or f"{func.__module__}.{func.__name__}",
            logger=logger
        )
        
        # Apply the monitor decorator
        return wrapper_instance.monitor(
            validate_inputs=validate_inputs,
            validate_outputs=validate_outputs
        )(func)
    
    return decorator


@contextmanager
def monitor_agent_session(
    agent_id: str,
    session_name: Optional[str] = None,
    logger: Optional[SecurityLogger] = None,
    enable_input_validation: bool = True,
    strict_validation: bool = False
) -> Generator[AgentWrapper, None, None]:
    """
    Context manager for monitoring agent sessions
    
    This context manager creates a temporary agent wrapper for monitoring
    a specific session or block of code.
    
    Args:
        agent_id: Unique identifier for the agent
        session_name: Optional name for the session
        logger: Security logger instance
        enable_input_validation: Enable input validation
        strict_validation: Use strict validation mode
    
    Usage:
        with monitor_agent_session("my_agent", "data_processing") as wrapper:
            # Your code here
            result = my_function()
    """
    wrapper = AgentWrapper(
        agent_id=agent_id,
        logger=logger,
        enable_input_validation=enable_input_validation,
        strict_validation=strict_validation
    )
    
    with wrapper.monitor_session(session_name) as session_id:
        # Add session_id to wrapper for easy access
        wrapper.current_session_id = session_id
        yield wrapper


def secure_function(
    validate_inputs: bool = True,
    validate_outputs: bool = False,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure standalone functions
    
    This decorator can be used to secure standalone functions that are not
    part of a class.
    
    Args:
        validate_inputs: Whether to validate function inputs
        validate_outputs: Whether to validate function outputs
        agent_id: Agent identifier for logging
        logger: Security logger instance
    
    Usage:
        @secure_function(validate_inputs=True)
        def process_data(data: str) -> str:
            return data.upper()
    """
    def decorator(func):
        # Create a wrapper instance for this function
        wrapper_instance = AgentWrapper(
            agent_id=agent_id or f"{func.__module__}.{func.__name__}",
            logger=logger
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use the wrapper's secure method functionality
            secured_func = wrapper_instance.monitor(
                validate_inputs=validate_inputs,
                validate_outputs=validate_outputs
            )(func)
            return secured_func(*args, **kwargs)
        
        # Add wrapper instance to function for accessing stats
        wrapper._agent_wrapper = wrapper_instance
        
        return wrapper
    
    return decorator


class SecurityContext:
    """
    Context manager for temporary security configurations
    
    This class provides a way to temporarily change security settings
    for a block of code.
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
        """Enter the security context"""
        self.wrapper = AgentWrapper(
            agent_id=self.agent_id,
            logger=self.logger,
            enable_input_validation=self.enable_input_validation,
            strict_validation=self.strict_validation,
            enable_performance_monitoring=self.enable_performance_monitoring
        )
        return self.wrapper

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the security context"""
        if self.wrapper:
            # Log final stats
            stats = self.wrapper.get_agent_stats()
            if self.wrapper.logger:
                self.wrapper.logger.info(
                    f"Security context ended for {self.agent_id}",
                    extra={
                        'agent_id': self.agent_id,
                        'final_stats': stats['stats'],
                        'component': 'security_context'
                    }
                )
        
        # Clean up
        self.wrapper = None


# Convenience functions
def get_agent_wrapper(obj) -> Optional[AgentWrapper]:
    """Get the agent wrapper from a secured object"""
    return getattr(obj, '_agent_wrapper', None)


def is_secured(obj) -> bool:
    """Check if an object is secured with AgentSentinel"""
    return hasattr(obj, '_agent_wrapper')


def get_security_stats(obj) -> Optional[dict]:
    """Get security statistics from a secured object"""
    wrapper = get_agent_wrapper(obj)
    if wrapper:
        return wrapper.get_agent_stats()
    return None 