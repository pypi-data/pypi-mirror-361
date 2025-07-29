"""
Tests for video extractors.
"""

import pytest
from unittest.mock import AsyncMock, patch
from bs4 import BeautifulSoup

from vokro_dl.extractors.base import BaseExtractor
from vokro_dl.extractors.registry import ExtractorRegistry
from vokro_dl.extractors.youtube import YouTubeExtractor
from vokro_dl.extractors.vimeo import VimeoExtractor
from vokro_dl.extractors.generic import GenericExtractor
from vokro_dl.core.models import VideoInfo, Format
from vokro_dl.core.exceptions import ExtractionError, UnsupportedPlatformError


class TestBaseExtractor:
    """Test base extractor functionality."""
    
    def test_can_handle_abstract(self):
        """Test that BaseExtractor is abstract."""
        with pytest.raises(TypeError):
            BaseExtractor()
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        class TestExtractor(BaseExtractor):
            PLATFORM_NAME = "test"
            async def extract_info(self, url): pass
        
        extractor = TestExtractor()
        
        # Test control character removal
        result = extractor._sanitize_string("Test\x00\x1fVideo")
        assert result == "TestVideo"
        
        # Test whitespace normalization
        result = extractor._sanitize_string("Test   \t\n  Video")
        assert result == "Test Video"
        
        # Test empty string
        result = extractor._sanitize_string("")
        assert result == ""
        
        # Test None
        result = extractor._sanitize_string(None)
        assert result == ""
    
    def test_parse_duration(self):
        """Test duration parsing."""
        class TestExtractor(BaseExtractor):
            PLATFORM_NAME = "test"
            async def extract_info(self, url): pass
        
        extractor = TestExtractor()
        
        # Test ISO 8601 format
        assert extractor._parse_duration("PT4M13S") == 253.0
        assert extractor._parse_duration("PT1H30M") == 5400.0
        assert extractor._parse_duration("PT45S") == 45.0
        
        # Test MM:SS format
        assert extractor._parse_duration("4:13") == 253.0
        assert extractor._parse_duration("1:30:45") == 5445.0
        
        # Test plain seconds
        assert extractor._parse_duration("253") == 253.0
        
        # Test invalid format
        assert extractor._parse_duration("invalid") is None
        assert extractor._parse_duration("") is None
    
    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        class TestExtractor(BaseExtractor):
            PLATFORM_NAME = "test"
            async def extract_info(self, url): pass
        
        extractor = TestExtractor()
        
        from vokro_dl.core.models import Format, Container, Codec, FormatType
        
        # High quality format
        hq_format = Format(
            format_id="hq",
            format_type=FormatType.VIDEO,
            container=Container.MP4,
            url="test",
            width=1920,
            height=1080,
            fps=60,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=5000,
            audio_bitrate=320
        )
        
        # Low quality format
        lq_format = Format(
            format_id="lq",
            format_type=FormatType.VIDEO,
            container=Container.MP4,
            url="test",
            width=640,
            height=360,
            fps=30,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=1000,
            audio_bitrate=128
        )
        
        hq_score = extractor._calculate_quality_score(hq_format)
        lq_score = extractor._calculate_quality_score(lq_format)
        
        assert hq_score > lq_score


class TestExtractorRegistry:
    """Test extractor registry."""
    
    def test_registry_init(self):
        """Test registry initialization."""
        registry = ExtractorRegistry()
        
        # Should have built-in extractors registered
        platforms = registry.list_platforms()
        assert "youtube" in platforms
        assert "vimeo" in platforms
        assert "generic" in platforms
    
    def test_register_extractor(self):
        """Test extractor registration."""
        registry = ExtractorRegistry()
        
        class TestExtractor(BaseExtractor):
            PLATFORM_NAME = "test"
            async def extract_info(self, url): pass
        
        registry.register_extractor(TestExtractor)
        
        assert "test" in registry.list_platforms()
        assert registry.get_extractor_by_platform("test") is not None
    
    def test_get_extractor_for_url(self):
        """Test getting extractor for URL."""
        registry = ExtractorRegistry()
        
        # YouTube URL
        extractor = registry.get_extractor("https://www.youtube.com/watch?v=test")
        assert isinstance(extractor, YouTubeExtractor)
        
        # Vimeo URL
        extractor = registry.get_extractor("https://vimeo.com/123456")
        assert isinstance(extractor, VimeoExtractor)
        
        # Generic URL (fallback)
        extractor = registry.get_extractor("https://unknown.com/video")
        assert isinstance(extractor, GenericExtractor)
    
    def test_unsupported_url(self):
        """Test handling of unsupported URLs."""
        registry = ExtractorRegistry()
        
        # Remove generic extractor to test unsupported URLs
        registry.unregister_extractor("generic")
        
        extractor = registry.get_extractor("https://unsupported.com/video")
        assert extractor is None


