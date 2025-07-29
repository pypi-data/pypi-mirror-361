"""
Data models for VokroDL.

This module defines Pydantic models for type-safe data structures
used throughout the library.
"""

from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator, root_validator


class Quality(str, Enum):
    """Video quality options."""
    BEST = "best"
    WORST = "worst"
    AUDIO_ONLY = "audio_only"
    # Specific resolutions
    RESOLUTION_144P = "144p"
    RESOLUTION_240P = "240p"
    RESOLUTION_360P = "360p"
    RESOLUTION_480P = "480p"
    RESOLUTION_720P = "720p"
    RESOLUTION_1080P = "1080p"
    RESOLUTION_1440P = "1440p"
    RESOLUTION_2160P = "2160p"
    RESOLUTION_4320P = "4320p"


class FormatType(str, Enum):
    """Media format types."""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"


class Container(str, Enum):
    """Container formats."""
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    AVI = "avi"
    MOV = "mov"
    FLV = "flv"
    # Audio containers
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    FLAC = "flac"
    WAV = "wav"
    M4A = "m4a"


class Codec(str, Enum):
    """Media codecs."""
    # Video codecs
    H264 = "h264"
    H265 = "h265"
    VP8 = "vp8"
    VP9 = "vp9"
    AV1 = "av1"
    # Audio codecs
    AAC_CODEC = "aac"
    MP3_CODEC = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    FLAC_CODEC = "flac"


class Format(BaseModel):
    """Represents a media format."""
    
    format_id: str = Field(..., description="Unique format identifier")
    format_type: FormatType = Field(..., description="Type of format")
    container: Container = Field(..., description="Container format")
    
    # Video properties
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    fps: Optional[float] = Field(None, description="Frames per second")
    video_codec: Optional[Codec] = Field(None, description="Video codec")
    
    # Audio properties
    audio_codec: Optional[Codec] = Field(None, description="Audio codec")
    audio_bitrate: Optional[int] = Field(None, description="Audio bitrate in kbps")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate in Hz")
    
    # Common properties
    bitrate: Optional[int] = Field(None, description="Total bitrate in kbps")
    filesize: Optional[int] = Field(None, description="File size in bytes")
    url: str = Field(..., description="Direct download URL")
    
    # Quality metrics
    quality_score: float = Field(0.0, description="Quality score for ranking")
    
    @property
    def resolution(self) -> Optional[str]:
        """Get resolution string (e.g., '1920x1080')."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return None
    
    @property
    def quality_label(self) -> Optional[str]:
        """Get quality label (e.g., '1080p')."""
        if self.height:
            return f"{self.height}p"
        return None


class Subtitle(BaseModel):
    """Represents subtitle information."""
    
    language: str = Field(..., description="Language code (e.g., 'en', 'es')")
    language_name: str = Field(..., description="Human-readable language name")
    url: str = Field(..., description="Subtitle download URL")
    format_type: str = Field(..., description="Subtitle format (srt, vtt, etc.)")
    auto_generated: bool = Field(False, description="Whether subtitle is auto-generated")


class Thumbnail(BaseModel):
    """Represents thumbnail information."""
    
    url: str = Field(..., description="Thumbnail URL")
    width: Optional[int] = Field(None, description="Thumbnail width")
    height: Optional[int] = Field(None, description="Thumbnail height")
    resolution: Optional[str] = Field(None, description="Resolution string")


class VideoInfo(BaseModel):
    """Complete video information."""
    
    # Basic information
    id: str = Field(..., description="Video ID")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    url: str = Field(..., description="Original video URL")
    
    # Platform information
    platform: str = Field(..., description="Platform name (youtube, vimeo, etc.)")
    uploader: Optional[str] = Field(None, description="Video uploader/channel")
    uploader_id: Optional[str] = Field(None, description="Uploader ID")
    uploader_url: Optional[str] = Field(None, description="Uploader profile URL")
    
    # Temporal information
    duration: Optional[float] = Field(None, description="Duration in seconds")
    upload_date: Optional[datetime] = Field(None, description="Upload date")
    view_count: Optional[int] = Field(None, description="View count")
    like_count: Optional[int] = Field(None, description="Like count")
    
    # Media information
    formats: List[Format] = Field(default_factory=list, description="Available formats")
    subtitles: List[Subtitle] = Field(default_factory=list, description="Available subtitles")
    thumbnails: List[Thumbnail] = Field(default_factory=list, description="Available thumbnails")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Video tags")
    categories: List[str] = Field(default_factory=list, description="Video categories")
    
    # Technical information
    webpage_url: str = Field(..., description="Webpage URL")
    original_url: str = Field(..., description="Original requested URL")
    
    @validator('url', 'webpage_url', 'original_url')
    def validate_url(cls, v):
        """Validate URL format."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {v}")
        return v
    
    def get_best_format(
        self, 
        quality: Quality = Quality.BEST,
        format_type: FormatType = FormatType.VIDEO
    ) -> Optional[Format]:
        """Get the best format matching criteria."""
        matching_formats = [f for f in self.formats if f.format_type == format_type]
        
        if not matching_formats:
            return None
        
        if quality == Quality.BEST:
            return max(matching_formats, key=lambda f: f.quality_score)
        elif quality == Quality.WORST:
            return min(matching_formats, key=lambda f: f.quality_score)
        else:
            # Try to match specific quality
            target_height = None
            if quality.value.endswith('p'):
                try:
                    target_height = int(quality.value[:-1])
                except ValueError:
                    pass
            
            if target_height:
                exact_matches = [f for f in matching_formats if f.height == target_height]
                if exact_matches:
                    return max(exact_matches, key=lambda f: f.quality_score)
        
        # Fallback to best
        return max(matching_formats, key=lambda f: f.quality_score)


class DownloadProgress(BaseModel):
    """Download progress information."""
    
    # Progress metrics
    downloaded_bytes: int = Field(0, description="Bytes downloaded")
    total_bytes: Optional[int] = Field(None, description="Total bytes to download")
    percent: float = Field(0.0, description="Download percentage (0-100)")
    
    # Speed metrics
    speed: float = Field(0.0, description="Download speed in bytes/second")
    eta: Optional[timedelta] = Field(None, description="Estimated time remaining")
    
    # Status information
    status: str = Field("downloading", description="Current status")
    filename: Optional[str] = Field(None, description="Output filename")
    
    # Timing information
    elapsed: timedelta = Field(default_factory=lambda: timedelta(0), description="Elapsed time")
    started_at: datetime = Field(default_factory=datetime.now, description="Start time")
    
    @property
    def speed_human(self) -> str:
        """Human-readable speed string."""
        if self.speed < 1024:
            return f"{self.speed:.1f} B/s"
        elif self.speed < 1024 * 1024:
            return f"{self.speed / 1024:.1f} KB/s"
        elif self.speed < 1024 * 1024 * 1024:
            return f"{self.speed / (1024 * 1024):.1f} MB/s"
        else:
            return f"{self.speed / (1024 * 1024 * 1024):.1f} GB/s"
    
    @property
    def size_human(self) -> str:
        """Human-readable size string."""
        if not self.total_bytes:
            return f"{self.downloaded_bytes:,} bytes"
        
        def format_bytes(bytes_val):
            if bytes_val < 1024:
                return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024:
                return f"{bytes_val / 1024:.1f} KB"
            elif bytes_val < 1024 * 1024 * 1024:
                return f"{bytes_val / (1024 * 1024):.1f} MB"
            else:
                return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"
        
        return f"{format_bytes(self.downloaded_bytes)} / {format_bytes(self.total_bytes)}"
