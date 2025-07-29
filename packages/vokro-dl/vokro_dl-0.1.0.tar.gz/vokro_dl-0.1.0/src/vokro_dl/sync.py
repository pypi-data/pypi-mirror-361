"""
Synchronous API wrapper for VokroDL.

This module provides a synchronous interface to VokroDL functionality
for easier integration in non-async codebases.
"""

import asyncio
import threading
from pathlib import Path
from typing import List, Optional, Callable, Any

from .core.downloader import VokroDL
from .core.config import DownloadConfig, GlobalConfig
from .core.models import VideoInfo, DownloadProgress
from .core.exceptions import VokroDLError


class VokroDLSync:
    """
    Synchronous wrapper for VokroDL.
    
    This class provides a synchronous interface to all VokroDL functionality
    by running async operations in a background event loop.
    """
    
    def __init__(
        self,
        config: Optional[DownloadConfig] = None,
        global_config: Optional[GlobalConfig] = None
    ):
        """
        Initialize synchronous VokroDL wrapper.
        
        Args:
            config: Download configuration
            global_config: Global configuration
        """
        self.config = config
        self.global_config = global_config
        self._loop = None
        self._thread = None
        self._downloader = None
    
    def _ensure_loop(self):
        """Ensure event loop is running in background thread."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(
                target=self._run_loop,
                daemon=True
            )
            self._thread.start()
            
            # Wait for loop to be ready
            while not self._loop.is_running():
                threading.Event().wait(0.01)
    
    def _run_loop(self):
        """Run event loop in background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro):
        """Run async coroutine and return result."""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
    
    async def _get_downloader(self) -> VokroDL:
        """Get or create downloader instance."""
        if self._downloader is None:
            self._downloader = VokroDL(self.config, self.global_config)
        return self._downloader
    
    def download(
        self,
        url: str,
        config_override: Optional[DownloadConfig] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> Path:
        """
        Download a video from the given URL.
        
        Args:
            url: Video URL to download
            config_override: Configuration overrides for this download
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the downloaded file
            
        Raises:
            VokroDLError: If download fails
        """
        async def _download():
            downloader = await self._get_downloader()
            return await downloader.download(url, config_override, progress_callback)
        
        return self._run_async(_download())
    
    def download_batch(
        self,
        urls: List[str],
        config_override: Optional[DownloadConfig] = None,
        progress_callback: Optional[Callable[[str, DownloadProgress], None]] = None
    ) -> List[Path]:
        """
        Download multiple videos.
        
        Args:
            urls: List of video URLs to download
            config_override: Configuration overrides
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of paths to downloaded files
        """
        async def _download_batch():
            downloader = await self._get_downloader()
            return await downloader.download_batch(urls, config_override, progress_callback)
        
        return self._run_async(_download_batch())
    
    def extract_info(self, url: str) -> VideoInfo:
        """
        Extract video information without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo object with extracted information
            
        Raises:
            VokroDLError: If extraction fails
        """
        async def _extract_info():
            downloader = await self._get_downloader()
            return await downloader.extract_info(url)
        
        return self._run_async(_extract_info())
    
    def close(self):
        """Clean up resources."""
        if self._downloader:
            self._run_async(self._downloader.close())
        
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def download_video(
    url: str,
    output_dir: Optional[Path] = None,
    quality: str = "best",
    audio_only: bool = False,
    progress_callback: Optional[Callable[[DownloadProgress], None]] = None
) -> Path:
    """
    Simple function to download a single video.
    
    Args:
        url: Video URL
        output_dir: Output directory (default: current directory)
        quality: Video quality (default: "best")
        audio_only: Extract audio only (default: False)
        progress_callback: Optional progress callback
        
    Returns:
        Path to downloaded file
        
    Raises:
        VokroDLError: If download fails
    """
    from .core.models import Quality
    from .core.config import DownloadConfig, OutputConfig, QualityConfig, PostProcessingConfig
    
    # Build configuration
    output_config = OutputConfig(output_dir=output_dir or Path.cwd())
    quality_config = QualityConfig(preferred_quality=Quality(quality))
    post_processing_config = PostProcessingConfig(extract_audio=audio_only)
    
    config = DownloadConfig(
        output=output_config,
        quality=quality_config,
        post_processing=post_processing_config
    )
    
    # Download
    with VokroDLSync(config) as downloader:
        return downloader.download(url, progress_callback=progress_callback)


def extract_video_info(url: str) -> VideoInfo:
    """
    Simple function to extract video information.
    
    Args:
        url: Video URL
        
    Returns:
        VideoInfo object
        
    Raises:
        VokroDLError: If extraction fails
    """
    with VokroDLSync() as downloader:
        return downloader.extract_info(url)


def download_playlist(
    url: str,
    output_dir: Optional[Path] = None,
    quality: str = "best",
    max_downloads: Optional[int] = None,
    progress_callback: Optional[Callable[[str, DownloadProgress], None]] = None
) -> List[Path]:
    """
    Simple function to download a playlist.
    
    Args:
        url: Playlist URL
        output_dir: Output directory (default: current directory)
        quality: Video quality (default: "best")
        max_downloads: Maximum number of videos to download
        progress_callback: Optional progress callback
        
    Returns:
        List of paths to downloaded files
        
    Raises:
        VokroDLError: If download fails
    """
    from .core.models import Quality
    from .core.config import DownloadConfig, OutputConfig, QualityConfig
    
    # Build configuration
    output_config = OutputConfig(output_dir=output_dir or Path.cwd())
    quality_config = QualityConfig(preferred_quality=Quality(quality))
    
    config = DownloadConfig(
        output=output_config,
        quality=quality_config,
        playlist_end=max_downloads
    )
    
    # Extract playlist and download
    with VokroDLSync(config) as downloader:
        # First extract info to get individual video URLs
        video_info = downloader.extract_info(url)
        
        # If it's a playlist, extract individual URLs
        # This is simplified - in real implementation would handle playlist extraction
        urls = [url]  # For now, just download the single URL
        
        return downloader.download_batch(urls, progress_callback=progress_callback)


class SimpleProgressPrinter:
    """Simple progress callback that prints to stdout."""
    
    def __init__(self, show_speed: bool = True, show_eta: bool = True):
        """
        Initialize progress printer.
        
        Args:
            show_speed: Show download speed
            show_eta: Show estimated time remaining
        """
        self.show_speed = show_speed
        self.show_eta = show_eta
        self.last_percent = -1
    
    def __call__(self, progress: DownloadProgress) -> None:
        """Print progress update."""
        # Only print on significant progress changes
        if abs(progress.percent - self.last_percent) < 1.0:
            return
        
        self.last_percent = progress.percent
        
        parts = [f"{progress.percent:.1f}%"]
        
        if progress.total_bytes:
            parts.append(progress.size_human)
        
        if self.show_speed and progress.speed > 0:
            parts.append(f"at {progress.speed_human}")
        
        if self.show_eta and progress.eta:
            eta_str = str(progress.eta).split('.')[0]  # Remove microseconds
            parts.append(f"ETA: {eta_str}")
        
        message = " ".join(parts)
        if progress.filename:
            print(f"{progress.filename}: {message}")
        else:
            print(message)
