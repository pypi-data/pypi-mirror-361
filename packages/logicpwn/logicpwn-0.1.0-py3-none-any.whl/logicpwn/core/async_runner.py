"""
Async request execution engine for LogicPwn Business Logic Exploitation Framework.

This module provides high-performance async HTTP request execution functionality
using aiohttp for concurrent request handling. Designed for large-scale
security testing and exploit chaining scenarios.

Key Features:
- Async HTTP requests with aiohttp
- Concurrent request execution
- Session management with async sessions
- Middleware integration for async workflows
- Advanced response analysis with RequestResult
- Rate limiting and connection pooling
- Comprehensive error handling

Usage::

    # Async request execution for high-performance testing
    async with AsyncRequestRunner() as runner:
        results = await runner.send_requests_batch(request_configs)
    
    # Single async request
    result = await send_request_async(url="https://target.com/api/data", method="POST")
    
    # Concurrent exploit chaining
    async with AsyncSessionManager() as session:
        responses = await session.execute_exploit_chain(exploit_configs)

"""

import asyncio
import aiohttp
import time
import uuid
from typing import Dict, Optional, Any, Union, List, AsyncGenerator
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..models.request_config import RequestConfig
from ..models.request_result import RequestResult, RequestMetadata, SecurityAnalysis
from ..exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from .config import get_timeout, get_max_retries
from .logging_utils import log_request, log_response, log_error, log_info, log_warning


