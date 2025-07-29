"""
Exception classes for VokroDL.

This module defines all custom exceptions used throughout the library,
providing clear error hierarchies and user-friendly error messages.
"""

from typing import Optional, Dict, Any


class VokroDLError(Exception):
    """Base exception for all VokroDL errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        result = self.message
        if self.suggestion:
            result += f"\n\nSuggestion: {self.suggestion}"
        return result


class DownloadError(VokroDLError):
    """Raised when a download operation fails."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.url = url
        self.status_code = status_code


class ExtractionError(VokroDLError):
    """Raised when video information extraction fails."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.url = url
        self.platform = platform


class NetworkError(VokroDLError):
    """Raised when network operations fail."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.url = url
        self.timeout = timeout


class ConfigurationError(VokroDLError):
    """Raised when configuration is invalid."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_value = config_value


class UnsupportedPlatformError(ExtractionError):
    """Raised when a platform is not supported."""
    
    def __init__(self, url: str, **kwargs):
        message = f"Platform not supported for URL: {url}"
        suggestion = "Check if the platform is supported or consider adding a custom extractor."
        super().__init__(message, url=url, suggestion=suggestion, **kwargs)


class QualityNotAvailableError(DownloadError):
    """Raised when requested quality is not available."""
    
    def __init__(
        self,
        requested_quality: str,
        available_qualities: list,
        **kwargs
    ):
        message = f"Quality '{requested_quality}' not available. Available: {', '.join(available_qualities)}"
        suggestion = f"Try one of the available qualities: {', '.join(available_qualities)}"
        super().__init__(message, suggestion=suggestion, **kwargs)
        self.requested_quality = requested_quality
        self.available_qualities = available_qualities


class AuthenticationError(VokroDLError):
    """Raised when authentication fails."""
    
    def __init__(self, platform: str, **kwargs):
        message = f"Authentication failed for {platform}"
        suggestion = "Check your credentials or authentication method."
        super().__init__(message, suggestion=suggestion, **kwargs)
        self.platform = platform


class RateLimitError(NetworkError):
    """Raised when rate limiting is encountered."""
    
    def __init__(
        self,
        platform: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        message = f"Rate limit exceeded for {platform}"
        if retry_after:
            message += f". Retry after {retry_after} seconds."
            suggestion = f"Wait {retry_after} seconds before retrying."
        else:
            suggestion = "Wait before retrying or reduce request frequency."
        
        super().__init__(message, suggestion=suggestion, **kwargs)
        self.platform = platform
        self.retry_after = retry_after


class PostProcessingError(VokroDLError):
    """Raised when post-processing operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.file_path = file_path


class SubtitleError(VokroDLError):
    """Raised when subtitle operations fail."""
    
    def __init__(
        self,
        message: str,
        language: Optional[str] = None,
        format_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.language = language
        self.format_type = format_type
