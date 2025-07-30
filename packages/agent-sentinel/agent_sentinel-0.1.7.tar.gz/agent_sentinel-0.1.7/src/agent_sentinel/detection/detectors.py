"""
Specialized threat detectors for AgentSentinel.

This module contains individual detector implementations for specific
threat types like SQL injection, XSS, command injection, etc.
"""

import re
from typing import Any, Dict, List, Optional, Pattern
from urllib.parse import unquote

from .engine import BaseDetector, DetectionResult
from ..core.constants import (
    ThreatType,
    SeverityLevel,
    THREAT_SEVERITY,
    SQL_INJECTION_PATTERNS,
    XSS_PATTERNS,
    COMMAND_INJECTION_PATTERNS,
    PATH_TRAVERSAL_PATTERNS,
    PROMPT_INJECTION_PATTERNS,
)
from ..core.config import Config


class SQLInjectionDetector(BaseDetector):
    """
    Detector for SQL injection attacks.
    
    This detector identifies attempts to inject malicious SQL code
    into application inputs that could compromise database security.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize SQL injection detector."""
        super().__init__(config, "sql_injection")
        self.patterns = SQL_INJECTION_PATTERNS
        self.threat_type = ThreatType.SQL_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Additional SQL-specific patterns
        self.sql_functions = [
            r'\b(substring|ascii|length|char|concat|database|user|version)\s*\(',
            r'\b(load_file|into\s+outfile|into\s+dumpfile)\b',
            r'\b(information_schema|mysql|pg_|sys\.)\b',
            r'\b(waitfor\s+delay|benchmark\s*\()\b',
        ]
        
        self.compiled_sql_functions = [re.compile(p, re.IGNORECASE) for p in self.sql_functions]
    
    def _detect_impl(self, data: str, context: Dict[str, Any]) -> Optional[DetectionResult]:
        """Detect SQL injection attempts."""
        if not self.is_enabled(self.threat_type):
            return None
        
        # Normalize input for analysis
        normalized_data = self._normalize_sql_input(data)
        
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check main SQL injection patterns
        for pattern in self.patterns:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"SQL keyword pattern: {match.group()}")
                confidence += 0.2
        
        # Check SQL function patterns
        for pattern in self.compiled_sql_functions:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"SQL function: {match.group()}")
                confidence += 0.15
        
        # Check for SQL injection indicators
        sql_indicators = [
            (r"'\s*or\s*'", "Boolean-based injection"),
            (r"'\s*and\s*'", "Boolean-based injection"),
            (r"union\s+select", "Union-based injection"),
            (r";\s*drop\s+table", "Destructive SQL command"),
            (r";\s*delete\s+from", "Destructive SQL command"),
            (r"--.*$", "SQL comment injection"),
            (r"/\*.*\*/", "SQL comment block"),
            (r"'\s*=\s*'", "Always-true condition"),
            (r"1\s*=\s*1", "Always-true condition"),
        ]
        
        for pattern, description in sql_indicators:
            if re.search(pattern, normalized_data, re.IGNORECASE):
                evidence.append(description)
                confidence += 0.25
        
        # Additional checks for context
        if context.get("input_type") == "search_query":
            # More lenient for search queries
            confidence *= 0.7
        elif context.get("input_type") == "user_input":
            # More strict for user inputs
            confidence *= 1.2
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:  # Minimum threshold for SQL injection
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                message=f"SQL injection attempt detected with confidence {confidence:.2f}",
                evidence=evidence,
                detector_name=self.name,
                processing_time_ms=0.0,  # Will be set by base class
                raw_matches=matches,
            )
        
        return None
    
    def _normalize_sql_input(self, data: str) -> str:
        """Normalize SQL input for consistent analysis."""
        # URL decode
        normalized = unquote(data)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Convert to lowercase for pattern matching
        normalized = normalized.lower()
        
        return normalized


