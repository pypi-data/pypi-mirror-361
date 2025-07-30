"""
MCP Wrapper for AgentSentinel

Enterprise-grade wrapper for monitoring and securing MCP (Model Context Protocol) tools,
including input validation, output sanitization, and comprehensive audit trails.
"""

import asyncio
import functools
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Union, Generator, AsyncGenerator
from dataclasses import dataclass, field

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..logging.structured_logger import SecurityLogger
from ..security.validators import InputValidator, ValidationResult
from .agent_wrapper import AgentWrapper


@dataclass
class MCPToolCall:
    """Represents an MCP tool call"""
    call_id: str
    tool_name: str
    agent_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    security_validations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPSession:
    """MCP tool usage session"""
    session_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tool_calls: List[MCPToolCall] = field(default_factory=list)
    security_events: List[SecurityEvent] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPWrapper:
    """
    Enterprise-grade MCP wrapper for tool monitoring and security
    
    Provides comprehensive monitoring, validation, and security features
    for MCP tool interactions in production environments.
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        enable_input_validation: bool = True,
        enable_output_validation: bool = True,
        enable_rate_limiting: bool = True,
        enable_performance_monitoring: bool = True,
        enable_audit_logging: bool = True,
        max_input_size: int = 1024 * 1024,  # 1MB
        max_output_size: int = 10 * 1024 * 1024,  # 10MB
        rate_limit_per_minute: int = 50,
        strict_validation: bool = False
    ):
        """
        Initialize MCP wrapper
        
        Args:
            agent_id: Unique identifier for the agent
            logger: Security logger instance
            enable_input_validation: Enable input validation
            enable_output_validation: Enable output validation
            enable_rate_limiting: Enable rate limiting
            enable_performance_monitoring: Enable performance monitoring
            enable_audit_logging: Enable comprehensive audit logging
            max_input_size: Maximum allowed input size in bytes
            max_output_size: Maximum allowed output size in bytes
            rate_limit_per_minute: Rate limit for tool calls per minute
            strict_validation: Use strict validation mode
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"mcp_wrapper_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        
        # Configuration
        self.enable_input_validation = enable_input_validation
        self.enable_output_validation = enable_output_validation
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_performance_monitoring = enable_performance_monitoring
        self.enable_audit_logging = enable_audit_logging
        self.max_input_size = max_input_size
        self.max_output_size = max_output_size
        self.rate_limit_per_minute = rate_limit_per_minute
        self.strict_validation = strict_validation
        
        # Initialize validators
        if self.enable_input_validation or self.enable_output_validation:
            self.input_validator = InputValidator(strict_mode=strict_validation)
        else:
            self.input_validator = None
        
        # Active MCP sessions
        self.active_sessions: Dict[str, MCPSession] = {}
        
        # Rate limiting tracking
        self.tool_call_counts: Dict[str, List[float]] = {}
        
        # Statistics
        self.stats = {
            'total_tool_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_sessions': 0,
            'security_events': 0,
            'rate_limit_violations': 0,
            'average_call_duration': 0.0,
            'tool_usage_patterns': {},
            'input_size_distribution': {},
            'output_size_distribution': {}
        }
        
        self.logger.info(f"MCP wrapper initialized for {agent_id}", extra={
            'component': 'mcp_wrapper',
            'agent_id': agent_id,
            'configuration': {
                'input_validation': enable_input_validation,
                'output_validation': enable_output_validation,
                'rate_limiting': enable_rate_limiting,
                'performance_monitoring': enable_performance_monitoring,
                'audit_logging': enable_audit_logging,
                'max_input_size': max_input_size,
                'max_output_size': max_output_size,
                'rate_limit_per_minute': rate_limit_per_minute
            }
        })

    def secure_mcp_tool(self, validate_inputs: bool = True, validate_outputs: bool = True):
        """
        Decorator for securing MCP tool calls
        
        Args:
            validate_inputs: Whether to validate tool inputs
            validate_outputs: Whether to validate tool outputs
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_tool_with_monitoring(
                    func, args, kwargs, validate_inputs, validate_outputs
                )
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_tool_with_monitoring_async(
                    func, args, kwargs, validate_inputs, validate_outputs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        
        return decorator

    def _execute_tool_with_monitoring(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_inputs: bool,
        validate_outputs: bool
    ) -> Any:
        """Execute MCP tool with comprehensive monitoring"""
        tool_name = func.__name__
        start_time = time.time()
        
        # Create tool call record
        call_id = str(uuid.uuid4())
        tool_call = MCPToolCall(
            call_id=call_id,
            tool_name=tool_name,
            agent_id=self.agent_id,
            input_data=self._extract_input_data(args, kwargs)
        )
        
        try:
            # Rate limiting check
            if self.enable_rate_limiting:
                self._check_rate_limit(tool_name)
            
            # Input validation
            if validate_inputs and self.input_validator:
                self._validate_tool_inputs(tool_call)
            
            # Input size validation
            self._validate_input_size(tool_call.input_data)
            
            # Execute the tool
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Output validation
            if validate_outputs and self.input_validator:
                self._validate_tool_output(result, tool_call)
            
            # Output size validation
            self._validate_output_size(result)
            
            # Record successful execution
            tool_call.end_time = datetime.now(timezone.utc)
            tool_call.duration = duration
            tool_call.output_data = self._sanitize_output(result)
            tool_call.success = True
            
            self._record_tool_call(tool_call)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_tool_performance(tool_name, duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failed execution
            tool_call.end_time = datetime.now(timezone.utc)
            tool_call.duration = duration
            tool_call.success = False
            tool_call.error_message = str(e)
            
            self._record_tool_call(tool_call)
            self._record_tool_error(tool_name, str(e), duration)
            raise

    async def _execute_tool_with_monitoring_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_inputs: bool,
        validate_outputs: bool
    ) -> Any:
        """Execute async MCP tool with comprehensive monitoring"""
        tool_name = func.__name__
        start_time = time.time()
        
        # Create tool call record
        call_id = str(uuid.uuid4())
        tool_call = MCPToolCall(
            call_id=call_id,
            tool_name=tool_name,
            agent_id=self.agent_id,
            input_data=self._extract_input_data(args, kwargs)
        )
        
        try:
            # Rate limiting check
            if self.enable_rate_limiting:
                self._check_rate_limit(tool_name)
            
            # Input validation
            if validate_inputs and self.input_validator:
                self._validate_tool_inputs(tool_call)
            
            # Input size validation
            self._validate_input_size(tool_call.input_data)
            
            # Execute the async tool
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Output validation
            if validate_outputs and self.input_validator:
                self._validate_tool_output(result, tool_call)
            
            # Output size validation
            self._validate_output_size(result)
            
            # Record successful execution
            tool_call.end_time = datetime.now(timezone.utc)
            tool_call.duration = duration
            tool_call.output_data = self._sanitize_output(result)
            tool_call.success = True
            
            self._record_tool_call(tool_call)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_tool_performance(tool_name, duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failed execution
            tool_call.end_time = datetime.now(timezone.utc)
            tool_call.duration = duration
            tool_call.success = False
            tool_call.error_message = str(e)
            
            self._record_tool_call(tool_call)
            self._record_tool_error(tool_name, str(e), duration)
            raise

    def _extract_input_data(self, args: tuple, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract input data from function arguments"""
        input_data = {
            'args': [str(arg) for arg in args],
            'kwargs': {key: str(value) for key, value in kwargs.items()}
        }
        
        # Try to extract structured data from common MCP patterns
        if args and isinstance(args[0], dict):
            input_data['structured_input'] = args[0]
        elif kwargs and 'input' in kwargs:
            input_data['structured_input'] = kwargs['input']
        
        return input_data

    def _check_rate_limit(self, tool_name: str):
        """Check rate limiting for tool calls"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries
        if tool_name in self.tool_call_counts:
            self.tool_call_counts[tool_name] = [
                timestamp for timestamp in self.tool_call_counts[tool_name]
                if timestamp > window_start
            ]
        else:
            self.tool_call_counts[tool_name] = []
        
        # Check limit
        if len(self.tool_call_counts[tool_name]) >= self.rate_limit_per_minute:
            self.stats['rate_limit_violations'] += 1
            
            event = SecurityEvent(
                threat_type=ThreatType.RATE_LIMIT_VIOLATION,
                severity=SeverityLevel.MEDIUM,
                message=f"Rate limit exceeded for tool {tool_name}",
                confidence=1.0,
                context={
                    'tool_name': tool_name,
                    'rate_limit': self.rate_limit_per_minute,
                    'current_count': len(self.tool_call_counts[tool_name]),
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='rate_limiting'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            raise Exception(f"Rate limit exceeded for tool {tool_name}")
        
        # Add current call
        self.tool_call_counts[tool_name].append(current_time)

    def _validate_input_size(self, input_data: Dict[str, Any]):
        """Validate input data size"""
        input_size = len(str(input_data).encode('utf-8'))
        
        if input_size > self.max_input_size:
            event = SecurityEvent(
                threat_type=ThreatType.RESOURCE_ABUSE,
                severity=SeverityLevel.MEDIUM,
                message=f"Input size exceeds limit: {input_size} bytes",
                confidence=1.0,
                context={
                    'input_size': input_size,
                    'max_input_size': self.max_input_size,
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='size_validation'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            raise Exception(f"Input size {input_size} bytes exceeds limit {self.max_input_size} bytes")

    def _validate_output_size(self, output_data: Any):
        """Validate output data size"""
        output_size = len(str(output_data).encode('utf-8'))
        
        if output_size > self.max_output_size:
            event = SecurityEvent(
                threat_type=ThreatType.RESOURCE_ABUSE,
                severity=SeverityLevel.MEDIUM,
                message=f"Output size exceeds limit: {output_size} bytes",
                confidence=1.0,
                context={
                    'output_size': output_size,
                    'max_output_size': self.max_output_size,
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='size_validation'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            raise Exception(f"Output size {output_size} bytes exceeds limit {self.max_output_size} bytes")

    def _validate_tool_inputs(self, tool_call: MCPToolCall):
        """Validate tool inputs for security threats"""
        if not self.input_validator:
            return
        
        validation_results = []
        
        # Validate string inputs
        for key, value in tool_call.input_data.items():
            if isinstance(value, str):
                validation = self.input_validator.validate(value)
                validation_results.append({
                    'type': 'input',
                    'key': key,
                    'result': validation.result.value,
                    'is_safe': validation.is_safe,
                    'threat_type': validation.threat_type.value if validation.threat_type else None,
                    'violations': validation.violations
                })
                
                if not validation.is_safe and validation.threat_type:
                    event = SecurityEvent(
                        threat_type=validation.threat_type,
                        severity=SeverityLevel.HIGH,
                        message=f"Malicious input detected in tool {tool_call.tool_name}",
                        confidence=validation.confidence_score,
                        context={
                            'tool_name': tool_call.tool_name,
                            'input_key': key,
                            'violations': validation.violations,
                            'input_sample': value[:100] + '...' if len(value) > 100 else value,
                            'agent_id': self.agent_id
                        },
                        agent_id=self.agent_id,
                        detection_method='input_validation'
                    )
                    
                    self.logger.security_event(
                        event.message,
                        threat_type=event.threat_type,
                        severity=event.severity,
                        confidence=event.confidence,
                        event_id=event.event_id,
                        extra=event.context
                    )
                    
                    self.stats['security_events'] += 1
                    raise Exception(f"Malicious input detected: {validation.violations}")
        
        tool_call.security_validations = validation_results

    def _validate_tool_output(self, output_data: Any, tool_call: MCPToolCall):
        """Validate tool output for security threats"""
        if not self.input_validator or not isinstance(output_data, str):
            return
        
        validation = self.input_validator.validate(output_data)
        
        if not validation.is_safe and validation.threat_type:
            event = SecurityEvent(
                threat_type=validation.threat_type,
                severity=SeverityLevel.MEDIUM,
                message=f"Potentially malicious output from tool {tool_call.tool_name}",
                confidence=validation.confidence_score,
                context={
                    'tool_name': tool_call.tool_name,
                    'output_sample': output_data[:200] + '...' if len(output_data) > 200 else output_data,
                    'violations': validation.violations,
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='output_validation'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            self.stats['security_events'] += 1

    def _sanitize_output(self, output_data: Any) -> Any:
        """Sanitize output data for logging"""
        if isinstance(output_data, str) and len(output_data) > 1000:
            return output_data[:1000] + '...'
        elif isinstance(output_data, dict):
            return {key: self._sanitize_output(value) for key, value in output_data.items()}
        elif isinstance(output_data, list):
            return [self._sanitize_output(item) for item in output_data[:10]]  # Limit to first 10 items
        else:
            return output_data

    def _record_tool_call(self, tool_call: MCPToolCall):
        """Record tool call information"""
        self.stats['total_tool_calls'] += 1
        
        if tool_call.success:
            self.stats['successful_calls'] += 1
        else:
            self.stats['failed_calls'] += 1
        
        # Update tool usage patterns
        tool_name = tool_call.tool_name
        current_count = self.stats['tool_usage_patterns'].get(tool_name, 0)
        self.stats['tool_usage_patterns'][tool_name] = current_count + 1
        
        # Update average call duration
        if tool_call.duration:
            total_calls = self.stats['total_tool_calls']
            current_avg = self.stats['average_call_duration']
            self.stats['average_call_duration'] = (
                (current_avg * (total_calls - 1) + tool_call.duration) / total_calls
            )
        
        # Update input/output size distributions
        input_size = len(str(tool_call.input_data).encode('utf-8'))
        size_range = f"{(input_size // 1024) * 1024}-{((input_size // 1024) + 1) * 1024}"
        current_count = self.stats['input_size_distribution'].get(size_range, 0)
        self.stats['input_size_distribution'][size_range] = current_count + 1
        
        if tool_call.output_data:
            output_size = len(str(tool_call.output_data).encode('utf-8'))
            size_range = f"{(output_size // 1024) * 1024}-{((output_size // 1024) + 1) * 1024}"
            current_count = self.stats['output_size_distribution'].get(size_range, 0)
            self.stats['output_size_distribution'][size_range] = current_count + 1
        
        # Add to active sessions
        for session in self.active_sessions.values():
            session.tool_calls.append(tool_call)
        
        # Log the tool call
        if self.enable_audit_logging:
            self.logger.info(f"MCP tool call: {tool_call.tool_name}", extra={
                'tool_name': tool_call.tool_name,
                'call_id': tool_call.call_id,
                'duration': tool_call.duration,
                'success': tool_call.success,
                'input_size': input_size,
                'security_validations': len(tool_call.security_validations),
                'agent_id': self.agent_id,
                'component': 'mcp_wrapper'
            })

    def _analyze_tool_performance(self, tool_name: str, duration: float):
        """Analyze tool performance for anomalies"""
        avg_duration = self.stats.get('average_call_duration', 0.0)
        
        if avg_duration > 0 and duration > avg_duration * 3:  # 3x slower than average
            self.logger.warning(
                f"Performance anomaly detected in tool {tool_name}",
                extra={
                    'tool_name': tool_name,
                    'duration': duration,
                    'average_duration': avg_duration,
                    'anomaly_factor': duration / avg_duration,
                    'agent_id': self.agent_id,
                    'is_performance_anomaly': True
                }
            )

    def _record_tool_error(self, tool_name: str, error: str, duration: float):
        """Record tool error"""
        self.logger.error(f"Error in MCP tool {tool_name}: {error}", extra={
            'tool_name': tool_name,
            'error': error,
            'duration': duration,
            'agent_id': self.agent_id,
            'component': 'mcp_wrapper'
        })

    @contextmanager
    def monitor_mcp_session(
        self,
        session_name: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Context manager for monitoring MCP sessions"""
        session_id = str(uuid.uuid4())
        session_name = session_name or f"mcp_session_{session_id[:8]}"
        
        session = MCPSession(
            session_id=session_id,
            agent_id=self.agent_id,
            start_time=datetime.now(timezone.utc)
        )
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Started MCP session {session_name}", extra={
            'session_id': session_id,
            'session_name': session_name,
            'agent_id': self.agent_id,
            'component': 'mcp_wrapper'
        })
        
        try:
            yield session_id
        finally:
            session.end_time = datetime.now(timezone.utc)
            
            # Calculate session metrics
            duration = (session.end_time - session.start_time).total_seconds()
            session.performance_metrics = {
                'duration': duration,
                'tool_calls': len(session.tool_calls),
                'security_events': len(session.security_events),
                'success_rate': len([call for call in session.tool_calls if call.success]) / len(session.tool_calls) if session.tool_calls else 0
            }
            
            self.logger.info(f"Ended MCP session {session_name}", extra={
                'session_id': session_id,
                'session_name': session_name,
                'duration': duration,
                'tool_calls': len(session.tool_calls),
                'security_events': len(session.security_events),
                'success_rate': session.performance_metrics['success_rate'],
                'agent_id': self.agent_id
            })
            
            # Remove from active sessions
            self.active_sessions.pop(session_id, None)
            self.stats['total_sessions'] += 1

    def get_mcp_stats(self) -> Dict[str, Any]:
        """Get comprehensive MCP statistics"""
        return {
            'agent_id': self.agent_id,
            'active_sessions': len(self.active_sessions),
            'stats': self.stats.copy(),
            'configuration': {
                'input_validation': self.enable_input_validation,
                'output_validation': self.enable_output_validation,
                'rate_limiting': self.enable_rate_limiting,
                'performance_monitoring': self.enable_performance_monitoring,
                'audit_logging': self.enable_audit_logging,
                'max_input_size': self.max_input_size,
                'max_output_size': self.max_output_size,
                'rate_limit_per_minute': self.rate_limit_per_minute
            },
            'validator_stats': self.input_validator.get_stats() if self.input_validator else None
        }

    def get_session_info(self, session_id: str) -> Optional[MCPSession]:
        """Get information about a specific MCP session"""
        return self.active_sessions.get(session_id)


