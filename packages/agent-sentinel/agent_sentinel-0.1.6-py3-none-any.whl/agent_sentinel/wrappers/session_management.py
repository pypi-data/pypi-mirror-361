"""
Session Management for Agent Wrapper

Handles session tracking, lifecycle management, and performance metrics
for monitored AI agent sessions.
"""

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Generator, List, Optional, Any
from dataclasses import dataclass, field

from ..core.types import SecurityEvent


@dataclass
class AgentSession:
    """Agent monitoring session data"""
    session_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    method_calls: List[Dict[str, Any]] = field(default_factory=list)
    security_events: List[SecurityEvent] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_duration(self) -> float:
        """Get session duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.get_duration(),
            'method_calls': len(self.method_calls),
            'security_events': len(self.security_events),
            'performance_metrics': self.performance_metrics,
            'metadata': self.metadata
        }


class SessionManager:
    """Manages agent monitoring sessions"""
    
    def __init__(self, agent_id: str, logger=None):
        self.agent_id = agent_id
        self.logger = logger
        self.active_sessions: Dict[str, AgentSession] = {}
        self.max_session_duration = 3600.0  # 1 hour
        self.session_stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'avg_session_duration': 0.0
        }

    def create_session(self, session_name: Optional[str] = None) -> str:
        """Create a new monitoring session"""
        session_id = str(uuid.uuid4())
        session_name = session_name or f"session_{session_id[:8]}"
        
        session = AgentSession(
            session_id=session_id,
            agent_id=self.agent_id,
            start_time=datetime.now(timezone.utc)
        )
        
        self.active_sessions[session_id] = session
        self.session_stats['active_sessions'] = len(self.active_sessions)
        
        if self.logger:
            self.logger.info(f"Created monitoring session {session_name}", extra={
                'session_id': session_id,
                'session_name': session_name,
                'agent_id': self.agent_id,
                'component': 'session_manager'
            })
        
        return session_id

    def end_session(self, session_id: str) -> Optional[AgentSession]:
        """End a monitoring session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        session.end_time = datetime.now(timezone.utc)
        duration = session.get_duration()
        
        # Update session metrics
        session.performance_metrics = {
            'duration': duration,
            'method_calls': len(session.method_calls),
            'security_events': len(session.security_events)
        }
        
        # Update stats
        self.session_stats['total_sessions'] += 1
        self.session_stats['active_sessions'] = len(self.active_sessions) - 1
        
        # Update average duration
        total_sessions = self.session_stats['total_sessions']
        current_avg = self.session_stats['avg_session_duration']
        self.session_stats['avg_session_duration'] = (
            (current_avg * (total_sessions - 1) + duration) / total_sessions
        )
        
        if self.logger:
            self.logger.info(f"Ended monitoring session", extra={
                'session_id': session_id,
                'duration': duration,
                'method_calls': len(session.method_calls),
                'security_events': len(session.security_events),
                'agent_id': self.agent_id
            })
        
        # Remove from active sessions
        self.active_sessions.pop(session_id, None)
        
        return session

    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get session information"""
        return self.active_sessions.get(session_id)

    def get_all_sessions(self) -> List[AgentSession]:
        """Get all active sessions"""
        return list(self.active_sessions.values())

    def add_method_call(self, session_id: str, method_call_info: Dict[str, Any]):
        """Add method call to session"""
        session = self.active_sessions.get(session_id)
        if session:
            session.method_calls.append(method_call_info)

    def add_security_event(self, session_id: str, security_event: SecurityEvent):
        """Add security event to session"""
        session = self.active_sessions.get(session_id)
        if session:
            session.security_events.append(security_event)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            'session_stats': self.session_stats.copy(),
            'active_sessions': len(self.active_sessions),
            'session_details': [s.to_dict() for s in self.active_sessions.values()]
        }

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (now - session.start_time).total_seconds() > self.max_session_duration:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
            if self.logger:
                self.logger.warning(f"Session {session_id} expired and was automatically closed")

    @contextmanager
    def monitor_session(self, session_name: Optional[str] = None) -> Generator[str, None, None]:
        """Context manager for monitoring sessions"""
        session_id = self.create_session(session_name)
        try:
            yield session_id
        finally:
            self.end_session(session_id) 