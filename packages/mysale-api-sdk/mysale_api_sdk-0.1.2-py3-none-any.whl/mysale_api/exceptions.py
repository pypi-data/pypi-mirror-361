import json
from typing import Optional, Dict, Any
import httpx


class MySaleAPIError(Exception):
    """Base exception for all MySale API errors."""
    
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


class AuthenticationError(MySaleAPIError):
    """Raised when authentication fails (401)."""
    pass


class ValidationError(MySaleAPIError):
    """Raised when request validation fails (422 - Unprocessable Entity)."""
    pass


class NotFoundError(MySaleAPIError):
    """Raised when a resource is not found (404)."""
    pass


class RateLimitError(MySaleAPIError):
    """Raised when rate limit is exceeded (429)."""
    pass


class ServerError(MySaleAPIError):
    """Raised when server error occurs (5xx)."""
    pass


class ForbiddenError(MySaleAPIError):
    """Raised when access is forbidden (403)."""
    pass


class BadRequestError(MySaleAPIError):
    """Raised when request is malformed (400)."""
    pass


class ConflictError(MySaleAPIError):
    """Raised when there is a conflict with the current state (409)."""
    pass


class UnprocessableEntityError(MySaleAPIError):
    """Raised when the request is well-formed but contains semantic errors (422)."""
    pass


class MethodNotAllowedError(MySaleAPIError):
    """Raised when HTTP method is not allowed (405)."""
    pass


class NotAcceptableError(MySaleAPIError):
    """Raised when the requested format is not acceptable (406)."""
    pass


class ServiceUnavailableError(MySaleAPIError):
    """Raised when the service is temporarily unavailable (503)."""
    pass


def create_exception_from_response(
    response: httpx.Response, 
    method: str, 
    url: str, 
    **kwargs
) -> MySaleAPIError:
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
                elif 'error' in error_data:
                    error_message = error_data['error']
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
    elif response.status_code == 405:
        return MethodNotAllowedError(error_message, response, retry_after=retry_after)
    elif response.status_code == 406:
        return NotAcceptableError(error_message, response, retry_after=retry_after)
    elif response.status_code == 409:
        return ConflictError(error_message, response, retry_after=retry_after)
    elif response.status_code == 422:
        return UnprocessableEntityError(error_message, response, retry_after=retry_after)
    elif response.status_code == 429:
        return RateLimitError(error_message, response, retry_after=retry_after)
    elif response.status_code == 503:
        return ServiceUnavailableError(error_message, response, retry_after=retry_after)
    elif 500 <= response.status_code < 600:
        return ServerError(error_message, response, retry_after=retry_after)
    else:
        return MySaleAPIError(error_message, response, retry_after=retry_after)
