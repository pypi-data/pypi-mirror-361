"""
Generic extractor for VokroDL.

This module provides a fallback extractor that attempts to extract
video information from any website using common patterns and heuristics.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseExtractor
from ..core.models import VideoInfo, Format, Thumbnail, Container, Codec
from ..core.exceptions import ExtractionError


class GenericExtractor(BaseExtractor):
    """Generic extractor for unknown platforms."""
    
    PLATFORM_NAME = "generic"
    
    # This extractor can handle any URL as a fallback
    URL_PATTERNS = [
        re.compile(r'https?://.*'),
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize generic extractor."""
        super().__init__(config)
        self._session = None
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Generic extractor can handle any URL but with lowest priority."""
        # Only handle if no other extractor can handle it
        return True
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            self._session = aiohttp.ClientSession(headers=headers)
        
        return self._session
    
    async def extract_info(self, url: str) -> VideoInfo:
        """Extract video information using generic methods."""
        try:
            session = await self._get_session()
            
            # Get webpage
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            duration = self._extract_duration(soup, html_content)
            
            # Extract video URLs
            formats = await self._extract_formats(soup, html_content, url, session)
            
            if not formats:
                raise ExtractionError("No video formats found")
            
            # Extract thumbnails
            thumbnails = self._extract_thumbnails(soup, url)
            
            # Generate video ID from URL
            video_id = self._generate_video_id(url)
            
            # Determine platform from URL
            platform = self._detect_platform(url)
            
            return VideoInfo(
                id=video_id,
                title=title,
                description=description,
                url=url,
                platform=platform,
                duration=duration,
                formats=formats,
                subtitles=[],
                thumbnails=thumbnails,
                webpage_url=url,
                original_url=url,
            )
            
        except Exception as e:
            raise ExtractionError(f"Failed to extract video info: {str(e)}", url=url) from e
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try various meta tags
        for property_name in ['og:title', 'twitter:title']:
            title_tag = soup.find('meta', property=property_name)
            if title_tag and title_tag.get('content'):
                return self._sanitize_string(title_tag['content'])
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            return self._sanitize_string(title_tag.get_text())
        
        return "Unknown Title"
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description."""
        for property_name in ['og:description', 'twitter:description', 'description']:
            desc_tag = soup.find('meta', attrs={'name': property_name}) or \
                      soup.find('meta', property=property_name)
            if desc_tag and desc_tag.get('content'):
                return self._sanitize_string(desc_tag['content'])
        
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
        
        # Try to find duration in JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'duration' in data:
                    duration_str = data['duration']
                    return self._parse_duration(duration_str)
            except (json.JSONDecodeError, KeyError):
                continue
        
        return None
    
    async def _extract_formats(
        self, 
        soup: BeautifulSoup, 
        html_content: str, 
        base_url: str,
        session: aiohttp.ClientSession
    ) -> List[Format]:
        """Extract video formats using various methods."""
        formats = []
        
        # Method 1: Look for HTML5 video tags
        video_tags = soup.find_all('video')
        for video_tag in video_tags:
            # Check for direct src
            if video_tag.get('src'):
                video_url = urljoin(base_url, video_tag['src'])
                format_obj = await self._create_format_from_url(video_url, session)
                if format_obj:
                    formats.append(format_obj)
            
            # Check for source tags
            source_tags = video_tag.find_all('source')
            for source_tag in source_tags:
                if source_tag.get('src'):
                    video_url = urljoin(base_url, source_tag['src'])
                    format_obj = await self._create_format_from_url(video_url, session)
                    if format_obj:
                        formats.append(format_obj)
        
        # Method 2: Look for common video file extensions in links
        video_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.m4v']
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if any(href.lower().endswith(ext) for ext in video_extensions):
                video_url = urljoin(base_url, href)
                format_obj = await self._create_format_from_url(video_url, session)
                if format_obj:
                    formats.append(format_obj)
        
        # Method 3: Look for video URLs in JavaScript/JSON
        video_url_patterns = [
            r'"(?:video_url|videoUrl|src)"\s*:\s*"([^"]+\.(?:mp4|webm|mkv|avi|mov|flv|m4v)[^"]*)"',
            r"'(?:video_url|videoUrl|src)'\s*:\s*'([^']+\.(?:mp4|webm|mkv|avi|mov|flv|m4v)[^']*)'",
            r'(?:video_url|videoUrl|src):\s*"([^"]+\.(?:mp4|webm|mkv|avi|mov|flv|m4v)[^"]*)"',
        ]
        
        for pattern in video_url_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                video_url = urljoin(base_url, match)
                format_obj = await self._create_format_from_url(video_url, session)
                if format_obj:
                    formats.append(format_obj)
        
        # Remove duplicates
        seen_urls = set()
        unique_formats = []
        for format_obj in formats:
            if format_obj.url not in seen_urls:
                seen_urls.add(format_obj.url)
                unique_formats.append(format_obj)
        
        return unique_formats
    
    async def _create_format_from_url(
        self, 
        video_url: str, 
        session: aiohttp.ClientSession
    ) -> Optional[Format]:
        """Create format object from video URL."""
        try:
            # Get file extension
            parsed_url = urlparse(video_url)
            path = parsed_url.path.lower()
            
            # Determine container from extension
            if path.endswith('.mp4'):
                container = Container.MP4
            elif path.endswith('.webm'):
                container = Container.WEBM
            elif path.endswith('.mkv'):
                container = Container.MKV
            elif path.endswith('.avi'):
                container = Container.AVI
            elif path.endswith('.mov'):
                container = Container.MOV
            elif path.endswith('.flv'):
                container = Container.FLV
            else:
                container = Container.MP4  # Default
            
            # Try to get content length
            try:
                async with session.head(video_url) as response:
                    if response.status == 200:
                        content_length = response.headers.get('content-length')
                        filesize = int(content_length) if content_length else None
                    else:
                        filesize = None
            except:
                filesize = None
            
            # Create format
            format_obj = self._build_format(
                format_id=f"generic-{container.value}",
                url=video_url,
                container=container.value,
                filesize=filesize,
                video_codec=Codec.H264,  # Assume H264
                audio_codec=Codec.AAC_CODEC,  # Assume AAC
            )
            
            format_obj.quality_score = self._calculate_quality_score(format_obj)
            return format_obj
            
        except Exception:
            return None
    
    def _extract_thumbnails(self, soup: BeautifulSoup, base_url: str) -> List[Thumbnail]:
        """Extract thumbnail URLs."""
        thumbnails = []
        
        # Try meta tags
        for property_name in ['og:image', 'twitter:image']:
            thumb_tag = soup.find('meta', property=property_name)
            if thumb_tag and thumb_tag.get('content'):
                thumb_url = urljoin(base_url, thumb_tag['content'])
                thumbnail = self._build_thumbnail(url=thumb_url)
                thumbnails.append(thumbnail)
        
        # Try video poster attribute
        video_tags = soup.find_all('video')
        for video_tag in video_tags:
            if video_tag.get('poster'):
                thumb_url = urljoin(base_url, video_tag['poster'])
                thumbnail = self._build_thumbnail(url=thumb_url)
                thumbnails.append(thumbnail)
        
        return thumbnails
    
    def _generate_video_id(self, url: str) -> str:
        """Generate a video ID from URL."""
        parsed = urlparse(url)
        # Use domain + path as ID
        return f"{parsed.netloc}{parsed.path}".replace('/', '_').replace('.', '_')
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform name from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extract main domain name
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            return domain_parts[-2]  # e.g., 'example' from 'example.com'
        
        return domain