class XSSDetector(BaseDetector):
    """
    Detector for Cross-Site Scripting (XSS) attacks.
    
    This detector identifies attempts to inject malicious scripts
    into web applications that could compromise user browsers.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize XSS detector."""
        super().__init__(config, "xss")
        self.patterns = XSS_PATTERNS
        self.threat_type = ThreatType.XSS_ATTACK
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Additional XSS-specific patterns
        self.xss_events = [
            r'on\w+\s*=\s*["\']?\s*\w+',  # Event handlers
            r'javascript\s*:',             # JavaScript protocol
            r'data\s*:\s*text/html',       # Data URL with HTML
            r'vbscript\s*:',               # VBScript protocol
        ]
        
        self.compiled_xss_events = [re.compile(p, re.IGNORECASE) for p in self.xss_events]
    
    def _detect_impl(self, data: str, context: Dict[str, Any]) -> Optional[DetectionResult]:
        """Detect XSS attempts."""
        if not self.is_enabled(self.threat_type):
            return None
        
        normalized_data = self._normalize_xss_input(data)
        
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check main XSS patterns
        for pattern in self.patterns:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"XSS pattern: {match.group()}")
                confidence += 0.3
        
        # Check XSS event handlers
        for pattern in self.compiled_xss_events:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"XSS event handler: {match.group()}")
                confidence += 0.25
        
        # Check for encoded XSS attempts
        encoded_patterns = [
            (r'%3c%73%63%72%69%70%74', "URL-encoded <script>"),
            (r'&#x3c;script', "HTML entity encoded <script>"),
            (r'&lt;script', "HTML entity encoded <script>"),
            (r'%22%3e%3cscript', "URL-encoded \"><script>"),
        ]
        
        for pattern, description in encoded_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                evidence.append(description)
                confidence += 0.4
        
        # Context-based adjustments
        if context.get("input_type") == "html_content":
            # More lenient for HTML content
            confidence *= 0.6
        elif context.get("input_type") == "user_comment":
            # More strict for user comments
            confidence *= 1.3
        
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                message=f"XSS attack attempt detected with confidence {confidence:.2f}",
                evidence=evidence,
                detector_name=self.name,
                processing_time_ms=0.0,
                raw_matches=matches,
            )
        
        return None
    
    def _normalize_xss_input(self, data: str) -> str:
        """Normalize XSS input for consistent analysis."""
        # URL decode
        normalized = unquote(data)
        
        # HTML entity decode (basic)
        html_entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&amp;': '&',
        }
        
        for entity, char in html_entities.items():
            normalized = normalized.replace(entity, char)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized


