"""
Real-time Threat Intelligence Integration for Agent Sentinel

This module provides enterprise-grade threat intelligence capabilities
similar to those found in Datadog Security, Snyk, and Wiz.
"""

import asyncio
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import httpx
from pathlib import Path

from ..core.constants import ThreatType, SeverityLevel
from ..core.exceptions import ThreatIntelligenceError
from ..logging.structured_logger import SecurityLogger


class ThreatIntelligenceSource(Enum):
    """Sources of threat intelligence."""
    INTERNAL = "internal"
    COMMUNITY = "community"
    COMMERCIAL = "commercial"
    GOVERNMENT = "government"
    OSINT = "osint"


@dataclass
class ThreatIndicator:
    """Threat indicator with intelligence metadata."""
    indicator_type: str  # hash, ip, domain, pattern, etc.
    value: str
    threat_type: ThreatType
    severity: SeverityLevel
    confidence: float
    source: ThreatIntelligenceSource
    first_seen: datetime
    last_seen: datetime
    description: str
    tags: Set[str] = field(default_factory=set)
    attribution: Optional[str] = None
    campaign: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if indicator has expired."""
        if self.ttl is None:
            return False
        return (datetime.now(timezone.utc) - self.last_seen).total_seconds() > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "indicator_type": self.indicator_type,
            "value": self.value,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "source": self.source.value,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "description": self.description,
            "tags": list(self.tags),
            "attribution": self.attribution,
            "campaign": self.campaign,
            "ttl": self.ttl
        }


class ThreatIntelligenceEngine:
    """Enterprise-grade threat intelligence engine."""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[SecurityLogger] = None):
        self.config = config
        self.logger = logger or SecurityLogger("threat_intelligence", "system")
        
        # Threat intelligence storage
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.indicator_cache: Dict[str, Any] = {}
        
        # Sources configuration
        self.sources = {
            "internal": self._load_internal_indicators,
            "community": self._load_community_indicators,
            "commercial": self._load_commercial_indicators,
            "osint": self._load_osint_indicators
        }
        
        # Update configuration
        self.update_interval = config.get("update_interval", 3600)  # 1 hour
        self.max_indicators = config.get("max_indicators", 100000)
        self.cleanup_interval = config.get("cleanup_interval", 86400)  # 24 hours
        
        # Performance metrics
        self.metrics = {
            "indicators_loaded": 0,
            "indicators_matched": 0,
            "sources_updated": 0,
            "last_update": None,
            "update_errors": 0
        }
        
        # Background tasks
        self._update_task = None
        self._cleanup_task = None
        self._running = False
        
        # Initialize with built-in indicators
        self._load_builtin_indicators()
    
    async def start(self) -> None:
        """Start the threat intelligence engine."""
        self._running = True
        
        # Start background update task
        self._update_task = asyncio.create_task(self._update_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Initial load
        await self._update_all_sources()
        
        self.logger.info("Threat intelligence engine started")
    
    async def stop(self) -> None:
        """Stop the threat intelligence engine."""
        self._running = False
        
        if self._update_task:
            self._update_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        self.logger.info("Threat intelligence engine stopped")
    
    async def check_threat(self, indicator_value: str, indicator_type: str = "auto") -> Optional[ThreatIndicator]:
        """Check if an indicator matches known threats."""
        if indicator_type == "auto":
            indicator_type = self._detect_indicator_type(indicator_value)
        
        # Create lookup key
        lookup_key = f"{indicator_type}:{indicator_value}"
        
        # Check direct match
        if lookup_key in self.indicators:
            indicator = self.indicators[lookup_key]
            if not indicator.is_expired():
                self.metrics["indicators_matched"] += 1
                return indicator
        
        # Check pattern matches for certain types
        if indicator_type in ["input", "output", "text"]:
            for key, indicator in self.indicators.items():
                if indicator.indicator_type == "pattern" and not indicator.is_expired():
                    if self._match_pattern(indicator.value, indicator_value):
                        self.metrics["indicators_matched"] += 1
                        return indicator
        
        return None
    
    def add_indicator(self, indicator: ThreatIndicator) -> None:
        """Add a new threat indicator."""
        lookup_key = f"{indicator.indicator_type}:{indicator.value}"
        self.indicators[lookup_key] = indicator
        self.metrics["indicators_loaded"] += 1
        
        # Enforce max indicators limit
        if len(self.indicators) > self.max_indicators:
            self._cleanup_old_indicators()
    
    def remove_indicator(self, indicator_type: str, value: str) -> bool:
        """Remove a threat indicator."""
        lookup_key = f"{indicator_type}:{value}"
        if lookup_key in self.indicators:
            del self.indicators[lookup_key]
            return True
        return False
    
    def get_indicators_by_type(self, indicator_type: str) -> List[ThreatIndicator]:
        """Get all indicators of a specific type."""
        return [
            indicator for key, indicator in self.indicators.items()
            if indicator.indicator_type == indicator_type and not indicator.is_expired()
        ]
    
    def get_indicators_by_threat(self, threat_type: ThreatType) -> List[ThreatIndicator]:
        """Get all indicators for a specific threat type."""
        return [
            indicator for indicator in self.indicators.values()
            if indicator.threat_type == threat_type and not indicator.is_expired()
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get threat intelligence metrics."""
        return {
            **self.metrics,
            "total_indicators": len(self.indicators),
            "active_indicators": len([i for i in self.indicators.values() if not i.is_expired()]),
            "sources_configured": len(self.sources),
            "cache_size": len(self.indicator_cache)
        }
    
    def _detect_indicator_type(self, value: str) -> str:
        """Auto-detect indicator type from value."""
        import re
        
        # IP address
        if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', value):
            return "ip"
        
        # Domain
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return "domain"
        
        # Hash (MD5, SHA1, SHA256)
        if re.match(r'^[a-fA-F0-9]{32}$', value):
            return "md5"
        if re.match(r'^[a-fA-F0-9]{40}$', value):
            return "sha1"
        if re.match(r'^[a-fA-F0-9]{64}$', value):
            return "sha256"
        
        # URL
        if value.startswith(('http://', 'https://', 'ftp://')):
            return "url"
        
        # Default to text pattern
        return "text"
    
    def _match_pattern(self, pattern: str, text: str) -> bool:
        """Match pattern against text."""
        import re
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            return False
    
    def _load_builtin_indicators(self) -> None:
        """Load built-in threat indicators."""
        builtin_indicators = [
            # SQL Injection patterns
            ThreatIndicator(
                indicator_type="pattern",
                value=r"(?i)(union\s+select|drop\s+table|exec\s*\(|script\s*>)",
                threat_type=ThreatType.SQL_INJECTION,
                severity=SeverityLevel.HIGH,
                confidence=0.9,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="SQL injection attack patterns",
                tags={"sql", "injection", "database"}
            ),
            
            # XSS patterns
            ThreatIndicator(
                indicator_type="pattern",
                value=r"(?i)(<script|javascript:|vbscript:|onload=|onerror=)",
                threat_type=ThreatType.XSS_ATTACK,
                severity=SeverityLevel.HIGH,
                confidence=0.85,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="Cross-site scripting attack patterns",
                tags={"xss", "script", "injection"}
            ),
            
            # Command injection patterns
            ThreatIndicator(
                indicator_type="pattern",
                value=r"(?i)(;|\||&|`|\$\(|wget|curl|nc|netcat|bash|sh|cmd|powershell)",
                threat_type=ThreatType.COMMAND_INJECTION,
                severity=SeverityLevel.CRITICAL,
                confidence=0.8,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="Command injection attack patterns",
                tags={"command", "injection", "shell"}
            ),
            
            # Prompt injection patterns
            ThreatIndicator(
                indicator_type="pattern",
                value=r"(?i)(ignore\s+previous|forget\s+instructions|system\s+prompt|jailbreak|bypass)",
                threat_type=ThreatType.PROMPT_INJECTION,
                severity=SeverityLevel.HIGH,
                confidence=0.75,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="LLM prompt injection patterns",
                tags={"prompt", "injection", "llm"}
            ),
            
            # Malicious domains (examples)
            ThreatIndicator(
                indicator_type="domain",
                value="evil-domain.com",
                threat_type=ThreatType.MALICIOUS_PAYLOAD,
                severity=SeverityLevel.HIGH,
                confidence=0.95,
                source=ThreatIntelligenceSource.COMMUNITY,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="Known malicious domain",
                tags={"malware", "phishing", "domain"}
            ),
            
            # Suspicious IPs (examples)
            ThreatIndicator(
                indicator_type="ip",
                value="192.168.1.100",
                threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                severity=SeverityLevel.MEDIUM,
                confidence=0.7,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                description="Suspicious IP address",
                tags={"ip", "suspicious", "access"}
            )
        ]
        
        for indicator in builtin_indicators:
            self.add_indicator(indicator)
    
    async def _load_internal_indicators(self) -> List[ThreatIndicator]:
        """Load internal threat indicators."""
        indicators = []
        
        # Load from internal database/files
        internal_file = Path("data/internal_indicators.json")
        if internal_file.exists():
            try:
                with open(internal_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        indicator = ThreatIndicator(
                            indicator_type=item["indicator_type"],
                            value=item["value"],
                            threat_type=ThreatType(item["threat_type"]),
                            severity=SeverityLevel(item["severity"]),
                            confidence=item["confidence"],
                            source=ThreatIntelligenceSource.INTERNAL,
                            first_seen=datetime.fromisoformat(item["first_seen"]),
                            last_seen=datetime.fromisoformat(item["last_seen"]),
                            description=item["description"],
                            tags=set(item.get("tags", []))
                        )
                        indicators.append(indicator)
            except Exception as e:
                self.logger.error(f"Failed to load internal indicators: {e}")
                self.metrics["update_errors"] += 1
        
        return indicators
    
    async def _load_community_indicators(self) -> List[ThreatIndicator]:
        """Load community threat indicators."""
        indicators = []
        
        # In a real implementation, this would connect to community feeds
        # For now, return empty list
        return indicators
    
    async def _load_commercial_indicators(self) -> List[ThreatIndicator]:
        """Load commercial threat indicators."""
        indicators = []
        
        # In a real implementation, this would connect to commercial feeds
        # like VirusTotal, AlienVault, etc.
        return indicators
    
    async def _load_osint_indicators(self) -> List[ThreatIndicator]:
        """Load OSINT threat indicators."""
        indicators = []
        
        # In a real implementation, this would connect to OSINT feeds
        return indicators
    
    async def _update_all_sources(self) -> None:
        """Update indicators from all sources."""
        for source_name, source_func in self.sources.items():
            try:
                indicators = await source_func()
                for indicator in indicators:
                    self.add_indicator(indicator)
                self.metrics["sources_updated"] += 1
            except Exception as e:
                self.logger.error(f"Failed to update source {source_name}: {e}")
                self.metrics["update_errors"] += 1
        
        self.metrics["last_update"] = datetime.now(timezone.utc)
    
    async def _update_loop(self) -> None:
        """Background update loop."""
        while self._running:
            try:
                await asyncio.sleep(self.update_interval)
                await self._update_all_sources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                self.metrics["update_errors"] += 1
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired_indicators()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def _cleanup_expired_indicators(self) -> None:
        """Remove expired indicators."""
        expired_keys = [
            key for key, indicator in self.indicators.items()
            if indicator.is_expired()
        ]
        
        for key in expired_keys:
            del self.indicators[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired indicators")
    
    def _cleanup_old_indicators(self) -> None:
        """Remove old indicators when limit is exceeded."""
        if len(self.indicators) <= self.max_indicators:
            return
        
        # Sort by last_seen and remove oldest
        sorted_indicators = sorted(
            self.indicators.items(),
            key=lambda x: x[1].last_seen
        )
        
        to_remove = len(self.indicators) - self.max_indicators
        for i in range(to_remove):
            key = sorted_indicators[i][0]
            del self.indicators[key]
        
        self.logger.info(f"Cleaned up {to_remove} old indicators")


class ThreatIntelligenceDetector:
    """Detector that uses threat intelligence to identify threats."""
    
    def __init__(self, intelligence_engine: ThreatIntelligenceEngine):
        self.intelligence_engine = intelligence_engine
        self.name = "ThreatIntelligenceDetector"
    
    async def detect(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect threats using threat intelligence."""
        results = []
        
        # Check inputs
        for key, value in context.get("inputs", {}).items():
            if isinstance(value, str):
                indicator = await self.intelligence_engine.check_threat(value)
                if indicator:
                    results.append({
                        "threat_type": indicator.threat_type,
                        "severity": indicator.severity,
                        "confidence": indicator.confidence,
                        "message": f"Threat intelligence match: {indicator.description}",
                        "context": {
                            "input_key": key,
                            "indicator_type": indicator.indicator_type,
                            "source": indicator.source.value,
                            "attribution": indicator.attribution,
                            "campaign": indicator.campaign,
                            "tags": list(indicator.tags)
                        }
                    })
        
        # Check outputs
        outputs = context.get("outputs")
        if outputs and isinstance(outputs, str):
            indicator = await self.intelligence_engine.check_threat(outputs)
            if indicator:
                results.append({
                    "threat_type": indicator.threat_type,
                    "severity": indicator.severity,
                    "confidence": indicator.confidence,
                    "message": f"Threat intelligence match in output: {indicator.description}",
                    "context": {
                        "output_match": True,
                        "indicator_type": indicator.indicator_type,
                        "source": indicator.source.value,
                        "attribution": indicator.attribution,
                        "campaign": indicator.campaign,
                        "tags": list(indicator.tags)
                    }
                })
        
        return results 