"""
Multi-Layer Detection Engine for Agent Sentinel

This module implements a sophisticated 6-layer defense system for comprehensive
threat detection in AI agents, following enterprise security best practices.

The 6-layer architecture:
1. Signature Matching Layer - Known attack patterns and signatures
2. Pattern Detection Layer - Regex-based pattern matching
3. Behavioral Analysis Layer - Agent behavior and anomaly detection
4. ML-Based Detection Layer - Machine learning threat classification
5. Threat Intelligence Layer - External threat feeds and IOCs
6. Risk Scoring Layer - Comprehensive risk assessment and prioritization

Enterprise features:
- Defense in depth with multiple detection mechanisms
- Adaptive threat detection with machine learning
- Real-time threat intelligence integration
- Cross-layer correlation and analysis
- Advanced risk scoring and prioritization
- Support for all agent types (A2A, MCP, autonomous)
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import hashlib
import logging
from pathlib import Path
import numpy as np

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..core.exceptions import AgentSentinelError, DetectionError
from ..intelligence.behavioral_analyzer import BehavioralAnalyzer, BehavioralAnomaly
from ..logging.structured_logger import SecurityLogger


class DetectionLayer(Enum):
    """Detection layers in the multi-layer system."""
    SIGNATURE_MATCHING = "signature_matching"
    PATTERN_DETECTION = "pattern_detection"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    ML_DETECTION = "ml_detection"
    THREAT_INTELLIGENCE = "threat_intelligence"
    RISK_SCORING = "risk_scoring"


class DetectionPriority(Enum):
    """Priority levels for detection processing."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class DetectionContext:
    """Context for multi-layer detection."""
    agent_id: str
    method_name: str
    inputs: Dict[str, Any]
    outputs: Optional[Any] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Layer-specific context
    layer_contexts: Dict[DetectionLayer, Dict[str, Any]] = field(default_factory=dict)
    
    def get_layer_context(self, layer: DetectionLayer) -> Dict[str, Any]:
        """Get context for specific detection layer."""
        return self.layer_contexts.get(layer, {})
    
    def set_layer_context(self, layer: DetectionLayer, context: Dict[str, Any]) -> None:
        """Set context for specific detection layer."""
        self.layer_contexts[layer] = context


@dataclass
class LayerResult:
    """Result from a detection layer."""
    layer: DetectionLayer
    threat_type: Optional[ThreatType]
    severity: SeverityLevel
    confidence: float
    message: str
    evidence: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_security_event(self, agent_id: str, context: DetectionContext) -> SecurityEvent:
        """Convert layer result to security event."""
        return SecurityEvent(
            threat_type=self.threat_type or ThreatType.MALICIOUS_PAYLOAD,
            severity=self.severity,
            message=self.message,
            confidence=self.confidence,
            context={
                "detection_layer": self.layer.value,
                "evidence": self.evidence,
                "metadata": self.metadata,
                "processing_time": self.processing_time,
                "method_name": context.method_name,
                "session_id": context.session_id,
                "user_id": context.user_id
            },
            agent_id=agent_id,
            timestamp=context.timestamp or datetime.now(timezone.utc),
            detection_method=f"multi_layer_{self.layer.value}"
        )


@dataclass
class CorrelatedThreat:
    """Correlated threat across multiple layers."""
    threat_type: ThreatType
    severity: SeverityLevel
    confidence: float
    message: str
    agent_id: str
    timestamp: datetime
    
    # Layer results that contributed to this threat
    layer_results: List[LayerResult] = field(default_factory=list)
    
    # Correlation metadata
    correlation_score: float = 0.0
    risk_score: float = 0.0
    attack_chain: List[str] = field(default_factory=list)
    
    def to_security_event(self, context: DetectionContext) -> SecurityEvent:
        """Convert correlated threat to security event."""
        return SecurityEvent(
            threat_type=self.threat_type,
            severity=self.severity,
            message=self.message,
            confidence=self.confidence,
            context={
                "correlation_score": self.correlation_score,
                "risk_score": self.risk_score,
                "attack_chain": self.attack_chain,
                "contributing_layers": [result.layer.value for result in self.layer_results],
                "layer_evidence": {
                    result.layer.value: result.evidence for result in self.layer_results
                },
                "method_name": context.method_name,
                "session_id": context.session_id,
                "user_id": context.user_id
            },
            agent_id=self.agent_id,
            timestamp=self.timestamp,
            detection_method="multi_layer_correlation"
        )


class DetectionLayerBase(ABC):
    """Base class for detection layers."""
    
    def __init__(
        self,
        layer_name: str,
        priority: DetectionPriority = DetectionPriority.MEDIUM,
        enabled: bool = True,
        timeout: float = 5.0
    ):
        self.layer_name = layer_name
        self.priority = priority
        self.enabled = enabled
        self.timeout = timeout
        
        # Performance metrics
        self.processed_count = 0
        self.detection_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # Thread safety
        self.lock = threading.Lock()
    
    @abstractmethod
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats in the given context."""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get layer performance metrics."""
        with self.lock:
            avg_processing_time = (
                self.total_processing_time / self.processed_count
                if self.processed_count > 0 else 0.0
            )
            
            detection_rate = (
                self.detection_count / self.processed_count
                if self.processed_count > 0 else 0.0
            )
            
            return {
                "layer_name": self.layer_name,
                "enabled": self.enabled,
                "processed_count": self.processed_count,
                "detection_count": self.detection_count,
                "detection_rate": detection_rate,
                "avg_processing_time": avg_processing_time,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(self.processed_count, 1)
            }
    
    def _update_metrics(self, processing_time: float, detected: bool = False, error: bool = False):
        """Update layer metrics."""
        with self.lock:
            self.processed_count += 1
            self.total_processing_time += processing_time
            
            if detected:
                self.detection_count += 1
            
            if error:
                self.error_count += 1


