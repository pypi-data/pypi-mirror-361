"""
Threat Intelligence Enricher

Integrates threat intelligence into security events for enhanced reporting and analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..core.exceptions import ThreatIntelligenceError
from ..core.types import SecurityEvent
from .exa_service import ExaThreatIntelligence
from .intelligence_types import ThreatIntelligence

logger = logging.getLogger(__name__)


@dataclass
class EnrichedSecurityEvent:
    """Security event enriched with threat intelligence"""
    original_event: SecurityEvent
    threat_intelligence: Optional[ThreatIntelligence] = None
    intelligence_confidence: float = 0.0
    enrichment_timestamp: Optional[datetime] = None
    enrichment_errors: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.enrichment_timestamp is None:
            self.enrichment_timestamp = datetime.now()
        if self.enrichment_errors is None:
            self.enrichment_errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert enriched event to dictionary"""
        return {
            'original_event': self.original_event.to_dict(),
            'threat_intelligence': self.threat_intelligence.to_dict() if self.threat_intelligence else None,
            'intelligence_confidence': self.intelligence_confidence,
            'enrichment_timestamp': self.enrichment_timestamp.isoformat() if self.enrichment_timestamp else None,
            'enrichment_errors': self.enrichment_errors or []
        }


class ThreatIntelligenceEnricher:
    """
    Enterprise-grade threat intelligence enricher
    
    Integrates with detection engine to provide real-time threat intelligence
    for security events, enhancing reports with contextual information.
    """
    
    def __init__(self, intelligence_service: ExaThreatIntelligence, config: Optional[Dict[str, Any]] = None):
        """
        Initialize threat intelligence enricher
        
        Args:
            intelligence_service: Exa threat intelligence service
            config: Optional configuration dictionary
        """
        self.intelligence_service = intelligence_service
        self.config = config or {}
        
        # Configuration options
        self.enabled = self.config.get('enabled', True)
        self.auto_enrich = self.config.get('auto_enrich', True)
        self.min_severity_for_enrichment = self.config.get('min_severity_for_enrichment', 'MEDIUM')
        self.enrichment_timeout = self.config.get('enrichment_timeout', 10.0)
        self.max_concurrent_enrichments = self.config.get('max_concurrent_enrichments', 5)
        
        # Semaphore for concurrent enrichments
        self.enrichment_semaphore = asyncio.Semaphore(self.max_concurrent_enrichments)
        
        # Statistics
        self.enrichment_stats = {
            'total_events': 0,
            'successful_enrichments': 0,
            'failed_enrichments': 0,
            'cached_enrichments': 0,
            'skipped_enrichments': 0
        }
        
        logger.info(f"Initialized threat intelligence enricher (enabled: {self.enabled})")
    
    async def enrich_security_event(self, event: SecurityEvent) -> EnrichedSecurityEvent:
        """
        Enrich a security event with threat intelligence
        
        Args:
            event: Security event to enrich
            
        Returns:
            EnrichedSecurityEvent with intelligence data
        """
        self.enrichment_stats['total_events'] += 1
        
        if not self.enabled:
            logger.debug("Threat intelligence enrichment disabled")
            self.enrichment_stats['skipped_enrichments'] += 1
            return EnrichedSecurityEvent(original_event=event)
        
        # Check if event meets enrichment criteria
        if not self._should_enrich_event(event):
            logger.debug(f"Event {event.event_id} doesn't meet enrichment criteria")
            self.enrichment_stats['skipped_enrichments'] += 1
            return EnrichedSecurityEvent(original_event=event)
        
        async with self.enrichment_semaphore:
            try:
                # Get threat intelligence with timeout
                intelligence = await asyncio.wait_for(
                    self.intelligence_service.get_threat_intelligence(
                        threat_type=event.threat_type.value,
                        context=self._build_intelligence_context(event)
                    ),
                    timeout=self.enrichment_timeout
                )
                
                enriched_event = EnrichedSecurityEvent(
                    original_event=event,
                    threat_intelligence=intelligence,
                    intelligence_confidence=intelligence.confidence_score
                )
                
                self.enrichment_stats['successful_enrichments'] += 1
                logger.info(f"Successfully enriched event {event.event_id} with intelligence")
                
                return enriched_event
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout enriching event {event.event_id}")
                self.enrichment_stats['failed_enrichments'] += 1
                return EnrichedSecurityEvent(
                    original_event=event,
                    enrichment_errors=["Enrichment timeout"]
                )
                
            except ThreatIntelligenceError as e:
                logger.error(f"Intelligence error enriching event {event.event_id}: {str(e)}")
                self.enrichment_stats['failed_enrichments'] += 1
                return EnrichedSecurityEvent(
                    original_event=event,
                    enrichment_errors=[f"Intelligence error: {str(e)}"]
                )
                
            except Exception as e:
                logger.error(f"Unexpected error enriching event {event.event_id}: {str(e)}")
                self.enrichment_stats['failed_enrichments'] += 1
                return EnrichedSecurityEvent(
                    original_event=event,
                    enrichment_errors=[f"Unexpected error: {str(e)}"]
                )
    
    async def enrich_multiple_events(self, events: List[SecurityEvent]) -> List[EnrichedSecurityEvent]:
        """
        Enrich multiple security events concurrently
        
        Args:
            events: List of security events to enrich
            
        Returns:
            List of enriched security events
        """
        if not events:
            return []
        
        logger.info(f"Starting concurrent enrichment of {len(events)} events")
        
        # Create enrichment tasks
        enrichment_tasks = [
            self.enrich_security_event(event) for event in events
        ]
        
        # Execute all enrichments concurrently
        enriched_events = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        # Handle exceptions in results
        results = []
        for i, result in enumerate(enriched_events):
            if isinstance(result, Exception):
                logger.error(f"Exception enriching event {i}: {str(result)}")
                results.append(EnrichedSecurityEvent(
                    original_event=events[i],
                    enrichment_errors=[f"Exception: {str(result)}"]
                ))
            else:
                results.append(result)
        
        successful_count = sum(1 for r in results if not r.enrichment_errors)
        logger.info(f"Completed enrichment: {successful_count}/{len(events)} successful")
        
        return results
    
    def _should_enrich_event(self, event: SecurityEvent) -> bool:
        """
        Determine if an event should be enriched with threat intelligence
        
        Args:
            event: Security event to evaluate
            
        Returns:
            True if event should be enriched
        """
        # Check severity threshold
        severity_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        event_severity = severity_order.get(event.severity, 0)
        min_severity = severity_order.get(self.min_severity_for_enrichment, 2)
        
        if event_severity < min_severity:
            return False
        
        # Check if threat type is supported
        if event.threat_type not in self.intelligence_service.THREAT_QUERIES:
            logger.debug(f"Threat type {event.threat_type} not supported for enrichment")
            return False
        
        # Check confidence threshold
        if event.confidence_score < 0.5:
            logger.debug(f"Event confidence too low for enrichment: {event.confidence_score}")
            return False
        
        return True
    
    def _build_intelligence_context(self, event: SecurityEvent) -> Dict[str, Any]:
        """
        Build context for threat intelligence queries
        
        Args:
            event: Security event
            
        Returns:
            Context dictionary for intelligence queries
        """
        context = {
            'event_id': event.event_id,
            'threat_type': event.threat_type,
            'severity': event.severity,
            'confidence_score': event.confidence_score,
            'timestamp': event.timestamp.isoformat(),
            'source': event.source
        }
        
        # Add relevant metadata
        if hasattr(event, 'metadata') and event.metadata:
            context['metadata'] = event.metadata
        
        # Add evidence if available
        if hasattr(event, 'evidence') and event.evidence:
            # Sanitize evidence to remove sensitive data
            sanitized_evidence = self._sanitize_evidence(event.evidence)
            context['evidence_patterns'] = sanitized_evidence
        
        return context
    
    def _sanitize_evidence(self, evidence: List[str]) -> List[str]:
        """
        Sanitize evidence to remove sensitive information
        
        Args:
            evidence: List of evidence strings
            
        Returns:
            Sanitized evidence list
        """
        sanitized = []
        
        for item in evidence:
            # Remove potential sensitive data patterns
            # This is a simplified implementation for demo
            if len(item) > 100:
                sanitized.append(item[:50] + "..." + item[-20:])
            else:
                sanitized.append(item)
        
        return sanitized
    
    def generate_intelligence_report(self, enriched_event: EnrichedSecurityEvent) -> str:
        """
        Generate human-readable intelligence report
        
        Args:
            enriched_event: Enriched security event
            
        Returns:
            Formatted intelligence report
        """
        if not enriched_event.threat_intelligence:
            return self._generate_basic_report(enriched_event.original_event)
        
        intelligence = enriched_event.threat_intelligence
        event = enriched_event.original_event
        
        # Build comprehensive report
        report_sections = []
        
        # Header
        report_sections.append("🚨 **THREAT DETECTION ALERT** - ENHANCED WITH INTELLIGENCE")
        report_sections.append("")
        
        # Detection Summary
        report_sections.append("**Detection Summary:**")
        report_sections.append(f"- Attack Type: {event.threat_type.value.replace('_', ' ').title()}")
        report_sections.append(f"- Severity: {event.severity.value}")
        report_sections.append(f"- Confidence: {event.confidence:.0%}")
        report_sections.append(f"- Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report_sections.append("")
        
        # CVE Intelligence
        if intelligence.cve_intelligence and intelligence.cve_intelligence.cve_id:
            report_sections.append("🔍 **CVE INTELLIGENCE:**")
            cve = intelligence.cve_intelligence
            report_sections.append(f"- CVE ID: {cve.cve_id}")
            if cve.cvss_score:
                report_sections.append(f"- CVSS Score: {cve.cvss_score}")
            if cve.description:
                report_sections.append(f"- Description: {cve.description}")
            report_sections.append("")
        
        # Attack Pattern Intelligence
        if intelligence.attack_pattern_intelligence:
            report_sections.append("🎯 **ATTACK PATTERN ANALYSIS:**")
            pattern = intelligence.attack_pattern_intelligence
            if pattern.technique_name:
                report_sections.append(f"- Technique: {pattern.technique_name}")
            if pattern.complexity_level:
                report_sections.append(f"- Complexity: {pattern.complexity_level}")
            if pattern.detection_methods:
                report_sections.append(f"- Detection Methods: {', '.join(pattern.detection_methods)}")
            report_sections.append("")
        
        # Attribution Intelligence
        if intelligence.attribution_intelligence and intelligence.attribution_intelligence.actor_groups:
            report_sections.append("🕵️ **ATTRIBUTION INTELLIGENCE:**")
            attribution = intelligence.attribution_intelligence
            if attribution.actor_groups:
                report_sections.append(f"- Threat Groups: {', '.join(attribution.actor_groups[:3])}")
            if attribution.target_sectors:
                report_sections.append(f"- Target Sectors: {', '.join(attribution.target_sectors)}")
            if attribution.recent_activity:
                report_sections.append(f"- Recent Activity: {attribution.recent_activity}")
            report_sections.append("")
        
        # Trend Intelligence
        if intelligence.trend_intelligence and intelligence.trend_intelligence.trend_description:
            report_sections.append("📈 **THREAT LANDSCAPE:**")
            trend = intelligence.trend_intelligence
            if trend.trend_description:
                report_sections.append(f"- Trend: {trend.trend_description}")
            if trend.frequency_change:
                report_sections.append(f"- Frequency Change: {trend.frequency_change}")
            if trend.industry_impact:
                report_sections.append(f"- Industry Impact: {trend.industry_impact}")
            report_sections.append("")
        
        # Mitigation Recommendations
        if intelligence.mitigation_intelligence:
            report_sections.append("💡 **RECOMMENDED ACTIONS:**")
            mitigation = intelligence.mitigation_intelligence
            if mitigation.primary_mitigation:
                report_sections.append(f"1. **PRIMARY**: {mitigation.primary_mitigation}")
            
            for i, secondary in enumerate(mitigation.secondary_mitigations[:3], 2):
                report_sections.append(f"{i}. **SECONDARY**: {secondary}")
            
            if mitigation.recommended_tools:
                report_sections.append(f"**Tools**: {', '.join(mitigation.recommended_tools)}")
            report_sections.append("")
        
        # Intelligence Metadata
        report_sections.append("📊 **INTELLIGENCE METADATA:**")
        report_sections.append(f"- Confidence Score: {intelligence.confidence_score:.0%}")
        report_sections.append(f"- Last Updated: {intelligence.last_updated.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report_sections.append(f"- Source: {intelligence.source.value}")
        
        return "\n".join(report_sections)
    
    def _generate_basic_report(self, event: SecurityEvent) -> str:
        """Generate basic report for events without intelligence"""
        return f"""
🚨 **THREAT DETECTION ALERT** - BASIC REPORT

**Detection Summary:**
- Attack Type: {event.threat_type.value.replace('_', ' ').title()}
- Severity: {event.severity.value}
- Confidence: {event.confidence:.0%}
- Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

**Note:** Threat intelligence enrichment not available for this event.
"""
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        return {
            **self.enrichment_stats,
            'success_rate': (
                self.enrichment_stats['successful_enrichments'] / 
                max(1, self.enrichment_stats['total_events'])
            ),
            'enabled': self.enabled,
            'auto_enrich': self.auto_enrich
        }
    
    def reset_stats(self):
        """Reset enrichment statistics"""
        self.enrichment_stats = {
            'total_events': 0,
            'successful_enrichments': 0,
            'failed_enrichments': 0,
            'cached_enrichments': 0,
            'skipped_enrichments': 0
        }
        logger.info("Enrichment statistics reset") 