class TestYouTubeExtractor:
    """Test YouTube extractor."""
    
    def test_can_handle_urls(self):
        """Test YouTube URL pattern matching."""
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        ]
        
        for url in youtube_urls:
            assert YouTubeExtractor.can_handle(url)
        
        # Non-YouTube URLs
        non_youtube_urls = [
            "https://vimeo.com/123456",
            "https://example.com/video",
        ]
        
        for url in non_youtube_urls:
            assert not YouTubeExtractor.can_handle(url)
    
    def test_extract_video_id(self):
        """Test video ID extraction."""
        extractor = YouTubeExtractor()
        
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            assert extractor._extract_video_id(url) == expected_id
        
        # Invalid URL
        with pytest.raises(ExtractionError):
            extractor._extract_video_id("https://example.com/video")
    
    @pytest.mark.asyncio
    async def test_extract_info(self, sample_youtube_html, mock_aiohttp):
        """Test YouTube video info extraction."""
        extractor = YouTubeExtractor()
        
        # Mock HTTP response
        mock_aiohttp.get(
            "https://www.youtube.com/watch?v=test123",
            payload=sample_youtube_html,
            content_type="text/html"
        )
        
        with patch.object(extractor, '_extract_formats', return_value=[]), \
             patch.object(extractor, '_extract_subtitles', return_value=[]):
            
            video_info = await extractor.extract_info("https://www.youtube.com/watch?v=test123")
            
            assert isinstance(video_info, VideoInfo)
            assert video_info.id == "test123"
            assert video_info.platform == "youtube"
            assert "Test Video" in video_info.title


class TestVimeoExtractor:
    """Test Vimeo extractor."""
    
    def test_can_handle_urls(self):
        """Test Vimeo URL pattern matching."""
        vimeo_urls = [
            "https://vimeo.com/123456789",
            "https://www.vimeo.com/123456789",
            "https://player.vimeo.com/video/123456789",
        ]
        
        for url in vimeo_urls:
            assert VimeoExtractor.can_handle(url)
        
        # Non-Vimeo URLs
        non_vimeo_urls = [
            "https://youtube.com/watch?v=test",
            "https://example.com/video",
        ]
        
        for url in non_vimeo_urls:
            assert not VimeoExtractor.can_handle(url)
    
    def test_extract_video_id(self):
        """Test Vimeo video ID extraction."""
        extractor = VimeoExtractor()
        
        test_cases = [
            ("https://vimeo.com/123456789", "123456789"),
            ("https://www.vimeo.com/123456789", "123456789"),
            ("https://player.vimeo.com/video/123456789", "123456789"),
        ]
        
        for url, expected_id in test_cases:
            assert extractor._extract_video_id(url) == expected_id


class TestGenericExtractor:
    """Test generic extractor."""
    
    def test_can_handle_any_url(self):
        """Test that generic extractor can handle any URL."""
        extractor = GenericExtractor()
        
        urls = [
            "https://example.com/video",
            "http://test.org/media.mp4",
            "https://unknown-site.net/watch?id=123",
        ]
        
        for url in urls:
            assert extractor.can_handle(url)
    
    @pytest.mark.asyncio
    async def test_extract_formats_from_html(self, sample_html_content):
        """Test format extraction from HTML."""
        extractor = GenericExtractor()
        soup = BeautifulSoup(sample_html_content, 'html.parser')
        
        # Mock session for HEAD requests
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1000000'}
        mock_session.head.return_value.__aenter__.return_value = mock_response
        
        formats = await extractor._extract_formats(
            soup, 
            sample_html_content, 
            "https://example.com/",
            mock_session
        )
        
        assert len(formats) >= 2  # Should find MP4 and WebM sources
        assert any(f.container.value == "mp4" for f in formats)
        assert any(f.container.value == "webm" for f in formats)
    
    def test_detect_platform(self):
        """Test platform detection from URL."""
        extractor = GenericExtractor()
        
        test_cases = [
            ("https://example.com/video", "example"),
            ("https://www.test.org/watch", "test"),
            ("http://media.site.net/video.mp4", "site"),
        ]
        
        for url, expected_platform in test_cases:
            assert extractor._detect_platform(url) == expected_platform
    
    def test_generate_video_id(self):
        """Test video ID generation."""
        extractor = GenericExtractor()
        
        video_id = extractor._generate_video_id("https://example.com/watch?v=123")
        assert "example_com" in video_id
        assert "watch" in video_id