class SignatureMatchingLayer(DetectionLayerBase):
    """Layer 1: Signature-based detection using known attack signatures."""
    
    def __init__(self, signatures_path: Optional[Path] = None):
        super().__init__("signature_matching", DetectionPriority.HIGH)
        
        # Load threat signatures
        self.signatures = self._load_signatures(signatures_path)
        
        # Signature categories
        self.signature_categories = {
            "malware": [],
            "exploit": [],
            "attack_tools": [],
            "suspicious_patterns": [],
            "known_bad_ips": [],
            "malicious_domains": []
        }
        
        self._categorize_signatures()
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats using signature matching."""
        start_time = time.time()
        results = []
        
        try:
            # Convert context to searchable text
            search_text = self._context_to_text(context)
            
            # Check against all signatures
            for signature_id, signature_data in self.signatures.items():
                if self._match_signature(search_text, signature_data):
                    result = LayerResult(
                        layer=DetectionLayer.SIGNATURE_MATCHING,
                        threat_type=ThreatType(signature_data.get("threat_type", "malicious_payload")),
                        severity=SeverityLevel(signature_data.get("severity", "MEDIUM")),
                        confidence=signature_data.get("confidence", 0.9),
                        message=f"Signature match: {signature_data.get('description', signature_id)}",
                        evidence={
                            "signature_id": signature_id,
                            "signature_description": signature_data.get("description", ""),
                            "match_pattern": signature_data.get("pattern", ""),
                            "category": signature_data.get("category", "unknown")
                        },
                        processing_time=time.time() - start_time,
                        metadata={"signature_version": signature_data.get("version", "1.0")}
                    )
                    results.append(result)
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"Signature matching failed: {e}")
    
    def _load_signatures(self, signatures_path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
        """Load threat signatures from file or use defaults."""
        if signatures_path and signatures_path.exists():
            try:
                with open(signatures_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load signatures from {signatures_path}: {e}")
        
        # Default signatures for common threats
        return {
            "sql_injection_union": {
                "pattern": r"(?i)(union\s+select|union\s+all\s+select)",
                "threat_type": "sql_injection",
                "severity": "HIGH",
                "confidence": 0.95,
                "description": "SQL injection using UNION SELECT",
                "category": "exploit"
            },
            "xss_script_tag": {
                "pattern": r"(?i)<script[^>]*>.*?</script>",
                "threat_type": "xss_attack",
                "severity": "HIGH",
                "confidence": 0.9,
                "description": "XSS attack using script tags",
                "category": "exploit"
            },
            "command_injection": {
                "pattern": r"(?i)(;|\||\&\&|\|\|)\s*(rm|del|format|shutdown|reboot)",
                "threat_type": "command_injection",
                "severity": "CRITICAL",
                "confidence": 0.95,
                "description": "Command injection attempt",
                "category": "exploit"
            },
            "path_traversal": {
                "pattern": r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                "threat_type": "path_traversal",
                "severity": "HIGH",
                "confidence": 0.85,
                "description": "Path traversal attempt",
                "category": "exploit"
            },
            "prompt_injection": {
                "pattern": r"(?i)(ignore\s+previous|forget\s+instructions|new\s+instructions|system\s+prompt)",
                "threat_type": "prompt_injection",
                "severity": "HIGH",
                "confidence": 0.8,
                "description": "Prompt injection attempt",
                "category": "exploit"
            }
        }
    
    def _categorize_signatures(self):
        """Categorize signatures by type."""
        for sig_id, sig_data in self.signatures.items():
            category = sig_data.get("category", "suspicious_patterns")
            if category in self.signature_categories:
                self.signature_categories[category].append(sig_id)
    
    def _context_to_text(self, context: DetectionContext) -> str:
        """Convert detection context to searchable text."""
        text_parts = []
        
        # Add method name
        text_parts.append(context.method_name)
        
        # Add input data
        for key, value in context.inputs.items():
            text_parts.append(f"{key}: {str(value)}")
        
        # Add output data
        if context.outputs:
            text_parts.append(f"output: {str(context.outputs)}")
        
        # Add metadata
        for key, value in context.metadata.items():
            text_parts.append(f"{key}: {str(value)}")
        
        return " ".join(text_parts)
    
    def _match_signature(self, text: str, signature_data: Dict[str, Any]) -> bool:
        """Check if text matches signature pattern."""
        import re
        
        pattern = signature_data.get("pattern", "")
        if not pattern:
            return False
        
        try:
            return bool(re.search(pattern, text))
        except re.error:
            return False


class PatternDetectionLayer(DetectionLayerBase):
    """Layer 2: Advanced pattern detection using regex and heuristics."""
    
    def __init__(self):
        super().__init__("pattern_detection", DetectionPriority.HIGH)
        
        # Load existing detectors
        from .detectors import (
            SQLInjectionDetector,
            XSSDetector,
            CommandInjectionDetector,
            PathTraversalDetector,
            PromptInjectionDetector
        )
        
        # Initialize detectors (simplified config)
        class DummyConfig:
            def __init__(self):
                self.detection = type('obj', (object,), {'enabled': True, 'confidence_threshold': 0.5})()
        
        config = DummyConfig()
        self.detectors = [
            SQLInjectionDetector(config),
            XSSDetector(config),
            CommandInjectionDetector(config),
            PathTraversalDetector(config),
            PromptInjectionDetector(config)
        ]
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats using pattern matching."""
        start_time = time.time()
        results = []
        
        try:
            # Convert context to string for pattern matching
            search_text = self._context_to_search_text(context)
            
            # Run all pattern detectors
            for detector in self.detectors:
                try:
                    detection_result = detector._detect_impl(search_text, context.metadata)
                    
                    if detection_result:
                        result = LayerResult(
                            layer=DetectionLayer.PATTERN_DETECTION,
                            threat_type=detection_result.threat_type,
                            severity=detection_result.severity,
                            confidence=detection_result.confidence,
                            message=detection_result.message,
                            evidence={
                                "detector": detector.__class__.__name__,
                                "pattern_matches": detection_result.evidence.get("patterns", []),
                                "confidence_breakdown": detection_result.evidence.get("confidence_breakdown", {}),
                                "raw_data": search_text[:500]  # Limit size
                            },
                            processing_time=time.time() - start_time,
                            metadata={"detector_version": "1.0"}
                        )
                        results.append(result)
                        
                except Exception as e:
                    logging.warning(f"Pattern detector {detector.__class__.__name__} failed: {e}")
                    continue
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"Pattern detection failed: {e}")
    
    def _context_to_search_text(self, context: DetectionContext) -> str:
        """Convert context to text for pattern matching."""
        text_parts = []
        
        # Add inputs
        for key, value in context.inputs.items():
            if isinstance(value, str):
                text_parts.append(value)
            else:
                text_parts.append(str(value))
        
        # Add outputs
        if context.outputs:
            if isinstance(context.outputs, str):
                text_parts.append(context.outputs)
            else:
                text_parts.append(str(context.outputs))
        
        return " ".join(text_parts)


