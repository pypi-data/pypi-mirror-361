"""
Monitoring Service

Business logic for system monitoring and health checking.
Follows industry standards for service layer design.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from ..infrastructure.monitoring.metrics import MetricsCollector
from ..infrastructure.monitoring.circuit_breaker import CircuitBreakerManager


class MonitoringService:
    """
    Service for system monitoring and health management.
    
    Responsibilities:
    - System health monitoring
    - Performance metrics aggregation
    - Alert threshold management
    - Health status reporting
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        circuit_breaker_manager: Optional[CircuitBreakerManager] = None
    ):
        """
        Initialize monitoring service.
        
        Args:
            metrics_collector: Metrics collection service
            circuit_breaker_manager: Circuit breaker manager
        """
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.circuit_breaker_manager = circuit_breaker_manager or CircuitBreakerManager()
        
        # Health check configuration
        self.health_check_interval = 30.0  # seconds
        self.last_health_check = None
        
        # Alert thresholds
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "avg_response_time": 1000,  # 1 second in ms
            "circuit_breaker_open": 1,  # Any open circuit breaker
            "memory_usage": 80.0,  # 80% memory usage
            "cpu_usage": 80.0,  # 80% CPU usage
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Returns:
            System health information
        """
        # Get metrics summary
        metrics_summary = self.metrics_collector.get_metrics_summary()
        
        # Get circuit breaker health
        cb_health = self.circuit_breaker_manager.get_health_summary()
        
        # Calculate overall health score
        health_score = self._calculate_health_score(metrics_summary, cb_health)
        
        # Determine overall status
        status = self._determine_overall_status(health_score, cb_health)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "health_score": health_score,
            "metrics": metrics_summary,
            "circuit_breakers": cb_health,
            "alerts": self._check_alert_conditions(metrics_summary, cb_health),
            "uptime": self._get_uptime(),
            "version": "1.0.0"
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get detailed performance metrics.
        
        Returns:
            Performance metrics data
        """
        metrics_summary = self.metrics_collector.get_metrics_summary()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics_summary,
            "performance_analysis": self._analyze_performance(metrics_summary),
            "trending": self._get_performance_trends(),
            "recommendations": self._get_performance_recommendations(metrics_summary)
        }
    
    def get_detector_health(self, detector_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health information for specific detector or all detectors.
        
        Args:
            detector_name: Specific detector name, or None for all
            
        Returns:
            Detector health information
        """
        if detector_name:
            return {
                "detector": detector_name,
                "stats": self.metrics_collector.get_detector_stats(detector_name),
                "circuit_breaker": self.circuit_breaker_manager.get_all_stats().get(detector_name, {})
            }
        else:
            # Get all detector health
            all_stats = {}
            cb_stats = self.circuit_breaker_manager.get_all_stats()
            
            # Get list of all detectors from metrics and circuit breakers
            all_detectors = set()
            
            # Add detectors from metrics
            for key in self.metrics_collector.counters.keys():
                if key.startswith("detection_requests."):
                    detector = key.replace("detection_requests.", "")
                    all_detectors.add(detector)
            
            # Add detectors from circuit breakers
            all_detectors.update(cb_stats.keys())
            
            # Compile stats for each detector
            for detector in all_detectors:
                all_stats[detector] = {
                    "stats": self.metrics_collector.get_detector_stats(detector),
                    "circuit_breaker": cb_stats.get(detector, {})
                }
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detectors": all_stats,
                "summary": {
                    "total_detectors": len(all_detectors),
                    "healthy_detectors": len([d for d, s in all_stats.items() 
                                            if s["circuit_breaker"].get("state") == "closed"]),
                    "degraded_detectors": len([d for d, s in all_stats.items() 
                                             if s["circuit_breaker"].get("state") == "open"])
                }
            }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for alert conditions.
        
        Returns:
            List of active alerts
        """
        metrics_summary = self.metrics_collector.get_metrics_summary()
        cb_health = self.circuit_breaker_manager.get_health_summary()
        
        return self._check_alert_conditions(metrics_summary, cb_health)
    
    def update_alert_thresholds(self, thresholds: Dict[str, float]) -> None:
        """
        Update alert thresholds.
        
        Args:
            thresholds: New threshold values
        """
        self.alert_thresholds.update(thresholds)
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics_collector.reset_metrics()
    
    def _calculate_health_score(
        self, 
        metrics_summary: Dict[str, Any], 
        cb_health: Dict[str, Any]
    ) -> float:
        """
        Calculate overall system health score (0-100).
        
        Args:
            metrics_summary: Metrics summary
            cb_health: Circuit breaker health
            
        Returns:
            Health score between 0 and 100
        """
        score = 100.0
        
        # Penalize for open circuit breakers
        open_breakers = cb_health.get("open_circuit_breakers", 0)
        total_breakers = cb_health.get("total_circuit_breakers", 1)
        if total_breakers > 0:
            cb_penalty = (open_breakers / total_breakers) * 30  # Up to 30 point penalty
            score -= cb_penalty
        
        # Penalize for high error rates
        if metrics_summary.get("enabled", False):
            counters = metrics_summary.get("counters", {})
            total_requests = sum(v for k, v in counters.items() if "detection_requests" in k)
            total_errors = sum(v for k, v in counters.items() if "errors" in k)
            
            if total_requests > 0:
                error_rate = total_errors / total_requests
                if error_rate > self.alert_thresholds["error_rate"]:
                    error_penalty = min(error_rate * 100, 40)  # Up to 40 point penalty
                    score -= error_penalty
        
        # Penalize for slow performance
        histogram_stats = metrics_summary.get("histogram_stats", {})
        for key, stats in histogram_stats.items():
            if "detection_duration" in key:
                avg_time_ms = stats.get("avg", 0) * 1000  # Convert to ms
                if avg_time_ms > self.alert_thresholds["avg_response_time"]:
                    perf_penalty = min((avg_time_ms / 1000) * 10, 20)  # Up to 20 point penalty
                    score -= perf_penalty
                    break
        
        return max(0.0, min(100.0, score))
    
    def _determine_overall_status(
        self, 
        health_score: float, 
        cb_health: Dict[str, Any]
    ) -> str:
        """
        Determine overall system status.
        
        Args:
            health_score: Health score (0-100)
            cb_health: Circuit breaker health
            
        Returns:
            Status string
        """
        if health_score >= 90:
            return "healthy"
        elif health_score >= 70:
            return "degraded"
        elif health_score >= 50:
            return "unhealthy"
        else:
            return "critical"
    
    def _check_alert_conditions(
        self, 
        metrics_summary: Dict[str, Any], 
        cb_health: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check for alert conditions.
        
        Args:
            metrics_summary: Metrics summary
            cb_health: Circuit breaker health
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Check circuit breaker alerts
        open_breakers = cb_health.get("open_circuit_breakers", 0)
        if open_breakers > 0:
            alerts.append({
                "type": "circuit_breaker_open",
                "severity": "high",
                "message": f"{open_breakers} circuit breakers are open",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Check error rate alerts
        if metrics_summary.get("enabled", False):
            counters = metrics_summary.get("counters", {})
            total_requests = sum(v for k, v in counters.items() if "detection_requests" in k)
            total_errors = sum(v for k, v in counters.items() if "errors" in k)
            
            if total_requests > 0:
                error_rate = total_errors / total_requests
                if error_rate > self.alert_thresholds["error_rate"]:
                    alerts.append({
                        "type": "high_error_rate",
                        "severity": "medium" if error_rate < 0.1 else "high",
                        "message": f"Error rate is {error_rate:.2%} (threshold: {self.alert_thresholds['error_rate']:.2%})",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
        
        # Check performance alerts
        histogram_stats = metrics_summary.get("histogram_stats", {})
        for key, stats in histogram_stats.items():
            if "detection_duration" in key:
                avg_time_ms = stats.get("avg", 0) * 1000
                if avg_time_ms > self.alert_thresholds["avg_response_time"]:
                    alerts.append({
                        "type": "slow_response_time",
                        "severity": "medium",
                        "message": f"Average response time is {avg_time_ms:.0f}ms (threshold: {self.alert_thresholds['avg_response_time']}ms)",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                break
        
        return alerts
    
    def _analyze_performance(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance metrics.
        
        Args:
            metrics_summary: Metrics summary
            
        Returns:
            Performance analysis
        """
        analysis = {
            "overall_performance": "good",
            "bottlenecks": [],
            "efficiency_score": 85.0,
            "recommendations": []
        }
        
        # Analyze histogram data
        histogram_stats = metrics_summary.get("histogram_stats", {})
        
        for key, stats in histogram_stats.items():
            if "detection_duration" in key:
                avg_time = stats.get("avg", 0)
                p95_time = stats.get("percentiles", {}).get("p95", 0)
                
                if avg_time > 0.5:  # 500ms
                    analysis["bottlenecks"].append(f"Slow detection times for {key}")
                    analysis["overall_performance"] = "degraded"
                    analysis["efficiency_score"] -= 15
                
                if p95_time > 2.0:  # 2 seconds
                    analysis["bottlenecks"].append(f"High p95 latency for {key}")
                    analysis["efficiency_score"] -= 10
        
        return analysis
    
    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends (placeholder for time-series analysis)."""
        return {
            "trend": "stable",
            "direction": "neutral",
            "confidence": 0.8
        }
    
    def _get_performance_recommendations(self, metrics_summary: Dict[str, Any]) -> List[str]:
        """
        Get performance improvement recommendations.
        
        Args:
            metrics_summary: Metrics summary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check error rates
        counters = metrics_summary.get("counters", {})
        total_requests = sum(v for k, v in counters.items() if "detection_requests" in k)
        total_errors = sum(v for k, v in counters.items() if "errors" in k)
        
        if total_requests > 0:
            error_rate = total_errors / total_requests
            if error_rate > 0.01:  # 1%
                recommendations.append("Investigate and reduce error rates")
        
        # Check performance
        histogram_stats = metrics_summary.get("histogram_stats", {})
        for key, stats in histogram_stats.items():
            if "detection_duration" in key:
                avg_time = stats.get("avg", 0)
                if avg_time > 0.2:  # 200ms
                    recommendations.append("Optimize detection algorithms for better performance")
                break
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    def _get_uptime(self) -> str:
        """Get system uptime (placeholder)."""
        # In a real implementation, this would track actual uptime
        return "99.9%" 