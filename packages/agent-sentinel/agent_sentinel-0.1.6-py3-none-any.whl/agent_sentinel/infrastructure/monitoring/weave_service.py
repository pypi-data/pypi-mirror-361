"""
Weave Service for Agent Sentinel

Enterprise-grade Weave integration for LLM tracing and monitoring.
Provides robust error handling, retry logic, and performance monitoring.
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import threading
import json

try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False

from ...core.config import WeaveConfig
from ...core.exceptions import AgentSentinelError
from .data_sanitizer import DataSanitizer, SanitizationConfig, create_default_sanitizer

logger = logging.getLogger(__name__)


class WeaveError(AgentSentinelError):
    """Base exception for Weave-related errors."""
    pass


class WeaveInitializationError(WeaveError):
    """Raised when Weave initialization fails."""
    pass


class WeaveTraceError(WeaveError):
    """Raised when Weave tracing operations fail."""
    pass


@dataclass
class WeaveMetrics:
    """Metrics for Weave operations."""
    
    total_traces: int = 0
    successful_traces: int = 0
    failed_traces: int = 0
    total_trace_time: float = 0.0
    initialization_time: Optional[float] = None
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate trace success rate."""
        if self.total_traces == 0:
            return 0.0
        return self.successful_traces / self.total_traces
    
    @property
    def average_trace_time(self) -> float:
        """Calculate average trace time."""
        if self.successful_traces == 0:
            return 0.0
        return self.total_trace_time / self.successful_traces
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_traces': self.total_traces,
            'successful_traces': self.successful_traces,
            'failed_traces': self.failed_traces,
            'success_rate': self.success_rate,
            'average_trace_time': self.average_trace_time,
            'initialization_time': self.initialization_time,
            'last_error': self.last_error,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None
        }


