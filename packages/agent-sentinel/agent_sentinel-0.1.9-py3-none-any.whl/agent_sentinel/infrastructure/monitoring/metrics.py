"""
Metrics Collection for Detection Engine

Enterprise-grade metrics collection with Prometheus support,
following industry standards for observability and monitoring.
"""

import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Optional Prometheus support
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary  # type: ignore
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricPoint:
    """Individual metric data point."""
    
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "labels": self.labels
        }


@dataclass
class MetricSeries:
    """Time series of metric data."""
    
    name: str
    metric_type: str  # counter, gauge, histogram, summary
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_point(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a metric point."""
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=value,
            labels=labels or {}
        )
        self.points.append(point)
    
    def get_recent_points(self, limit: int = 100) -> List[MetricPoint]:
        """Get recent metric points."""
        return list(self.points)[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for this metric series."""
        if not self.points:
            return {"count": 0}
        
        values = [p.value for p in self.points]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "oldest": values[0] if values else None
        }


class MetricsCollector:
    """
    Enterprise-grade metrics collection for detection operations.
    
    Provides comprehensive metrics collection with optional Prometheus
    integration for production monitoring.
    """
    
    def __init__(self, enabled: bool = True, prometheus_enabled: bool = True) -> None:
        """
        Initialize metrics collector.
        
        Args:
            enabled: Whether to collect metrics
            prometheus_enabled: Whether to use Prometheus metrics
        """
        self.enabled = enabled
        self.prometheus_enabled = prometheus_enabled and PROMETHEUS_AVAILABLE
        
        # Internal metrics storage
        self.metrics: Dict[str, MetricSeries] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Prometheus metrics (if available)
        if self.prometheus_enabled:
            self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            return
        
        # Detection request counter
        self.prom_detection_requests = Counter(
            'agentsentinel_detection_requests_total',
            'Total number of detection requests',
            ['detector_name', 'threat_type', 'severity']
        )
        
        # Detection duration histogram
        self.prom_detection_duration = Histogram(
            'agentsentinel_detection_duration_seconds',
            'Detection processing duration in seconds',
            ['detector_name']
        )
        
        # Detection confidence summary
        self.prom_detection_confidence = Summary(
            'agentsentinel_detection_confidence',
            'Detection confidence scores',
            ['detector_name', 'threat_type']
        )
        
        # Active detections gauge
        self.prom_active_detections = Gauge(
            'agentsentinel_active_detections',
            'Number of active detection operations'
        )
        
        # Error counter
        self.prom_errors = Counter(
            'agentsentinel_errors_total',
            'Total number of detection errors',
            ['detector_name', 'error_type']
        )
        
        # Circuit breaker state gauge
        self.prom_circuit_breaker_state = Gauge(
            'agentsentinel_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['detector_name']
        )
    
    def record_detection_request(
        self,
        detector_name: str,
        threat_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> None:
        """Record a detection request."""
        if not self.enabled:
            return
        
        # Internal metrics
        key = f"detection_requests.{detector_name}"
        self.counters[key] += 1
        
        if key not in self.metrics:
            self.metrics[key] = MetricSeries(key, "counter")
        
        labels = {
            "detector_name": detector_name,
            "threat_type": threat_type or "unknown",
            "severity": severity or "unknown"
        }
        self.metrics[key].add_point(1, labels)
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_detection_requests.labels(
                detector_name=detector_name,
                threat_type=threat_type or "unknown",
                severity=severity or "unknown"
            ).inc()
    
    def record_detection_duration(
        self,
        detector_name: str,
        duration_seconds: float
    ) -> None:
        """Record detection processing duration."""
        if not self.enabled:
            return
        
        # Internal metrics
        key = f"detection_duration.{detector_name}"
        self.histograms[key].append(duration_seconds)
        
        if key not in self.metrics:
            self.metrics[key] = MetricSeries(key, "histogram")
        
        self.metrics[key].add_point(duration_seconds, {"detector_name": detector_name})
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_detection_duration.labels(
                detector_name=detector_name
            ).observe(duration_seconds)
    
    def record_detection_confidence(
        self,
        detector_name: str,
        threat_type: str,
        confidence: float
    ) -> None:
        """Record detection confidence score."""
        if not self.enabled:
            return
        
        # Internal metrics
        key = f"detection_confidence.{detector_name}.{threat_type}"
        
        if key not in self.metrics:
            self.metrics[key] = MetricSeries(key, "summary")
        
        labels = {
            "detector_name": detector_name,
            "threat_type": threat_type
        }
        self.metrics[key].add_point(confidence, labels)
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_detection_confidence.labels(
                detector_name=detector_name,
                threat_type=threat_type
            ).observe(confidence)
    
    def record_error(self, detector_name: str, error_type: str) -> None:
        """Record an error."""
        if not self.enabled:
            return
        
        # Internal metrics
        key = f"errors.{detector_name}.{error_type}"
        self.counters[key] += 1
        
        if key not in self.metrics:
            self.metrics[key] = MetricSeries(key, "counter")
        
        labels = {
            "detector_name": detector_name,
            "error_type": error_type
        }
        self.metrics[key].add_point(1, labels)
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_errors.labels(
                detector_name=detector_name,
                error_type=error_type
            ).inc()
    
    def set_active_detections(self, count: int) -> None:
        """Set the number of active detections."""
        if not self.enabled:
            return
        
        # Internal metrics
        self.gauges["active_detections"] = count
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_active_detections.set(count)
    
    def set_circuit_breaker_state(self, detector_name: str, state: str) -> None:
        """Set circuit breaker state."""
        if not self.enabled:
            return
        
        # Map state to numeric value
        state_map = {"closed": 0, "open": 1, "half_open": 2}
        state_value = state_map.get(state, 0)
        
        # Internal metrics
        key = f"circuit_breaker_state.{detector_name}"
        self.gauges[key] = state_value
        
        # Prometheus metrics
        if self.prometheus_enabled:
            self.prom_circuit_breaker_state.labels(
                detector_name=detector_name
            ).set(state_value)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        if not self.enabled:
            return {"enabled": False}
        
        summary = {
            "enabled": True,
            "prometheus_enabled": self.prometheus_enabled,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "metric_series_count": len(self.metrics),
            "histogram_stats": {}
        }
        
        # Add histogram statistics
        for key, values in self.histograms.items():
            if values:
                summary["histogram_stats"][key] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "percentiles": self._calculate_percentiles(values)
                }
        
        return summary
    
    def get_metric_series(self, name: str) -> Optional[MetricSeries]:
        """Get a specific metric series."""
        return self.metrics.get(name)
    
    def get_all_metric_series(self) -> Dict[str, MetricSeries]:
        """Get all metric series."""
        return self.metrics.copy()
    
    def get_detector_stats(self, detector_name: str) -> Dict[str, Any]:
        """Get statistics for a specific detector."""
        stats = {
            "detector_name": detector_name,
            "requests": 0,
            "errors": 0,
            "avg_duration": 0.0,
            "circuit_breaker_state": "unknown"
        }
        
        # Count requests
        request_key = f"detection_requests.{detector_name}"
        if request_key in self.counters:
            stats["requests"] = self.counters[request_key]
        
        # Count errors
        error_count = 0
        for key, count in self.counters.items():
            if key.startswith(f"errors.{detector_name}."):
                error_count += count
        stats["errors"] = error_count
        
        # Calculate average duration
        duration_key = f"detection_duration.{detector_name}"
        if duration_key in self.histograms:
            durations = self.histograms[duration_key]
            if durations:
                stats["avg_duration"] = sum(durations) / len(durations)
        
        # Get circuit breaker state
        cb_key = f"circuit_breaker_state.{detector_name}"
        if cb_key in self.gauges:
            state_value = int(self.gauges[cb_key])
            state_map = {0: "closed", 1: "open", 2: "half_open"}
            stats["circuit_breaker_state"] = state_map.get(state_value, "unknown")
        
        return stats
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for a list of values."""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        percentiles = {}
        for p in [50, 90, 95, 99]:
            index = int(n * p / 100)
            if index >= n:
                index = n - 1
            percentiles[f"p{p}"] = sorted_values[index]
        
        return percentiles
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            import json
            return json.dumps(self.get_metrics_summary(), indent=2)
        elif format == "prometheus" and self.prometheus_enabled:
            from prometheus_client import generate_latest  # type: ignore
            return generate_latest().decode('utf-8')
        else:
            return str(self.get_metrics_summary()) 