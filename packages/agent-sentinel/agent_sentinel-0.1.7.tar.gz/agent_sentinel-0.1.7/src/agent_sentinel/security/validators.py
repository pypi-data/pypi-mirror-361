"""
Security Input Validators

Enterprise-grade input validation to prevent injection attacks and 
ensure data integrity in AI agent interactions.
"""

import re
import html
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from ..core.constants import ThreatType
from ..core.exceptions import ValidationError


class ValidationResult(Enum):
    """Validation result status"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


@dataclass
class ValidationResponse:
    """Comprehensive validation response"""
    result: ValidationResult
    is_safe: bool
    confidence_score: float
    threat_type: Optional[ThreatType] = None
    violations: Optional[List[str]] = None
    sanitized_input: Optional[str] = None
    risk_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.metadata is None:
            self.metadata = {}


class BaseValidator(ABC):
    """Base class for security validators"""
    
    def __init__(self, strict_mode: bool = False, max_input_length: int = 10000):
        """
        Initialize base validator
        
        Args:
            strict_mode: Enable strict validation mode
            max_input_length: Maximum allowed input length
        """
        self.strict_mode = strict_mode
        self.max_input_length = max_input_length
        self.validation_stats = {
            'total_validations': 0,
            'blocked_inputs': 0,
            'suspicious_inputs': 0,
            'threat_patterns_detected': {}
        }

    @abstractmethod
    def validate(self, input_data: str) -> ValidationResponse:
        """Validate input data against security threats"""
        pass

    def _update_stats(self, result: ValidationResponse):
        """Update validation statistics"""
        self.validation_stats['total_validations'] += 1
        
        if result.result == ValidationResult.BLOCKED:
            self.validation_stats['blocked_inputs'] += 1
        elif result.result == ValidationResult.SUSPICIOUS:
            self.validation_stats['suspicious_inputs'] += 1
        
        if result.threat_type:
            threat_name = result.threat_type.value
            current_count = self.validation_stats['threat_patterns_detected'].get(threat_name, 0)
            self.validation_stats['threat_patterns_detected'][threat_name] = current_count + 1

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.validation_stats.copy()


class InputValidator(BaseValidator):
    """
    Comprehensive input validator that checks for multiple threat types
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize comprehensive input validator"""
        super().__init__(*args, **kwargs)
        
        # Initialize specialized validators
        self.sql_validator = SQLInjectionValidator(strict_mode=self.strict_mode)
        self.xss_validator = XSSValidator(strict_mode=self.strict_mode)
        self.cmd_validator = CommandInjectionValidator(strict_mode=self.strict_mode)
        
        # Prompt injection patterns
        self.prompt_injection_patterns = [
            re.compile(r'ignore\s+previous\s+instructions', re.IGNORECASE),
            re.compile(r'forget\s+everything', re.IGNORECASE),
            re.compile(r'act\s+as\s+if', re.IGNORECASE),
            re.compile(r'pretend\s+to\s+be', re.IGNORECASE),
            re.compile(r'system\s+prompt', re.IGNORECASE),
            re.compile(r'override\s+instructions', re.IGNORECASE),
            re.compile(r'jailbreak', re.IGNORECASE),
            re.compile(r'escape\s+your\s+programming', re.IGNORECASE)
        ]

    def validate(self, input_data: str) -> ValidationResponse:
        """
        Comprehensive validation against all threat types
        
        Args:
            input_data: Input string to validate
            
        Returns:
            ValidationResponse with comprehensive analysis
        """
        if not isinstance(input_data, str):
            input_data = str(input_data)
        
        # Basic input checks
        if len(input_data) > self.max_input_length:
            result = ValidationResponse(
                result=ValidationResult.BLOCKED,
                is_safe=False,
                confidence_score=1.0,
                threat_type=ThreatType.MALICIOUS_PAYLOAD,
                violations=[f"Input exceeds maximum length ({self.max_input_length})"],
                risk_score=100.0
            )
            self._update_stats(result)
            return result
        
        # Run all validators
        validators_results = {
            'sql': self.sql_validator.validate(input_data),
            'xss': self.xss_validator.validate(input_data),
            'cmd': self.cmd_validator.validate(input_data),
            'prompt': self._validate_prompt_injection(input_data)
        }
        
        # Aggregate results
        violations = []
        threat_types = []
        risk_scores = []
        max_confidence = 0.0
        is_safe = True
        
        for validator_name, validation_result in validators_results.items():
            if not validation_result.is_safe:
                is_safe = False
                if validation_result.violations:
                    violations.extend(validation_result.violations)
                if validation_result.threat_type:
                    threat_types.append(validation_result.threat_type)
                risk_scores.append(validation_result.risk_score)
                max_confidence = max(max_confidence, validation_result.confidence_score)
        
        # Determine overall result
        if not is_safe:
            if max_confidence >= 0.8 or self.strict_mode:
                overall_result = ValidationResult.BLOCKED
            else:
                overall_result = ValidationResult.SUSPICIOUS
        else:
            overall_result = ValidationResult.VALID
        
        result = ValidationResponse(
            result=overall_result,
            is_safe=is_safe,
            confidence_score=max_confidence,
            threat_type=threat_types[0] if threat_types else None,
            violations=violations,
            sanitized_input=self._sanitize_input(input_data) if violations else input_data,
            risk_score=max(risk_scores) if risk_scores else 0.0,
            metadata={
                'validator_results': {k: v.result.value for k, v in validators_results.items()},
                'detected_threats': [t.value for t in threat_types]
            }
        )
        
        self._update_stats(result)
        return result

    def _validate_prompt_injection(self, input_data: str) -> ValidationResponse:
        """Validate against prompt injection attacks"""
        violations = []
        confidence = 0.0
        
        for pattern in self.prompt_injection_patterns:
            if pattern.search(input_data):
                violations.append(f"Prompt injection pattern detected: {pattern.pattern}")
                confidence = max(confidence, 0.8)
        
        # Check for suspicious instruction-like phrases
        instruction_keywords = ['execute', 'run', 'eval', 'import', 'delete', 'remove', 'override']
        for keyword in instruction_keywords:
            if keyword in input_data.lower():
                violations.append(f"Suspicious instruction keyword: {keyword}")
                confidence = max(confidence, 0.6)
        
        is_safe = len(violations) == 0
        
        return ValidationResponse(
            result=ValidationResult.VALID if is_safe else ValidationResult.SUSPICIOUS,
            is_safe=is_safe,
            confidence_score=confidence,
            threat_type=ThreatType.PROMPT_INJECTION if violations else None,
            violations=violations,
            risk_score=confidence * 100 if violations else 0.0
        )

    def _sanitize_input(self, input_data: str) -> str:
        """Basic input sanitization"""
        # HTML escape
        sanitized = html.escape(input_data)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized


class SQLInjectionValidator(BaseValidator):
    """Specialized validator for SQL injection attacks"""
    
    def __init__(self, *args, **kwargs):
        """Initialize SQL injection validator"""
        super().__init__(*args, **kwargs)
        
        # SQL injection patterns
        self.sql_patterns = [
            re.compile(r"'.*'", re.IGNORECASE),
            re.compile(r'".*"', re.IGNORECASE),
            re.compile(r'union\s+select', re.IGNORECASE),
            re.compile(r'drop\s+table', re.IGNORECASE),
            re.compile(r'delete\s+from', re.IGNORECASE),
            re.compile(r'insert\s+into', re.IGNORECASE),
            re.compile(r'update\s+.*set', re.IGNORECASE),
            re.compile(r'--', re.IGNORECASE),
            re.compile(r'/\*.*\*/', re.IGNORECASE),
            re.compile(r';\s*drop', re.IGNORECASE),
            re.compile(r'1\s*=\s*1', re.IGNORECASE),
            re.compile(r'or\s+1\s*=\s*1', re.IGNORECASE),
            re.compile(r'and\s+1\s*=\s*1', re.IGNORECASE),
            re.compile(r'admin\s*--', re.IGNORECASE),
            re.compile(r'char\(', re.IGNORECASE),
            re.compile(r'concat\(', re.IGNORECASE),
            re.compile(r'substring\(', re.IGNORECASE),
            re.compile(r'waitfor\s+delay', re.IGNORECASE),
            re.compile(r'benchmark\(', re.IGNORECASE),
            re.compile(r'pg_sleep\(', re.IGNORECASE)
        ]

    def validate(self, input_data: str) -> ValidationResponse:
        """Validate against SQL injection patterns"""
        violations = []
        confidence = 0.0
        
        for pattern in self.sql_patterns:
            matches = pattern.findall(input_data)
            if matches:
                violations.append(f"SQL injection pattern detected: {pattern.pattern}")
                # Higher confidence for more dangerous patterns
                if any(keyword in pattern.pattern.lower() for keyword in ['drop', 'delete', 'union']):
                    confidence = max(confidence, 0.9)
                else:
                    confidence = max(confidence, 0.7)
        
        is_safe = len(violations) == 0
        
        result = ValidationResponse(
            result=ValidationResult.VALID if is_safe else ValidationResult.BLOCKED,
            is_safe=is_safe,
            confidence_score=confidence,
            threat_type=ThreatType.SQL_INJECTION if violations else None,
            violations=violations,
            risk_score=confidence * 100 if violations else 0.0,
            metadata={'pattern_matches': len(violations)}
        )
        
        self._update_stats(result)
        return result


class XSSValidator(BaseValidator):
    """Specialized validator for Cross-Site Scripting (XSS) attacks"""
    
    def __init__(self, *args, **kwargs):
        """Initialize XSS validator"""
        super().__init__(*args, **kwargs)
        
        # XSS patterns
        self.xss_patterns = [
            re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<script.*?>', re.IGNORECASE),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onload, etc.
            re.compile(r'<iframe.*?>', re.IGNORECASE),
            re.compile(r'<object.*?>', re.IGNORECASE),
            re.compile(r'<embed.*?>', re.IGNORECASE),
            re.compile(r'<link.*?>', re.IGNORECASE),
            re.compile(r'<meta.*?>', re.IGNORECASE),
            re.compile(r'document\.cookie', re.IGNORECASE),
            re.compile(r'document\.write', re.IGNORECASE),
            re.compile(r'window\.location', re.IGNORECASE),
            re.compile(r'eval\(', re.IGNORECASE),
            re.compile(r'expression\(', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE)
        ]

    def validate(self, input_data: str) -> ValidationResponse:
        """Validate against XSS patterns"""
        violations = []
        confidence = 0.0
        
        for pattern in self.xss_patterns:
            matches = pattern.findall(input_data)
            if matches:
                violations.append(f"XSS pattern detected: {pattern.pattern}")
                # Script tags are highest risk
                if 'script' in pattern.pattern.lower():
                    confidence = max(confidence, 0.95)
                else:
                    confidence = max(confidence, 0.8)
        
        is_safe = len(violations) == 0
        
        result = ValidationResponse(
            result=ValidationResult.VALID if is_safe else ValidationResult.BLOCKED,
            is_safe=is_safe,
            confidence_score=confidence,
            threat_type=ThreatType.XSS_ATTACK if violations else None,
            violations=violations,
            risk_score=confidence * 100 if violations else 0.0,
            metadata={'pattern_matches': len(violations)}
        )
        
        self._update_stats(result)
        return result


class CommandInjectionValidator(BaseValidator):
    """Specialized validator for command injection attacks"""
    
    def __init__(self, *args, **kwargs):
        """Initialize command injection validator"""
        super().__init__(*args, **kwargs)
        
        # Command injection patterns
        self.cmd_patterns = [
            re.compile(r';\s*\w+', re.IGNORECASE),  # ; command
            re.compile(r'\|\s*\w+', re.IGNORECASE),  # | command
            re.compile(r'&&\s*\w+', re.IGNORECASE),  # && command
            re.compile(r'\|\|\s*\w+', re.IGNORECASE),  # || command
            re.compile(r'`.*`', re.IGNORECASE),  # backticks
            re.compile(r'\$\(.*\)', re.IGNORECASE),  # $() command substitution
            re.compile(r'>\s*/dev/null', re.IGNORECASE),
            re.compile(r'/etc/passwd', re.IGNORECASE),
            re.compile(r'rm\s+-rf', re.IGNORECASE),
            re.compile(r'wget\s+', re.IGNORECASE),
            re.compile(r'curl\s+', re.IGNORECASE),
            re.compile(r'nc\s+', re.IGNORECASE),  # netcat
            re.compile(r'telnet\s+', re.IGNORECASE),
            re.compile(r'ssh\s+', re.IGNORECASE),
            re.compile(r'powershell', re.IGNORECASE),
            re.compile(r'cmd\.exe', re.IGNORECASE),
            re.compile(r'/bin/sh', re.IGNORECASE),
            re.compile(r'/bin/bash', re.IGNORECASE)
        ]

    def validate(self, input_data: str) -> ValidationResponse:
        """Validate against command injection patterns"""
        violations = []
        confidence = 0.0
        
        for pattern in self.cmd_patterns:
            matches = pattern.findall(input_data)
            if matches:
                violations.append(f"Command injection pattern detected: {pattern.pattern}")
                # Destructive commands are highest risk
                if any(keyword in pattern.pattern.lower() for keyword in ['rm', 'del', 'format']):
                    confidence = max(confidence, 0.95)
                else:
                    confidence = max(confidence, 0.8)
        
        is_safe = len(violations) == 0
        
        result = ValidationResponse(
            result=ValidationResult.VALID if is_safe else ValidationResult.BLOCKED,
            is_safe=is_safe,
            confidence_score=confidence,
            threat_type=ThreatType.COMMAND_INJECTION if violations else None,
            violations=violations,
            risk_score=confidence * 100 if violations else 0.0,
            metadata={'pattern_matches': len(violations)}
        )
        
        self._update_stats(result)
        return result 