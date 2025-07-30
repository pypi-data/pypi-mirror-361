"""
Advanced Behavioral Analysis System for Agent Sentinel

This module implements sophisticated behavioral analysis capabilities for AI agents,
including agent fingerprinting, usage pattern analysis, anomaly detection, and
behavioral threat identification.

Enterprise-grade features:
- Agent fingerprinting and profiling
- Usage pattern analysis and baseline establishment
- Behavioral anomaly detection with ML-based scoring
- Cross-session behavioral correlation
- Adaptive threat detection based on behavioral patterns
- Support for all agent types (A2A, MCP, autonomous agents)
"""

import asyncio
import hashlib
import json
import statistics
import time
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import numpy as np
from pathlib import Path

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..core.exceptions import AgentSentinelError
from ..logging.structured_logger import SecurityLogger


class BehavioralAnomalyType(Enum):
    """Types of behavioral anomalies that can be detected."""
    USAGE_PATTERN_DEVIATION = "usage_pattern_deviation"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    TIMING_ANOMALY = "timing_anomaly"
    SEQUENCE_ANOMALY = "sequence_anomaly"
    PARAMETER_ANOMALY = "parameter_anomaly"
    RESOURCE_USAGE_ANOMALY = "resource_usage_anomaly"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNUSUAL_DATA_ACCESS = "unusual_data_access"
    SUSPICIOUS_TOOL_USAGE = "suspicious_tool_usage"
    COMMUNICATION_PATTERN_ANOMALY = "communication_pattern_anomaly"


class AgentType(Enum):
    """Types of AI agents that can be monitored."""
    AUTONOMOUS_AGENT = "autonomous_agent"
    A2A_AGENT = "a2a_agent"  # Agent-to-Agent
    MCP_AGENT = "mcp_agent"  # Model Context Protocol
    CHATBOT = "chatbot"
    WORKFLOW_AGENT = "workflow_agent"
    TOOL_AGENT = "tool_agent"
    ORCHESTRATOR = "orchestrator"
    UNKNOWN = "unknown"


@dataclass
class AgentFingerprint:
    """Comprehensive agent fingerprint for identification and analysis."""
    agent_id: str
    agent_type: AgentType
    creation_time: datetime
    last_seen: datetime
    
    # Behavioral characteristics
    method_usage_patterns: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    parameter_patterns: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    timing_patterns: Dict[str, float] = field(default_factory=dict)
    sequence_patterns: List[str] = field(default_factory=list)
    resource_usage_patterns: Dict[str, float] = field(default_factory=dict)
    
    # Communication patterns (for A2A and MCP agents)
    communication_patterns: Dict[str, Any] = field(default_factory=dict)
    tool_usage_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Statistical baselines
    baseline_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    confidence_score: float = 0.0
    
    # Metadata
    environment: str = "unknown"
    version: str = "unknown"
    capabilities: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fingerprint to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "creation_time": self.creation_time.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "method_usage_patterns": self.method_usage_patterns,
            "parameter_patterns": self.parameter_patterns,
            "timing_patterns": self.timing_patterns,
            "sequence_patterns": self.sequence_patterns,
            "resource_usage_patterns": self.resource_usage_patterns,
            "communication_patterns": self.communication_patterns,
            "tool_usage_patterns": self.tool_usage_patterns,
            "baseline_metrics": self.baseline_metrics,
            "confidence_score": self.confidence_score,
            "environment": self.environment,
            "version": self.version,
            "capabilities": list(self.capabilities)
        }


@dataclass
class BehavioralEvent:
    """Represents a behavioral event for analysis."""
    timestamp: datetime
    agent_id: str
    method_name: str
    parameters: Dict[str, Any]
    execution_time: float
    result_type: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "method_name": self.method_name,
            "parameters": self.parameters,
            "execution_time": self.execution_time,
            "result_type": self.result_type,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "context": self.context
        }


@dataclass
class BehavioralAnomaly:
    """Represents a detected behavioral anomaly."""
    anomaly_type: BehavioralAnomalyType
    severity: SeverityLevel
    confidence: float
    description: str
    agent_id: str
    timestamp: datetime
    evidence: Dict[str, Any]
    baseline_deviation: float
    risk_score: float
    
    def to_security_event(self) -> SecurityEvent:
        """Convert anomaly to security event."""
        return SecurityEvent(
            threat_type=ThreatType.BEHAVIORAL_ANOMALY,
            severity=self.severity,
            message=self.description,
            confidence=self.confidence,
            context={
                "anomaly_type": self.anomaly_type.value,
                "evidence": self.evidence,
                "baseline_deviation": self.baseline_deviation,
                "risk_score": self.risk_score
            },
            agent_id=self.agent_id,
            timestamp=self.timestamp,
            detection_method="behavioral_analysis"
        )


