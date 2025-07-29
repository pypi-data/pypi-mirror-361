"""
Base extractor class for VokroDL.

This module defines the abstract base class that all platform extractors
must implement, providing a consistent interface for video information
extraction.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Pattern
from urllib.parse import urlparse

from ..core.models import VideoInfo, Format, Subtitle, Thumbnail
from ..core.exceptions import ExtractionError


class BaseExtractor(ABC):
    """
    Abstract base class for video extractors.
    
    All platform-specific extractors must inherit from this class
    and implement the required methods.
    """
    
    # Platform identifier (must be set by subclasses)
    PLATFORM_NAME: str = ""
    
    # URL patterns that this extractor can handle
    URL_PATTERNS: List[Pattern[str]] = []
    
    # Whether this extractor supports playlists
    SUPPORTS_PLAYLISTS: bool = False
    
    # Whether this extractor requires authentication
    REQUIRES_AUTH: bool = False
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize extractor.
        
        Args:
            config: Platform-specific configuration
        """
        self.config = config or {}
        self._session = None
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Check if this extractor can handle the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if this extractor can handle the URL
        """
        for pattern in cls.URL_PATTERNS:
            if pattern.match(url):
                return True
        return False
    
    @abstractmethod
    async def extract_info(self, url: str) -> VideoInfo:
        """
        Extract video information from URL.
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo object with extracted information
            
        Raises:
            ExtractionError: If extraction fails
        """
        pass
    
    async def extract_playlist(self, url: str) -> List[VideoInfo]:
        """
        Extract playlist information from URL.
        
        Args:
            url: Playlist URL
            
        Returns:
            List of VideoInfo objects
            
        Raises:
            ExtractionError: If extraction fails or not supported
        """
        if not self.SUPPORTS_PLAYLISTS:
            raise ExtractionError(
                f"Playlist extraction not supported by {self.PLATFORM_NAME} extractor"
            )
        
        # Default implementation - subclasses should override
        raise NotImplementedError("Playlist extraction not implemented")
    
    def _extract_video_id(self, url: str) -> str:
        """
        Extract video ID from URL.
        
        Args:
            url: Video URL
            
        Returns:
            Video ID
            
        Raises:
            ExtractionError: If video ID cannot be extracted
        """
        # Default implementation - subclasses should override
        parsed = urlparse(url)
        return parsed.path.strip('/')
    
    def _build_format(
        self,
        format_id: str,
        url: str,
        container: str,
        **kwargs
    ) -> Format:
        """
        Build a Format object with common defaults.
        
        Args:
            format_id: Format identifier
            url: Download URL
            container: Container format
            **kwargs: Additional format properties
            
        Returns:
            Format object
        """
        from ..core.models import Container, FormatType
        
        # Convert string container to enum
        try:
            container_enum = Container(container.lower())
        except ValueError:
            container_enum = Container.MP4  # Default fallback
        
        # Determine format type
        format_type = FormatType.VIDEO
        if container.lower() in ['mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a']:
            format_type = FormatType.AUDIO
        
        return Format(
            format_id=format_id,
            format_type=format_type,
            container=container_enum,
            url=url,
            **kwargs
        )
    
    def _build_subtitle(
        self,
        language: str,
        language_name: str,
        url: str,
        format_type: str = "srt",
        auto_generated: bool = False
    ) -> Subtitle:
        """
        Build a Subtitle object.
        
        Args:
            language: Language code
            language_name: Human-readable language name
            url: Subtitle URL
            format_type: Subtitle format
            auto_generated: Whether subtitle is auto-generated
            
        Returns:
            Subtitle object
        """
        return Subtitle(
            language=language,
            language_name=language_name,
            url=url,
            format_type=format_type,
            auto_generated=auto_generated
        )
    
    def _build_thumbnail(
        self,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Thumbnail:
        """
        Build a Thumbnail object.
        
        Args:
            url: Thumbnail URL
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            Thumbnail object
        """
        resolution = None
        if width and height:
            resolution = f"{width}x{height}"
        
        return Thumbnail(
            url=url,
            width=width,
            height=height,
            resolution=resolution
        )
    
    def _calculate_quality_score(self, format_obj: Format) -> float:
        """
        Calculate quality score for format ranking.
        
        Args:
            format_obj: Format object
            
        Returns:
            Quality score (higher is better)
        """
        score = 0.0
        
        # Video quality scoring
        if format_obj.height:
            score += format_obj.height * 10
        
        if format_obj.fps:
            score += format_obj.fps
        
        if format_obj.bitrate:
            score += format_obj.bitrate / 1000
        
        # Audio quality scoring
        if format_obj.audio_bitrate:
            score += format_obj.audio_bitrate / 100
        
        # Codec preferences (higher scores for better codecs)
        codec_scores = {
            'h264': 100,
            'h265': 150,
            'vp9': 120,
            'av1': 140,
            'aac': 50,
            'opus': 60,
            'mp3': 30,
        }
        
        if format_obj.video_codec:
            score += codec_scores.get(format_obj.video_codec.value, 0)
        
        if format_obj.audio_codec:
            score += codec_scores.get(format_obj.audio_codec.value, 0)
        
        return score
    
    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize string for safe use in filenames and metadata.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove control characters and normalize whitespace
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _parse_duration(self, duration_str: str) -> Optional[float]:
        """
        Parse duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., "PT4M13S", "4:13", "253")
            
        Returns:
            Duration in seconds or None if parsing fails
        """
        if not duration_str:
            return None
        
        # ISO 8601 duration format (PT4M13S)
        iso_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if iso_match:
            hours, minutes, seconds = iso_match.groups()
            total_seconds = 0
            if hours:
                total_seconds += int(hours) * 3600
            if minutes:
                total_seconds += int(minutes) * 60
            if seconds:
                total_seconds += int(seconds)
            return float(total_seconds)
        
        # MM:SS or HH:MM:SS format
        time_match = re.match(r'(?:(\d+):)?(\d+):(\d+)', duration_str)
        if time_match:
            hours, minutes, seconds = time_match.groups()
            total_seconds = int(minutes) * 60 + int(seconds)
            if hours:
                total_seconds += int(hours) * 3600
            return float(total_seconds)
        
        # Plain seconds
        try:
            return float(duration_str)
        except ValueError:
            return None
    
    async def close(self):
        """Clean up extractor resources."""
        if self._session and hasattr(self._session, 'close'):
            await self._session.close()


class PlaylistExtractor(BaseExtractor):
    """
    Base class for extractors that support playlists.
    
    Provides common functionality for playlist extraction.
    """
    
    SUPPORTS_PLAYLISTS = True
    
    @abstractmethod
    async def extract_playlist_info(self, url: str) -> Dict[str, Any]:
        """
        Extract playlist metadata.
        
        Args:
            url: Playlist URL
            
        Returns:
            Dictionary with playlist information
        """
        pass
    
    @abstractmethod
    async def extract_playlist_entries(self, url: str) -> List[str]:
        """
        Extract video URLs from playlist.
        
        Args:
            url: Playlist URL
            
        Returns:
            List of video URLs
        """
        pass
    
    async def extract_playlist(self, url: str) -> List[VideoInfo]:
        """
        Extract complete playlist information.
        
        Args:
            url: Playlist URL
            
        Returns:
            List of VideoInfo objects
        """
        # Get video URLs from playlist
        video_urls = await self.extract_playlist_entries(url)
        
        # Extract info for each video
        video_infos = []
        for video_url in video_urls:
            try:
                video_info = await self.extract_info(video_url)
                video_infos.append(video_info)
            except Exception as e:
                # Log error but continue with other videos
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to extract info for {video_url}: {e}")
        
        return video_infos