# Simple decorator for individual MCP tool methods
def secure_mcp_method(
    validate_inputs: bool = True,
    validate_outputs: bool = True,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Simple decorator to secure individual MCP tool methods
    
    Usage:
        @secure_mcp_method()
        def search_web(query: str):
            # Tool implementation
            pass
    """
    def decorator(func):
        # Robustly extract module and name for agent_id
        func_module = getattr(func, "__module__", None) or "unknown_module"
        func_name = getattr(func, "__name__", None) or "unknown_function"
        safe_agent_id = agent_id or f"{func_module}.{func_name}"
        
        # Create a wrapper instance for this method
        wrapper_instance = MCPWrapper(
            agent_id=safe_agent_id,
            logger=logger,
            enable_input_validation=validate_inputs,
            enable_output_validation=validate_outputs
        )
        
        # Apply the secure MCP tool decorator
        return wrapper_instance.secure_mcp_tool(
            validate_inputs=validate_inputs,
            validate_outputs=validate_outputs
        )(func)
    
    return decorator


# Convenience decorators
def secure_mcp_tool(
    agent_id: Optional[str] = None,
    enable_input_validation: bool = True,
    enable_output_validation: bool = True,
    enable_rate_limiting: bool = True,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure MCP tool methods
    
    Usage:
        @secure_mcp_tool(agent_id="my_agent")
        class MyMCPTools:
            @secure_mcp_tool()
            def search_web(self, query: str):
                # Tool implementation
                pass
    """
    def decorator(cls):
        # Create wrapper instance
        wrapper_instance = MCPWrapper(
            agent_id=agent_id or cls.__name__,
            logger=logger,
            enable_input_validation=enable_input_validation,
            enable_output_validation=enable_output_validation,
            enable_rate_limiting=enable_rate_limiting
        )
        
        # Add wrapper instance to class
        cls._mcp_wrapper = wrapper_instance
        
        # Add convenience methods
        cls.secure_mcp_tool = wrapper_instance.secure_mcp_tool
        cls.monitor_mcp_session = wrapper_instance.monitor_mcp_session
        cls.get_mcp_stats = lambda self: wrapper_instance.get_mcp_stats()
        
        return cls
    
    return decorator


def secure_tool_call(
    validate_inputs: bool = True,
    validate_outputs: bool = True,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure individual MCP tool calls
    
    Usage:
        @secure_tool_call(validate_inputs=True, validate_outputs=True)
        def search_web(query: str):
            # Tool implementation
            pass
    """
    def decorator(func):
        # Create a wrapper instance for this method
        wrapper_instance = MCPWrapper(
            agent_id=agent_id or f"{func.__module__}.{func.__name__}",
            logger=logger
        )
        
        # Apply the secure MCP tool decorator
        return wrapper_instance.secure_mcp_tool(
            validate_inputs=validate_inputs,
            validate_outputs=validate_outputs
        )(func)
    
    return decorator


@contextmanager
def monitor_mcp_session(
    agent_id: str,
    session_name: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Generator[MCPWrapper, None, None]:
    """
    Context manager for monitoring MCP sessions
    
    Usage:
        with monitor_mcp_session("my_agent") as wrapper:
            # MCP tool calls
            pass
    """
    wrapper = MCPWrapper(
        agent_id=agent_id,
        logger=logger
    )
    
    with wrapper.monitor_mcp_session(session_name) as session_id:
        yield wrapper 