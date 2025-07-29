import json
from typing import Optional, Dict, Any
import httpx


class AkeneoAPIError(Exception):
    """Base exception for all Akeneo API errors."""
    
    def __init__(
        self, 
        message: str, 
        response: Optional[httpx.Response] = None,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = status_code or (response.status_code if response else None)
        self.retry_after = float(retry_after) if retry_after is not None else None
        
        # Try to extract additional error info from response
        self.error_code = None
        self.error_details = None
        
        if response and response.content:
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    self.error_code = error_data.get('code')
                    self.error_details = error_data.get('message') or error_data.get('errors')
            except (json.JSONDecodeError, ValueError):
                pass


class AuthenticationError(AkeneoAPIError):
    """Raised when authentication fails."""
    pass


class ValidationError(AkeneoAPIError):
    """Raised when request validation fails (422)."""
    pass


class NotFoundError(AkeneoAPIError):
    """Raised when a resource is not found (404)."""
    pass


class RateLimitError(AkeneoAPIError):
    """Raised when rate limit is exceeded (429)."""
    pass


class ServerError(AkeneoAPIError):
    """Raised when server error occurs (5xx)."""
    pass


class ForbiddenError(AkeneoAPIError):
    """Raised when access is forbidden (403)."""
    pass


class BadRequestError(AkeneoAPIError):
    """Raised when request is malformed (400)."""
    pass


def create_exception_from_response(
    response: httpx.Response, 
    method: str, 
    url: str, 
    **kwargs
) -> AkeneoAPIError:
    """Create an appropriate exception from an HTTP response."""
    
    # Extract retry-after header if present
    retry_after = None
    retry_after_header = response.headers.get("Retry-After")
    if retry_after_header and retry_after_header.isdigit():
        retry_after = int(retry_after_header)
    
    # Try to get error message from response
    error_message = f"{method} {url} failed with status {response.status_code}"
    
    try:
        if response.content:
            error_data = response.json()
            if isinstance(error_data, dict):
                if 'message' in error_data:
                    error_message = error_data['message']
                elif 'errors' in error_data:
                    errors = error_data['errors']
                    if isinstance(errors, list) and errors:
                        error_message = str(errors[0])
                    else:
                        error_message = str(errors)
    except (json.JSONDecodeError, ValueError):
        # If we can't parse JSON, use the raw content
        if response.content:
            error_message = response.content.decode('utf-8', errors='ignore')[:200]
    
    # Map status codes to specific exceptions
    if response.status_code == 400:
        return BadRequestError(error_message, response, retry_after=retry_after)
    elif response.status_code == 401:
        return AuthenticationError(error_message, response, retry_after=retry_after)
    elif response.status_code == 403:
        return ForbiddenError(error_message, response, retry_after=retry_after)
    elif response.status_code == 404:
        return NotFoundError(error_message, response, retry_after=retry_after)
    elif response.status_code == 422:
        return ValidationError(error_message, response, retry_after=retry_after)
    elif response.status_code == 429:
        return RateLimitError(error_message, response, retry_after=retry_after)
    elif 500 <= response.status_code < 600:
        return ServerError(error_message, response, retry_after=retry_after)
    else:
        return AkeneoAPIError(error_message, response, retry_after=retry_after)
