"""
Detection Models

Data models and types for the detection engine, following industry standards
for clean separation of concerns and single responsibility principle.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core.constants import ThreatType, SeverityLevel, MAX_INPUT_SIZE
from ..core.exceptions import DetectionError, ValidationError


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


@dataclass
class DetectionRequest:
    """Request for threat detection analysis."""
    
    data: str
    context: DetectionContext
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "data_length": len(self.data),
            "context": self.context.to_dict()
        }


@dataclass
class DetectionStats:
    """Statistics for detection operations."""
    
    total_requests: int = 0
    successful_detections: int = 0
    failed_detections: int = 0
    avg_processing_time_ms: float = 0.0
    threats_detected: int = 0
    false_positives: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_detections": self.successful_detections,
            "failed_detections": self.failed_detections,
            "avg_processing_time_ms": self.avg_processing_time_ms,
            "threats_detected": self.threats_detected,
            "false_positives": self.false_positives,
            "success_rate": (
                self.successful_detections / self.total_requests 
                if self.total_requests > 0 else 0.0
            ),
            "threat_detection_rate": (
                self.threats_detected / self.successful_detections 
                if self.successful_detections > 0 else 0.0
            )
        } 