class CommandInjectionDetector(BaseDetector):
    """
    Detector for OS command injection attacks.
    
    This detector identifies attempts to inject malicious operating
    system commands that could compromise server security.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize command injection detector."""
        super().__init__(config, "command_injection")
        self.patterns = COMMAND_INJECTION_PATTERNS
        self.threat_type = ThreatType.COMMAND_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Dangerous commands
        self.dangerous_commands = [
            r'\b(rm\s+-rf|rmdir|del)\b',
            r'\b(cat|type)\s+/etc/passwd',
            r'\b(wget|curl|fetch)\s+http',
            r'\b(nc|netcat)\s+-',
            r'\b(chmod|chown)\s+',
            r'\b(sudo|su)\s+',
            r'\b(kill|killall)\s+',
            r'\b(ps|top|netstat)\b',
        ]
        
        self.compiled_dangerous_commands = [re.compile(p, re.IGNORECASE) for p in self.dangerous_commands]
    
    def _detect_impl(self, data: str, context: Dict[str, Any]) -> Optional[DetectionResult]:
        """Detect command injection attempts."""
        if not self.is_enabled(self.threat_type):
            return None
        
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check main command injection patterns
        for pattern in self.patterns:
            match = pattern.search(data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Command injection pattern: {match.group()}")
                confidence += 0.4
        
        # Check dangerous commands
        for pattern in self.compiled_dangerous_commands:
            match = pattern.search(data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Dangerous command: {match.group()}")
                confidence += 0.3
        
        # Check for command separators
        separators = [';', '|', '&', '`', '$()']
        for sep in separators:
            if sep in data:
                evidence.append(f"Command separator: {sep}")
                confidence += 0.2
        
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                message=f"Command injection attempt detected with confidence {confidence:.2f}",
                evidence=evidence,
                detector_name=self.name,
                processing_time_ms=0.0,
                raw_matches=matches,
            )
        
        return None


class PathTraversalDetector(BaseDetector):
    """
    Detector for path traversal attacks.
    
    This detector identifies attempts to access files and directories
    outside of the intended scope using directory traversal techniques.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize path traversal detector."""
        super().__init__(config, "path_traversal")
        self.patterns = PATH_TRAVERSAL_PATTERNS
        self.threat_type = ThreatType.PATH_TRAVERSAL
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Sensitive file patterns
        self.sensitive_files = [
            r'/etc/passwd',
            r'/etc/shadow',
            r'/windows/system32/config/sam',
            r'/proc/self/environ',
            r'\.ssh/id_rsa',
            r'\.aws/credentials',
        ]
        
        self.compiled_sensitive_files = [re.compile(p, re.IGNORECASE) for p in self.sensitive_files]
    
    def _detect_impl(self, data: str, context: Dict[str, Any]) -> Optional[DetectionResult]:
        """Detect path traversal attempts."""
        if not self.is_enabled(self.threat_type):
            return None
        
        normalized_data = unquote(data)
        
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check main path traversal patterns
        for pattern in self.patterns:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Path traversal pattern: {match.group()}")
                confidence += 0.3
        
        # Check sensitive file access
        for pattern in self.compiled_sensitive_files:
            match = pattern.search(normalized_data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Sensitive file access: {match.group()}")
                confidence += 0.5
        
        # Check for multiple traversal attempts
        traversal_count = len(re.findall(r'\.\./', normalized_data))
        if traversal_count > 1:
            evidence.append(f"Multiple traversal attempts: {traversal_count}")
            confidence += 0.2 * traversal_count
        
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                message=f"Path traversal attempt detected with confidence {confidence:.2f}",
                evidence=evidence,
                detector_name=self.name,
                processing_time_ms=0.0,
                raw_matches=matches,
            )
        
        return None


class PromptInjectionDetector(BaseDetector):
    """
    Detector for AI prompt injection attacks.
    
    This detector identifies attempts to manipulate AI language models
    by injecting malicious prompts that override original instructions.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize prompt injection detector."""
        super().__init__(config, "prompt_injection")
        self.patterns = PROMPT_INJECTION_PATTERNS
        self.threat_type = ThreatType.PROMPT_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Additional prompt injection patterns
        self.injection_phrases = [
            r'ignore\s+all\s+previous\s+instructions',
            r'disregard\s+the\s+above',
            r'you\s+are\s+now\s+a\s+different\s+ai',
            r'new\s+instructions\s*:',
            r'override\s+your\s+programming',
            r'forget\s+your\s+original\s+purpose',
            r'act\s+as\s+if\s+you\s+are',
            r'pretend\s+you\s+are\s+not',
            r'do\s+not\s+mention\s+this\s+prompt',
        ]
        
        self.compiled_injection_phrases = [re.compile(p, re.IGNORECASE) for p in self.injection_phrases]
    
    def _detect_impl(self, data: str, context: Dict[str, Any]) -> Optional[DetectionResult]:
        """Detect prompt injection attempts."""
        if not self.is_enabled(self.threat_type):
            return None
        
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check main prompt injection patterns
        for pattern in self.patterns:
            match = pattern.search(data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Prompt injection pattern: {match.group()}")
                confidence += 0.4
        
        # Check additional injection phrases
        for pattern in self.compiled_injection_phrases:
            match = pattern.search(data)
            if match:
                matches.append({
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": match.span(),
                })
                evidence.append(f"Injection phrase: {match.group()}")
                confidence += 0.3
        
        # Check for instruction override attempts
        instruction_keywords = [
            'instruction', 'directive', 'command', 'order',
            'task', 'goal', 'objective', 'purpose'
        ]
        
        override_words = [
            'ignore', 'disregard', 'forget', 'override',
            'replace', 'change', 'modify', 'new'
        ]
        
        for inst_word in instruction_keywords:
            for override_word in override_words:
                pattern = f'{override_word}.*{inst_word}'
                if re.search(pattern, data, re.IGNORECASE):
                    evidence.append(f"Instruction override: {override_word} {inst_word}")
                    confidence += 0.25
        
        # Check for role-playing attempts
        role_patterns = [
            r'you\s+are\s+(?:now\s+)?(?:a|an)\s+\w+',
            r'act\s+as\s+(?:a|an)\s+\w+',
            r'pretend\s+to\s+be\s+(?:a|an)\s+\w+',
            r'simulate\s+being\s+(?:a|an)\s+\w+',
        ]
        
        for pattern in role_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                evidence.append("Role-playing attempt detected")
                confidence += 0.3
                break
        
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                message=f"Prompt injection attempt detected with confidence {confidence:.2f}",
                evidence=evidence,
                detector_name=self.name,
                processing_time_ms=0.0,
                raw_matches=matches,
            )
        
        return None 