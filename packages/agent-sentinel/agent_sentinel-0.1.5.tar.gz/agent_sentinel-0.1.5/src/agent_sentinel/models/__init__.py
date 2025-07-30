"""
Models Package

Data models and domain objects following industry standards.
Models contain only data and validation logic, no business logic.
"""

from .detection_models import (
    DetectionContext,
    DetectionResult,
    DetectionRequest,
    DetectionStats,
    DetectionStatus,
    ThreatLevel
)

__all__ = [
    "DetectionContext",
    "DetectionResult", 
    "DetectionRequest",
    "DetectionStats",
    "DetectionStatus",
    "ThreatLevel",
] 