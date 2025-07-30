"""
Detection Service

Business logic for threat detection operations.
Follows industry standards for service layer design.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any

from ..models.detection_models import (
    DetectionContext,
    DetectionResult,
    DetectionRequest,
    DetectionStats,
    ThreatLevel
)
from ..core.constants import ThreatType, SeverityLevel
from ..core.exceptions import DetectionError, RateLimitError
from ..infrastructure.monitoring.metrics import MetricsCollector
from ..infrastructure.monitoring.circuit_breaker import CircuitBreakerManager


class DetectionService:
    """
    Core detection service implementing business logic.
    
    This service orchestrates threat detection operations,
    manages detection workflows, and enforces business rules.
    
    Responsibilities:
    - Threat detection orchestration
    - Business rule enforcement
    - Result aggregation and analysis
    - Performance optimization
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        circuit_breaker_manager: Optional[CircuitBreakerManager] = None,
        max_concurrent_detections: int = 100,
        detection_timeout: float = 30.0
    ):
        """
        Initialize detection service.
        
        Args:
            metrics_collector: Metrics collection service
            circuit_breaker_manager: Circuit breaker manager
            max_concurrent_detections: Maximum concurrent detection operations
            detection_timeout: Timeout for detection operations
        """
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.circuit_breaker_manager = circuit_breaker_manager or CircuitBreakerManager()
        self.max_concurrent_detections = max_concurrent_detections
        self.detection_timeout = detection_timeout
        
        # Detection statistics
        self.stats = DetectionStats()
        
        # Active detection tracking
        self.active_detections = 0
        self.detection_semaphore = asyncio.Semaphore(max_concurrent_detections)
        
        # Registered detectors
        self.detectors: Dict[str, Any] = {}
        
    def register_detector(self, name: str, detector: Any) -> None:
        """
        Register a threat detector.
        
        Args:
            name: Detector name
            detector: Detector instance
        """
        self.detectors[name] = detector
        
    async def analyze_threat(
        self,
        data: str,
        context: Optional[DetectionContext] = None
    ) -> List[DetectionResult]:
        """
        Analyze data for potential threats.
        
        Args:
            data: Data to analyze
            context: Detection context
            
        Returns:
            List of detection results
            
        Raises:
            DetectionError: If detection fails
            RateLimitError: If rate limit exceeded
        """
        # Create default context if not provided
        if context is None:
            context = DetectionContext(
                input_size=len(data),
                input_type="text"
            )
        
        # Create detection request
        request = DetectionRequest(data=data, context=context)
        
        # Check rate limits and capacity
        await self._validate_detection_request(request)
        
        # Execute detection with circuit breaker protection
        start_time = time.time()
        try:
            async with self.detection_semaphore:
                self.active_detections += 1
                self.metrics_collector.set_active_detections(self.active_detections)
                
                results = await self._execute_detection(request)
                
                # Update statistics
                processing_time = time.time() - start_time
                self._update_stats(request, results, processing_time)
                
                return results
                
        finally:
            self.active_detections -= 1
            self.metrics_collector.set_active_detections(self.active_detections)
    
    async def _execute_detection(self, request: DetectionRequest) -> List[DetectionResult]:
        """
        Execute detection using registered detectors.
        
        Args:
            request: Detection request
            
        Returns:
            List of detection results
        """
        results = []
        
        # Run all detectors concurrently
        detection_tasks = []
        for detector_name, detector in self.detectors.items():
            task = self._run_detector_with_circuit_breaker(
                detector_name, detector, request
            )
            detection_tasks.append(task)
        
        # Wait for all detections to complete
        if detection_tasks:
            detector_results = await asyncio.gather(
                *detection_tasks, return_exceptions=True
            )
            
            # Process results
            for i, result in enumerate(detector_results):
                if isinstance(result, Exception):
                    # Log detector error
                    detector_name = list(self.detectors.keys())[i]
                    self.metrics_collector.record_error(
                        detector_name, type(result).__name__
                    )
                elif result is not None:
                    results.append(result)
        
        # Apply business rules to results
        filtered_results = self._apply_business_rules(results)
        
        return filtered_results
    
    async def _run_detector_with_circuit_breaker(
        self,
        detector_name: str,
        detector: Any,
        request: DetectionRequest
    ) -> Optional[DetectionResult]:
        """
        Run detector with circuit breaker protection.
        
        Args:
            detector_name: Name of the detector
            detector: Detector instance
            request: Detection request
            
        Returns:
            Detection result or None if failed
        """
        try:
            # Get circuit breaker for this detector
            circuit_breaker = await self.circuit_breaker_manager.get_circuit_breaker(
                detector_name
            )
            
            # Record detection request
            self.metrics_collector.record_detection_request(detector_name)
            
            # Execute detection with circuit breaker
            start_time = time.time()
            async with circuit_breaker:
                result = await detector.detect(request.data, request.context)
                
                # Record metrics
                duration = time.time() - start_time
                self.metrics_collector.record_detection_duration(
                    detector_name, duration
                )
                
                if result:
                    self.metrics_collector.record_detection_confidence(
                        detector_name, result.threat_type.value, result.confidence
                    )
                
                return result
                
        except Exception as e:
            # Record error
            self.metrics_collector.record_error(detector_name, type(e).__name__)
            # Don't re-raise - let other detectors continue
            return None
    
    def _apply_business_rules(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """
        Apply business rules to filter and prioritize results.
        
        Args:
            results: Raw detection results
            
        Returns:
            Filtered and prioritized results
        """
        if not results:
            return results
        
        # Remove low-confidence results
        high_confidence_results = [
            result for result in results
            if result.confidence >= 0.7  # Business rule: minimum confidence
        ]
        
        # Deduplicate similar threats
        deduplicated_results = self._deduplicate_results(high_confidence_results)
        
        # Sort by risk score (highest first)
        sorted_results = sorted(
            deduplicated_results,
            key=lambda r: r.risk_score,
            reverse=True
        )
        
        return sorted_results
    
    def _deduplicate_results(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """
        Remove duplicate or similar detection results.
        
        Args:
            results: Detection results to deduplicate
            
        Returns:
            Deduplicated results
        """
        # Group by threat type
        threat_groups: Dict[ThreatType, List[DetectionResult]] = {}
        for result in results:
            if result.threat_type not in threat_groups:
                threat_groups[result.threat_type] = []
            threat_groups[result.threat_type].append(result)
        
        # Keep highest confidence result per threat type
        deduplicated = []
        for threat_type, group in threat_groups.items():
            best_result = max(group, key=lambda r: r.confidence)
            deduplicated.append(best_result)
        
        return deduplicated
    
    async def _validate_detection_request(self, request: DetectionRequest) -> None:
        """
        Validate detection request against business rules.
        
        Args:
            request: Detection request to validate
            
        Raises:
            RateLimitError: If rate limit exceeded
            DetectionError: If request is invalid
        """
        # Check concurrent detection limit
        if self.active_detections >= self.max_concurrent_detections:
            raise RateLimitError(
                f"Maximum concurrent detections ({self.max_concurrent_detections}) exceeded"
            )
        
        # Validate input size
        if len(request.data) == 0:
            raise DetectionError("Empty input data provided")
        
        if len(request.data) > 10 * 1024 * 1024:  # 10MB limit
            raise DetectionError("Input data too large (>10MB)")
    
    def _update_stats(
        self,
        request: DetectionRequest,
        results: List[DetectionResult],
        processing_time: float
    ) -> None:
        """
        Update detection statistics.
        
        Args:
            request: Detection request
            results: Detection results
            processing_time: Processing time in seconds
        """
        self.stats.total_requests += 1
        
        if results:
            self.stats.successful_detections += 1
            self.stats.threats_detected += len([
                r for r in results if r.threat_type != ThreatType.BEHAVIORAL_ANOMALY
            ])
        else:
            self.stats.failed_detections += 1
        
        # Update average processing time
        total_requests = self.stats.total_requests
        current_avg = self.stats.avg_processing_time_ms
        self.stats.avg_processing_time_ms = (
            (current_avg * (total_requests - 1) + processing_time * 1000) / total_requests
        )
    
    def get_statistics(self) -> DetectionStats:
        """Get detection statistics."""
        return self.stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status."""
        cb_health = self.circuit_breaker_manager.get_health_summary()
        
        return {
            "service_name": "DetectionService",
            "status": "healthy" if cb_health["overall_health"] == "healthy" else "degraded",
            "active_detections": self.active_detections,
            "max_concurrent_detections": self.max_concurrent_detections,
            "registered_detectors": len(self.detectors),
            "circuit_breaker_health": cb_health,
            "statistics": self.stats.to_dict()
        } 