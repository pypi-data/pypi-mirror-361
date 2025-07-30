"""
Exception classes for Lync Attribution Python SDK.
"""

from typing import Optional, Dict, Any


class LyncError(Exception):
    """Base exception for all Lync Attribution errors."""
    pass


class LyncConfigurationError(LyncError):
    """Raised when there's a configuration error."""
    pass


class LyncAPIError(LyncError):
    """Raised when the Lync API returns an error."""
    
    def __init__(
        self, 
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.status_code:
            return f"HTTP {self.status_code}: {base_msg}"
        return base_msg


class LyncTimeoutError(LyncError):
    """Raised when a request times out."""
    pass


class LyncConnectionError(LyncError):
    """Raised when there's a connection error."""
    pass


class LyncValidationError(LyncError):
    """Raised when input validation fails."""
    pass


class LyncRateLimitError(LyncAPIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after 