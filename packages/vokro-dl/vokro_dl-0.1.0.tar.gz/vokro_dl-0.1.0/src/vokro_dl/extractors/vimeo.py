"""
Vimeo extractor for VokroDL.

This module provides video extraction functionality for Vimeo videos.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseExtractor
from ..core.models import VideoInfo, Format, Subtitle, Thumbnail, Container, Codec
from ..core.exceptions import ExtractionError


class VimeoExtractor(BaseExtractor):
    """Vimeo video extractor."""
    
    PLATFORM_NAME = "vimeo"
    
    URL_PATTERNS = [
        re.compile(r'https?://(?:www\.)?vimeo\.com/\d+'),
        re.compile(r'https?://player\.vimeo\.com/video/\d+'),
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Vimeo extractor."""
        super().__init__(config)
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            self._session = aiohttp.ClientSession(headers=headers)
        
        return self._session
    
    def _extract_video_id(self, url: str) -> str:
        """Extract Vimeo video ID from URL."""
        patterns = [
            r'vimeo\.com/(\d+)',
            r'player\.vimeo\.com/video/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ExtractionError(f"Could not extract video ID from URL: {url}")
    
    async def extract_info(self, url: str) -> VideoInfo:
        """Extract video information from Vimeo URL."""
        video_id = self._extract_video_id(url)
        
        try:
            session = await self._get_session()
            
            # Get video page
            video_url = f"https://vimeo.com/{video_id}"
            async with session.get(video_url) as response:
                response.raise_for_status()
                html_content = await response.text()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            uploader = self._extract_uploader(soup)
            duration = self._extract_duration(soup, html_content)
            view_count = self._extract_view_count(html_content)
            upload_date = self._extract_upload_date(soup)
            
            # Extract formats
            formats = await self._extract_formats(video_id, session, html_content)
            
            # Extract thumbnails
            thumbnails = self._extract_thumbnails(soup)
            
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
                subtitles=[],  # Vimeo subtitle extraction would be implemented here
                thumbnails=thumbnails,
                webpage_url=video_url,
                original_url=url,
            )
            
        except Exception as e:
            raise ExtractionError(f"Failed to extract Vimeo video info: {str(e)}", url=url) from e
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract video title."""
        # Try meta tag first
        title_tag = soup.find('meta', property='og:title')
        if title_tag and title_tag.get('content'):
            return self._sanitize_string(title_tag['content'])
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
            # Remove " on Vimeo" suffix
            title = re.sub(r' on Vimeo$', '', title)
            return self._sanitize_string(title)
        
        return "Unknown Title"
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract video description."""
        desc_tag = soup.find('meta', property='og:description')
        if desc_tag and desc_tag.get('content'):
            return self._sanitize_string(desc_tag['content'])
        
        return None
    
    def _extract_uploader(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract uploader name."""
        # Try to find uploader in meta tags
        uploader_tag = soup.find('meta', property='video:director')
        if uploader_tag and uploader_tag.get('content'):
            return self._sanitize_string(uploader_tag['content'])
        
        return None
    
    def _extract_duration(self, soup: BeautifulSoup, html_content: str) -> Optional[float]:
        """Extract video duration."""
        # Try meta tag
        duration_tag = soup.find('meta', property='video:duration')
        if duration_tag and duration_tag.get('content'):
            try:
                return float(duration_tag['content'])
            except ValueError:
                pass
        
        # Try to find in JSON data
        duration_match = re.search(r'"duration":(\d+)', html_content)
        if duration_match:
            return float(duration_match.group(1))
        
        return None
    
    def _extract_view_count(self, html_content: str) -> Optional[int]:
        """Extract view count."""
        view_match = re.search(r'"plays":(\d+)', html_content)
        if view_match:
            return int(view_match.group(1))
        
        return None
    
    def _extract_upload_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract upload date."""
        date_tag = soup.find('meta', property='video:release_date')
        if date_tag and date_tag.get('content'):
            try:
                return datetime.fromisoformat(date_tag['content'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        return None
    
    async def _extract_formats(
        self, 
        video_id: str, 
        session: aiohttp.ClientSession,
        html_content: str
    ) -> List[Format]:
        """Extract available formats."""
        formats = []
        
        # Try to find config JSON in HTML
        config_match = re.search(r'window\.vimeoPlayerConfig\s*=\s*({.+?});', html_content)
        if not config_match:
            # Fallback: try to get config from API
            try:
                config_url = f"https://player.vimeo.com/video/{video_id}/config"
                async with session.get(config_url) as response:
                    if response.status == 200:
                        config_data = await response.json()
                    else:
                        config_data = {}
            except:
                config_data = {}
        else:
            try:
                config_data = json.loads(config_match.group(1))
            except json.JSONDecodeError:
                config_data = {}
        
        # Extract progressive formats
        progressive_files = config_data.get('request', {}).get('files', {}).get('progressive', [])
        
        for file_info in progressive_files:
            quality = file_info.get('quality', 'unknown')
            width = file_info.get('width')
            height = file_info.get('height')
            url = file_info.get('url')
            
            if not url:
                continue
            
            format_obj = self._build_format(
                format_id=f"progressive-{quality}",
                url=url,
                container="mp4",
                width=width,
                height=height,
                video_codec=Codec.H264,
                audio_codec=Codec.AAC_CODEC,
            )
            format_obj.quality_score = self._calculate_quality_score(format_obj)
            formats.append(format_obj)
        
        # Extract HLS formats if available
        hls_data = config_data.get('request', {}).get('files', {}).get('hls')
        if hls_data and hls_data.get('url'):
            # In a real implementation, would parse HLS manifest
            hls_format = self._build_format(
                format_id="hls",
                url=hls_data['url'],
                container="mp4",
                video_codec=Codec.H264,
                audio_codec=Codec.AAC_CODEC,
            )
            hls_format.quality_score = self._calculate_quality_score(hls_format)
            formats.append(hls_format)
        
        return formats
    
    def _extract_thumbnails(self, soup: BeautifulSoup) -> List[Thumbnail]:
        """Extract thumbnail URLs."""
        thumbnails = []
        
        # Try meta tag
        thumb_tag = soup.find('meta', property='og:image')
        if thumb_tag and thumb_tag.get('content'):
            thumbnail = self._build_thumbnail(url=thumb_tag['content'])
            thumbnails.append(thumbnail)
        
        return thumbnails
