"""
Threat Intelligence Enricher

Integrates threat intelligence into security events for enhanced reporting and analysis.
Features LLM orchestrator for intelligent query generation and report synthesis.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# LLM and Weave imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..core.exceptions import ThreatIntelligenceError
from ..core.types import SecurityEvent
from ..infrastructure.monitoring.weave_service import WeaveService
from .exa_service import ExaThreatIntelligence
from .intelligence_types import ThreatIntelligence

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceOrchestration:
    """Results from LLM orchestrator analysis"""
    threat_analysis: str
    search_queries: List[str]
    intelligence_priorities: List[str]
    business_impact_assessment: str
    confidence_score: float


@dataclass
class EnrichedSecurityEvent:
    """Security event enriched with threat intelligence"""
    original_event: SecurityEvent
    orchestration: Optional[IntelligenceOrchestration] = None
    threat_intelligence: Optional[ThreatIntelligence] = None
    intelligence_confidence: float = 0.0
    enrichment_timestamp: Optional[datetime] = None
    enrichment_errors: Optional[List[str]] = None
    llm_generated_report: Optional[str] = None
    
    def __post_init__(self):
        if self.enrichment_timestamp is None:
            self.enrichment_timestamp = datetime.now()
        if self.enrichment_errors is None:
            self.enrichment_errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert enriched event to dictionary"""
        return {
            'original_event': self.original_event.to_dict(),
            'orchestration': {
                'threat_analysis': self.orchestration.threat_analysis,
                'search_queries': self.orchestration.search_queries,
                'intelligence_priorities': self.orchestration.intelligence_priorities,
                'business_impact_assessment': self.orchestration.business_impact_assessment,
                'confidence_score': self.orchestration.confidence_score
            } if self.orchestration else None,
            'threat_intelligence': self.threat_intelligence.to_dict() if self.threat_intelligence else None,
            'intelligence_confidence': self.intelligence_confidence,
            'enrichment_timestamp': self.enrichment_timestamp.isoformat() if self.enrichment_timestamp else None,
            'enrichment_errors': self.enrichment_errors or [],
            'llm_generated_report': self.llm_generated_report
        }


