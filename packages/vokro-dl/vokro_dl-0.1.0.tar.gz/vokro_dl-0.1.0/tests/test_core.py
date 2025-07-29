"""
Tests for core VokroDL functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from vokro_dl.core.downloader import VokroDL
from vokro_dl.core.config import DownloadConfig, OutputConfig
from vokro_dl.core.models import VideoInfo, DownloadProgress, Quality, FormatType
from vokro_dl.core.exceptions import DownloadError, ExtractionError


class TestVokroDL:
    """Test VokroDL main class."""
    
    @pytest.mark.asyncio
    async def test_init(self, download_config, global_config):
        """Test VokroDL initialization."""
        downloader = VokroDL(download_config, global_config)
        
        assert downloader.config == download_config
        assert downloader.global_config == global_config
        assert downloader.extractor_registry is not None
        assert downloader.retry_manager is not None
        assert downloader.network_manager is not None
        
        await downloader.close()
    
    @pytest.mark.asyncio
    async def test_extract_info(self, downloader, sample_video_info):
        """Test video information extraction."""
        # Mock extractor
        mock_extractor = AsyncMock()
        mock_extractor.extract_info.return_value = sample_video_info
        
        with patch.object(downloader.extractor_registry, 'get_extractor', return_value=mock_extractor):
            result = await downloader.extract_info("https://example.com/video")
            
            assert result == sample_video_info
            mock_extractor.extract_info.assert_called_once_with("https://example.com/video")
    
    @pytest.mark.asyncio
    async def test_extract_info_no_extractor(self, downloader):
        """Test extraction with no suitable extractor."""
        with patch.object(downloader.extractor_registry, 'get_extractor', return_value=None):
            with pytest.raises(ExtractionError):
                await downloader.extract_info("https://unsupported.com/video")
    
    @pytest.mark.asyncio
    async def test_download_success(self, downloader, sample_video_info, temp_dir, mock_progress_callback):
        """Test successful video download."""
        # Mock extractor
        mock_extractor = AsyncMock()
        mock_extractor.extract_info.return_value = sample_video_info
        
        # Mock network manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1000'}
        mock_response.content.iter_chunked = AsyncMock(return_value=[b'test' * 250])
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(downloader.extractor_registry, 'get_extractor', return_value=mock_extractor), \
             patch.object(downloader.network_manager, 'get_session', return_value=mock_session), \
             patch('aiofiles.open', create=True) as mock_aiofiles:
            
            # Mock file operations
            mock_file = AsyncMock()
            mock_aiofiles.return_value.__aenter__.return_value = mock_file
            
            result = await downloader.download(
                "https://example.com/video",
                progress_callback=mock_progress_callback
            )
            
            assert isinstance(result, Path)
            assert result.name == "Test Video.mp4"
            mock_progress_callback.assert_called()
    
    @pytest.mark.asyncio
    async def test_download_no_formats(self, downloader, sample_video_info):
        """Test download with no available formats."""
        # Remove formats from video info
        sample_video_info.formats = []
        
        mock_extractor = AsyncMock()
        mock_extractor.extract_info.return_value = sample_video_info
        
        with patch.object(downloader.extractor_registry, 'get_extractor', return_value=mock_extractor):
            with pytest.raises(DownloadError, match="No suitable format found"):
                await downloader.download("https://example.com/video")
    
    @pytest.mark.asyncio
    async def test_download_batch(self, downloader, sample_video_info, mock_progress_callback):
        """Test batch downloading."""
        urls = [
            "https://example.com/video1",
            "https://example.com/video2"
        ]
        
        # Mock successful downloads
        with patch.object(downloader, 'download', return_value=Path("test.mp4")) as mock_download:
            results = await downloader.download_batch(urls, progress_callback=mock_progress_callback)
            
            assert len(results) == 2
            assert all(isinstance(r, Path) for r in results)
            assert mock_download.call_count == 2
    
    def test_generate_output_path(self, downloader, sample_video_info):
        """Test output path generation."""
        format_info = sample_video_info.formats[0]
        
        output_path = downloader._generate_output_path(
            sample_video_info, 
            format_info, 
            downloader.config
        )
        
        assert output_path.name == "Test Video.mp4"
        assert output_path.parent == downloader.config.output.output_dir
    
    def test_sanitize_filename(self, downloader):
        """Test filename sanitization."""
        # Test invalid characters
        result = downloader._sanitize_filename("Test<>:\"/\\|?*Video")
        assert result == "Test_________Video"
        
        # Test long filename
        long_name = "a" * 250
        result = downloader._sanitize_filename(long_name)
        assert len(result) <= 200
        
        # Test whitespace
        result = downloader._sanitize_filename("  Test Video  ")
        assert result == "Test Video"


class TestDownloadConfig:
    """Test download configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DownloadConfig()
        
        assert config.parallel_downloads == 1
        assert config.resume_downloads is True
        assert config.playlist_start == 1
        assert config.verbose is False
        assert config.quiet is False
    
    def test_output_config(self, temp_dir):
        """Test output configuration."""
        output_config = OutputConfig(
            output_dir=temp_dir,
            filename_template="%(title)s_%(id)s.%(ext)s",
            overwrite=True
        )
        
        config = DownloadConfig(output=output_config)
        
        assert config.output.output_dir == temp_dir
        assert config.output.filename_template == "%(title)s_%(id)s.%(ext)s"
        assert config.output.overwrite is True
    
    def test_playlist_validation(self):
        """Test playlist configuration validation."""
        # Valid configuration
        config = DownloadConfig(playlist_start=1, playlist_end=10)
        assert config.playlist_start == 1
        assert config.playlist_end == 10
        
        # Invalid configuration should raise validation error
        with pytest.raises(ValueError):
            DownloadConfig(playlist_start=10, playlist_end=5)


