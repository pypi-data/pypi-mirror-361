"""
Agent Wrapper

High-level wrapper for monitoring AI agents with decorators, context managers,
and behavior analysis.
"""

import asyncio
import functools
import inspect
import time
import uuid
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Union, Generator, AsyncGenerator
from dataclasses import dataclass, field

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..core.event_registry import get_global_registry
from ..logging.structured_logger import SecurityLogger
from ..security.validators import InputValidator, ValidationResult


@dataclass
class AgentSession:
    """Agent monitoring session data"""
    session_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    method_calls: List[Dict[str, Any]] = field(default_factory=list)
    security_events: List[SecurityEvent] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MethodCallInfo:
    """Information about a monitored method call"""
    method_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    exception: Optional[Exception] = None
    security_validations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentWrapper:
    """
    Enterprise-grade agent wrapper for comprehensive monitoring
    
    Provides decorators and context managers for monitoring AI agent behavior,
    detecting security threats, and analyzing performance patterns.
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        enable_input_validation: bool = True,
        enable_behavior_analysis: bool = True,
        enable_performance_monitoring: bool = True,
        strict_validation: bool = False,
        max_session_duration: float = 3600.0  # 1 hour
    ):
        """
        Initialize agent wrapper
        
        Args:
            agent_id: Unique identifier for the agent
            logger: Security logger instance
            enable_input_validation: Enable input validation
            enable_behavior_analysis: Enable behavior analysis
            enable_performance_monitoring: Enable performance monitoring
            strict_validation: Use strict validation mode
            max_session_duration: Maximum session duration in seconds
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"agent_wrapper_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        
        # Configuration
        self.enable_input_validation = enable_input_validation
        self.enable_behavior_analysis = enable_behavior_analysis
        self.enable_performance_monitoring = enable_performance_monitoring
        self.strict_validation = strict_validation
        self.max_session_duration = max_session_duration
        
        # Initialize validators
        if self.enable_input_validation:
            self.input_validator = InputValidator(strict_mode=strict_validation)
        else:
            self.input_validator = None
        
        # Connect to global event registry
        self.global_registry = get_global_registry()
        
        # Active sessions tracking
        self.active_sessions: Dict[str, AgentSession] = {}
        self.current_session: Optional[AgentSession] = None
        
        # Global statistics
        self.stats = {
            'total_method_calls': 0,
            'total_sessions': 0,
            'security_events': 0,
            'validation_blocks': 0,
            'average_call_duration': 0.0,
            'threat_types_detected': {},
            'method_call_patterns': {}
        }
        
        self.logger.info(f"Agent wrapper initialized for {agent_id}", extra={
            'component': 'agent_wrapper',
            'agent_id': agent_id,
            'configuration': {
                'input_validation': enable_input_validation,
                'behavior_analysis': enable_behavior_analysis,
                'performance_monitoring': enable_performance_monitoring,
                'strict_validation': strict_validation
            }
        })

    def monitor(self, validate_inputs: bool = True, validate_outputs: bool = False):
        """
        Decorator for monitoring individual agent methods
        Args:
            validate_inputs: Whether to validate method inputs
            validate_outputs: Whether to validate method outputs
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_monitoring(
                    func, args, kwargs, validate_inputs, validate_outputs
                )
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_monitoring_async(
                    func, args, kwargs, validate_inputs, validate_outputs
                )
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        return decorator

    def _execute_with_monitoring(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: Dict[str, Any],
        validate_inputs: bool,
        validate_outputs: bool
    ) -> Any:
        """Execute function with comprehensive monitoring"""
        method_name = func.__name__
        call_info = MethodCallInfo(
            method_name=method_name,
            start_time=datetime.now(timezone.utc),
            args=self._sanitize_args(args),
            kwargs=self._sanitize_kwargs(kwargs)
        )
        
        try:
            # Input validation
            if validate_inputs and self.input_validator:
                self._validate_method_inputs(args, kwargs, call_info)
            
            # Execute method
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Output validation
            if validate_outputs and self.input_validator and isinstance(result, str):
                self._validate_method_output(result, call_info)
            
            # Record successful execution
            call_info.end_time = datetime.now(timezone.utc)
            call_info.duration = duration
            call_info.result = self._sanitize_result(result)
            
            self._record_method_call(call_info)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_performance(method_name, duration)
            
            return result
            
        except Exception as e:
            call_info.exception = e
            call_info.end_time = datetime.now(timezone.utc)
            call_info.duration = time.time() - time.mktime(call_info.start_time.timetuple())
            
            # Log security event for exceptions
            self.logger.security_event(
                f"Exception in monitored method {method_name}",
                threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                severity=SeverityLevel.MEDIUM,
                confidence=0.7,
                extra={
                    'method_name': method_name,
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'agent_id': self.agent_id
                }
            )
            
            self._record_method_call(call_info)
            raise

    async def _execute_with_monitoring_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_inputs: bool,
        validate_outputs: bool
    ) -> Any:
        """Execute async function with comprehensive monitoring"""
        method_name = func.__name__
        call_info = MethodCallInfo(
            method_name=method_name,
            start_time=datetime.now(timezone.utc),
            args=self._sanitize_args(args),
            kwargs=self._sanitize_kwargs(kwargs)
        )
        
        try:
            # Input validation
            if validate_inputs and self.input_validator:
                self._validate_method_inputs(args, kwargs, call_info)
            
            # Execute method
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Output validation
            if validate_outputs and self.input_validator and isinstance(result, str):
                self._validate_method_output(result, call_info)
            
            # Record successful execution
            call_info.end_time = datetime.now(timezone.utc)
            call_info.duration = duration
            call_info.result = self._sanitize_result(result)
            
            self._record_method_call(call_info)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_performance(method_name, duration)
            
            return result
            
        except Exception as e:
            call_info.exception = e
            call_info.end_time = datetime.now(timezone.utc)
            call_info.duration = time.time() - time.mktime(call_info.start_time.timetuple())
            
            # Log security event for exceptions
            self.logger.security_event(
                f"Exception in monitored async method {method_name}",
                threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                severity=SeverityLevel.MEDIUM,
                confidence=0.7,
                extra={
                    'method_name': method_name,
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'agent_id': self.agent_id
                }
            )
            
            self._record_method_call(call_info)
            raise

    def _validate_method_inputs(self, args: tuple, kwargs: Dict[str, Any], call_info: MethodCallInfo):
        """Validate method inputs for security threats"""
        validation_results = []
        
        if not self.input_validator:
            return
        
        # Validate string arguments
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                validation = self.input_validator.validate(arg)
                validation_results.append({
                    'type': 'arg',
                    'index': i,
                    'result': validation.result.value,
                    'is_safe': validation.is_safe,
                    'threat_type': validation.threat_type.value if validation.threat_type else None,
                    'violations': validation.violations
                })
                
                if not validation.is_safe and validation.threat_type:
                    # Create security event
                    event = SecurityEvent(
                        threat_type=validation.threat_type,
                        severity=SeverityLevel.HIGH,
                        message=f"Malicious input detected in method {call_info.method_name}",
                        confidence=validation.confidence_score,
                        context={
                            'method_name': call_info.method_name,
                            'argument_index': i,
                            'violations': validation.violations,
                            'input_sample': arg[:100] + '...' if len(arg) > 100 else arg
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
                    
                    # Register with global registry (THIS IS THE KEY FIX!)
                    self.global_registry.register_event(event)
                    
                    # Store in current session if available
                    if hasattr(self, 'current_session') and self.current_session:
                        self.current_session.security_events.append(event)
                    
                    # Update stats
                    self.stats['security_events'] += 1
                    self.stats['validation_blocks'] += 1
                    
                    threat_type_name = validation.threat_type.value
                    current_count = self.stats['threat_types_detected'].get(threat_type_name, 0)
                    self.stats['threat_types_detected'][threat_type_name] = current_count + 1
        
        # Validate keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, str):
                validation = self.input_validator.validate(value)
                validation_results.append({
                    'type': 'kwarg',
                    'key': key,
                    'result': validation.result.value,
                    'is_safe': validation.is_safe,
                    'threat_type': validation.threat_type.value if validation.threat_type else None,
                    'violations': validation.violations
                })
                
                if not validation.is_safe and validation.threat_type:
                    # Create security event for kwargs
                    event = SecurityEvent(
                        threat_type=validation.threat_type,
                        severity=SeverityLevel.HIGH,
                        message=f"Malicious input detected in method {call_info.method_name}",
                        confidence=validation.confidence_score,
                        context={
                            'method_name': call_info.method_name,
                            'argument_name': key,
                            'violations': validation.violations,
                            'input_sample': value[:100] + '...' if len(value) > 100 else value
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
        
        call_info.security_validations = validation_results

    def _validate_method_output(self, result: str, call_info: MethodCallInfo):
        """Validate method output for security threats"""
        if self.input_validator:
            validation = self.input_validator.validate(result)
            
            if not validation.is_safe:
                self.logger.security_event(
                    f"Potentially malicious output from method {call_info.method_name}",
                    threat_type=validation.threat_type,
                    severity=SeverityLevel.MEDIUM,
                    confidence=validation.confidence_score,
                    extra={
                        'method_name': call_info.method_name,
                        'output_sample': result[:200] + '...' if len(result) > 200 else result,
                        'violations': validation.violations
                    }
                )

    def _record_method_call(self, call_info: MethodCallInfo):
        """Record method call information"""
        self.stats['total_method_calls'] += 1
        
        # Update method call patterns
        method_name = call_info.method_name
        current_count = self.stats['method_call_patterns'].get(method_name, 0)
        self.stats['method_call_patterns'][method_name] = current_count + 1
        
        # Update average call duration
        if call_info.duration:
            total_calls = self.stats['total_method_calls']
            current_avg = self.stats['average_call_duration']
            self.stats['average_call_duration'] = (
                (current_avg * (total_calls - 1) + call_info.duration) / total_calls
            )
        
        # Add to active sessions
        for session in self.active_sessions.values():
            session.method_calls.append({
                'method_name': call_info.method_name,
                'start_time': call_info.start_time.isoformat(),
                'end_time': call_info.end_time.isoformat() if call_info.end_time else None,
                'duration': call_info.duration,
                'success': call_info.exception is None,
                'security_validations': call_info.security_validations
            })

    def _analyze_performance(self, method_name: str, duration: float):
        """Analyze method performance for anomalies"""
        # Simple performance anomaly detection
        avg_duration = self.stats.get('average_call_duration', 0.0)
        
        if avg_duration > 0 and duration > avg_duration * 5:  # 5x slower than average
            self.logger.warning(
                f"Performance anomaly detected in method {method_name}",
                extra={
                    'method_name': method_name,
                    'duration': duration,
                    'average_duration': avg_duration,
                    'anomaly_factor': duration / avg_duration,
                    'agent_id': self.agent_id,
                    'is_performance_anomaly': True
                }
            )

    def _sanitize_args(self, args: tuple) -> tuple:
        """Sanitize arguments for logging"""
        return tuple(
            '[REDACTED]' if self._is_sensitive_data(arg) else str(arg)[:100]
            for arg in args
        )

    def _sanitize_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize keyword arguments for logging"""
        return {
            key: '[REDACTED]' if self._is_sensitive_data(value) else str(value)[:100]
            for key, value in kwargs.items()
        }

    def _sanitize_result(self, result: Any) -> Any:
        """Sanitize result for logging"""
        if self._is_sensitive_data(result):
            return '[REDACTED]'
        elif isinstance(result, str) and len(result) > 200:
            return result[:200] + '...'
        else:
            return result

    def _is_sensitive_data(self, data: Any) -> bool:
        """Check if data contains sensitive information"""
        if not isinstance(data, str):
            return False
        
        sensitive_keywords = ['password', 'token', 'key', 'secret', 'credential', 'auth']
        data_lower = str(data).lower()
        
        return any(keyword in data_lower for keyword in sensitive_keywords)

    @contextmanager
    def monitor_session(self, session_name: Optional[str] = None) -> Generator[str, None, None]:
        """Context manager for monitoring agent sessions"""
        session_id = str(uuid.uuid4())
        session_name = session_name or f"session_{session_id[:8]}"
        
        session = AgentSession(
            session_id=session_id,
            agent_id=self.agent_id,
            start_time=datetime.now(timezone.utc)
        )
        
        self.active_sessions[session_id] = session
        # Set as current session for event storage
        old_session = self.current_session
        self.current_session = session
        
        self.logger.info(f"Started monitoring session {session_name}", extra={
            'session_id': session_id,
            'session_name': session_name,
            'agent_id': self.agent_id,
            'component': 'agent_wrapper'
        })
        
        try:
            yield session_id
        finally:
            # Restore previous session
            self.current_session = old_session
            session.end_time = datetime.now(timezone.utc)
            
            # Calculate session metrics
            duration = (session.end_time - session.start_time).total_seconds()
            session.performance_metrics = {
                'duration': duration,
                'method_calls': len(session.method_calls),
                'security_events': len(session.security_events)
            }
            
            self.logger.info(f"Ended monitoring session {session_name}", extra={
                'session_id': session_id,
                'session_name': session_name,
                'duration': duration,
                'method_calls': len(session.method_calls),
                'security_events': len(session.security_events),
                'agent_id': self.agent_id
            })
            
            # Remove from active sessions
            self.active_sessions.pop(session_id, None)
            self.stats['total_sessions'] += 1

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics"""
        return {
            'agent_id': self.agent_id,
            'active_sessions': len(self.active_sessions),
            'stats': self.stats.copy(),
            'configuration': {
                'input_validation': self.enable_input_validation,
                'behavior_analysis': self.enable_behavior_analysis,
                'performance_monitoring': self.enable_performance_monitoring,
                'strict_validation': self.strict_validation
            },
            'validator_stats': self.input_validator.get_stats() if self.input_validator else None
        }

    def get_session_info(self, session_id: str) -> Optional[AgentSession]:
        """Get information about a specific session"""
        return self.active_sessions.get(session_id)


# Convenience decorators and functions
def sentinel(
    agent_id: Optional[str] = None,
    enable_input_validation: bool = True,
    strict_validation: bool = False,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to monitor an entire agent class
    Usage:
        @sentinel(agent_id="my_agent")
        class MyAgent:
            def process_data(self, data: str) -> str:
                return data.upper()
    """
    def decorator(cls):
        wrapper_instance = AgentWrapper(
            agent_id=agent_id or cls.__name__,
            logger=logger,
            enable_input_validation=enable_input_validation,
            strict_validation=strict_validation
        )
        for attr_name in dir(cls):
            if not attr_name.startswith('_'):
                attr = getattr(cls, attr_name)
                if callable(attr):
                    wrapped_method = wrapper_instance.monitor()(attr)
                    setattr(cls, attr_name, wrapped_method)
        cls._agent_wrapper = wrapper_instance
        return cls
    return decorator


@contextmanager
def monitor_agent_session(
    agent_id: str,
    session_name: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Generator[AgentWrapper, None, None]:
    """
    Context manager for monitoring agent sessions
    
    Usage:
        with monitor_agent_session("my_agent") as wrapper:
            result = my_function()
    """
    wrapper = AgentWrapper(agent_id=agent_id, logger=logger)
    
    with wrapper.monitor_session(session_name) as session_id:
        yield wrapper 