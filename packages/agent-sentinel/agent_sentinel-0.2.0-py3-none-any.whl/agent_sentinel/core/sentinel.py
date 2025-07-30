"""
Main AgentSentinel class.

This module contains the primary interface for the AgentSentinel SDK,
coordinating all security monitoring, detection, and logging functionality.
"""

import asyncio
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator, Callable, Pattern
from datetime import datetime, timezone
import threading
import logging
from dataclasses import dataclass

from .config import Config
from .constants import ThreatType, SeverityLevel
from .exceptions import AgentSentinelError, ConfigurationError, SecurityError
from .types import SecurityEvent
from .report_generator import UnifiedReportGenerator
from .event_registry import get_global_registry
from ..infrastructure.monitoring.weave_service import WeaveService
from ..infrastructure.monitoring.circuit_breaker import CircuitBreaker
from ..enterprise.threat_intelligence import ThreatIntelligenceEngine
# Intelligence imports removed - handled externally


@dataclass
class FunctionContext:
    """Context information for a monitored function."""
    type: str
    metadata: Dict[str, Any]


class AgentSentinel:
    """
    Main class for AgentSentinel security monitoring SDK.
    
    This class provides the primary interface for monitoring AI agents,
    detecting security threats, and managing security events.
    
    Usage:
        # Initialize with configuration
        sentinel = AgentSentinel(config_path="config.yaml")
        
        # Monitor an agent method
        @sentinel.monitor_method
        def process_data(data: str) -> str:
            return data.upper()
        
        # Or use context manager
        with sentinel.monitor_session("my_agent"):
            result = process_data("hello world")
    """
    
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
        auto_start: bool = True,
        enable_threat_intelligence: bool = True,  # Enable by default when API key available
    ) -> None:
        """
        Initialize AgentSentinel.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Dictionary configuration
            agent_id: Agent identifier
            environment: Environment name
            auto_start: Whether to automatically start monitoring
        """
        # Load configuration
        try:
            self.config = Config(
                config_path=config_path,
                config_dict=config_dict,
                agent_id=agent_id,
                environment=environment,
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize configuration: {e}")
        
        # Initialize core components
        self.agent_id = self.config.agent_id
        self.environment = self.config.environment
        self.is_running = False
        self.start_time = datetime.now(timezone.utc)
        
        # Event storage and processing
        self.events: List[SecurityEvent] = []  # Local storage for backward compatibility
        self.event_lock = threading.Lock()
        self.event_handlers: List[Callable[[SecurityEvent], None]] = []
        
        # Connect to global event registry
        self.global_registry = get_global_registry()
        
        # Session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "average_confidence": 0.0,
            "processing_time": 0.0,
        }
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize Weave service
        self.weave_service = WeaveService(self.config.weave)
        
        # Initialize circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=SecurityError
        )
        
        # Initialize detection engine
        from ..detection.engine import DetectionEngine
        self.detection_engine = DetectionEngine({
            "detection": {
                "enabled": self.config.detection.enabled,
                "confidence_threshold": self.config.detection.confidence_threshold
            }
        })
        
        # Initialize threat intelligence engine if enabled
        self.threat_intelligence = None
        if enable_threat_intelligence:
            try:
                from ..logging.structured_logger import SecurityLogger
                threat_logger = SecurityLogger(f"threat_intel_{self.agent_id}", self.agent_id)
                self.threat_intelligence = ThreatIntelligenceEngine(
                    config={"update_interval": 3600, "max_indicators": 10000},
                    logger=threat_logger
                )
                # Start threat intelligence in background if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.threat_intelligence.start())
                except RuntimeError:
                    # No running event loop, start it when needed
                    pass
            except Exception as e:
                self.logger.warning(f"Failed to initialize threat intelligence: {e}")
        
        # Core SDK - No LLM dependencies
        # LLM/Agentic enrichment should be handled externally
        self.logger.info("Agent Sentinel initialized for core security monitoring")
        self.logger.info("For AI-powered analysis, export events to external enrichment service")
        
        # Initialize unified report generator
        self.report_generator = UnifiedReportGenerator(
            agent_id=self.agent_id,
            log_file=self.config.logging.file
        )
        
        # Auto-start if requested
        if auto_start:
            self.start()
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        log_config = self.config.logging
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_config.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger(f"agent_sentinel.{self.agent_id}")
        self.logger.setLevel(getattr(logging, log_config.level.upper()))
        
        # Create file handler
        handler = logging.FileHandler(log_config.file)
        
        # Create formatter
        if log_config.format == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "agent_id": "' + 
                self.agent_id + '", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info(f"AgentSentinel initialized for agent {self.agent_id}")
    
    def start(self) -> None:
        """Start the AgentSentinel monitoring system."""
        if self.is_running:
            self.logger.warning("AgentSentinel is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"AgentSentinel started for agent {self.agent_id}")
    
    def stop(self) -> None:
        """Stop the AgentSentinel monitoring system."""
        if not self.is_running:
            self.logger.warning("AgentSentinel is not running")
            return
        
        self.is_running = False
        
        # Shutdown Weave service
        if self.weave_service:
            try:
                asyncio.run(self.weave_service.shutdown())
            except Exception as e:
                self.logger.warning(f"Error shutting down Weave service: {e}")
        
        # Log final statistics
        uptime = datetime.now(timezone.utc) - self.start_time
        self.logger.info(
            f"AgentSentinel stopped for agent {self.agent_id}. "
            f"Uptime: {uptime.total_seconds():.2f} seconds, "
            f"Total events: {self.metrics['total_events']}"
        )
    
    def add_event_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """
        Add a custom event handler for security events.
        
        Args:
            handler: Function that takes a SecurityEvent and processes it
        """
        self.event_handlers.append(handler)
        # Also add to global registry so it handles events from decorators
        self.global_registry.add_event_handler(handler)
        self.logger.debug(f"Added event handler: {handler.__name__}")
    
    def record_event(self, event: SecurityEvent) -> None:
        """
        Record a security event.
        
        Args:
            event: SecurityEvent to record
        """
        if not self.is_running:
            self.logger.warning("Cannot record event: AgentSentinel is not running")
            return
        
        with self.event_lock:
            # Add to local event storage (for backward compatibility)
            self.events.append(event)
            
            # Add to global registry (this is the main fix!)
            self.global_registry.register_event(event)
            
            # Update metrics
            self.metrics["total_events"] += 1
            
            threat_type = event.threat_type.value
            if threat_type not in self.metrics["events_by_type"]:
                self.metrics["events_by_type"][threat_type] = 0
            self.metrics["events_by_type"][threat_type] += 1
            
            severity = event.severity.value
            if severity not in self.metrics["events_by_severity"]:
                self.metrics["events_by_severity"][severity] = 0
            self.metrics["events_by_severity"][severity] += 1
            
            # Update average confidence
            total_confidence = sum(e.confidence for e in self.events)
            self.metrics["average_confidence"] = total_confidence / len(self.events)
        
        # Log the event
        self.logger.warning(f"Security event recorded: {event}")
        
        # Process through event handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler {handler.__name__}: {e}")
        
        # Raise SecurityError if confidence is high enough
        if event.confidence >= self.config.detection.confidence_threshold:
            raise SecurityError(
                event.message,
                threat_type=event.threat_type.value,
                severity=event.severity.value,
                confidence=event.confidence,
                details=event.context
            )
    
    def create_security_event(
        self,
        threat_type: ThreatType,
        message: str,
        confidence: float,
        context: Dict[str, Any],
        detection_method: str = "manual",
        raw_data: Optional[str] = None,
    ) -> SecurityEvent:
        """
        Create a new security event.
        
        Args:
            threat_type: Type of threat detected
            message: Human-readable description
            confidence: Confidence score (0.0-1.0)
            context: Additional context
            detection_method: How the threat was detected
            raw_data: Raw data that triggered detection
            
        Returns:
            SecurityEvent instance
        """
        # Get severity from configuration or defaults
        severity = self.config.get_rule_severity(threat_type)
        
        event = SecurityEvent(
            threat_type=threat_type,
            severity=severity,
            message=message,
            confidence=confidence,
            context=context,
            agent_id=self.agent_id,
            detection_method=detection_method,
            raw_data=raw_data,
        )
        
        # Record the event in the system
        self.record_event(event)
        
        return event
    
    @contextmanager
    def monitor_session(self, session_name: str) -> Generator[str, None, None]:
        """
        Context manager for monitoring a session.
        
        Args:
            session_name: Name of the session to monitor
            
        Yields:
            Session ID for tracking
        """
        session_id = f"{self.agent_id}_{session_name}_{int(time.time() * 1000)}"
        
        with self.session_lock:
            self.active_sessions[session_id] = {
                "name": session_name,
                "start_time": datetime.now(timezone.utc),
                "agent_id": self.agent_id,
                "events": [],
            }
        
        self.logger.info(f"Started monitoring session: {session_id}")
        
        try:
            yield session_id
        finally:
            with self.session_lock:
                if session_id in self.active_sessions:
                    session = self.active_sessions.pop(session_id)
                    duration = datetime.now(timezone.utc) - session["start_time"]
                    self.logger.info(
                        f"Finished monitoring session: {session_id}, "
                        f"Duration: {duration.total_seconds():.2f} seconds, "
                        f"Events: {len(session['events'])}"
                    )
    
    def monitor_method(self, func: Callable) -> Callable:
        """
        Decorator for monitoring regular functions and methods.
        
        For MCP tools, use @monitor_mcp() instead.
        
        Args:
            func: Function to monitor
            
        Returns:
            Wrapped function with security monitoring
        """
        def wrapper(*args, **kwargs):
            method_name = func.__name__
            
            with self.monitor_session(f"method_{method_name}"):
                try:
                    start_time = time.time()
                    
                    # Standard threat analysis for inputs
                    self._analyze_inputs_for_threats(args, kwargs, method_name)
                    
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Standard threat analysis for outputs
                    self._analyze_outputs_for_threats(result, method_name)
                    
                    self.logger.debug(
                        f"Method {method_name} completed in {duration:.3f}s"
                    )
                    
                    return result
                except SecurityError:
                    # Re-raise SecurityError without modification
                    raise
                except Exception as e:
                    # Log the exception
                    self.logger.error(f"Exception in monitored method {method_name}: {e}")
                    
                    # Create a security event for unexpected errors
                    event = self.create_security_event(
                        threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                        message=f"Exception in method {method_name}: {str(e)}",
                        confidence=0.5,
                        context={"method": method_name, "exception": str(e)},
                        detection_method="exception_monitoring",
                    )
                    
                    self.record_event(event)
                    raise
        
        return wrapper
    
    # Alias for easier usage
    monitor = monitor_method
    
    # Removed complex universal detection logic - use explicit decorators instead
    
    def _apply_context_security(self, context, args: tuple, kwargs: dict, method_name: str) -> None:
        """
        Apply context-specific security validation.
        
        Args:
            context: Detected function context
            args: Function arguments
            kwargs: Function keyword arguments
            method_name: Name of the monitored method
        """
        # Removed - use explicit decorators instead
        pass
    
    def _apply_mcp_security(self, args: tuple, kwargs: dict, method_name: str) -> None:
        """
        Apply MCP-specific security validation.
        
        Args:
            args: Function arguments
            kwargs: Function keyword arguments
            method_name: Name of the monitored method
        """
        # Removed - use @monitor_mcp() instead
        pass
    
    def _apply_communication_security(self, args: tuple, kwargs: dict, method_name: str) -> None:
        """
        Apply agent-to-agent communication security validation.
        
        Args:
            args: Function arguments
            kwargs: Function keyword arguments
            method_name: Name of the monitored method
        """
        # Removed - use @secure_communication instead
        pass
    
    def _apply_class_method_security(self, context, args: tuple, kwargs: dict, method_name: str) -> None:
        """
        Apply class method security validation.
        
        Args:
            context: Function context
            args: Function arguments
            kwargs: Function keyword arguments
            method_name: Name of the monitored method
        """
        # Removed - standard monitoring is sufficient
        pass
    
    def _apply_context_output_security(self, context, result: Any, method_name: str) -> None:
        """
        Apply context-specific output security validation.
        
        Args:
            context: Function context
            result: Function result
            method_name: Name of the monitored method
        """
        # Removed - use explicit decorators instead
        pass
    
    def _validate_mcp_output(self, result: Any, method_name: str) -> None:
        """
        Validate MCP tool output for security threats.
        
        Args:
            result: Tool output to validate
            method_name: Name of the monitored method
        """
        # Removed - use @monitor_mcp() instead
        pass
    
    def _validate_communication_output(self, result: Any, method_name: str) -> None:
        """
        Validate agent communication output for security threats.
        
        Args:
            result: Communication output to validate
            method_name: Name of the monitored method
        """
        # Removed - use @secure_communication instead
        pass

    async def check_threat_intelligence(self, indicator: str, indicator_type: str = "auto") -> Optional[Dict[str, Any]]:
        """
        Check if an indicator is flagged in threat intelligence.
        
        Args:
            indicator: The indicator to check (IP, domain, hash, etc.)
            indicator_type: Type of indicator (auto-detect if not specified)
            
        Returns:
            Threat indicator data if found, None otherwise
        """
        if not self.threat_intelligence:
            return None
            
        try:
            threat_indicator = await self.threat_intelligence.check_threat(indicator, indicator_type)
            if threat_indicator:
                return threat_indicator.to_dict()
            return None
        except Exception as e:
            self.logger.error(f"Error checking threat intelligence: {e}")
            return None
    
    def execute_with_circuit_breaker(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit breaker is open or function fails
        """
        async def async_wrapper():
            async with self.circuit_breaker:
                return func(*args, **kwargs)
        
        # For sync functions, we need to handle this differently
        if asyncio.iscoroutinefunction(func):
            return asyncio.run(async_wrapper())
        else:
            return asyncio.run(async_wrapper())
    
    def get_threat_intelligence_metrics(self) -> Dict[str, Any]:
        """
        Get threat intelligence metrics.
        
        Returns:
            Dictionary containing threat intelligence metrics
        """
        if not self.threat_intelligence:
            return {"enabled": False}
            
        return {
            "enabled": True,
            **self.threat_intelligence.get_metrics()
        }
    
    def get_circuit_breaker_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.
        
        Returns:
            Dictionary containing circuit breaker metrics
        """
        stats = self.circuit_breaker.get_stats()
        return {
            "state": self.circuit_breaker.state.value,
            "failure_count": self.circuit_breaker.failure_count,
            "last_failure_time": self.circuit_breaker.last_failure_time,
            **stats
        }
    
    def _analyze_inputs_for_threats(self, args: tuple, kwargs: dict, method_name: str) -> None:
        """
        Analyze function inputs for security threats using pattern detection.
        
        Args:
            args: Function arguments
            kwargs: Function keyword arguments
            method_name: Name of the monitored method
        """
        if not self.config.detection.enabled:
            return
        
        # Convert all inputs to strings for pattern analysis
        input_texts = []
        
        # Add positional arguments
        for i, arg in enumerate(args):
            if isinstance(arg, (str, bytes)):
                input_texts.append(str(arg))
            elif hasattr(arg, '__str__'):
                input_texts.append(str(arg))
        
        # Add keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, (str, bytes)):
                input_texts.append(f"{key}: {value}")
            elif hasattr(value, '__str__'):
                input_texts.append(f"{key}: {str(value)}")
        
        # Analyze each input text for threats
        for input_text in input_texts:
            self._detect_threats_in_text(input_text, f"input_{method_name}", "input_analysis")
    
    def _analyze_outputs_for_threats(self, result: Any, method_name: str) -> None:
        """
        Analyze function outputs for security threats using pattern detection.
        
        Args:
            result: Function return value
            method_name: Name of the monitored method
        """
        if not self.config.detection.enabled:
            return
        
        # Convert output to string for pattern analysis
        if isinstance(result, (str, bytes)):
            output_text = str(result)
        elif hasattr(result, '__str__'):
            output_text = str(result)
        else:
            return  # Skip non-string outputs
        
        # Analyze output text for threats
        self._detect_threats_in_text(output_text, f"output_{method_name}", "output_analysis")
    
    def _detect_threats_in_text(self, text: str, context_name: str, detection_method: str) -> None:
        """
        Detect security threats in text using pattern matching.
        
        Args:
            text: Text to analyze
            context_name: Context identifier for the analysis
            detection_method: Method used for detection
        """
        from .constants import THREAT_PATTERNS, THREAT_SEVERITY
        
        # Analyze text against all threat patterns
        for threat_type, patterns in THREAT_PATTERNS.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Calculate confidence based on pattern match strength
                    confidence = self._calculate_pattern_confidence(pattern, text, matches)
                    
                    # Only create event if confidence meets threshold
                    if confidence >= self.config.detection.confidence_threshold:
                        severity = THREAT_SEVERITY.get(threat_type, SeverityLevel.MEDIUM)
                        
                        event = self.create_security_event(
                            threat_type=threat_type,
                            message=f"Potential {threat_type.value.replace('_', ' ')} detected in {context_name}",
                            confidence=confidence,
                            context={
                                "text": text[:500],  # Limit text length for storage
                                "pattern": pattern.pattern,
                                "matches": matches[:10],  # Limit matches
                                "context": context_name,
                                "detection_method": detection_method
                            },
                            detection_method=f"pattern_{detection_method}",
                            raw_data=text
                        )
                        
                        self.record_event(event)
                        self.logger.warning(
                            f"Security threat detected: {threat_type.value} "
                            f"(confidence: {confidence:.1%}) in {context_name}"
                        )
    
    def _calculate_pattern_confidence(self, pattern: 'Pattern', text: str, matches: list) -> float:
        """
        Calculate confidence score for pattern matches.
        
        Args:
            pattern: Regex pattern that matched
            text: Original text
            matches: List of matches found
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence on pattern complexity and match quality
        base_confidence = 0.7
        
        # Boost confidence for exact matches
        if len(matches) == 1 and matches[0] == text.strip():
            base_confidence += 0.2
        
        # Boost confidence for multiple matches (indicates systematic attack)
        if len(matches) > 1:
            base_confidence += 0.1
        
        # Boost confidence for longer, more complex patterns
        if len(pattern.pattern) > 20:
            base_confidence += 0.1
        
        # Reduce confidence for very short patterns (false positives)
        if len(pattern.pattern) < 5:
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_events(
        self,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        limit: Optional[int] = None,
        include_all_agents: bool = False,
    ) -> List[SecurityEvent]:
        """
        Get security events with optional filtering.
        
        This method retrieves events from the global registry. By default, it gets
        events for this specific agent, but can optionally get events from all agents.
        
        Args:
            threat_type: Filter by threat type
            severity: Filter by severity
            limit: Maximum number of events to return
            include_all_agents: If True, get events from all agents (useful when decorators use different agent IDs)
            
        Returns:
            List of matching security events from monitoring components
        """
        if include_all_agents:
            # Get events from all agents (useful for decorator compatibility)
            return self.global_registry.get_events(
                agent_id=None,  # None means all agents
                threat_type=threat_type,
                severity=severity,
                limit=limit
            )
        else:
            # Get events from this specific agent
            events = self.global_registry.get_events(
                agent_id=self.agent_id,
                threat_type=threat_type,
                severity=severity,
                limit=limit
            )
            
            # FALLBACK: If no events found for this agent, try getting from all agents
            # This helps with the decorator agent ID mismatch issue
            if len(events) == 0:
                all_events = self.global_registry.get_events(
                    agent_id=None,
                    threat_type=threat_type,
                    severity=severity,
                    limit=limit
                )
                if len(all_events) > 0:
                    self.logger.warning(
                        f"No events found for agent '{self.agent_id}', but found {len(all_events)} events from other agents. "
                        f"Consider using include_all_agents=True or ensuring decorator agent IDs match."
                    )
                return all_events
            
            return events
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics and statistics.
        
        Returns:
            Dictionary containing metrics
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        
        metrics = {
            "agent_id": self.agent_id,
            "environment": self.environment,
            "uptime_seconds": uptime.total_seconds(),
            "is_running": self.is_running,
            "total_events": self.metrics["total_events"],
            "events_by_type": self.metrics["events_by_type"].copy(),
            "events_by_severity": self.metrics["events_by_severity"].copy(),
            "average_confidence": self.metrics["average_confidence"],
            "active_sessions": len(self.active_sessions),
            "configuration": {
                "detection_enabled": self.config.detection.enabled,
                "confidence_threshold": self.config.detection.confidence_threshold,
                "weave_enabled": self.config.weave.enabled,
                "alerts_enabled": self.config.alerts.enabled,
            },
        }
        
        # Add Weave metrics
        if self.weave_service:
            metrics["weave"] = self.weave_service.get_metrics()
        
        return metrics
    
    def reload_config(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            True if configuration was reloaded, False otherwise
        """
        try:
            reloaded = self.config.reload()
            if reloaded:
                self.logger.info("Configuration reloaded successfully")
            return reloaded
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def __str__(self) -> str:
        """String representation."""
        return f"AgentSentinel(agent_id={self.agent_id}, running={self.is_running})"
    
    def export_events(self, format: str = "json", include_metrics: bool = True) -> Dict[str, Any]:
        """
        Export all security events and metrics for external processing.
        
        Args:
            format: Export format ("json" or "dict")
            include_metrics: Whether to include metrics in export
            
        Returns:
            Dictionary containing events and optional metrics
        """
        with self.event_lock:
            export_data = {
                "agent_id": self.agent_id,
                "environment": self.environment,
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "total_events": len(self.events),
                "events": [event.to_dict() for event in self.events]
            }
            
            if include_metrics:
                export_data["metrics"] = self.metrics.copy()
                export_data["metrics"]["uptime_seconds"] = (
                    datetime.now(timezone.utc) - self.start_time
                ).total_seconds()
        
        self.logger.info(f"Exported {len(self.events)} events for external processing")
        return export_data
    
    def export_events_to_file(self, file_path: str, format: str = "json") -> None:
        """
        Export security events to a file for external processing.
        
        Args:
            file_path: Path to export file
            format: Export format ("json" or "yaml")
        """
        import json
        import yaml
        
        export_data = self.export_events(format="dict")
        
        with open(file_path, 'w') as f:
            if format.lower() == "json":
                json.dump(export_data, f, indent=2, default=str)
            elif format.lower() == "yaml":
                yaml.dump(export_data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Exported events to {file_path}")
    
    def get_events_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all security events for dashboard/reporting.
        
        Returns:
            Dictionary with event summary statistics
        """
        with self.event_lock:
            if not self.events:
                return {
                    "total_events": 0,
                    "events_by_type": {},
                    "events_by_severity": {},
                    "average_confidence": 0.0,
                    "latest_event": None
                }
            
            # Get latest event
            latest_event = max(self.events, key=lambda e: e.timestamp)
            
            return {
                "total_events": len(self.events),
                "events_by_type": self.metrics["events_by_type"],
                "events_by_severity": self.metrics["events_by_severity"],
                "average_confidence": self.metrics["average_confidence"],
                "latest_event": latest_event.to_dict(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all services.
        
        Returns:
            Health check results
        """
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id,
            "environment": self.environment,
            "services": {},
            "errors": []
        }
        
        # Check core service
        health["services"]["core"] = {
            "status": "healthy" if self.is_running else "stopped",
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            "total_events": self.metrics["total_events"]
        }
        
        # Check Weave service
        if self.weave_service:
            try:
                weave_health = await self.weave_service.health_check()
                health["services"]["weave"] = weave_health
                
                if weave_health["status"] != "healthy":
                    health["status"] = "degraded"
                    health["errors"].extend(weave_health.get("errors", []))
                    
            except Exception as e:
                health["services"]["weave"] = {
                    "status": "error",
                    "error": str(e)
                }
                health["status"] = "degraded"
                health["errors"].append(f"Weave health check failed: {str(e)}")
        
        # Note: Threat intelligence is now handled externally
        health["services"]["threat_intelligence"] = {
            "status": "external",
            "note": "AI-powered analysis handled by external enrichment service"
        }
        
        # Check configuration
        try:
            config_health = {
                "status": "healthy",
                "detection_enabled": self.config.detection.enabled,
                "weave_enabled": self.config.weave.enabled,
                "alerts_enabled": self.config.alerts.enabled
            }
            health["services"]["configuration"] = config_health
        except Exception as e:
            health["services"]["configuration"] = {
                "status": "error",
                "error": str(e)
            }
            health["status"] = "unhealthy"
            health["errors"].append(f"Configuration check failed: {str(e)}")
        
        return health
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"AgentSentinel(agent_id='{self.agent_id}', environment='{self.environment}', running={self.is_running})" 

    def export_for_llm_analysis(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export comprehensive security data for LLM agentic analysis.
        
        This method consolidates all security information into a single structure
        that can be easily sent to external LLM enrichment services.
        
        Args:
            file_path: Optional path to save the export (if None, returns dict only)
            
        Returns:
            Dictionary containing all security data for LLM processing
        """
        import json
        
        # Get all current events
        events = self.get_events()
        
        # Get comprehensive metrics
        metrics = self.get_metrics()
        
        # Get events summary
        summary = self.get_events_summary()
        
        # Read recent log entries (last 100 lines)
        log_entries = []
        try:
            with open(self.config.logging.file, 'r') as f:
                lines = f.readlines()
                # Get last 100 log entries
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                for line in recent_lines:
                    try:
                        log_entry = json.loads(line.strip())
                        log_entries.append(log_entry)
                    except json.JSONDecodeError:
                        # Skip non-JSON lines
                        continue
        except FileNotFoundError:
            log_entries = []
        
        # Create comprehensive export
        llm_export = {
            "export_metadata": {
                "agent_id": self.agent_id,
                "environment": self.environment,
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "export_type": "llm_analysis",
                "version": "1.0"
            },
            "security_events": {
                "total_count": len(events),
                "events": [event.to_dict() for event in events],
                "summary": summary
            },
            "operational_metrics": metrics,
            "recent_logs": {
                "total_entries": len(log_entries),
                "entries": log_entries[-50:]  # Last 50 log entries
            },
            "analysis_ready": {
                "has_security_events": len(events) > 0,
                "high_confidence_events": len([e for e in events if e.confidence >= 0.8]),
                "critical_events": len([e for e in events if e.severity.value == "CRITICAL"]),
                "suspicious_patterns": [e.threat_type.value for e in events if e.confidence >= 0.7]
            }
        }
        
        # Save to file if path provided
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(llm_export, f, indent=2, default=str)
            self.logger.info(f"LLM analysis export saved to {file_path}")
        
        return llm_export 

    def export_consolidated_logs(self, file_path: Optional[str] = None) -> str:
        """
        Export all logs and events to a single consolidated file optimized for LLM processing.
        
        Args:
            file_path: Optional custom path, defaults to logs/consolidated_security_logs.json
            
        Returns:
            Path to the exported file
        """
        if file_path is None:
            file_path = "logs/consolidated_security_logs.json"
        
        # Ensure logs directory exists
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Get all events with full context
        events = self.get_events()
        
        # Create consolidated log structure
        consolidated_data = {
            "agent_id": self.agent_id,
            "environment": self.environment,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            "total_events": len(events),
            "security_events": [],
            "monitoring_sessions": [],
            "metrics": self.get_metrics()
        }
        
        # Add detailed event information
        for event in events:
            event_data = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "threat_type": event.threat_type.value,
                "severity": event.severity.value,
                "confidence": event.confidence,
                "message": event.message,
                "detection_method": event.detection_method,
                "context": event.context,
                "raw_data": event.raw_data
            }
            consolidated_data["security_events"].append(event_data)
        
        # Add session information
        with self.session_lock:
            for session_id, session_data in self.active_sessions.items():
                session_info = {
                    "session_id": session_id,
                    "name": session_data["name"],
                    "start_time": session_data["start_time"].isoformat(),
                    "duration_seconds": (datetime.now(timezone.utc) - session_data["start_time"]).total_seconds(),
                    "events_count": len(session_data.get("events", []))
                }
                consolidated_data["monitoring_sessions"].append(session_info)
        
        # Export to file
        import json
        with open(file_path, 'w') as f:
            json.dump(consolidated_data, f, indent=2, default=str)
        
        self.logger.info(f"Consolidated logs exported to {file_path}")
        return file_path
    
    def generate_security_report(self, file_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive security report.
        
        Args:
            file_path: Optional file path to save the report
            
        Returns:
            Path to the generated report file
        """
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/{self.agent_id}_security_report_{timestamp}.md"
        
        # Get all events and metrics
        events = self.get_events()
        metrics = self.get_metrics()
        
        # Generate report content
        report_content = self._generate_report_content(events, metrics)
        
        # Save to file
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(report_content)
        
        self.logger.info(f"Security report generated: {file_path}")
        return file_path
    
    def generate_unified_report(self, file_path: Optional[str] = None) -> str:
        """
        Generate a unified monitoring report combining logs, events, and analysis.
        
        This creates a single comprehensive file with:
        - Real-time session logs
        - Security events and analysis
        - Performance metrics
        - Threat intelligence insights
        - Actionable recommendations
        
        Args:
            file_path: Optional file path to save the report
            
        Returns:
            Path to the generated unified report file
        """
        # Get current events and metrics
        events = self.get_events()
        metrics = self.get_metrics()
        
        # Add uptime to metrics
        uptime = datetime.now(timezone.utc) - self.start_time
        metrics['uptime_seconds'] = uptime.total_seconds()
        
        # Generate unified report
        report = self.report_generator.generate_unified_report(events, metrics)
        
        # Log the report generation
        self.logger.info(f"Unified report generated: {self.report_generator.get_report_path()}")
        
        return str(self.report_generator.get_report_path())
    
    def get_unified_report_path(self) -> str:
        """
        Get the path to the most recent unified report.
        
        Returns:
            Path to the unified report file
        """
        return str(self.report_generator.get_report_path()) 