"""
Custom exceptions for AgentSentinel.

This module defines the exception hierarchy used throughout the SDK.
"""

from typing import Any, Dict, Optional


class AgentSentinelError(Exception):
    """Base exception for all AgentSentinel errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ConfigurationError(AgentSentinelError):
    """Raised when there's an error in configuration."""

    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_path = config_path
        self.config_key = config_key
        if config_path:
            self.details["config_path"] = config_path
        if config_key:
            self.details["config_key"] = config_key


class SecurityError(AgentSentinelError):
    """Raised when a security threat is detected."""

    def __init__(
        self,
        message: str,
        threat_type: Optional[str] = None,
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="SECURITY_ERROR", **kwargs)
        self.threat_type = threat_type
        self.severity = severity
        self.confidence = confidence
        if threat_type:
            self.details["threat_type"] = threat_type
        if severity:
            self.details["severity"] = severity
        if confidence is not None:
            self.details["confidence"] = confidence


class DetectionError(AgentSentinelError):
    """Raised when there's an error in the detection engine."""

    def __init__(
        self,
        message: str,
        detector_name: Optional[str] = None,
        rule_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="DETECTION_ERROR", **kwargs)
        self.detector_name = detector_name
        self.rule_name = rule_name
        if detector_name:
            self.details["detector_name"] = detector_name
        if rule_name:
            self.details["rule_name"] = rule_name


class RateLimitError(AgentSentinelError):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        current_rate: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        self.limit = limit
        self.window = window
        self.current_rate = current_rate
        if limit is not None:
            self.details["limit"] = limit
        if window is not None:
            self.details["window"] = window
        if current_rate is not None:
            self.details["current_rate"] = current_rate


class ValidationError(AgentSentinelError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field_name = field_name
        self.field_value = field_value
        if field_name:
            self.details["field_name"] = field_name
        if field_value is not None:
            self.details["field_value"] = str(field_value)  # Convert to string for logging


class WeaveError(AgentSentinelError):
    """Raised when there's an error with Weave integration."""

    def __init__(
        self,
        message: str,
        project_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="WEAVE_ERROR", **kwargs)
        self.project_name = project_name
        if project_name:
            self.details["project_name"] = project_name


class AlertError(AgentSentinelError):
    """Raised when there's an error with alert handling."""

    def __init__(
        self,
        message: str,
        alert_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="ALERT_ERROR", **kwargs)
        self.alert_type = alert_type
        if alert_type:
            self.details["alert_type"] = alert_type


class ThreatIntelligenceError(AgentSentinelError):
    """Raised when there's an error with threat intelligence operations."""

    def __init__(
        self,
        message: str,
        service_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, error_code="THREAT_INTELLIGENCE_ERROR", **kwargs)
        self.service_type = service_type
        if service_type:
            self.details["service_type"] = service_type 