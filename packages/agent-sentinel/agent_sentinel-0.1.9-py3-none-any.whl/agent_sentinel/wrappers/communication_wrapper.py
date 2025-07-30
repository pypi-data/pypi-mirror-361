"""
Communication Wrapper for AgentSentinel

Enterprise-grade wrapper for monitoring and securing agent-to-agent communications,
including message validation, encryption, and audit trails.
"""

import asyncio
import functools
import hashlib
import json
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Union, Generator, AsyncGenerator
from dataclasses import dataclass, field

from ..core.constants import ThreatType, SeverityLevel
from ..core.types import SecurityEvent
from ..logging.structured_logger import SecurityLogger
from ..security.validators import InputValidator, ValidationResult
from .agent_wrapper import AgentWrapper


@dataclass
class CommunicationMessage:
    """Represents a communication message between agents"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    encryption_level: str = "none"
    signature: Optional[str] = None
    priority: str = "normal"
    ttl: Optional[int] = None


@dataclass
class CommunicationSession:
    """Communication session between agents"""
    session_id: str
    initiator_id: str
    participant_ids: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: List[CommunicationMessage] = field(default_factory=list)
    security_events: List[SecurityEvent] = field(default_factory=list)
    encryption_enabled: bool = False
    rate_limits: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommunicationWrapper:
    """
    Enterprise-grade communication wrapper for agent-to-agent messaging
    
    Provides comprehensive monitoring, validation, and security features
    for inter-agent communications in production environments.
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[SecurityLogger] = None,
        enable_message_validation: bool = True,
        enable_encryption: bool = False,
        enable_rate_limiting: bool = True,
        enable_audit_logging: bool = True,
        max_message_size: int = 1024 * 1024,  # 1MB
        rate_limit_per_minute: int = 100,
        strict_validation: bool = False
    ):
        """
        Initialize communication wrapper
        
        Args:
            agent_id: Unique identifier for the agent
            logger: Security logger instance
            enable_message_validation: Enable message content validation
            enable_encryption: Enable message encryption
            enable_rate_limiting: Enable rate limiting
            enable_audit_logging: Enable comprehensive audit logging
            max_message_size: Maximum allowed message size in bytes
            rate_limit_per_minute: Rate limit for messages per minute
            strict_validation: Use strict validation mode
        """
        self.agent_id = agent_id
        self.logger = logger or SecurityLogger(
            name=f"communication_wrapper_{agent_id}",
            agent_id=agent_id,
            json_format=True
        )
        
        # Configuration
        self.enable_message_validation = enable_message_validation
        self.enable_encryption = enable_encryption
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_audit_logging = enable_audit_logging
        self.max_message_size = max_message_size
        self.rate_limit_per_minute = rate_limit_per_minute
        self.strict_validation = strict_validation
        
        # Initialize validators
        if self.enable_message_validation:
            self.message_validator = InputValidator(strict_mode=strict_validation)
        else:
            self.message_validator = None
        
        # Active communication sessions
        self.active_sessions: Dict[str, CommunicationSession] = {}
        
        # Rate limiting tracking
        self.message_counts: Dict[str, List[float]] = {}
        
        # Statistics
        self.stats = {
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'total_sessions': 0,
            'security_events': 0,
            'rate_limit_violations': 0,
            'encryption_events': 0,
            'average_message_size': 0.0,
            'message_types': {},
            'communication_patterns': {}
        }
        
        self.logger.info(f"Communication wrapper initialized for {agent_id}", extra={
            'component': 'communication_wrapper',
            'agent_id': agent_id,
            'configuration': {
                'message_validation': enable_message_validation,
                'encryption': enable_encryption,
                'rate_limiting': enable_rate_limiting,
                'audit_logging': enable_audit_logging,
                'max_message_size': max_message_size,
                'rate_limit_per_minute': rate_limit_per_minute
            }
        })

    def secure_send(self, validate_content: bool = True, encrypt: bool = None):
        """
        Decorator for securing message sending
        
        Args:
            validate_content: Whether to validate message content
            encrypt: Whether to encrypt messages (overrides global setting)
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_send_with_monitoring(
                    func, args, kwargs, validate_content, encrypt
                )
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_send_with_monitoring_async(
                    func, args, kwargs, validate_content, encrypt
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        
        return decorator

    def secure_receive(self, validate_content: bool = True, decrypt: bool = None):
        """
        Decorator for securing message receiving
        
        Args:
            validate_content: Whether to validate message content
            decrypt: Whether to decrypt messages (overrides global setting)
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_receive_with_monitoring(
                    func, args, kwargs, validate_content, decrypt
                )
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_receive_with_monitoring_async(
                    func, args, kwargs, validate_content, decrypt
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        
        return decorator

    def _execute_send_with_monitoring(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_content: bool,
        encrypt: Optional[bool]
    ) -> Any:
        """Execute send function with comprehensive monitoring"""
        method_name = func.__name__
        start_time = time.time()
        
        try:
            # Extract message details from function call
            message_info = self._extract_message_info(args, kwargs)
            
            # Rate limiting check
            if self.enable_rate_limiting:
                self._check_rate_limit(message_info['recipient_id'])
            
            # Message size validation
            if message_info['content']:
                self._validate_message_size(message_info['content'])
            
            # Content validation
            if validate_content and self.message_validator and message_info['content']:
                self._validate_message_content(message_info['content'], method_name)
            
            # Encryption (if enabled)
            if encrypt or (encrypt is None and self.enable_encryption):
                message_info['content'] = self._encrypt_message(message_info['content'])
                message_info['encryption_level'] = 'standard'
            
            # Execute the send function
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record successful send
            self._record_message_sent(message_info, duration, method_name)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_send_error(method_name, str(e), duration)
            raise

    async def _execute_send_with_monitoring_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_content: bool,
        encrypt: Optional[bool]
    ) -> Any:
        """Execute async send function with comprehensive monitoring"""
        method_name = func.__name__
        start_time = time.time()
        
        try:
            # Extract message details from function call
            message_info = self._extract_message_info(args, kwargs)
            
            # Rate limiting check
            if self.enable_rate_limiting:
                self._check_rate_limit(message_info['recipient_id'])
            
            # Message size validation
            if message_info['content']:
                self._validate_message_size(message_info['content'])
            
            # Content validation
            if validate_content and self.message_validator and message_info['content']:
                self._validate_message_content(message_info['content'], method_name)
            
            # Encryption (if enabled)
            if encrypt or (encrypt is None and self.enable_encryption):
                message_info['content'] = self._encrypt_message(message_info['content'])
                message_info['encryption_level'] = 'standard'
            
            # Execute the async send function
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record successful send
            self._record_message_sent(message_info, duration, method_name)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_send_error(method_name, str(e), duration)
            raise

    def _execute_receive_with_monitoring(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_content: bool,
        decrypt: Optional[bool]
    ) -> Any:
        """Execute receive function with comprehensive monitoring"""
        method_name = func.__name__
        start_time = time.time()
        
        try:
            # Execute the receive function
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract message details from result
            message_info = self._extract_received_message_info(result)
            
            # Decryption (if enabled)
            if decrypt or (decrypt is None and self.enable_encryption):
                message_info['content'] = self._decrypt_message(message_info['content'])
                message_info['encryption_level'] = 'decrypted'
            
            # Content validation
            if validate_content and self.message_validator and message_info['content']:
                self._validate_message_content(message_info['content'], method_name)
            
            # Record successful receive
            self._record_message_received(message_info, duration, method_name)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_receive_error(method_name, str(e), duration)
            raise

    async def _execute_receive_with_monitoring_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        validate_content: bool,
        decrypt: Optional[bool]
    ) -> Any:
        """Execute async receive function with comprehensive monitoring"""
        method_name = func.__name__
        start_time = time.time()
        
        try:
            # Execute the async receive function
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract message details from result
            message_info = self._extract_received_message_info(result)
            
            # Decryption (if enabled)
            if decrypt or (decrypt is None and self.enable_encryption):
                message_info['content'] = self._decrypt_message(message_info['content'])
                message_info['encryption_level'] = 'decrypted'
            
            # Content validation
            if validate_content and self.message_validator and message_info['content']:
                self._validate_message_content(message_info['content'], method_name)
            
            # Record successful receive
            self._record_message_received(message_info, duration, method_name)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_receive_error(method_name, str(e), duration)
            raise

    def _extract_message_info(self, args: tuple, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract message information from function arguments"""
        # Default values
        message_info = {
            'recipient_id': 'unknown',
            'content': '',
            'message_type': 'text',
            'priority': 'normal',
            'metadata': {}
        }
        
        # Try to extract from common parameter patterns
        if args:
            if len(args) >= 1:
                message_info['recipient_id'] = str(args[0])
            if len(args) >= 2:
                message_info['content'] = str(args[1])
        
        # Override with kwargs
        if 'recipient_id' in kwargs:
            message_info['recipient_id'] = str(kwargs['recipient_id'])
        if 'content' in kwargs:
            message_info['content'] = str(kwargs['content'])
        if 'message_type' in kwargs:
            message_info['message_type'] = str(kwargs['message_type'])
        if 'priority' in kwargs:
            message_info['priority'] = str(kwargs['priority'])
        if 'metadata' in kwargs:
            message_info['metadata'] = kwargs['metadata']
        
        return message_info

    def _extract_received_message_info(self, result: Any) -> Dict[str, Any]:
        """Extract message information from receive function result"""
        # Default values
        message_info = {
            'sender_id': 'unknown',
            'content': '',
            'message_type': 'text',
            'metadata': {}
        }
        
        # Try to extract from common result patterns
        if isinstance(result, dict):
            message_info.update({
                'sender_id': str(result.get('sender_id', 'unknown')),
                'content': str(result.get('content', '')),
                'message_type': str(result.get('message_type', 'text')),
                'metadata': result.get('metadata', {})
            })
        elif isinstance(result, str):
            message_info['content'] = result
        elif hasattr(result, '__dict__'):
            # Object with attributes
            message_info.update({
                'sender_id': str(getattr(result, 'sender_id', 'unknown')),
                'content': str(getattr(result, 'content', '')),
                'message_type': str(getattr(result, 'message_type', 'text')),
                'metadata': getattr(result, 'metadata', {})
            })
        
        return message_info

    def _check_rate_limit(self, recipient_id: str):
        """Check rate limiting for message sending"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries
        if recipient_id in self.message_counts:
            self.message_counts[recipient_id] = [
                timestamp for timestamp in self.message_counts[recipient_id]
                if timestamp > window_start
            ]
        else:
            self.message_counts[recipient_id] = []
        
        # Check limit
        if len(self.message_counts[recipient_id]) >= self.rate_limit_per_minute:
            self.stats['rate_limit_violations'] += 1
            
            event = SecurityEvent(
                threat_type=ThreatType.RATE_LIMIT_VIOLATION,
                severity=SeverityLevel.MEDIUM,
                message=f"Rate limit exceeded for recipient {recipient_id}",
                confidence=1.0,
                context={
                    'recipient_id': recipient_id,
                    'rate_limit': self.rate_limit_per_minute,
                    'current_count': len(self.message_counts[recipient_id]),
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='rate_limiting'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            raise Exception(f"Rate limit exceeded for recipient {recipient_id}")
        
        # Add current message
        self.message_counts[recipient_id].append(current_time)

    def _validate_message_size(self, content: str):
        """Validate message size"""
        content_size = len(content.encode('utf-8'))
        
        if content_size > self.max_message_size:
            event = SecurityEvent(
                threat_type=ThreatType.RESOURCE_ABUSE,
                severity=SeverityLevel.MEDIUM,
                message=f"Message size exceeds limit: {content_size} bytes",
                confidence=1.0,
                context={
                    'message_size': content_size,
                    'max_size': self.max_message_size,
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='size_validation'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            raise Exception(f"Message size {content_size} bytes exceeds limit {self.max_message_size} bytes")

    def _validate_message_content(self, content: str, method_name: str):
        """Validate message content for security threats"""
        if not self.message_validator:
            return
        
        validation = self.message_validator.validate(content)
        
        if not validation.is_safe and validation.threat_type:
            event = SecurityEvent(
                threat_type=validation.threat_type,
                severity=SeverityLevel.HIGH,
                message=f"Malicious content detected in {method_name}",
                confidence=validation.confidence_score,
                context={
                    'method_name': method_name,
                    'content_sample': content[:100] + '...' if len(content) > 100 else content,
                    'violations': validation.violations,
                    'agent_id': self.agent_id
                },
                agent_id=self.agent_id,
                detection_method='content_validation'
            )
            
            self.logger.security_event(
                event.message,
                threat_type=event.threat_type,
                severity=event.severity,
                confidence=event.confidence,
                event_id=event.event_id,
                extra=event.context
            )
            
            self.stats['security_events'] += 1
            raise Exception(f"Malicious content detected: {validation.violations}")

    def _encrypt_message(self, content: str) -> str:
        """Encrypt message content (placeholder for enterprise encryption)"""
        # In a real implementation, this would use proper encryption
        # For now, we'll use a simple hash as a placeholder
        if not content:
            return content
        
        # Simple placeholder encryption (replace with real encryption in production)
        encrypted = hashlib.sha256(content.encode()).hexdigest()[:len(content)]
        self.stats['encryption_events'] += 1
        
        self.logger.debug(f"Message encrypted", extra={
            'agent_id': self.agent_id,
            'original_length': len(content),
            'encrypted_length': len(encrypted)
        })
        
        return encrypted

    def _decrypt_message(self, content: str) -> str:
        """Decrypt message content (placeholder for enterprise decryption)"""
        # In a real implementation, this would use proper decryption
        # For now, we'll return the content as-is
        if not content:
            return content
        
        self.logger.debug(f"Message decrypted", extra={
            'agent_id': self.agent_id,
            'content_length': len(content)
        })
        
        return content

    def _record_message_sent(self, message_info: Dict[str, Any], duration: float, method_name: str):
        """Record successful message send"""
        self.stats['total_messages_sent'] += 1
        
        # Update message type statistics
        message_type = message_info['message_type']
        current_count = self.stats['message_types'].get(message_type, 0)
        self.stats['message_types'][message_type] = current_count + 1
        
        # Update average message size
        content_size = len(message_info['content'].encode('utf-8'))
        total_messages = self.stats['total_messages_sent']
        current_avg = self.stats['average_message_size']
        self.stats['average_message_size'] = (
            (current_avg * (total_messages - 1) + content_size) / total_messages
        )
        
        # Update communication patterns
        recipient_id = message_info['recipient_id']
        pattern_key = f"{self.agent_id}->{recipient_id}"
        current_count = self.stats['communication_patterns'].get(pattern_key, 0)
        self.stats['communication_patterns'][pattern_key] = current_count + 1
        
        # Log the send event
        if self.enable_audit_logging:
            self.logger.info(f"Message sent via {method_name}", extra={
                'method_name': method_name,
                'recipient_id': recipient_id,
                'message_type': message_type,
                'content_size': content_size,
                'duration': duration,
                'encryption_level': message_info.get('encryption_level', 'none'),
                'priority': message_info.get('priority', 'normal'),
                'agent_id': self.agent_id,
                'component': 'communication_wrapper'
            })

    def _record_message_received(self, message_info: Dict[str, Any], duration: float, method_name: str):
        """Record successful message receive"""
        self.stats['total_messages_received'] += 1
        
        # Update message type statistics
        message_type = message_info['message_type']
        current_count = self.stats['message_types'].get(message_type, 0)
        self.stats['message_types'][message_type] = current_count + 1
        
        # Update average message size
        content_size = len(message_info['content'].encode('utf-8'))
        total_messages = self.stats['total_messages_received']
        current_avg = self.stats['average_message_size']
        self.stats['average_message_size'] = (
            (current_avg * (total_messages - 1) + content_size) / total_messages
        )
        
        # Update communication patterns
        sender_id = message_info['sender_id']
        pattern_key = f"{sender_id}->{self.agent_id}"
        current_count = self.stats['communication_patterns'].get(pattern_key, 0)
        self.stats['communication_patterns'][pattern_key] = current_count + 1
        
        # Log the receive event
        if self.enable_audit_logging:
            self.logger.info(f"Message received via {method_name}", extra={
                'method_name': method_name,
                'sender_id': sender_id,
                'message_type': message_type,
                'content_size': content_size,
                'duration': duration,
                'encryption_level': message_info.get('encryption_level', 'none'),
                'agent_id': self.agent_id,
                'component': 'communication_wrapper'
            })

    def _record_send_error(self, method_name: str, error: str, duration: float):
        """Record send error"""
        self.logger.error(f"Error in send method {method_name}: {error}", extra={
            'method_name': method_name,
            'error': error,
            'duration': duration,
            'agent_id': self.agent_id,
            'component': 'communication_wrapper'
        })

    def _record_receive_error(self, method_name: str, error: str, duration: float):
        """Record receive error"""
        self.logger.error(f"Error in receive method {method_name}: {error}", extra={
            'method_name': method_name,
            'error': error,
            'duration': duration,
            'agent_id': self.agent_id,
            'component': 'communication_wrapper'
        })

    @contextmanager
    def monitor_communication_session(
        self,
        session_name: Optional[str] = None,
        participant_ids: Optional[List[str]] = None
    ) -> Generator[str, None, None]:
        """Context manager for monitoring communication sessions"""
        session_id = str(uuid.uuid4())
        session_name = session_name or f"comm_session_{session_id[:8]}"
        
        session = CommunicationSession(
            session_id=session_id,
            initiator_id=self.agent_id,
            participant_ids=participant_ids or [self.agent_id],
            start_time=datetime.now(timezone.utc),
            encryption_enabled=self.enable_encryption
        )
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Started communication session {session_name}", extra={
            'session_id': session_id,
            'session_name': session_name,
            'initiator_id': self.agent_id,
            'participant_ids': participant_ids,
            'encryption_enabled': self.enable_encryption,
            'component': 'communication_wrapper'
        })
        
        try:
            yield session_id
        finally:
            session.end_time = datetime.now(timezone.utc)
            
            # Calculate session metrics
            duration = (session.end_time - session.start_time).total_seconds()
            
            self.logger.info(f"Ended communication session {session_name}", extra={
                'session_id': session_id,
                'session_name': session_name,
                'duration': duration,
                'messages_count': len(session.messages),
                'security_events': len(session.security_events),
                'initiator_id': self.agent_id,
                'component': 'communication_wrapper'
            })
            
            # Remove from active sessions
            self.active_sessions.pop(session_id, None)
            self.stats['total_sessions'] += 1

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get comprehensive communication statistics"""
        return {
            'agent_id': self.agent_id,
            'active_sessions': len(self.active_sessions),
            'stats': self.stats.copy(),
            'configuration': {
                'message_validation': self.enable_message_validation,
                'encryption': self.enable_encryption,
                'rate_limiting': self.enable_rate_limiting,
                'audit_logging': self.enable_audit_logging,
                'max_message_size': self.max_message_size,
                'rate_limit_per_minute': self.rate_limit_per_minute
            },
            'validator_stats': self.message_validator.get_stats() if self.message_validator else None
        }

    def get_session_info(self, session_id: str) -> Optional[CommunicationSession]:
        """Get information about a specific communication session"""
        return self.active_sessions.get(session_id)


# Convenience decorators
def secure_communication(
    agent_id: Optional[str] = None,
    enable_message_validation: bool = True,
    enable_encryption: bool = False,
    enable_rate_limiting: bool = True,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure agent communication methods
    
    Usage:
        @secure_communication(agent_id="my_agent")
        class MyAgent:
            @secure_send()
            def send_message(self, recipient_id: str, content: str):
                # Send logic
                pass
            
            @secure_receive()
            def receive_message(self, sender_id: str, content: str):
                # Receive logic
                pass
    """
    def decorator(cls):
        # Create wrapper instance
        wrapper_instance = CommunicationWrapper(
            agent_id=agent_id or cls.__name__,
            logger=logger,
            enable_message_validation=enable_message_validation,
            enable_encryption=enable_encryption,
            enable_rate_limiting=enable_rate_limiting
        )
        
        # Add wrapper instance to class
        cls._communication_wrapper = wrapper_instance
        
        # Add convenience methods
        cls.secure_send = wrapper_instance.secure_send
        cls.secure_receive = wrapper_instance.secure_receive
        cls.monitor_communication_session = wrapper_instance.monitor_communication_session
        cls.get_communication_stats = lambda self: wrapper_instance.get_communication_stats()
        
        return cls
    
    return decorator


def secure_send(
    validate_content: bool = True,
    encrypt: Optional[bool] = None,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure individual send methods
    
    Usage:
        @secure_send(validate_content=True, encrypt=True)
        def send_message(self, recipient_id: str, content: str):
            # Send logic
            pass
    """
    def decorator(func):
        # Create a wrapper instance for this method
        wrapper_instance = CommunicationWrapper(
            agent_id=agent_id or f"{func.__module__}.{func.__name__}",
            logger=logger
        )
        
        # Apply the secure send decorator
        return wrapper_instance.secure_send(
            validate_content=validate_content,
            encrypt=encrypt
        )(func)
    
    return decorator


def secure_receive(
    validate_content: bool = True,
    decrypt: Optional[bool] = None,
    agent_id: Optional[str] = None,
    logger: Optional[SecurityLogger] = None
) -> Callable:
    """
    Decorator to secure individual receive methods
    
    Usage:
        @secure_receive(validate_content=True, decrypt=True)
        def receive_message(self, sender_id: str, content: str):
            # Receive logic
            pass
    """
    def decorator(func):
        # Create a wrapper instance for this method
        wrapper_instance = CommunicationWrapper(
            agent_id=agent_id or f"{func.__module__}.{func.__name__}",
            logger=logger
        )
        
        # Apply the secure receive decorator
        return wrapper_instance.secure_receive(
            validate_content=validate_content,
            decrypt=decrypt
        )(func)
    
    return decorator


@contextmanager
def monitor_communication_session(
    agent_id: str,
    session_name: Optional[str] = None,
    participant_ids: Optional[List[str]] = None,
    logger: Optional[SecurityLogger] = None
) -> Generator[CommunicationWrapper, None, None]:
    """
    Context manager for monitoring communication sessions
    
    Usage:
        with monitor_communication_session("my_agent") as wrapper:
            # Communication logic
            pass
    """
    wrapper = CommunicationWrapper(
        agent_id=agent_id,
        logger=logger
    )
    
    with wrapper.monitor_communication_session(session_name, participant_ids) as session_id:
        yield wrapper 