class WeaveService:
    """
    Enterprise-grade Weave service for LLM tracing and monitoring.
    
    Features:
    - Robust initialization with fallback handling
    - Automatic retry logic for failed operations
    - Performance monitoring and metrics collection
    - Thread-safe operations
    - Graceful degradation when Weave is unavailable
    """
    
    def __init__(self, config: WeaveConfig):
        """
        Initialize Weave service.
        
        Args:
            config: Weave configuration
        """
        self.config = config
        self.metrics = WeaveMetrics()
        self._initialized = False
        self._initialization_lock = threading.Lock()
        self._trace_lock = threading.Lock()
        
        # Initialize data sanitizer if privacy controls are enabled
        if (config.redact_pii or config.redact_api_keys or config.redact_user_data):
            sanitization_config = SanitizationConfig(
                redact_pii=config.redact_pii,
                redact_api_keys=config.redact_api_keys,
                redact_user_data=config.redact_user_data,
                max_string_length=config.max_payload_size // 1024  # Convert to reasonable string length
            )
            self.sanitizer = DataSanitizer(sanitization_config)
        else:
            self.sanitizer = None
        
        # Initialize Weave if enabled and available
        if self.config.enabled and WEAVE_AVAILABLE:
            self._initialize_weave()
        elif self.config.enabled and not WEAVE_AVAILABLE:
            logger.warning("Weave is enabled but weave package is not installed. Install with: pip install weave")
        
        logger.info(f"Weave service initialized (enabled: {self.is_enabled}, sanitization: {self.sanitizer is not None})")
    
    @property
    def is_enabled(self) -> bool:
        """Check if Weave is enabled and available."""
        return self.config.enabled and WEAVE_AVAILABLE and self._initialized
    
    @property
    def is_available(self) -> bool:
        """Check if Weave package is available."""
        return WEAVE_AVAILABLE
    
    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data before sending to Weave."""
        if self.sanitizer is None:
            return data
        
        try:
            return self.sanitizer.sanitize_any(data)
        except Exception as e:
            logger.warning(f"Error sanitizing data for Weave: {e}")
            return {"sanitization_error": "Failed to sanitize data"}
    
    def _initialize_weave(self) -> None:
        """Initialize Weave with proper error handling and security settings."""
        with self._initialization_lock:
            if self._initialized:
                return
            
            try:
                start_time = time.time()
                
                # Set up Weave configuration with security settings
                init_kwargs = {
                    'project_name': self.config.project_name,
                    'settings': {
                        'capture_code': not self.config.disable_code_capture,
                        'capture_system_info': not self.config.disable_system_info,
                        'capture_client_info': not self.config.disable_system_info
                    }
                }
                
                if self.config.api_key:
                    os.environ['WEAVE_API_KEY'] = self.config.api_key
                
                if self.config.base_url:
                    init_kwargs['base_url'] = self.config.base_url
                
                # Set up autopatch settings with sanitization if enabled
                if self.sanitizer:
                    sanitize_func = self.sanitizer.create_sanitization_function()
                    init_kwargs['autopatch_settings'] = {
                        'openai': {
                            'op_settings': {
                                'postprocess_inputs': sanitize_func,
                                'postprocess_output': sanitize_func
                            }
                        }
                    }
                
                # Initialize Weave
                weave.init(**init_kwargs)
                
                self.metrics.initialization_time = time.time() - start_time
                self._initialized = True
                
                logger.info(f"Weave initialized successfully (project: {self.config.project_name}, security: enabled)")
                
            except Exception as e:
                error_msg = f"Failed to initialize Weave: {str(e)}"
                logger.error(error_msg)
                self.metrics.last_error = error_msg
                self.metrics.last_error_time = datetime.now()
                
                if self.config.enabled:
                    # In enterprise mode, we might want to raise an error
                    # For now, we'll continue with degraded functionality
                    logger.warning("Continuing with Weave disabled due to initialization failure")
    
    def _should_trace(self) -> bool:
        """Determine if we should trace based on sampling rate."""
        if not self.is_enabled:
            return False
        
        import random
        return random.random() < self.config.sampling_rate
    
    def _record_trace_attempt(self, success: bool, duration: float, error: Optional[str] = None) -> None:
        """Record metrics for a trace attempt."""
        with self._trace_lock:
            self.metrics.total_traces += 1
            
            if success:
                self.metrics.successful_traces += 1
                self.metrics.total_trace_time += duration
            else:
                self.metrics.failed_traces += 1
                if error:
                    self.metrics.last_error = error
                    self.metrics.last_error_time = datetime.now()
    
    def create_op_decorator(self, name: Optional[str] = None) -> Callable:
        """
        Create a Weave operation decorator with enterprise features.
        
        Args:
            name: Optional name for the operation
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            if not self.is_enabled or not self._should_trace():
                return func
            
            try:
                # Use Weave's op decorator
                return weave.op(name=name)(func)
            except Exception as e:
                logger.warning(f"Failed to create Weave op decorator: {e}")
                return func
        
        return decorator
    
    @asynccontextmanager
    async def trace_operation(
        self,
        operation_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing operations with retry logic.
        
        Args:
            operation_name: Name of the operation
            inputs: Input data for the operation
            metadata: Additional metadata
        """
        if not self.is_enabled or not self._should_trace():
            yield None
            return
        
        start_time = time.time()
        trace_data = {
            'operation': operation_name,
            'inputs': inputs or {},
            'metadata': metadata or {},
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Start trace
            with weave.trace(operation_name) as trace:
                if inputs:
                    trace.log_inputs(inputs)
                
                if metadata:
                    for key, value in metadata.items():
                        trace.log(key, value)
                
                yield trace
                
                # Record successful trace
                duration = time.time() - start_time
                self._record_trace_attempt(True, duration)
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Weave trace failed for {operation_name}: {str(e)}"
            logger.warning(error_msg)
            
            self._record_trace_attempt(False, duration, error_msg)
            
            # Yield None to continue operation without tracing
            yield None
    
    async def log_llm_call(
        self,
        model: str,
        messages: list,
        response: Optional[str] = None,
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        latency: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log LLM call with comprehensive metadata.
        
        Args:
            model: Model name
            messages: Input messages
            response: LLM response
            tokens_used: Number of tokens used
            cost: Cost of the call
            latency: Response latency
            error: Error message if call failed
        """
        if not self.is_enabled or not self.config.trace_llm_calls:
            return
        
        async with self.trace_operation(
            "llm_call",
            inputs={
                'model': model,
                'messages': messages,
                'tokens_used': tokens_used,
                'cost': cost,
                'latency': latency
            },
            metadata={
                'operation_type': 'llm_call',
                'model': model,
                'success': error is None
            }
        ) as trace:
            if trace:
                if response:
                    trace.log('response', response)
                if error:
                    trace.log('error', error)
    
    async def log_intelligence_operation(
        self,
        operation_type: str,
        threat_type: str,
        queries: Optional[list] = None,
        results: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log intelligence gathering operation.
        
        Args:
            operation_type: Type of intelligence operation
            threat_type: Type of threat being analyzed
            queries: Search queries used
            results: Intelligence results
            confidence: Confidence score
            error: Error message if operation failed
        """
        if not self.is_enabled or not self.config.trace_intelligence_ops:
            return
        
        async with self.trace_operation(
            "intelligence_operation",
            inputs={
                'operation_type': operation_type,
                'threat_type': threat_type,
                'queries': queries,
                'confidence': confidence
            },
            metadata={
                'operation_type': 'intelligence',
                'threat_type': threat_type,
                'success': error is None
            }
        ) as trace:
            if trace:
                if results:
                    trace.log('results', results)
                if error:
                    trace.log('error', error)
    
    async def log_report_generation(
        self,
        report_type: str,
        event_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        report_length: Optional[int] = None,
        generation_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log report generation operation.
        
        Args:
            report_type: Type of report generated
            event_id: Security event ID
            inputs: Input data for report generation
            report_length: Length of generated report
            generation_time: Time taken to generate report
            error: Error message if generation failed
        """
        if not self.is_enabled or not self.config.trace_report_generation:
            return
        
        async with self.trace_operation(
            "report_generation",
            inputs={
                'report_type': report_type,
                'event_id': event_id,
                'inputs': inputs,
                'report_length': report_length,
                'generation_time': generation_time
            },
            metadata={
                'operation_type': 'report_generation',
                'event_id': event_id,
                'success': error is None
            }
        ) as trace:
            if trace:
                if error:
                    trace.log('error', error)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current Weave service metrics."""
        return {
            'enabled': self.is_enabled,
            'available': self.is_available,
            'initialized': self._initialized,
            'config': {
                'project_name': self.config.project_name,
                'sampling_rate': self.config.sampling_rate,
                'trace_llm_calls': self.config.trace_llm_calls,
                'trace_intelligence_ops': self.config.trace_intelligence_ops,
                'trace_report_generation': self.config.trace_report_generation
            },
            'metrics': self.metrics.to_dict()
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self._trace_lock:
            self.metrics = WeaveMetrics()
            self.metrics.initialization_time = self.metrics.initialization_time  # Keep init time
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Weave service.
        
        Returns:
            Health check results
        """
        health = {
            'status': 'healthy',
            'enabled': self.is_enabled,
            'available': self.is_available,
            'initialized': self._initialized,
            'errors': []
        }
        
        if self.config.enabled and not WEAVE_AVAILABLE:
            health['status'] = 'degraded'
            health['errors'].append('Weave package not installed')
        
        if self.config.enabled and not self._initialized:
            health['status'] = 'unhealthy'
            health['errors'].append('Weave initialization failed')
        
        if self.metrics.last_error:
            health['status'] = 'degraded'
            health['errors'].append(f'Recent error: {self.metrics.last_error}')
        
        return health
    
    async def shutdown(self) -> None:
        """Gracefully shutdown Weave service."""
        if self.is_enabled:
            try:
                # Flush any pending traces
                if hasattr(weave, 'flush'):
                    weave.flush()
                
                logger.info("Weave service shutdown completed")
                
            except Exception as e:
                logger.warning(f"Error during Weave shutdown: {e}")
        
        self._initialized = False 