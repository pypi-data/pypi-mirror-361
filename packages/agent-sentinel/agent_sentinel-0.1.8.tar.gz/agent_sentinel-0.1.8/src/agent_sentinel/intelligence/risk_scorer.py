"""
Advanced Risk Scoring System for Agent Sentinel

This module implements a sophisticated risk scoring system that provides
comprehensive threat assessment and prioritization for AI agents.

Enterprise-grade features:
- Multi-dimensional risk assessment
- Dynamic risk scoring based on context and behavior
- Threat prioritization and escalation
- Risk trend analysis and prediction
- Compliance and regulatory risk assessment
- Cross-agent risk correlation
- Real-time risk monitoring and alerting
"""

import asyncio
import json
import statistics
import time
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import math
import logging
from pathlib import Path
import hashlib

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..core.exceptions import AgentSentinelError
from ..logging.structured_logger import SecurityLogger


class RiskCategory(Enum):
    """Categories of risk assessment."""
    SECURITY_RISK = "security_risk"
    OPERATIONAL_RISK = "operational_risk"
    COMPLIANCE_RISK = "compliance_risk"
    REPUTATIONAL_RISK = "reputational_risk"
    FINANCIAL_RISK = "financial_risk"
    PRIVACY_RISK = "privacy_risk"
    AVAILABILITY_RISK = "availability_risk"
    INTEGRITY_RISK = "integrity_risk"


class RiskLevel(Enum):
    """Risk levels for threat assessment."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"


class RiskFactor(Enum):
    """Factors that contribute to risk scoring."""
    THREAT_SEVERITY = "threat_severity"
    THREAT_CONFIDENCE = "threat_confidence"
    ASSET_VALUE = "asset_value"
    VULNERABILITY_SCORE = "vulnerability_score"
    EXPOSURE_LEVEL = "exposure_level"
    ATTACK_VECTOR = "attack_vector"
    IMPACT_SCOPE = "impact_scope"
    TEMPORAL_FACTORS = "temporal_factors"
    ENVIRONMENTAL_FACTORS = "environmental_factors"
    BEHAVIORAL_FACTORS = "behavioral_factors"


@dataclass
class RiskContext:
    """Context for risk assessment."""
    agent_id: str
    threat_type: ThreatType
    severity: SeverityLevel
    confidence: float
    timestamp: datetime
    
    # Asset and environment context
    asset_value: float = 0.5  # 0.0 to 1.0
    environment: str = "unknown"
    criticality: float = 0.5  # 0.0 to 1.0
    
    # Threat context
    attack_vector: str = "unknown"
    impact_scope: str = "local"
    exploit_complexity: float = 0.5  # 0.0 to 1.0
    
    # Behavioral context
    user_behavior: Dict[str, Any] = field(default_factory=dict)
    agent_behavior: Dict[str, Any] = field(default_factory=dict)
    session_context: Dict[str, Any] = field(default_factory=dict)
    
    # Historical context
    historical_events: List[SecurityEvent] = field(default_factory=list)
    trend_data: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance context
    compliance_requirements: List[str] = field(default_factory=list)
    regulatory_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk context to dictionary."""
        return {
            "agent_id": self.agent_id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "asset_value": self.asset_value,
            "environment": self.environment,
            "criticality": self.criticality,
            "attack_vector": self.attack_vector,
            "impact_scope": self.impact_scope,
            "exploit_complexity": self.exploit_complexity,
            "user_behavior": self.user_behavior,
            "agent_behavior": self.agent_behavior,
            "session_context": self.session_context,
            "historical_events": len(self.historical_events),
            "trend_data": self.trend_data,
            "compliance_requirements": self.compliance_requirements,
            "regulatory_context": self.regulatory_context
        }


