"""
Threat Report Generator

Generates focused threat analysis reports with security insights,
risk assessments, and actionable recommendations.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import requests

from .types import SecurityEvent
from .constants import ThreatType, SeverityLevel


@dataclass
class ThreatReport:
    """Focused threat analysis report"""
    agent_id: str
    report_id: str
    generated_at: datetime
    time_range: Dict[str, datetime]
    threat_summary: Dict[str, Any]
    security_events: List[SecurityEvent]
    risk_assessment: Dict[str, Any]
    threat_analysis: Dict[str, Any]
    recommendations: List[str]
    compliance_check: Dict[str, Any]
    executive_summary: str


class ThreatReportGenerator:
    """
    Generates focused threat analysis reports
    """
    
    def __init__(
        self,
        agent_id: str,
        report_file: Optional[str] = None,
        report_format: str = "json",  # "json", "html", "pdf"
        include_executive_summary: bool = True,
        include_compliance: bool = True,
        include_recommendations: bool = True
    ):
        """
        Initialize threat report generator
        
        Args:
            agent_id: Agent identifier
            report_file: Path to report file (auto-generated if None)
            report_format: Output format ("json", "html", "pdf")
            include_executive_summary: Include executive summary
            include_compliance: Include compliance checks
            include_recommendations: Include actionable recommendations
        """
        self.agent_id = agent_id
        self.report_format = report_format
        self.include_executive_summary = include_executive_summary
        self.include_compliance = include_compliance
        self.include_recommendations = include_recommendations
        
        # Set up report file
        if report_file:
            self.report_file = Path(report_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.report_file = Path(f"reports/{agent_id}_threat_report_{timestamp}.{report_format}")
        
        # Ensure reports directory exists
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"threat_report_generator.{agent_id}")
    
    def generate_threat_report(
        self,
        events: List[SecurityEvent],
        time_range: Optional[Dict[str, datetime]] = None
    ) -> ThreatReport:
        """
        Generate comprehensive threat report
        
        Args:
            events: Security events to analyze
            time_range: Time range for the report
            
        Returns:
            ThreatReport with detailed analysis
        """
        if not time_range:
            time_range = {
                "start": datetime.now(timezone.utc),
                "end": datetime.now(timezone.utc)
            }
        
        report_id = f"threat_report_{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate threat summary
        threat_summary = self._generate_threat_summary(events)
        
        # Perform risk assessment
        risk_assessment = self._perform_risk_assessment(events)
        
        # Analyze threats in detail
        threat_analysis = self._analyze_threats_detailed(events)
        
        # Generate recommendations
        recommendations = []
        if self.include_recommendations:
            recommendations = self._generate_recommendations(events, risk_assessment)
        
        # Compliance check
        compliance_check = {}
        if self.include_compliance:
            compliance_check = self._check_compliance(events)
        
        # Executive summary
        executive_summary = ""
        if self.include_executive_summary:
            executive_summary = self._generate_executive_summary(events, risk_assessment)
        
        report = ThreatReport(
            agent_id=self.agent_id,
            report_id=report_id,
            generated_at=datetime.now(timezone.utc),
            time_range=time_range,
            threat_summary=threat_summary,
            security_events=events,
            risk_assessment=risk_assessment,
            threat_analysis=threat_analysis,
            recommendations=recommendations,
            compliance_check=compliance_check,
            executive_summary=executive_summary
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_threat_summary(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Generate high-level threat summary"""
        if not events:
            return {
                "total_threats": 0,
                "threat_level": "LOW",
                "most_common_threat": None,
                "highest_severity": None,
                "time_distribution": {}
            }
        
        # Count threats by type
        threat_counts = {}
        severity_counts = {}
        time_distribution = {}
        
        for event in events:
            # Threat type counts
            threat_type = event.threat_type.value
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
            
            # Severity counts
            severity = event.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Time distribution (by hour)
            hour = event.timestamp.hour
            time_distribution[hour] = time_distribution.get(hour, 0) + 1
        
        # Determine overall threat level
        threat_level = self._calculate_threat_level(events)
        
        return {
            "total_threats": len(events),
            "threat_level": threat_level,
            "threat_breakdown": threat_counts,
            "severity_breakdown": severity_counts,
            "most_common_threat": max(threat_counts.items(), key=lambda x: x[1])[0] if threat_counts else None,
            "highest_severity": max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else None,
            "time_distribution": time_distribution
        }
    
    def _perform_risk_assessment(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        if not events:
            return {
                "overall_risk_score": 0.0,
                "risk_level": "LOW",
                "risk_factors": [],
                "trend_analysis": "STABLE"
            }
        
        # Calculate risk scores
        risk_scores = []
        risk_factors = []
        
        for event in events:
            # Base risk score based on severity and confidence
            base_score = event.confidence * self._severity_to_weight(event.severity)
            
            # Additional risk factors
            if event.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                risk_factors.append(f"High severity {event.threat_type.value} detected")
            
            if event.confidence >= 0.9:
                risk_factors.append(f"High confidence threat: {event.threat_type.value}")
            
            risk_scores.append(base_score)
        
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Determine risk level
        risk_level = self._score_to_risk_level(overall_risk_score)
        
        # Trend analysis (simplified - would need historical data for real trends)
        trend_analysis = "INCREASING" if len(events) > 10 else "STABLE"
        
        return {
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "risk_factors": list(set(risk_factors)),  # Remove duplicates
            "trend_analysis": trend_analysis,
            "risk_distribution": {
                "low": sum(1 for score in risk_scores if score < 2.0),
                "medium": sum(1 for score in risk_scores if 2.0 <= score < 3.0),
                "high": sum(1 for score in risk_scores if score >= 3.0)
            }
        }
    
    def _analyze_threats_detailed(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Perform detailed threat analysis"""
        if not events:
            return {
                "threat_patterns": {},
                "attack_vectors": {},
                "vulnerability_analysis": {},
                "threat_intelligence": {}
            }
        
        # Analyze threat patterns
        threat_patterns = {}
        attack_vectors = {}
        vulnerability_analysis = {}
        
        for event in events:
            threat_type = event.threat_type.value
            
            # Pattern analysis
            if threat_type not in threat_patterns:
                threat_patterns[threat_type] = {
                    "count": 0,
                    "severities": [],
                    "confidences": [],
                    "timestamps": []
                }
            
            threat_patterns[threat_type]["count"] += 1
            threat_patterns[threat_type]["severities"].append(event.severity.value)
            threat_patterns[threat_type]["confidences"].append(event.confidence)
            threat_patterns[threat_type]["timestamps"].append(event.timestamp.isoformat())
            
            # Attack vector analysis
            attack_vector = self._determine_attack_vector(event)
            attack_vectors[attack_vector] = attack_vectors.get(attack_vector, 0) + 1
            
            # Vulnerability analysis
            vulnerability = self._identify_vulnerability(event)
            if vulnerability:
                vulnerability_analysis[vulnerability] = vulnerability_analysis.get(vulnerability, 0) + 1
        
        # Threat intelligence (simplified)
        threat_intelligence = {
            "known_threats": len([e for e in events if e.confidence > 0.8]),
            "novel_threats": len([e for e in events if e.confidence < 0.5]),
            "threat_sources": self._identify_threat_sources(events)
        }
        
        return {
            "threat_patterns": threat_patterns,
            "attack_vectors": attack_vectors,
            "vulnerability_analysis": vulnerability_analysis,
            "threat_intelligence": threat_intelligence
        }
    
    def _generate_recommendations(self, events: List[SecurityEvent], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not events:
            recommendations.append("No threats detected. Continue monitoring for potential security issues.")
            return recommendations
        
        # Risk-based recommendations
        risk_level = risk_assessment.get("risk_level", "LOW")
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendations.append("IMMEDIATE ACTION REQUIRED: High risk level detected. Review all security events and implement additional monitoring.")
        
        # Threat-specific recommendations
        threat_types = set(event.threat_type.value for event in events)
        
        if ThreatType.DATA_EXFILTRATION.value in threat_types:
            recommendations.append("Implement data loss prevention (DLP) controls and monitor data access patterns.")
        
        if ThreatType.COMMAND_INJECTION.value in threat_types:
            recommendations.append("Strengthen input validation and implement command execution restrictions.")
        
        if ThreatType.PRIVILEGE_ESCALATION.value in threat_types:
            recommendations.append("Review and restrict agent permissions. Implement principle of least privilege.")
        
        if ThreatType.BEHAVIORAL_ANOMALY.value in threat_types:
            recommendations.append("Enhance behavioral monitoring and establish baseline patterns for normal agent behavior.")
        
        # Performance recommendations
        high_severity_count = len([e for e in events if e.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]])
        if high_severity_count > 5:
            recommendations.append("Consider implementing automated threat response and alerting systems.")
        
        # General recommendations
        recommendations.append("Regularly review and update security policies and monitoring rules.")
        recommendations.append("Implement comprehensive logging and audit trails for all agent activities.")
        recommendations.append("Consider integrating with external threat intelligence feeds for enhanced detection.")
        
        return recommendations
    
    def _check_compliance(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Check compliance with security standards"""
        compliance_results = {
            "overall_compliance": "COMPLIANT",
            "standards": {
                "data_protection": "COMPLIANT",
                "access_control": "COMPLIANT",
                "audit_logging": "COMPLIANT",
                "incident_response": "COMPLIANT"
            },
            "violations": [],
            "recommendations": []
        }
        
        if not events:
            return compliance_results
        
        # Check for compliance violations
        critical_events = [e for e in events if e.severity == SeverityLevel.CRITICAL]
        if critical_events:
            compliance_results["overall_compliance"] = "NON_COMPLIANT"
            compliance_results["standards"]["incident_response"] = "NON_COMPLIANT"
            compliance_results["violations"].append("Critical security events detected without immediate response")
        
        data_events = [e for e in events if e.threat_type == ThreatType.DATA_EXFILTRATION]
        if data_events:
            compliance_results["standards"]["data_protection"] = "NON_COMPLIANT"
            compliance_results["violations"].append("Data exfiltration attempts detected")
        
        privilege_events = [e for e in events if e.threat_type == ThreatType.PRIVILEGE_ESCALATION]
        if privilege_events:
            compliance_results["standards"]["access_control"] = "NON_COMPLIANT"
            compliance_results["violations"].append("Privilege escalation attempts detected")
        
        # Generate compliance recommendations
        if compliance_results["violations"]:
            compliance_results["recommendations"].append("Implement immediate remediation for detected violations")
            compliance_results["recommendations"].append("Review and update security controls")
            compliance_results["recommendations"].append("Conduct security awareness training")
        
        return compliance_results
    
    def _generate_executive_summary(self, events: List[SecurityEvent], risk_assessment: Dict[str, Any]) -> str:
        """Generate executive summary for non-technical stakeholders"""
        if not events:
            return f"Security monitoring for agent '{self.agent_id}' shows no threats detected. The system is operating securely with low risk levels."
        
        total_threats = len(events)
        risk_level = risk_assessment.get("risk_level", "LOW")
        risk_score = risk_assessment.get("overall_risk_score", 0.0)
        
        critical_events = len([e for e in events if e.severity == SeverityLevel.CRITICAL])
        high_events = len([e for e in events if e.severity == SeverityLevel.HIGH])
        
        summary = f"Security monitoring for agent '{self.agent_id}' detected {total_threats} security events "
        summary += f"with an overall risk level of {risk_level} (score: {risk_score:.2f}). "
        
        if critical_events > 0:
            summary += f"CRITICAL: {critical_events} critical security events require immediate attention. "
        
        if high_events > 0:
            summary += f"High severity events: {high_events}. "
        
        if risk_level in ["LOW", "MEDIUM"]:
            summary += "The system is operating within acceptable security parameters."
        else:
            summary += "IMMEDIATE ACTION REQUIRED: Security review and remediation needed."
        
        return summary
    
    def _calculate_threat_level(self, events: List[SecurityEvent]) -> str:
        """Calculate overall threat level"""
        if not events:
            return "LOW"
        
        critical_count = len([e for e in events if e.severity == SeverityLevel.CRITICAL])
        high_count = len([e for e in events if e.severity == SeverityLevel.HIGH])
        
        if critical_count > 0:
            return "CRITICAL"
        elif high_count > 2:
            return "HIGH"
        elif high_count > 0 or len(events) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _severity_to_weight(self, severity: SeverityLevel) -> float:
        """Convert severity to weight for risk calculation"""
        return {
            SeverityLevel.LOW: 1.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.CRITICAL: 4.0
        }.get(severity, 1.0)
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score >= 3.5:
            return "CRITICAL"
        elif score >= 2.5:
            return "HIGH"
        elif score >= 1.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_attack_vector(self, event: SecurityEvent) -> str:
        """Determine the attack vector for a security event"""
        if event.threat_type == ThreatType.COMMAND_INJECTION:
            return "Command Injection"
        elif event.threat_type == ThreatType.DATA_EXFILTRATION:
            return "Data Exfiltration"
        elif event.threat_type == ThreatType.PRIVILEGE_ESCALATION:
            return "Privilege Escalation"
        elif event.threat_type == ThreatType.BEHAVIORAL_ANOMALY:
            return "Behavioral Anomaly"
        else:
            return "Unknown"
    
    def _identify_vulnerability(self, event: SecurityEvent) -> Optional[str]:
        """Identify potential vulnerability from security event"""
        if event.threat_type == ThreatType.COMMAND_INJECTION:
            return "Input Validation"
        elif event.threat_type == ThreatType.DATA_EXFILTRATION:
            return "Data Access Control"
        elif event.threat_type == ThreatType.PRIVILEGE_ESCALATION:
            return "Permission Management"
        else:
            return None
    
    def _identify_threat_sources(self, events: List[SecurityEvent]) -> List[str]:
        """Identify potential threat sources"""
        sources = []
        
        for event in events:
            if event.threat_type == ThreatType.COMMAND_INJECTION:
                sources.append("Malicious Input")
            elif event.threat_type == ThreatType.DATA_EXFILTRATION:
                sources.append("Data Access Abuse")
            elif event.threat_type == ThreatType.PRIVILEGE_ESCALATION:
                sources.append("Permission Exploitation")
        
        return list(set(sources))  # Remove duplicates
    
    def _save_report(self, report: ThreatReport) -> None:
        """Save report to file"""
        try:
            if self.report_format == "json":
                with open(self.report_file, 'w') as f:
                    json.dump(report.__dict__, f, default=str, indent=2)
            elif self.report_format == "html":
                html_content = self._generate_html_report(report)
                with open(self.report_file, 'w') as f:
                    f.write(html_content)
            else:
                # Default to JSON
                with open(self.report_file, 'w') as f:
                    json.dump(report.__dict__, f, default=str, indent=2)
            
            self.logger.info(f"Threat report saved to {self.report_file}")
        except Exception as e:
            self.logger.error(f"Error saving threat report: {e}")
    
    def _generate_html_report(self, report: ThreatReport) -> str:
        """Generate HTML version of the threat report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Threat Report - {report.agent_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .critical {{ background-color: #ffebee; border-color: #f44336; }}
                .high {{ background-color: #fff3e0; border-color: #ff9800; }}
                .medium {{ background-color: #fff8e1; border-color: #ffc107; }}
                .low {{ background-color: #e8f5e8; border-color: #4caf50; }}
                .recommendation {{ background-color: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Threat Report - {report.agent_id}</h1>
                <p>Generated: {report.generated_at}</p>
                <p>Report ID: {report.report_id}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{report.executive_summary}</p>
            </div>
            
            <div class="section">
                <h2>Threat Summary</h2>
                <p>Total Threats: {report.threat_summary['total_threats']}</p>
                <p>Threat Level: {report.threat_summary['threat_level']}</p>
            </div>
            
            <div class="section">
                <h2>Risk Assessment</h2>
                <p>Risk Level: {report.risk_assessment['risk_level']}</p>
                <p>Risk Score: {report.risk_assessment['overall_risk_score']:.2f}</p>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {''.join(f'<div class="recommendation">{rec}</div>' for rec in report.recommendations)}
            </div>
        </body>
        </html>
        """
        return html
    
    def get_report_path(self) -> Path:
        """Get the path to the generated report"""
        return self.report_file 