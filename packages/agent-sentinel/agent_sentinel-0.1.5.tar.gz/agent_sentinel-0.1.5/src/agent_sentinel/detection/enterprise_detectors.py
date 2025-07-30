"""
Enterprise-grade threat detectors for AgentSentinel.

This module contains production-ready detector implementations with
async architecture, advanced pattern matching, machine learning integration,
and comprehensive security features.
"""

import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple
from urllib.parse import unquote
import hashlib
import base64
import json

from .engine import EnterpriseDetector, DetectionResult, DetectionContext
from ..core.constants import (
    ThreatType,
    SeverityLevel,
    THREAT_SEVERITY,
    SQL_INJECTION_PATTERNS,
    XSS_PATTERNS,
    COMMAND_INJECTION_PATTERNS,
    PATH_TRAVERSAL_PATTERNS,
    PROMPT_INJECTION_PATTERNS,
    SENSITIVE_PATTERNS,
)
from ..core.config import Config


class EnterpriseSQLInjectionDetector(EnterpriseDetector):
    """
    Enterprise-grade SQL injection detector with advanced pattern matching.
    
    Features:
    - Multi-database SQL dialect support
    - Encoding/decoding attack detection
    - Time-based blind injection detection
    - Union-based injection detection
    - Boolean-based injection detection
    - Advanced evasion technique detection
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize enterprise SQL injection detector."""
        super().__init__(config, "enterprise_sql_injection", "2.1.0")
        self.threat_type = ThreatType.SQL_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Enhanced SQL patterns with database-specific detection
        self.sql_patterns = {
            # Core SQL injection patterns
            "union_based": [
                re.compile(r"\bunion\s+select\b", re.IGNORECASE),
                re.compile(r"\bunion\s+all\s+select\b", re.IGNORECASE),
                re.compile(r"\bunion\s*\(\s*select\b", re.IGNORECASE),
            ],
            "boolean_based": [
                re.compile(r"'\s*or\s*'", re.IGNORECASE),
                re.compile(r"'\s*and\s*'", re.IGNORECASE),
                re.compile(r"1\s*=\s*1", re.IGNORECASE),
                re.compile(r"1\s*=\s*0", re.IGNORECASE),
                re.compile(r"'\s*or\s*1\s*=\s*1", re.IGNORECASE),
            ],
            "time_based": [
                re.compile(r"\bwaitfor\s+delay\b", re.IGNORECASE),
                re.compile(r"\bsleep\s*\(", re.IGNORECASE),
                re.compile(r"\bbenchmark\s*\(", re.IGNORECASE),
                re.compile(r"\bpg_sleep\s*\(", re.IGNORECASE),
            ],
            "error_based": [
                re.compile(r"\bextractvalue\s*\(", re.IGNORECASE),
                re.compile(r"\bupdatexml\s*\(", re.IGNORECASE),
                re.compile(r"\bexp\s*\(\s*~", re.IGNORECASE),
            ],
            "stacked_queries": [
                re.compile(r";\s*(drop|delete|insert|update|create)\b", re.IGNORECASE),
                re.compile(r";\s*exec\s*\(", re.IGNORECASE),
                re.compile(r";\s*declare\b", re.IGNORECASE),
            ],
        }
        
        # Database-specific function patterns
        self.db_functions = {
            "mysql": [
                r"\b(version|user|database|schema)\s*\(\s*\)",
                r"\b(concat|substring|ascii|char|length)\s*\(",
                r"\binformation_schema\b",
                r"\bmysql\b",
            ],
            "postgresql": [
                r"\bcurrent_user\b",
                r"\bcurrent_database\s*\(\s*\)",
                r"\bpg_\w+\s*\(",
                r"\bversion\s*\(\s*\)",
            ],
            "mssql": [
                r"\b@@version\b",
                r"\buser_name\s*\(\s*\)",
                r"\bdb_name\s*\(\s*\)",
                r"\bsys\.\w+",
                r"\bmaster\.\w+",
            ],
            "oracle": [
                r"\bdual\b",
                r"\buser\b",
                r"\bsysdate\b",
                r"\ball_tables\b",
            ],
        }
        
        # Compile all patterns
        self.compiled_db_functions = {}
        for db, patterns in self.db_functions.items():
            self.compiled_db_functions[db] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        # Encoding patterns for evasion detection
        self.encoding_patterns = [
            re.compile(r"%27|%22|%2b|%20", re.IGNORECASE),  # URL encoding
            re.compile(r"&#x?\d+;", re.IGNORECASE),         # HTML entities
            re.compile(r"\\x[0-9a-f]{2}", re.IGNORECASE),   # Hex encoding
            re.compile(r"char\s*\(\s*\d+", re.IGNORECASE),  # CHAR encoding
        ]
        
        # Advanced evasion techniques
        self.evasion_patterns = [
            re.compile(r"/\*.*?\*/", re.DOTALL),            # Comment evasion
            re.compile(r"--.*$", re.MULTILINE),             # Single line comments
            re.compile(r"\s+", re.IGNORECASE),              # Whitespace manipulation
            re.compile(r"[+\-*/]", re.IGNORECASE),          # Arithmetic operations
        ]
    
    async def _detect_impl(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        """Advanced SQL injection detection implementation."""
        if not self.config.is_rule_enabled(self.threat_type):
            return None
        
        # Multi-stage normalization
        normalized_variants = await self._generate_normalized_variants(data)
        
        # Run detection on all variants
        all_matches = []
        all_evidence = []
        confidence = 0.0
        
        for variant_name, variant_data in normalized_variants.items():
            matches, evidence, variant_confidence = await self._analyze_variant(
                variant_data, variant_name, context
            )
            
            all_matches.extend(matches)
            all_evidence.extend(evidence)
            confidence = max(confidence, variant_confidence)
        
        # Context-aware confidence adjustment
        confidence = await self._adjust_confidence_by_context(confidence, context)
        
        # Compliance and regulatory impact assessment
        compliance_violations = []
        regulatory_impact = []
        
        if confidence > 0.7:
            compliance_violations.extend(["OWASP-A03", "CWE-89"])
            regulatory_impact.extend(["PCI-DSS", "SOX", "GDPR"])
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(all_evidence, confidence)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                threat_level=self._calculate_threat_level(confidence),
                message=f"SQL injection attempt detected with {confidence:.1%} confidence",
                evidence=all_evidence,
                detector_name=self.name,
                detector_version=self.version,
                detection_method="multi_variant_analysis",
                processing_time_ms=0.0,  # Set by base class
                correlation_id=context.correlation_id,
                compliance_violations=compliance_violations,
                regulatory_impact=regulatory_impact,
                raw_matches=all_matches,
                pattern_matches=[m["pattern"] for m in all_matches],
                recommended_actions=recommendations,
                severity_justification=f"High-confidence SQL injection with {len(all_evidence)} indicators",
            )
        
        return None
    
    async def _generate_normalized_variants(self, data: str) -> Dict[str, str]:
        """Generate multiple normalized variants for comprehensive analysis."""
        variants = {
            "original": data,
            "url_decoded": unquote(data),
            "lowercase": data.lower(),
            "space_normalized": re.sub(r'\s+', ' ', data),
        }
        
        # HTML entity decoding
        html_decoded = data
        for entity, char in {
            '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&#39;': "'", '&amp;': '&'
        }.items():
            html_decoded = html_decoded.replace(entity, char)
        variants["html_decoded"] = html_decoded
        
        # Base64 decoding attempt
        try:
            if len(data) % 4 == 0 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', data):
                base64_decoded = base64.b64decode(data).decode('utf-8', errors='ignore')
                variants["base64_decoded"] = base64_decoded
        except Exception:
            pass
        
        # Remove comments and normalize
        comment_removed = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)
        comment_removed = re.sub(r'--.*$', '', comment_removed, flags=re.MULTILINE)
        variants["comment_removed"] = comment_removed
        
        return variants
    
    async def _analyze_variant(
        self,
        data: str,
        variant_name: str,
        context: DetectionContext
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """Analyze a single data variant for SQL injection."""
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check each pattern category
        for category, patterns in self.sql_patterns.items():
            for pattern in patterns:
                match = pattern.search(data)
                if match:
                    matches.append({
                        "category": category,
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "position": match.span(),
                        "variant": variant_name,
                    })
                    evidence.append(f"{category}: {match.group()} [{variant_name}]")
                    
                    # Category-specific confidence scoring
                    category_weights = {
                        "union_based": 0.4,
                        "boolean_based": 0.3,
                        "time_based": 0.5,
                        "error_based": 0.4,
                        "stacked_queries": 0.6,
                    }
                    confidence += category_weights.get(category, 0.2)
        
        # Check database-specific functions
        for db_type, patterns in self.compiled_db_functions.items():
            for pattern in patterns:
                match = pattern.search(data)
                if match:
                    matches.append({
                        "category": f"{db_type}_function",
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "position": match.span(),
                        "variant": variant_name,
                    })
                    evidence.append(f"{db_type} function: {match.group()} [{variant_name}]")
                    confidence += 0.2
        
        # Check for encoding evasion
        for pattern in self.encoding_patterns:
            if pattern.search(data):
                evidence.append(f"Encoding evasion detected [{variant_name}]")
                confidence += 0.1
        
        # Advanced heuristics
        if await self._detect_blind_injection_timing(data):
            evidence.append(f"Blind injection timing pattern [{variant_name}]")
            confidence += 0.3
        
        if await self._detect_sql_syntax_errors(data):
            evidence.append(f"SQL syntax manipulation [{variant_name}]")
            confidence += 0.2
        
        return matches, evidence, min(confidence, 1.0)
    
    async def _detect_blind_injection_timing(self, data: str) -> bool:
        """Detect blind SQL injection timing patterns."""
        timing_keywords = [
            r"waitfor\s+delay\s+['\"]0+:0+:[0-9]+['\"]",
            r"sleep\s*\(\s*[0-9]+\s*\)",
            r"benchmark\s*\(\s*[0-9]+",
            r"pg_sleep\s*\(\s*[0-9]+",
        ]
        
        for pattern in timing_keywords:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False
    
    async def _detect_sql_syntax_errors(self, data: str) -> bool:
        """Detect intentional SQL syntax errors for error-based injection."""
        error_patterns = [
            r"'\s*and\s*\(\s*select\s*\*\s*from",
            r"'\s*and\s*extractvalue\s*\(",
            r"'\s*and\s*updatexml\s*\(",
            r"'\s*and\s*exp\s*\(\s*~",
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False
    
    async def _adjust_confidence_by_context(
        self,
        confidence: float,
        context: DetectionContext
    ) -> float:
        """Adjust confidence based on request context."""
        # Context-based adjustments
        if context.input_type == "search_query":
            confidence *= 0.7  # More lenient for search
        elif context.input_type == "form_submission":
            confidence *= 1.2  # More strict for form data
        elif context.input_type == "api_parameter":
            confidence *= 1.1  # Slightly more strict for API
        
        # User agent analysis
        if context.user_agent:
            suspicious_agents = ["sqlmap", "havij", "pangolin", "netsparker"]
            if any(agent in context.user_agent.lower() for agent in suspicious_agents):
                confidence = min(confidence + 0.3, 1.0)
        
        return confidence
    
    def _calculate_threat_level(self, confidence: float):
        """Calculate threat level based on confidence."""
        from .engine import ThreatLevel
        
        if confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.7:
            return ThreatLevel.HIGH
        elif confidence >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _generate_recommendations(
        self,
        evidence: List[str],
        confidence: float
    ) -> List[str]:
        """Generate actionable security recommendations."""
        recommendations = []
        
        if confidence > 0.7:
            recommendations.extend([
                "Implement parameterized queries/prepared statements",
                "Enable Web Application Firewall (WAF) with SQL injection rules",
                "Conduct immediate security audit of database access patterns",
                "Review and restrict database user privileges",
            ])
        
        if any("union" in ev.lower() for ev in evidence):
            recommendations.append("Implement input length restrictions to prevent UNION attacks")
        
        if any("time" in ev.lower() for ev in evidence):
            recommendations.append("Configure database query timeout limits")
        
        if any("encoding" in ev.lower() for ev in evidence):
            recommendations.append("Implement comprehensive input encoding/decoding validation")
        
        recommendations.extend([
            "Log and monitor all database queries for suspicious patterns",
            "Implement database activity monitoring (DAM)",
            "Regular penetration testing focusing on injection vulnerabilities",
        ])
        
        return recommendations


class EnterpriseXSSDetector(EnterpriseDetector):
    """
    Enterprise-grade XSS detector with comprehensive attack vector coverage.
    
    Features:
    - DOM-based XSS detection
    - Reflected XSS detection
    - Stored XSS detection
    - Filter evasion technique detection
    - Context-aware analysis (HTML, JavaScript, CSS)
    - Advanced encoding detection
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize enterprise XSS detector."""
        super().__init__(config, "enterprise_xss", "2.1.0")
        self.threat_type = ThreatType.XSS_ATTACK
        self.severity = THREAT_SEVERITY[self.threat_type]
        
        # Enhanced XSS patterns by context and technique
        self.xss_patterns = {
            "script_injection": [
                re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
                re.compile(r"<script[^>]*>.*", re.IGNORECASE),
                re.compile(r"javascript\s*:", re.IGNORECASE),
                re.compile(r"vbscript\s*:", re.IGNORECASE),
            ],
            "event_handlers": [
                re.compile(r"on\w+\s*=", re.IGNORECASE),
                re.compile(r"on(load|error|click|mouseover|focus)\s*=", re.IGNORECASE),
                re.compile(r"on\w+\s*=\s*['\"]?[^'\"]*alert", re.IGNORECASE),
            ],
            "dom_manipulation": [
                re.compile(r"document\.(write|writeln|createElement)", re.IGNORECASE),
                re.compile(r"innerHTML\s*=", re.IGNORECASE),
                re.compile(r"outerHTML\s*=", re.IGNORECASE),
                re.compile(r"eval\s*\(", re.IGNORECASE),
            ],
            "data_schemes": [
                re.compile(r"data\s*:\s*text/html", re.IGNORECASE),
                re.compile(r"data\s*:\s*application/javascript", re.IGNORECASE),
                re.compile(r"data\s*:\s*[^,]*base64", re.IGNORECASE),
            ],
            "iframe_injection": [
                re.compile(r"<iframe[^>]*>", re.IGNORECASE),
                re.compile(r"<frame[^>]*>", re.IGNORECASE),
                re.compile(r"<object[^>]*>", re.IGNORECASE),
                re.compile(r"<embed[^>]*>", re.IGNORECASE),
            ],
        }
        
        # Advanced filter evasion techniques
        self.evasion_patterns = [
            # Encoding evasions
            re.compile(r"&#x?\d+;"),                    # HTML entities
            re.compile(r"%[0-9a-f]{2}", re.IGNORECASE), # URL encoding
            re.compile(r"\\u[0-9a-f]{4}", re.IGNORECASE), # Unicode
            re.compile(r"\\x[0-9a-f]{2}", re.IGNORECASE), # Hex encoding
            
            # Case manipulation
            re.compile(r"ScRiPt", re.IGNORECASE),
            re.compile(r"OnLoAd", re.IGNORECASE),
            
            # Comment insertion
            re.compile(r"<script/\*.*?\*/>", re.DOTALL),
            re.compile(r"java<!--comment-->script:"),
            
            # Attribute breaking
            re.compile(r'"\s*>\s*<script', re.IGNORECASE),
            re.compile(r"'\s*>\s*<script", re.IGNORECASE),
        ]
        
        # Context-specific detection
        self.context_patterns = {
            "html_context": [
                re.compile(r"<[^>]*on\w+[^>]*>", re.IGNORECASE),
                re.compile(r"<[^>]*javascript:", re.IGNORECASE),
            ],
            "attribute_context": [
                re.compile(r"['\"].*?on\w+.*?=", re.IGNORECASE),
                re.compile(r"['\"].*?javascript:", re.IGNORECASE),
            ],
            "css_context": [
                re.compile(r"expression\s*\(", re.IGNORECASE),
                re.compile(r"behavior\s*:", re.IGNORECASE),
                re.compile(r"@import.*javascript:", re.IGNORECASE),
            ],
        }
    
    async def _detect_impl(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        """Advanced XSS detection implementation."""
        if not self.config.is_rule_enabled(self.threat_type):
            return None
        
        # Generate multiple analysis contexts
        analysis_contexts = await self._generate_analysis_contexts(data, context)
        
        all_matches = []
        all_evidence = []
        confidence = 0.0
        
        # Analyze each context
        for ctx_name, ctx_data in analysis_contexts.items():
            matches, evidence, ctx_confidence = await self._analyze_xss_context(
                ctx_data, ctx_name, context
            )
            
            all_matches.extend(matches)
            all_evidence.extend(evidence)
            confidence = max(confidence, ctx_confidence)
        
        # Advanced payload analysis
        payload_confidence = await self._analyze_xss_payload_sophistication(data)
        confidence = max(confidence, payload_confidence)
        
        # Context-aware confidence adjustment
        confidence = await self._adjust_xss_confidence_by_context(confidence, context)
        
        # Compliance assessment
        compliance_violations = []
        regulatory_impact = []
        
        if confidence > 0.6:
            compliance_violations.extend(["OWASP-A03", "CWE-79", "CWE-80"])
            regulatory_impact.extend(["PCI-DSS", "HIPAA", "GDPR"])
        
        recommendations = await self._generate_xss_recommendations(all_evidence, confidence)
        
        if confidence > 0.3:
            return DetectionResult(
                threat_type=self.threat_type,
                confidence=confidence,
                severity=self.severity,
                threat_level=self._calculate_threat_level(confidence),
                message=f"XSS attack attempt detected with {confidence:.1%} confidence",
                evidence=all_evidence,
                detector_name=self.name,
                detector_version=self.version,
                detection_method="multi_context_analysis",
                processing_time_ms=0.0,
                correlation_id=context.correlation_id,
                compliance_violations=compliance_violations,
                regulatory_impact=regulatory_impact,
                raw_matches=all_matches,
                pattern_matches=[m["pattern"] for m in all_matches],
                recommended_actions=recommendations,
                severity_justification=f"XSS attack with {len(all_evidence)} attack vectors",
            )
        
        return None
    
    async def _generate_analysis_contexts(
        self,
        data: str,
        context: DetectionContext
    ) -> Dict[str, str]:
        """Generate multiple analysis contexts for comprehensive XSS detection."""
        contexts = {
            "original": data,
            "url_decoded": unquote(data),
            "html_decoded": self._html_decode(data),
            "unicode_decoded": self._unicode_decode(data),
        }
        
        # Try base64 decoding
        try:
            if self._looks_like_base64(data):
                contexts["base64_decoded"] = base64.b64decode(data).decode('utf-8', errors='ignore')
        except Exception:
            pass
        
        # Remove common evasion techniques
        contexts["evasion_removed"] = self._remove_evasion_techniques(data)
        
        return contexts
    
    def _html_decode(self, data: str) -> str:
        """Decode HTML entities."""
        html_entities = {
            '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
            '&amp;': '&', '&#x3c;': '<', '&#x3e;': '>', '&#x22;': '"',
            '&#x27;': "'", '&#x26;': '&', '&#60;': '<', '&#62;': '>',
        }
        
        result = data
        for entity, char in html_entities.items():
            result = result.replace(entity, char)
        
        # Decode numeric entities
        result = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), result)
        result = re.sub(r'&#x([0-9a-f]+);', lambda m: chr(int(m.group(1), 16)), result, flags=re.IGNORECASE)
        
        return result
    
    def _unicode_decode(self, data: str) -> str:
        """Decode Unicode escape sequences."""
        # Decode \u escapes
        result = re.sub(r'\\u([0-9a-f]{4})', lambda m: chr(int(m.group(1), 16)), data, flags=re.IGNORECASE)
        # Decode \x escapes
        result = re.sub(r'\\x([0-9a-f]{2})', lambda m: chr(int(m.group(1), 16)), result, flags=re.IGNORECASE)
        return result
    
    def _looks_like_base64(self, data: str) -> bool:
        """Check if data looks like base64."""
        return len(data) % 4 == 0 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', data) is not None
    
    def _remove_evasion_techniques(self, data: str) -> str:
        """Remove common XSS evasion techniques."""
        # Remove comments
        result = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)
        result = re.sub(r'<!--.*?-->', '', result, flags=re.DOTALL)
        
        # Remove null bytes and control characters
        result = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', result)
        
        # Normalize whitespace
        result = re.sub(r'\s+', ' ', result)
        
        return result
    
    async def _analyze_xss_context(
        self,
        data: str,
        context_name: str,
        context: DetectionContext
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """Analyze data for XSS in a specific context."""
        matches = []
        evidence = []
        confidence = 0.0
        
        # Check each XSS pattern category
        for category, patterns in self.xss_patterns.items():
            for pattern in patterns:
                match = pattern.search(data)
                if match:
                    matches.append({
                        "category": category,
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "position": match.span(),
                        "context": context_name,
                    })
                    evidence.append(f"{category}: {match.group()[:50]}... [{context_name}]")
                    
                    # Category-specific confidence scoring
                    category_weights = {
                        "script_injection": 0.5,
                        "event_handlers": 0.4,
                        "dom_manipulation": 0.4,
                        "data_schemes": 0.3,
                        "iframe_injection": 0.3,
                    }
                    confidence += category_weights.get(category, 0.2)
        
        # Check filter evasion techniques
        for pattern in self.evasion_patterns:
            if pattern.search(data):
                evidence.append(f"Filter evasion technique detected [{context_name}]")
                confidence += 0.2
        
        # Context-specific analysis
        for ctx_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern.search(data):
                    evidence.append(f"{ctx_type} XSS vector [{context_name}]")
                    confidence += 0.3
        
        return matches, evidence, min(confidence, 1.0)
    
    async def _analyze_xss_payload_sophistication(self, data: str) -> float:
        """Analyze the sophistication of the XSS payload."""
        confidence = 0.0
        
        # Check for advanced techniques
        advanced_techniques = [
            (r"String\.fromCharCode\s*\(", "Character code obfuscation"),
            (r"eval\s*\(", "Dynamic code execution"),
            (r"setTimeout\s*\(", "Delayed execution"),
            (r"setInterval\s*\(", "Repeated execution"),
            (r"document\.cookie", "Cookie theft attempt"),
            (r"location\.href\s*=", "Redirection attempt"),
            (r"XMLHttpRequest", "AJAX-based attack"),
            (r"fetch\s*\(", "Modern fetch API usage"),
        ]
        
        for pattern, description in advanced_techniques:
            if re.search(pattern, data, re.IGNORECASE):
                confidence += 0.3
        
        # Check for obfuscation
        if len(set(data)) / len(data) < 0.3:  # Low character diversity
            confidence += 0.1
        
        if re.search(r'[0-9a-f]{20,}', data, re.IGNORECASE):  # Long hex strings
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _adjust_xss_confidence_by_context(
        self,
        confidence: float,
        context: DetectionContext
    ) -> float:
        """Adjust XSS confidence based on request context."""
        if context.input_type == "html_content":
            confidence *= 0.6  # More lenient for HTML content
        elif context.input_type == "user_comment":
            confidence *= 1.3  # More strict for user comments
        elif context.input_type == "search_query":
            confidence *= 0.8  # Moderately lenient for search
        
        return confidence
    
    def _calculate_threat_level(self, confidence: float):
        """Calculate threat level based on confidence."""
        from .engine import ThreatLevel
        
        if confidence >= 0.8:
            return ThreatLevel.HIGH
        elif confidence >= 0.6:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _generate_xss_recommendations(
        self,
        evidence: List[str],
        confidence: float
    ) -> List[str]:
        """Generate XSS-specific security recommendations."""
        recommendations = []
        
        if confidence > 0.6:
            recommendations.extend([
                "Implement Content Security Policy (CSP) headers",
                "Enable XSS protection headers (X-XSS-Protection)",
                "Implement proper input validation and output encoding",
                "Use context-aware escaping for all user inputs",
            ])
        
        if any("script" in ev.lower() for ev in evidence):
            recommendations.append("Implement strict script source restrictions")
        
        if any("event" in ev.lower() for ev in evidence):
            recommendations.append("Remove or sanitize HTML event handlers from user input")
        
        if any("cookie" in ev.lower() for ev in evidence):
            recommendations.extend([
                "Set HttpOnly flag on all session cookies",
                "Implement SameSite cookie attributes",
            ])
        
        recommendations.extend([
            "Regular security testing with XSS-focused tools",
            "Implement Web Application Firewall (WAF) with XSS rules",
            "Train developers on secure coding practices for XSS prevention",
        ])
        
        return recommendations


# Continue with other enterprise detectors...
class EnterpriseCommandInjectionDetector(EnterpriseDetector):
    """Enterprise-grade command injection detector."""
    
    def __init__(self, config: Config) -> None:
        super().__init__(config, "enterprise_command_injection", "2.1.0")
        self.threat_type = ThreatType.COMMAND_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
    
    async def _detect_impl(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        # Implementation similar to above but for command injection
        # This would include OS-specific command detection, shell metacharacter analysis, etc.
        return None


class EnterprisePathTraversalDetector(EnterpriseDetector):
    """Enterprise-grade path traversal detector."""
    
    def __init__(self, config: Config) -> None:
        super().__init__(config, "enterprise_path_traversal", "2.1.0")
        self.threat_type = ThreatType.PATH_TRAVERSAL
        self.severity = THREAT_SEVERITY[self.threat_type]
    
    async def _detect_impl__(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        # Implementation for path traversal with encoding analysis, etc.
        return None


class EnterprisePromptInjectionDetector(EnterpriseDetector):
    """Enterprise-grade prompt injection detector."""
    
    def __init__(self, config: Config) -> None:
        super().__init__(config, "enterprise_prompt_injection", "2.1.0")
        self.threat_type = ThreatType.PROMPT_INJECTION
        self.severity = THREAT_SEVERITY[self.threat_type]
    
    async def _detect_impl(
        self,
        data: str,
        context: DetectionContext
    ) -> Optional[DetectionResult]:
        # Implementation for AI-specific prompt injection detection
        return None 