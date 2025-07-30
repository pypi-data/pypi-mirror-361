"""
Log Generator

Generates structured logs for agent monitoring with configurable formats
and output destinations.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

try:
    import structlog
except ImportError:
    # Fallback if structlog is not available
    structlog = None

from .types import SecurityEvent
from .constants import ThreatType, SeverityLevel


@dataclass
class LogEntry:
    """Individual log entry with structured data"""
    timestamp: datetime
    level: str
    message: str
    agent_id: str
    session_id: Optional[str] = None
    method_name: Optional[str] = None
    event_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)


class LogGenerator:
    """
    Generates structured logs for agent monitoring
    """
    
    def __init__(
        self,
        agent_id: str,
        log_file: Optional[str] = None,
        log_format: str = "json",  # "json", "text", "csv"
        log_level: str = "INFO",
        include_performance: bool = True,
        include_security: bool = True,
        include_metadata: bool = True
    ):
        """
        Initialize log generator
        
        Args:
            agent_id: Agent identifier
            log_file: Path to log file (auto-generated if None)
            log_format: Output format ("json", "text", "csv")
            log_level: Minimum log level
            include_performance: Include performance metrics
            include_security: Include security events
            include_metadata: Include metadata
        """
        self.agent_id = agent_id
        self.log_format = log_format
        self.log_level = getattr(logging, log_level.upper())
        self.include_performance = include_performance
        self.include_security = include_security
        self.include_metadata = include_metadata
        
        # Set up log file
        if log_file:
            self.log_file = Path(log_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = Path(f"logs/{agent_id}_monitoring_{timestamp}.log")
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up structured logger
        self.logger = self._setup_logger()
        
        # Track log entries
        self.log_entries: List[LogEntry] = []
    
    def _setup_logger(self):
        """Set up structured logger with appropriate configuration"""
        if structlog is None:
            # Fallback to standard logging
            return logging.getLogger(f"agent_sentinel.{self.agent_id}")
        
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        if self.log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(f"agent_sentinel.{self.agent_id}")
    
    def log_method_call(
        self,
        method_name: str,
        start_time: datetime,
        end_time: datetime,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        result: Any = None,
        exception: Optional[Exception] = None,
        session_id: Optional[str] = None
    ) -> None:
        """Log a method call with full context"""
        duration = (end_time - start_time).total_seconds()
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=start_time,
            level="INFO" if not exception else "ERROR",
            message=f"Method call: {method_name}",
            agent_id=self.agent_id,
            session_id=session_id,
            method_name=method_name,
            event_type="method_call",
            metadata={
                "args": self._sanitize_data(args) if args else None,
                "kwargs": self._sanitize_data(kwargs) if kwargs else None,
                "result": self._sanitize_data(result) if result else None,
                "exception": str(exception) if exception else None,
                "success": exception is None
            },
            performance={
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )
        
        self._write_log_entry(log_entry)
        self.log_entries.append(log_entry)
    
    def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security event"""
        log_entry = LogEntry(
            timestamp=event.timestamp,
            level="WARNING" if event.severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM] else "ERROR",
            message=f"Security event: {event.message}",
            agent_id=self.agent_id,
            session_id=None,  # SecurityEvent doesn't have session_id
            event_type="security_event",
            metadata={
                "threat_type": event.threat_type.value,
                "severity": event.severity.value,
                "confidence": event.confidence,
                "context": event.context
            },
            security={
                "threat_type": event.threat_type.value,
                "severity": event.severity.value,
                "confidence": event.confidence,
                "risk_score": event.confidence * self._severity_to_weight(event.severity)
            }
        )
        
        self._write_log_entry(log_entry)
        self.log_entries.append(log_entry)
    
    def log_performance_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a performance metric"""
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message=f"Performance metric: {metric_name}",
            agent_id=self.agent_id,
            event_type="performance_metric",
            metadata=metadata or {},
            performance={
                "metric_name": metric_name,
                "value": value
            }
        )
        
        self._write_log_entry(log_entry)
        self.log_entries.append(log_entry)
    
    def log_session_event(self, session_id: str, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a session-related event"""
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message=f"Session event: {message}",
            agent_id=self.agent_id,
            session_id=session_id,
            event_type=f"session_{event_type}",
            metadata=metadata or {}
        )
        
        self._write_log_entry(log_entry)
        self.log_entries.append(log_entry)
    
    def _write_log_entry(self, entry: LogEntry) -> None:
        """Write log entry to file and structured logger"""
        # Prepare log data
        log_data = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level,
            "message": entry.message,
            "agent_id": entry.agent_id,
            "session_id": entry.session_id,
            "method_name": entry.method_name,
            "event_type": entry.event_type
        }
        
        # Add optional data based on configuration
        if self.include_metadata and entry.metadata:
            log_data["metadata"] = entry.metadata
        
        if self.include_performance and entry.performance:
            log_data["performance"] = entry.performance
        
        if self.include_security and entry.security:
            log_data["security"] = entry.security
        
        # Write to file
        with open(self.log_file, 'a') as f:
            if self.log_format == "json":
                f.write(json.dumps(log_data) + '\n')
            elif self.log_format == "csv":
                # Convert to CSV format
                csv_line = self._to_csv(log_data)
                f.write(csv_line + '\n')
            else:
                # Text format
                text_line = self._to_text(log_data)
                f.write(text_line + '\n')
        
        # Also log to structured logger (avoid conflicts with reserved fields)
        safe_log_data = {k: v for k, v in log_data.items() if k not in ['method_name', 'event_type']}
        
        if entry.level == "ERROR":
            self.logger.error(entry.message, **safe_log_data)
        elif entry.level == "WARNING":
            self.logger.warning(entry.message, **safe_log_data)
        else:
            self.logger.info(entry.message, **safe_log_data)
    
    def _to_csv(self, log_data: Dict[str, Any]) -> str:
        """Convert log data to CSV format"""
        import csv
        import io
        
        # Flatten nested data for CSV
        flat_data = {
            "timestamp": log_data.get("timestamp", ""),
            "level": log_data.get("level", ""),
            "message": log_data.get("message", ""),
            "agent_id": log_data.get("agent_id", ""),
            "session_id": log_data.get("session_id", ""),
            "method_name": log_data.get("method_name", ""),
            "event_type": log_data.get("event_type", "")
        }
        
        # Add metadata as separate columns
        if "metadata" in log_data:
            for key, value in log_data["metadata"].items():
                flat_data[f"metadata_{key}"] = str(value)
        
        # Add performance as separate columns
        if "performance" in log_data:
            for key, value in log_data["performance"].items():
                flat_data[f"performance_{key}"] = str(value)
        
        # Add security as separate columns
        if "security" in log_data:
            for key, value in log_data["security"].items():
                flat_data[f"security_{key}"] = str(value)
        
        # Convert to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=flat_data.keys())
        writer.writerow(flat_data)
        return output.getvalue().strip()
    
    def _to_text(self, log_data: Dict[str, Any]) -> str:
        """Convert log data to human-readable text format"""
        timestamp = log_data.get("timestamp", "")
        level = log_data.get("level", "")
        message = log_data.get("message", "")
        agent_id = log_data.get("agent_id", "")
        
        text = f"[{timestamp}] {level} - {agent_id}: {message}"
        
        if log_data.get("session_id"):
            text += f" (session: {log_data['session_id']})"
        
        if log_data.get("method_name"):
            text += f" (method: {log_data['method_name']})"
        
        if log_data.get("metadata"):
            text += f" | metadata: {log_data['metadata']}"
        
        if log_data.get("performance"):
            text += f" | performance: {log_data['performance']}"
        
        if log_data.get("security"):
            text += f" | security: {log_data['security']}"
        
        return text
    
    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive information)"""
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items() if not self._is_sensitive_key(k)}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 1000:
            return data[:1000] + "... (truncated)"
        else:
            return data
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key contains sensitive information"""
        sensitive_patterns = [
            'password', 'token', 'key', 'secret', 'auth', 'credential',
            'private', 'sensitive', 'personal', 'ssn', 'credit'
        ]
        return any(pattern in key.lower() for pattern in sensitive_patterns)
    
    def _severity_to_weight(self, severity: SeverityLevel) -> float:
        """Convert severity level to weight for risk calculation"""
        return {
            SeverityLevel.LOW: 1.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.CRITICAL: 4.0
        }.get(severity, 1.0)
    
    def get_log_entries(self) -> List[LogEntry]:
        """Get all logged entries"""
        return self.log_entries.copy()
    
    def get_log_file_path(self) -> Path:
        """Get the path to the log file"""
        return self.log_file
    
    def clear_logs(self) -> None:
        """Clear all logged entries (but keep file)"""
        self.log_entries.clear()
    
    def export_logs(self, format: str = "json") -> str:
        """Export all logs in specified format"""
        if format == "json":
            return json.dumps([entry.__dict__ for entry in self.log_entries], default=str, indent=2)
        elif format == "csv":
            # Convert all entries to CSV
            csv_lines = []
            for entry in self.log_entries:
                log_data = {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                    "agent_id": entry.agent_id,
                    "session_id": entry.session_id,
                    "method_name": entry.method_name,
                    "event_type": entry.event_type,
                    "metadata": json.dumps(entry.metadata) if entry.metadata else "",
                    "performance": json.dumps(entry.performance) if entry.performance else "",
                    "security": json.dumps(entry.security) if entry.security else ""
                }
                csv_lines.append(self._to_csv(log_data))
            return "\n".join(csv_lines)
        else:
            # Text format
            text_lines = []
            for entry in self.log_entries:
                log_data = {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                    "agent_id": entry.agent_id,
                    "session_id": entry.session_id,
                    "method_name": entry.method_name,
                    "event_type": entry.event_type,
                    "metadata": entry.metadata,
                    "performance": entry.performance,
                    "security": entry.security
                }
                text_lines.append(self._to_text(log_data))
            return "\n".join(text_lines) 