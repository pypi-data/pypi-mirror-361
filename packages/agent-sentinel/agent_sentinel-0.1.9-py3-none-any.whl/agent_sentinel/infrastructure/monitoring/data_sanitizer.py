"""
Data Sanitization for Weave Integration

Enterprise-grade data sanitization to protect sensitive information
before sending traces to external services.
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SanitizationConfig:
    """Configuration for data sanitization."""
    
    redact_pii: bool = True
    redact_api_keys: bool = True
    redact_user_data: bool = True
    redact_ip_addresses: bool = True
    redact_emails: bool = True
    redact_phone_numbers: bool = True
    redact_credit_cards: bool = True
    redact_ssn: bool = True
    max_string_length: int = 1000
    custom_patterns: Optional[Dict[str, str]] = None


class DataSanitizer:
    """
    Enterprise-grade data sanitizer for protecting sensitive information.
    
    Provides comprehensive PII and sensitive data redaction before
    sending traces to external monitoring services.
    """
    
    # Common sensitive data patterns
    PATTERNS = {
        'api_key': [
            r'sk-[a-zA-Z0-9]{48,}',  # OpenAI API keys
            r'xoxb-[0-9]{11,12}-[0-9]{11,12}-[a-zA-Z0-9]{24}',  # Slack bot tokens
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub personal access tokens
            r'AIza[0-9A-Za-z_-]{35}',  # Google API keys
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ],
        'phone': [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US phone numbers
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b'  # US phone with parentheses
        ],
        'ip_address': [
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'  # IPv4 addresses
        ],
        'credit_card': [
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b'  # Credit card numbers
        ],
        'ssn': [
            r'\b\d{3}-?\d{2}-?\d{4}\b'  # US SSN
        ],
        'password': [
            r'password["\s]*[:=]["\s]*[^\s"]+',
            r'passwd["\s]*[:=]["\s]*[^\s"]+',
            r'pwd["\s]*[:=]["\s]*[^\s"]+'
        ]
    }
    
    def __init__(self, config: SanitizationConfig):
        """Initialize data sanitizer with configuration."""
        self.config = config
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance."""
        self.compiled_patterns = {}
        
        for category, patterns in self.PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        # Add custom patterns if provided
        if self.config.custom_patterns:
            for name, pattern in self.config.custom_patterns.items():
                self.compiled_patterns[name] = [re.compile(pattern, re.IGNORECASE)]
    
    def sanitize_string(self, text: str) -> str:
        """
        Sanitize a string by redacting sensitive information.
        
        Args:
            text: Input string to sanitize
            
        Returns:
            Sanitized string with sensitive data redacted
        """
        if not isinstance(text, str):
            return text
        
        # Truncate overly long strings
        if len(text) > self.config.max_string_length:
            text = text[:self.config.max_string_length] + "...[TRUNCATED]"
        
        sanitized = text
        
        # Apply redaction based on configuration
        if self.config.redact_api_keys:
            sanitized = self._redact_category(sanitized, 'api_key')
            sanitized = self._redact_category(sanitized, 'password')
        
        if self.config.redact_emails:
            sanitized = self._redact_category(sanitized, 'email')
        
        if self.config.redact_phone_numbers:
            sanitized = self._redact_category(sanitized, 'phone')
        
        if self.config.redact_ip_addresses:
            sanitized = self._redact_category(sanitized, 'ip_address')
        
        if self.config.redact_credit_cards:
            sanitized = self._redact_category(sanitized, 'credit_card')
        
        if self.config.redact_ssn:
            sanitized = self._redact_category(sanitized, 'ssn')
        
        return sanitized
    
    def _redact_category(self, text: str, category: str) -> str:
        """Redact all patterns in a specific category."""
        if category not in self.compiled_patterns:
            return text
        
        for pattern in self.compiled_patterns[category]:
            text = pattern.sub(f'[REDACTED_{category.upper()}]', text)
        
        return text
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize a dictionary.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize the key
            sanitized_key = self.sanitize_string(str(key))
            
            # Sanitize the value based on its type
            if isinstance(value, str):
                sanitized_value = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized_value = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_value = self.sanitize_list(value)
            else:
                sanitized_value = value
            
            sanitized[sanitized_key] = sanitized_value
        
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """
        Sanitize a list by sanitizing each element.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        if not isinstance(data, list):
            return data
        
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    def sanitize_any(self, data: Any) -> Any:
        """
        Sanitize any data type.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, str):
            return self.sanitize_string(data)
        elif isinstance(data, dict):
            return self.sanitize_dict(data)
        elif isinstance(data, list):
            return self.sanitize_list(data)
        else:
            return data
    
    def create_sanitization_function(self) -> Callable:
        """
        Create a sanitization function for use with Weave postprocessing.
        
        Returns:
            Function that can be used with Weave's postprocess_inputs/outputs
        """
        def sanitize_for_weave(inputs: Union[Dict, Any]) -> Union[Dict, Any]:
            """Sanitize inputs/outputs for Weave tracing."""
            try:
                return self.sanitize_any(inputs)
            except Exception as e:
                logger.warning(f"Error during sanitization: {e}")
                return {"sanitization_error": "Failed to sanitize data", "original_type": str(type(inputs))}
        
        return sanitize_for_weave
    
    def get_sanitization_stats(self) -> Dict[str, int]:
        """Get statistics about sanitization operations."""
        # This would be enhanced to track actual redaction counts
        return {
            "patterns_configured": len(self.compiled_patterns),
            "redaction_enabled": sum([
                self.config.redact_pii,
                self.config.redact_api_keys,
                self.config.redact_user_data,
                self.config.redact_ip_addresses,
                self.config.redact_emails,
                self.config.redact_phone_numbers,
                self.config.redact_credit_cards,
                self.config.redact_ssn
            ])
        }


def create_default_sanitizer() -> DataSanitizer:
    """Create a sanitizer with secure default configuration."""
    config = SanitizationConfig(
        redact_pii=True,
        redact_api_keys=True,
        redact_user_data=True,
        redact_ip_addresses=True,
        redact_emails=True,
        redact_phone_numbers=True,
        redact_credit_cards=True,
        redact_ssn=True,
        max_string_length=1000
    )
    return DataSanitizer(config) 