class BehavioralAnalysisLayer(DetectionLayerBase):
    """Layer 3: Behavioral analysis and anomaly detection."""
    
    def __init__(self, behavioral_analyzer: Optional[BehavioralAnalyzer] = None):
        super().__init__("behavioral_analysis", DetectionPriority.MEDIUM)
        self.behavioral_analyzer = behavioral_analyzer
        
        # Behavioral pattern cache
        self.pattern_cache = {}
        self.anomaly_threshold = 0.7
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats using behavioral analysis."""
        start_time = time.time()
        results = []
        
        try:
            if not self.behavioral_analyzer:
                return results
            
            # Record behavioral event
            self.behavioral_analyzer.record_behavioral_event(
                method_name=context.method_name,
                parameters=context.inputs,
                execution_time=context.metadata.get("execution_time", 0.0),
                result_type=type(context.outputs).__name__ if context.outputs else "None",
                session_id=context.session_id,
                user_id=context.user_id,
                context=context.metadata
            )
            
            # Analyze patterns
            analysis = self.behavioral_analyzer.analyze_behavioral_patterns()
            
            # Check for anomalies
            if analysis.get("anomalies", {}).get("total_detected", 0) > 0:
                recent_anomalies = analysis["anomalies"].get("recent_anomalies", [])
                
                for anomaly_data in recent_anomalies[-5:]:  # Last 5 anomalies
                    if anomaly_data.get("confidence", 0) >= self.anomaly_threshold:
                        result = LayerResult(
                            layer=DetectionLayer.BEHAVIORAL_ANALYSIS,
                            threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                            severity=SeverityLevel(anomaly_data.get("severity", "MEDIUM")),
                            confidence=anomaly_data.get("confidence", 0.5),
                            message=f"Behavioral anomaly: {anomaly_data.get('description', 'Unknown anomaly')}",
                            evidence={
                                "anomaly_type": anomaly_data.get("anomaly_type", "unknown"),
                                "baseline_deviation": anomaly_data.get("baseline_deviation", 0.0),
                                "risk_score": anomaly_data.get("risk_score", 0.0),
                                "behavioral_evidence": anomaly_data.get("evidence", {})
                            },
                            processing_time=time.time() - start_time,
                            metadata={"analysis_timestamp": analysis.get("analysis_timestamp", "")}
                        )
                        results.append(result)
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"Behavioral analysis failed: {e}")


class MLDetectionLayer(DetectionLayerBase):
    """Layer 4: Machine learning-based threat detection."""
    
    def __init__(self, model_path: Optional[Path] = None):
        super().__init__("ml_detection", DetectionPriority.MEDIUM)
        
        # ML model placeholder - in production, load actual ML models
        self.model = None
        self.feature_extractor = None
        self.model_loaded = False
        
        # Threat classification thresholds
        self.classification_thresholds = {
            ThreatType.SQL_INJECTION: 0.8,
            ThreatType.XSS_ATTACK: 0.75,
            ThreatType.COMMAND_INJECTION: 0.85,
            ThreatType.PROMPT_INJECTION: 0.7,
            ThreatType.BEHAVIORAL_ANOMALY: 0.65
        }
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats using machine learning."""
        start_time = time.time()
        results = []
        
        try:
            # For now, implement rule-based ML simulation
            # In production, this would use actual ML models
            features = self._extract_features(context)
            predictions = self._classify_threats(features)
            
            for threat_type, confidence in predictions.items():
                threshold = self.classification_thresholds.get(threat_type, 0.7)
                
                if confidence >= threshold:
                    severity = self._determine_severity(confidence)
                    
                    result = LayerResult(
                        layer=DetectionLayer.ML_DETECTION,
                        threat_type=threat_type,
                        severity=severity,
                        confidence=confidence,
                        message=f"ML-based detection: {threat_type.value} (confidence: {confidence:.2f})",
                        evidence={
                            "ml_features": features,
                            "prediction_confidence": confidence,
                            "threshold": threshold,
                            "model_version": "1.0"
                        },
                        processing_time=time.time() - start_time,
                        metadata={"ml_model": "threat_classifier_v1"}
                    )
                    results.append(result)
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"ML detection failed: {e}")
    
    def _extract_features(self, context: DetectionContext) -> Dict[str, float]:
        """Extract features for ML classification."""
        features = {}
        
        # Text-based features
        text_content = self._get_text_content(context)
        features["text_length"] = len(text_content)
        features["special_char_ratio"] = self._calculate_special_char_ratio(text_content)
        features["sql_keyword_count"] = self._count_sql_keywords(text_content)
        features["script_tag_count"] = text_content.lower().count("<script")
        features["command_char_count"] = sum(text_content.count(c) for c in [";", "|", "&", "$"])
        
        # Behavioral features
        features["method_name_length"] = len(context.method_name)
        features["param_count"] = len(context.inputs)
        features["execution_time"] = context.metadata.get("execution_time", 0.0)
        
        # Normalize features
        return self._normalize_features(features)
    
    def _classify_threats(self, features: Dict[str, float]) -> Dict[ThreatType, float]:
        """Classify threats based on features (ML simulation)."""
        predictions = {}
        
        # SQL Injection prediction
        sql_score = (
            features.get("sql_keyword_count", 0) * 0.4 +
            features.get("special_char_ratio", 0) * 0.3 +
            features.get("text_length", 0) * 0.1
        )
        predictions[ThreatType.SQL_INJECTION] = min(1.0, sql_score)
        
        # XSS prediction
        xss_score = (
            features.get("script_tag_count", 0) * 0.5 +
            features.get("special_char_ratio", 0) * 0.3
        )
        predictions[ThreatType.XSS_ATTACK] = min(1.0, xss_score)
        
        # Command Injection prediction
        cmd_score = (
            features.get("command_char_count", 0) * 0.4 +
            features.get("special_char_ratio", 0) * 0.3
        )
        predictions[ThreatType.COMMAND_INJECTION] = min(1.0, cmd_score)
        
        # Behavioral anomaly prediction
        behavioral_score = (
            features.get("execution_time", 0) * 0.3 +
            features.get("param_count", 0) * 0.2
        )
        predictions[ThreatType.BEHAVIORAL_ANOMALY] = min(1.0, behavioral_score)
        
        return predictions
    
    def _get_text_content(self, context: DetectionContext) -> str:
        """Extract text content from context."""
        text_parts = []
        
        for value in context.inputs.values():
            if isinstance(value, str):
                text_parts.append(value)
        
        if context.outputs and isinstance(context.outputs, str):
            text_parts.append(context.outputs)
        
        return " ".join(text_parts)
    
    def _calculate_special_char_ratio(self, text: str) -> float:
        """Calculate ratio of special characters in text."""
        if not text:
            return 0.0
        
        special_chars = set("!@#$%^&*()[]{}|\\:;\"'<>?/.,`~")
        special_count = sum(1 for c in text if c in special_chars)
        
        return special_count / len(text)
    
    def _count_sql_keywords(self, text: str) -> float:
        """Count SQL keywords in text."""
        sql_keywords = [
            "select", "insert", "update", "delete", "drop", "create", "alter",
            "union", "where", "from", "join", "having", "group", "order"
        ]
        
        text_lower = text.lower()
        count = sum(text_lower.count(keyword) for keyword in sql_keywords)
        
        return min(1.0, count / 5.0)  # Normalize
    
    def _normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Normalize features to [0, 1] range."""
        normalized = {}
        
        for key, value in features.items():
            if key == "text_length":
                normalized[key] = min(1.0, value / 10000.0)  # Normalize to 10k chars
            elif key == "param_count":
                normalized[key] = min(1.0, value / 20.0)  # Normalize to 20 params
            elif key == "execution_time":
                normalized[key] = min(1.0, value / 60.0)  # Normalize to 60 seconds
            else:
                normalized[key] = min(1.0, value)
        
        return normalized
    
    def _determine_severity(self, confidence: float) -> SeverityLevel:
        """Determine severity based on confidence."""
        if confidence >= 0.9:
            return SeverityLevel.CRITICAL
        elif confidence >= 0.8:
            return SeverityLevel.HIGH
        elif confidence >= 0.6:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW


class ThreatIntelligenceLayer(DetectionLayerBase):
    """Layer 5: Threat intelligence and IOC matching."""
    
    def __init__(self, threat_feeds: Optional[List[str]] = None):
        super().__init__("threat_intelligence", DetectionPriority.LOW)
        
        # Threat intelligence feeds
        self.threat_feeds = threat_feeds or []
        self.ioc_cache = {}
        self.last_update = None
        
        # IOC categories
        self.ioc_types = {
            "ip_addresses": set(),
            "domains": set(),
            "file_hashes": set(),
            "urls": set(),
            "patterns": []
        }
        
        # Load initial threat intelligence
        self._load_threat_intelligence()
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Detect threats using threat intelligence."""
        start_time = time.time()
        results = []
        
        try:
            # Update threat intelligence if needed
            await self._update_threat_intelligence()
            
            # Extract IOCs from context
            iocs = self._extract_iocs(context)
            
            # Check IOCs against threat intelligence
            for ioc_type, ioc_value in iocs.items():
                if self._is_malicious_ioc(ioc_type, ioc_value):
                    threat_info = self._get_threat_info(ioc_type, ioc_value)
                    
                    result = LayerResult(
                        layer=DetectionLayer.THREAT_INTELLIGENCE,
                        threat_type=ThreatType(threat_info.get("threat_type", "malicious_payload")),
                        severity=SeverityLevel(threat_info.get("severity", "HIGH")),
                        confidence=threat_info.get("confidence", 0.9),
                        message=f"Threat intelligence match: {ioc_type} - {ioc_value}",
                        evidence={
                            "ioc_type": ioc_type,
                            "ioc_value": ioc_value,
                            "threat_source": threat_info.get("source", "unknown"),
                            "first_seen": threat_info.get("first_seen", ""),
                            "last_seen": threat_info.get("last_seen", "")
                        },
                        processing_time=time.time() - start_time,
                        metadata={"threat_feed_version": "1.0"}
                    )
                    results.append(result)
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"Threat intelligence detection failed: {e}")
    
    def _load_threat_intelligence(self):
        """Load threat intelligence from feeds."""
        # Placeholder for threat intelligence loading
        # In production, this would load from actual threat feeds
        
        # Sample malicious IOCs
        self.ioc_types["ip_addresses"].update([
            "192.168.1.100",  # Example malicious IP
            "10.0.0.50"
        ])
        
        self.ioc_types["domains"].update([
            "malicious-domain.com",
            "evil-site.net"
        ])
        
        self.ioc_types["patterns"].extend([
            {"pattern": r"(?i)download.*malware", "threat_type": "malware", "severity": "HIGH"},
            {"pattern": r"(?i)exploit.*kit", "threat_type": "exploit", "severity": "HIGH"}
        ])
    
    async def _update_threat_intelligence(self):
        """Update threat intelligence from feeds."""
        # Check if update is needed (every hour)
        now = datetime.now(timezone.utc)
        if self.last_update and (now - self.last_update).total_seconds() < 3600:
            return
        
        # Update threat intelligence
        # In production, this would fetch from actual threat feeds
        self.last_update = now
    
    def _extract_iocs(self, context: DetectionContext) -> Dict[str, str]:
        """Extract IOCs from detection context."""
        iocs = {}
        
        # Extract text content
        text_content = self._get_text_content(context)
        
        # Extract IP addresses
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_matches = re.findall(ip_pattern, text_content)
        for ip in ip_matches:
            iocs[f"ip_{ip}"] = ip
        
        # Extract domains
        domain_pattern = r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        domain_matches = re.findall(domain_pattern, text_content)
        for domain in domain_matches:
            iocs[f"domain_{domain}"] = domain
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?'
        url_matches = re.findall(url_pattern, text_content)
        for url in url_matches:
            iocs[f"url_{url}"] = url
        
        return iocs
    
    def _is_malicious_ioc(self, ioc_type: str, ioc_value: str) -> bool:
        """Check if IOC is malicious."""
        if ioc_type.startswith("ip_"):
            return ioc_value in self.ioc_types["ip_addresses"]
        elif ioc_type.startswith("domain_"):
            return ioc_value in self.ioc_types["domains"]
        elif ioc_type.startswith("url_"):
            return any(domain in ioc_value for domain in self.ioc_types["domains"])
        
        return False
    
    def _get_threat_info(self, ioc_type: str, ioc_value: str) -> Dict[str, Any]:
        """Get threat information for IOC."""
        return {
            "threat_type": "malicious_payload",
            "severity": "HIGH",
            "confidence": 0.9,
            "source": "threat_intelligence",
            "first_seen": "2024-01-01T00:00:00Z",
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_text_content(self, context: DetectionContext) -> str:
        """Get text content from context."""
        text_parts = []
        
        for value in context.inputs.values():
            if isinstance(value, str):
                text_parts.append(value)
        
        if context.outputs and isinstance(context.outputs, str):
            text_parts.append(context.outputs)
        
        return " ".join(text_parts)


class RiskScoringLayer(DetectionLayerBase):
    """Layer 6: Risk scoring and threat prioritization."""
    
    def __init__(self):
        super().__init__("risk_scoring", DetectionPriority.CRITICAL)
        
        # Risk scoring weights
        self.layer_weights = {
            DetectionLayer.SIGNATURE_MATCHING: 0.25,
            DetectionLayer.PATTERN_DETECTION: 0.20,
            DetectionLayer.BEHAVIORAL_ANALYSIS: 0.15,
            DetectionLayer.ML_DETECTION: 0.20,
            DetectionLayer.THREAT_INTELLIGENCE: 0.20
        }
        
        # Severity multipliers
        self.severity_multipliers = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.LOW: 0.4
        }
        
        # Threat type risk factors
        self.threat_risk_factors = {
            ThreatType.SQL_INJECTION: 0.9,
            ThreatType.COMMAND_INJECTION: 0.95,
            ThreatType.XSS_ATTACK: 0.7,
            ThreatType.PATH_TRAVERSAL: 0.8,
            ThreatType.PROMPT_INJECTION: 0.6,
            ThreatType.BEHAVIORAL_ANOMALY: 0.5,
            ThreatType.MALICIOUS_PAYLOAD: 0.8
        }
    
    async def detect(self, context: DetectionContext) -> List[LayerResult]:
        """Calculate risk scores for detected threats."""
        start_time = time.time()
        results = []
        
        try:
            # Get results from previous layers
            previous_results = self._get_previous_layer_results(context)
            
            if not previous_results:
                return results
            
            # Calculate comprehensive risk score
            risk_score = self._calculate_risk_score(previous_results, context)
            
            # Determine overall threat level
            threat_level = self._determine_threat_level(risk_score)
            
            # Create risk scoring result
            result = LayerResult(
                layer=DetectionLayer.RISK_SCORING,
                threat_type=self._get_primary_threat_type(previous_results),
                severity=threat_level,
                confidence=self._calculate_confidence(previous_results),
                message=f"Risk assessment: {risk_score:.2f} (threat level: {threat_level.value})",
                evidence={
                    "risk_score": risk_score,
                    "contributing_layers": [r.layer.value for r in previous_results],
                    "threat_breakdown": self._get_threat_breakdown(previous_results),
                    "risk_factors": self._get_risk_factors(previous_results, context)
                },
                processing_time=time.time() - start_time,
                metadata={"risk_model_version": "1.0"}
            )
            
            results.append(result)
            
            self._update_metrics(time.time() - start_time, len(results) > 0)
            return results
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, error=True)
            raise DetectionError(f"Risk scoring failed: {e}")
    
    def _get_previous_layer_results(self, context: DetectionContext) -> List[LayerResult]:
        """Get results from previous detection layers."""
        # This would be populated by the multi-layer engine
        return context.get_layer_context(DetectionLayer.RISK_SCORING).get("previous_results", [])
    
    def _calculate_risk_score(self, results: List[LayerResult], context: DetectionContext) -> float:
        """Calculate comprehensive risk score."""
        if not results:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for result in results:
            # Get layer weight
            layer_weight = self.layer_weights.get(result.layer, 0.1)
            
            # Get severity multiplier
            severity_multiplier = self.severity_multipliers.get(result.severity, 0.5)
            
            # Get threat type risk factor
            threat_risk_factor = self.threat_risk_factors.get(result.threat_type, 0.5)
            
            # Calculate weighted score
            score = result.confidence * severity_multiplier * threat_risk_factor * layer_weight
            total_score += score
            total_weight += layer_weight
        
        # Normalize score
        if total_weight > 0:
            base_score = total_score / total_weight
        else:
            base_score = 0.0
        
        # Apply context-based adjustments
        context_multiplier = self._get_context_multiplier(context)
        
        final_score = min(1.0, base_score * context_multiplier)
        
        return final_score
    
    def _determine_threat_level(self, risk_score: float) -> SeverityLevel:
        """Determine threat level based on risk score."""
        if risk_score >= 0.8:
            return SeverityLevel.CRITICAL
        elif risk_score >= 0.6:
            return SeverityLevel.HIGH
        elif risk_score >= 0.4:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _get_primary_threat_type(self, results: List[LayerResult]) -> ThreatType:
        """Get primary threat type from results."""
        if not results:
            return ThreatType.MALICIOUS_PAYLOAD
        
        # Find highest confidence threat
        highest_confidence_result = max(results, key=lambda r: r.confidence)
        return highest_confidence_result.threat_type
    
    def _calculate_confidence(self, results: List[LayerResult]) -> float:
        """Calculate overall confidence from layer results."""
        if not results:
            return 0.0
        
        # Use weighted average of confidences
        total_confidence = 0.0
        total_weight = 0.0
        
        for result in results:
            weight = self.layer_weights.get(result.layer, 0.1)
            total_confidence += result.confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _get_threat_breakdown(self, results: List[LayerResult]) -> Dict[str, Any]:
        """Get breakdown of threats by type and layer."""
        breakdown = {
            "by_threat_type": defaultdict(int),
            "by_layer": defaultdict(int),
            "by_severity": defaultdict(int)
        }
        
        for result in results:
            breakdown["by_threat_type"][result.threat_type.value] += 1
            breakdown["by_layer"][result.layer.value] += 1
            breakdown["by_severity"][result.severity.value] += 1
        
        return dict(breakdown)
    
    def _get_risk_factors(self, results: List[LayerResult], context: DetectionContext) -> Dict[str, Any]:
        """Get risk factors that contributed to the score."""
        factors = {
            "multiple_layer_detections": len(results) > 1,
            "high_confidence_detections": sum(1 for r in results if r.confidence > 0.8),
            "critical_threats": sum(1 for r in results if r.severity == SeverityLevel.CRITICAL),
            "method_name": context.method_name,
            "session_context": bool(context.session_id),
            "user_context": bool(context.user_id)
        }
        
        return factors
    
    def _get_context_multiplier(self, context: DetectionContext) -> float:
        """Get context-based risk multiplier."""
        multiplier = 1.0
        
        # Increase risk for sensitive methods
        sensitive_methods = ["execute", "eval", "system", "shell", "command"]
        if any(method in context.method_name.lower() for method in sensitive_methods):
            multiplier *= 1.2
        
        # Increase risk for privileged operations
        if context.metadata.get("privileged", False):
            multiplier *= 1.3
        
        # Increase risk for external inputs
        if context.metadata.get("external_input", False):
            multiplier *= 1.1
        
        return multiplier