@dataclass
class RiskScore:
    """Comprehensive risk score result."""
    overall_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    category_scores: Dict[RiskCategory, float]
    factor_scores: Dict[RiskFactor, float]
    
    # Detailed assessment
    threat_assessment: Dict[str, Any]
    impact_assessment: Dict[str, Any]
    likelihood_assessment: Dict[str, Any]
    
    # Temporal factors
    urgency_score: float
    trend_score: float
    escalation_score: float
    
    # Recommendations
    risk_mitigation: List[str]
    priority_actions: List[str]
    monitoring_recommendations: List[str]
    
    # Metadata
    calculation_timestamp: datetime
    model_version: str
    confidence_interval: Tuple[float, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk score to dictionary."""
        return {
            "overall_score": self.overall_score,
            "risk_level": self.risk_level.value,
            "category_scores": {cat.value: score for cat, score in self.category_scores.items()},
            "factor_scores": {factor.value: score for factor, score in self.factor_scores.items()},
            "threat_assessment": self.threat_assessment,
            "impact_assessment": self.impact_assessment,
            "likelihood_assessment": self.likelihood_assessment,
            "urgency_score": self.urgency_score,
            "trend_score": self.trend_score,
            "escalation_score": self.escalation_score,
            "risk_mitigation": self.risk_mitigation,
            "priority_actions": self.priority_actions,
            "monitoring_recommendations": self.monitoring_recommendations,
            "calculation_timestamp": self.calculation_timestamp.isoformat(),
            "model_version": self.model_version,
            "confidence_interval": self.confidence_interval
        }


@dataclass
class RiskTrend:
    """Risk trend analysis result."""
    agent_id: str
    time_period: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_magnitude: float  # Rate of change
    
    # Historical data
    historical_scores: List[Tuple[datetime, float]]
    moving_averages: Dict[str, float]
    volatility_metrics: Dict[str, float]
    
    # Predictions
    predicted_score: float
    prediction_confidence: float
    risk_forecast: Dict[str, Any]
    
    # Anomalies
    anomalies_detected: List[Dict[str, Any]]
    pattern_changes: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk trend to dictionary."""
        return {
            "agent_id": self.agent_id,
            "time_period": self.time_period,
            "trend_direction": self.trend_direction,
            "trend_magnitude": self.trend_magnitude,
            "historical_scores": [
                (ts.isoformat(), score) for ts, score in self.historical_scores
            ],
            "moving_averages": self.moving_averages,
            "volatility_metrics": self.volatility_metrics,
            "predicted_score": self.predicted_score,
            "prediction_confidence": self.prediction_confidence,
            "risk_forecast": self.risk_forecast,
            "anomalies_detected": self.anomalies_detected,
            "pattern_changes": self.pattern_changes
        }


class RiskScoringEngine:
    """
    Advanced risk scoring engine for comprehensive threat assessment.
    
    This engine provides sophisticated risk scoring capabilities including:
    - Multi-dimensional risk assessment
    - Dynamic contextual scoring
    - Threat prioritization and escalation
    - Risk trend analysis and prediction
    - Compliance and regulatory risk assessment
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        config: Optional[Dict[str, Any]] = None,
        enable_ml_scoring: bool = True,
        enable_trend_analysis: bool = True
    ):
        """
        Initialize risk scoring engine.
        
        Args:
            agent_id: ID of the agent being assessed
            logger: Security logger instance
            config: Risk scoring configuration
            enable_ml_scoring: Enable ML-based risk scoring
            enable_trend_analysis: Enable trend analysis
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"risk_scorer_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        self.config = config or self._get_default_config()
        self.enable_ml_scoring = enable_ml_scoring
        self.enable_trend_analysis = enable_trend_analysis
        
        # Risk scoring models and weights
        self.risk_weights = self._load_risk_weights()
        self.threat_matrices = self._load_threat_matrices()
        self.compliance_frameworks = self._load_compliance_frameworks()
        
        # Historical data for trend analysis
        self.risk_history: deque = deque(maxlen=1000)
        self.trend_cache: Dict[str, RiskTrend] = {}
        
        # Risk scoring cache
        self.score_cache: Dict[str, RiskScore] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Performance metrics
        self.metrics = {
            "total_assessments": 0,
            "avg_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "trend_analyses": 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        self.logger.info(f"Risk scoring engine initialized for agent {agent_id}")
    
    async def calculate_risk_score(self, context: RiskContext) -> RiskScore:
        """
        Calculate comprehensive risk score for given context.
        
        Args:
            context: Risk assessment context
            
        Returns:
            Comprehensive risk score
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(context)
            cached_score = self._get_cached_score(cache_key)
            
            if cached_score:
                self._update_metrics(time.time() - start_time, cache_hit=True)
                return cached_score
            
            # Calculate risk score components
            category_scores = await self._calculate_category_scores(context)
            factor_scores = await self._calculate_factor_scores(context)
            
            # Calculate overall risk score
            overall_score = self._calculate_overall_score(category_scores, factor_scores)
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Perform detailed assessments
            threat_assessment = await self._assess_threat(context)
            impact_assessment = await self._assess_impact(context)
            likelihood_assessment = await self._assess_likelihood(context)
            
            # Calculate temporal factors
            urgency_score = self._calculate_urgency_score(context)
            trend_score = await self._calculate_trend_score(context)
            escalation_score = self._calculate_escalation_score(context)
            
            # Generate recommendations
            risk_mitigation = self._generate_risk_mitigation(context, overall_score)
            priority_actions = self._generate_priority_actions(context, overall_score)
            monitoring_recommendations = self._generate_monitoring_recommendations(context)
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(
                overall_score, factor_scores, context
            )
            
            # Create risk score result
            risk_score = RiskScore(
                overall_score=overall_score,
                risk_level=risk_level,
                category_scores=category_scores,
                factor_scores=factor_scores,
                threat_assessment=threat_assessment,
                impact_assessment=impact_assessment,
                likelihood_assessment=likelihood_assessment,
                urgency_score=urgency_score,
                trend_score=trend_score,
                escalation_score=escalation_score,
                risk_mitigation=risk_mitigation,
                priority_actions=priority_actions,
                monitoring_recommendations=monitoring_recommendations,
                calculation_timestamp=datetime.now(timezone.utc),
                model_version="2.0",
                confidence_interval=confidence_interval
            )
            
            # Cache the result
            self._cache_score(cache_key, risk_score)
            
            # Update historical data
            self._update_risk_history(context, risk_score)
            
            # Update metrics
            self._update_metrics(time.time() - start_time, cache_hit=False)
            
            self.logger.info(
                f"Risk score calculated: {overall_score:.3f} ({risk_level.value})",
                extra={
                    "agent_id": context.agent_id,
                    "threat_type": context.threat_type.value,
                    "overall_score": overall_score,
                    "risk_level": risk_level.value,
                    "processing_time": time.time() - start_time
                }
            )
            
            return risk_score
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {e}")
            raise AgentSentinelError(f"Risk score calculation failed: {e}")
    
    async def analyze_risk_trends(
        self,
        time_period: str = "24h",
        include_predictions: bool = True
    ) -> RiskTrend:
        """
        Analyze risk trends for the agent.
        
        Args:
            time_period: Time period for analysis
            include_predictions: Whether to include predictions
            
        Returns:
            Risk trend analysis
        """
        if not self.enable_trend_analysis:
            raise AgentSentinelError("Trend analysis is disabled")
        
        try:
            # Get historical data for the period
            historical_data = self._get_historical_data(time_period)
            
            if len(historical_data) < 2:
                return self._create_empty_trend(time_period)
            
            # Calculate trend metrics
            trend_direction = self._calculate_trend_direction(historical_data)
            trend_magnitude = self._calculate_trend_magnitude(historical_data)
            
            # Calculate moving averages
            moving_averages = self._calculate_moving_averages(historical_data)
            
            # Calculate volatility metrics
            volatility_metrics = self._calculate_volatility_metrics(historical_data)
            
            # Detect anomalies
            anomalies_detected = self._detect_risk_anomalies(historical_data)
            
            # Detect pattern changes
            pattern_changes = self._detect_pattern_changes(historical_data)
            
            # Generate predictions if enabled
            predicted_score = 0.0
            prediction_confidence = 0.0
            risk_forecast = {}
            
            if include_predictions:
                predicted_score = self._predict_future_risk(historical_data)
                prediction_confidence = self._calculate_prediction_confidence(historical_data)
                risk_forecast = self._generate_risk_forecast(historical_data)
            
            # Create trend result
            trend = RiskTrend(
                agent_id=self.agent_id,
                time_period=time_period,
                trend_direction=trend_direction,
                trend_magnitude=trend_magnitude,
                historical_scores=historical_data,
                moving_averages=moving_averages,
                volatility_metrics=volatility_metrics,
                predicted_score=predicted_score,
                prediction_confidence=prediction_confidence,
                risk_forecast=risk_forecast,
                anomalies_detected=anomalies_detected,
                pattern_changes=pattern_changes
            )
            
            # Cache trend analysis
            self.trend_cache[time_period] = trend
            
            self.logger.info(
                f"Risk trend analysis completed: {trend_direction} trend with magnitude {trend_magnitude:.3f}"
            )
            
            return trend
            
        except Exception as e:
            self.logger.error(f"Risk trend analysis failed: {e}")
            raise AgentSentinelError(f"Risk trend analysis failed: {e}")
    
    async def assess_compliance_risk(
        self,
        context: RiskContext,
        frameworks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess compliance risk for specific frameworks.
        
        Args:
            context: Risk assessment context
            frameworks: List of compliance frameworks to assess
            
        Returns:
            Compliance risk assessment
        """
        frameworks = frameworks or context.compliance_requirements
        
        if not frameworks:
            return {"status": "no_frameworks", "assessments": {}}
        
        compliance_assessments = {}
        
        for framework in frameworks:
            assessment = await self._assess_framework_compliance(context, framework)
            compliance_assessments[framework] = assessment
        
        # Calculate overall compliance risk
        overall_compliance_risk = self._calculate_overall_compliance_risk(compliance_assessments)
        
        return {
            "overall_compliance_risk": overall_compliance_risk,
            "assessments": compliance_assessments,
            "recommendations": self._generate_compliance_recommendations(compliance_assessments),
            "priority_actions": self._generate_compliance_actions(compliance_assessments)
        }
    
    async def _calculate_category_scores(self, context: RiskContext) -> Dict[RiskCategory, float]:
        """Calculate risk scores for each category."""
        category_scores = {}
        
        # Security Risk
        security_score = self._calculate_security_risk(context)
        category_scores[RiskCategory.SECURITY_RISK] = security_score
        
        # Operational Risk
        operational_score = self._calculate_operational_risk(context)
        category_scores[RiskCategory.OPERATIONAL_RISK] = operational_score
        
        # Compliance Risk
        compliance_score = self._calculate_compliance_risk(context)
        category_scores[RiskCategory.COMPLIANCE_RISK] = compliance_score
        
        # Reputational Risk
        reputational_score = self._calculate_reputational_risk(context)
        category_scores[RiskCategory.REPUTATIONAL_RISK] = reputational_score
        
        # Financial Risk
        financial_score = self._calculate_financial_risk(context)
        category_scores[RiskCategory.FINANCIAL_RISK] = financial_score
        
        # Privacy Risk
        privacy_score = self._calculate_privacy_risk(context)
        category_scores[RiskCategory.PRIVACY_RISK] = privacy_score
        
        # Availability Risk
        availability_score = self._calculate_availability_risk(context)
        category_scores[RiskCategory.AVAILABILITY_RISK] = availability_score
        
        # Integrity Risk
        integrity_score = self._calculate_integrity_risk(context)
        category_scores[RiskCategory.INTEGRITY_RISK] = integrity_score
        
        return category_scores
    
    async def _calculate_factor_scores(self, context: RiskContext) -> Dict[RiskFactor, float]:
        """Calculate risk scores for each factor."""
        factor_scores = {}
        
        # Threat Severity
        severity_score = self._severity_to_score(context.severity)
        factor_scores[RiskFactor.THREAT_SEVERITY] = severity_score
        
        # Threat Confidence
        factor_scores[RiskFactor.THREAT_CONFIDENCE] = context.confidence
        
        # Asset Value
        factor_scores[RiskFactor.ASSET_VALUE] = context.asset_value
        
        # Vulnerability Score
        vulnerability_score = self._calculate_vulnerability_score(context)
        factor_scores[RiskFactor.VULNERABILITY_SCORE] = vulnerability_score
        
        # Exposure Level
        exposure_score = self._calculate_exposure_score(context)
        factor_scores[RiskFactor.EXPOSURE_LEVEL] = exposure_score
        
        # Attack Vector
        attack_vector_score = self._calculate_attack_vector_score(context)
        factor_scores[RiskFactor.ATTACK_VECTOR] = attack_vector_score
        
        # Impact Scope
        impact_scope_score = self._calculate_impact_scope_score(context)
        factor_scores[RiskFactor.IMPACT_SCOPE] = impact_scope_score
        
        # Temporal Factors
        temporal_score = self._calculate_temporal_factors(context)
        factor_scores[RiskFactor.TEMPORAL_FACTORS] = temporal_score
        
        # Environmental Factors
        environmental_score = self._calculate_environmental_factors(context)
        factor_scores[RiskFactor.ENVIRONMENTAL_FACTORS] = environmental_score
        
        # Behavioral Factors
        behavioral_score = self._calculate_behavioral_factors(context)
        factor_scores[RiskFactor.BEHAVIORAL_FACTORS] = behavioral_score
        
        return factor_scores
    
    def _calculate_overall_score(
        self,
        category_scores: Dict[RiskCategory, float],
        factor_scores: Dict[RiskFactor, float]
    ) -> float:
        """Calculate overall risk score from category and factor scores."""
        # Weighted combination of category scores
        category_weight = 0.6
        factor_weight = 0.4
        
        # Calculate weighted category score
        category_total = 0.0
        category_weight_sum = 0.0
        
        for category, score in category_scores.items():
            weight = self.risk_weights["categories"].get(category.value, 1.0)
            category_total += score * weight
            category_weight_sum += weight
        
        category_average = category_total / category_weight_sum if category_weight_sum > 0 else 0.0
        
        # Calculate weighted factor score
        factor_total = 0.0
        factor_weight_sum = 0.0
        
        for factor, score in factor_scores.items():
            weight = self.risk_weights["factors"].get(factor.value, 1.0)
            factor_total += score * weight
            factor_weight_sum += weight
        
        factor_average = factor_total / factor_weight_sum if factor_weight_sum > 0 else 0.0
        
        # Combine category and factor scores
        overall_score = (category_average * category_weight) + (factor_average * factor_weight)
        
        return min(1.0, max(0.0, overall_score))
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level based on score."""
        if score >= 0.9:
            return RiskLevel.EXTREME
        elif score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MODERATE
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _calculate_security_risk(self, context: RiskContext) -> float:
        """Calculate security risk score."""
        # Base score on threat type and severity
        base_score = self._get_threat_base_score(context.threat_type, context.severity)
        
        # Adjust based on confidence
        confidence_adjustment = context.confidence * 0.3
        
        # Adjust based on attack vector
        attack_vector_adjustment = self._get_attack_vector_adjustment(context.attack_vector)
        
        # Adjust based on asset value
        asset_adjustment = context.asset_value * 0.2
        
        security_score = base_score + confidence_adjustment + attack_vector_adjustment + asset_adjustment
        
        return min(1.0, max(0.0, security_score))
    
    def _calculate_operational_risk(self, context: RiskContext) -> float:
        """Calculate operational risk score."""
        # Base score on impact to operations
        base_score = 0.3
        
        # Adjust based on criticality
        criticality_adjustment = context.criticality * 0.4
        
        # Adjust based on availability impact
        availability_impact = self._assess_availability_impact(context)
        
        # Adjust based on recovery complexity
        recovery_complexity = self._assess_recovery_complexity(context)
        
        operational_score = base_score + criticality_adjustment + availability_impact + recovery_complexity
        
        return min(1.0, max(0.0, operational_score))
    
    def _calculate_compliance_risk(self, context: RiskContext) -> float:
        """Calculate compliance risk score."""
        if not context.compliance_requirements:
            return 0.0
        
        # Base score on regulatory requirements
        base_score = 0.2
        
        # Adjust based on data sensitivity
        data_sensitivity = self._assess_data_sensitivity(context)
        
        # Adjust based on regulatory environment
        regulatory_adjustment = self._get_regulatory_adjustment(context.regulatory_context)
        
        compliance_score = base_score + data_sensitivity + regulatory_adjustment
        
        return min(1.0, max(0.0, compliance_score))
    
    def _calculate_reputational_risk(self, context: RiskContext) -> float:
        """Calculate reputational risk score."""
        # Base score on threat visibility
        base_score = 0.2
        
        # Adjust based on public exposure
        public_exposure = self._assess_public_exposure(context)
        
        # Adjust based on stakeholder impact
        stakeholder_impact = self._assess_stakeholder_impact(context)
        
        reputational_score = base_score + public_exposure + stakeholder_impact
        
        return min(1.0, max(0.0, reputational_score))
    
    def _calculate_financial_risk(self, context: RiskContext) -> float:
        """Calculate financial risk score."""
        # Base score on potential financial impact
        base_score = 0.1
        
        # Adjust based on asset value
        asset_value_adjustment = context.asset_value * 0.3
        
        # Adjust based on business impact
        business_impact = self._assess_business_impact(context)
        
        financial_score = base_score + asset_value_adjustment + business_impact
        
        return min(1.0, max(0.0, financial_score))
    
    def _calculate_privacy_risk(self, context: RiskContext) -> float:
        """Calculate privacy risk score."""
        # Base score on data exposure potential
        base_score = 0.1
        
        # Adjust based on PII exposure
        pii_exposure = self._assess_pii_exposure(context)
        
        # Adjust based on data classification
        data_classification = self._assess_data_classification(context)
        
        privacy_score = base_score + pii_exposure + data_classification
        
        return min(1.0, max(0.0, privacy_score))
    
    def _calculate_availability_risk(self, context: RiskContext) -> float:
        """Calculate availability risk score."""
        # Base score on service disruption potential
        base_score = 0.2
        
        # Adjust based on criticality
        criticality_adjustment = context.criticality * 0.4
        
        # Adjust based on recovery time
        recovery_time_adjustment = self._assess_recovery_time(context)
        
        availability_score = base_score + criticality_adjustment + recovery_time_adjustment
        
        return min(1.0, max(0.0, availability_score))
    
    def _calculate_integrity_risk(self, context: RiskContext) -> float:
        """Calculate integrity risk score."""
        # Base score on data integrity impact
        base_score = 0.2
        
        # Adjust based on data criticality
        data_criticality = self._assess_data_criticality(context)
        
        # Adjust based on tampering potential
        tampering_potential = self._assess_tampering_potential(context)
        
        integrity_score = base_score + data_criticality + tampering_potential
        
        return min(1.0, max(0.0, integrity_score))
    
    # Helper methods for risk calculations
    def _severity_to_score(self, severity: SeverityLevel) -> float:
        """Convert severity level to score."""
        return {
            SeverityLevel.LOW: 0.2,
            SeverityLevel.MEDIUM: 0.4,
            SeverityLevel.HIGH: 0.7,
            SeverityLevel.CRITICAL: 1.0
        }.get(severity, 0.3)
    
    def _get_threat_base_score(self, threat_type: ThreatType, severity: SeverityLevel) -> float:
        """Get base score for threat type and severity."""
        threat_scores = {
            ThreatType.SQL_INJECTION: 0.8,
            ThreatType.COMMAND_INJECTION: 0.9,
            ThreatType.XSS_ATTACK: 0.6,
            ThreatType.PATH_TRAVERSAL: 0.7,
            ThreatType.PROMPT_INJECTION: 0.5,
            ThreatType.BEHAVIORAL_ANOMALY: 0.4,
            ThreatType.DATA_EXFILTRATION: 0.8,
            ThreatType.UNAUTHORIZED_ACCESS: 0.7
        }
        
        base_score = threat_scores.get(threat_type, 0.5)
        severity_multiplier = self._severity_to_score(severity)
        
        return base_score * severity_multiplier
    
    def _get_attack_vector_adjustment(self, attack_vector: str) -> float:
        """Get adjustment based on attack vector."""
        vector_scores = {
            "network": 0.3,
            "adjacent": 0.2,
            "local": 0.1,
            "physical": 0.05,
            "unknown": 0.15
        }
        
        return vector_scores.get(attack_vector, 0.15)
    
    # Assessment helper methods
    def _assess_availability_impact(self, context: RiskContext) -> float:
        """Assess availability impact."""
        # Simplified assessment - in production, this would be more sophisticated
        if context.impact_scope == "global":
            return 0.4
        elif context.impact_scope == "regional":
            return 0.3
        elif context.impact_scope == "local":
            return 0.2
        else:
            return 0.1
    
    def _assess_recovery_complexity(self, context: RiskContext) -> float:
        """Assess recovery complexity."""
        # Based on exploit complexity and environment
        complexity_score = context.exploit_complexity * 0.2
        
        # Adjust based on environment
        if context.environment == "production":
            complexity_score += 0.2
        elif context.environment == "staging":
            complexity_score += 0.1
        
        return min(0.3, complexity_score)
    
    def _assess_data_sensitivity(self, context: RiskContext) -> float:
        """Assess data sensitivity."""
        # Check for sensitive data indicators
        sensitive_indicators = ["pii", "financial", "health", "confidential"]
        
        sensitivity_score = 0.0
        for indicator in sensitive_indicators:
            if indicator in str(context.user_behavior).lower():
                sensitivity_score += 0.1
        
        return min(0.4, sensitivity_score)
    
    def _get_regulatory_adjustment(self, regulatory_context: Dict[str, Any]) -> float:
        """Get adjustment based on regulatory context."""
        if not regulatory_context:
            return 0.0
        
        # Check for high-impact regulations
        high_impact_regs = ["gdpr", "hipaa", "sox", "pci_dss"]
        
        adjustment = 0.0
        for reg in high_impact_regs:
            if reg in regulatory_context:
                adjustment += 0.1
        
        return min(0.3, adjustment)
    
    def _assess_public_exposure(self, context: RiskContext) -> float:
        """Assess public exposure risk."""
        # Simplified assessment
        if context.environment == "production":
            return 0.3
        elif context.environment == "staging":
            return 0.1
        else:
            return 0.05
    
    def _assess_stakeholder_impact(self, context: RiskContext) -> float:
        """Assess stakeholder impact."""
        # Based on asset value and criticality
        return (context.asset_value + context.criticality) * 0.15
    
    def _assess_business_impact(self, context: RiskContext) -> float:
        """Assess business impact."""
        # Based on criticality and environment
        base_impact = context.criticality * 0.2
        
        if context.environment == "production":
            base_impact += 0.2
        
        return min(0.4, base_impact)
    
    def _assess_pii_exposure(self, context: RiskContext) -> float:
        """Assess PII exposure risk."""
        # Check for PII indicators in context
        pii_indicators = ["email", "phone", "ssn", "credit_card", "address"]
        
        exposure_score = 0.0
        context_str = str(context.user_behavior).lower()
        
        for indicator in pii_indicators:
            if indicator in context_str:
                exposure_score += 0.1
        
        return min(0.4, exposure_score)
    
    def _assess_data_classification(self, context: RiskContext) -> float:
        """Assess data classification level."""
        # Simplified classification assessment
        classification_levels = {
            "public": 0.0,
            "internal": 0.1,
            "confidential": 0.2,
            "restricted": 0.3,
            "top_secret": 0.4
        }
        
        # Check session context for classification
        classification = context.session_context.get("data_classification", "internal")
        
        return classification_levels.get(classification, 0.1)
    
    def _assess_recovery_time(self, context: RiskContext) -> float:
        """Assess recovery time impact."""
        # Based on criticality and complexity
        base_time = context.criticality * 0.2
        complexity_adjustment = context.exploit_complexity * 0.1
        
        return min(0.3, base_time + complexity_adjustment)
    
    def _assess_data_criticality(self, context: RiskContext) -> float:
        """Assess data criticality."""
        # Based on asset value and environment
        return (context.asset_value + context.criticality) * 0.15
    
    def _assess_tampering_potential(self, context: RiskContext) -> float:
        """Assess tampering potential."""
        # Based on threat type and access level
        tampering_scores = {
            ThreatType.SQL_INJECTION: 0.3,
            ThreatType.COMMAND_INJECTION: 0.4,
            ThreatType.PATH_TRAVERSAL: 0.2,
            ThreatType.DATA_EXFILTRATION: 0.1
        }
        
        return tampering_scores.get(context.threat_type, 0.15)
    
    # Factor calculation methods
    def _calculate_vulnerability_score(self, context: RiskContext) -> float:
        """Calculate vulnerability score."""
        # Based on exploit complexity and environment
        base_score = 1.0 - context.exploit_complexity  # Lower complexity = higher vulnerability
        
        # Adjust based on environment hardening
        if context.environment == "production":
            base_score *= 0.8  # Assume better hardening
        elif context.environment == "development":
            base_score *= 1.2  # Assume less hardening
        
        return min(1.0, max(0.0, base_score))
    
    def _calculate_exposure_score(self, context: RiskContext) -> float:
        """Calculate exposure score."""
        # Based on attack vector and environment
        vector_exposure = {
            "network": 0.8,
            "adjacent": 0.6,
            "local": 0.4,
            "physical": 0.2,
            "unknown": 0.5
        }
        
        base_exposure = vector_exposure.get(context.attack_vector, 0.5)
        
        # Adjust based on environment
        if context.environment == "production":
            base_exposure *= 1.2
        
        return min(1.0, base_exposure)
    
    def _calculate_attack_vector_score(self, context: RiskContext) -> float:
        """Calculate attack vector score."""
        return self._get_attack_vector_adjustment(context.attack_vector) * 2.5
    
    def _calculate_impact_scope_score(self, context: RiskContext) -> float:
        """Calculate impact scope score."""
        scope_scores = {
            "global": 1.0,
            "regional": 0.7,
            "local": 0.4,
            "isolated": 0.2,
            "unknown": 0.5
        }
        
        return scope_scores.get(context.impact_scope, 0.5)
    
    def _calculate_temporal_factors(self, context: RiskContext) -> float:
        """Calculate temporal factors score."""
        # Time-based risk factors
        now = datetime.now(timezone.utc)
        time_diff = (now - context.timestamp).total_seconds()
        
        # Recent events are more critical
        recency_score = max(0.0, 1.0 - (time_diff / 3600))  # Decay over 1 hour
        
        return recency_score * 0.5
    
    def _calculate_environmental_factors(self, context: RiskContext) -> float:
        """Calculate environmental factors score."""
        env_scores = {
            "production": 0.8,
            "staging": 0.5,
            "development": 0.3,
            "test": 0.2,
            "unknown": 0.4
        }
        
        return env_scores.get(context.environment, 0.4)
    
    def _calculate_behavioral_factors(self, context: RiskContext) -> float:
        """Calculate behavioral factors score."""
        # Analyze behavioral patterns
        behavioral_score = 0.0
        
        # Check for anomalous behavior
        if context.agent_behavior.get("anomalous", False):
            behavioral_score += 0.3
        
        # Check for suspicious patterns
        if context.user_behavior.get("suspicious", False):
            behavioral_score += 0.2
        
        # Check for privilege escalation
        if context.session_context.get("privilege_escalation", False):
            behavioral_score += 0.4
        
        return min(1.0, behavioral_score)
    
    # Assessment methods
    async def _assess_threat(self, context: RiskContext) -> Dict[str, Any]:
        """Assess threat characteristics."""
        return {
            "threat_type": context.threat_type.value,
            "severity": context.severity.value,
            "confidence": context.confidence,
            "attack_vector": context.attack_vector,
            "exploit_complexity": context.exploit_complexity,
            "threat_actor": "unknown",  # Would be enhanced with threat intelligence
            "attack_sophistication": self._assess_attack_sophistication(context),
            "persistence_capability": self._assess_persistence_capability(context)
        }
    
    async def _assess_impact(self, context: RiskContext) -> Dict[str, Any]:
        """Assess impact characteristics."""
        return {
            "confidentiality_impact": self._assess_confidentiality_impact(context),
            "integrity_impact": self._assess_integrity_impact(context),
            "availability_impact": self._assess_availability_impact(context),
            "scope": context.impact_scope,
            "affected_assets": self._identify_affected_assets(context),
            "business_impact": self._assess_business_impact(context),
            "recovery_time": self._estimate_recovery_time(context)
        }
    
    async def _assess_likelihood(self, context: RiskContext) -> Dict[str, Any]:
        """Assess likelihood of successful attack."""
        return {
            "exploit_probability": 1.0 - context.exploit_complexity,
            "vulnerability_score": self._calculate_vulnerability_score(context),
            "exposure_level": self._calculate_exposure_score(context),
            "threat_motivation": self._assess_threat_motivation(context),
            "defensive_effectiveness": self._assess_defensive_effectiveness(context),
            "overall_likelihood": self._calculate_overall_likelihood(context)
        }
    
    # Helper assessment methods
    def _assess_attack_sophistication(self, context: RiskContext) -> float:
        """Assess attack sophistication level."""
        sophistication_scores = {
            ThreatType.SQL_INJECTION: 0.6,
            ThreatType.COMMAND_INJECTION: 0.7,
            ThreatType.XSS_ATTACK: 0.4,
            ThreatType.PROMPT_INJECTION: 0.5,
            ThreatType.BEHAVIORAL_ANOMALY: 0.3
        }
        
        return sophistication_scores.get(context.threat_type, 0.5)
    
    def _assess_persistence_capability(self, context: RiskContext) -> float:
        """Assess persistence capability."""
        # Based on threat type and environment
        persistence_scores = {
            ThreatType.COMMAND_INJECTION: 0.8,
            ThreatType.SQL_INJECTION: 0.6,
            ThreatType.PATH_TRAVERSAL: 0.4,
            ThreatType.XSS_ATTACK: 0.3
        }
        
        base_score = persistence_scores.get(context.threat_type, 0.3)
        
        # Adjust based on environment
        if context.environment == "production":
            base_score *= 1.2
        
        return min(1.0, base_score)
    
    def _assess_confidentiality_impact(self, context: RiskContext) -> float:
        """Assess confidentiality impact."""
        # Based on data sensitivity and threat type
        data_sensitivity = self._assess_data_sensitivity(context)
        
        impact_scores = {
            ThreatType.DATA_EXFILTRATION: 0.9,
            ThreatType.SQL_INJECTION: 0.7,
            ThreatType.PATH_TRAVERSAL: 0.6,
            ThreatType.UNAUTHORIZED_ACCESS: 0.8
        }
        
        base_impact = impact_scores.get(context.threat_type, 0.3)
        
        return min(1.0, base_impact + data_sensitivity)
    
    def _assess_integrity_impact(self, context: RiskContext) -> float:
        """Assess integrity impact."""
        impact_scores = {
            ThreatType.SQL_INJECTION: 0.8,
            ThreatType.COMMAND_INJECTION: 0.9,
            ThreatType.XSS_ATTACK: 0.6,
            ThreatType.PATH_TRAVERSAL: 0.5
        }
        
        return impact_scores.get(context.threat_type, 0.3)
    
    def _identify_affected_assets(self, context: RiskContext) -> List[str]:
        """Identify potentially affected assets."""
        # Simplified asset identification
        assets = ["agent_system"]
        
        if context.threat_type in [ThreatType.SQL_INJECTION, ThreatType.DATA_EXFILTRATION]:
            assets.append("database")
        
        if context.threat_type == ThreatType.COMMAND_INJECTION:
            assets.extend(["file_system", "operating_system"])
        
        if context.environment == "production":
            assets.append("production_environment")
        
        return assets
    
    def _estimate_recovery_time(self, context: RiskContext) -> str:
        """Estimate recovery time."""
        # Based on threat type and environment
        if context.threat_type == ThreatType.COMMAND_INJECTION:
            return "4-8 hours"
        elif context.threat_type == ThreatType.SQL_INJECTION:
            return "2-4 hours"
        elif context.threat_type == ThreatType.DATA_EXFILTRATION:
            return "1-2 hours"
        else:
            return "1-2 hours"
    
    def _assess_threat_motivation(self, context: RiskContext) -> float:
        """Assess threat actor motivation."""
        # Based on asset value and environment
        motivation_score = context.asset_value * 0.5
        
        if context.environment == "production":
            motivation_score += 0.3
        
        return min(1.0, motivation_score)
    
    def _assess_defensive_effectiveness(self, context: RiskContext) -> float:
        """Assess defensive effectiveness."""
        # Based on environment and security measures
        effectiveness_scores = {
            "production": 0.7,
            "staging": 0.5,
            "development": 0.3,
            "test": 0.4
        }
        
        return effectiveness_scores.get(context.environment, 0.4)
    
    def _calculate_overall_likelihood(self, context: RiskContext) -> float:
        """Calculate overall likelihood score."""
        exploit_prob = 1.0 - context.exploit_complexity
        vulnerability_score = self._calculate_vulnerability_score(context)
        exposure_score = self._calculate_exposure_score(context)
        motivation = self._assess_threat_motivation(context)
        defensive_effectiveness = self._assess_defensive_effectiveness(context)
        
        # Weighted combination
        likelihood = (
            exploit_prob * 0.3 +
            vulnerability_score * 0.3 +
            exposure_score * 0.2 +
            motivation * 0.1 +
            (1.0 - defensive_effectiveness) * 0.1
        )
        
        return min(1.0, max(0.0, likelihood))
    
    # Utility methods
    def _calculate_urgency_score(self, context: RiskContext) -> float:
        """Calculate urgency score."""
        # Based on severity, confidence, and temporal factors
        severity_score = self._severity_to_score(context.severity)
        confidence_factor = context.confidence
        temporal_factor = self._calculate_temporal_factors(context)
        
        urgency = (severity_score * 0.5) + (confidence_factor * 0.3) + (temporal_factor * 0.2)
        
        return min(1.0, urgency)
    
    async def _calculate_trend_score(self, context: RiskContext) -> float:
        """Calculate trend score."""
        if not self.enable_trend_analysis or len(self.risk_history) < 2:
            return 0.0
        
        # Get recent risk scores
        recent_scores = [entry[1] for entry in list(self.risk_history)[-10:]]
        
        if len(recent_scores) < 2:
            return 0.0
        
        # Calculate trend
        trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, trend + 0.5))
    
    def _calculate_escalation_score(self, context: RiskContext) -> float:
        """Calculate escalation score."""
        # Based on risk factors that suggest escalation
        escalation_factors = []
        
        # High severity
        if context.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            escalation_factors.append(0.3)
        
        # High confidence
        if context.confidence > 0.8:
            escalation_factors.append(0.2)
        
        # Production environment
        if context.environment == "production":
            escalation_factors.append(0.2)
        
        # High asset value
        if context.asset_value > 0.7:
            escalation_factors.append(0.2)
        
        # Critical compliance requirements
        if any(req in ["gdpr", "hipaa", "sox"] for req in context.compliance_requirements):
            escalation_factors.append(0.1)
        
        return min(1.0, sum(escalation_factors))
    
    def _generate_risk_mitigation(self, context: RiskContext, risk_score: float) -> List[str]:
        """Generate risk mitigation recommendations."""
        mitigations = []
        
        # Threat-specific mitigations
        if context.threat_type == ThreatType.SQL_INJECTION:
            mitigations.extend([
                "Implement parameterized queries",
                "Apply input validation and sanitization",
                "Use least privilege database access",
                "Enable database activity monitoring"
            ])
        
        elif context.threat_type == ThreatType.COMMAND_INJECTION:
            mitigations.extend([
                "Implement input validation and sanitization",
                "Use command allow-lists",
                "Apply principle of least privilege",
                "Enable system call monitoring"
            ])
        
        elif context.threat_type == ThreatType.XSS_ATTACK:
            mitigations.extend([
                "Implement output encoding",
                "Use Content Security Policy (CSP)",
                "Apply input validation",
                "Enable XSS protection headers"
            ])
        
        # General high-risk mitigations
        if risk_score > 0.7:
            mitigations.extend([
                "Implement immediate incident response",
                "Enhance monitoring and alerting",
                "Review and update security policies",
                "Conduct security assessment"
            ])
        
        return mitigations
    
    def _generate_priority_actions(self, context: RiskContext, risk_score: float) -> List[str]:
        """Generate priority actions."""
        actions = []
        
        if risk_score > 0.8:
            actions.extend([
                "Immediate security team notification",
                "Activate incident response plan",
                "Implement emergency containment measures"
            ])
        
        elif risk_score > 0.6:
            actions.extend([
                "Escalate to security team",
                "Implement additional monitoring",
                "Review access controls"
            ])
        
        else:
            actions.extend([
                "Log and monitor",
                "Review security controls",
                "Schedule security assessment"
            ])
        
        return actions
    
    def _generate_monitoring_recommendations(self, context: RiskContext) -> List[str]:
        """Generate monitoring recommendations."""
        recommendations = []
        
        # Threat-specific monitoring
        if context.threat_type == ThreatType.SQL_INJECTION:
            recommendations.extend([
                "Monitor database query patterns",
                "Enable SQL injection detection rules",
                "Track database access anomalies"
            ])
        
        elif context.threat_type == ThreatType.COMMAND_INJECTION:
            recommendations.extend([
                "Monitor system command execution",
                "Track process creation events",
                "Enable command injection detection"
            ])
        
        # General monitoring
        recommendations.extend([
            "Enhance behavioral monitoring",
            "Implement real-time alerting",
            "Enable comprehensive logging"
        ])
        
        return recommendations
    
    def _calculate_confidence_interval(
        self,
        risk_score: float,
        factor_scores: Dict[RiskFactor, float],
        context: RiskContext
    ) -> Tuple[float, float]:
        """Calculate confidence interval for risk score."""
        # Simplified confidence interval calculation
        # In production, this would use more sophisticated statistical methods
        
        # Base confidence on data quality and completeness
        confidence_factors = [
            context.confidence,  # Threat detection confidence
            min(1.0, len(factor_scores) / 10.0),  # Factor completeness
            min(1.0, len(context.historical_events) / 50.0)  # Historical data
        ]
        
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Calculate margin of error
        margin_of_error = (1.0 - overall_confidence) * 0.2
        
        lower_bound = max(0.0, risk_score - margin_of_error)
        upper_bound = min(1.0, risk_score + margin_of_error)
        
        return (lower_bound, upper_bound)
    
    # Caching methods
    def _generate_cache_key(self, context: RiskContext) -> str:
        """Generate cache key for risk context."""
        key_data = {
            "agent_id": context.agent_id,
            "threat_type": context.threat_type.value,
            "severity": context.severity.value,
            "confidence": round(context.confidence, 2),
            "asset_value": round(context.asset_value, 2),
            "environment": context.environment,
            "timestamp": context.timestamp.strftime("%Y-%m-%d-%H-%M")  # Minute precision
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_score(self, cache_key: str) -> Optional[RiskScore]:
        """Get cached risk score."""
        if cache_key not in self.score_cache:
            return None
        
        cached_score, cache_time = self.score_cache[cache_key]
        
        # Check if cache is still valid
        if (datetime.now(timezone.utc) - cache_time).total_seconds() > self.cache_ttl:
            del self.score_cache[cache_key]
            return None
        
        return cached_score
    
    def _cache_score(self, cache_key: str, score: RiskScore) -> None:
        """Cache risk score."""
        self.score_cache[cache_key] = (score, datetime.now(timezone.utc))
        
        # Clean up old cache entries
        if len(self.score_cache) > 1000:
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        now = datetime.now(timezone.utc)
        expired_keys = []
        
        for key, (score, cache_time) in self.score_cache.items():
            if (now - cache_time).total_seconds() > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.score_cache[key]
    
    def _update_risk_history(self, context: RiskContext, score: RiskScore) -> None:
        """Update risk history for trend analysis."""
        with self.lock:
            self.risk_history.append((context.timestamp, score.overall_score))
    
    def _update_metrics(self, processing_time: float, cache_hit: bool = False) -> None:
        """Update performance metrics."""
        with self.lock:
            self.metrics["total_assessments"] += 1
            
            # Update average processing time
            current_avg = self.metrics["avg_processing_time"]
            total_assessments = self.metrics["total_assessments"]
            
            self.metrics["avg_processing_time"] = (
                (current_avg * (total_assessments - 1)) + processing_time
            ) / total_assessments
            
            # Update cache hit rate
            if cache_hit:
                cache_hits = self.metrics.get("cache_hits", 0) + 1
                self.metrics["cache_hits"] = cache_hits
                self.metrics["cache_hit_rate"] = cache_hits / total_assessments
    
    # Configuration methods
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default risk scoring configuration."""
        return {
            "risk_weights": {
                "categories": {
                    "security_risk": 1.0,
                    "operational_risk": 0.8,
                    "compliance_risk": 0.9,
                    "reputational_risk": 0.7,
                    "financial_risk": 0.8,
                    "privacy_risk": 0.9,
                    "availability_risk": 0.8,
                    "integrity_risk": 0.9
                },
                "factors": {
                    "threat_severity": 1.0,
                    "threat_confidence": 0.9,
                    "asset_value": 0.8,
                    "vulnerability_score": 0.9,
                    "exposure_level": 0.7,
                    "attack_vector": 0.8,
                    "impact_scope": 0.8,
                    "temporal_factors": 0.6,
                    "environmental_factors": 0.7,
                    "behavioral_factors": 0.8
                }
            },
            "thresholds": {
                "extreme_risk": 0.9,
                "critical_risk": 0.8,
                "high_risk": 0.6,
                "moderate_risk": 0.4,
                "low_risk": 0.2
            },
            "cache_ttl": 300,
            "enable_ml_scoring": True,
            "enable_trend_analysis": True
        }
    
    def _load_risk_weights(self) -> Dict[str, Any]:
        """Load risk scoring weights."""
        return self.config.get("risk_weights", {})
    
    def _load_threat_matrices(self) -> Dict[str, Any]:
        """Load threat assessment matrices."""
        # Placeholder for threat matrices
        return {
            "cvss_matrix": {},
            "owasp_matrix": {},
            "custom_matrix": {}
        }
    
    def _load_compliance_frameworks(self) -> Dict[str, Any]:
        """Load compliance framework configurations."""
        return {
            "gdpr": {
                "risk_factors": ["privacy_risk", "data_protection"],
                "severity_multiplier": 1.2,
                "mandatory_controls": ["data_encryption", "access_logging"]
            },
            "hipaa": {
                "risk_factors": ["privacy_risk", "data_security"],
                "severity_multiplier": 1.3,
                "mandatory_controls": ["audit_logging", "access_controls"]
            },
            "sox": {
                "risk_factors": ["integrity_risk", "financial_risk"],
                "severity_multiplier": 1.1,
                "mandatory_controls": ["change_management", "audit_trails"]
            }
        }
    
    # Trend analysis methods
    def _get_historical_data(self, time_period: str) -> List[Tuple[datetime, float]]:
        """Get historical risk data for specified period."""
        now = datetime.now(timezone.utc)
        
        # Parse time period
        if time_period == "1h":
            cutoff = now - timedelta(hours=1)
        elif time_period == "24h":
            cutoff = now - timedelta(hours=24)
        elif time_period == "7d":
            cutoff = now - timedelta(days=7)
        elif time_period == "30d":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(hours=24)  # Default to 24h
        
        # Filter historical data
        return [
            (timestamp, score) for timestamp, score in self.risk_history
            if timestamp >= cutoff
        ]
    
    def _create_empty_trend(self, time_period: str) -> RiskTrend:
        """Create empty trend for insufficient data."""
        return RiskTrend(
            agent_id=self.agent_id,
            time_period=time_period,
            trend_direction="stable",
            trend_magnitude=0.0,
            historical_scores=[],
            moving_averages={},
            volatility_metrics={},
            predicted_score=0.0,
            prediction_confidence=0.0,
            risk_forecast={},
            anomalies_detected=[],
            pattern_changes=[]
        )
    
    def _calculate_trend_direction(self, historical_data: List[Tuple[datetime, float]]) -> str:
        """Calculate trend direction."""
        if len(historical_data) < 2:
            return "stable"
        
        scores = [score for _, score in historical_data]
        
        # Simple linear trend
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return "increasing"
        elif diff < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_trend_magnitude(self, historical_data: List[Tuple[datetime, float]]) -> float:
        """Calculate trend magnitude."""
        if len(historical_data) < 2:
            return 0.0
        
        scores = [score for _, score in historical_data]
        
        # Calculate rate of change
        first_score = scores[0]
        last_score = scores[-1]
        
        return abs(last_score - first_score) / len(scores)
    
    def _calculate_moving_averages(self, historical_data: List[Tuple[datetime, float]]) -> Dict[str, float]:
        """Calculate moving averages."""
        scores = [score for _, score in historical_data]
        
        if len(scores) < 2:
            return {}
        
        averages = {}
        
        # 5-point moving average
        if len(scores) >= 5:
            averages["5_point"] = sum(scores[-5:]) / 5
        
        # 10-point moving average
        if len(scores) >= 10:
            averages["10_point"] = sum(scores[-10:]) / 10
        
        # Overall average
        averages["overall"] = sum(scores) / len(scores)
        
        return averages
    
    def _calculate_volatility_metrics(self, historical_data: List[Tuple[datetime, float]]) -> Dict[str, float]:
        """Calculate volatility metrics."""
        scores = [score for _, score in historical_data]
        
        if len(scores) < 2:
            return {}
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        return {
            "mean": mean_score,
            "variance": variance,
            "standard_deviation": std_dev,
            "coefficient_of_variation": std_dev / mean_score if mean_score > 0 else 0.0
        }
    
    def _detect_risk_anomalies(self, historical_data: List[Tuple[datetime, float]]) -> List[Dict[str, Any]]:
        """Detect anomalies in risk data."""
        if len(historical_data) < 10:
            return []
        
        scores = [score for _, score in historical_data]
        timestamps = [ts for ts, _ in historical_data]
        
        # Calculate statistical thresholds
        mean_score = sum(scores) / len(scores)
        std_dev = math.sqrt(sum((score - mean_score) ** 2 for score in scores) / len(scores))
        
        upper_threshold = mean_score + (2 * std_dev)
        lower_threshold = mean_score - (2 * std_dev)
        
        anomalies = []
        
        for i, (timestamp, score) in enumerate(zip(timestamps, scores)):
            if score > upper_threshold or score < lower_threshold:
                anomalies.append({
                    "timestamp": timestamp.isoformat(),
                    "score": score,
                    "type": "high" if score > upper_threshold else "low",
                    "deviation": abs(score - mean_score) / std_dev
                })
        
        return anomalies
    
    def _detect_pattern_changes(self, historical_data: List[Tuple[datetime, float]]) -> List[Dict[str, Any]]:
        """Detect pattern changes in risk data."""
        if len(historical_data) < 20:
            return []
        
        # Simple pattern change detection
        # In production, this would use more sophisticated change point detection
        
        scores = [score for _, score in historical_data]
        timestamps = [ts for ts, _ in historical_data]
        
        changes = []
        window_size = 10
        
        for i in range(window_size, len(scores) - window_size):
            before_window = scores[i-window_size:i]
            after_window = scores[i:i+window_size]
            
            before_avg = sum(before_window) / len(before_window)
            after_avg = sum(after_window) / len(after_window)
            
            if abs(after_avg - before_avg) > 0.2:  # Significant change
                changes.append({
                    "timestamp": timestamps[i].isoformat(),
                    "change_type": "increase" if after_avg > before_avg else "decrease",
                    "magnitude": abs(after_avg - before_avg),
                    "before_average": before_avg,
                    "after_average": after_avg
                })
        
        return changes
    
    def _predict_future_risk(self, historical_data: List[Tuple[datetime, float]]) -> float:
        """Predict future risk score."""
        if len(historical_data) < 5:
            return 0.0
        
        scores = [score for _, score in historical_data]
        
        # Simple linear prediction
        # In production, this would use more sophisticated ML models
        
        # Calculate trend
        recent_scores = scores[-5:]
        trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        
        # Predict next score
        predicted_score = scores[-1] + trend
        
        return min(1.0, max(0.0, predicted_score))
    
    def _calculate_prediction_confidence(self, historical_data: List[Tuple[datetime, float]]) -> float:
        """Calculate prediction confidence."""
        if len(historical_data) < 5:
            return 0.0
        
        scores = [score for _, score in historical_data]
        
        # Base confidence on data consistency
        std_dev = math.sqrt(sum((score - sum(scores)/len(scores)) ** 2 for score in scores) / len(scores))
        
        # Lower standard deviation = higher confidence
        confidence = max(0.0, 1.0 - (std_dev * 2))
        
        return confidence
    
    def _generate_risk_forecast(self, historical_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Generate risk forecast."""
        if len(historical_data) < 5:
            return {}
        
        predicted_score = self._predict_future_risk(historical_data)
        prediction_confidence = self._calculate_prediction_confidence(historical_data)
        
        return {
            "predicted_score": predicted_score,
            "confidence": prediction_confidence,
            "forecast_horizon": "1 hour",
            "key_factors": ["historical_trend", "volatility"],
            "risk_scenarios": {
                "best_case": max(0.0, predicted_score - 0.1),
                "worst_case": min(1.0, predicted_score + 0.1),
                "most_likely": predicted_score
            }
        }
    
    # Compliance assessment methods
    async def _assess_framework_compliance(self, context: RiskContext, framework: str) -> Dict[str, Any]:
        """Assess compliance for specific framework."""
        framework_config = self.compliance_frameworks.get(framework, {})
        
        if not framework_config:
            return {"status": "unknown_framework", "score": 0.0}
        
        # Calculate compliance risk score
        base_risk = self._calculate_security_risk(context)
        severity_multiplier = framework_config.get("severity_multiplier", 1.0)
        
        compliance_risk = base_risk * severity_multiplier
        
        # Check mandatory controls
        mandatory_controls = framework_config.get("mandatory_controls", [])
        control_compliance = self._assess_control_compliance(context, mandatory_controls)
        
        return {
            "framework": framework,
            "compliance_risk": compliance_risk,
            "control_compliance": control_compliance,
            "severity_multiplier": severity_multiplier,
            "recommendations": self._generate_framework_recommendations(framework, compliance_risk)
        }
    
    def _assess_control_compliance(self, context: RiskContext, controls: List[str]) -> Dict[str, Any]:
        """Assess compliance with mandatory controls."""
        # Simplified control assessment
        # In production, this would integrate with actual control systems
        
        compliance_status = {}
        
        for control in controls:
            # Mock compliance check
            compliance_status[control] = {
                "status": "compliant",  # Would be actual status
                "effectiveness": 0.8,  # Would be actual effectiveness
                "last_assessed": datetime.now(timezone.utc).isoformat()
            }
        
        overall_compliance = sum(
            status["effectiveness"] for status in compliance_status.values()
        ) / len(compliance_status) if compliance_status else 0.0
        
        return {
            "controls": compliance_status,
            "overall_compliance": overall_compliance,
            "compliant_controls": len(compliance_status),
            "total_controls": len(controls)
        }
    
    def _generate_framework_recommendations(self, framework: str, compliance_risk: float) -> List[str]:
        """Generate framework-specific recommendations."""
        recommendations = []
        
        if framework == "gdpr":
            recommendations.extend([
                "Implement data encryption at rest and in transit",
                "Enable comprehensive audit logging",
                "Establish data retention policies",
                "Implement privacy by design principles"
            ])
        
        elif framework == "hipaa":
            recommendations.extend([
                "Implement access controls and authentication",
                "Enable audit logging for all data access",
                "Establish incident response procedures",
                "Conduct regular security assessments"
            ])
        
        elif framework == "sox":
            recommendations.extend([
                "Implement change management controls",
                "Enable comprehensive audit trails",
                "Establish segregation of duties",
                "Conduct regular compliance testing"
            ])
        
        if compliance_risk > 0.7:
            recommendations.append("Immediate compliance review required")
        
        return recommendations
    
    def _calculate_overall_compliance_risk(self, assessments: Dict[str, Any]) -> float:
        """Calculate overall compliance risk."""
        if not assessments:
            return 0.0
        
        total_risk = 0.0
        total_weight = 0.0
        
        for framework, assessment in assessments.items():
            risk = assessment.get("compliance_risk", 0.0)
            weight = 1.0  # Could be framework-specific
            
            total_risk += risk * weight
            total_weight += weight
        
        return total_risk / total_weight if total_weight > 0 else 0.0
    
    def _generate_compliance_recommendations(self, assessments: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        for framework, assessment in assessments.items():
            framework_recommendations = assessment.get("recommendations", [])
            recommendations.extend(framework_recommendations)
        
        # Remove duplicates
        return list(set(recommendations))
    
    def _generate_compliance_actions(self, assessments: Dict[str, Any]) -> List[str]:
        """Generate compliance priority actions."""
        actions = []
        
        high_risk_frameworks = [
            framework for framework, assessment in assessments.items()
            if assessment.get("compliance_risk", 0.0) > 0.7
        ]
        
        if high_risk_frameworks:
            actions.append(f"Immediate compliance review for: {', '.join(high_risk_frameworks)}")
        
        actions.extend([
            "Review and update compliance policies",
            "Conduct compliance training",
            "Schedule compliance audit"
        ])
        
        return actions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get risk scoring engine metrics."""
        with self.lock:
            return {
                "agent_id": self.agent_id,
                "total_assessments": self.metrics["total_assessments"],
                "avg_processing_time": self.metrics["avg_processing_time"],
                "cache_hit_rate": self.metrics["cache_hit_rate"],
                "trend_analyses": self.metrics["trend_analyses"],
                "cache_size": len(self.score_cache),
                "history_size": len(self.risk_history),
                "enable_ml_scoring": self.enable_ml_scoring,
                "enable_trend_analysis": self.enable_trend_analysis
            }
    
    def clear_cache(self) -> None:
        """Clear risk scoring cache."""
        with self.lock:
            self.score_cache.clear()
            self.trend_cache.clear()
            self.logger.info("Risk scoring cache cleared")
    
    def reset_history(self) -> None:
        """Reset risk history."""
        with self.lock:
            self.risk_history.clear()
            self.logger.info("Risk history reset")
    
    def shutdown(self) -> None:
        """Shutdown risk scoring engine."""
        self.logger.info(f"Risk scoring engine shutdown for agent {self.agent_id}") 