class ThreatIntelligenceEnricher:
    """
    Enterprise-grade threat intelligence enricher with LLM orchestration
    
    Features:
    1. LLM Orchestrator: Analyzes security events and generates intelligent search strategies
    2. Enhanced Exa Integration: Uses LLM-generated queries for targeted intelligence gathering
    3. Intelligent Report Synthesis: Combines orchestrator insights with Exa intelligence
    """
    
    def __init__(self, intelligence_service: ExaThreatIntelligence, config: Optional[Dict[str, Any]] = None):
        """
        Initialize threat intelligence enricher with LLM orchestration
        
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
        self.enrichment_timeout = self.config.get('enrichment_timeout', 15.0)  # Increased for LLM calls
        self.max_concurrent_enrichments = self.config.get('max_concurrent_enrichments', 3)  # Reduced for LLM calls
        
        # LLM configuration (simplified - now handled by AgenticOrchestrator)
        self.enable_llm_orchestration = self.config.get('enable_llm_orchestration', True) and OPENAI_AVAILABLE
        self.llm_timeout = self.config.get('llm_timeout', 30.0)
        
        # Initialize OpenAI client (for backward compatibility)
        self.openai_client = None
        if self.enable_llm_orchestration and OPENAI_AVAILABLE:
            api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("LLM orchestration enabled with OpenAI")
            else:
                self.enable_llm_orchestration = False
                logger.warning("OpenAI API key not found")
        
        # Initialize Weave service
        from ..core.config import WeaveConfig
        weave_config = WeaveConfig(**self.config.get('weave', {}))
        self.weave_service = WeaveService(weave_config)
        
        logger.info(f"Weave service initialized (enabled: {self.weave_service.is_enabled})")
        
        # Semaphore for concurrent enrichments
        self.enrichment_semaphore = asyncio.Semaphore(self.max_concurrent_enrichments)
        
        # Statistics
        self.enrichment_stats = {
            'total_events': 0,
            'successful_enrichments': 0,
            'failed_enrichments': 0,
            'cached_enrichments': 0,
            'skipped_enrichments': 0,
            'orchestration_successes': 0,
            'orchestration_failures': 0,
            'llm_reports_generated': 0,
            'llm_report_failures': 0
        }
        
        logger.info(f"Initialized threat intelligence enricher (enabled: {self.enabled}, LLM: {self.enable_llm_orchestration})")

    async def enrich_security_event(self, event: SecurityEvent) -> EnrichedSecurityEvent:
        """
        Enrich a security event with LLM orchestration and threat intelligence
        
        Args:
            event: Security event to enrich
            
        Returns:
            EnrichedSecurityEvent with orchestration and intelligence data
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
                # Step 1: LLM Orchestrator Analysis
                orchestration = None
                if self.enable_llm_orchestration:
                    orchestration = await self._orchestrate_intelligence_gathering(event)
                
                # Step 2: Enhanced Exa Intelligence Gathering
                intelligence = await self._gather_enhanced_intelligence(event, orchestration)
                
                # Step 3: Create enriched event
                enriched_event = EnrichedSecurityEvent(
                    original_event=event,
                    orchestration=orchestration,
                    threat_intelligence=intelligence,
                    intelligence_confidence=intelligence.confidence_score if intelligence else 0.0
                )
                
                self.enrichment_stats['successful_enrichments'] += 1
                logger.info(f"Successfully enriched event {event.event_id} with orchestration and intelligence")
                
                return enriched_event
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout enriching event {event.event_id}")
                self.enrichment_stats['failed_enrichments'] += 1
                return EnrichedSecurityEvent(
                    original_event=event,
                    enrichment_errors=["Enrichment timeout"]
                )
                
            except Exception as e:
                logger.error(f"Error enriching event {event.event_id}: {str(e)}")
                self.enrichment_stats['failed_enrichments'] += 1
                return EnrichedSecurityEvent(
                    original_event=event,
                    enrichment_errors=[f"Enrichment error: {str(e)}"]
                )

    async def _orchestrate_intelligence_gathering(self, event: SecurityEvent) -> Optional[IntelligenceOrchestration]:
        """
        LLM Orchestrator: Analyzes security event and generates intelligent search strategy
        
        Args:
            event: Security event to analyze
            
        Returns:
            IntelligenceOrchestration with analysis and search strategy
        """
        # This is now handled by AgenticOrchestrator in the main sentinel class
        logger.debug("Orchestration now handled by AgenticOrchestrator")
        return None

    async def _gather_enhanced_intelligence(
        self, 
        event: SecurityEvent, 
        orchestration: Optional[IntelligenceOrchestration]
    ) -> Optional[ThreatIntelligence]:
        """
        Gather enhanced threat intelligence using LLM-generated queries
        
        Args:
            event: Security event
            orchestration: LLM orchestration results
            
        Returns:
            ThreatIntelligence object with enhanced data
        """
        try:
            # Use LLM-generated queries if available, otherwise fall back to default
            if orchestration and orchestration.search_queries:
                # Use orchestrator's intelligent queries
                custom_queries = orchestration.search_queries
                logger.info(f"Using {len(custom_queries)} LLM-generated queries for intelligence gathering")
                
                # Temporarily override the service's search queries
                original_queries = self.intelligence_service.THREAT_SEARCH_QUERIES.get(event.threat_type.value, [])
                self.intelligence_service.THREAT_SEARCH_QUERIES[event.threat_type.value] = custom_queries
                
                try:
                    intelligence = await asyncio.wait_for(
                        self.intelligence_service.get_threat_intelligence(
                            threat_type=event.threat_type.value,
                            context=self._build_intelligence_context(event)
                        ),
                        timeout=self.enrichment_timeout
                    )
                    
                    # Enhance intelligence with orchestration insights
                    if intelligence and orchestration:
                        intelligence.processing_notes.append(f"Enhanced with LLM orchestration (confidence: {orchestration.confidence_score:.0%})")
                        intelligence.processing_notes.append(f"Business impact: {orchestration.business_impact_assessment}")
                        
                        # Boost confidence if orchestration was confident
                        if orchestration.confidence_score > 0.8:
                            intelligence.confidence_score = min(intelligence.confidence_score + 0.1, 1.0)
                    
                    return intelligence
                    
                finally:
                    # Restore original queries
                    self.intelligence_service.THREAT_SEARCH_QUERIES[event.threat_type.value] = original_queries
            
            else:
                # Fall back to standard intelligence gathering
                return await asyncio.wait_for(
                    self.intelligence_service.get_threat_intelligence(
                        threat_type=event.threat_type.value,
                        context=self._build_intelligence_context(event)
                    ),
                    timeout=self.enrichment_timeout
                )
                
        except Exception as e:
            logger.error(f"Enhanced intelligence gathering failed: {str(e)}")
            return None

    async def generate_orchestrated_intelligence_report(self, enriched_event: EnrichedSecurityEvent) -> str:
        """
        Generate comprehensive intelligence report using LLM synthesis
        
        Args:
            enriched_event: Enriched security event with orchestration and intelligence
            
        Returns:
            Comprehensive, actionable intelligence report
        """
        if not self.enable_llm_orchestration:
            return await self.generate_enhanced_intelligence_report(enriched_event)
        
        try:
            system_prompt = """You are a senior cybersecurity analyst creating executive-level threat intelligence reports. Generate a comprehensive, actionable report that security teams and executives can use to make informed decisions.

Your report should:
1. Provide clear executive summary
2. Explain technical details in accessible language
3. Include specific, actionable recommendations
4. Assess business impact and risk
5. Provide immediate and long-term response strategies
6. Use professional formatting with clear sections

Format in markdown with proper headers and structure."""

            # Prepare comprehensive context
            context = self._prepare_orchestrated_context(enriched_event)
            
            user_prompt = f"""
Create a comprehensive threat intelligence report based on this analysis:

**SECURITY EVENT:**
{context['event_summary']}

**LLM ORCHESTRATION ANALYSIS:**
{context['orchestration_summary']}

**THREAT INTELLIGENCE DATA:**
{context['intelligence_summary']}

**EXTERNAL SOURCES:**
{context['sources_summary']}

Generate a professional, executive-ready threat intelligence report that provides both technical depth and strategic insights.
"""

            response = await asyncio.wait_for(
                self.openai_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=3000
                ),
                timeout=self.llm_timeout
            )
            
            report = response.choices[0].message.content
            
            # Update statistics
            self.enrichment_stats['llm_reports_generated'] += 1
            
            # Store the generated report
            enriched_event.llm_generated_report = report
            
            logger.info(f"Generated orchestrated intelligence report for event {enriched_event.original_event.event_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"Orchestrated report generation failed: {e}")
            self.enrichment_stats['llm_report_failures'] += 1
            
            # Fallback to enhanced report
            return await self.generate_enhanced_intelligence_report(enriched_event)

    def _prepare_orchestrated_context(self, enriched_event: EnrichedSecurityEvent) -> Dict[str, str]:
        """
        Prepare comprehensive context for orchestrated report generation
        
        Args:
            enriched_event: Enriched security event
            
        Returns:
            Context dictionary with all relevant information
        """
        event = enriched_event.original_event
        orchestration = enriched_event.orchestration
        intelligence = enriched_event.threat_intelligence
        
        # Event summary
        event_summary = f"""
- Threat Type: {event.threat_type.value.replace('_', ' ').title()}
- Severity: {event.severity.value}
- Confidence: {event.confidence:.0%}
- Detection Method: {event.detection_method}
- Agent: {event.agent_id}
- Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Message: {event.message}
"""

        # Orchestration summary
        orchestration_summary = "No orchestration analysis available"
        if orchestration:
            orchestration_summary = f"""
**Threat Analysis:** {orchestration.threat_analysis}

**Intelligence Priorities:** {', '.join(orchestration.intelligence_priorities)}

**Business Impact:** {orchestration.business_impact_assessment}

**Orchestration Confidence:** {orchestration.confidence_score:.0%}
"""

        # Intelligence summary
        intelligence_summary = "No detailed intelligence available"
        if intelligence:
            intel_parts = []
            
            if intelligence.cve_intelligence and intelligence.cve_intelligence.cve_id:
                intel_parts.append(f"CVE: {intelligence.cve_intelligence.cve_id}")
                if intelligence.cve_intelligence.cvss_score:
                    intel_parts.append(f"CVSS: {intelligence.cve_intelligence.cvss_score}")
            
            if intelligence.attack_pattern_intelligence:
                if intelligence.attack_pattern_intelligence.technique_name:
                    intel_parts.append(f"Attack Technique: {intelligence.attack_pattern_intelligence.technique_name}")
            
            if intelligence.mitigation_intelligence:
                if intelligence.mitigation_intelligence.primary_mitigation:
                    intel_parts.append(f"Primary Mitigation: {intelligence.mitigation_intelligence.primary_mitigation}")
            
            if intelligence.attribution_intelligence and intelligence.attribution_intelligence.actor_groups:
                intel_parts.append(f"Associated Groups: {', '.join(intelligence.attribution_intelligence.actor_groups[:2])}")
            
            if intelligence.trend_intelligence and intelligence.trend_intelligence.trend_description:
                intel_parts.append(f"Trend: {intelligence.trend_intelligence.trend_description}")
            
            intelligence_summary = '\n'.join(intel_parts) if intel_parts else "No specific intelligence patterns identified"

        # Sources summary
        sources_summary = "No external sources available"
        if intelligence and hasattr(intelligence, 'raw_data') and intelligence.raw_data.get('sources'):
            sources = intelligence.raw_data['sources'][:3]
            sources_summary = '\n'.join(sources)

        return {
            'event_summary': event_summary,
            'orchestration_summary': orchestration_summary,
            'intelligence_summary': intelligence_summary,
            'sources_summary': sources_summary
        }
    
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
        event_severity = severity_order.get(event.severity.value, 0)
        min_severity = severity_order.get(self.min_severity_for_enrichment, 2)
        
        if event_severity < min_severity:
            return False
        
        # Check if threat type is supported
        if event.threat_type.value not in self.intelligence_service.THREAT_SEARCH_QUERIES:
            logger.debug(f"Threat type {event.threat_type.value} not supported for enrichment")
            return False
        
        # Check confidence threshold
        if event.confidence < 0.5:
            logger.debug(f"Event confidence too low for enrichment: {event.confidence}")
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
            'threat_type': event.threat_type.value,
            'severity': event.severity.value,
            'confidence_score': event.confidence,
            'timestamp': event.timestamp.isoformat(),
            'detection_method': event.detection_method
        }
        
        # Add relevant context data
        if event.context:
            context['context'] = event.context
        
        # Add raw data if available
        if event.raw_data:
            context['raw_data'] = event.raw_data[:200] + "..." if len(event.raw_data) > 200 else event.raw_data
        
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
    
    async def generate_enhanced_intelligence_report(self, enriched_event: EnrichedSecurityEvent) -> str:
        """
        Generate AI-enhanced intelligence report using LLM
        
        Args:
            enriched_event: Enriched security event
            
        Returns:
            Professional, contextual intelligence report
        """
        if not self.enable_llm_orchestration:
            return self.generate_intelligence_report(enriched_event)
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(enriched_event)
            
            # Generate report using LLM with Weave tracing
            report = await self._generate_llm_report_with_weave_service(context, enriched_event)
            
            # Update statistics
            self.enrichment_stats['llm_reports_generated'] += 1
            
            # Store the generated report
            enriched_event.llm_generated_report = report
            
            return report
            
        except Exception as e:
            logger.error(f"LLM report generation failed: {e}")
            self.enrichment_stats['llm_report_failures'] += 1
            
            # Fallback to template-based report
            return self.generate_intelligence_report(enriched_event)
    
    async def _generate_llm_report_with_weave_service(self, context: Dict[str, Any], enriched_event: EnrichedSecurityEvent) -> str:
        """Generate LLM report with Weave service tracing"""
        start_time = time.time()
        
        try:
            # Log the LLM call with Weave
            await self.weave_service.log_llm_call(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "Generate threat intelligence report"},
                    {"role": "user", "content": str(context)}
                ]
            )
            
            report = await self._generate_llm_report(context, enriched_event)
            
            # Log report generation
            await self.weave_service.log_report_generation(
                report_type="enhanced_intelligence_report",
                event_id=enriched_event.original_event.event_id,
                inputs=context,
                report_length=len(report),
                generation_time=time.time() - start_time
            )
            
            return report
            
        except Exception as e:
            # Log error
            await self.weave_service.log_report_generation(
                report_type="enhanced_intelligence_report",
                event_id=enriched_event.original_event.event_id,
                inputs=context,
                generation_time=time.time() - start_time,
                error=str(e)
            )
            raise
    
    async def _generate_llm_report(self, context: Dict[str, Any], enriched_event: EnrichedSecurityEvent) -> str:
        """
        Generate LLM report using OpenAI
        
        Args:
            context: LLM context data
            enriched_event: Enriched security event
            
        Returns:
            AI-generated intelligence report
        """
        system_prompt = """You are a cybersecurity threat intelligence analyst. Generate a professional, actionable security report based on the provided threat intelligence data. 

Your report should:
1. Be clear, concise, and professional (no emojis)
2. Focus on actionable insights and recommendations
3. Explain the threat's business impact
4. Provide specific mitigation steps
5. Include relevant technical details
6. Use proper security terminology
7. Structure the report with clear sections

Format the report in markdown with proper headers and bullet points."""

        user_prompt = f"""
Analyze this security threat and generate a comprehensive intelligence report:

**Security Event:**
- Threat Type: {context['threat_type']}
- Severity: {context['severity']}
- Confidence: {context['confidence']:.0%}
- Timestamp: {context['timestamp']}
- Agent: {context['agent_id']}

**Threat Intelligence Data:**
{context['intelligence_summary']}

**Raw Intelligence Sources:**
{context['raw_sources']}

Generate a professional security intelligence report that security teams can act upon immediately.
"""

        try:
            response = await asyncio.wait_for(
                self.openai_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                ),
                timeout=self.llm_timeout
            )
            
            return response.choices[0].message.content
            
        except asyncio.TimeoutError:
            raise ThreatIntelligenceError("LLM report generation timed out")
        except Exception as e:
            raise ThreatIntelligenceError(f"LLM report generation failed: {str(e)}")
    
    def _prepare_llm_context(self, enriched_event: EnrichedSecurityEvent) -> Dict[str, Any]:
        """
        Prepare context data for LLM report generation
        
        Args:
            enriched_event: Enriched security event
            
        Returns:
            Context dictionary for LLM
        """
        event = enriched_event.original_event
        intelligence = enriched_event.threat_intelligence
        
        context = {
            'threat_type': event.threat_type.value.replace('_', ' ').title(),
            'severity': event.severity.value,
            'confidence': event.confidence,
            'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'agent_id': event.agent_id,
            'event_id': event.event_id
        }
        
        # Add intelligence summary
        if intelligence:
            intelligence_summary = []
            
            # CVE Intelligence
            if intelligence.cve_intelligence and intelligence.cve_intelligence.cve_id:
                cve = intelligence.cve_intelligence
                intelligence_summary.append(f"CVE: {cve.cve_id}")
                if cve.cvss_score:
                    intelligence_summary.append(f"CVSS Score: {cve.cvss_score}")
                if cve.description:
                    intelligence_summary.append(f"Description: {cve.description}")
            
            # Attack Pattern Intelligence
            if intelligence.attack_pattern_intelligence:
                pattern = intelligence.attack_pattern_intelligence
                if pattern.technique_name:
                    intelligence_summary.append(f"Attack Technique: {pattern.technique_name}")
                if pattern.complexity_level:
                    intelligence_summary.append(f"Complexity: {pattern.complexity_level}")
                if pattern.detection_methods:
                    intelligence_summary.append(f"Detection Methods: {', '.join(pattern.detection_methods)}")
            
            # Mitigation Intelligence
            if intelligence.mitigation_intelligence:
                mitigation = intelligence.mitigation_intelligence
                if mitigation.primary_mitigation:
                    intelligence_summary.append(f"Primary Mitigation: {mitigation.primary_mitigation}")
                if mitigation.recommended_tools:
                    intelligence_summary.append(f"Recommended Tools: {', '.join(mitigation.recommended_tools)}")
            
            # Attribution Intelligence
            if intelligence.attribution_intelligence:
                attribution = intelligence.attribution_intelligence
                if attribution.actor_groups:
                    intelligence_summary.append(f"Associated Threat Groups: {', '.join(attribution.actor_groups[:3])}")
                if attribution.target_sectors:
                    intelligence_summary.append(f"Target Sectors: {', '.join(attribution.target_sectors)}")
            
            # Trend Intelligence
            if intelligence.trend_intelligence:
                trend = intelligence.trend_intelligence
                if trend.trend_description:
                    intelligence_summary.append(f"Trend: {trend.trend_description}")
                if trend.industry_impact:
                    intelligence_summary.append(f"Industry Impact: {trend.industry_impact}")
            
            context['intelligence_summary'] = '\n'.join(intelligence_summary) if intelligence_summary else "No detailed intelligence available"
            
            # Add raw sources for context
            raw_sources = []
            if hasattr(intelligence, 'raw_data') and intelligence.raw_data.get('sources'):
                raw_sources = intelligence.raw_data['sources'][:3]  # Limit to top 3 sources
            context['raw_sources'] = '\n'.join(raw_sources) if raw_sources else "No external sources available"
            
        else:
            context['intelligence_summary'] = "No threat intelligence available"
            context['raw_sources'] = "No external sources available"
        
        return context
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        return {
            **self.enrichment_stats,
            'success_rate': (
                self.enrichment_stats['successful_enrichments'] / 
                max(1, self.enrichment_stats['total_events'])
            ),
            'llm_success_rate': (
                self.enrichment_stats['llm_reports_generated'] / 
                max(1, self.enrichment_stats['llm_reports_generated'] + self.enrichment_stats['llm_report_failures'])
            ),
            'enabled': self.enabled,
            'auto_enrich': self.auto_enrich,
            'llm_orchestration_enabled': self.enable_llm_orchestration,
            'weave_enabled': self.weave_service.is_enabled
        }
    
    def reset_stats(self):
        """Reset enrichment statistics"""
        self.enrichment_stats = {
            'total_events': 0,
            'successful_enrichments': 0,
            'failed_enrichments': 0,
            'cached_enrichments': 0,
            'skipped_enrichments': 0,
            'llm_reports_generated': 0,
            'llm_report_failures': 0
        }
        logger.info("Enrichment statistics reset") 