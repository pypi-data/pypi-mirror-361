"""
Enterprise-grade detection engine for AgentSentinel.

This module implements a production-ready, high-performance threat detection engine
with async architecture, circuit breakers, comprehensive metrics, and enterprise
security features.
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Set, Union
import logging
import hashlib
import weakref

# Third-party imports for enterprise features
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import opentelemetry
    from opentelemetry import trace
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

from ..core.constants import ThreatType, SeverityLevel, THREAT_SEVERITY, MAX_INPUT_SIZE
from ..core.config import Config
from ..core.exceptions import DetectionError, RateLimitError, ValidationError


class DetectionStatus(Enum):
    """Status of detection operations."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"


class ThreatLevel(Enum):
    """Standardized threat levels for enterprise reporting."""
    
    INFORMATIONAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class DetectionContext:
    """
    Enterprise-grade detection context with full observability.
    
    This class provides comprehensive context for threat detection
    with correlation IDs, tracing, and enterprise metadata.
    """
    
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    input_type: Optional[str] = None
    input_size: int = 0
    input_hash: Optional[str] = None
    parent_span_id: Optional[str] = None
    tenant_id: Optional[str] = None
    environment: str = "unknown"
    compliance_tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        if self.input_size > MAX_INPUT_SIZE:
            raise ValidationError(
                f"Input size {self.input_size} exceeds maximum allowed {MAX_INPUT_SIZE}",
                field_name="input_size",
                field_value=self.input_size
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging and metrics."""
        return {
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "request_timestamp": self.request_timestamp.isoformat(),
            "input_type": self.input_type,
            "input_size": self.input_size,
            "input_hash": self.input_hash,
            "tenant_id": self.tenant_id,
            "environment": self.environment,
            "compliance_tags": self.compliance_tags,
            "custom_metadata": self.custom_metadata,
        }


@dataclass
class DetectionResult:
    """
    Enterprise-grade detection result with comprehensive metadata.
    
    This class provides detailed detection results with enterprise features
    like compliance reporting, risk scoring, and audit trails.
    """
    
    # Core detection data
    threat_type: ThreatType
    confidence: float
    severity: SeverityLevel
    threat_level: ThreatLevel
    message: str
    evidence: List[str]
    
    # Detection metadata
    detector_name: str
    detector_version: str
    detection_method: str
    processing_time_ms: float
    
    # Enterprise metadata
    correlation_id: str
    detection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Risk and compliance
    risk_score: float = 0.0
    compliance_violations: List[str] = field(default_factory=list)
    regulatory_impact: List[str] = field(default_factory=list)
    
    # Technical details
    raw_matches: List[Dict[str, Any]] = field(default_factory=list)
    pattern_matches: List[str] = field(default_factory=list)
    false_positive_probability: float = 0.0
    
    # Remediation guidance
    recommended_actions: List[str] = field(default_factory=list)
    severity_justification: str = ""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and calculations."""
        if not 0.0 <= self.confidence <= 1.0:
            raise DetectionError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}",
                detector_name=self.detector_name
            )
        
        # Calculate risk score based on confidence and severity
        severity_weights = {
            SeverityLevel.LOW: 0.2,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.CRITICAL: 1.0,
        }
        
        base_risk = severity_weights.get(self.severity, 0.5)
        self.risk_score = min(base_risk * self.confidence * 100, 100.0)
        
        # Map severity to threat level
        severity_to_threat_level = {
            SeverityLevel.LOW: ThreatLevel.LOW,
            SeverityLevel.MEDIUM: ThreatLevel.MEDIUM,
            SeverityLevel.HIGH: ThreatLevel.HIGH,
            SeverityLevel.CRITICAL: ThreatLevel.CRITICAL,
        }
        
        if hasattr(self, 'threat_level') and self.threat_level is None:
            self.threat_level = severity_to_threat_level.get(self.severity, ThreatLevel.MEDIUM)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert detection result to dictionary for serialization."""
        return {
            # Core detection data
            "threat_type": self.threat_type.value,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "threat_level": self.threat_level.value,
            "message": self.message,
            "evidence": self.evidence,
            
            # Detection metadata
            "detector_name": self.detector_name,
            "detector_version": self.detector_version,
            "detection_method": self.detection_method,
            "processing_time_ms": self.processing_time_ms,
            
            # Enterprise metadata
            "correlation_id": self.correlation_id,
            "detection_id": self.detection_id,
            "timestamp": self.timestamp.isoformat(),
            
            # Risk and compliance
            "risk_score": self.risk_score,
            "compliance_violations": self.compliance_violations,
            "regulatory_impact": self.regulatory_impact,
            
            # Technical details
            "raw_matches": self.raw_matches,
            "pattern_matches": self.pattern_matches,
            "false_positive_probability": self.false_positive_probability,
            
            # Remediation guidance
            "recommended_actions": self.recommended_actions,
            "severity_justification": self.severity_justification,
        }
    
    def __str__(self) -> str:
        """String representation of detection result."""
        return (
            f"DetectionResult({self.threat_type.value}, "
            f"confidence={self.confidence:.2f}, "
            f"risk_score={self.risk_score:.1f})"
        )


class CircuitBreaker:
    """
    Enterprise-grade circuit breaker for detector resilience.
    
    Implements the circuit breaker pattern to prevent cascading failures
    and provide graceful degradation during detector issues.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        
        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.total_requests += 1
        
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise DetectionError(
                    "Circuit breaker is open",
                    error_code="CIRCUIT_BREAKER_OPEN"
                )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is None:
            # Success
            self.successful_requests += 1
            self._on_success()
        elif issubclass(exc_type, self.expected_exception):
            # Expected failure
            self.failed_requests += 1
            self._on_failure()
        
        return False  # Don't suppress exceptions
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self) -> None:
        """Handle successful operation."""
        if self.state == "half-open":
            self.state = "closed"
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                self.successful_requests / max(self.total_requests, 1) * 100
            ),
        }


