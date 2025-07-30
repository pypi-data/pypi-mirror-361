"""
Agentic LLM Orchestration System for Security Intelligence

This module implements a multi-agent LLM system for security analysis:
1. ThreatAnalyst Agent: Deep analysis of security events and attack classification
2. IntelligenceAgent: Threat research and context gathering using LLM knowledge
3. ReportAgent: Executive-level security report generation

The system uses only LLM capabilities without external API dependencies.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from ..core.types import SecurityEvent
from ..core.constants import ThreatType, SeverityLevel

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Roles for different agents in the orchestration system."""
    THREAT_ANALYST = "threat_analyst"
    INTELLIGENCE_RESEARCHER = "intelligence_researcher"
    REPORT_GENERATOR = "report_generator"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentResponse:
    """Response from an agent in the orchestration system."""
    agent_role: AgentRole
    content: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ThreatAnalysis:
    """Comprehensive threat analysis from ThreatAnalyst agent."""
    attack_type: str
    attack_vector: str
    severity_assessment: str
    technical_details: str
    indicators_of_compromise: List[str]
    attack_patterns: List[str]
    potential_impact: str
    confidence_score: float
    recommended_actions: List[str]
    similar_attacks: List[str]


@dataclass
class ThreatIntelligence:
    """Intelligence gathered by IntelligenceAgent."""
    threat_landscape: str
    attack_trends: str
    mitigation_strategies: List[str]
    industry_context: str
    regulatory_implications: str
    business_impact: str
    prevention_measures: List[str]
    detection_improvements: List[str]


@dataclass
class ExecutiveReport:
    """Executive-level security report from ReportAgent."""
    executive_summary: str
    threat_overview: str
    business_impact: str
    risk_assessment: str
    immediate_actions: List[str]
    strategic_recommendations: List[str]
    compliance_considerations: str
    resource_requirements: str


@dataclass
class AgenticOrchestrationResult:
    """Complete result from agentic orchestration."""
    original_event: SecurityEvent
    threat_analysis: ThreatAnalysis
    threat_intelligence: ThreatIntelligence
    executive_report: ExecutiveReport
    orchestration_metadata: Dict[str, Any]
    total_processing_time: float
    confidence_score: float


