"""
Threat Intelligence Data Types

Structured data classes for organizing and storing threat intelligence information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ThreatSeverity(Enum):
    """Standardized threat severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IntelligenceSource(Enum):
    """Sources of threat intelligence"""
    CVE_DATABASE = "CVE_DATABASE"
    THREAT_FEEDS = "THREAT_FEEDS"
    SECURITY_RESEARCH = "SECURITY_RESEARCH"
    INCIDENT_REPORTS = "INCIDENT_REPORTS"
    APT_TRACKING = "APT_TRACKING"


@dataclass
class CVEIntelligence:
    """CVE vulnerability intelligence"""
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    severity: Optional[ThreatSeverity] = None
    description: Optional[str] = None
    affected_products: List[str] = field(default_factory=list)
    published_date: Optional[datetime] = None
    references: List[str] = field(default_factory=list)
    exploitation_likelihood: Optional[str] = None


@dataclass
class AttackPatternIntelligence:
    """Attack pattern and technique intelligence"""
    technique_id: Optional[str] = None
    technique_name: Optional[str] = None
    tactic: Optional[str] = None
    description: Optional[str] = None
    detection_methods: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    recent_usage: Optional[str] = None
    complexity_level: Optional[str] = None


@dataclass
class MitigationIntelligence:
    """Mitigation and remediation intelligence"""
    primary_mitigation: Optional[str] = None
    secondary_mitigations: List[str] = field(default_factory=list)
    implementation_difficulty: Optional[str] = None
    effectiveness_rating: Optional[str] = None
    cost_impact: Optional[str] = None
    recommended_tools: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)


@dataclass
class AttributionIntelligence:
    """Threat actor attribution intelligence"""
    actor_groups: List[str] = field(default_factory=list)
    campaign_names: List[str] = field(default_factory=list)
    target_sectors: List[str] = field(default_factory=list)
    geographic_focus: List[str] = field(default_factory=list)
    motivation: Optional[str] = None
    sophistication_level: Optional[str] = None
    recent_activity: Optional[str] = None


@dataclass
class TrendIntelligence:
    """Threat trend and landscape intelligence"""
    trend_description: Optional[str] = None
    frequency_change: Optional[str] = None
    seasonal_patterns: Optional[str] = None
    emerging_variants: List[str] = field(default_factory=list)
    industry_impact: Optional[str] = None
    predicted_evolution: Optional[str] = None
    related_threats: List[str] = field(default_factory=list)


@dataclass
class ThreatIntelligence:
    """Comprehensive threat intelligence container"""
    threat_type: str
    confidence_score: float
    last_updated: datetime
    source: IntelligenceSource
    
    # Intelligence components
    cve_intelligence: Optional[CVEIntelligence] = None
    attack_pattern_intelligence: Optional[AttackPatternIntelligence] = None
    mitigation_intelligence: Optional[MitigationIntelligence] = None
    attribution_intelligence: Optional[AttributionIntelligence] = None
    trend_intelligence: Optional[TrendIntelligence] = None
    
    # Raw data and metadata
    raw_data: Dict[str, Any] = field(default_factory=dict)
    search_queries: List[str] = field(default_factory=list)
    processing_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert intelligence to dictionary format"""
        return {
            'threat_type': self.threat_type,
            'confidence_score': self.confidence_score,
            'last_updated': self.last_updated.isoformat(),
            'source': self.source.value,
            'cve_intelligence': self.cve_intelligence.__dict__ if self.cve_intelligence else None,
            'attack_pattern_intelligence': self.attack_pattern_intelligence.__dict__ if self.attack_pattern_intelligence else None,
            'mitigation_intelligence': self.mitigation_intelligence.__dict__ if self.mitigation_intelligence else None,
            'attribution_intelligence': self.attribution_intelligence.__dict__ if self.attribution_intelligence else None,
            'trend_intelligence': self.trend_intelligence.__dict__ if self.trend_intelligence else None,
            'raw_data': self.raw_data,
            'search_queries': self.search_queries,
            'processing_notes': self.processing_notes
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the intelligence"""
        summary_parts = []
        
        if self.cve_intelligence and self.cve_intelligence.cve_id:
            summary_parts.append(f"CVE: {self.cve_intelligence.cve_id}")
        
        if self.attack_pattern_intelligence and self.attack_pattern_intelligence.technique_name:
            summary_parts.append(f"Technique: {self.attack_pattern_intelligence.technique_name}")
        
        if self.attribution_intelligence and self.attribution_intelligence.actor_groups:
            summary_parts.append(f"Attribution: {', '.join(self.attribution_intelligence.actor_groups[:2])}")
        
        if self.trend_intelligence and self.trend_intelligence.trend_description:
            summary_parts.append(f"Trend: {self.trend_intelligence.trend_description}")
        
        return " | ".join(summary_parts) if summary_parts else f"Threat Intelligence for {self.threat_type}" 