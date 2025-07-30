"""
Core functionality for LogicPwn Business Logic Exploitation Framework.

This package contains the core modules for authentication, request execution,
configuration management, logging, middleware, and response analysis.
It provides the foundation for exploit chaining workflows.
"""

from .auth import (
    authenticate_session,
    validate_session,
    logout_session,
    AuthConfig
)

from .runner import send_request, send_request_advanced

from .async_runner import (
    AsyncRequestRunner,
    AsyncSessionManager,
    send_request_async,
    send_requests_batch_async,
    async_session_manager,
    AsyncRequestContext
)

from .config import (
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
    AuthDefaults
)

from .logging_utils import (
    logger,
    log_request,
    log_response,
    log_error,
    log_info,
    log_debug,
    log_warning,
    LogicPwnLogger,
    SensitiveDataRedactor
)

from .middleware import (
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

__all__ = [
    # Authentication functions
    'authenticate_session',
    'validate_session', 
    'logout_session',
    'AuthConfig',
    # Request execution functions
    'send_request',
    'send_request_advanced',
    # Async request execution functions
    'AsyncRequestRunner',
    'AsyncSessionManager',
    'send_request_async',
    'send_requests_batch_async',
    'async_session_manager',
    'AsyncRequestContext',
    # Configuration
    'config',
    'get_timeout',
    'get_max_retries',
    'get_sensitive_headers',
    'get_sensitive_params',
    'get_redaction_string',
    'get_max_log_body_size',
    'get_log_level',
    'get_logging_defaults',
    'is_request_logging_enabled',
    'is_response_logging_enabled',
    'is_error_logging_enabled',
    'get_session_timeout',
    'get_max_sessions',
    'HTTPMethod',
    'BodyType',
    'RequestDefaults',
    'SecurityDefaults',
    'LoggingDefaults',
    'AuthDefaults',
    # Logging
    'logger',
    'log_request',
    'log_response',
    'log_error',
    'log_info',
    'log_debug',
    'log_warning',
    'LogicPwnLogger',
    'SensitiveDataRedactor',
    # Middleware
    'middleware_manager',
    'add_middleware',
    'remove_middleware',
    'enable_middleware',
    'disable_middleware',
    'get_middleware',
    'list_middleware',
    'BaseMiddleware',
    'AuthenticationMiddleware',
    'LoggingMiddleware',
    'RetryMiddleware',
    'SecurityMiddleware',
    'SessionMiddleware',
    'MiddlewareContext',
    'RetryException'
] 