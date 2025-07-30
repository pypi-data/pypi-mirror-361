"""
Structured Security Logger

Enterprise-grade structured logging with security-focused features, audit trails,
and threat detection integration.
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field

from ..core.constants import ThreatType, SeverityLevel
from ..core.exceptions import AgentSentinelError


@dataclass
class SecurityLogEntry:
    """Structured security log entry"""
    timestamp: datetime
    level: str
    logger_name: str
    message: str
    agent_id: str
    session_id: Optional[str] = None
    threat_type: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'logger': self.logger_name,
            'message': self.message,
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'confidence': self.confidence,
            'event_id': self.event_id,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'context': self.context,
            'metadata': self.metadata,
            'stack_trace': self.stack_trace,
            'performance': self.performance_metrics
        }

    def to_json(self) -> str:
        """Convert log entry to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(',', ':'))


class StructuredLogger:
    """
    Enterprise-grade structured logger with security features
    
    Provides structured logging with JSON formatting, security context,
    and performance monitoring capabilities.
    """
    
    def __init__(
        self,
        name: str,
        agent_id: str,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        json_format: bool = True,
        enable_console: bool = True,
        enable_audit_trail: bool = True,
        max_message_length: int = 10000,
        sensitive_fields: Optional[List[str]] = None
    ):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            agent_id: Agent identifier
            log_level: Logging level
            log_file: Optional log file path
            json_format: Whether to use JSON formatting
            enable_console: Whether to enable console output
            enable_audit_trail: Whether to maintain audit trail
            max_message_length: Maximum message length for security
            sensitive_fields: List of sensitive field names to sanitize
        """
        self.name = name
        self.agent_id = agent_id
        self.json_format = json_format
        self.enable_audit_trail = enable_audit_trail
        self.max_message_length = max_message_length
        self.sensitive_fields = sensitive_fields or [
            'password', 'token', 'key', 'secret', 'credential',
            'auth', 'session', 'cookie', 'authorization'
        ]
        
        # Initialize Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        self._setup_formatters()
        
        # Create handlers
        self._setup_handlers(log_file, enable_console)
        
        # Audit trail storage
        self.audit_entries: List[SecurityLogEntry] = []
        self.audit_lock = threading.Lock()
        
        # Performance tracking
        self.performance_stats = {
            'total_logs': 0,
            'logs_by_level': {},
            'avg_log_time': 0.0,
            'last_log_time': None
        }
        
        # Security monitoring
        self.security_alerts = []
        self.threat_patterns = {}
        
        self.info(f"Structured logger initialized", extra={
            'component': 'logger',
            'configuration': {
                'json_format': json_format,
                'audit_trail': enable_audit_trail,
                'max_message_length': max_message_length
            }
        })

    def _setup_formatters(self):
        """Setup log formatters"""
        if self.json_format:
            # JSON formatter for structured logs
            self.formatter = logging.Formatter('%(message)s')
        else:
            # Traditional formatter
            self.formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

    def _setup_handlers(self, log_file: Optional[str], enable_console: bool):
        """Setup log handlers"""
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data from log entries"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Truncate long strings for security
            if len(data) > self.max_message_length:
                return data[:self.max_message_length] + "...[TRUNCATED]"
            return data
        else:
            return data

    def _create_log_entry(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> SecurityLogEntry:
        """Create structured log entry"""
        extra = extra or {}
        
        # Sanitize extra data
        sanitized_extra = self._sanitize_data(extra)
        
        return SecurityLogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            logger_name=self.name,
            message=message,
            agent_id=self.agent_id,
            session_id=sanitized_extra.get('session_id'),
            threat_type=sanitized_extra.get('threat_type'),
            severity=sanitized_extra.get('severity'),
            confidence=sanitized_extra.get('confidence'),
            event_id=sanitized_extra.get('event_id'),
            correlation_id=sanitized_extra.get('correlation_id'),
            user_id=sanitized_extra.get('user_id'),
            source_ip=sanitized_extra.get('source_ip'),
            user_agent=sanitized_extra.get('user_agent'),
            endpoint=sanitized_extra.get('endpoint'),
            method=sanitized_extra.get('method'),
            context=sanitized_extra.get('context', {}),
            metadata=sanitized_extra.get('metadata', {}),
            stack_trace=sanitized_extra.get('stack_trace'),
            performance_metrics=sanitized_extra.get('performance_metrics', {})
        )

    def _log_with_structure(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal method for structured logging"""
        start_time = time.time()
        
        try:
            # Create structured log entry
            log_entry = self._create_log_entry(level, message, extra)
            
            # Format message for output
            if self.json_format:
                formatted_message = log_entry.to_json()
            else:
                formatted_message = message
            
            # Log using Python logger
            log_method = getattr(self.logger, level.lower())
            log_method(formatted_message)
            
            # Add to audit trail if enabled
            if self.enable_audit_trail:
                with self.audit_lock:
                    self.audit_entries.append(log_entry)
                    # Keep only last 10000 entries
                    if len(self.audit_entries) > 10000:
                        self.audit_entries = self.audit_entries[-5000:]
            
            # Update performance stats
            log_time = time.time() - start_time
            self.performance_stats['total_logs'] += 1
            self.performance_stats['last_log_time'] = log_time
            
            level_count = self.performance_stats['logs_by_level'].get(level, 0)
            self.performance_stats['logs_by_level'][level] = level_count + 1
            
            # Update average log time
            total_logs = self.performance_stats['total_logs']
            current_avg = self.performance_stats['avg_log_time']
            self.performance_stats['avg_log_time'] = (
                (current_avg * (total_logs - 1) + log_time) / total_logs
            )
            
        except Exception as e:
            # Fallback logging
            self.logger.error(f"Error in structured logging: {e}")

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log_with_structure("DEBUG", message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log_with_structure("INFO", message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log_with_structure("WARNING", message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log_with_structure("ERROR", message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self._log_with_structure("CRITICAL", message, extra)

    def security_event(
        self,
        message: str,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        confidence: Optional[float] = None,
        event_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log security event with additional context"""
        extra = extra or {}
        extra.update({
            'threat_type': threat_type.value if threat_type else None,
            'severity': severity.value if severity else None,
            'confidence': confidence,
            'event_id': event_id,
            'is_security_event': True
        })
        
        self.warning(f"SECURITY EVENT: {message}", extra)

    def audit(self, action: str, user_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        """Log audit event"""
        extra = extra or {}
        extra.update({
            'audit_action': action,
            'user_id': user_id,
            'is_audit_event': True
        })
        
        self.info(f"AUDIT: {action}", extra)

    def performance(self, operation: str, duration: float, extra: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        extra = extra or {}
        extra.update({
            'operation': operation,
            'duration_ms': duration * 1000,
            'performance_metrics': {
                'operation': operation,
                'duration': duration,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        })
        
        self.info(f"PERFORMANCE: {operation} completed in {duration:.3f}s", extra)

    def get_audit_trail(self, limit: Optional[int] = None) -> List[SecurityLogEntry]:
        """Get audit trail entries"""
        with self.audit_lock:
            if limit:
                return self.audit_entries[-limit:]
            return self.audit_entries.copy()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_stats.copy()

    def search_logs(
        self,
        query: str,
        level: Optional[str] = None,
        threat_type: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityLogEntry]:
        """Search audit trail for specific entries"""
        results = []
        
        with self.audit_lock:
            for entry in reversed(self.audit_entries):
                if len(results) >= limit:
                    break
                
                # Apply filters
                if level and entry.level != level:
                    continue
                if threat_type and entry.threat_type != threat_type:
                    continue
                
                # Search in message and context
                if query.lower() in entry.message.lower():
                    results.append(entry)
                elif any(query.lower() in str(v).lower() for v in entry.context.values()):
                    results.append(entry)
        
        return results

    def export_audit_trail(self, file_path: str, format: str = "json"):
        """Export audit trail to file"""
        audit_entries = self.get_audit_trail()
        
        if format == "json":
            with open(file_path, 'w') as f:
                json.dump([entry.to_dict() for entry in audit_entries], f, indent=2)
        elif format == "csv":
            import csv
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=audit_entries[0].to_dict().keys())
                writer.writeheader()
                for entry in audit_entries:
                    writer.writerow(entry.to_dict())


class SecurityLogger(StructuredLogger):
    """
    Specialized security logger with enhanced threat detection features
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize security logger with enhanced features"""
        super().__init__(*args, **kwargs)
        
        # Security-specific configuration
        self.threat_detection_enabled = True
        self.alert_thresholds = {
            'error_rate': 10,  # errors per minute
            'security_events': 5,  # security events per minute
            'failed_attempts': 3   # failed attempts per minute
        }
        
        # Monitoring counters
        self.security_counters = {
            'errors_last_minute': 0,
            'security_events_last_minute': 0,
            'failed_attempts_last_minute': 0,
            'last_reset': time.time()
        }

    def _reset_counters_if_needed(self):
        """Reset counters every minute"""
        now = time.time()
        if now - self.security_counters['last_reset'] >= 60:
            self.security_counters.update({
                'errors_last_minute': 0,
                'security_events_last_minute': 0,
                'failed_attempts_last_minute': 0,
                'last_reset': now
            })

    def _check_alert_thresholds(self):
        """Check if any alert thresholds are exceeded"""
        self._reset_counters_if_needed()
        
        alerts = []
        
        if self.security_counters['errors_last_minute'] > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {self.security_counters['errors_last_minute']} errors/min")
        
        if self.security_counters['security_events_last_minute'] > self.alert_thresholds['security_events']:
            alerts.append(f"High security event rate: {self.security_counters['security_events_last_minute']} events/min")
        
        if self.security_counters['failed_attempts_last_minute'] > self.alert_thresholds['failed_attempts']:
            alerts.append(f"High failure rate: {self.security_counters['failed_attempts_last_minute']} failures/min")
        
        return alerts

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Enhanced error logging with threshold monitoring"""
        super().error(message, extra)
        
        self.security_counters['errors_last_minute'] += 1
        alerts = self._check_alert_thresholds()
        
        for alert in alerts:
            self.critical(f"SECURITY ALERT: {alert}", {
                'alert_type': 'threshold_exceeded',
                'is_security_alert': True
            })

    def security_event(
        self,
        message: str,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        confidence: Optional[float] = None,
        event_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Enhanced security event logging"""
        super().security_event(message, threat_type, severity, confidence, event_id, extra)
        
        self.security_counters['security_events_last_minute'] += 1
        alerts = self._check_alert_thresholds()
        
        for alert in alerts:
            self.critical(f"SECURITY ALERT: {alert}", {
                'alert_type': 'security_threshold_exceeded',
                'is_security_alert': True
            })

    def failed_attempt(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log failed attempt with monitoring"""
        extra = extra or {}
        extra['attempt_result'] = 'failed'
        
        self.warning(f"FAILED ATTEMPT: {message}", extra)
        
        self.security_counters['failed_attempts_last_minute'] += 1
        alerts = self._check_alert_thresholds()
        
        for alert in alerts:
            self.critical(f"SECURITY ALERT: {alert}", {
                'alert_type': 'failure_threshold_exceeded',
                'is_security_alert': True
            })

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security monitoring summary"""
        self._reset_counters_if_needed()
        
        return {
            'current_counters': self.security_counters.copy(),
            'alert_thresholds': self.alert_thresholds.copy(),
            'performance_stats': self.get_performance_stats(),
            'total_audit_entries': len(self.audit_entries)
        } 