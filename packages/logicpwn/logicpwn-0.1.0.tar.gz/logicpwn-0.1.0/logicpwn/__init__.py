"""
LogicPwn - Business Logic Exploitation & Exploit Chaining Automation Tool.

This package provides a comprehensive suite of security testing tools
with a modular design for advanced business logic exploitation and
multi-step attack automation. Built for penetration testing, security
research, and automated vulnerability assessment.

Key Features:
- Advanced authentication with session persistence
- Exploit chaining workflows
- Modular architecture for easy extension
- Enterprise-grade error handling and logging
- Comprehensive testing and validation
- Centralized configuration management
- Sensitive data redaction and secure logging
- Middleware system for extensibility
- Advanced response analysis and security detection
- High-performance async request execution

Example Usage:
    from logicpwn.core.auth import authenticate_session
    from logicpwn.core import send_request, send_request_advanced
    from logicpwn.core import send_request_async, AsyncRequestRunner
    from logicpwn.models import RequestResult
    
    # Synchronous authentication for exploit chaining
    session = authenticate_session(auth_config)
    
    # Chain exploits with persistent session
    response = session.get("https://target.com/admin/panel")
    response = session.post("https://target.com/api/users", data=payload)
    
    # Use advanced request runner with middleware
    result = send_request_advanced(url="https://target.com/api/data", method="POST")
    if result.has_vulnerabilities():
        print("Security issues detected!")
    
    # High-performance async requests
    async with AsyncRequestRunner() as runner:
        results = await runner.send_requests_batch(request_configs)
"""

from .core import (
    authenticate_session,
    validate_session,
    logout_session,
    AuthConfig,
    send_request,
    send_request_advanced,
    # Async functionality
    AsyncRequestRunner,
    AsyncSessionManager,
    send_request_async,
    send_requests_batch_async,
    async_session_manager,
    AsyncRequestContext,
    # Configuration
    config,
    get_timeout,
    get_max_retries,
    get_sensitive_headers,
    get_sensitive_params,
    get_redaction_string,
    get_max_log_body_size,
    get_log_level,
    get_logging_defaults,
    is_request_logging_enabled,
    is_response_logging_enabled,
    is_error_logging_enabled,
    get_session_timeout,
    get_max_sessions,
    HTTPMethod,
    BodyType,
    RequestDefaults,
    SecurityDefaults,
    LoggingDefaults,
    AuthDefaults,
    # Logging
    logger,
    log_request,
    log_response,
    log_error,
    log_info,
    log_debug,
    log_warning,
    LogicPwnLogger,
    SensitiveDataRedactor,
    # Middleware
    middleware_manager,
    add_middleware,
    remove_middleware,
    enable_middleware,
    disable_middleware,
    get_middleware,
    list_middleware,
    BaseMiddleware,
    AuthenticationMiddleware,
    LoggingMiddleware,
    RetryMiddleware,
    SecurityMiddleware,
    SessionMiddleware,
    MiddlewareContext,
    RetryException
)

from .models import (
    RequestConfig,
    RequestResult,
    RequestMetadata,
    SecurityAnalysis
)

from .exceptions import (
    AuthenticationError,
    LoginFailedException,
    NetworkError,
    ValidationError,
    SessionError,
    TimeoutError
)

__version__ = "0.1.0"
__author__ = "LogicPwn Team"

__all__ = [
    # Core functionality
    "authenticate_session",
    "validate_session",
    "logout_session",
    "AuthConfig",
    "send_request",
    "send_request_advanced",
    
    # Async functionality
    "AsyncRequestRunner",
    "AsyncSessionManager",
    "send_request_async",
    "send_requests_batch_async",
    "async_session_manager",
    "AsyncRequestContext",
    
    # Configuration
    "config",
    "get_timeout",
    "get_max_retries",
    "get_sensitive_headers",
    "get_sensitive_params",
    "get_redaction_string",
    "get_max_log_body_size",
    "get_log_level",
    "get_logging_defaults",
    "is_request_logging_enabled",
    "is_response_logging_enabled",
    "is_error_logging_enabled",
    "get_session_timeout",
    "get_max_sessions",
    "HTTPMethod",
    "BodyType",
    "RequestDefaults",
    "SecurityDefaults",
    "LoggingDefaults",
    "AuthDefaults",
    
    # Logging
    "logger",
    "log_request",
    "log_response",
    "log_error",
    "log_info",
    "log_debug",
    "log_warning",
    "LogicPwnLogger",
    "SensitiveDataRedactor",
    
    # Middleware
    "middleware_manager",
    "add_middleware",
    "remove_middleware",
    "enable_middleware",
    "disable_middleware",
    "get_middleware",
    "list_middleware",
    "BaseMiddleware",
    "AuthenticationMiddleware",
    "LoggingMiddleware",
    "RetryMiddleware",
    "SecurityMiddleware",
    "SessionMiddleware",
    "MiddlewareContext",
    "RetryException",
    
    # Models
    "RequestConfig",
    "RequestResult",
    "RequestMetadata",
    "SecurityAnalysis",
    
    # Exceptions
    "AuthenticationError",
    "LoginFailedException",
    "NetworkError", 
    "ValidationError",
    "SessionError",
    "TimeoutError"
] 