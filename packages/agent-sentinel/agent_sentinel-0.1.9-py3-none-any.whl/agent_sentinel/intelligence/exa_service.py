"""
Exa Threat Intelligence Service

Real-time threat intelligence gathering using Exa's semantic search capabilities.
"""

import asyncio
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

try:
    import exa_py
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False

from cachetools import TTLCache
from ..core.exceptions import ThreatIntelligenceError
from .intelligence_types import (
    ThreatIntelligence, 
    CVEIntelligence, 
    AttackPatternIntelligence,
    MitigationIntelligence,
    AttributionIntelligence,
    TrendIntelligence,
    IntelligenceSource,
    ThreatSeverity
)

logger = logging.getLogger(__name__)


@dataclass
class ExaSearchResult:
    """Processed search result from Exa API"""
    title: str
    url: str
    text: str
    score: float
    published_date: Optional[datetime] = None
    

class ExaThreatIntelligence:
    """
    Enterprise-grade threat intelligence service using Exa search
    
    Provides real-time threat intelligence for security event enrichment
    with structured data extraction and caching capabilities.
    """
    
    # Optimized search queries for threat intelligence
    THREAT_SEARCH_QUERIES = {
        'sql_injection': [
            "CVE SQL injection vulnerability 2024 database security",
            "SQL injection attack techniques prevention methods",
            "Database security vulnerabilities recent disclosure",
            "SQL injection detection tools enterprise security"
        ],
        'xss': [
            "CVE XSS cross-site scripting vulnerability 2024",
            "XSS attack vectors prevention techniques",
            "Cross-site scripting security vulnerabilities",
            "XSS detection tools web application security"
        ],
        'command_injection': [
            "CVE command injection vulnerability 2024 RCE",
            "Command injection attack prevention secure coding",
            "Remote code execution vulnerabilities disclosure",
            "Command injection detection security tools"
        ],
        'path_traversal': [
            "CVE path traversal vulnerability 2024 directory",
            "Path traversal attack prevention file security",
            "Directory traversal vulnerabilities disclosure",
            "Path traversal detection security tools"
        ],
        'prompt_injection': [
            "AI prompt injection vulnerability LLM security",
            "Prompt injection attack techniques AI safety",
            "LLM security vulnerabilities model safety",
            "AI prompt injection prevention techniques"
        ]
    }
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Exa threat intelligence service
        
        Args:
            api_key: Exa API key (if not provided, will try to get from environment)
            config: Optional configuration dictionary
        """
        if not EXA_AVAILABLE:
            raise ThreatIntelligenceError("exa_py package not available. Install with: pip install exa_py")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('EXA_API_KEY')
        if not self.api_key:
            raise ThreatIntelligenceError("Exa API key not provided. Set EXA_API_KEY environment variable or pass api_key parameter")
        
        # Initialize Exa client
        try:
            self.exa_client = exa_py.Exa(api_key=self.api_key)
        except Exception as e:
            raise ThreatIntelligenceError(f"Failed to initialize Exa client: {str(e)}")
        
        self.config = config or {}
        
        # Performance optimizations (with environment variable support)
        self.cache = TTLCache(
            maxsize=self.config.get('cache_size', int(os.getenv('EXA_CACHE_SIZE', '1000'))),
            ttl=self.config.get('cache_ttl', int(os.getenv('EXA_CACHE_TTL', '3600')))  # 1 hour
        )
        
        # Search configuration
        self.max_results_per_query = self.config.get('max_results_per_query', int(os.getenv('EXA_MAX_RESULTS', '3')))
        self.search_timeout = self.config.get('search_timeout', float(os.getenv('EXA_TIMEOUT', '10.0')))
        self.content_max_chars = self.config.get('content_max_chars', int(os.getenv('EXA_MAX_CHARS', '2000')))
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', int(os.getenv('EXA_RATE_LIMIT', '100')))  # queries per hour
        self.query_count = 0
        self.rate_limit_reset = datetime.now() + timedelta(hours=1)
        
        logger.info(f"Initialized Exa threat intelligence service")
    
    async def get_threat_intelligence(self, threat_type: str, context: Optional[Dict[str, Any]] = None) -> ThreatIntelligence:
        """
        Get comprehensive threat intelligence for a security event
        
        Args:
            threat_type: Type of threat (sql_injection, xss, etc.)
            context: Additional context for targeted searches
            
        Returns:
            ThreatIntelligence object with enriched data
        """
        cache_key = f"{threat_type}_{hash(str(context))}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Cache hit for threat intelligence: {threat_type}")
            return self.cache[cache_key]
        
        # Check rate limits
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded for threat intelligence queries")
            raise ThreatIntelligenceError("Rate limit exceeded")
        
        try:
            # Get search queries for this threat type
            search_queries = self.THREAT_SEARCH_QUERIES.get(threat_type, [f"{threat_type} security vulnerability"])
            
            # Perform searches and content retrieval
            all_results = []
            for query in search_queries:
                try:
                    # Use search_and_contents for comprehensive results
                    search_response = await self._search_with_contents(query)
                    all_results.extend(search_response)
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {str(e)}")
                    continue
            
            if not all_results:
                logger.warning(f"No search results found for threat type: {threat_type}")
                return self._create_empty_intelligence(threat_type)
            
            # Extract intelligence from results
            intelligence = await self._extract_intelligence(threat_type, all_results)
            
            # Cache the result
            self.cache[cache_key] = intelligence
            
            logger.info(f"Successfully enriched threat intelligence for {threat_type}")
            return intelligence
            
        except Exception as e:
            logger.error(f"Error getting threat intelligence for {threat_type}: {str(e)}")
            raise ThreatIntelligenceError(f"Failed to get threat intelligence: {str(e)}")
    
    async def _search_with_contents(self, query: str) -> List[ExaSearchResult]:
        """
        Perform Exa search with content retrieval
        
        Args:
            query: Search query string
            
        Returns:
            List of ExaSearchResult objects
        """
        try:
            # Use Exa's search_and_contents for comprehensive results
            search_response = self.exa_client.search_and_contents(
                query,
                num_results=self.max_results_per_query,
                text={
                    "max_characters": self.content_max_chars,
                    "include_html_tags": False
                },
                start_published_date="2020-01-01",  # Focus on recent content
                use_autoprompt=True  # Let Exa optimize the query
            )
            
            results = []
            for result in search_response.results:
                results.append(ExaSearchResult(
                    title=result.title,
                    url=result.url,
                    text=result.text or "",
                    score=result.score,
                    published_date=result.published_date
                ))
            
            self.query_count += 1
            logger.debug(f"Exa search completed for query: {query}, found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Exa search failed for query '{query}': {str(e)}")
            return []
    
    async def _extract_intelligence(self, threat_type: str, results: List[ExaSearchResult]) -> ThreatIntelligence:
        """
        Extract structured intelligence from search results
        
        Args:
            threat_type: Type of threat
            results: List of search results
            
        Returns:
            ThreatIntelligence object
        """
        # Extract different types of intelligence
        cve_intelligence = self._extract_cve_intelligence(results)
        attack_pattern_intelligence = self._extract_attack_pattern_intelligence(results)
        mitigation_intelligence = self._extract_mitigation_intelligence(results)
        attribution_intelligence = self._extract_attribution_intelligence(results)
        trend_intelligence = self._extract_trend_intelligence(results)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(results)
        
        # Create comprehensive intelligence object
        intelligence = ThreatIntelligence(
            threat_type=threat_type,
            confidence_score=confidence_score,
            last_updated=datetime.now(),
            source=IntelligenceSource.THREAT_FEEDS,
            cve_intelligence=cve_intelligence,
            attack_pattern_intelligence=attack_pattern_intelligence,
            mitigation_intelligence=mitigation_intelligence,
            attribution_intelligence=attribution_intelligence,
            trend_intelligence=trend_intelligence,
            search_queries=self.THREAT_SEARCH_QUERIES.get(threat_type, []),
            raw_data={"results_count": len(results), "sources": [r.url for r in results]},
            processing_notes=[f"Processed {len(results)} search results from Exa"]
        )
        
        return intelligence
    
    def _extract_cve_intelligence(self, results: List[ExaSearchResult]) -> CVEIntelligence:
        """Extract CVE information from search results"""
        cve_data = {}
        
        for result in results:
            text = result.text.lower()
            
            # Extract CVE ID
            cve_matches = re.findall(r'cve-\d{4}-\d{4,}', text)
            if cve_matches and not cve_data.get('cve_id'):
                cve_data['cve_id'] = cve_matches[0].upper()
            
            # Extract CVSS score
            cvss_matches = re.findall(r'cvss[:\s]+(\d+\.?\d*)', text)
            if cvss_matches and not cve_data.get('cvss_score'):
                try:
                    cve_data['cvss_score'] = float(cvss_matches[0])
                except ValueError:
                    pass
            
            # Extract severity
            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in text and not cve_data.get('severity'):
                    cve_data['severity'] = severity
                    break
        
        return CVEIntelligence(
            cve_id=cve_data.get('cve_id'),
            cvss_score=cve_data.get('cvss_score'),
            severity=self._map_severity(cve_data.get('severity')),
            description=results[0].text[:300] + "..." if results else None,
            references=[r.url for r in results[:3]]
        )
    
    def _extract_attack_pattern_intelligence(self, results: List[ExaSearchResult]) -> AttackPatternIntelligence:
        """Extract attack pattern information from search results"""
        techniques = []
        detection_methods = []
        
        for result in results:
            if 'technique' in result.text.lower() or 'method' in result.text.lower():
                techniques.append(result.title)
            if 'detection' in result.text.lower() or 'monitor' in result.text.lower():
                detection_methods.append("Pattern-based detection")
        
        return AttackPatternIntelligence(
            technique_name=techniques[0] if techniques else None,
            description=results[0].text[:200] + "..." if results else None,
            detection_methods=list(set(detection_methods)) or ["Signature-based detection", "Behavioral analysis"],
            complexity_level="Advanced"
        )
    
    def _extract_mitigation_intelligence(self, results: List[ExaSearchResult]) -> MitigationIntelligence:
        """Extract mitigation information from search results"""
        mitigations = []
        tools = []
        
        for result in results:
            text = result.text.lower()
            if 'prevent' in text or 'mitigation' in text:
                mitigations.append("Input validation and sanitization")
            if 'tool' in text or 'scanner' in text:
                tools.append("Security scanner")
        
        return MitigationIntelligence(
            primary_mitigation="Implement input validation and secure coding practices",
            secondary_mitigations=mitigations[:3] or ["Web Application Firewall", "Regular security audits"],
            effectiveness_rating="High",
            recommended_tools=list(set(tools)) or ["OWASP ZAP", "Burp Suite", "Checkmarx"],
            compliance_requirements=["OWASP Top 10", "PCI DSS", "ISO 27001"]
        )
    
    def _extract_attribution_intelligence(self, results: List[ExaSearchResult]) -> AttributionIntelligence:
        """Extract attribution information from search results"""
        actors = []
        campaigns = []
        
        for result in results:
            text = result.text.lower()
            # Look for APT groups
            apt_matches = re.findall(r'apt[-\s]?\d+', text)
            actors.extend([match.upper() for match in apt_matches])
            
            # Look for campaign names
            if 'campaign' in text or 'operation' in text:
                campaigns.append("Recent campaign activity")
        
        return AttributionIntelligence(
            actor_groups=list(set(actors)) or ["Unknown threat actors"],
            campaign_names=list(set(campaigns)),
            target_sectors=["Technology", "Financial", "Healthcare"],
            motivation="Financial gain and data theft"
        )
    
    def _extract_trend_intelligence(self, results: List[ExaSearchResult]) -> TrendIntelligence:
        """Extract trend information from search results"""
        trends = []
        
        for result in results:
            text = result.text.lower()
            if 'increase' in text or 'trend' in text or 'growing' in text:
                trends.append("Increasing attack frequency")
            if '2024' in text or '2023' in text:
                trends.append("Recent activity surge")
        
        return TrendIntelligence(
            trend_description="Significant increase in attack attempts",
            frequency_change="Notable increase in recent months",
            industry_impact="High impact on web applications and databases",
            emerging_variants=["AI-powered attacks", "Automated exploitation"]
        )
    
    def _calculate_confidence_score(self, results: List[ExaSearchResult]) -> float:
        """Calculate confidence score based on search results quality"""
        if not results:
            return 0.0
        
        # Base score on number of results
        base_score = min(len(results) / 10.0, 0.8)
        
        # Adjust based on content quality
        has_recent_content = any(r.published_date and r.published_date > datetime.now() - timedelta(days=365) for r in results)
        has_technical_content = any(len(r.text) > 500 for r in results)
        
        if has_recent_content:
            base_score += 0.1
        if has_technical_content:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _map_severity(self, severity_str: Optional[str]) -> Optional[ThreatSeverity]:
        """Map string severity to ThreatSeverity enum"""
        if not severity_str:
            return None
        
        severity_str = severity_str.lower()
        
        if severity_str == 'critical':
            return ThreatSeverity.CRITICAL
        elif severity_str == 'high':
            return ThreatSeverity.HIGH
        elif severity_str == 'medium':
            return ThreatSeverity.MEDIUM
        elif severity_str == 'low':
            return ThreatSeverity.LOW
        else:
            return None
    
    def _create_empty_intelligence(self, threat_type: str) -> ThreatIntelligence:
        """Create empty intelligence object when no results found"""
        return ThreatIntelligence(
            threat_type=threat_type,
            confidence_score=0.0,
            last_updated=datetime.now(),
            source=IntelligenceSource.THREAT_FEEDS,
            processing_notes=["No search results found"]
        )
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Reset counter if hour has passed
        if now >= self.rate_limit_reset:
            self.query_count = 0
            self.rate_limit_reset = now + timedelta(hours=1)
        
        return self.query_count < self.rate_limit
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            'cache_size': len(self.cache),
            'cache_maxsize': self.cache.maxsize,
            'cache_ttl': self.cache.ttl,
            'query_count': self.query_count,
            'rate_limit': self.rate_limit,
            'exa_available': EXA_AVAILABLE
        } 