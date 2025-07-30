"""
Core types for AgentSentinel SDK.

This module defines shared types used across the SDK to avoid circular imports.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .constants import ThreatType, SeverityLevel


class SecurityEvent:
    """
    Represents a security event detected by AgentSentinel.
    
    This class encapsulates all information about a security incident,
    including threat details, context, and metadata.
    """
    
    def __init__(
        self,
        threat_type: ThreatType,
        severity: SeverityLevel,
        message: str,
        confidence: float,
        context: Dict[str, Any],
        agent_id: str,
        timestamp: Optional[datetime] = None,
        detection_method: str = "unknown",
        raw_data: Optional[str] = None,
    ) -> None:
        """
        Initialize a security event.
        
        Args:
            threat_type: Type of threat detected
            severity: Severity level of the threat
            message: Human-readable description of the threat
            confidence: Confidence score (0.0-1.0)
            context: Additional context about the threat
            agent_id: ID of the agent where threat was detected
            timestamp: When the threat was detected
            detection_method: Method used to detect the threat
            raw_data: Raw data that triggered the detection
        """
        self.threat_type = threat_type
        self.severity = severity
        self.message = message
        self.confidence = confidence
        self.context = context
        self.agent_id = agent_id
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.detection_method = detection_method
        self.raw_data = raw_data
        self.event_id = f"{agent_id}_{int(self.timestamp.timestamp() * 1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert security event to dictionary for logging/serialization."""
        return {
            "event_id": self.event_id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "confidence": self.confidence,
            "context": self.context,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "detection_method": self.detection_method,
            "raw_data": self.raw_data,
        }
    
    def __str__(self) -> str:
        """String representation of the security event."""
        return f"SecurityEvent({self.threat_type.value}, {self.severity.value}, {self.confidence:.2f})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SecurityEvent(threat_type={self.threat_type.value}, severity={self.severity.value}, confidence={self.confidence})" 