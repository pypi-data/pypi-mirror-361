"""
Security constants for AgentSentinel.

This module defines the core security constants used throughout the SDK,
including threat types, severity levels, and detection patterns.
"""

from enum import Enum
from typing import Any, Dict, List, Pattern
import re


class ThreatType(Enum):
    """Types of security threats that can be detected."""
    
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MALICIOUS_PAYLOAD = "malicious_payload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    COMMUNICATION_TAMPERING = "communication_tampering"
    
    # Advanced threat types for enterprise-grade detection
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_TOOL_USAGE = "suspicious_tool_usage"
    UNUSUAL_DATA_ACCESS = "unusual_data_access"
    TIMING_ATTACK = "timing_attack"
    FREQUENCY_ATTACK = "frequency_attack"
    SEQUENCE_ATTACK = "sequence_attack"
    PARAMETER_MANIPULATION = "parameter_manipulation"
    RESOURCE_ABUSE = "resource_abuse"
    CROSS_AGENT_ATTACK = "cross_agent_attack"
    PROTOCOL_VIOLATION = "protocol_violation"


class SeverityLevel(Enum):
    """Severity levels for security threats."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionMethod(Enum):
    """Methods used for threat detection."""
    
    RULE_BASED = "rule_based"
    PATTERN_BASED = "pattern_based"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    MACHINE_LEARNING = "machine_learning"
    SIGNATURE_BASED = "signature_based"


# SQL Injection patterns - these are common attack patterns
SQL_INJECTION_PATTERNS: List[Pattern[str]] = [
    re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
    re.compile(r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)", re.IGNORECASE),
    re.compile(r"(\bINSERT\b.*\bINTO\b)", re.IGNORECASE),
    re.compile(r"(\bUPDATE\b.*\bSET\b)", re.IGNORECASE),
    re.compile(r"(\bDELETE\b.*\bFROM\b)", re.IGNORECASE),
    re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"(\bALTER\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"([\'\"].*[\'\"].*=.*[\'\"].*[\'\"])", re.IGNORECASE),
    re.compile(r"([\'\"].*or.*[\'\"].*=.*[\'\"])", re.IGNORECASE),
    re.compile(r"([\'\"].*and.*[\'\"].*=.*[\'\"])", re.IGNORECASE),
    re.compile(r"(--.*)", re.IGNORECASE),
    re.compile(r"(/\*.*\*/)", re.IGNORECASE),
]

# XSS Attack patterns - cross-site scripting attempts
XSS_PATTERNS: List[Pattern[str]] = [
    re.compile(r"<script[^>]*>.*</script>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<script[^>]*>.*", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"<iframe[^>]*>", re.IGNORECASE),
    re.compile(r"<object[^>]*>", re.IGNORECASE),
    re.compile(r"<embed[^>]*>", re.IGNORECASE),
    re.compile(r"<link[^>]*>", re.IGNORECASE),
    re.compile(r"<meta[^>]*>", re.IGNORECASE),
    re.compile(r"vbscript:", re.IGNORECASE),
    re.compile(r"data:.*base64", re.IGNORECASE),
]

# Command Injection patterns - OS command execution attempts
COMMAND_INJECTION_PATTERNS: List[Pattern[str]] = [
    re.compile(r"[;&|`]", re.IGNORECASE),
    re.compile(r"\$\(.*\)", re.IGNORECASE),
    re.compile(r"`.*`", re.IGNORECASE),
    re.compile(r"(rm\s+(-rf\s+)?[/\w]*)", re.IGNORECASE),
    re.compile(r"(cat\s+/etc/passwd)", re.IGNORECASE),
    re.compile(r"(wget\s+http)", re.IGNORECASE),
    re.compile(r"(curl\s+http)", re.IGNORECASE),
    re.compile(r"(nc\s+-)", re.IGNORECASE),
    re.compile(r"(chmod\s+)", re.IGNORECASE),
    re.compile(r"(sudo\s+)", re.IGNORECASE),
]

# Path Traversal patterns - directory traversal attempts
PATH_TRAVERSAL_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\.\.\/", re.IGNORECASE),
    re.compile(r"\.\.\\", re.IGNORECASE),
    re.compile(r"%2e%2e%2f", re.IGNORECASE),
    re.compile(r"%2e%2e%5c", re.IGNORECASE),
    re.compile(r"\.\.%2f", re.IGNORECASE),
    re.compile(r"\.\.%5c", re.IGNORECASE),
    re.compile(r"\/etc\/passwd", re.IGNORECASE),
    re.compile(r"\/windows\/system32", re.IGNORECASE),
]

# Prompt Injection patterns - AI prompt manipulation attempts
PROMPT_INJECTION_PATTERNS: List[Pattern[str]] = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"forget\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"act\s+as\s+if", re.IGNORECASE),
    re.compile(r"pretend\s+to\s+be", re.IGNORECASE),
    re.compile(r"simulate\s+being", re.IGNORECASE),
    re.compile(r"roleplay\s+as", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"override\s+(?:all\s+)?(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"execute\s+code", re.IGNORECASE),
    re.compile(r"run\s+command", re.IGNORECASE),
    re.compile(r"new\s+(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"different\s+(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"updated\s+(?:instructions|rules|guidelines)", re.IGNORECASE),
    re.compile(r"ignore\s+the\s+above", re.IGNORECASE),
    re.compile(r"ignore\s+everything\s+above", re.IGNORECASE),
    re.compile(r"start\s+over", re.IGNORECASE),
    re.compile(r"begin\s+new", re.IGNORECASE),
    re.compile(r"reset\s+(?:conversation|context)", re.IGNORECASE),
]

# Threat severity mapping - how serious each threat type is
THREAT_SEVERITY: Dict[ThreatType, SeverityLevel] = {
    ThreatType.SQL_INJECTION: SeverityLevel.CRITICAL,
    ThreatType.XSS_ATTACK: SeverityLevel.HIGH,
    ThreatType.COMMAND_INJECTION: SeverityLevel.CRITICAL,
    ThreatType.PATH_TRAVERSAL: SeverityLevel.HIGH,
    ThreatType.PROMPT_INJECTION: SeverityLevel.HIGH,
    ThreatType.DATA_EXFILTRATION: SeverityLevel.CRITICAL,
    ThreatType.RATE_LIMIT_VIOLATION: SeverityLevel.MEDIUM,
    ThreatType.RESOURCE_EXHAUSTION: SeverityLevel.HIGH,
    ThreatType.MALICIOUS_PAYLOAD: SeverityLevel.HIGH,
    ThreatType.UNAUTHORIZED_ACCESS: SeverityLevel.CRITICAL,
    ThreatType.BEHAVIORAL_ANOMALY: SeverityLevel.MEDIUM,
    ThreatType.COMMUNICATION_TAMPERING: SeverityLevel.HIGH,
}

# Pattern mapping - which patterns detect which threats
THREAT_PATTERNS: Dict[ThreatType, List[Pattern[str]]] = {
    ThreatType.SQL_INJECTION: SQL_INJECTION_PATTERNS,
    ThreatType.XSS_ATTACK: XSS_PATTERNS,
    ThreatType.COMMAND_INJECTION: COMMAND_INJECTION_PATTERNS,
    ThreatType.PATH_TRAVERSAL: PATH_TRAVERSAL_PATTERNS,
    ThreatType.PROMPT_INJECTION: PROMPT_INJECTION_PATTERNS,
}

# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "agent_id": "default_agent",
    "environment": "development",
    "detection": {
        "enabled": True,
        "confidence_threshold": 0.7,  # Valid value between 0.0 and 1.0
        "rules": {
            "sql_injection": {"enabled": True, "severity": "CRITICAL"},
            "xss_attack": {"enabled": True, "severity": "HIGH"},
            "command_injection": {"enabled": True, "severity": "CRITICAL"},
            "path_traversal": {"enabled": True, "severity": "HIGH"},
            "prompt_injection": {"enabled": True, "severity": "HIGH"},
        },
        "rate_limits": {
            "default": {"requests": 100, "window": 60},
        },
    },
    "logging": {
        "level": "INFO",
        "format": "json",
        "file": "logs/agent_sentinel.log",
        "max_size": 100 * 1024 * 1024,  # 100MB
        "backup_count": 5,
    },
    "weave": {
        "enabled": False,
        "project_name": "agent-sentinel",
    },
    "alerts": {
        "enabled": False,  # Disabled by default for easier setup
        "webhook_url": None,
        "email": {"enabled": False},
    },
    "dashboard": {
        "enabled": False,
        "host": "localhost",
        "port": 8000,
    },
}

# Rate limiting defaults
DEFAULT_RATE_LIMIT = 100
DEFAULT_RATE_WINDOW = 60  # seconds

# Confidence score thresholds
CONFIDENCE_THRESHOLDS: Dict[str, float] = {
    "LOW": 0.3,
    "MEDIUM": 0.6,
    "HIGH": 0.8,
    "CRITICAL": 0.9,
}

# Maximum sizes for security
MAX_INPUT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_SIZE = 100 * 1024 * 1024   # 100MB
MAX_EVENTS_IN_MEMORY = 10000

# Sensitive data patterns for redaction
SENSITIVE_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),  # Credit card
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
    re.compile(r"\b(?:password|passwd|pwd|secret|key|token)\s*[:=]\s*\S+", re.IGNORECASE),  # Passwords
] 