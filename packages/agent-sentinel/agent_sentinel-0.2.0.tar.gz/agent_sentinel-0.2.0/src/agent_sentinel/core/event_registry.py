"""
Global Event Registry

A singleton registry to centrally collect and manage security events from all 
AgentWrapper instances and make them available to AgentSentinel instances.
"""

import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timezone
from ..core.types import SecurityEvent
from ..core.constants import ThreatType, SeverityLevel


class GlobalEventRegistry:
    """
    Singleton registry for collecting security events from all monitoring components.
    
    This ensures that events detected by individual decorators (@monitor, @sentinel) 
    are available to the main AgentSentinel instance via get_events().
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GlobalEventRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.events: List[SecurityEvent] = []
            self.events_by_agent: Dict[str, List[SecurityEvent]] = {}
            self.event_lock = threading.Lock()
            self.event_handlers: List[Callable[[SecurityEvent], None]] = []
            self._initialized = True
    
    def register_event(self, event: SecurityEvent) -> None:
        """
        Register a security event from any monitoring component.
        
        Args:
            event: SecurityEvent to register
        """
        with self.event_lock:
            # Add to global event list
            self.events.append(event)
            
            # Add to agent-specific events
            agent_id = event.agent_id
            if agent_id not in self.events_by_agent:
                self.events_by_agent[agent_id] = []
            self.events_by_agent[agent_id].append(event)
        
        # Process through global event handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't break the system
                pass
    
    def get_events(
        self,
        agent_id: Optional[str] = None,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        limit: Optional[int] = None,
    ) -> List[SecurityEvent]:
        """
        Get security events with optional filtering.
        
        Args:
            agent_id: Filter by agent ID (if None, returns all events)
            threat_type: Filter by threat type
            severity: Filter by severity
            limit: Maximum number of events to return
            
        Returns:
            List of matching security events
        """
        with self.event_lock:
            if agent_id:
                events = self.events_by_agent.get(agent_id, []).copy()
            else:
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
    
    def get_agent_events(self, agent_id: str) -> List[SecurityEvent]:
        """
        Get all events for a specific agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            List of events for the agent
        """
        return self.get_events(agent_id=agent_id)
    
    def get_event_count(self, agent_id: Optional[str] = None) -> int:
        """
        Get total event count.
        
        Args:
            agent_id: Optional agent ID filter
            
        Returns:
            Total number of events
        """
        if agent_id:
            return len(self.events_by_agent.get(agent_id, []))
        else:
            return len(self.events)
    
    def add_event_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """
        Add a global event handler.
        
        Args:
            handler: Function that takes a SecurityEvent and processes it
        """
        self.event_handlers.append(handler)
    
    def clear_events(self, agent_id: Optional[str] = None) -> None:
        """
        Clear events (useful for testing).
        
        Args:
            agent_id: If provided, only clear events for this agent
        """
        with self.event_lock:
            if agent_id:
                if agent_id in self.events_by_agent:
                    # Remove agent-specific events
                    agent_events = self.events_by_agent[agent_id]
                    self.events = [e for e in self.events if e not in agent_events]
                    del self.events_by_agent[agent_id]
            else:
                # Clear all events
                self.events.clear()
                self.events_by_agent.clear()
    
    def get_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get event metrics.
        
        Args:
            agent_id: Optional agent ID filter
            
        Returns:
            Dictionary containing event metrics
        """
        events = self.get_events(agent_id=agent_id)
        
        if not events:
            return {
                "total_events": 0,
                "events_by_type": {},
                "events_by_severity": {},
                "average_confidence": 0.0,
            }
        
        # Calculate metrics
        events_by_type = {}
        events_by_severity = {}
        total_confidence = 0.0
        
        for event in events:
            # Count by type
            threat_type = event.threat_type.value
            events_by_type[threat_type] = events_by_type.get(threat_type, 0) + 1
            
            # Count by severity
            severity = event.severity.value
            events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
            
            # Sum confidence
            total_confidence += event.confidence
        
        average_confidence = total_confidence / len(events) if events else 0.0
        
        return {
            "total_events": len(events),
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "average_confidence": average_confidence,
        }

    def get_all_events(
        self,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        limit: Optional[int] = None,
    ) -> List[SecurityEvent]:
        """
        Get all security events from all agents (fallback method).
        
        Args:
            threat_type: Filter by threat type
            severity: Filter by severity
            limit: Maximum number of events to return
            
        Returns:
            List of all security events from all agents
        """
        return self.get_events(
            agent_id=None,  # This gets all events
            threat_type=threat_type,
            severity=severity,
            limit=limit
        )


# Global instance
global_event_registry = GlobalEventRegistry()


def get_global_registry() -> GlobalEventRegistry:
    """Get the global event registry instance."""
    return global_event_registry 