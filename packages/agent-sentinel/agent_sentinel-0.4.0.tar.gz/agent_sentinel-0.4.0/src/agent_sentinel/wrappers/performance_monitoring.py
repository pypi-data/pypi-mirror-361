"""
Performance Monitoring for Agent Wrapper

Handles performance tracking, anomaly detection, and metrics collection
for monitored AI agent method calls.
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MethodCallInfo:
    """Information about a monitored method call"""
    method_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    args: tuple = ()
    kwargs: Optional[Dict[str, Any]] = None
    result: Any = None
    exception: Optional[Exception] = None
    security_validations: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.security_validations is None:
            self.security_validations = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert method call info to dictionary"""
        return {
            'method_name': self.method_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'success': self.exception is None,
            'security_validations': self.security_validations,
            'metadata': self.metadata
        }


class PerformanceMonitor:
    """Monitors and analyzes method performance"""
    
    def __init__(self, agent_id: str, logger=None):
        self.agent_id = agent_id
        self.logger = logger
        
        # Performance statistics
        self.stats = {
            'total_method_calls': 0,
            'average_call_duration': 0.0,
            'method_call_patterns': {},
            'performance_anomalies': 0,
            'slowest_methods': {},
            'fastest_methods': {}
        }
        
        # Performance thresholds
        self.anomaly_threshold_multiplier = 5.0  # 5x slower than average
        self.slow_method_threshold = 1.0  # 1 second
        self.fast_method_threshold = 0.001  # 1 millisecond
        
        # Recent performance history (for anomaly detection)
        self.recent_calls: List[MethodCallInfo] = []
        self.max_recent_calls = 1000

    def start_monitoring_call(self, method_name: str, args: tuple, kwargs: Dict[str, Any]) -> MethodCallInfo:
        """Start monitoring a method call"""
        call_info = MethodCallInfo(
            method_name=method_name,
            start_time=datetime.now(timezone.utc),
            args=self._sanitize_args(args),
            kwargs=self._sanitize_kwargs(kwargs)
        )
        
        return call_info

    def end_monitoring_call(self, call_info: MethodCallInfo, result: Any = None, exception: Optional[Exception] = None):
        """End monitoring a method call"""
        call_info.end_time = datetime.now(timezone.utc)
        call_info.duration = time.time() - time.mktime(call_info.start_time.timetuple())
        call_info.result = self._sanitize_result(result)
        call_info.exception = exception
        
        # Update statistics
        self._update_stats(call_info)
        
        # Check for performance anomalies
        self._check_performance_anomalies(call_info)
        
        # Store in recent calls
        self.recent_calls.append(call_info)
        if len(self.recent_calls) > self.max_recent_calls:
            self.recent_calls = self.recent_calls[-self.max_recent_calls // 2:]

    def _update_stats(self, call_info: MethodCallInfo):
        """Update performance statistics"""
        if call_info.duration is None:
            return
        
        # Update total calls
        self.stats['total_method_calls'] += 1
        
        # Update method call patterns
        method_name = call_info.method_name
        current_count = self.stats['method_call_patterns'].get(method_name, 0)
        self.stats['method_call_patterns'][method_name] = current_count + 1
        
        # Update average call duration
        total_calls = self.stats['total_method_calls']
        current_avg = self.stats['average_call_duration']
        self.stats['average_call_duration'] = (
            (current_avg * (total_calls - 1) + call_info.duration) / total_calls
        )
        
        # Track slowest and fastest methods
        self._update_method_extremes(call_info)

    def _update_method_extremes(self, call_info: MethodCallInfo):
        """Update slowest and fastest method tracking"""
        if call_info.duration is None:
            return
        
        method_name = call_info.method_name
        duration = call_info.duration
        
        # Update slowest methods
        if method_name not in self.stats['slowest_methods'] or duration > self.stats['slowest_methods'][method_name]:
            self.stats['slowest_methods'][method_name] = duration
        
        # Update fastest methods
        if method_name not in self.stats['fastest_methods'] or duration < self.stats['fastest_methods'][method_name]:
            self.stats['fastest_methods'][method_name] = duration

    def _check_performance_anomalies(self, call_info: MethodCallInfo):
        """Check for performance anomalies"""
        if call_info.duration is None:
            return
        
        # Check against average duration
        avg_duration = self.stats['average_call_duration']
        if avg_duration > 0 and call_info.duration > avg_duration * self.anomaly_threshold_multiplier:
            self.stats['performance_anomalies'] += 1
            
            if self.logger:
                self.logger.warning(
                    f"Performance anomaly detected in method {call_info.method_name}",
                    extra={
                        'method_name': call_info.method_name,
                        'duration': call_info.duration,
                        'average_duration': avg_duration,
                        'anomaly_factor': call_info.duration / avg_duration,
                        'agent_id': self.agent_id,
                        'is_performance_anomaly': True
                    }
                )
        
        # Check against absolute thresholds
        if call_info.duration > self.slow_method_threshold:
            if self.logger:
                self.logger.info(
                    f"Slow method execution detected: {call_info.method_name}",
                    extra={
                        'method_name': call_info.method_name,
                        'duration': call_info.duration,
                        'threshold': self.slow_method_threshold,
                        'agent_id': self.agent_id,
                        'is_slow_method': True
                    }
                )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'stats': self.stats.copy(),
            'recent_calls_count': len(self.recent_calls),
            'configuration': {
                'anomaly_threshold_multiplier': self.anomaly_threshold_multiplier,
                'slow_method_threshold': self.slow_method_threshold,
                'fast_method_threshold': self.fast_method_threshold
            }
        }

    def get_method_performance(self, method_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific method"""
        method_calls = [call for call in self.recent_calls if call.method_name == method_name]
        
        if not method_calls:
            return {'method_name': method_name, 'calls': 0}
        
        durations = [call.duration for call in method_calls if call.duration is not None]
        
        if not durations:
            return {'method_name': method_name, 'calls': len(method_calls), 'durations': []}
        
        return {
            'method_name': method_name,
            'calls': len(method_calls),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_duration': sum(durations),
            'success_rate': len([call for call in method_calls if call.exception is None]) / len(method_calls)
        }

    def get_slowest_methods(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest methods"""
        sorted_methods = sorted(
            self.stats['slowest_methods'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'method_name': method, 'max_duration': duration}
            for method, duration in sorted_methods[:limit]
        ]

    def get_recent_anomalies(self, limit: int = 10) -> List[MethodCallInfo]:
        """Get recent performance anomalies"""
        avg_duration = self.stats['average_call_duration']
        if avg_duration == 0:
            return []
        
        anomalies = [
            call for call in self.recent_calls
            if call.duration and call.duration > avg_duration * self.anomaly_threshold_multiplier
        ]
        
        # Sort by duration (slowest first)
        anomalies.sort(key=lambda x: x.duration or 0, reverse=True)
        
        return anomalies[:limit]

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