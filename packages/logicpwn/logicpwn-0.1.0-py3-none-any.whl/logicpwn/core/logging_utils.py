"""
Centralized logging utilities for LogicPwn.

This module provides a centralized logging system with sensitive data redaction,
consistent formatting, and easy configuration. It ensures that sensitive
information like passwords, tokens, and session data is properly redacted
from logs while maintaining useful debugging information.
"""

import logging
import json
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse
from .config import (
    get_sensitive_headers, get_sensitive_params, get_redaction_string,
    get_max_log_body_size, get_log_level, get_logging_defaults
)


class SensitiveDataRedactor:
    """Handles redaction of sensitive data from logs."""
    
    def __init__(self):
        self.sensitive_headers = get_sensitive_headers()
        self.sensitive_params = get_sensitive_params()
        self.redaction_string = get_redaction_string()
        self.max_body_size = get_max_log_body_size()
    
    def redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Redact sensitive headers from a dictionary."""
        if not headers:
            return {}
        
        redacted_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                redacted_headers[key] = self.redaction_string
            else:
                redacted_headers[key] = value
        
        return redacted_headers
    
    def redact_url_params(self, url: str) -> str:
        """Redact sensitive parameters from URL query string."""
        if not url or '?' not in url:
            return url
        
        parsed = urlparse(url)
        if not parsed.query:
            return url
        
        # Parse query parameters
        params = parse_qs(parsed.query)
        redacted_params = {}
        
        for key, values in params.items():
            if key.lower() in self.sensitive_params:
                redacted_params[key] = [self.redaction_string]
            else:
                redacted_params[key] = values
        
        # Reconstruct URL with redacted parameters
        redacted_query = urlencode(redacted_params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{redacted_query}"
    
    def redact_json_body(self, body: Union[str, Dict, List]) -> str:
        """Redact sensitive data from JSON body."""
        if not body:
            return ""
        
        try:
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            
            redacted_data = self._redact_json_recursive(data)
            return json.dumps(redacted_data, indent=2)
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON, treat as string
            return self._redact_string_body(str(body))
    
    def _redact_json_recursive(self, data: Any) -> Any:
        """Recursively redact sensitive data from JSON structure."""
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if isinstance(key, str) and key.lower() in self.sensitive_params:
                    redacted[key] = self.redaction_string
                else:
                    redacted[key] = self._redact_json_recursive(value)
            return redacted
        elif isinstance(data, list):
            return [self._redact_json_recursive(item) for item in data]
        else:
            return data
    
    def _redact_string_body(self, body: str) -> str:
        """Redact sensitive patterns from string body."""
        if not body:
            return ""
        
        # Truncate if too long
        if len(body) > self.max_body_size:
            body = body[:self.max_body_size] + "... [TRUNCATED]"
        
        # Simple pattern matching for common sensitive data
        patterns = [
            r'password["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'key["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'auth["\']?\s*[:=]\s*["\'][^"\']*["\']',
        ]
        
        redacted_body = body
        for pattern in patterns:
            redacted_body = re.sub(pattern, lambda m: m.group().split('=')[0] + '=' + f'"{self.redaction_string}"', redacted_body, flags=re.IGNORECASE)
        
        return redacted_body
    
    def redact_form_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive form data."""
        if not data:
            return {}
        
        redacted_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in self.sensitive_params:
                redacted_data[key] = self.redaction_string
            else:
                redacted_data[key] = value
        
        return redacted_data


class LogicPwnLogger:
    """Centralized logger for LogicPwn with sensitive data redaction."""
    
    def __init__(self, name: str = "logicpwn"):
        self.logger = logging.getLogger(name)
        self.redactor = SensitiveDataRedactor()
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with proper configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                get_logging_defaults().LOG_FORMAT,
                datefmt=get_logging_defaults().LOG_DATE_FORMAT
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, get_log_level().upper()))
    
    def log_request(self, method: str, url: str, headers: Optional[Dict] = None,
                   params: Optional[Dict] = None, body: Optional[Any] = None,
                   timeout: Optional[int] = None):
        """Log request details with sensitive data redaction."""
        if not get_logging_defaults().ENABLE_REQUEST_LOGGING:
            return
        
        redacted_url = self.redactor.redact_url_params(url)
        redacted_headers = self.redactor.redact_headers(headers or {})
        
        log_data = {
            "method": method,
            "url": redacted_url,
            "headers": redacted_headers,
            "timeout": timeout
        }
        
        if params:
            log_data["params"] = self.redactor.redact_form_data(params)
        
        if body:
            if isinstance(body, dict):
                log_data["body"] = self.redactor.redact_form_data(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[:self.redactor.max_body_size]
        
        self.logger.info(f"Request: {json.dumps(log_data, indent=2)}")
    
    def log_response(self, status_code: int, headers: Optional[Dict] = None,
                    body: Optional[Any] = None, response_time: Optional[float] = None):
        """Log response details with sensitive data redaction."""
        if not get_logging_defaults().ENABLE_RESPONSE_LOGGING:
            return
        
        redacted_headers = self.redactor.redact_headers(headers or {})
        
        log_data = {
            "status_code": status_code,
            "headers": redacted_headers,
            "response_time": response_time
        }
        
        if body:
            if isinstance(body, (dict, list)):
                log_data["body"] = self.redactor.redact_json_body(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[:self.redactor.max_body_size]
        
        self.logger.info(f"Response: {json.dumps(log_data, indent=2)}")
    
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log error details with sensitive data redaction."""
        if not get_logging_defaults().ENABLE_ERROR_LOGGING:
            return
        
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if context:
            # Redact any sensitive data in context
            redacted_context = {}
            for key, value in context.items():
                if isinstance(value, dict):
                    redacted_context[key] = self.redactor.redact_form_data(value)
                elif isinstance(value, str) and key.lower() in self.redactor.sensitive_params:
                    redacted_context[key] = self.redactor.redaction_string
                else:
                    redacted_context[key] = value
            log_data["context"] = redacted_context
        
        self.logger.error(f"Error: {json.dumps(log_data, indent=2)}")
    
    def log_info(self, message: str, data: Optional[Dict] = None):
        """Log informational message with optional data."""
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.info(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.info(message)
    
    def log_debug(self, message: str, data: Optional[Dict] = None):
        """Log debug message with optional data."""
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.debug(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.debug(message)
    
    def log_warning(self, message: str, data: Optional[Dict] = None):
        """Log warning message with optional data."""
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.warning(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.warning(message)


# Global logger instance
logger = LogicPwnLogger()


# Convenience functions for easy access
def log_request(method: str, url: str, headers: Optional[Dict] = None,
                params: Optional[Dict] = None, body: Optional[Any] = None,
                timeout: Optional[int] = None):
    """Log request details."""
    logger.log_request(method, url, headers, params, body, timeout)


def log_response(status_code: int, headers: Optional[Dict] = None,
                body: Optional[Any] = None, response_time: Optional[float] = None):
    """Log response details."""
    logger.log_response(status_code, headers, body, response_time)


def log_error(error: Exception, context: Optional[Dict] = None):
    """Log error details."""
    logger.log_error(error, context)


def log_info(message: str, data: Optional[Dict] = None):
    """Log informational message."""
    logger.log_info(message, data)


def log_debug(message: str, data: Optional[Dict] = None):
    """Log debug message."""
    logger.log_debug(message, data)


def log_warning(message: str, data: Optional[Dict] = None):
    """Log warning message."""
    logger.log_warning(message, data) 