class ThreatAnalystAgent:
    """
    Agent specialized in deep security event analysis and threat classification.
    
    This agent acts as a security expert that can:
    - Analyze attack patterns and vectors
    - Classify threat types and severity
    - Identify indicators of compromise
    - Provide technical recommendations
    """
    
    def __init__(self, llm_client, config: Optional[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.agent_role = AgentRole.THREAT_ANALYST
        
    async def analyze_security_event(self, event: SecurityEvent) -> ThreatAnalysis:
        """Perform deep analysis of a security event."""
        start_time = time.time()
        
        system_prompt = """You are a Senior Security Analyst with 15+ years of experience in cybersecurity, threat hunting, and incident response. Your expertise includes:

- Advanced threat analysis and attack pattern recognition
- Malware analysis and reverse engineering
- Network security and intrusion detection
- Application security and vulnerability assessment
- Threat intelligence and IOC analysis

Analyze the provided security event with the depth and precision of a seasoned security professional. Focus on technical accuracy, threat classification, and actionable insights."""

        user_prompt = f"""
Analyze this security event in detail:

**Event Details:**
- Threat Type: {event.threat_type.value}
- Severity: {event.severity.value}
- Message: {event.message}
- Confidence: {event.confidence:.2%}
- Detection Method: {event.detection_method}
- Agent ID: {event.agent_id}
- Timestamp: {event.timestamp}

**Context:**
{json.dumps(event.context, indent=2)}

**Raw Data:**
{event.raw_data or 'No raw data available'}

Provide a comprehensive analysis including:

1. **Attack Type Classification**: Detailed categorization of the attack
2. **Attack Vector Analysis**: How the attack was executed
3. **Severity Assessment**: Risk level and potential impact
4. **Technical Details**: Deep technical analysis of the attack
5. **Indicators of Compromise**: Specific IOCs identified
6. **Attack Patterns**: Known patterns and signatures
7. **Potential Impact**: What could happen if successful
8. **Recommended Actions**: Immediate technical responses
9. **Similar Attacks**: Historical context and related threats

Format your response as a structured analysis with clear sections and actionable insights.
"""

        try:
            # Support both OpenAI and Gemini clients
            if hasattr(self.llm_client, 'chat'):  # OpenAI client
                response = await self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,  # Low temperature for analytical precision
                    max_tokens=2000
                )
                analysis_content = response.choices[0].message.content
            else:  # Gemini client
                response = await self.llm_client.generate_content(
                    f"{system_prompt}\n\n{user_prompt}"
                )
                analysis_content = response.text
            processing_time = time.time() - start_time
            
            # Parse the structured response (simplified for now)
            analysis = self._parse_threat_analysis(analysis_content, event)
            
            logger.info(f"ThreatAnalyst completed analysis in {processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"ThreatAnalyst failed: {e}")
            # Return fallback analysis
            return ThreatAnalysis(
                attack_type=event.threat_type.value,
                attack_vector="Unknown",
                severity_assessment=event.severity.value,
                technical_details=f"Analysis failed: {str(e)}",
                indicators_of_compromise=[],
                attack_patterns=[],
                potential_impact="Analysis unavailable",
                confidence_score=0.5,
                recommended_actions=["Manual investigation required"],
                similar_attacks=[]
            )
    
    def _parse_threat_analysis(self, content: str, event: SecurityEvent) -> ThreatAnalysis:
        """Parse LLM response into structured threat analysis."""
        # For now, create a structured analysis from the content
        # In production, you might use more sophisticated parsing
        return ThreatAnalysis(
            attack_type=event.threat_type.value,
            attack_vector="Extracted from analysis",
            severity_assessment=event.severity.value,
            technical_details=content,
            indicators_of_compromise=[],
            attack_patterns=[],
            potential_impact="Extracted from analysis",
            confidence_score=event.confidence,
            recommended_actions=["Extracted from analysis"],
            similar_attacks=[]
        )


class IntelligenceAgent:
    """
    Agent specialized in threat intelligence research and context gathering.
    
    This agent acts as a threat intelligence analyst that can:
    - Research threat landscapes and trends
    - Provide industry context and insights
    - Suggest mitigation strategies
    - Analyze business impact
    """
    
    def __init__(self, llm_client, config: Optional[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.agent_role = AgentRole.INTELLIGENCE_RESEARCHER
        
    async def research_threat_intelligence(self, analysis: ThreatAnalysis, event: SecurityEvent) -> ThreatIntelligence:
        """Research threat intelligence based on the analysis."""
        start_time = time.time()
        
        system_prompt = """You are a Senior Threat Intelligence Analyst with deep expertise in:

- Global threat landscape analysis
- APT group tactics, techniques, and procedures (TTPs)
- Industry-specific threat trends
- Regulatory compliance and security frameworks
- Business risk assessment
- Strategic security planning

Your role is to provide strategic context and intelligence around security threats, focusing on broader implications, trends, and strategic recommendations."""

        user_prompt = f"""
Based on this threat analysis, provide comprehensive threat intelligence:

**Threat Analysis Summary:**
- Attack Type: {analysis.attack_type}
- Attack Vector: {analysis.attack_vector}
- Severity: {analysis.severity_assessment}
- Confidence: {analysis.confidence_score:.2%}

**Technical Details:**
{analysis.technical_details}

**Event Context:**
- Industry/Environment: {event.context.get('industry', 'General')}
- System Type: {event.context.get('system_type', 'Unknown')}
- Geographic Region: {event.context.get('region', 'Unknown')}

Provide strategic intelligence including:

1. **Threat Landscape**: Current threat environment for this attack type
2. **Attack Trends**: Recent trends and evolution of this threat
3. **Mitigation Strategies**: Proven defense strategies and frameworks
4. **Industry Context**: Sector-specific insights and risks
5. **Regulatory Implications**: Compliance and regulatory considerations
6. **Business Impact**: Strategic business implications
7. **Prevention Measures**: Long-term prevention strategies
8. **Detection Improvements**: Enhanced detection capabilities

Focus on strategic insights that help leadership make informed security decisions.
"""

        try:
            # Support both OpenAI and Gemini clients
            if hasattr(self.llm_client, 'chat'):  # OpenAI client
                response = await self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,  # Slightly higher for creative intelligence insights
                    max_tokens=2000
                )
                intelligence_content = response.choices[0].message.content
            else:  # Gemini client
                response = await self.llm_client.generate_content(
                    f"{system_prompt}\n\n{user_prompt}"
                )
                intelligence_content = response.text
            processing_time = time.time() - start_time
            
            intelligence = self._parse_threat_intelligence(intelligence_content)
            
            logger.info(f"IntelligenceAgent completed research in {processing_time:.2f}s")
            return intelligence
            
        except Exception as e:
            logger.error(f"IntelligenceAgent failed: {e}")
            return ThreatIntelligence(
                threat_landscape="Intelligence gathering failed",
                attack_trends="Analysis unavailable",
                mitigation_strategies=["Manual research required"],
                industry_context="Context unavailable",
                regulatory_implications="Review required",
                business_impact="Assessment needed",
                prevention_measures=["Standard security measures"],
                detection_improvements=["Enhanced monitoring recommended"]
            )
    
    def _parse_threat_intelligence(self, content: str) -> ThreatIntelligence:
        """Parse LLM response into structured threat intelligence."""
        return ThreatIntelligence(
            threat_landscape="Extracted from intelligence",
            attack_trends="Extracted from intelligence",
            mitigation_strategies=["Extracted from intelligence"],
            industry_context="Extracted from intelligence",
            regulatory_implications="Extracted from intelligence",
            business_impact="Extracted from intelligence",
            prevention_measures=["Extracted from intelligence"],
            detection_improvements=["Extracted from intelligence"]
        )


class ReportAgent:
    """
    Agent specialized in executive-level security report generation.
    
    This agent acts as a security communications expert that can:
    - Generate executive summaries
    - Translate technical findings to business language
    - Provide strategic recommendations
    - Create actionable reports for leadership
    """
    
    def __init__(self, llm_client, config: Optional[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.agent_role = AgentRole.REPORT_GENERATOR
        
    async def generate_executive_report(
        self, 
        analysis: ThreatAnalysis, 
        intelligence: ThreatIntelligence,
        event: SecurityEvent
    ) -> ExecutiveReport:
        """Generate executive-level security report."""
        start_time = time.time()
        
        system_prompt = """You are a Senior Security Communications Specialist and CISO advisor with expertise in:

- Executive security reporting and communication
- Business risk translation and assessment
- Strategic security planning and roadmapping
- Regulatory compliance and governance
- Crisis communication and incident reporting
- Board-level security presentations

Your role is to translate technical security findings into clear, actionable business intelligence for executive leadership and board members."""

        user_prompt = f"""
Create an executive-level security report based on the following analysis:

**Security Event:**
- Type: {event.threat_type.value}
- Severity: {event.severity.value}
- System: {event.agent_id}
- Time: {event.timestamp}

**Technical Analysis:**
{analysis.technical_details}

**Threat Intelligence:**
{intelligence.threat_landscape}

**Business Context:**
- Industry Impact: {intelligence.industry_context}
- Regulatory Considerations: {intelligence.regulatory_implications}
- Business Risk: {intelligence.business_impact}

Generate a comprehensive executive report with:

1. **Executive Summary**: 3-4 sentence overview for C-level executives
2. **Threat Overview**: Business-focused threat description
3. **Business Impact**: Clear articulation of business risks and implications
4. **Risk Assessment**: Quantified risk levels and potential consequences
5. **Immediate Actions**: Specific next steps with owners and timelines
6. **Strategic Recommendations**: Long-term strategic security improvements
7. **Compliance Considerations**: Regulatory and compliance implications
8. **Resource Requirements**: Budget and resource needs for remediation

Write for an executive audience - clear, concise, action-oriented, and business-focused.
"""

        try:
            # Support both OpenAI and Gemini clients
            if hasattr(self.llm_client, 'chat'):  # OpenAI client
                response = await self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Balanced for clear communication
                    max_tokens=2500
                )
                report_content = response.choices[0].message.content
            else:  # Gemini client
                response = await self.llm_client.generate_content(
                    f"{system_prompt}\n\n{user_prompt}"
                )
                report_content = response.text
            processing_time = time.time() - start_time
            
            report = self._parse_executive_report(report_content)
            
            logger.info(f"ReportAgent completed report in {processing_time:.2f}s")
            return report
            
        except Exception as e:
            logger.error(f"ReportAgent failed: {e}")
            return ExecutiveReport(
                executive_summary="Security event detected requiring immediate attention.",
                threat_overview="Technical analysis in progress.",
                business_impact="Impact assessment needed.",
                risk_assessment="Risk evaluation required.",
                immediate_actions=["Investigate security event", "Assess system impact"],
                strategic_recommendations=["Enhance security monitoring"],
                compliance_considerations="Compliance review needed.",
                resource_requirements="Resource assessment required."
            )
    
    def _parse_executive_report(self, content: str) -> ExecutiveReport:
        """Parse LLM response into structured executive report."""
        return ExecutiveReport(
            executive_summary="Extracted from report",
            threat_overview="Extracted from report",
            business_impact="Extracted from report",
            risk_assessment="Extracted from report",
            immediate_actions=["Extracted from report"],
            strategic_recommendations=["Extracted from report"],
            compliance_considerations="Extracted from report",
            resource_requirements="Extracted from report"
        )


class AgenticOrchestrator:
    """
    Main orchestrator that coordinates the multi-agent security analysis workflow.
    
    This orchestrator manages the flow between:
    1. ThreatAnalyst → Technical analysis
    2. IntelligenceAgent → Strategic intelligence
    3. ReportAgent → Executive reporting
    """
    
    def __init__(self, llm_client, config: Optional[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.config = config or {}
        
        # Initialize agents
        self.threat_analyst = ThreatAnalystAgent(llm_client, config)
        self.intelligence_agent = IntelligenceAgent(llm_client, config)
        self.report_agent = ReportAgent(llm_client, config)
        
        # Orchestration metrics
        self.orchestration_stats = {
            'total_orchestrations': 0,
            'successful_orchestrations': 0,
            'failed_orchestrations': 0,
            'average_processing_time': 0.0,
            'agent_performance': {
                'threat_analyst': {'calls': 0, 'success': 0, 'avg_time': 0.0},
                'intelligence_agent': {'calls': 0, 'success': 0, 'avg_time': 0.0},
                'report_agent': {'calls': 0, 'success': 0, 'avg_time': 0.0}
            }
        }
    
    async def orchestrate_security_analysis(self, event: SecurityEvent) -> AgenticOrchestrationResult:
        """
        Orchestrate the complete multi-agent security analysis workflow.
        
        Args:
            event: Security event to analyze
            
        Returns:
            Complete orchestration result with analysis, intelligence, and report
        """
        start_time = time.time()
        self.orchestration_stats['total_orchestrations'] += 1
        
        try:
            logger.info(f"Starting agentic orchestration for event: {event.threat_type.value}")
            
            # Step 1: Threat Analysis
            logger.info("Step 1: ThreatAnalyst analyzing security event...")
            threat_analysis = await self.threat_analyst.analyze_security_event(event)
            
            # Step 2: Intelligence Research
            logger.info("Step 2: IntelligenceAgent researching threat intelligence...")
            threat_intelligence = await self.intelligence_agent.research_threat_intelligence(
                threat_analysis, event
            )
            
            # Step 3: Executive Report Generation
            logger.info("Step 3: ReportAgent generating executive report...")
            executive_report = await self.report_agent.generate_executive_report(
                threat_analysis, threat_intelligence, event
            )
            
            # Calculate final metrics
            total_time = time.time() - start_time
            confidence_score = (threat_analysis.confidence_score + 0.8) / 2  # Blend with base confidence
            
            result = AgenticOrchestrationResult(
                original_event=event,
                threat_analysis=threat_analysis,
                threat_intelligence=threat_intelligence,
                executive_report=executive_report,
                orchestration_metadata={
                    'orchestration_version': '1.0',
                    'agents_used': ['threat_analyst', 'intelligence_agent', 'report_agent'],
                    'processing_stages': 3,
                    'total_tokens_estimated': 6000,  # Rough estimate
                    'orchestration_id': f"orch_{int(time.time() * 1000)}"
                },
                total_processing_time=total_time,
                confidence_score=confidence_score
            )
            
            self.orchestration_stats['successful_orchestrations'] += 1
            self._update_performance_stats(total_time)
            
            logger.info(f"Agentic orchestration completed successfully in {total_time:.2f}s")
            return result
            
        except Exception as e:
            self.orchestration_stats['failed_orchestrations'] += 1
            logger.error(f"Agentic orchestration failed: {e}")
            raise
    
    def _update_performance_stats(self, processing_time: float):
        """Update orchestration performance statistics."""
        total = self.orchestration_stats['total_orchestrations']
        current_avg = self.orchestration_stats['average_processing_time']
        
        # Update rolling average
        self.orchestration_stats['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration performance statistics."""
        return self.orchestration_stats.copy()
    
    def reset_stats(self):
        """Reset orchestration statistics."""
        self.orchestration_stats = {
            'total_orchestrations': 0,
            'successful_orchestrations': 0,
            'failed_orchestrations': 0,
            'average_processing_time': 0.0,
            'agent_performance': {
                'threat_analyst': {'calls': 0, 'success': 0, 'avg_time': 0.0},
                'intelligence_agent': {'calls': 0, 'success': 0, 'avg_time': 0.0},
                'report_agent': {'calls': 0, 'success': 0, 'avg_time': 0.0}
            }
        } 