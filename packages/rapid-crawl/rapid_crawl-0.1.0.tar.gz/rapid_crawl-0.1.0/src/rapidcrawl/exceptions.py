"""
Custom exceptions for the RapidCrawl package.
"""

from typing import Optional, Dict, Any


class RapidCrawlError(Exception):
    """Base exception for all RapidCrawl errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(RapidCrawlError):
    """Raised when API authentication fails."""
    
    def __init__(self, message: str = "Invalid API key or authentication failed"):
        super().__init__(message)


class RateLimitError(RapidCrawlError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
    ):
        details = {}
        if retry_after is not None:
            details["retry_after"] = retry_after
        if limit is not None:
            details["limit"] = limit
        if remaining is not None:
            details["remaining"] = remaining
            
        super().__init__(message, details)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


class ScrapingError(RapidCrawlError):
    """Raised when web scraping encounters an error."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        error_type: Optional[str] = None,
    ):
        details = {}
        if url:
            details["url"] = url
        if status_code is not None:
            details["status_code"] = status_code
        if error_type:
            details["error_type"] = error_type
            
        super().__init__(message, details)
        self.url = url
        self.status_code = status_code
        self.error_type = error_type


class ValidationError(RapidCrawlError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
            
        super().__init__(message, details)
        self.field = field
        self.value = value


class TimeoutError(RapidCrawlError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str = "Operation timed out", timeout: Optional[float] = None):
        details = {}
        if timeout is not None:
            details["timeout"] = timeout
            
        super().__init__(message, details)
        self.timeout = timeout


class NetworkError(RapidCrawlError):
    """Raised when a network error occurs."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        details = {}
        if cause:
            details["cause"] = str(cause)
            details["cause_type"] = type(cause).__name__
            
        super().__init__(message, details)
        self.cause = cause


class ConfigurationError(RapidCrawlError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
            
        super().__init__(message, details)
        self.config_key = config_key