class MultiLayerDetectionEngine:
    """
    Multi-layer detection engine coordinating all detection layers.
    
    This engine implements a sophisticated 6-layer defense system for
    comprehensive threat detection in AI agents.
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        behavioral_analyzer: Optional[BehavioralAnalyzer] = None,
        enable_correlation: bool = True,
        max_processing_time: float = 30.0
    ):
        """
        Initialize multi-layer detection engine.
        
        Args:
            agent_id: ID of the agent being monitored
            logger: Security logger instance
            behavioral_analyzer: Behavioral analyzer instance
            enable_correlation: Enable cross-layer correlation
            max_processing_time: Maximum processing time per detection
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"multi_layer_engine_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        self.enable_correlation = enable_correlation
        self.max_processing_time = max_processing_time
        
        # Initialize detection layers
        self.layers = [
            SignatureMatchingLayer(),
            PatternDetectionLayer(),
            BehavioralAnalysisLayer(behavioral_analyzer),
            MLDetectionLayer(),
            ThreatIntelligenceLayer(),
            RiskScoringLayer()
        ]
        
        # Processing queue and workers
        self.processing_queue = asyncio.Queue()
        self.result_cache = {}
        self.correlation_engine = ThreatCorrelationEngine() if enable_correlation else None
        
        # Performance metrics
        self.metrics = {
            "total_detections": 0,
            "layer_performance": {},
            "correlation_stats": {},
            "processing_times": deque(maxlen=1000)
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        self.logger.info(f"Multi-layer detection engine initialized for agent {agent_id}")
    
    async def detect_threats(self, context: DetectionContext) -> List[SecurityEvent]:
        """
        Run threat detection across all layers.
        
        Args:
            context: Detection context
            
        Returns:
            List of security events
        """
        start_time = time.time()
        
        try:
            # Run detection layers in parallel
            layer_results = await self._run_detection_layers(context)
            
            # Correlate results across layers
            if self.enable_correlation and self.correlation_engine:
                correlated_threats = await self.correlation_engine.correlate_threats(
                    layer_results, context
                )
                
                # Convert correlated threats to security events
                events = [threat.to_security_event(context) for threat in correlated_threats]
            else:
                # Convert layer results to security events
                events = [result.to_security_event(self.agent_id, context) for result in layer_results]
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, len(events))
            
            self.logger.info(
                f"Multi-layer detection completed: {len(events)} threats detected in {processing_time:.3f}s"
            )
            
            return events
            
        except Exception as e:
            self.logger.error(f"Multi-layer detection failed: {e}")
            raise DetectionError(f"Multi-layer detection failed: {e}")
    
    async def _run_detection_layers(self, context: DetectionContext) -> List[LayerResult]:
        """Run detection across all enabled layers."""
        tasks = []
        
        for layer in self.layers:
            if layer.enabled:
                task = asyncio.create_task(
                    asyncio.wait_for(layer.detect(context), timeout=layer.timeout)
                )
                tasks.append((layer, task))
        
        # Wait for all tasks to complete
        results = []
        for layer, task in tasks:
            try:
                layer_results = await task
                results.extend(layer_results)
                
                # Store results for risk scoring layer
                if layer.layer_name != "risk_scoring":
                    context.set_layer_context(
                        DetectionLayer.RISK_SCORING,
                        {"previous_results": results}
                    )
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"Layer {layer.layer_name} timed out")
            except Exception as e:
                self.logger.error(f"Layer {layer.layer_name} failed: {e}")
        
        return results
    
    def _update_metrics(self, processing_time: float, threat_count: int):
        """Update engine metrics."""
        with self.lock:
            self.metrics["total_detections"] += threat_count
            self.metrics["processing_times"].append(processing_time)
            
            # Update layer performance metrics
            for layer in self.layers:
                layer_metrics = layer.get_metrics()
                self.metrics["layer_performance"][layer.layer_name] = layer_metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get engine performance metrics."""
        with self.lock:
            avg_processing_time = (
                sum(self.metrics["processing_times"]) / len(self.metrics["processing_times"])
                if self.metrics["processing_times"] else 0.0
            )
            
            return {
                "agent_id": self.agent_id,
                "total_detections": self.metrics["total_detections"],
                "avg_processing_time": avg_processing_time,
                "layer_performance": self.metrics["layer_performance"],
                "correlation_stats": self.metrics["correlation_stats"],
                "enabled_layers": [layer.layer_name for layer in self.layers if layer.enabled]
            }
    
    def add_layer(self, layer: DetectionLayerBase):
        """Add custom detection layer."""
        self.layers.append(layer)
        self.logger.info(f"Added custom detection layer: {layer.layer_name}")
    
    def enable_layer(self, layer_name: str):
        """Enable detection layer."""
        for layer in self.layers:
            if layer.layer_name == layer_name:
                layer.enabled = True
                self.logger.info(f"Enabled detection layer: {layer_name}")
                return
        
        self.logger.warning(f"Layer not found: {layer_name}")
    
    def disable_layer(self, layer_name: str):
        """Disable detection layer."""
        for layer in self.layers:
            if layer.layer_name == layer_name:
                layer.enabled = False
                self.logger.info(f"Disabled detection layer: {layer_name}")
                return
        
        self.logger.warning(f"Layer not found: {layer_name}")


class ThreatCorrelationEngine:
    """Engine for correlating threats across multiple detection layers."""
    
    def __init__(self):
        self.correlation_rules = self._load_correlation_rules()
        self.correlation_window = 300  # 5 minutes
        self.min_correlation_score = 0.6
    
    async def correlate_threats(
        self,
        layer_results: List[LayerResult],
        context: DetectionContext
    ) -> List[CorrelatedThreat]:
        """Correlate threats across detection layers."""
        if len(layer_results) < 2:
            # No correlation possible with single result
            return [self._single_result_to_threat(result, context) for result in layer_results]
        
        # Group results by threat type
        threat_groups = defaultdict(list)
        for result in layer_results:
            threat_groups[result.threat_type].append(result)
        
        correlated_threats = []
        
        for threat_type, results in threat_groups.items():
            if len(results) > 1:
                # Multiple layers detected same threat type
                correlated_threat = self._correlate_same_threat_type(results, context)
                correlated_threats.append(correlated_threat)
            else:
                # Single detection
                threat = self._single_result_to_threat(results[0], context)
                correlated_threats.append(threat)
        
        return correlated_threats
    
    def _correlate_same_threat_type(
        self,
        results: List[LayerResult],
        context: DetectionContext
    ) -> CorrelatedThreat:
        """Correlate results of the same threat type."""
        # Calculate correlation score
        correlation_score = self._calculate_correlation_score(results)
        
        # Calculate combined confidence
        combined_confidence = self._calculate_combined_confidence(results)
        
        # Determine severity (highest wins)
        max_severity = max(results, key=lambda r: self._severity_to_int(r.severity)).severity
        
        # Create correlated threat
        return CorrelatedThreat(
            threat_type=results[0].threat_type,
            severity=max_severity,
            confidence=combined_confidence,
            message=f"Correlated threat detected by {len(results)} layers: {results[0].threat_type.value}",
            agent_id=context.agent_id,
            timestamp=context.timestamp or datetime.now(timezone.utc),
            layer_results=results,
            correlation_score=correlation_score,
            risk_score=self._calculate_risk_score(results, correlation_score)
        )
    
    def _single_result_to_threat(
        self,
        result: LayerResult,
        context: DetectionContext
    ) -> CorrelatedThreat:
        """Convert single result to correlated threat."""
        return CorrelatedThreat(
            threat_type=result.threat_type,
            severity=result.severity,
            confidence=result.confidence,
            message=result.message,
            agent_id=context.agent_id,
            timestamp=context.timestamp or datetime.now(timezone.utc),
            layer_results=[result],
            correlation_score=0.0,
            risk_score=result.confidence * self._severity_to_float(result.severity)
        )
    
    def _calculate_correlation_score(self, results: List[LayerResult]) -> float:
        """Calculate correlation score for multiple results."""
        if len(results) < 2:
            return 0.0
        
        # Base score on number of layers
        base_score = min(1.0, len(results) / 4.0)  # Max at 4 layers
        
        # Adjust based on confidence consistency
        confidences = [r.confidence for r in results]
        confidence_std = np.std(confidences) if len(confidences) > 1 else 0.0
        consistency_bonus = max(0.0, 1.0 - confidence_std)
        
        return base_score * consistency_bonus
    
    def _calculate_combined_confidence(self, results: List[LayerResult]) -> float:
        """Calculate combined confidence from multiple results."""
        if not results:
            return 0.0
        
        # Use weighted average based on layer reliability
        layer_weights = {
            DetectionLayer.SIGNATURE_MATCHING: 0.3,
            DetectionLayer.PATTERN_DETECTION: 0.25,
            DetectionLayer.BEHAVIORAL_ANALYSIS: 0.15,
            DetectionLayer.ML_DETECTION: 0.2,
            DetectionLayer.THREAT_INTELLIGENCE: 0.1
        }
        
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for result in results:
            weight = layer_weights.get(result.layer, 0.1)
            total_weighted_confidence += result.confidence * weight
            total_weight += weight
        
        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _calculate_risk_score(self, results: List[LayerResult], correlation_score: float) -> float:
        """Calculate risk score for correlated threat."""
        # Base risk on highest confidence
        base_risk = max(result.confidence for result in results)
        
        # Adjust based on correlation
        correlation_bonus = correlation_score * 0.3
        
        # Adjust based on severity
        max_severity = max(results, key=lambda r: self._severity_to_int(r.severity)).severity
        severity_multiplier = self._severity_to_float(max_severity)
        
        return min(1.0, (base_risk + correlation_bonus) * severity_multiplier)
    
    def _severity_to_int(self, severity: SeverityLevel) -> int:
        """Convert severity to integer for comparison."""
        return {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }.get(severity, 1)
    
    def _severity_to_float(self, severity: SeverityLevel) -> float:
        """Convert severity to float for calculations."""
        return {
            SeverityLevel.LOW: 0.4,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.CRITICAL: 1.0
        }.get(severity, 0.5)
    
    def _load_correlation_rules(self) -> Dict[str, Any]:
        """Load correlation rules."""
        # Placeholder for correlation rules
        return {
            "same_threat_multiple_layers": {
                "min_layers": 2,
                "confidence_boost": 0.2,
                "severity_escalation": True
            },
            "attack_chain_detection": {
                "enabled": True,
                "time_window": 300,
                "min_correlation_score": 0.6
            }
        } 