@dataclass
class AsyncRequestContext:
    """Context for async request execution."""
    request_id: str
    url: str
    method: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    timeout: Optional[int] = None
    session_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class AsyncRequestRunner:
    """High-performance async request runner for concurrent security testing."""
    
    def __init__(self, 
                 max_concurrent: int = 10,
                 rate_limit: Optional[float] = None,
                 timeout: Optional[int] = None,
                 verify_ssl: bool = True):
        """
        Initialize async request runner.
        
        Args:
            max_concurrent: Maximum concurrent requests
            rate_limit: Requests per second limit
            timeout: Default timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.timeout = timeout or get_timeout()
        self.verify_ssl = verify_ssl
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent,
            verify_ssl=self.verify_ssl
        )
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def send_request(self, 
                          url: str,
                          method: str = "GET",
                          headers: Optional[Dict[str, str]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          raw_body: Optional[str] = None,
                          timeout: Optional[int] = None) -> RequestResult:
        """
        Send a single async HTTP request.
        
        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Form data
            json_data: JSON body
            raw_body: Raw body content
            timeout: Request timeout
            
        Returns:
            RequestResult with response analysis
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
        
        async with self.semaphore:
            return await self._execute_request(
                url=url,
                method=method,
                headers=headers or {},
                params=params or {},
                data=data,
                json_data=json_data,
                raw_body=raw_body,
                timeout=timeout or self.timeout
            )
    
    async def send_requests_batch(self, 
                                 request_configs: List[Union[Dict[str, Any], RequestConfig]],
                                 max_concurrent: Optional[int] = None) -> List[RequestResult]:
        """
        Send multiple requests concurrently.
        
        Args:
            request_configs: List of request configurations
            max_concurrent: Override max concurrent requests
            
        Returns:
            List of RequestResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent or self.max_concurrent)
        
        async def execute_with_semaphore(config):
            async with semaphore:
                if isinstance(config, dict):
                    return await self.send_request(**config)
                else:
                    return await self.send_request(
                        url=config.url,
                        method=config.method,
                        headers=config.headers,
                        params=config.params,
                        data=config.data,
                        json_data=config.json_data,
                        raw_body=config.raw_body,
                        timeout=config.timeout
                    )
        
        tasks = [execute_with_semaphore(config) for config in request_configs]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_request(self,
                              url: str,
                              method: str,
                              headers: Dict[str, str],
                              params: Dict[str, Any],
                              data: Optional[Dict[str, Any]] = None,
                              json_data: Optional[Dict[str, Any]] = None,
                              raw_body: Optional[str] = None,
                              timeout: Optional[int] = None) -> RequestResult:
        """Execute a single async request with comprehensive error handling."""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Prepare request data
            request_kwargs = {
                'headers': headers,
                'params': params,
                'timeout': aiohttp.ClientTimeout(total=timeout or self.timeout)
            }
            
            if data:
                request_kwargs['data'] = data
            elif json_data:
                request_kwargs['json'] = json_data
            elif raw_body:
                request_kwargs['data'] = raw_body
            
            # Log request
            log_request(method, url, headers, data or json_data or raw_body)
            
            # Add specific logging for HEAD requests
            if method.upper() == "HEAD":
                log_info(f"HEAD request to {url} - will return headers only, no body expected")
            
            # Execute request
            async with self.session.request(method, url, **request_kwargs) as response:
                duration = time.time() - start_time
                
                # Read response content
                content = await response.read()
                text = content.decode('utf-8', errors='ignore')
                
                # Parse response body
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        body = await response.json()
                    else:
                        body = text
                except Exception:
                    body = text
                
                # Create RequestResult
                result = RequestResult.from_response(
                    url=url,
                    method=method,
                    response=type('MockResponse', (), {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'text': text,
                        'content': content,
                        'json': lambda: body if isinstance(body, dict) else None
                    })(),
                    duration=duration
                )
                
                # Log response
                log_response(response.status, dict(response.headers), body, duration)
                
                # Add specific logging for HEAD response
                if method.upper() == "HEAD":
                    log_info(f"HEAD response headers: {dict(response.headers)}")
                
                return result
                
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_error(TimeoutError(f"Request timeout after {timeout or self.timeout}s"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=TimeoutError(f"Request timeout after {timeout or self.timeout}s"),
                duration=duration
            )
            
        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            log_error(NetworkError(f"Network error: {str(e)}"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=NetworkError(f"Network error: {str(e)}"),
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            log_error(RequestExecutionError(f"Request execution error: {str(e)}"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=RequestExecutionError(f"Request execution error: {str(e)}"),
                duration=duration
            )


class AsyncSessionManager:
    """Async session manager for persistent authentication and exploit chaining."""
    
    def __init__(self, 
                 auth_config: Optional[Dict[str, Any]] = None,
                 max_concurrent: int = 10,
                 timeout: Optional[int] = None):
        """
        Initialize async session manager.
        
        Args:
            auth_config: Authentication configuration
            max_concurrent: Maximum concurrent requests
            timeout: Default timeout in seconds
        """
        self.auth_config = auth_config
        self.max_concurrent = max_concurrent
        self.timeout = timeout or get_timeout()
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookies: Dict[str, str] = {}
        self.headers: Dict[str, str] = {}
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent
        )
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config
        )
        
        # Authenticate if config provided
        if self.auth_config:
            await self.authenticate()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate using the provided auth configuration."""
        if not self.auth_config:
            raise ValidationError("No authentication configuration provided")
        
        try:
            auth_url = self.auth_config['url']
            method = self.auth_config.get('method', 'POST')
            credentials = self.auth_config.get('credentials', {})
            headers = self.auth_config.get('headers', {})
            
            # Prepare request data
            request_data = credentials.copy()
            
            async with self.session.request(
                method=method,
                url=auth_url,
                data=request_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    # Store cookies and headers for session persistence
                    self.cookies.update(response.cookies)
                    self.headers.update(headers)
                    log_info("Authentication successful", {'url': auth_url})
                    return True
                else:
                    log_error(NetworkError(f"Authentication failed: {response.status}"), {
                        'url': auth_url, 'status': response.status
                    })
                    return False
                    
        except Exception as e:
            log_error(NetworkError(f"Authentication error: {str(e)}"), {
                'url': self.auth_config.get('url', 'unknown')
            })
            return False
    
    async def get(self, url: str, **kwargs) -> RequestResult:
        """Send authenticated GET request."""
        return await self._send_authenticated_request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> RequestResult:
        """Send authenticated POST request."""
        return await self._send_authenticated_request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> RequestResult:
        """Send authenticated PUT request."""
        return await self._send_authenticated_request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> RequestResult:
        """Send authenticated DELETE request."""
        return await self._send_authenticated_request('DELETE', url, **kwargs)
    
    async def _send_authenticated_request(self, method: str, url: str, **kwargs) -> RequestResult:
        """Send authenticated request with session persistence."""
        headers = kwargs.get('headers', {}).copy()
        headers.update(self.headers)
        
        cookies = kwargs.get('cookies', {}).copy()
        cookies.update(self.cookies)
        
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': headers,
            'cookies': cookies,
            **{k: v for k, v in kwargs.items() if k not in ['headers', 'cookies']}
        }
        
        async with self.session.request(**request_kwargs) as response:
            # Update session cookies
            self.cookies.update(response.cookies)
            
            # Create RequestResult
            content = await response.read()
            text = content.decode('utf-8', errors='ignore')
            
            try:
                if 'application/json' in response.headers.get('content-type', ''):
                    body = await response.json()
                else:
                    body = text
            except Exception:
                body = text
            
            return RequestResult.from_response(
                url=url,
                method=method,
                response=type('MockResponse', (), {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'text': text,
                    'content': content,
                    'json': lambda: body if isinstance(body, dict) else None
                })(),
                duration=0.0  # Duration calculation would need to be implemented
            )
    
    async def execute_exploit_chain(self, 
                                   exploit_configs: List[Dict[str, Any]]) -> List[RequestResult]:
        """
        Execute a chain of exploits with session persistence.
        
        Args:
            exploit_configs: List of exploit configurations
            
        Returns:
            List of RequestResult objects from the exploit chain
        """
        results = []
        
        for config in exploit_configs:
            method = config.get('method', 'GET')
            url = config['url']
            data = config.get('data')
            headers = config.get('headers', {})
            
            if method.upper() == 'GET':
                result = await self.get(url, headers=headers)
            elif method.upper() == 'POST':
                result = await self.post(url, data=data, headers=headers)
            elif method.upper() == 'PUT':
                result = await self.put(url, data=data, headers=headers)
            elif method.upper() == 'DELETE':
                result = await self.delete(url, headers=headers)
            else:
                raise ValidationError(f"Unsupported HTTP method: {method}")
            
            results.append(result)
            
            # Check if exploit was successful
            if result.status_code >= 400:
                log_warning(f"Exploit step failed: {url}", {
                    'status_code': result.status_code,
                    'method': method
                })
        
        return results


