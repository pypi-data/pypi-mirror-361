"""
Authentication module for LogicPwn Business Logic Exploitation Framework.

This module provides secure authentication functionality with session management,
credential validation, and error handling. Designed for exploit chaining and
multi-step security testing workflows.

Key Features:
- Form-based and token-based authentication
- Persistent session management for exploit chaining
- Secure credential handling and logging
- Comprehensive input validation
- Enterprise-grade error handling

Usage::

    # Basic authentication for exploit chaining
    session = authenticate_session(auth_config)
    
    # Use persistent session for subsequent exploit steps
    response = session.get("https://target.com/admin/panel")
    response = session.post("https://target.com/api/users", data=payload)

"""

import requests
from typing import Dict, Optional, Any, Union, List
from pydantic import BaseModel, Field, field_validator
from loguru import logger
from urllib.parse import urlparse

from ..exceptions import (
    AuthenticationError,
    LoginFailedException,
    NetworkError,
    ValidationError,
    SessionError,
    TimeoutError
)

# Module constants for maintainability and configuration
HTTP_METHODS = {"GET", "POST"}
DEFAULT_SESSION_TIMEOUT = 10
MAX_RESPONSE_TEXT_LENGTH = 500


class AuthConfig(BaseModel):
    """Authentication configuration model for exploit chaining workflows.
    
    This model validates and stores authentication configuration parameters
    including login URL, credentials, and success/failure indicators.
    Designed to support various authentication methods for different
    target applications and APIs.
    """
    
    url: str = Field(..., description="Login endpoint URL")
    method: str = Field(default="POST", description="HTTP method for login")
    credentials: Dict[str, str] = Field(..., description="Login credentials")
    success_indicators: List[str] = Field(default_factory=list, description="Text indicators of successful login")
    failure_indicators: List[str] = Field(default_factory=list, description="Text indicators of failed login")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional HTTP headers")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format for authentication endpoints."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format - must include scheme and netloc')
        return v
    
    @field_validator('credentials')
    @classmethod
    def validate_credentials(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate credentials are not empty for authentication."""
        if not v:
            raise ValueError('Credentials cannot be empty')
        return v
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method for authentication requests."""
        v_up = v.upper()
        if v_up not in HTTP_METHODS:
            raise ValueError(f'method must be one of {HTTP_METHODS}')
        return v_up


def _sanitize_credentials(credentials: Dict[str, str]) -> Dict[str, str]:
    """Sanitize credentials for secure logging (replace values with asterisks per character).
    
    This function ensures that sensitive credential data is never logged
    while maintaining the structure for debugging purposes.
    """
    return {key: '*' * len(value) if value else '***' for key, value in credentials.items()}


def _check_response_indicators(response_text: str, indicators: List[str], indicator_type: str) -> bool:
    """Check if response contains specified indicators for authentication validation.
    
    This function performs case-insensitive text matching to determine
    if authentication was successful or failed based on response content.
    
    Args:
        response_text: Response text to check
        indicators: List of indicators to search for
        indicator_type: Type of indicators ('success' or 'failure')
        
    Returns:
        True if any indicator is found, False otherwise
    """
    if not indicators:
        return False
    
    response_lower = response_text.lower()
    for indicator in indicators:
        if indicator.lower() in response_lower:
            logger.debug(f"Found {indicator_type} indicator: {indicator}")
            return True
    
    return False


def _create_session(config: AuthConfig) -> requests.Session:
    """Create and configure session with authentication settings.
    
    This function sets up a requests session with proper configuration
    for authentication, including SSL verification, timeouts, and headers.
    
    Args:
        config: Authentication configuration
        
    Returns:
        Configured requests session ready for authentication
    """
    session = requests.Session()
    session.verify = config.verify_ssl
    session.timeout = config.timeout
    
    if config.headers:
        session.headers.update(config.headers)
    
    return session


def _prepare_request_kwargs(config: AuthConfig) -> Dict[str, Any]:
    """Prepare request parameters for authentication.
    
    This function prepares the request parameters based on the HTTP method,
    setting up data for POST requests or params for GET requests.
    
    Args:
        config: Authentication configuration
        
    Returns:
        Dictionary of request parameters ready for session.request()
    """
    request_kwargs = {
        'timeout': config.timeout,
        'verify': config.verify_ssl
    }
    
    if config.method == "POST":
        request_kwargs['data'] = config.credentials
    else:  # GET
        request_kwargs['params'] = config.credentials
    
    return request_kwargs


def _handle_response_indicators(response: requests.Response, config: AuthConfig) -> None:
    """Handle response indicator checking and raise appropriate exceptions.
    
    This function validates the authentication response by checking for
    success and failure indicators in the response text. It raises
    LoginFailedException if authentication appears to have failed.
    
    Args:
        response: HTTP response object from authentication request
        config: Authentication configuration
        
    Raises:
        LoginFailedException: If authentication fails based on indicators
    """
    response_text = response.text
    
    # Check for failure indicators first
    if _check_response_indicators(response_text, config.failure_indicators, "failure"):
        logger.error("Authentication failed - failure indicators found in response")
        raise LoginFailedException(
            message="Authentication failed - failure indicators detected",
            response_code=response.status_code,
            response_text=response_text[:MAX_RESPONSE_TEXT_LENGTH]
        )
    
    # Check for success indicators
    if config.success_indicators:
        if not _check_response_indicators(response_text, config.success_indicators, "success"):
            logger.error("Authentication failed - no success indicators found")
            raise LoginFailedException(
                message="Authentication failed - no success indicators detected",
                response_code=response.status_code,
                response_text=response_text[:MAX_RESPONSE_TEXT_LENGTH]
            )


def _validate_config(auth_config: Union[AuthConfig, Dict[str, Any]]) -> AuthConfig:
    """Validate and convert authentication configuration.
    
    This function ensures the authentication configuration is valid and
    converts dictionary inputs to AuthConfig objects for consistent handling.
    
    Args:
        auth_config: Authentication configuration (dict or AuthConfig object)
        
    Returns:
        Validated AuthConfig object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if isinstance(auth_config, dict):
        return AuthConfig(**auth_config)
    return auth_config


def authenticate_session(auth_config: Union[AuthConfig, Dict[str, Any]]) -> requests.Session:
    """
    Authenticate and return a session with persistent cookies for exploit chaining.
    
    This function handles the complete authentication process including
    configuration validation, credential submission, and session management.
    The returned session maintains cookies and headers for subsequent
    exploit steps in multi-step security testing workflows.
    
    Args:
        auth_config: Authentication configuration (dict or AuthConfig object)
        
    Returns:
        Authenticated requests.Session object with persistent cookies
        
    Raises:
        ValidationError: If configuration is invalid
        NetworkError: If network issues occur during authentication
        LoginFailedException: If login fails with provided credentials
        TimeoutError: If authentication request times out
        SessionError: If session creation fails
        
    Example::

        # Basic authentication for exploit chaining
        auth_config = {
            "url": "https://target.com/login",
            "credentials": {"username": "admin", "password": "secret"},
            "success_indicators": ["dashboard", "welcome"]
        }
        session = authenticate_session(auth_config)
        
        # Use session for subsequent exploit steps
        response = session.get("https://target.com/admin/panel")
    """
    try:
        # Validate configuration
        config = _validate_config(auth_config)
        
        # Log authentication attempt (without sensitive data)
        sanitized_creds = _sanitize_credentials(config.credentials)
        logger.info(f"Attempting authentication to {config.url} with method {config.method}")
        logger.debug(f"Credentials: {sanitized_creds}")
        
        # Create and configure session
        session = _create_session(config)
        
        # Prepare request parameters
        request_kwargs = _prepare_request_kwargs(config)
        
        # Perform authentication request
        logger.debug(f"Sending {config.method} request to {config.url}")
        response = session.request(config.method, config.url, **request_kwargs)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Handle response indicators
        _handle_response_indicators(response, config)
        
        # Verify session has cookies (optional check)
        if not session.cookies:
            logger.warning("No cookies received during authentication")
        
        logger.info("Authentication successful - session created with persistent cookies")
        return session
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Authentication request timed out after {config.timeout} seconds")
        raise TimeoutError(
            message=f"Authentication request timed out after {config.timeout} seconds",
            timeout_seconds=config.timeout
        ) from e
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Network connection error during authentication: {e}")
        raise NetworkError(
            message="Network connection error during authentication",
            original_exception=e
        ) from e
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during authentication: {e}")
        raise NetworkError(
            message=f"Request error during authentication: {e}",
            original_exception=e
        ) from e
        
    except ValueError as e:
        logger.error(f"Configuration validation error: {e}")
        raise ValidationError(
            message=f"Configuration validation error: {e}",
            field="configuration",
            value=str(e)
        ) from e
        
    except LoginFailedException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        raise AuthenticationError(f"Unexpected error during authentication: {e}") from e


def validate_session(session: requests.Session, test_url: str) -> bool:
    """
    Validate that a session is still authenticated for exploit chaining.
    
    This function tests if the authenticated session is still valid by
    making a request to a test URL. Useful for checking session
    validity before proceeding with exploit steps.
    
    Args:
        session: The session to validate
        test_url: URL to test authentication against
        
    Returns:
        True if session is still valid, False otherwise
        
    Example::

        # Validate session before exploit step
        if validate_session(session, "https://target.com/admin/check"):
            response = session.get("https://target.com/admin/panel")
    """
    try:
        response = session.get(test_url, timeout=DEFAULT_SESSION_TIMEOUT)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        logger.warning(f"Session validation failed: {e}")
        return False


def logout_session(session: requests.Session, logout_url: str) -> bool:
    """
    Logout from the current session to clean up after exploit chaining.
    
    This function performs a logout request and clears session cookies.
    Useful for cleaning up after completing exploit chains or for
    testing logout functionality.
    
    Args:
        session: The session to logout
        logout_url: URL to logout from
        
    Returns:
        True if logout successful, False otherwise
        
    Example:
        # Clean up after exploit chain
        logout_session(session, "https://target.com/logout")
    """
    try:
        response = session.get(logout_url, timeout=DEFAULT_SESSION_TIMEOUT)
        session.cookies.clear()
        logger.info("Session logged out successfully")
        return True
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        logger.error(f"Logout failed: {e}")
        return False 