class MetricsCollector:
    """
    Enterprise-grade metrics collection with Prometheus integration.
    
    Provides comprehensive metrics for detection engine performance,
    security events, and operational health.
    """
    
    def __init__(self, enabled: bool = True) -> None:
        """Initialize metrics collector."""
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        
        if self.enabled:
            # Detection metrics
            self.detection_requests = Counter(
                'agentsentinel_detection_requests_total',
                'Total detection requests',
                ['detector_name', 'threat_type', 'severity']
            )
            
            self.detection_duration = Histogram(
                'agentsentinel_detection_duration_seconds',
                'Detection processing duration',
                ['detector_name']
            )
            
            self.detection_confidence = Histogram(
                'agentsentinel_detection_confidence',
                'Detection confidence scores',
                ['detector_name', 'threat_type']
            )
            
            # Performance metrics
            self.active_detections = Gauge(
                'agentsentinel_active_detections',
                'Number of active detections'
            )
            
            self.memory_usage = Gauge(
                'agentsentinel_memory_usage_bytes',
                'Memory usage in bytes'
            )
            
            # Error metrics
            self.detection_errors = Counter(
                'agentsentinel_detection_errors_total',
                'Total detection errors',
                ['detector_name', 'error_type']
            )
            
            # Circuit breaker metrics
            self.circuit_breaker_state = Gauge(
                'agentsentinel_circuit_breaker_state',
                'Circuit breaker state (0=closed, 1=half-open, 2=open)',
                ['detector_name']
            )
    
    def record_detection_request(
        self,
        detector_name: str,
        threat_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> None:
        """Record a detection request."""
        if self.enabled:
            self.detection_requests.labels(
                detector_name=detector_name,
                threat_type=threat_type or "none",
                severity=severity or "none"
            ).inc()
    
    def record_detection_duration(
        self,
        detector_name: str,
        duration_seconds: float
    ) -> None:
        """Record detection processing duration."""
        if self.enabled:
            self.detection_duration.labels(
                detector_name=detector_name
            ).observe(duration_seconds)
    
    def record_detection_confidence(
        self,
        detector_name: str,
        threat_type: str,
        confidence: float
    ) -> None:
        """Record detection confidence score."""
        if self.enabled:
            self.detection_confidence.labels(
                detector_name=detector_name,
                threat_type=threat_type
            ).observe(confidence)
    
    def record_error(self, detector_name: str, error_type: str) -> None:
        """Record a detection error."""
        if self.enabled:
            self.detection_errors.labels(
                detector_name=detector_name,
                error_type=error_type
            ).inc()
    
    def set_active_detections(self, count: int) -> None:
        """Set the number of active detections."""
        if self.enabled:
            self.active_detections.set(count)
    
    def set_circuit_breaker_state(self, detector_name: str, state: str) -> None:
        """Set circuit breaker state."""
        if self.enabled:
            state_map = {"closed": 0, "half-open": 1, "open": 2}
            self.circuit_breaker_state.labels(
                detector_name=detector_name
            ).set(state_map.get(state, 0))


class EnterpriseDetector(ABC):
    """
    Abstract base class for enterprise-grade threat detectors.
    
    Provides a comprehensive framework for building production-ready
    detectors with async architecture, metrics, and enterprise features.
    """
    
    def __init__(
        self,
        config: Config,
        name: str,
        version: str = "1.0.0",
        max_concurrent: int = 100,
    ) -> None:
        """
        Initialize enterprise detector.
        
        Args:
            config: Configuration object
            name: Detector name
            version: Detector version
            max_concurrent: Maximum concurrent detections
        """
        self.config = config
        self.name = name
        self.version = version
        self.max_concurrent = max_concurrent
        
        # Async primitives
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.shutdown_event = asyncio.Event()
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            expected_exception=DetectionError
        )
        
        # Metrics
        self.metrics = MetricsCollector()
        
        # Caching
        self.result_cache: Dict[str, DetectionResult] = {}
        self.cache_ttl = 300  # 5 minutes
        self.cache_timestamps: Dict[str, float] = {}
        
        # Performance tracking
        self.detection_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # Logger with correlation ID support
        self.logger = logging.getLogger(f"agent_sentinel.detection.{name}")
        
        # Weak reference tracking for memory management
        self.active_detections = weakref.WeakSet()
        
    async def detect(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        """
        Detect threats in the provided data with enterprise features.
        
        Args:
            data: Input data to analyze
            context: Detection context with metadata
            
        Returns:
            DetectionResult if threat detected, None otherwise
        """
        # Validate input
        await self._validate_input(data, context)
        
        # Check cache first
        cache_key = self._get_cache_key(data, context)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Rate limiting via semaphore
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # Circuit breaker protection
                async with self.circuit_breaker:
                    # Record metrics
                    self.metrics.record_detection_request(self.name)
                    self.metrics.set_active_detections(len(self.active_detections))
                    
                    # Perform detection
                    result = await self._detect_impl(data, context)
                    
                    # Record performance metrics
                    processing_time = time.time() - start_time
                    self.metrics.record_detection_duration(self.name, processing_time)
                    
                    if result:
                        result.processing_time_ms = processing_time * 1000
                        result.detector_name = self.name
                        result.detector_version = self.version
                        result.correlation_id = context.correlation_id
                        
                        # Record detection metrics
                        self.metrics.record_detection_confidence(
                            self.name,
                            result.threat_type.value,
                            result.confidence
                        )
                        
                        # Cache result
                        self._cache_result(cache_key, result)
                    
                    # Update statistics
                    self.detection_count += 1
                    self.total_processing_time += processing_time
                    
                    return result
                    
            except Exception as e:
                self.error_count += 1
                self.metrics.record_error(self.name, type(e).__name__)
                
                error_msg = f"Detection failed in {self.name}: {str(e)}"
                self.logger.error(
                    error_msg,
                    extra={
                        "correlation_id": context.correlation_id,
                        "detector_name": self.name,
                        "error_type": type(e).__name__,
                        "input_size": context.input_size,
                    }
                )
                
                raise DetectionError(error_msg, detector_name=self.name) from e
    
    @abstractmethod
    async def _detect_impl(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        """
        Implementation-specific detection logic.
        
        This method must be implemented by subclasses to provide
        the actual threat detection functionality.
        """
        pass
    
    async def _validate_input(self, data: str, context: DetectionContext) -> None:
        """Validate input data and context."""
        if not data:
            raise ValidationError("Input data cannot be empty")
        
        if len(data) > MAX_INPUT_SIZE:
            raise ValidationError(
                f"Input size {len(data)} exceeds maximum {MAX_INPUT_SIZE}",
                field_name="data",
                field_value=len(data)
            )
        
        # Update context with computed values
        context.input_size = len(data)
        context.input_hash = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, data: str, context: DetectionContext) -> str:
        """Generate cache key for result caching."""
        key_data = f"{self.name}:{context.input_hash}:{context.input_type}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[DetectionResult]:
        """Get cached detection result if valid."""
        if cache_key not in self.result_cache:
            return None
        
        # Check TTL
        timestamp = self.cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp > self.cache_ttl:
            # Cache expired
            del self.result_cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None
        
        return self.result_cache[cache_key]
    
    def _cache_result(self, cache_key: str, result: DetectionResult) -> None:
        """Cache detection result."""
        self.result_cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
        
        # Cleanup old cache entries (simple LRU)
        if len(self.result_cache) > 1000:
            oldest_keys = sorted(
                self.cache_timestamps.items(),
                key=lambda x: x[1]
            )[:100]  # Remove oldest 100 entries
            
            for key, _ in oldest_keys:
                self.result_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the detector."""
        return {
            "name": self.name,
            "version": self.version,
            "status": "healthy" if not self.shutdown_event.is_set() else "shutdown",
            "circuit_breaker": self.circuit_breaker.get_stats(),
            "statistics": {
                "detection_count": self.detection_count,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(self.detection_count, 1) * 100,
                "average_processing_time_ms": (
                    self.total_processing_time / max(self.detection_count, 1) * 1000
                ),
                "cache_size": len(self.result_cache),
                "active_detections": len(self.active_detections),
            },
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the detector."""
        self.shutdown_event.set()
        
        # Wait for active detections to complete
        if self.active_detections:
            await asyncio.gather(
                *self.active_detections,
                return_exceptions=True
            )
        
        # Clear caches
        self.result_cache.clear()
        self.cache_timestamps.clear()
        
        self.logger.info(f"Detector {self.name} shutdown complete")


class EnterpriseDetectionEngine:
    """
    Enterprise-grade detection engine with async architecture.
    
    This engine provides production-ready threat detection with
    high-performance async operations, comprehensive metrics,
    circuit breakers, and enterprise security features.
    """
    
    def __init__(self, config: Config) -> None:
        """
        Initialize enterprise detection engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger("agent_sentinel.detection.engine")
        
        # Engine state
        self.detectors: List[EnterpriseDetector] = []
        self.enabled = config.detection.enabled
        self.confidence_threshold = config.detection.confidence_threshold
        
        # Async primitives
        self.max_concurrent_analyses = 1000
        self.analysis_semaphore = asyncio.Semaphore(self.max_concurrent_analyses)
        self.shutdown_event = asyncio.Event()
        
        # Metrics and monitoring
        self.metrics = MetricsCollector()
        self.start_time = time.time()
        
        # Performance tracking
        self.total_analyses = 0
        self.total_detections = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # Result aggregation
        self.detection_history: deque = deque(maxlen=10000)
        
        # Rate limiting
        self.rate_limiter: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Initialize detectors
        self._initialize_detectors()
        
        self.logger.info(
            f"Enterprise detection engine initialized with {len(self.detectors)} detectors"
        )
    
    def _initialize_detectors(self) -> None:
        """Initialize enterprise detectors."""
        # Import here to avoid circular imports
        from .enterprise_detectors import (
            EnterpriseSQLInjectionDetector,
            EnterpriseXSSDetector,
            EnterpriseCommandInjectionDetector,
            EnterprisePathTraversalDetector,
            EnterprisePromptInjectionDetector,
        )
        
        detector_classes = [
            EnterpriseSQLInjectionDetector,
            EnterpriseXSSDetector,
            EnterpriseCommandInjectionDetector,
            EnterprisePathTraversalDetector,
            EnterprisePromptInjectionDetector,
        ]
        
        for detector_class in detector_classes:
            try:
                detector = detector_class(self.config)
                self.detectors.append(detector)
                self.logger.debug(f"Initialized detector: {detector.name}")
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize detector {detector_class.__name__}: {e}"
                )
    
    async def analyze(
        self,
        data: str,
        context: Optional[DetectionContext] = None
    ) -> List[DetectionResult]:
        """
        Analyze input data for security threats with enterprise features.
        
        Args:
            data: Input data to analyze
            context: Detection context with metadata
            
        Returns:
            List of detection results sorted by risk score
        """
        if not self.enabled:
            return []
        
        if self.shutdown_event.is_set():
            raise DetectionError("Detection engine is shutting down")
        
        # Create context if not provided
        if context is None:
            context = DetectionContext()
        
        # Rate limiting check
        await self._check_rate_limits(context)
        
        # Global rate limiting via semaphore
        async with self.analysis_semaphore:
            start_time = time.time()
            
            try:
                # Run all detectors concurrently
                detection_tasks = []
                for detector in self.detectors:
                    if await self._is_detector_enabled(detector, context):
                        task = asyncio.create_task(
                            detector.detect(data, context)
                        )
                        detection_tasks.append((detector.name, task))
                
                # Wait for all detections with timeout
                results = []
                timeout = 5.0  # 5 second timeout
                
                for detector_name, task in detection_tasks:
                    try:
                        result = await asyncio.wait_for(task, timeout=timeout)
                        if result:
                            results.append(result)
                    except asyncio.TimeoutError:
                        self.logger.warning(
                            f"Detector {detector_name} timed out",
                            extra={"correlation_id": context.correlation_id}
                        )
                        self.metrics.record_error(detector_name, "timeout")
                    except Exception as e:
                        self.logger.error(
                            f"Detector {detector_name} failed: {e}",
                            extra={"correlation_id": context.correlation_id}
                        )
                        self.metrics.record_error(detector_name, type(e).__name__)
                
                # Update statistics
                processing_time = time.time() - start_time
                self.total_analyses += 1
                self.total_processing_time += processing_time
                
                if results:
                    self.total_detections += 1
                
                # Sort by risk score (highest first)
                results.sort(key=lambda x: x.risk_score, reverse=True)
                
                # Store in history for analysis
                self.detection_history.append({
                    "timestamp": datetime.now(timezone.utc),
                    "correlation_id": context.correlation_id,
                    "results_count": len(results),
                    "processing_time_ms": processing_time * 1000,
                    "input_size": context.input_size,
                })
                
                # Log significant detections
                if results:
                    high_risk_results = [r for r in results if r.risk_score >= 70]
                    if high_risk_results:
                        self.logger.warning(
                            f"High-risk threats detected: {len(high_risk_results)}",
                            extra={
                                "correlation_id": context.correlation_id,
                                "threat_types": [r.threat_type.value for r in high_risk_results],
                                "max_risk_score": max(r.risk_score for r in high_risk_results),
                            }
                        )
                
                return results
                
            except Exception as e:
                self.error_count += 1
                self.logger.error(
                    f"Analysis failed: {e}",
                    extra={"correlation_id": context.correlation_id}
                )
                raise DetectionError(f"Detection analysis failed: {str(e)}") from e
    
    async def _check_rate_limits(self, context: DetectionContext) -> None:
        """Check rate limits for the request."""
        # Simple rate limiting based on source IP
        source_key = context.source_ip or "unknown"
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        rate_queue = self.rate_limiter[source_key]
        while rate_queue and current_time - rate_queue[0] > 60:
            rate_queue.popleft()
        
        # Check rate limit (default: 100 requests per minute)
        rate_limit = 100
        if len(rate_queue) >= rate_limit:
            raise RateLimitError(
                f"Rate limit exceeded: {rate_limit} requests per minute",
                limit=rate_limit,
                window=60,
                current_rate=len(rate_queue)
            )
        
        # Add current request
        rate_queue.append(current_time)
    
    async def _is_detector_enabled(
        self,
        detector: EnterpriseDetector,
        context: DetectionContext
    ) -> bool:
        """Check if detector should be enabled for this request."""
        # Basic enabled check
        if not detector.circuit_breaker.state == "closed":
            return False
        
        # Context-based filtering
        if context.environment == "test" and detector.name in ["prompt_injection"]:
            # Disable certain detectors in test environment
            return False
        
        return True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the detection engine."""
        detector_health = []
        for detector in self.detectors:
            health = await detector.health_check()
            detector_health.append(health)
        
        uptime = time.time() - self.start_time
        
        return {
            "status": "healthy" if not self.shutdown_event.is_set() else "shutting_down",
            "uptime_seconds": uptime,
            "configuration": {
                "enabled": self.enabled,
                "confidence_threshold": self.confidence_threshold,
                "max_concurrent_analyses": self.max_concurrent_analyses,
            },
            "statistics": {
                "total_analyses": self.total_analyses,
                "total_detections": self.total_detections,
                "error_count": self.error_count,
                "detection_rate": self.total_detections / max(self.total_analyses, 1) * 100,
                "error_rate": self.error_count / max(self.total_analyses, 1) * 100,
                "average_processing_time_ms": (
                    self.total_processing_time / max(self.total_analyses, 1) * 1000
                ),
            },
            "detectors": detector_health,
            "rate_limiting": {
                "active_sources": len(self.rate_limiter),
                "total_rate_limited_requests": sum(
                    len(queue) for queue in self.rate_limiter.values()
                ),
            },
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the detection engine."""
        self.logger.info("Starting detection engine shutdown...")
        self.shutdown_event.set()
        
        # Shutdown all detectors
        shutdown_tasks = [detector.shutdown() for detector in self.detectors]
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.logger.info("Detection engine shutdown complete")
    
    def __str__(self) -> str:
        """String representation of the detection engine."""
        enabled_count = sum(1 for d in self.detectors if d.circuit_breaker.state == "closed")
        return (
            f"EnterpriseDetectionEngine("
            f"detectors={enabled_count}/{len(self.detectors)}, "
            f"enabled={self.enabled})"
        ) 