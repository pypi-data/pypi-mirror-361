"""
Detection module for AgentSentinel.

This module contains the threat detection engine and specialized detectors
for various security threats like SQL injection, XSS, command injection, etc.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import DetectionEngine, DetectionResult
    from .detectors import (
        SQLInjectionDetector,
        XSSDetector,
        CommandInjectionDetector,
        PathTraversalDetector,
        PromptInjectionDetector,
    )

__all__ = [
    "DetectionEngine",
    "DetectionResult",
    "SQLInjectionDetector",
    "XSSDetector",
    "CommandInjectionDetector",
    "PathTraversalDetector",
    "PromptInjectionDetector",
] 