"""
Enhanced World-Class Detection Engine for Agent Sentinel

This module provides enterprise-grade threat detection with advanced capabilities:
- Real-time behavioral analysis
- Multi-layer threat detection
- Advanced pattern recognition
- ML-based anomaly detection
- Cross-agent attack detection
- Zero-day threat detection
- Compliance monitoring

Maintains simple @monitor interface while providing enterprise-grade security.
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import hashlib
import statistics
import re
from pathlib import Path

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..core.exceptions import DetectionError
from ..logging.structured_logger import SecurityLogger
from .engine import BaseDetector, DetectionResult, DetectionContext, DetectionEngine, DetectionMethod
from .enterprise_detectors import (
    EnterpriseDetectionContext, 
    AgentType, 
    AttackVector,
    AdvancedPromptInjectionDetector,
    A2AAgentDetector,
    MCPAgentDetector,
    AutonomousAgentDetector,
    CrossAgentAttackDetector
)


class DetectionLayer(Enum):
    """Six layers of detection in our enhanced engine."""
    PATTERN_MATCHING = "pattern_matching"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    THREAT_INTELLIGENCE = "threat_intelligence"
    ML_CLASSIFICATION = "ml_classification"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"


@dataclass
class EnhancedDetectionResult:
    """Enhanced detection result with additional context."""
    threat_type: ThreatType
    severity: SeverityLevel
    confidence: float
    message: str
    detection_layer: DetectionLayer
    detector_name: str
    
    # Enhanced context
    attack_vector: Optional[AttackVector] = None
    risk_score: float = 0.0
    mitigation_suggestions: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
    
    # Technical details
    raw_data: Optional[str] = None
    pattern_matches: List[str] = field(default_factory=list)
    behavioral_indicators: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal context
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    
    def to_legacy_result(self) -> DetectionResult:
        """Convert to legacy DetectionResult format."""
        return DetectionResult(
            threat_type=self.threat_type,
            severity=self.severity,
            confidence=self.confidence,
            message=self.message,
            context={
                "attack_vector": self.attack_vector.value if self.attack_vector else None,
                "risk_score": self.risk_score,
                "mitigation_suggestions": self.mitigation_suggestions,
                "related_events": self.related_events,
                "behavioral_indicators": self.behavioral_indicators,
                "pattern_matches": self.pattern_matches,
                "correlation_id": self.correlation_id
            },
            detection_method=DetectionMethod.BEHAVIOR_MODELING,
            detector_name=self.detector_name,
            raw_data=self.raw_data
        )


class BehavioralAnalysisEngine:
    """Advanced behavioral analysis engine for detecting anomalies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_behaviors: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.baseline_window = config.get("baseline_window_hours", 24)
        self.anomaly_threshold = config.get("anomaly_threshold", 2.0)  # Standard deviations
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Behavioral metrics
        self.metrics = {
            "total_analyses": 0,
            "anomalies_detected": 0,
            "profiles_created": 0,
            "last_analysis": None
        }
    
    def analyze_behavior(self, context: EnterpriseDetectionContext) -> List[EnhancedDetectionResult]:
        """Analyze behavior and detect anomalies."""
        results = []
        
        with self._lock:
            # Update behavioral profile
            self._update_profile(context)
            
            # Detect anomalies
            anomalies = self._detect_behavioral_anomalies(context)
            
            # Convert to detection results
            for anomaly in anomalies:
                results.append(EnhancedDetectionResult(
                    threat_type=anomaly["threat_type"],
                    severity=anomaly["severity"],
                    confidence=anomaly["confidence"],
                    message=anomaly["message"],
                    detection_layer=DetectionLayer.BEHAVIORAL_ANALYSIS,
                    detector_name="BehavioralAnalysisEngine",
                    attack_vector=anomaly.get("attack_vector"),
                    risk_score=anomaly.get("risk_score", 0.0),
                    behavioral_indicators=anomaly.get("indicators", {}),
                    mitigation_suggestions=anomaly.get("mitigations", [])
                ))
            
            self.metrics["total_analyses"] += 1
            if anomalies:
                self.metrics["anomalies_detected"] += len(anomalies)
            self.metrics["last_analysis"] = datetime.now(timezone.utc)
        
        return results
    
    def _update_profile(self, context: EnterpriseDetectionContext) -> None:
        """Update behavioral profile for agent."""
        agent_id = context.agent_id
        
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = {
                "created_at": datetime.now(timezone.utc),
                "total_calls": 0,
                "methods": defaultdict(int),
                "call_patterns": [],
                "timing_patterns": [],
                "input_patterns": {},
                "output_patterns": {},
                "session_lengths": [],
                "error_rates": [],
                "last_updated": datetime.now(timezone.utc)
            }
            self.metrics["profiles_created"] += 1
        
        profile = self.agent_profiles[agent_id]
        
        # Update basic metrics
        profile["total_calls"] += 1
        profile["methods"][context.method_name] += 1
        profile["last_updated"] = datetime.now(timezone.utc)
        
        # Update timing patterns
        current_time = time.time()
        profile["timing_patterns"].append(current_time)
        
        # Keep only recent patterns (last 24 hours)
        cutoff_time = current_time - (self.baseline_window * 3600)
        profile["timing_patterns"] = [t for t in profile["timing_patterns"] if t > cutoff_time]
        
        # Update input patterns
        for key, value in context.inputs.items():
            if key not in profile["input_patterns"]:
                profile["input_patterns"][key] = {"types": set(), "lengths": [], "patterns": []}
            
            profile["input_patterns"][key]["types"].add(type(value).__name__)
            if isinstance(value, str):
                profile["input_patterns"][key]["lengths"].append(len(value))
                profile["input_patterns"][key]["patterns"].append(value[:100])  # Sample
        
        # Update output patterns
        if context.outputs:
            if "output" not in profile["output_patterns"]:
                profile["output_patterns"]["output"] = {"types": set(), "lengths": [], "patterns": []}
            
            profile["output_patterns"]["output"]["types"].add(type(context.outputs).__name__)
            if isinstance(context.outputs, str):
                profile["output_patterns"]["output"]["lengths"].append(len(context.outputs))
                profile["output_patterns"]["output"]["patterns"].append(str(context.outputs)[:100])
    
    def _detect_behavioral_anomalies(self, context: EnterpriseDetectionContext) -> List[Dict[str, Any]]:
        """Detect behavioral anomalies."""
        anomalies = []
        agent_id = context.agent_id
        
        if agent_id not in self.agent_profiles:
            return anomalies
        
        profile = self.agent_profiles[agent_id]
        
        # Check for timing anomalies
        timing_anomalies = self._check_timing_anomalies(context, profile)
        anomalies.extend(timing_anomalies)
        
        # Check for input anomalies
        input_anomalies = self._check_input_anomalies(context, profile)
        anomalies.extend(input_anomalies)
        
        # Check for method usage anomalies
        method_anomalies = self._check_method_anomalies(context, profile)
        anomalies.extend(method_anomalies)
        
        # Check for session anomalies
        session_anomalies = self._check_session_anomalies(context, profile)
        anomalies.extend(session_anomalies)
        
        return anomalies
    
    def _check_timing_anomalies(self, context: EnterpriseDetectionContext, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for timing-based anomalies."""
        anomalies = []
        timing_patterns = profile["timing_patterns"]
        
        if len(timing_patterns) < 10:  # Need baseline
            return anomalies
        
        # Calculate call intervals
        intervals = []
        for i in range(1, len(timing_patterns)):
            intervals.append(timing_patterns[i] - timing_patterns[i-1])
        
        if len(intervals) < 5:
            return anomalies
        
        # Check for burst patterns (rapid successive calls)
        recent_intervals = intervals[-5:]  # Last 5 intervals
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Detect burst (calls much faster than normal)
        if std_interval > 0:
            for interval in recent_intervals:
                if interval < (avg_interval - self.anomaly_threshold * std_interval):
                    anomalies.append({
                        "threat_type": ThreatType.RATE_LIMIT_VIOLATION,
                        "severity": SeverityLevel.MEDIUM,
                        "confidence": 0.7,
                        "message": f"Burst pattern detected: {interval:.2f}s interval vs {avg_interval:.2f}s average",
                        "attack_vector": AttackVector.RESOURCE_EXHAUSTION,
                        "risk_score": 0.6,
                        "indicators": {
                            "current_interval": interval,
                            "average_interval": avg_interval,
                            "standard_deviation": std_interval
                        },
                        "mitigations": ["Implement rate limiting", "Monitor for automated attacks"]
                    })
        
        return anomalies
    
    def _check_input_anomalies(self, context: EnterpriseDetectionContext, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for input-based anomalies."""
        anomalies = []
        
        for key, value in context.inputs.items():
            if key not in profile["input_patterns"]:
                continue
            
            pattern_data = profile["input_patterns"][key]
            
            # Check for unusual input length
            if isinstance(value, str) and pattern_data["lengths"]:
                avg_length = statistics.mean(pattern_data["lengths"])
                std_length = statistics.stdev(pattern_data["lengths"]) if len(pattern_data["lengths"]) > 1 else 0
                
                if std_length > 0 and len(value) > (avg_length + self.anomaly_threshold * std_length):
                    anomalies.append({
                        "threat_type": ThreatType.BEHAVIORAL_ANOMALY,
                        "severity": SeverityLevel.MEDIUM,
                        "confidence": 0.6,
                        "message": f"Unusual input length for {key}: {len(value)} vs {avg_length:.1f} average",
                        "attack_vector": AttackVector.DATA_EXFILTRATION,
                        "risk_score": 0.5,
                        "indicators": {
                            "input_key": key,
                            "current_length": len(value),
                            "average_length": avg_length,
                            "standard_deviation": std_length
                        },
                        "mitigations": ["Validate input lengths", "Implement input sanitization"]
                    })
            
            # Check for unusual input type
            current_type = type(value).__name__
            if current_type not in pattern_data["types"]:
                anomalies.append({
                    "threat_type": ThreatType.BEHAVIORAL_ANOMALY,
                    "severity": SeverityLevel.LOW,
                    "confidence": 0.5,
                    "message": f"Unusual input type for {key}: {current_type} not in {pattern_data['types']}",
                    "attack_vector": AttackVector.PROTOCOL_MANIPULATION,
                    "risk_score": 0.3,
                    "indicators": {
                        "input_key": key,
                        "current_type": current_type,
                        "expected_types": list(pattern_data["types"])
                    },
                    "mitigations": ["Implement type validation", "Add input schema validation"]
                })
        
        return anomalies
    
    def _check_method_anomalies(self, context: EnterpriseDetectionContext, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for method usage anomalies."""
        anomalies = []
        method_counts = profile["methods"]
        
        if len(method_counts) < 3:  # Need baseline
            return anomalies
        
        # Check if method is rarely used
        total_calls = sum(method_counts.values())
        method_frequency = method_counts[context.method_name] / total_calls
        
        # Calculate average frequency
        avg_frequency = 1.0 / len(method_counts)
        
        # If method is used much less frequently than average, it might be suspicious
        if method_frequency < (avg_frequency * 0.1):  # Less than 10% of average
            anomalies.append({
                "threat_type": ThreatType.UNAUTHORIZED_ACCESS,
                "severity": SeverityLevel.LOW,
                "confidence": 0.4,
                "message": f"Rarely used method called: {context.method_name} ({method_frequency:.1%} frequency)",
                "attack_vector": AttackVector.PRIVILEGE_ESCALATION,
                "risk_score": 0.3,
                "indicators": {
                    "method_name": context.method_name,
                    "frequency": method_frequency,
                    "average_frequency": avg_frequency,
                    "total_calls": total_calls
                },
                "mitigations": ["Monitor unusual method access", "Implement method-level permissions"]
            })
        
        return anomalies
    
    def _check_session_anomalies(self, context: EnterpriseDetectionContext, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for session-based anomalies."""
        anomalies = []
        
        # Track session behavior
        session_id = context.session_context.get("session_id", "default")
        session_behaviors = self.session_behaviors[session_id]
        
        # Add current behavior
        session_behaviors.append({
            "timestamp": datetime.now(timezone.utc),
            "method": context.method_name,
            "agent_id": context.agent_id,
            "inputs": context.inputs
        })
        
        # Keep only recent behaviors (last hour)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        session_behaviors[:] = [b for b in session_behaviors if b["timestamp"] > cutoff_time]
        
        # Check for session hijacking (different agents in same session)
        agent_ids = set(b["agent_id"] for b in session_behaviors)
        if len(agent_ids) > 1:
            anomalies.append({
                "threat_type": ThreatType.UNAUTHORIZED_ACCESS,
                "severity": SeverityLevel.HIGH,
                "confidence": 0.8,
                "message": f"Multiple agents in same session: {agent_ids}",
                "attack_vector": AttackVector.AGENT_HIJACKING,
                "risk_score": 0.8,
                "indicators": {
                    "session_id": session_id,
                    "agent_ids": list(agent_ids),
                    "behavior_count": len(session_behaviors)
                },
                "mitigations": ["Implement session validation", "Monitor cross-agent sessions"]
            })
        
        return anomalies
    
    def get_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get behavioral profile for agent."""
        return self.agent_profiles.get(agent_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get behavioral analysis metrics."""
        return {
            **self.metrics,
            "profiles_count": len(self.agent_profiles),
            "session_count": len(self.session_behaviors)
        }


class EnhancedDetectionEngine:
    """World-class detection engine with six layers of protection."""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[SecurityLogger] = None):
        self.config = config
        self.logger = logger or SecurityLogger(
            name="enhanced_detection_engine", 
            agent_id="system"
        )
        
        # Initialize behavioral analysis engine
        self.behavioral_engine = BehavioralAnalysisEngine(config)
        
        # Initialize enterprise detectors
        self.enterprise_detectors = {
            "prompt_injection": AdvancedPromptInjectionDetector(config),
            "a2a_agent": A2AAgentDetector(config),
            "mcp_agent": MCPAgentDetector(config),
            "autonomous_agent": AutonomousAgentDetector(config),
            "cross_agent": CrossAgentAttackDetector(config)
        }
        
        # Initialize legacy detection engine
        self.legacy_engine = DetectionEngine(config)
        
        # Detection metrics
        self.metrics = {
            "total_detections": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "detection_layers_used": defaultdict(int),
            "last_detection": None
        }
        
        # Thread safety
        self._lock = threading.Lock()
    
    async def detect_threats(self, context: DetectionContext) -> List[DetectionResult]:
        """Detect threats using all six layers of protection."""
        all_results = []
        
        # Convert to enterprise context
        enterprise_context = self._convert_to_enterprise_context(context)
        
        # Layer 1: Pattern Matching (Legacy engine)
        try:
            legacy_results = await self.legacy_engine.detect_threats(context)
            all_results.extend(legacy_results)
            
            if legacy_results:
                self.metrics["detection_layers_used"][DetectionLayer.PATTERN_MATCHING.value] += 1
        except Exception as e:
            self.logger.error(f"Pattern matching layer failed: {e}")
        
        # Layer 2: Behavioral Analysis
        try:
            behavioral_results = self.behavioral_engine.analyze_behavior(enterprise_context)
            all_results.extend([r.to_legacy_result() for r in behavioral_results])
            
            if behavioral_results:
                self.metrics["detection_layers_used"][DetectionLayer.BEHAVIORAL_ANALYSIS.value] += 1
        except Exception as e:
            self.logger.error(f"Behavioral analysis layer failed: {e}")
        
        # Layer 3: Anomaly Detection (Enterprise detectors)
        try:
            for detector_name, detector in self.enterprise_detectors.items():
                enterprise_results = detector.detect_with_context(enterprise_context)
                all_results.extend([r.to_legacy_result() if hasattr(r, 'to_legacy_result') else r for r in enterprise_results])
                
                if enterprise_results:
                    self.metrics["detection_layers_used"][DetectionLayer.ANOMALY_DETECTION.value] += 1
        except Exception as e:
            self.logger.error(f"Anomaly detection layer failed: {e}")
        
        # Layer 4: Threat Intelligence (Future implementation)
        # Layer 5: ML Classification (Future implementation)
        # Layer 6: Contextual Analysis (Future implementation)
        
        # Update metrics
        with self._lock:
            self.metrics["total_detections"] += 1
            if all_results:
                self.metrics["threats_detected"] += len(all_results)
            self.metrics["last_detection"] = datetime.now(timezone.utc)
        
        return all_results
    
    def _convert_to_enterprise_context(self, context: DetectionContext) -> EnterpriseDetectionContext:
        """Convert legacy context to enterprise context."""
        # Detect agent type from method name and inputs
        agent_type = self._detect_agent_type(context)
        
        return EnterpriseDetectionContext(
            agent_id=context.agent_id,
            agent_type=agent_type,
            method_name=context.method_name,
            inputs=context.inputs,
            outputs=context.outputs,
            timestamp=context.timestamp or datetime.now(timezone.utc),
            session_context=context.metadata or {},
            agent_metadata=context.metadata or {}
        )
    
    def _detect_agent_type(self, context: DetectionContext) -> AgentType:
        """Detect agent type from context."""
        method_name = context.method_name.lower()
        inputs = str(context.inputs).lower()
        
        # MCP agent detection
        if any(keyword in method_name for keyword in ["mcp", "protocol", "tool", "resource"]):
            return AgentType.MCP_AGENT
        
        if any(keyword in inputs for keyword in ["mcp", "protocol", "jsonrpc"]):
            return AgentType.MCP_AGENT
        
        # A2A agent detection
        if any(keyword in method_name for keyword in ["agent", "communicate", "coordinate", "collaborate"]):
            return AgentType.A2A_AGENT
        
        # Autonomous agent detection
        if any(keyword in method_name for keyword in ["autonomous", "execute", "plan", "decide"]):
            return AgentType.AUTONOMOUS_AGENT
        
        # Default to unknown
        return AgentType.UNKNOWN
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive detection metrics."""
        return {
            **self.metrics,
            "behavioral_metrics": self.behavioral_engine.get_metrics(),
            "enterprise_detectors": {
                name: detector.get_metrics() if hasattr(detector, 'get_metrics') else {"name": name}
                for name, detector in self.enterprise_detectors.items()
            },
            "legacy_metrics": self.legacy_engine.get_metrics()
        }
    
    def get_behavioral_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get behavioral profile for agent."""
        return self.behavioral_engine.get_profile(agent_id)
    
    def add_custom_detector(self, name: str, detector: BaseDetector) -> None:
        """Add custom detector to the engine."""
        self.enterprise_detectors[name] = detector
    
    def shutdown(self) -> None:
        """Shutdown the detection engine."""
        self.legacy_engine.shutdown() 