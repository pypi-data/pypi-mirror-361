"""
Agent Wrapper

High-level wrapper for monitoring AI agents with decorators, context managers,
and behavior analysis.
"""

import asyncio
import functools
import inspect
import threading
import time
import uuid
import weakref
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timezone, timedelta
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


@dataclass
class ConfigurationValidation:
    """Configuration validation results"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]


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
        max_session_duration: float = 3600.0,  # 1 hour
        max_concurrent_sessions: int = 100,
        session_cleanup_interval: float = 300.0,  # 5 minutes
        memory_threshold_mb: int = 512
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
            max_concurrent_sessions: Maximum concurrent sessions
            session_cleanup_interval: Session cleanup interval in seconds
            memory_threshold_mb: Memory threshold for cleanup in MB
        """
        self.agent_id = agent_id
        
        # Thread safety
        self._lock = threading.RLock()
        self._session_lock = threading.Lock()
        
        # Configuration
        self.enable_input_validation = enable_input_validation
        self.enable_behavior_analysis = enable_behavior_analysis
        self.enable_performance_monitoring = enable_performance_monitoring
        self.strict_validation = strict_validation
        self.max_session_duration = max_session_duration
        self.max_concurrent_sessions = max_concurrent_sessions
        self.session_cleanup_interval = session_cleanup_interval
        self.memory_threshold_mb = memory_threshold_mb
        
        # Validate configuration
        config_validation = self._validate_configuration()
        if not config_validation.is_valid:
            raise ValueError(f"Invalid configuration: {config_validation.issues}")
        
        # Configure log file path
        log_file = f"logs/agent_sentinel_{agent_id}.log"
        
        self.logger = logger or SecurityLogger(
            name=f"agent_wrapper_{agent_id}",
            agent_id=agent_id,
            json_format=True,
            log_file=log_file
        )
        
        # Initialize validators
        if self.enable_input_validation:
            self.input_validator = InputValidator(strict_mode=strict_validation)
        else:
            self.input_validator = None
        
        # Connect to global event registry
        self.global_registry = get_global_registry()
        
        # Active sessions tracking with thread safety
        self.active_sessions: Dict[str, AgentSession] = {}
        self.current_session: Optional[AgentSession] = None
        self._last_cleanup_time = datetime.now(timezone.utc)
        
        # Global statistics with thread safety
        self.stats = {
            'total_method_calls': 0,
            'total_sessions': 0,
            'security_events': 0,
            'validation_blocks': 0,
            'average_call_duration': 0.0,
            'threat_types_detected': {},
            'method_call_patterns': {},
            'memory_usage_mb': 0.0,
            'cleanup_cycles': 0,
            'errors_handled': 0
        }
        
        # Error handling statistics
        self.error_stats = {
            'memory_errors': 0,
            'timeout_errors': 0,
            'validation_errors': 0,
            'serialization_errors': 0,
            'other_errors': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = None
        self._cleanup_running = False
        self._start_cleanup_thread()
        
        self.logger.info(f"Agent wrapper initialized for {agent_id}", extra={
            'component': 'agent_wrapper',
            'agent_id': agent_id,
            'configuration': {
                'input_validation': enable_input_validation,
                'behavior_analysis': enable_behavior_analysis,
                'performance_monitoring': enable_performance_monitoring,
                'strict_validation': strict_validation,
                'max_session_duration': max_session_duration,
                'max_concurrent_sessions': max_concurrent_sessions,
                'session_cleanup_interval': session_cleanup_interval,
                'memory_threshold_mb': memory_threshold_mb
            },
            'validation': config_validation.__dict__
        })

    def _validate_configuration(self) -> ConfigurationValidation:
        """Validate configuration for potential issues"""
        issues = []
        warnings = []
        recommendations = []
        
        # Critical validation - these should cause failures
        if self.max_session_duration <= 0:
            issues.append("Session duration must be positive (>0)")
        elif self.max_session_duration > 86400:  # 24 hours
            issues.append("Session duration too long (>24 hours) - may cause memory issues")
        elif self.max_session_duration > 3600:  # 1 hour
            warnings.append("Long session duration (>1 hour) - monitor memory usage")
        
        if self.max_concurrent_sessions <= 0:
            issues.append("Concurrent sessions must be positive (>0)")
        elif self.max_concurrent_sessions > 1000:
            issues.append("Too many concurrent sessions (>1000) - may cause resource exhaustion")
        elif self.max_concurrent_sessions > 100:
            warnings.append("High concurrent sessions (>100) - monitor performance")
        
        if self.session_cleanup_interval <= 0:
            issues.append("Cleanup interval must be positive (>0)")
        elif self.session_cleanup_interval < 60:  # 1 minute
            warnings.append("Frequent cleanup interval (<1 minute) - may impact performance")
        elif self.session_cleanup_interval > 1800:  # 30 minutes
            warnings.append("Infrequent cleanup interval (>30 minutes) - may cause memory buildup")
        
        if self.memory_threshold_mb <= 0:
            issues.append("Memory threshold must be positive (>0)")
        elif self.memory_threshold_mb < 100:
            warnings.append("Low memory threshold (<100MB) - may trigger frequent cleanups")
        elif self.memory_threshold_mb > 2048:
            warnings.append("High memory threshold (>2GB) - may allow memory buildup")
        
        # Type validation for boolean flags
        if not isinstance(self.enable_input_validation, bool):
            issues.append("enable_input_validation must be a boolean")
        if not isinstance(self.enable_behavior_analysis, bool):
            issues.append("enable_behavior_analysis must be a boolean")
        if not isinstance(self.enable_performance_monitoring, bool):
            issues.append("enable_performance_monitoring must be a boolean")
        if not isinstance(self.strict_validation, bool):
            issues.append("strict_validation must be a boolean")
        
        # Agent ID validation
        if not self.agent_id or not isinstance(self.agent_id, str):
            issues.append("agent_id must be a non-empty string")
        elif len(self.agent_id) > 100:
            issues.append("agent_id too long (>100 characters)")
        
        # Recommendations
        if not issues and not warnings:
            recommendations.append("Configuration looks optimal for production use")
        else:
            recommendations.append("Consider adjusting configuration based on your use case")
            if warnings:
                recommendations.append("Monitor system performance and adjust as needed")
        
        return ConfigurationValidation(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations
        )

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_running = True
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name=f"cleanup-{self.agent_id}"
            )
            self._cleanup_thread.start()

    def _cleanup_worker(self):
        """Background worker for session cleanup"""
        while self._cleanup_running:
            try:
                time.sleep(self.session_cleanup_interval)
                self.cleanup_old_sessions()
                self._check_memory_usage()
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}", extra={
                    'component': 'cleanup_worker',
                    'agent_id': self.agent_id,
                    'error_type': type(e).__name__
                })

    def cleanup_old_sessions(self, max_age_hours: Optional[int] = None):
        """Clean up old sessions to prevent memory leaks"""
        if max_age_hours is None:
            max_age_hours = int(self.max_session_duration / 3600)
        
        with self._session_lock:
            current_time = datetime.now(timezone.utc)
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                if (current_time - session.start_time).total_seconds() > max_age_hours * 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                self.stats['cleanup_cycles'] += 1
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions", extra={
                    'component': 'cleanup',
                    'agent_id': self.agent_id,
                    'expired_sessions': len(expired_sessions),
                    'remaining_sessions': len(self.active_sessions)
                })

    def _check_memory_usage(self):
        """Check memory usage and trigger cleanup if needed"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.stats['memory_usage_mb'] = memory_mb
            
            if memory_mb > self.memory_threshold_mb:
                self.logger.warning(f"Memory usage {memory_mb:.1f}MB exceeds threshold {self.memory_threshold_mb}MB", extra={
                    'component': 'memory_check',
                    'agent_id': self.agent_id,
                    'memory_mb': memory_mb,
                    'threshold_mb': self.memory_threshold_mb
                })
                # Force cleanup
                self.cleanup_old_sessions(max_age_hours=1)
        except ImportError:
            # psutil not available, skip memory check
            pass
        except Exception as e:
            self.logger.error(f"Memory check error: {e}", extra={
                'component': 'memory_check',
                'agent_id': self.agent_id,
                'error_type': type(e).__name__
            })

    def _handle_memory_error(self):
        """Handle memory errors gracefully"""
        self.error_stats['memory_errors'] += 1
        self.stats['errors_handled'] += 1
        
        # Force cleanup
        self.cleanup_old_sessions(max_age_hours=1)
        
        self.logger.error("Memory error detected - performed emergency cleanup", extra={
            'component': 'error_handler',
            'agent_id': self.agent_id,
            'error_type': 'MemoryError',
            'cleanup_performed': True
        })

    def _handle_timeout_error(self):
        """Handle timeout errors gracefully"""
        self.error_stats['timeout_errors'] += 1
        self.stats['errors_handled'] += 1
        
        self.logger.warning("Timeout error detected", extra={
            'component': 'error_handler',
            'agent_id': self.agent_id,
            'error_type': 'TimeoutError'
        })

    def _handle_serialization_error(self):
        """Handle serialization errors gracefully"""
        self.error_stats['serialization_errors'] += 1
        self.stats['errors_handled'] += 1
        
        self.logger.warning("Serialization error detected - using fallback serialization", extra={
            'component': 'error_handler',
            'agent_id': self.agent_id,
            'error_type': 'SerializationError'
        })

    def _handle_generic_error(self, error: Exception):
        """Handle generic errors gracefully"""
        self.error_stats['other_errors'] += 1
        self.stats['errors_handled'] += 1
        
        self.logger.error(f"Generic error handled: {type(error).__name__}", extra={
            'component': 'error_handler',
            'agent_id': self.agent_id,
            'error_type': type(error).__name__,
            'error_message': str(error)
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
        """Execute function with comprehensive monitoring and error handling"""
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
            
            with self._lock:
                self._record_method_call(call_info)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_performance(method_name, duration)
            
            return result
            
        except MemoryError as e:
            self._handle_memory_error()
            raise
        except TimeoutError as e:
            self._handle_timeout_error()
            raise
        except (TypeError, ValueError) as e:
            # Likely serialization error
            self._handle_serialization_error()
            raise
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
            
            with self._lock:
                self._record_method_call(call_info)
            
            self._handle_generic_error(e)
            raise

    async def _execute_with_monitoring_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_inputs: bool,
        validate_outputs: bool
    ) -> Any:
        """Execute async function with comprehensive monitoring and error handling"""
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
            
            with self._lock:
                self._record_method_call(call_info)
            
            # Performance monitoring
            if self.enable_performance_monitoring:
                self._analyze_performance(method_name, duration)
            
            return result
            
        except MemoryError as e:
            self._handle_memory_error()
            raise
        except TimeoutError as e:
            self._handle_timeout_error()
            raise
        except (TypeError, ValueError) as e:
            # Likely serialization error
            self._handle_serialization_error()
            raise
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
            
            with self._lock:
                self._record_method_call(call_info)
            
            self._handle_generic_error(e)
            raise

    def _validate_method_inputs(self, args: tuple, kwargs: Dict[str, Any], call_info: MethodCallInfo):
        """Validate method inputs for security threats with thread safety"""
        validation_results = []
        
        if not self.input_validator:
            return
        
        # Validate string arguments
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                try:
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
                        
                        # Register with global registry
                        self.global_registry.register_event(event)
                        
                        # Store in current session if available
                        if hasattr(self, 'current_session') and self.current_session:
                            self.current_session.security_events.append(event)
                        
                        # Update stats with thread safety
                        with self._lock:
                            self.stats['security_events'] += 1
                            self.stats['validation_blocks'] += 1
                            
                            threat_type_name = validation.threat_type.value
                            current_count = self.stats['threat_types_detected'].get(threat_type_name, 0)
                            self.stats['threat_types_detected'][threat_type_name] = current_count + 1
                            
                except Exception as e:
                    self.error_stats['validation_errors'] += 1
                    self.logger.error(f"Validation error for argument {i}: {e}", extra={
                        'component': 'validation',
                        'agent_id': self.agent_id,
                        'error_type': type(e).__name__
                    })
        
        # Validate keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, str):
                try:
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
                        
                        # Register with global registry
                        self.global_registry.register_event(event)
                        
                        # Store in current session if available
                        if hasattr(self, 'current_session') and self.current_session:
                            self.current_session.security_events.append(event)
                        
                        # Update stats with thread safety
                        with self._lock:
                            self.stats['security_events'] += 1
                            self.stats['validation_blocks'] += 1
                            
                            threat_type_name = validation.threat_type.value
                            current_count = self.stats['threat_types_detected'].get(threat_type_name, 0)
                            self.stats['threat_types_detected'][threat_type_name] = current_count + 1
                            
                except Exception as e:
                    self.error_stats['validation_errors'] += 1
                    self.logger.error(f"Validation error for kwarg {key}: {e}", extra={
                        'component': 'validation',
                        'agent_id': self.agent_id,
                        'error_type': type(e).__name__
                    })
        
        call_info.security_validations = validation_results

    def _validate_method_output(self, result: str, call_info: MethodCallInfo):
        """Validate method output for security threats"""
        if not self.input_validator:
            return
        
        try:
            validation = self.input_validator.validate(result)
            
            if not validation.is_safe and validation.threat_type:
                # Create security event for output
                event = SecurityEvent(
                    threat_type=validation.threat_type,
                    severity=SeverityLevel.HIGH,
                    message=f"Malicious output detected in method {call_info.method_name}",
                    confidence=validation.confidence_score,
                    context={
                        'method_name': call_info.method_name,
                        'violations': validation.violations,
                        'output_sample': result[:100] + '...' if len(result) > 100 else result
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
                
                # Register with global registry
                self.global_registry.register_event(event)
                
                # Store in current session if available
                if hasattr(self, 'current_session') and self.current_session:
                    self.current_session.security_events.append(event)
                
                # Update stats with thread safety
                with self._lock:
                    self.stats['security_events'] += 1
                    self.stats['validation_blocks'] += 1
                    
                    threat_type_name = validation.threat_type.value
                    current_count = self.stats['threat_types_detected'].get(threat_type_name, 0)
                    self.stats['threat_types_detected'][threat_type_name] = current_count + 1
                    
        except Exception as e:
            self.error_stats['validation_errors'] += 1
            self.logger.error(f"Output validation error: {e}", extra={
                'component': 'validation',
                'agent_id': self.agent_id,
                'error_type': type(e).__name__
            })

    def _record_method_call(self, call_info: MethodCallInfo):
        """Record method call with thread safety"""
        # Update global stats
        self.stats['total_method_calls'] += 1
        
        # Update average call duration
        total_calls = self.stats['total_method_calls']
        current_avg = self.stats['average_call_duration']
        if call_info.duration is not None:
            self.stats['average_call_duration'] = (
                (current_avg * (total_calls - 1) + call_info.duration) / total_calls
            )
        
        # Update method call patterns
        method_name = call_info.method_name
        if method_name not in self.stats['method_call_patterns']:
            self.stats['method_call_patterns'][method_name] = {
                'total_calls': 0,
                'total_duration': 0.0,
                'average_duration': 0.0,
                'errors': 0
            }
        
        pattern = self.stats['method_call_patterns'][method_name]
        pattern['total_calls'] += 1
        if call_info.duration is not None:
            pattern['total_duration'] += call_info.duration
            pattern['average_duration'] = pattern['total_duration'] / pattern['total_calls']
        
        if call_info.exception:
            pattern['errors'] += 1
        
        # Store in current session if available
        if hasattr(self, 'current_session') and self.current_session:
            self.current_session.method_calls.append({
                'method_name': call_info.method_name,
                'start_time': call_info.start_time.isoformat(),
                'end_time': call_info.end_time.isoformat() if call_info.end_time else None,
                'duration': call_info.duration,
                'has_exception': call_info.exception is not None,
                'exception_type': type(call_info.exception).__name__ if call_info.exception else None
            })

    def _analyze_performance(self, method_name: str, duration: float):
        """Analyze method performance with thread safety"""
        with self._lock:
            if method_name not in self.stats['method_call_patterns']:
                self.stats['method_call_patterns'][method_name] = {
                    'total_calls': 0,
                    'total_duration': 0.0,
                    'average_duration': 0.0,
                    'errors': 0
                }
            
            pattern = self.stats['method_call_patterns'][method_name]
            pattern['total_calls'] += 1
            pattern['total_duration'] += duration
            pattern['average_duration'] = pattern['total_duration'] / pattern['total_calls']

    def _sanitize_args(self, args: tuple) -> tuple:
        """Safely sanitize arguments for logging"""
        try:
            return tuple(self._safe_serialize(arg) for arg in args)
        except Exception:
            return tuple(f"<{type(arg).__name__}>" for arg in args)

    def _sanitize_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Safely sanitize keyword arguments for logging"""
        try:
            return {key: self._safe_serialize(value) for key, value in kwargs.items()}
        except Exception:
            return {key: f"<{type(value).__name__}>" for key, value in kwargs.items()}

    def _sanitize_result(self, result: Any) -> Any:
        """Safely sanitize result for logging"""
        try:
            return self._safe_serialize(result)
        except Exception:
            return f"<{type(result).__name__}>"

    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize objects for logging"""
        try:
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [self._safe_serialize(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: self._safe_serialize(value) for key, value in obj.items()}
            elif hasattr(obj, '__dict__'):
                # Try to serialize object attributes
                try:
                    return {key: self._safe_serialize(value) for key, value in obj.__dict__.items()}
                except Exception:
                    return f"<{type(obj).__name__}>"
            else:
                return f"<{type(obj).__name__}>"
        except Exception:
            return f"<{type(obj).__name__}>"

    def _is_sensitive_data(self, data: Any) -> bool:
        """Check if data contains sensitive information"""
        if isinstance(data, str):
            sensitive_patterns = [
                'password', 'token', 'key', 'secret', 'credential',
                'api_key', 'private_key', 'access_token'
            ]
            data_lower = data.lower()
            return any(pattern in data_lower for pattern in sensitive_patterns)
        return False

    @contextmanager
    def monitor_session(self, session_name: Optional[str] = None) -> Generator[str, None, None]:
        """Context manager for monitoring agent sessions with thread safety"""
        session_id = f"{self.agent_id}_{uuid.uuid4().hex[:8]}"
        session = AgentSession(
            session_id=session_id,
            agent_id=self.agent_id,
            start_time=datetime.now(timezone.utc),
            metadata={'session_name': session_name}
        )
        
        # Check concurrent session limit
        with self._session_lock:
            if len(self.active_sessions) >= self.max_concurrent_sessions:
                raise RuntimeError(f"Maximum concurrent sessions ({self.max_concurrent_sessions}) exceeded")
            
            self.active_sessions[session_id] = session
            self.current_session = session
            self.stats['total_sessions'] += 1
        
        try:
            yield session_id
        finally:
            # Clean up session
            session.end_time = datetime.now(timezone.utc)
            with self._session_lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics with thread safety"""
        with self._lock:
            stats_copy = self.stats.copy()
            stats_copy['error_stats'] = self.error_stats.copy()
            stats_copy['active_sessions_count'] = len(self.active_sessions)
            stats_copy['cleanup_thread_alive'] = self._cleanup_thread.is_alive() if self._cleanup_thread else False
            return stats_copy

    def get_session_info(self, session_id: str) -> Optional[AgentSession]:
        """Get session information with thread safety"""
        with self._session_lock:
            return self.active_sessions.get(session_id)

    def shutdown(self):
        """Gracefully shutdown the agent wrapper"""
        self._cleanup_running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)
        
        # Clean up all sessions
        self.cleanup_old_sessions(max_age_hours=0)
        
        self.logger.info(f"Agent wrapper shutdown for {self.agent_id}", extra={
            'component': 'shutdown',
            'agent_id': self.agent_id
        })

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.shutdown()
        except Exception:
            pass


def sentinel(
    agent_id: Optional[str] = None,
    enable_input_validation: bool = True,
    strict_validation: bool = False,
    logger: Optional[SecurityLogger] = None
) -> Callable:
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
    def decorator(cls):
        # Create wrapper instance
        wrapper_instance = AgentWrapper(
            agent_id=agent_id or cls.__name__,
            logger=logger,
            enable_input_validation=enable_input_validation,
            strict_validation=strict_validation,
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
        setattr(cls, 'shutdown', lambda self: wrapper_instance.shutdown())
        
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
    
    # Ensure cleanup
    wrapper.shutdown()


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
            self.wrapper.shutdown()


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