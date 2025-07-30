"""
Circuit Breaker Pattern Implementation

Enterprise-grade circuit breaker for resilient detection operations,
following industry standards for fault tolerance and reliability.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Type
from enum import Enum

from ...core.exceptions import DetectionError


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Enterprise-grade circuit breaker implementation.
    
    Provides fault tolerance for detection operations by automatically
    failing fast when error rates exceed thresholds.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        name: str = "default"
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type to track for failures
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # State tracking
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.success_count = 0
        
        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_changes = 0
        
        # Concurrency control
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._check_state()
        
        if self.state == CircuitBreakerState.OPEN:
            raise DetectionError(
                f"Circuit breaker '{self.name}' is OPEN",
                detector_name=self.name
            )
        
        self.total_requests += 1
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        async with self._lock:
            if exc_type is None:
                # Success
                self._on_success()
            elif issubclass(exc_type, self.expected_exception):
                # Expected failure
                self._on_failure()
            
            return False  # Don't suppress exceptions
    
    async def _check_state(self) -> None:
        """Check and potentially change circuit breaker state."""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.state_changes += 1
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset from OPEN state."""
        if self.last_failure_time is None:
            return False
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self) -> None:
        """Handle successful operation."""
        self.total_successes += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Recovery successful, close circuit
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.state_changes += 1
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN]:
                self.state = CircuitBreakerState.OPEN
                self.state_changes += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "state_changes": self.state_changes,
            "failure_rate": (
                self.total_failures / self.total_requests
                if self.total_requests > 0 else 0.0
            ),
            "last_failure_time": self.last_failure_time,
            "time_since_last_failure": (
                time.time() - self.last_failure_time
                if self.last_failure_time else None
            )
        }
    
    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.state_changes += 1
    
    def force_open(self) -> None:
        """Manually open circuit breaker."""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = time.time()
        self.state_changes += 1
    
    def is_available(self) -> bool:
        """Check if circuit breaker allows requests."""
        return self.state != CircuitBreakerState.OPEN
    
    def __str__(self) -> str:
        """String representation."""
        return f"CircuitBreaker({self.name}, state={self.state.value}, failures={self.failure_count})"


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.
    
    Provides centralized management of circuit breakers for different
    detection components.
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ) -> CircuitBreaker:
        """Get or create circuit breaker."""
        async with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    expected_exception=expected_exception,
                    name=name
                )
            
            return self.circuit_breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {
            name: cb.get_stats()
            for name, cb in self.circuit_breakers.items()
        }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for cb in self.circuit_breakers.values():
            cb.reset()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all circuit breakers."""
        total_breakers = len(self.circuit_breakers)
        open_breakers = sum(
            1 for cb in self.circuit_breakers.values()
            if cb.state == CircuitBreakerState.OPEN
        )
        half_open_breakers = sum(
            1 for cb in self.circuit_breakers.values()
            if cb.state == CircuitBreakerState.HALF_OPEN
        )
        
        return {
            "total_circuit_breakers": total_breakers,
            "open_circuit_breakers": open_breakers,
            "half_open_circuit_breakers": half_open_breakers,
            "closed_circuit_breakers": total_breakers - open_breakers - half_open_breakers,
            "overall_health": "healthy" if open_breakers == 0 else "degraded",
            "circuit_breaker_names": list(self.circuit_breakers.keys())
        } 