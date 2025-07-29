"""
Pytest configuration and fixtures for VokroDL tests.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import Mock

import pytest
import aiohttp
from aioresponses import aioresponses

from vokro_dl.core.config import DownloadConfig, GlobalConfig, OutputConfig
from vokro_dl.core.downloader import VokroDL


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def download_config(temp_dir: Path) -> DownloadConfig:
    """Create a test download configuration."""
    output_config = OutputConfig(
        output_dir=temp_dir,
        filename_template="%(title)s.%(ext)s",
        overwrite=True
    )
    
    return DownloadConfig(
        output=output_config,
        verbose=True
    )


@pytest.fixture
def global_config() -> GlobalConfig:
    """Create a test global configuration."""
    return GlobalConfig()


@pytest.fixture
async def downloader(download_config: DownloadConfig, global_config: GlobalConfig) -> AsyncGenerator[VokroDL, None]:
    """Create a VokroDL instance for testing."""
    downloader = VokroDL(download_config, global_config)
    yield downloader
    await downloader.close()


@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp responses."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def sample_video_info():
    """Sample video information for testing."""
    from vokro_dl.core.models import VideoInfo, Format, Container, Codec, FormatType
    
    formats = [
        Format(
            format_id="22",
            format_type=FormatType.VIDEO,
            container=Container.MP4,
            url="https://example.com/video.mp4",
            width=1280,
            height=720,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=1000,
            quality_score=720.0
        ),
        Format(
            format_id="18",
            format_type=FormatType.VIDEO,
            container=Container.MP4,
            url="https://example.com/video_low.mp4",
            width=640,
            height=360,
            video_codec=Codec.H264,
            audio_codec=Codec.AAC_CODEC,
            bitrate=500,
            quality_score=360.0
        )
    ]
    
    return VideoInfo(
        id="test_video_123",
        title="Test Video",
        description="A test video for unit tests",
        url="https://example.com/watch?v=test_video_123",
        platform="test",
        uploader="Test Channel",
        duration=120.0,
        formats=formats,
        subtitles=[],
        thumbnails=[],
        webpage_url="https://example.com/watch?v=test_video_123",
        original_url="https://example.com/watch?v=test_video_123"
    )


@pytest.fixture
def mock_progress_callback():
    """Mock progress callback for testing."""
    return Mock()


@pytest.fixture
def sample_html_content():
    """Sample HTML content for extractor testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Video - Example Site</title>
        <meta property="og:title" content="Test Video">
        <meta property="og:description" content="A test video">
        <meta property="og:image" content="https://example.com/thumb.jpg">
        <meta property="video:duration" content="120">
    </head>
    <body>
        <video controls>
            <source src="https://example.com/video.mp4" type="video/mp4">
            <source src="https://example.com/video.webm" type="video/webm">
        </video>
    </body>
    </html>
    """


@pytest.fixture
def sample_youtube_html():
    """Sample YouTube HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Video - YouTube</title>
        <meta property="og:title" content="Test Video">
        <meta property="og:description" content="A test YouTube video">
        <meta itemprop="duration" content="PT2M">
        <meta itemprop="uploadDate" content="2023-01-01T00:00:00Z">
    </head>
    <body>
        <script>
            var ytInitialData = {
                "contents": {
                    "videoDetails": {
                        "videoId": "test123",
                        "title": "Test Video",
                        "lengthSeconds": "120",
                        "viewCount": "1000"
                    }
                }
            };
        </script>
    </body>
    </html>
    """


# Pytest markers
pytest_plugins = []

# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


# Skip network tests by default
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--run-network"):
        # Don't skip network tests if explicitly requested
        return
    
    skip_network = pytest.mark.skip(reason="need --run-network option to run")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_network)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="run network tests"
    )
    parser.addoption(
        "--run-slow",
        action="store_true", 
        default=False,
        help="run slow tests"
    )