# Convenience functions for easy async usage
async def send_request_async(url: str,
                            method: str = "GET",
                            headers: Optional[Dict[str, str]] = None,
                            **kwargs) -> RequestResult:
    """
    Send a single async HTTP request.
    
    Args:
        url: Target URL
        method: HTTP method
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        RequestResult with response analysis
    """
    async with AsyncRequestRunner() as runner:
        return await runner.send_request(url=url, method=method, headers=headers, **kwargs)


async def send_requests_batch_async(request_configs: List[Union[Dict[str, Any], RequestConfig]],
                                   max_concurrent: int = 10) -> List[RequestResult]:
    """
    Send multiple requests concurrently.
    
    Args:
        request_configs: List of request configurations
        max_concurrent: Maximum concurrent requests
        
    Returns:
        List of RequestResult objects
    """
    async with AsyncRequestRunner(max_concurrent=max_concurrent) as runner:
        return await runner.send_requests_batch(request_configs)


@asynccontextmanager
async def async_session_manager(auth_config: Optional[Dict[str, Any]] = None,
                               max_concurrent: int = 10) -> AsyncGenerator[AsyncSessionManager, None]:
    """
    Async context manager for session management.
    
    Args:
        auth_config: Authentication configuration
        max_concurrent: Maximum concurrent requests
        
    Yields:
        AsyncSessionManager instance
    """
    async with AsyncSessionManager(auth_config=auth_config, max_concurrent=max_concurrent) as session:
        yield session 