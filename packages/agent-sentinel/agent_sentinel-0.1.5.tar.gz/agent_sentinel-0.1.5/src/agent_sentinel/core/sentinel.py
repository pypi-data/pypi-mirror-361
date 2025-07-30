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
from typing import Any, Dict, List, Optional, Union, Generator, Callable
from datetime import datetime, timezone
import threading
import logging

from .config import Config
from .constants import ThreatType, SeverityLevel
from .exceptions import AgentSentinelError, ConfigurationError, SecurityError
from .types import SecurityEvent
from ..intelligence.enricher import ThreatIntelligenceEnricher, EnrichedSecurityEvent
from ..intelligence.exa_service import ExaThreatIntelligence


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
        exa_api_key: Optional[str] = None,
        enable_threat_intelligence: bool = False,
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
        self.events: List[SecurityEvent] = []
        self.event_lock = threading.Lock()
        self.event_handlers: List[Callable[[SecurityEvent], None]] = []
        
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
        
        # Initialize detection engine (placeholder for now)
        self.detection_engine = None
        
        # Initialize threat intelligence (optional)
        self.threat_intelligence_enricher = None
        self.exa_service = None
        
        if enable_threat_intelligence:
            try:
                # Use provided API key or get from environment
                api_key = exa_api_key or os.getenv('EXA_API_KEY')
                
                if not api_key:
                    self.logger.warning("Exa API key not found. Set EXA_API_KEY environment variable to enable threat intelligence.")
                    self.threat_intelligence_enricher = None
                else:
                    # Initialize Exa threat intelligence service
                    self.exa_service = ExaThreatIntelligence(api_key=api_key)
                    self.threat_intelligence_enricher = ThreatIntelligenceEnricher(
                        self.exa_service,
                        config=getattr(self.config, 'threat_intelligence', {})
                    )
                    self.logger.info("Threat intelligence enrichment enabled with Exa API")
            except Exception as e:
                self.logger.warning(f"Failed to initialize threat intelligence: {e}")
                self.threat_intelligence_enricher = None
        
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
            # Add to event storage
            self.events.append(event)
            
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
        
        return SecurityEvent(
            threat_type=threat_type,
            severity=severity,
            message=message,
            confidence=confidence,
            context=context,
            agent_id=self.agent_id,
            detection_method=detection_method,
            raw_data=raw_data,
        )
    
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
        Decorator for monitoring individual methods.
        
        Args:
            func: Function to monitor
            
        Returns:
            Wrapped function with monitoring
        """
        def wrapper(*args, **kwargs):
            method_name = func.__name__
            
            with self.monitor_session(f"method_{method_name}"):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    self.logger.debug(
                        f"Method {method_name} completed in {duration:.3f}s"
                    )
                    
                    return result
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
    
    def get_events(
        self,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        limit: Optional[int] = None,
    ) -> List[SecurityEvent]:
        """
        Get security events with optional filtering.
        
        Args:
            threat_type: Filter by threat type
            severity: Filter by severity
            limit: Maximum number of events to return
            
        Returns:
            List of matching security events
        """
        with self.event_lock:
            events = self.events.copy()
        
        # Apply filters
        if threat_type:
            events = [e for e in events if e.threat_type == threat_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            events = events[:limit]
        
        return events
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics and statistics.
        
        Returns:
            Dictionary containing metrics
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        
        return {
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
    
    async def enrich_security_event(self, event: SecurityEvent) -> 'EnrichedSecurityEvent':
        """
        Enrich a security event with threat intelligence
        
        Args:
            event: Security event to enrich
            
        Returns:
            EnrichedSecurityEvent with intelligence data
        """
        if not self.threat_intelligence_enricher:
            # Return basic enriched event without intelligence
            return EnrichedSecurityEvent(original_event=event)
        
        try:
            enriched_event = await self.threat_intelligence_enricher.enrich_security_event(event)
            self.logger.info(f"Successfully enriched security event {event.event_id}")
            return enriched_event
        except Exception as e:
            self.logger.error(f"Failed to enrich security event {event.event_id}: {str(e)}")
            return EnrichedSecurityEvent(
                original_event=event,
                enrichment_errors=[f"Enrichment failed: {str(e)}"]
            )
    
    def generate_intelligence_report(self, enriched_event: 'EnrichedSecurityEvent') -> str:
        """
        Generate enhanced security report with threat intelligence
        
        Args:
            enriched_event: Enriched security event
            
        Returns:
            Formatted intelligence report
        """
        if not self.threat_intelligence_enricher:
            return f"""
🚨 **THREAT DETECTION ALERT**

**Detection Summary:**
- Attack Type: {enriched_event.original_event.threat_type.value}
- Severity: {enriched_event.original_event.severity.value}
- Confidence: {enriched_event.original_event.confidence:.0%}
- Agent: {enriched_event.original_event.agent_id}
- Timestamp: {enriched_event.original_event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

**Note:** Threat intelligence enrichment not available.
"""
        
        return self.threat_intelligence_enricher.generate_intelligence_report(enriched_event)
    
    def get_threat_intelligence_stats(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        if not self.threat_intelligence_enricher:
            return {"enabled": False, "reason": "Threat intelligence not initialized"}
        
        stats = self.threat_intelligence_enricher.get_enrichment_stats()
        if self.exa_service:
            stats.update(self.exa_service.get_cache_stats())
        
        return stats
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"AgentSentinel(agent_id='{self.agent_id}', environment='{self.environment}', running={self.is_running})" 