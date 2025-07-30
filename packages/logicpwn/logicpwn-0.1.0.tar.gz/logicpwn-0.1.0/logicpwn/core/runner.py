"""
Request execution engine for LogicPwn Business Logic Exploitation Framework.

This module provides HTTP request execution functionality using authenticated
sessions from the auth module. Designed for exploit chaining and multi-step
security testing workflows.

Key Features:
- Send authenticated requests using sessions from auth module
- Support all HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD)
- Flexible request configuration via dict or RequestConfig object
- Multiple body types (JSON, form data, raw body)
- Request metadata collection (timing, status, etc.)
- Comprehensive error handling with detailed exceptions
- Secure request/response logging without sensitive data
- Middleware integration for extensibility
- Advanced response analysis with RequestResult

Usage::

    # Send authenticated request for exploit chaining
    session = authenticate_session(auth_config)
    response = send_request(session, request_config)
    
    # Use response for subsequent exploit steps
    if response.status_code == 200:
        exploit_data = response.json()
    
    # Use advanced runner with middleware and analysis
    result = send_request_advanced(url="https://target.com/api/data", method="POST")
    if result.has_vulnerabilities():
        print("Security issues detected!")

"""

import requests
import time
import uuid
from typing import Dict, Optional, Any, Union
from loguru import logger

from ..models.request_config import RequestConfig
from ..models.request_result import RequestResult
from ..exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from .config import get_timeout, get_max_retries
from .logging_utils import log_request, log_response, log_error
from .middleware import (
    middleware_manager, MiddlewareContext, RetryException
)

# Module constants for maintainability and configuration
MAX_RESPONSE_TEXT_LENGTH = 500


