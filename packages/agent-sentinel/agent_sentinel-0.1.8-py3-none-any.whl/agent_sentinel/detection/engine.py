"""
Enterprise-grade detection engine with modular plugin architecture.

This module implements a robust, extensible runtime security framework
similar to enterprise security tools like Datadog Security, Snyk, and Wiz.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import threading
from queue import Queue
import hashlib
import json
from datetime import datetime, timezone

from ..core.types import SecurityEvent
from ..core.constants import ThreatType, SeverityLevel


class DetectionMethod(Enum):
    """Detection methods supported by the engine."""
    RULE_BASED = "rule_based"
    PATTERN_BASED = "pattern_based"
    ML_BASED = "ml_based"
    EXTERNAL_FEED = "external_feed"
    ANOMALY_DETECTION = "anomaly_detection"
    BEHAVIOR_MODELING = "behavior_modeling"


@dataclass
class DetectionContext:
    """Context for detection operations."""
    agent_id: str
    method_name: str
    inputs: Dict[str, Any]
    outputs: Optional[Any] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DetectionResult:
    """Result of a detection operation."""
    threat_type: ThreatType
    severity: SeverityLevel
    confidence: float
    message: str
    context: Dict[str, Any]
    detection_method: DetectionMethod
    detector_name: str
    raw_data: Optional[str] = None


class BaseDetector(ABC):
    """Base class for all detectors in the modular pipeline."""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.detection_count = 0
        self.last_detection: Optional[datetime] = None
    
    @abstractmethod
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        """Detect threats in the given context."""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detector metrics."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "detection_count": self.detection_count,
            "last_detection": self.last_detection.isoformat() if self.last_detection else None
        }


class RuleBasedDetector(BaseDetector):
    """Rule-based detector for time-based, threshold, and domain-specific rules."""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        super().__init__("RuleBasedDetector")
        self.rules = rules
        self.call_history: Dict[str, List[float]] = {}
        self.sensitive_token_patterns = [
            r"\b(password|secret|key|token|credential)\b",
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]
    
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        results = []
        
        # Time-based rules
        for rule in self.rules:
            if rule.get("type") == "time_based":
                results.extend(await self._check_time_based_rule(rule, context))
            elif rule.get("type") == "threshold":
                results.extend(await self._check_threshold_rule(rule, context))
            elif rule.get("type") == "domain_specific":
                results.extend(await self._check_domain_rule(rule, context))
        
        return results
    
    async def _check_time_based_rule(self, rule: Dict[str, Any], context: DetectionContext) -> List[DetectionResult]:
        """Check time-based rules (e.g., tool called > 3x in 60s)."""
        results = []
        key = f"{context.agent_id}_{context.method_name}"
        current_time = time.time()
        
        # Initialize history if needed
        if key not in self.call_history:
            self.call_history[key] = []
        
        # Add current call
        self.call_history[key].append(current_time)
        
        # Remove old calls outside window
        window = rule.get("window_seconds", 60)
        self.call_history[key] = [t for t in self.call_history[key] if current_time - t <= window]
        
        # Check threshold
        max_calls = rule.get("max_calls", 3)
        if len(self.call_history[key]) > max_calls:
            results.append(DetectionResult(
                threat_type=ThreatType.RATE_LIMIT_VIOLATION,
                severity=SeverityLevel.MEDIUM,
                confidence=0.8,
                message=f"Rate limit exceeded: {len(self.call_history[key])} calls in {window}s",
                context={
                    "method": context.method_name,
                    "call_count": len(self.call_history[key]),
                    "window_seconds": window,
                    "max_allowed": max_calls
                },
                detection_method=DetectionMethod.RULE_BASED,
                detector_name=self.name
            ))
        
        return results
    
    async def _check_threshold_rule(self, rule: Dict[str, Any], context: DetectionContext) -> List[DetectionResult]:
        """Check threshold rules (e.g., request contains >10 sensitive tokens)."""
        results = []
        
        # Count sensitive tokens in inputs
        sensitive_count = 0
        for key, value in context.inputs.items():
            if isinstance(value, str):
                import re
                for pattern in self.sensitive_token_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        sensitive_count += 1
        
        max_sensitive = rule.get("max_sensitive_tokens", 5)
        if sensitive_count > max_sensitive:
            results.append(DetectionResult(
                threat_type=ThreatType.DATA_EXFILTRATION,
                severity=SeverityLevel.HIGH,
                confidence=0.7,
                message=f"Too many sensitive tokens detected: {sensitive_count}",
                context={
                    "sensitive_count": sensitive_count,
                    "max_allowed": max_sensitive,
                    "inputs": context.inputs
                },
                detection_method=DetectionMethod.RULE_BASED,
                detector_name=self.name
            ))
        
        return results
    
    async def _check_domain_rule(self, rule: Dict[str, Any], context: DetectionContext) -> List[DetectionResult]:
        """Check domain-specific rules."""
        results = []
        
        # Example: Don't call tool Y with query type Z
        forbidden_tools = rule.get("forbidden_tools", [])
        forbidden_queries = rule.get("forbidden_queries", [])
        
        if context.method_name in forbidden_tools:
            results.append(DetectionResult(
                threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                severity=SeverityLevel.HIGH,
                confidence=0.9,
                message=f"Forbidden tool accessed: {context.method_name}",
                context={
                    "forbidden_tool": context.method_name,
                    "inputs": context.inputs
                },
                detection_method=DetectionMethod.RULE_BASED,
                detector_name=self.name
            ))
        
        return results


class PatternBasedDetector(BaseDetector):
    """Pattern-based detector using regex and prompt filters."""
    
    def __init__(self):
        super().__init__("PatternBasedDetector")
        from ..core.constants import THREAT_PATTERNS
        self.patterns = THREAT_PATTERNS
    
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        results = []
        
        # Analyze inputs
        for key, value in context.inputs.items():
            if isinstance(value, str):
                results.extend(await self._analyze_text(value, f"input_{key}"))
        
        # Analyze outputs
        if context.outputs and isinstance(context.outputs, str):
            results.extend(await self._analyze_text(context.outputs, "output"))
        
        return results
    
    async def _analyze_text(self, text: str, context_name: str) -> List[DetectionResult]:
        """Analyze text for threat patterns."""
        results = []
        
        for threat_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    confidence = self._calculate_confidence(pattern, text, matches)
                    if confidence >= 0.7:  # Configurable threshold
                        results.append(DetectionResult(
                            threat_type=threat_type,
                            severity=self._get_severity(threat_type),
                            confidence=confidence,
                            message=f"Pattern match detected: {threat_type.value}",
                            context={
                                "text": text[:500],
                                "pattern": pattern.pattern,
                                "matches": matches[:10],
                                "context": context_name
                            },
                            detection_method=DetectionMethod.PATTERN_BASED,
                            detector_name=self.name,
                            raw_data=text
                        ))
        
        return results
    
    def _calculate_confidence(self, pattern, text: str, matches: list) -> float:
        """Calculate confidence score for pattern matches."""
        base_confidence = 0.7
        
        if len(matches) == 1 and matches[0] == text.strip():
            base_confidence += 0.2
        
        if len(matches) > 1:
            base_confidence += 0.1
        
        if len(pattern.pattern) > 20:
            base_confidence += 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def _get_severity(self, threat_type: ThreatType) -> SeverityLevel:
        """Get severity level for threat type."""
        from ..core.constants import THREAT_SEVERITY
        return THREAT_SEVERITY.get(threat_type, SeverityLevel.MEDIUM)


class AnomalyDetector(BaseDetector):
    """Anomaly detection based on behavioral modeling."""
    
    def __init__(self):
        super().__init__("AnomalyDetector")
        self.behavior_profiles: Dict[str, Dict[str, Any]] = {}
        self.sequence_history: Dict[str, List[str]] = {}
    
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        results = []
        
        # Update behavior profile
        self._update_profile(context)
        
        # Check for anomalies
        anomalies = self._detect_anomalies(context)
        for anomaly in anomalies:
            results.append(DetectionResult(
                threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                severity=SeverityLevel.MEDIUM,
                confidence=anomaly["confidence"],
                message=f"Behavioral anomaly detected: {anomaly['reason']}",
                context=anomaly["context"],
                detection_method=DetectionMethod.ANOMALY_DETECTION,
                detector_name=self.name
            ))
        
        return results
    
    def _update_profile(self, context: DetectionContext):
        """Update behavior profile for the agent."""
        agent_key = context.agent_id
        
        if agent_key not in self.behavior_profiles:
            self.behavior_profiles[agent_key] = {
                "method_calls": {},
                "input_patterns": {},
                "timing_patterns": [],
                "last_update": time.time()
            }
        
        profile = self.behavior_profiles[agent_key]
        
        # Update method call frequency
        if context.method_name not in profile["method_calls"]:
            profile["method_calls"][context.method_name] = 0
        profile["method_calls"][context.method_name] += 1
        
        # Update timing patterns
        profile["timing_patterns"].append(time.time())
        if len(profile["timing_patterns"]) > 100:
            profile["timing_patterns"] = profile["timing_patterns"][-100:]
    
    def _detect_anomalies(self, context: DetectionContext) -> List[Dict[str, Any]]:
        """Detect behavioral anomalies."""
        anomalies = []
        agent_key = context.agent_id
        
        if agent_key not in self.behavior_profiles:
            return anomalies
        
        profile = self.behavior_profiles[agent_key]
        
        # Check for unusual method calls
        total_calls = sum(profile["method_calls"].values())
        if total_calls > 0:
            method_ratio = profile["method_calls"].get(context.method_name, 0) / total_calls
            if method_ratio > 0.8:  # Method called >80% of the time
                anomalies.append({
                    "confidence": 0.6,
                    "reason": "Unusual method call frequency",
                    "context": {
                        "method": context.method_name,
                        "ratio": method_ratio,
                        "total_calls": total_calls
                    }
                })
        
        # Check for rapid successive calls
        if len(profile["timing_patterns"]) >= 2:
            recent_calls = profile["timing_patterns"][-5:]
            intervals = [recent_calls[i] - recent_calls[i-1] for i in range(1, len(recent_calls))]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            
            if avg_interval < 0.1:  # Calls less than 100ms apart
                anomalies.append({
                    "confidence": 0.7,
                    "reason": "Rapid successive calls detected",
                    "context": {
                        "avg_interval": avg_interval,
                        "recent_calls": len(recent_calls)
                    }
                })
        
        return anomalies


class DetectionEngine:
    """Enterprise-grade detection engine with modular pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detectors: List[BaseDetector] = []
        self.async_queue = Queue()
        self.logging_thread = None
        self.is_running = False
        
        # Initialize detectors
        self._initialize_detectors()
        
        # Start async processing
        self._start_async_processing()
    
    def _initialize_detectors(self):
        """Initialize the detection pipeline."""
        # Rule-based detector with default rules
        default_rules = [
            {
                "type": "time_based",
                "window_seconds": 60,
                "max_calls": 10
            },
            {
                "type": "threshold",
                "max_sensitive_tokens": 5
            }
        ]
        self.detectors.append(RuleBasedDetector(default_rules))
        
        # Pattern-based detector
        self.detectors.append(PatternBasedDetector())
        
        # Anomaly detector
        self.detectors.append(AnomalyDetector())
    
    def _start_async_processing(self):
        """Start async processing thread."""
        self.is_running = True
        self.logging_thread = threading.Thread(target=self._async_processor, daemon=True)
        self.logging_thread.start()
    
    def _async_processor(self):
        """Async processor for non-blocking operations."""
        while self.is_running:
            try:
                # Process queued items
                while not self.async_queue.empty():
                    task = self.async_queue.get_nowait()
                    asyncio.run(task)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                print(f"Error in async processor: {e}")
    
    async def detect_threats(self, context: DetectionContext) -> List[DetectionResult]:
        """Detect threats using all enabled detectors."""
        all_results = []
        
        for detector in self.detectors:
            if detector.enabled:
                try:
                    results = await detector.detect(context)
                    all_results.extend(results)
                    
                    # Update detector metrics
                    if results:
                        detector.detection_count += len(results)
                        detector.last_detection = datetime.now(timezone.utc)
                
                except Exception as e:
                    # Log detector errors but continue with other detectors
                    print(f"Error in detector {detector.name}: {e}")
        
        return all_results
    
    def add_detector(self, detector: BaseDetector):
        """Add a custom detector to the pipeline."""
        self.detectors.append(detector)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        return {
            "total_detectors": len(self.detectors),
            "enabled_detectors": len([d for d in self.detectors if d.enabled]),
            "detector_metrics": [d.get_metrics() for d in self.detectors],
            "queue_size": self.async_queue.qsize(),
            "is_running": self.is_running
        }
    
    def shutdown(self):
        """Shutdown the detection engine."""
        self.is_running = False
        if self.logging_thread:
            self.logging_thread.join(timeout=5) 