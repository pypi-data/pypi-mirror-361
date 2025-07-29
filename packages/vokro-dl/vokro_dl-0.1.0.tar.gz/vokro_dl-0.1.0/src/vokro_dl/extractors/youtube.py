"""
YouTube extractor for VokroDL.

This module provides video extraction functionality for YouTube videos
and playlists with support for various formats and qualities.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import parse_qs, urlparse

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseExtractor, PlaylistExtractor
from ..core.models import VideoInfo, Format, Subtitle, Thumbnail, Container, Codec, FormatType
from ..core.exceptions import ExtractionError


class YouTubeExtractor(PlaylistExtractor):
    """YouTube video and playlist extractor."""
    
    PLATFORM_NAME = "youtube"
    
    URL_PATTERNS = [
        re.compile(r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+'),
        re.compile(r'https?://(?:www\.)?youtube\.com/embed/[\w-]+'),
        re.compile(r'https?://youtu\.be/[\w-]+'),
        re.compile(r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+'),
        re.compile(r'https?://(?:www\.)?youtube\.com/channel/[\w-]+'),
        re.compile(r'https?://(?:www\.)?youtube\.com/user/[\w-]+'),
        re.compile(r'https?://(?:www\.)?youtube\.com/c/[\w-]+'),
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize YouTube extractor."""
        super().__init__(config)
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self._session = aiohttp.ClientSession(headers=headers)
        
        return self._session
    
    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'embed/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ExtractionError(f"Could not extract video ID from URL: {url}")
    
    async def extract_info(self, url: str) -> VideoInfo:
        """Extract video information from YouTube URL."""
        video_id = self._extract_video_id(url)
        
        try:
            session = await self._get_session()
            
            # Get video page
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            async with session.get(video_url) as response:
                response.raise_for_status()
                html_content = await response.text()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic information
            title = self._extract_title(soup, html_content)
            description = self._extract_description(soup, html_content)
            uploader = self._extract_uploader(soup, html_content)
            duration = self._extract_duration(soup, html_content)
            view_count = self._extract_view_count(soup, html_content)
            upload_date = self._extract_upload_date(soup, html_content)
            
            # Extract formats (simplified - in real implementation would parse player response)
            formats = await self._extract_formats(video_id, session)
            
            # Extract subtitles
            subtitles = await self._extract_subtitles(video_id, session)
            
            # Extract thumbnails
            thumbnails = self._extract_thumbnails(video_id)
            
            return VideoInfo(
                id=video_id,
                title=title,
                description=description,
                url=video_url,
                platform=self.PLATFORM_NAME,
                uploader=uploader,
                duration=duration,
                view_count=view_count,
                upload_date=upload_date,
                formats=formats,
                subtitles=subtitles,
                thumbnails=thumbnails,
                webpage_url=video_url,
                original_url=url,
            )
            
        except Exception as e:
            raise ExtractionError(f"Failed to extract YouTube video info: {str(e)}", url=url) from e
    
    def _extract_title(self, soup: BeautifulSoup, html_content: str) -> str:
        """Extract video title."""
        # Try meta tag first
        title_tag = soup.find('meta', property='og:title')
        if title_tag and title_tag.get('content'):
            return self._sanitize_string(title_tag['content'])
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
            # Remove " - YouTube" suffix
            title = re.sub(r' - YouTube$', '', title)
            return self._sanitize_string(title)
        
        # Fallback to regex search in HTML
        title_match = re.search(r'"title":"([^"]+)"', html_content)
        if title_match:
            return self._sanitize_string(title_match.group(1))
        
        return "Unknown Title"
    
    def _extract_description(self, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """Extract video description."""
        desc_tag = soup.find('meta', property='og:description')
        if desc_tag and desc_tag.get('content'):
            return self._sanitize_string(desc_tag['content'])
        
        return None
    
    def _extract_uploader(self, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """Extract uploader/channel name."""
        # Try to find channel name in various places
        uploader_match = re.search(r'"ownerChannelName":"([^"]+)"', html_content)
        if uploader_match:
            return self._sanitize_string(uploader_match.group(1))
        
        return None
    
    def _extract_duration(self, soup: BeautifulSoup, html_content: str) -> Optional[float]:
        """Extract video duration."""
        # Try meta tag
        duration_tag = soup.find('meta', itemprop='duration')
        if duration_tag and duration_tag.get('content'):
            return self._parse_duration(duration_tag['content'])
        
        # Try regex search
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', html_content)
        if duration_match:
            return float(duration_match.group(1))
        
        return None
    
    def _extract_view_count(self, soup: BeautifulSoup, html_content: str) -> Optional[int]:
        """Extract view count."""
        view_match = re.search(r'"viewCount":"(\d+)"', html_content)
        if view_match:
            return int(view_match.group(1))
        
        return None
    
    def _extract_upload_date(self, soup: BeautifulSoup, html_content: str) -> Optional[datetime]:
        """Extract upload date."""
        date_tag = soup.find('meta', itemprop='uploadDate')
        if date_tag and date_tag.get('content'):
            try:
                return datetime.fromisoformat(date_tag['content'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        return None
    
    async def _extract_formats(self, video_id: str, session: aiohttp.ClientSession) -> List[Format]:
        """Extract available formats (simplified implementation)."""
        # This is a simplified implementation
        # In a real implementation, you would need to:
        # 1. Extract the player response JSON
        # 2. Parse streaming data
        # 3. Handle signature decryption
        # 4. Extract all available formats with proper metadata
        
        formats = []
        
        # Add some example formats (in real implementation, these would be extracted)
        base_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Example HD format
        hd_format = self._build_format(
            format_id="22",
            url=base_url,  # This would be the actual stream URL
            container="mp4",
            width=1280,
            height=720,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=1000,
            audio_bitrate=128,
        )
        hd_format.quality_score = self._calculate_quality_score(hd_format)
        formats.append(hd_format)
        
        # Example SD format
        sd_format = self._build_format(
            format_id="18",
            url=base_url,
            container="mp4",
            width=640,
            height=360,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=500,
            audio_bitrate=96,
        )
        sd_format.quality_score = self._calculate_quality_score(sd_format)
        formats.append(sd_format)
        
        return formats
    
    async def _extract_subtitles(self, video_id: str, session: aiohttp.ClientSession) -> List[Subtitle]:
        """Extract available subtitles."""
        # Simplified implementation
        # In real implementation, would extract from player response
        return []
    
    def _extract_thumbnails(self, video_id: str) -> List[Thumbnail]:
        """Extract thumbnail URLs."""
        thumbnails = []
        
        # YouTube thumbnail URLs follow a predictable pattern
        base_url = f"https://img.youtube.com/vi/{video_id}"
        
        thumbnail_configs = [
            ("maxresdefault.jpg", 1280, 720),
            ("hqdefault.jpg", 480, 360),
            ("mqdefault.jpg", 320, 180),
            ("default.jpg", 120, 90),
        ]
        
        for filename, width, height in thumbnail_configs:
            thumbnail = self._build_thumbnail(
                url=f"{base_url}/{filename}",
                width=width,
                height=height
            )
            thumbnails.append(thumbnail)
        
        return thumbnails
    
    async def extract_playlist_info(self, url: str) -> Dict[str, Any]:
        """Extract playlist metadata."""
        # Extract playlist ID
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        playlist_id = query_params.get('list', [None])[0]
        
        if not playlist_id:
            raise ExtractionError("Could not extract playlist ID from URL")
        
        return {
            'id': playlist_id,
            'title': 'YouTube Playlist',  # Would extract actual title
            'description': None,
            'uploader': None,
        }
    
    async def extract_playlist_entries(self, url: str) -> List[str]:
        """Extract video URLs from playlist."""
        # Simplified implementation
        # In real implementation, would parse playlist page and extract all video IDs
        return []