def _validate_config(request_config: Union[RequestConfig, Dict[str, Any]]) -> RequestConfig:
    """Validate and convert request configuration to RequestConfig object.
    
    This function ensures the request configuration is valid and converts
    dictionary configurations to RequestConfig objects for consistent processing.
    
    Args:
        request_config: Request configuration (dict or RequestConfig object)
        
    Returns:
        Validated RequestConfig object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        if isinstance(request_config, dict):
            config = RequestConfig(**request_config)
        elif isinstance(request_config, RequestConfig):
            config = request_config
        else:
            raise ValidationError(
                message="Request configuration must be dict or RequestConfig object",
                field="request_config",
                value=str(type(request_config))
            )
        
        logger.debug(f"Request configuration validated: {config.method} {config.url}")
        return config
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            message=f"Invalid request configuration: {str(e)}",
            field="request_config",
            value=str(request_config)
        )


def _prepare_request_kwargs(config: RequestConfig) -> Dict[str, Any]:
    """Prepare kwargs for requests.Session.request() method.
    
    This function prepares the request parameters based on the configuration,
    setting up headers, body content, and other request parameters.
    
    Args:
        config: Validated RequestConfig object
        
    Returns:
        Dictionary of request parameters ready for session.request()
    """
    request_kwargs = {
        'method': config.method,
        'url': config.url,
        'timeout': config.timeout,
        'verify': config.verify_ssl
    }
    
    # Add headers if specified
    if config.headers:
        request_kwargs['headers'] = config.headers
    
    # Add query parameters if specified
    if config.params:
        request_kwargs['params'] = config.params
    
    # Add body content (only one type allowed)
    if config.data is not None:
        request_kwargs['data'] = config.data
    elif config.json_data is not None:
        request_kwargs['json'] = config.json_data
    elif config.raw_body is not None:
        request_kwargs['data'] = config.raw_body
    
    return request_kwargs


def _execute_request(session: requests.Session, config: RequestConfig, kwargs: Dict[str, Any]) -> requests.Response:
    """Execute the HTTP request using the provided session.
    
    This function performs the actual HTTP request and handles network
    errors, timeouts, and other execution issues.
    
    Args:
        session: Authenticated requests.Session from auth module
        config: Request configuration
        kwargs: Request parameters
        
    Returns:
        requests.Response object
        
    Raises:
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
    """
    try:
        logger.debug(f"Executing {config.method} request to {config.url}")
        response = session.request(**kwargs)
        
        # Check for HTTP error status codes
        if response.status_code >= 400:
            logger.warning(f"Request returned error status: {response.status_code}")
            response_text = response.text[:MAX_RESPONSE_TEXT_LENGTH] if response.text else None
            raise ResponseError(
                message=f"Request failed with status {response.status_code}",
                status_code=response.status_code,
                response_text=response_text
            )
        
        return response
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timed out after {config.timeout} seconds")
        raise TimeoutError(
            message=f"Request timed out after {config.timeout} seconds",
            timeout_seconds=config.timeout
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during request execution: {e}")
        raise NetworkError(
            message=f"Network error during request execution: {str(e)}",
            original_exception=e
        )


def _log_request_info(config: RequestConfig, response: requests.Response, duration: float) -> None:
    """Log request/response information without sensitive data.
    
    This function logs request details, response status, and timing
    information while ensuring no sensitive data is exposed.
    
    Args:
        config: Request configuration
        response: Response object
        duration: Request duration in seconds
    """
    # Safe logging - avoid logging sensitive data
    safe_url = config.url
    if 'password' in safe_url or 'token' in safe_url:
        safe_url = safe_url.split('?')[0] + '***'
    
    logger.info(f"Request completed: {config.method} {safe_url}")
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Request duration: {duration:.3f}s")
    
    # Add specific logging for HEAD requests
    if config.method.upper() == "HEAD":
        logger.info(f"HEAD request - response contains headers only, no body expected")
        logger.debug(f"HEAD response headers: {dict(response.headers)}")
    
    # Log response size for debugging (handle Mock objects)
    try:
        content_length = len(response.content) if response.content else 0
        logger.debug(f"Response size: {content_length} bytes")
    except (TypeError, AttributeError):
        # Handle Mock objects or responses without content
        logger.debug("Response size: Unable to determine (Mock or no content)")


def send_request(
    session: requests.Session,
    request_config: Union[RequestConfig, Dict[str, Any]]
) -> requests.Response:
    """Send an HTTP request using the provided authenticated session.
    
    This function validates the request configuration, prepares the request
    parameters, executes the request, and logs the results. It's designed
    for use in exploit chaining workflows where authenticated sessions
    are used for multiple requests.
    
    Args:
        session: Authenticated requests.Session from auth module
        request_config: Request configuration (dict or RequestConfig object)
        
    Returns:
        requests.Response object with full response data
        
    Raises:
        RequestExecutionError: If request fails to execute
        ValidationError: If request configuration is invalid
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
        
    Example::

        # Send authenticated GET request
        session = authenticate_session(auth_config)
        response = send_request(session, {
            "url": "https://target.com/admin/panel",
            "method": "GET",
            "headers": {"User-Agent": "LogicPwn/1.0"}
        })
        
        # Send authenticated POST request with JSON
        response = send_request(session, {
            "url": "https://target.com/api/users",
            "method": "POST",
            "json_data": {"username": "test", "role": "admin"},
            "headers": {"Content-Type": "application/json"}
        })
    """
    # Validate configuration
    config = _validate_config(request_config)
    
    # Prepare request parameters
    kwargs = _prepare_request_kwargs(config)
    
    # Execute request with timing
    start_time = time.time()
    response = _execute_request(session, config, kwargs)
    duration = time.time() - start_time
    
    # Log request information
    _log_request_info(config, response, duration)
    
    return response


def send_request_advanced(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    raw_body: Optional[str] = None,
    timeout: Optional[int] = None,
    verify_ssl: bool = True,
    session: Optional[requests.Session] = None,
    session_data: Optional[Dict[str, Any]] = None
) -> RequestResult:
    """Send an HTTP request with advanced features including middleware and analysis.
    
    This function provides advanced request execution with middleware integration,
    security analysis, and comprehensive response metadata. It's designed for
    security testing and exploit chaining workflows.
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
        headers: Request headers
        params: Query parameters
        data: Form data
        json_data: JSON data
        raw_body: Raw request body
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        session: Optional requests.Session (creates new if not provided)
        session_data: Optional session data for middleware
        
    Returns:
        RequestResult object with response data and security analysis
        
    Raises:
        RequestExecutionError: If request fails to execute
        ValidationError: If request configuration is invalid
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
        
    Example::

        # Send request with security analysis
        result = send_request_advanced(
            url="https://target.com/api/data",
            method="POST",
            json_data={"action": "test"},
            headers={"Authorization": "Bearer token"}
        )
        
        if result.has_vulnerabilities():
            print("Security issues detected!")
            print(f"Error messages: {result.security_analysis.error_messages}")
    """
    # Validate body types - only one should be specified
    body_fields = [data, json_data, raw_body]
    specified_fields = [field for field in body_fields if field is not None]
    
    if len(specified_fields) > 1:
        field_names = []
        if data is not None:
            field_names.append('data (form data)')
        if json_data is not None:
            field_names.append('json_data (JSON data)')
        if raw_body is not None:
            field_names.append('raw_body (raw body content)')
        
        raise ValidationError(
            f"Multiple body types specified: {', '.join(field_names)}. "
            f"Only one body type allowed per request. Use either form data, "
            f"JSON data, or raw body content, but not multiple types."
        )
    
    # Create RequestResult for tracking
    result = RequestResult(url=url, method=method)
    
    # Use provided session or create new one
    if session is None:
        session = requests.Session()
    
    # Create middleware context
    context = MiddlewareContext(
        request_id=str(uuid.uuid4()),
        url=url,
        method=method.upper(),
        headers=headers or {},
        params=params,
        body=data or json_data or raw_body,
        timeout=timeout or get_timeout(),
        session_data=session_data
    )
    
    # Process request through middleware
    try:
        context = middleware_manager.process_request(context)
    except Exception as e:
        log_error(e, {"url": url, "method": method})
        # Continue with request even if middleware fails
    
    # Log request
    log_request(
        method=context.method,
        url=context.url,
        headers=context.headers,
        params=context.params,
        body=context.body,
        timeout=context.timeout
    )
    
    # Prepare request configuration
    request_config = RequestConfig(
        url=context.url,
        method=context.method,
        headers=context.headers,
        params=context.params,
        data=context.body if isinstance(context.body, dict) else None,
        json_data=context.body if isinstance(context.body, dict) else None,
        raw_body=context.body if isinstance(context.body, str) else None,
        timeout=context.timeout,
        verify_ssl=verify_ssl
    )
    
    # Execute request with retry logic
    max_retries = get_max_retries()
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # Execute request
            start_time = time.time()
            response = send_request(session, request_config)
            duration = time.time() - start_time
            
            # Set response data in RequestResult
            result.set_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text if response.text else None
            )
            
            # Log response
            log_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text if response.text else None,
                response_time=duration
            )
            
            # Process response through middleware
            try:
                result = middleware_manager.process_response(context, result)
            except RetryException:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.info(f"Retrying request (attempt {retry_count}/{max_retries})")
                    continue
                else:
                    raise RequestExecutionError("Max retries exceeded")
            except Exception as e:
                log_error(e, {"url": url, "method": method})
                # Continue even if middleware fails
            
            return result
            
        except (NetworkError, TimeoutError) as e:
            retry_count += 1
            if retry_count <= max_retries:
                logger.warning(f"Request failed, retrying ({retry_count}/{max_retries}): {e}")
                continue
            else:
                # Set error in result
                result.metadata.error = str(e)
                log_error(e, {"url": url, "method": method})
                raise
        except Exception as e:
            # Set error in result
            result.metadata.error = str(e)
            log_error(e, {"url": url, "method": method})
            raise
    
    # This should never be reached, but just in case
    raise RequestExecutionError("Unexpected error in request execution") 