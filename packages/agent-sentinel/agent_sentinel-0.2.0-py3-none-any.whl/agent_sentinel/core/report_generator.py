"""
Unified Report Generator

Generates comprehensive monitoring reports that combine real-time logs,
security events, performance metrics, and analysis into a single file.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .types import SecurityEvent
from .constants import ThreatType, SeverityLevel


@dataclass
class UnifiedReport:
    """Comprehensive monitoring report combining logs and analysis"""
    agent_id: str
    start_time: datetime
    end_time: datetime
    session_logs: List[Dict[str, Any]] = field(default_factory=list)
    security_events: List[SecurityEvent] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    threat_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class UnifiedReportGenerator:
    """
    Generates unified monitoring reports with logs and analysis
    """
    
    def __init__(
        self,
        agent_id: str,
        log_file: str = "logs/agent_sentinel.log",
        report_file: Optional[str] = None
    ):
        """
        Initialize report generator
        
        Args:
            agent_id: Agent identifier
            log_file: Path to log file to analyze
            report_file: Output report file path (auto-generated if None)
        """
        self.agent_id = agent_id
        self.log_file = Path(log_file)
        
        if report_file:
            self.report_file = Path(report_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.report_file = Path(f"logs/{agent_id}_unified_report_{timestamp}.json")
        
        # Ensure logs directory exists
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"report_generator.{agent_id}")
    
    def generate_unified_report(self, events: List[SecurityEvent], metrics: Dict[str, Any]) -> UnifiedReport:
        """
        Generate comprehensive unified report
        
        Args:
            events: Security events from monitoring
            metrics: Performance and security metrics
            
        Returns:
            UnifiedReport with all monitoring data
        """
        start_time = datetime.now(timezone.utc)
        
        # Parse existing logs
        session_logs = self._parse_logs()
        
        # Analyze security events
        threat_analysis = self._analyze_threats(events)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(events, threat_analysis)
        
        # Create summary
        summary = self._create_summary(events, metrics, threat_analysis)
        
        end_time = datetime.now(timezone.utc)
        
        report = UnifiedReport(
            agent_id=self.agent_id,
            start_time=start_time,
            end_time=end_time,
            session_logs=session_logs,
            security_events=events,
            performance_metrics=metrics,
            threat_analysis=threat_analysis,
            recommendations=recommendations,
            summary=summary
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _parse_logs(self) -> List[Dict[str, Any]]:
        """Parse existing log file for this agent"""
        logs = []
        
        if not self.log_file.exists():
            return logs
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        log_entry = json.loads(line)
                        # Filter logs for this agent
                        if log_entry.get('agent_id') == self.agent_id:
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Error parsing logs: {e}")
        
        return logs
    
    def _analyze_threats(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze security events and generate threat insights"""
        if not events:
            return {
                'total_threats': 0,
                'threat_breakdown': {},
                'severity_distribution': {},
                'confidence_analysis': {},
                'risk_score': 0.0
            }
        
        # Threat breakdown by type
        threat_breakdown = {}
        severity_distribution = {}
        confidence_scores = []
        
        for event in events:
            threat_type = event.threat_type.value
            severity = event.severity.value
            
            threat_breakdown[threat_type] = threat_breakdown.get(threat_type, 0) + 1
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            confidence_scores.append(event.confidence)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(events)
        
        # Confidence analysis
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        high_confidence_threats = sum(1 for score in confidence_scores if score >= 0.8)
        
        return {
            'total_threats': len(events),
            'threat_breakdown': threat_breakdown,
            'severity_distribution': severity_distribution,
            'confidence_analysis': {
                'average_confidence': avg_confidence,
                'high_confidence_threats': high_confidence_threats,
                'confidence_distribution': {
                    'low': sum(1 for score in confidence_scores if score < 0.5),
                    'medium': sum(1 for score in confidence_scores if 0.5 <= score < 0.8),
                    'high': high_confidence_threats
                }
            },
            'risk_score': risk_score,
            'most_common_threat': max(threat_breakdown.items(), key=lambda x: x[1])[0] if threat_breakdown else None,
            'highest_severity': max(severity_distribution.items(), key=lambda x: x[1])[0] if severity_distribution else None
        }
    
    def _calculate_risk_score(self, events: List[SecurityEvent]) -> float:
        """Calculate overall risk score based on events"""
        if not events:
            return 0.0
        
        # Severity weights
        severity_weights = {
            SeverityLevel.LOW: 1.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.CRITICAL: 4.0
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for event in events:
            weight = severity_weights.get(event.severity, 1.0)
            score = event.confidence * weight
            total_score += score
            total_weight += weight
        
        return (total_score / total_weight) if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, events: List[SecurityEvent], threat_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if not events:
            recommendations.append("No security threats detected. Continue monitoring for best practices.")
            return recommendations
        
        # Risk-based recommendations
        risk_score = threat_analysis.get('risk_score', 0.0)
        if risk_score > 0.7:
            recommendations.append("HIGH RISK: Immediate action required. Review all security events and implement additional safeguards.")
        elif risk_score > 0.4:
            recommendations.append("MEDIUM RISK: Review security events and consider implementing additional monitoring.")
        else:
            recommendations.append("LOW RISK: Standard monitoring sufficient. Continue with current security practices.")
        
        # Threat-specific recommendations
        threat_breakdown = threat_analysis.get('threat_breakdown', {})
        
        if 'sql_injection' in threat_breakdown:
            recommendations.append("SQL Injection detected: Implement input validation and parameterized queries.")
        
        if 'xss_attack' in threat_breakdown:
            recommendations.append("XSS Attack detected: Sanitize user inputs and implement Content Security Policy.")
        
        if 'prompt_injection' in threat_breakdown:
            recommendations.append("Prompt Injection detected: Implement prompt validation and rate limiting.")
        
        if 'command_injection' in threat_breakdown:
            recommendations.append("Command Injection detected: Avoid shell execution and implement strict input validation.")
        
        # Confidence-based recommendations
        confidence_analysis = threat_analysis.get('confidence_analysis', {})
        high_confidence_threats = confidence_analysis.get('high_confidence_threats', 0)
        
        if high_confidence_threats > 0:
            recommendations.append(f"High-confidence threats detected ({high_confidence_threats}): Prioritize these for immediate investigation.")
        
        # Performance recommendations
        if len(events) > 10:
            recommendations.append("High event volume: Consider implementing automated response mechanisms.")
        
        return recommendations
    
    def _create_summary(self, events: List[SecurityEvent], metrics: Dict[str, Any], threat_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of monitoring session"""
        total_events = len(events)
        risk_score = threat_analysis.get('risk_score', 0.0)
        
        # Determine overall status
        if risk_score > 0.7:
            status = "CRITICAL"
        elif risk_score > 0.4:
            status = "WARNING"
        elif total_events > 0:
            status = "ATTENTION"
        else:
            status = "CLEAN"
        
        return {
            'status': status,
            'total_security_events': total_events,
            'risk_score': risk_score,
            'monitoring_duration': metrics.get('uptime_seconds', 0),
            'threats_blocked': metrics.get('total_events', 0),
            'detection_rate': metrics.get('detection_rate', 100.0),
            'most_critical_threat': threat_analysis.get('highest_severity'),
            'recommendations_count': len(self._generate_recommendations(events, threat_analysis))
        }
    
    def _save_report(self, report: UnifiedReport) -> None:
        """Save unified report to file"""
        try:
            # Convert report to JSON-serializable format
            report_data = {
                'metadata': {
                    'agent_id': report.agent_id,
                    'generated_at': report.end_time.isoformat(),
                    'monitoring_start': report.start_time.isoformat(),
                    'report_version': '1.0'
                },
                'summary': report.summary,
                'threat_analysis': report.threat_analysis,
                'recommendations': report.recommendations,
                'performance_metrics': report.performance_metrics,
                'security_events': [
                    {
                        'event_id': event.event_id,
                        'timestamp': event.timestamp.isoformat(),
                        'threat_type': event.threat_type.value,
                        'severity': event.severity.value,
                        'confidence': event.confidence,
                        'message': event.message,
                        'context': event.context
                    }
                    for event in report.security_events
                ],
                'session_logs': report.session_logs
            }
            
            with open(self.report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.logger.info(f"Unified report saved to: {self.report_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving unified report: {e}")
    
    def get_report_path(self) -> Path:
        """Get the path where the report was saved"""
        return self.report_file 