class TestVideoInfo:
    """Test VideoInfo model."""
    
    def test_get_best_format(self, sample_video_info):
        """Test best format selection."""
        # Test best quality
        best_format = sample_video_info.get_best_format(Quality.BEST, FormatType.VIDEO)
        assert best_format is not None
        assert best_format.height == 720  # Higher quality format
        
        # Test worst quality
        worst_format = sample_video_info.get_best_format(Quality.WORST, FormatType.VIDEO)
        assert worst_format is not None
        assert worst_format.height == 360  # Lower quality format
        
        # Test specific quality
        hd_format = sample_video_info.get_best_format(Quality.RESOLUTION_720P, FormatType.VIDEO)
        assert hd_format is not None
        assert hd_format.height == 720
    
    def test_url_validation(self):
        """Test URL validation in VideoInfo."""
        from vokro_dl.core.models import VideoInfo
        
        # Valid URLs should work
        valid_info = VideoInfo(
            id="test",
            title="Test",
            url="https://example.com/video",
            platform="test",
            webpage_url="https://example.com/watch",
            original_url="https://example.com/original"
        )
        assert valid_info.url == "https://example.com/video"
        
        # Invalid URLs should raise validation error
        with pytest.raises(ValueError):
            VideoInfo(
                id="test",
                title="Test", 
                url="not-a-url",
                platform="test",
                webpage_url="https://example.com/watch",
                original_url="https://example.com/original"
            )


class TestDownloadProgress:
    """Test DownloadProgress model."""
    
    def test_progress_properties(self):
        """Test progress calculation properties."""
        progress = DownloadProgress(
            downloaded_bytes=500,
            total_bytes=1000,
            speed=1024  # 1 KB/s
        )
        
        assert progress.percent == 50.0
        assert progress.speed_human == "1.0 KB/s"
        assert "500" in progress.size_human
        assert "1.0 KB" in progress.size_human
    
    def test_speed_formatting(self):
        """Test speed formatting."""
        # Test bytes per second
        progress = DownloadProgress(speed=500)
        assert progress.speed_human == "500.0 B/s"
        
        # Test KB/s
        progress = DownloadProgress(speed=1536)  # 1.5 KB/s
        assert progress.speed_human == "1.5 KB/s"
        
        # Test MB/s
        progress = DownloadProgress(speed=2 * 1024 * 1024)  # 2 MB/s
        assert progress.speed_human == "2.0 MB/s"
        
        # Test GB/s
        progress = DownloadProgress(speed=3 * 1024 * 1024 * 1024)  # 3 GB/s
        assert progress.speed_human == "3.0 GB/s"