class BehavioralAnalyzer:
    """
    Advanced behavioral analysis system for AI agents.
    
    This system provides comprehensive behavioral monitoring and analysis,
    including agent fingerprinting, pattern recognition, and anomaly detection.
    
    Key Features:
    - Agent fingerprinting and profiling
    - Usage pattern analysis and baseline establishment
    - Real-time behavioral anomaly detection
    - Cross-session behavioral correlation
    - Adaptive threat detection
    - Support for all agent types (A2A, MCP, autonomous)
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        baseline_window: int = 100,  # Events to establish baseline
        anomaly_threshold: float = 2.0,  # Standard deviations for anomaly
        max_events_memory: int = 10000,
        enable_ml_detection: bool = True,
        persistence_path: Optional[Path] = None
    ):
        """
        Initialize behavioral analyzer.
        
        Args:
            agent_id: ID of the agent being analyzed
            logger: Security logger instance
            baseline_window: Number of events to establish behavioral baseline
            anomaly_threshold: Threshold for anomaly detection (std deviations)
            max_events_memory: Maximum events to keep in memory
            enable_ml_detection: Enable ML-based anomaly detection
            persistence_path: Path to persist behavioral data
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"behavioral_analyzer_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        
        # Configuration
        self.baseline_window = baseline_window
        self.anomaly_threshold = anomaly_threshold
        self.max_events_memory = max_events_memory
        self.enable_ml_detection = enable_ml_detection
        self.persistence_path = persistence_path
        
        # Agent fingerprint and behavioral data
        self.agent_fingerprint: Optional[AgentFingerprint] = None
        self.behavioral_events: deque = deque(maxlen=max_events_memory)
        self.baseline_established = False
        
        # Pattern analysis data structures
        self.method_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.timing_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.sequence_patterns: deque = deque(maxlen=50)
        self.parameter_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Anomaly detection state
        self.detected_anomalies: List[BehavioralAnomaly] = []
        self.anomaly_callbacks: List[Callable[[BehavioralAnomaly], None]] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Load persisted data if available
        self._load_behavioral_data()
        
        self.logger.info(f"Behavioral analyzer initialized for agent {agent_id}")
    
    def detect_agent_type(self, context: Dict[str, Any]) -> AgentType:
        """
        Detect the type of agent based on behavioral patterns and context.
        
        Args:
            context: Context information about the agent
            
        Returns:
            Detected agent type
        """
        # Check for explicit agent type indicators
        if "agent_type" in context:
            try:
                return AgentType(context["agent_type"])
            except ValueError:
                pass
        
        # Analyze behavioral patterns to infer agent type
        if not self.behavioral_events:
            return AgentType.UNKNOWN
        
        # Analyze method patterns
        method_names = [event.method_name for event in self.behavioral_events]
        method_frequency = defaultdict(int)
        for method in method_names:
            method_frequency[method] += 1
        
        # A2A agents typically have communication-focused methods
        a2a_indicators = ["send_message", "receive_message", "communicate", "negotiate", "collaborate"]
        a2a_score = sum(method_frequency.get(method, 0) for method in a2a_indicators)
        
        # MCP agents have protocol-specific methods
        mcp_indicators = ["handle_request", "process_context", "update_context", "mcp_call"]
        mcp_score = sum(method_frequency.get(method, 0) for method in mcp_indicators)
        
        # Tool agents focus on specific tool usage
        tool_indicators = ["execute_tool", "use_tool", "tool_call", "api_call"]
        tool_score = sum(method_frequency.get(method, 0) for method in tool_indicators)
        
        # Autonomous agents have decision-making methods
        autonomous_indicators = ["make_decision", "plan", "execute", "evaluate", "adapt"]
        autonomous_score = sum(method_frequency.get(method, 0) for method in autonomous_indicators)
        
        # Determine agent type based on highest score
        scores = {
            AgentType.A2A_AGENT: a2a_score,
            AgentType.MCP_AGENT: mcp_score,
            AgentType.TOOL_AGENT: tool_score,
            AgentType.AUTONOMOUS_AGENT: autonomous_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return AgentType.UNKNOWN
    
    def create_agent_fingerprint(self, context: Dict[str, Any]) -> AgentFingerprint:
        """
        Create a comprehensive fingerprint for the agent.
        
        Args:
            context: Context information about the agent
            
        Returns:
            Agent fingerprint
        """
        with self.lock:
            now = datetime.now(timezone.utc)
            
            # Detect agent type
            agent_type = self.detect_agent_type(context)
            
            # Create fingerprint
            fingerprint = AgentFingerprint(
                agent_id=self.agent_id,
                agent_type=agent_type,
                creation_time=now,
                last_seen=now,
                environment=context.get("environment", "unknown"),
                version=context.get("version", "unknown")
            )
            
            # Extract capabilities from context
            if "capabilities" in context:
                fingerprint.capabilities = set(context["capabilities"])
            
            # Analyze behavioral patterns if we have enough data
            if len(self.behavioral_events) >= self.baseline_window:
                fingerprint.method_usage_patterns = self._analyze_method_patterns()
                fingerprint.parameter_patterns = self._analyze_parameter_patterns()
                fingerprint.timing_patterns = self._analyze_timing_patterns()
                fingerprint.sequence_patterns = self._analyze_sequence_patterns()
                fingerprint.resource_usage_patterns = self._analyze_resource_patterns()
                fingerprint.communication_patterns = self._analyze_communication_patterns()
                fingerprint.tool_usage_patterns = self._analyze_tool_patterns()
                fingerprint.baseline_metrics = self._calculate_baseline_metrics()
                fingerprint.confidence_score = self._calculate_fingerprint_confidence()
            
            self.agent_fingerprint = fingerprint
            self.logger.info(f"Created agent fingerprint for {self.agent_id} (type: {agent_type.value})")
            
            return fingerprint
    
    def record_behavioral_event(
        self,
        method_name: str,
        parameters: Dict[str, Any],
        execution_time: float,
        result_type: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a behavioral event for analysis.
        
        Args:
            method_name: Name of the method called
            parameters: Method parameters
            execution_time: Time taken to execute
            result_type: Type of result returned
            session_id: Session identifier
            user_id: User identifier
            context: Additional context
        """
        with self.lock:
            event = BehavioralEvent(
                timestamp=datetime.now(timezone.utc),
                agent_id=self.agent_id,
                method_name=method_name,
                parameters=self._sanitize_parameters(parameters),
                execution_time=execution_time,
                result_type=result_type,
                session_id=session_id,
                user_id=user_id,
                context=context or {}
            )
            
            self.behavioral_events.append(event)
            
            # Update patterns
            self._update_method_patterns(event)
            self._update_timing_patterns(event)
            self._update_sequence_patterns(event)
            self._update_parameter_patterns(event)
            
            # Check for anomalies if baseline is established
            if self.baseline_established:
                anomalies = self._detect_anomalies(event)
                for anomaly in anomalies:
                    self._handle_anomaly(anomaly)
            
            # Establish baseline if we have enough events
            if not self.baseline_established and len(self.behavioral_events) >= self.baseline_window:
                self._establish_baseline()
    
    def analyze_behavioral_patterns(self) -> Dict[str, Any]:
        """
        Analyze current behavioral patterns.
        
        Returns:
            Comprehensive behavioral analysis
        """
        with self.lock:
            if not self.behavioral_events:
                return {"status": "no_data", "message": "No behavioral events recorded"}
            
            analysis = {
                "agent_id": self.agent_id,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "total_events": len(self.behavioral_events),
                "baseline_established": self.baseline_established,
                "agent_fingerprint": self.agent_fingerprint.to_dict() if self.agent_fingerprint else None,
                "patterns": {
                    "method_patterns": self._analyze_method_patterns(),
                    "timing_patterns": self._analyze_timing_patterns(),
                    "sequence_patterns": self._analyze_sequence_patterns(),
                    "parameter_patterns": self._analyze_parameter_patterns(),
                    "resource_patterns": self._analyze_resource_patterns(),
                    "communication_patterns": self._analyze_communication_patterns(),
                    "tool_patterns": self._analyze_tool_patterns()
                },
                "anomalies": {
                    "total_detected": len(self.detected_anomalies),
                    "recent_anomalies": [
                        anomaly.__dict__ for anomaly in self.detected_anomalies[-10:]
                    ],
                    "anomaly_types": self._get_anomaly_type_distribution()
                },
                "risk_assessment": self._calculate_risk_assessment(),
                "recommendations": self._generate_recommendations()
            }
            
            return analysis
    
    def detect_anomalies(self, event: BehavioralEvent) -> List[BehavioralAnomaly]:
        """
        Detect behavioral anomalies in the given event.
        
        Args:
            event: Behavioral event to analyze
            
        Returns:
            List of detected anomalies
        """
        if not self.baseline_established:
            return []
        
        return self._detect_anomalies(event)
    
    def _detect_anomalies(self, event: BehavioralEvent) -> List[BehavioralAnomaly]:
        """Internal method to detect anomalies."""
        anomalies = []
        
        # Timing anomaly detection
        timing_anomaly = self._detect_timing_anomaly(event)
        if timing_anomaly:
            anomalies.append(timing_anomaly)
        
        # Frequency anomaly detection
        frequency_anomaly = self._detect_frequency_anomaly(event)
        if frequency_anomaly:
            anomalies.append(frequency_anomaly)
        
        # Sequence anomaly detection
        sequence_anomaly = self._detect_sequence_anomaly(event)
        if sequence_anomaly:
            anomalies.append(sequence_anomaly)
        
        # Parameter anomaly detection
        parameter_anomaly = self._detect_parameter_anomaly(event)
        if parameter_anomaly:
            anomalies.append(parameter_anomaly)
        
        # Resource usage anomaly detection
        resource_anomaly = self._detect_resource_anomaly(event)
        if resource_anomaly:
            anomalies.append(resource_anomaly)
        
        # Communication pattern anomaly (for A2A/MCP agents)
        if self.agent_fingerprint and self.agent_fingerprint.agent_type in [AgentType.A2A_AGENT, AgentType.MCP_AGENT]:
            comm_anomaly = self._detect_communication_anomaly(event)
            if comm_anomaly:
                anomalies.append(comm_anomaly)
        
        return anomalies
    
    def _detect_timing_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect timing-based anomalies."""
        method_timings = self.timing_patterns.get(event.method_name, deque())
        
        if len(method_timings) < 10:  # Need enough data for baseline
            return None
        
        # Calculate baseline statistics
        timings_list = list(method_timings)
        mean_time = statistics.mean(timings_list)
        std_time = statistics.stdev(timings_list) if len(timings_list) > 1 else 0
        
        if std_time == 0:
            return None
        
        # Check for anomaly
        z_score = abs(event.execution_time - mean_time) / std_time
        
        if z_score > self.anomaly_threshold:
            severity = SeverityLevel.HIGH if z_score > 3.0 else SeverityLevel.MEDIUM
            confidence = min(0.95, z_score / 5.0)  # Cap at 95%
            
            return BehavioralAnomaly(
                anomaly_type=BehavioralAnomalyType.TIMING_ANOMALY,
                severity=severity,
                confidence=confidence,
                description=f"Method {event.method_name} execution time ({event.execution_time:.3f}s) deviates significantly from baseline ({mean_time:.3f}s ± {std_time:.3f}s)",
                agent_id=self.agent_id,
                timestamp=event.timestamp,
                evidence={
                    "method_name": event.method_name,
                    "execution_time": event.execution_time,
                    "baseline_mean": mean_time,
                    "baseline_std": std_time,
                    "z_score": z_score
                },
                baseline_deviation=z_score,
                risk_score=self._calculate_timing_risk_score(z_score, severity)
            )
        
        return None
    
    def _detect_frequency_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect frequency-based anomalies."""
        # Analyze method call frequency in recent time windows
        now = event.timestamp
        recent_events = [
            e for e in self.behavioral_events 
            if (now - e.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        method_counts = defaultdict(int)
        for e in recent_events:
            method_counts[e.method_name] += 1
        
        # Get baseline frequency for this method
        baseline_frequency = self.method_patterns.get(event.method_name, {}).get("hourly_frequency", 0)
        
        if baseline_frequency == 0:
            return None
        
        current_frequency = method_counts[event.method_name]
        frequency_ratio = current_frequency / baseline_frequency
        
        # Check for significant deviation
        if frequency_ratio > 3.0 or frequency_ratio < 0.3:
            severity = SeverityLevel.HIGH if frequency_ratio > 5.0 or frequency_ratio < 0.1 else SeverityLevel.MEDIUM
            confidence = min(0.9, abs(1 - frequency_ratio))
            
            return BehavioralAnomaly(
                anomaly_type=BehavioralAnomalyType.FREQUENCY_ANOMALY,
                severity=severity,
                confidence=confidence,
                description=f"Method {event.method_name} frequency ({current_frequency}/hour) deviates from baseline ({baseline_frequency}/hour)",
                agent_id=self.agent_id,
                timestamp=event.timestamp,
                evidence={
                    "method_name": event.method_name,
                    "current_frequency": current_frequency,
                    "baseline_frequency": baseline_frequency,
                    "frequency_ratio": frequency_ratio
                },
                baseline_deviation=abs(1 - frequency_ratio),
                risk_score=self._calculate_frequency_risk_score(frequency_ratio, severity)
            )
        
        return None
    
    def _detect_sequence_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect sequence-based anomalies."""
        if len(self.sequence_patterns) < 5:
            return None
        
        # Get recent method sequence
        recent_sequence = [e.method_name for e in list(self.behavioral_events)[-5:]]
        
        # Check against known patterns
        sequence_str = " -> ".join(recent_sequence)
        
        # Simple pattern matching - in production, use more sophisticated sequence analysis
        known_patterns = self._get_known_sequences()
        
        if sequence_str not in known_patterns and len(recent_sequence) >= 3:
            # Check if this is a completely new sequence pattern
            similarity_score = self._calculate_sequence_similarity(recent_sequence, known_patterns)
            
            if similarity_score < 0.3:  # Low similarity to known patterns
                return BehavioralAnomaly(
                    anomaly_type=BehavioralAnomalyType.SEQUENCE_ANOMALY,
                    severity=SeverityLevel.MEDIUM,
                    confidence=1.0 - similarity_score,
                    description=f"Unusual method sequence detected: {sequence_str}",
                    agent_id=self.agent_id,
                    timestamp=event.timestamp,
                    evidence={
                        "sequence": recent_sequence,
                        "sequence_string": sequence_str,
                        "similarity_score": similarity_score,
                        "known_patterns": list(known_patterns)[:5]  # Sample of known patterns
                    },
                    baseline_deviation=1.0 - similarity_score,
                    risk_score=self._calculate_sequence_risk_score(similarity_score)
                )
        
        return None
    
    def _detect_parameter_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect parameter-based anomalies."""
        method_params = self.parameter_patterns.get(event.method_name, {})
        
        if not method_params:
            return None
        
        # Check parameter types and values
        anomalies_found = []
        
        for param_name, param_value in event.parameters.items():
            baseline_info = method_params.get(param_name, {})
            
            if not baseline_info:
                continue
            
            # Check parameter type
            expected_type = baseline_info.get("type")
            actual_type = type(param_value).__name__
            
            if expected_type and actual_type != expected_type:
                anomalies_found.append(f"Parameter {param_name} type mismatch: expected {expected_type}, got {actual_type}")
            
            # Check parameter value ranges for numeric types
            if isinstance(param_value, (int, float)):
                value_range = baseline_info.get("range", {})
                min_val = value_range.get("min")
                max_val = value_range.get("max")
                
                if min_val is not None and param_value < min_val:
                    anomalies_found.append(f"Parameter {param_name} value {param_value} below baseline minimum {min_val}")
                
                if max_val is not None and param_value > max_val:
                    anomalies_found.append(f"Parameter {param_name} value {param_value} above baseline maximum {max_val}")
        
        if anomalies_found:
            return BehavioralAnomaly(
                anomaly_type=BehavioralAnomalyType.PARAMETER_ANOMALY,
                severity=SeverityLevel.MEDIUM,
                confidence=0.8,
                description=f"Parameter anomalies detected in {event.method_name}: {'; '.join(anomalies_found)}",
                agent_id=self.agent_id,
                timestamp=event.timestamp,
                evidence={
                    "method_name": event.method_name,
                    "anomalies": anomalies_found,
                    "parameters": event.parameters,
                    "baseline_parameters": method_params
                },
                baseline_deviation=len(anomalies_found) / max(len(event.parameters), 1),
                risk_score=self._calculate_parameter_risk_score(len(anomalies_found))
            )
        
        return None
    
    def _detect_resource_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect resource usage anomalies."""
        # This would integrate with system monitoring to detect resource usage patterns
        # For now, we'll use execution time as a proxy for resource usage
        
        if event.execution_time > 30.0:  # Unusually long execution
            return BehavioralAnomaly(
                anomaly_type=BehavioralAnomalyType.RESOURCE_USAGE_ANOMALY,
                severity=SeverityLevel.HIGH,
                confidence=0.9,
                description=f"Excessive resource usage detected: {event.method_name} took {event.execution_time:.2f}s",
                agent_id=self.agent_id,
                timestamp=event.timestamp,
                evidence={
                    "method_name": event.method_name,
                    "execution_time": event.execution_time,
                    "threshold": 30.0
                },
                baseline_deviation=event.execution_time / 30.0,
                risk_score=min(1.0, event.execution_time / 60.0)  # Cap at 1 minute
            )
        
        return None
    
    def _detect_communication_anomaly(self, event: BehavioralEvent) -> Optional[BehavioralAnomaly]:
        """Detect communication pattern anomalies for A2A/MCP agents."""
        # Check for unusual communication patterns
        communication_methods = ["send_message", "receive_message", "communicate", "handle_request"]
        
        if event.method_name not in communication_methods:
            return None
        
        # Analyze communication frequency and patterns
        recent_comm_events = [
            e for e in self.behavioral_events 
            if e.method_name in communication_methods and 
            (event.timestamp - e.timestamp).total_seconds() < 300  # Last 5 minutes
        ]
        
        if len(recent_comm_events) > 100:  # Excessive communication
            return BehavioralAnomaly(
                anomaly_type=BehavioralAnomalyType.COMMUNICATION_PATTERN_ANOMALY,
                severity=SeverityLevel.HIGH,
                confidence=0.85,
                description=f"Excessive communication activity: {len(recent_comm_events)} communications in 5 minutes",
                agent_id=self.agent_id,
                timestamp=event.timestamp,
                evidence={
                    "communication_count": len(recent_comm_events),
                    "time_window": 300,
                    "method_name": event.method_name
                },
                baseline_deviation=len(recent_comm_events) / 50.0,  # Assume 50 is normal
                risk_score=min(1.0, len(recent_comm_events) / 200.0)
            )
        
        return None
    
    def _establish_baseline(self) -> None:
        """Establish behavioral baseline from collected events."""
        with self.lock:
            self.logger.info(f"Establishing behavioral baseline for agent {self.agent_id}")
            
            # Calculate baseline metrics
            self.method_patterns = self._analyze_method_patterns()
            
            # Mark baseline as established
            self.baseline_established = True
            
            self.logger.info(f"Behavioral baseline established for agent {self.agent_id}")
    
    def _analyze_method_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Analyze method usage patterns."""
        patterns = defaultdict(lambda: {
            "call_count": 0,
            "avg_execution_time": 0.0,
            "std_execution_time": 0.0,
            "hourly_frequency": 0.0,
            "success_rate": 1.0,
            "parameter_patterns": {}
        })
        
        # Group events by method
        method_events = defaultdict(list)
        for event in self.behavioral_events:
            method_events[event.method_name].append(event)
        
        # Calculate patterns for each method
        for method_name, events in method_events.items():
            pattern = patterns[method_name]
            pattern["call_count"] = len(events)
            
            # Timing statistics
            execution_times = [e.execution_time for e in events]
            pattern["avg_execution_time"] = statistics.mean(execution_times)
            if len(execution_times) > 1:
                pattern["std_execution_time"] = statistics.stdev(execution_times)
            
            # Frequency analysis
            if self.behavioral_events:
                time_span = (self.behavioral_events[-1].timestamp - self.behavioral_events[0].timestamp).total_seconds()
                if time_span > 0:
                    pattern["hourly_frequency"] = len(events) / (time_span / 3600)
        
        return dict(patterns)
    
    def _analyze_timing_patterns(self) -> Dict[str, float]:
        """Analyze timing patterns."""
        patterns = {}
        
        for method_name, timings in self.timing_patterns.items():
            if len(timings) > 0:
                patterns[method_name] = {
                    "mean": statistics.mean(timings),
                    "std": statistics.stdev(timings) if len(timings) > 1 else 0.0,
                    "min": min(timings),
                    "max": max(timings)
                }
        
        return patterns
    
    def _analyze_sequence_patterns(self) -> List[str]:
        """Analyze method sequence patterns."""
        sequences = []
        
        # Extract sequences of length 3-5
        for i in range(len(self.behavioral_events) - 2):
            sequence = [
                self.behavioral_events[i].method_name,
                self.behavioral_events[i + 1].method_name,
                self.behavioral_events[i + 2].method_name
            ]
            sequences.append(" -> ".join(sequence))
        
        # Return most common sequences
        sequence_counts = defaultdict(int)
        for seq in sequences:
            sequence_counts[seq] += 1
        
        return sorted(sequence_counts.keys(), key=sequence_counts.get, reverse=True)[:20]
    
    def _analyze_parameter_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Analyze parameter patterns."""
        patterns = defaultdict(lambda: defaultdict(dict))
        
        for event in self.behavioral_events:
            method_name = event.method_name
            
            for param_name, param_value in event.parameters.items():
                param_info = patterns[method_name][param_name]
                
                # Track parameter type
                param_type = type(param_value).__name__
                param_info["type"] = param_type
                
                # Track value ranges for numeric types
                if isinstance(param_value, (int, float)):
                    if "range" not in param_info:
                        param_info["range"] = {"min": param_value, "max": param_value}
                    else:
                        param_info["range"]["min"] = min(param_info["range"]["min"], param_value)
                        param_info["range"]["max"] = max(param_info["range"]["max"], param_value)
        
        return dict(patterns)
    
    def _analyze_resource_patterns(self) -> Dict[str, float]:
        """Analyze resource usage patterns."""
        patterns = {}
        
        if self.behavioral_events:
            execution_times = [e.execution_time for e in self.behavioral_events]
            patterns["avg_execution_time"] = statistics.mean(execution_times)
            patterns["max_execution_time"] = max(execution_times)
            patterns["total_execution_time"] = sum(execution_times)
        
        return patterns
    
    def _analyze_communication_patterns(self) -> Dict[str, Any]:
        """Analyze communication patterns for A2A/MCP agents."""
        patterns = {}
        
        communication_methods = ["send_message", "receive_message", "communicate", "handle_request"]
        comm_events = [e for e in self.behavioral_events if e.method_name in communication_methods]
        
        if comm_events:
            patterns["communication_frequency"] = len(comm_events) / max(len(self.behavioral_events), 1)
            patterns["avg_communication_time"] = statistics.mean([e.execution_time for e in comm_events])
        
        return patterns
    
    def _analyze_tool_patterns(self) -> Dict[str, Any]:
        """Analyze tool usage patterns."""
        patterns = {}
        
        tool_methods = ["execute_tool", "use_tool", "tool_call", "api_call"]
        tool_events = [e for e in self.behavioral_events if e.method_name in tool_methods]
        
        if tool_events:
            patterns["tool_usage_frequency"] = len(tool_events) / max(len(self.behavioral_events), 1)
            patterns["avg_tool_execution_time"] = statistics.mean([e.execution_time for e in tool_events])
        
        return patterns
    
    def _calculate_baseline_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate baseline metrics for anomaly detection."""
        metrics = {}
        
        # Method timing baselines
        for method_name, timings in self.timing_patterns.items():
            if len(timings) > 1:
                metrics[method_name] = {
                    "timing_mean": statistics.mean(timings),
                    "timing_std": statistics.stdev(timings)
                }
        
        return metrics
    
    def _calculate_fingerprint_confidence(self) -> float:
        """Calculate confidence score for agent fingerprint."""
        if not self.behavioral_events:
            return 0.0
        
        # Base confidence on amount of data and pattern consistency
        data_score = min(1.0, len(self.behavioral_events) / (self.baseline_window * 2))
        
        # Pattern consistency score (simplified)
        pattern_score = 0.8  # Would calculate based on pattern consistency
        
        return (data_score + pattern_score) / 2
    
    def _calculate_risk_assessment(self) -> Dict[str, Any]:
        """Calculate overall risk assessment."""
        if not self.detected_anomalies:
            return {"risk_level": "LOW", "risk_score": 0.0, "factors": []}
        
        # Calculate risk based on anomalies
        risk_scores = [anomaly.risk_score for anomaly in self.detected_anomalies]
        avg_risk = statistics.mean(risk_scores)
        max_risk = max(risk_scores)
        
        # Determine risk level
        if max_risk > 0.8:
            risk_level = "CRITICAL"
        elif max_risk > 0.6:
            risk_level = "HIGH"
        elif max_risk > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": max_risk,
            "average_risk": avg_risk,
            "total_anomalies": len(self.detected_anomalies),
            "factors": [anomaly.anomaly_type.value for anomaly in self.detected_anomalies[-5:]]
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on analysis."""
        recommendations = []
        
        if not self.baseline_established:
            recommendations.append("Continue monitoring to establish behavioral baseline")
        
        if self.detected_anomalies:
            anomaly_types = set(anomaly.anomaly_type for anomaly in self.detected_anomalies)
            
            if BehavioralAnomalyType.TIMING_ANOMALY in anomaly_types:
                recommendations.append("Investigate unusual execution times - possible performance issues or attacks")
            
            if BehavioralAnomalyType.FREQUENCY_ANOMALY in anomaly_types:
                recommendations.append("Review method call frequency patterns - possible automated attacks")
            
            if BehavioralAnomalyType.PARAMETER_ANOMALY in anomaly_types:
                recommendations.append("Validate input parameters - possible injection attempts")
        
        return recommendations
    
    def _get_anomaly_type_distribution(self) -> Dict[str, int]:
        """Get distribution of anomaly types."""
        distribution = defaultdict(int)
        for anomaly in self.detected_anomalies:
            distribution[anomaly.anomaly_type.value] += 1
        return dict(distribution)
    
    def _get_known_sequences(self) -> Set[str]:
        """Get known method sequences."""
        return set(self.sequence_patterns)
    
    def _calculate_sequence_similarity(self, sequence: List[str], known_patterns: Set[str]) -> float:
        """Calculate similarity between sequence and known patterns."""
        if not known_patterns:
            return 0.0
        
        sequence_str = " -> ".join(sequence)
        
        # Simple similarity calculation - in production, use more sophisticated methods
        max_similarity = 0.0
        for pattern in known_patterns:
            # Calculate Jaccard similarity
            set1 = set(sequence_str.split())
            set2 = set(pattern.split())
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            similarity = intersection / union if union > 0 else 0.0
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_timing_risk_score(self, z_score: float, severity: SeverityLevel) -> float:
        """Calculate risk score for timing anomalies."""
        base_score = min(1.0, z_score / 5.0)
        severity_multiplier = {
            SeverityLevel.LOW: 0.3,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.HIGH: 0.9,
            SeverityLevel.CRITICAL: 1.0
        }
        return base_score * severity_multiplier.get(severity, 0.5)
    
    def _calculate_frequency_risk_score(self, frequency_ratio: float, severity: SeverityLevel) -> float:
        """Calculate risk score for frequency anomalies."""
        deviation = abs(1 - frequency_ratio)
        base_score = min(1.0, deviation / 2.0)
        severity_multiplier = {
            SeverityLevel.LOW: 0.3,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.HIGH: 0.9,
            SeverityLevel.CRITICAL: 1.0
        }
        return base_score * severity_multiplier.get(severity, 0.5)
    
    def _calculate_sequence_risk_score(self, similarity_score: float) -> float:
        """Calculate risk score for sequence anomalies."""
        return min(1.0, (1.0 - similarity_score) * 0.8)
    
    def _calculate_parameter_risk_score(self, anomaly_count: int) -> float:
        """Calculate risk score for parameter anomalies."""
        return min(1.0, anomaly_count * 0.2)
    
    def _handle_anomaly(self, anomaly: BehavioralAnomaly) -> None:
        """Handle detected anomaly."""
        self.detected_anomalies.append(anomaly)
        
        # Log anomaly
        self.logger.warning(
            f"Behavioral anomaly detected: {anomaly.description}",
            extra={
                "anomaly_type": anomaly.anomaly_type.value,
                "severity": anomaly.severity.value,
                "confidence": anomaly.confidence,
                "risk_score": anomaly.risk_score,
                "evidence": anomaly.evidence
            }
        )
        
        # Trigger callbacks
        for callback in self.anomaly_callbacks:
            try:
                callback(anomaly)
            except Exception as e:
                self.logger.error(f"Error in anomaly callback: {e}")
    
    def _update_method_patterns(self, event: BehavioralEvent) -> None:
        """Update method usage patterns."""
        if event.method_name not in self.method_patterns:
            self.method_patterns[event.method_name] = {
                "call_count": 0,
                "avg_execution_time": 0.0,
                "std_execution_time": 0.0,
                "hourly_frequency": 0.0,
                "success_rate": 1.0,
                "parameter_patterns": {},
                "last_called": None
            }
        
        pattern = self.method_patterns[event.method_name]
        pattern["call_count"] += 1
        pattern["last_called"] = event.timestamp
    
    def _update_timing_patterns(self, event: BehavioralEvent) -> None:
        """Update timing patterns."""
        self.timing_patterns[event.method_name].append(event.execution_time)
    
    def _update_sequence_patterns(self, event: BehavioralEvent) -> None:
        """Update sequence patterns."""
        self.sequence_patterns.append(event.method_name)
    
    def _update_parameter_patterns(self, event: BehavioralEvent) -> None:
        """Update parameter patterns."""
        method_name = event.method_name
        if method_name not in self.parameter_patterns:
            self.parameter_patterns[method_name] = {}
        
        for param_name, param_value in event.parameters.items():
            if param_name not in self.parameter_patterns[method_name]:
                self.parameter_patterns[method_name][param_name] = {
                    "types": set(),
                    "values": deque(maxlen=100)
                }
            
            param_pattern = self.parameter_patterns[method_name][param_name]
            param_pattern["types"].add(type(param_value).__name__)
            param_pattern["values"].append(param_value)
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for storage."""
        sanitized = {}
        
        for key, value in parameters.items():
            # Limit string length
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "..."
            # Convert complex objects to string representation
            elif hasattr(value, '__dict__'):
                sanitized[key] = str(type(value).__name__)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _load_behavioral_data(self) -> None:
        """Load persisted behavioral data."""
        if not self.persistence_path or not self.persistence_path.exists():
            return
        
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
            
            # Load agent fingerprint
            if "fingerprint" in data:
                fp_data = data["fingerprint"]
                self.agent_fingerprint = AgentFingerprint(
                    agent_id=fp_data["agent_id"],
                    agent_type=AgentType(fp_data["agent_type"]),
                    creation_time=datetime.fromisoformat(fp_data["creation_time"]),
                    last_seen=datetime.fromisoformat(fp_data["last_seen"]),
                    method_usage_patterns=fp_data.get("method_usage_patterns", {}),
                    parameter_patterns=fp_data.get("parameter_patterns", {}),
                    timing_patterns=fp_data.get("timing_patterns", {}),
                    sequence_patterns=fp_data.get("sequence_patterns", []),
                    resource_usage_patterns=fp_data.get("resource_usage_patterns", {}),
                    communication_patterns=fp_data.get("communication_patterns", {}),
                    tool_usage_patterns=fp_data.get("tool_usage_patterns", {}),
                    baseline_metrics=fp_data.get("baseline_metrics", {}),
                    confidence_score=fp_data.get("confidence_score", 0.0),
                    environment=fp_data.get("environment", "unknown"),
                    version=fp_data.get("version", "unknown"),
                    capabilities=set(fp_data.get("capabilities", []))
                )
            
            # Load baseline status
            self.baseline_established = data.get("baseline_established", False)
            
            self.logger.info(f"Loaded behavioral data for agent {self.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to load behavioral data: {e}")
    
    def _save_behavioral_data(self) -> None:
        """Save behavioral data to persistence."""
        if not self.persistence_path:
            return
        
        try:
            data = {
                "agent_id": self.agent_id,
                "baseline_established": self.baseline_established,
                "fingerprint": self.agent_fingerprint.to_dict() if self.agent_fingerprint else None,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            # Ensure directory exists
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved behavioral data for agent {self.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save behavioral data: {e}")
    
    def add_anomaly_callback(self, callback: Callable[[BehavioralAnomaly], None]) -> None:
        """Add callback for anomaly detection."""
        self.anomaly_callbacks.append(callback)
    
    def get_agent_fingerprint(self) -> Optional[AgentFingerprint]:
        """Get current agent fingerprint."""
        return self.agent_fingerprint
    
    def get_detected_anomalies(self) -> List[BehavioralAnomaly]:
        """Get all detected anomalies."""
        return self.detected_anomalies.copy()
    
    def reset_baseline(self) -> None:
        """Reset behavioral baseline."""
        with self.lock:
            self.baseline_established = False
            self.method_patterns.clear()
            self.timing_patterns.clear()
            self.sequence_patterns.clear()
            self.parameter_patterns.clear()
            self.detected_anomalies.clear()
            
            self.logger.info(f"Reset behavioral baseline for agent {self.agent_id}")
    
    def shutdown(self) -> None:
        """Shutdown behavioral analyzer."""
        self._save_behavioral_data()
        self.logger.info(f"Behavioral analyzer shutdown for agent {self.agent_id}") 