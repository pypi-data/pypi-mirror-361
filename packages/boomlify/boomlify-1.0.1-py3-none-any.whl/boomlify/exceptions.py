"""
Custom exceptions for the Boomlify client.
"""

from typing import Optional, Dict, Any


class BoomlifyError(Exception):
    """Base exception for all Boomlify errors."""
    
    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.response = response


class BoomlifyAPIError(BoomlifyError):
    """Exception raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.status_code = status_code


class BoomlifyAuthError(BoomlifyAPIError):
    """Exception raised for authentication errors (401, 403)."""
    pass


class BoomlifyNotFoundError(BoomlifyAPIError):
    """Exception raised when a resource is not found (404)."""
    pass


class BoomlifyRateLimitError(BoomlifyAPIError):
    """Exception raised when rate limit is exceeded (429)."""
    
    def __init__(self, message: str, status_code: int, retry_after: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class BoomlifyTimeoutError(BoomlifyError):
    """Exception raised when a request times out."""
    pass


class BoomlifyValidationError(BoomlifyError):
    """Exception raised for client-side validation errors."""
    pass 