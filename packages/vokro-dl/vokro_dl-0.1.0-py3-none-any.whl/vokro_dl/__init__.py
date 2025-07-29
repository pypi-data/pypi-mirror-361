"""
VokroDL - Advanced Video Downloading Library

A comprehensive video downloading library that surpasses yt-dlp in terms of 
usability and functionality.
"""

from .core.downloader import VokroDL
from .core.config import DownloadConfig, GlobalConfig
from .core.exceptions import (
    VokroDLError,
    DownloadError,
    ExtractionError,
    NetworkError,
    ConfigurationError,
)
from .core.models import (
    VideoInfo,
    DownloadProgress,
    Quality,
    Format,
    Subtitle,
)

__version__ = "0.1.0"
__author__ = "Danil Borkov"
__email__ = "106639488+vokrob@users.noreply.github.com"

__all__ = [
    # Main classes
    "VokroDL",
    "DownloadConfig",
    "GlobalConfig",
    
    # Exceptions
    "VokroDLError",
    "DownloadError", 
    "ExtractionError",
    "NetworkError",
    "ConfigurationError",
    
    # Models
    "VideoInfo",
    "DownloadProgress",
    "Quality",
    "Format",
    "Subtitle",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
]
