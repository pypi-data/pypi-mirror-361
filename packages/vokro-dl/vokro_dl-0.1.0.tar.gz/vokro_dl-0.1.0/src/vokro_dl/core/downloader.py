"""
Main downloader class for VokroDL.

This module contains the core VokroDL class that orchestrates video downloading,
extraction, and post-processing operations.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Union
from urllib.parse import urlparse

import aiohttp
import aiofiles
from rich.console import Console
from rich.progress import Progress, TaskID

from .config import DownloadConfig, GlobalConfig, merge_configs
from .models import VideoInfo, DownloadProgress, Quality, FormatType
from .exceptions import (
    VokroDLError,
    DownloadError,
    ExtractionError,
    NetworkError,
    UnsupportedPlatformError,
)
from ..extractors import ExtractorRegistry
from ..utils.retry import RetryManager
from ..utils.progress import ProgressTracker
from ..utils.networking import NetworkManager
from ..utils.quality_selector import QualitySelector
from ..utils.metadata import MetadataProcessor, ThumbnailProcessor
from ..utils.subtitles import SubtitleProcessor
from ..utils.post_processing import get_global_manager


logger = logging.getLogger(__name__)


class VokroDL:
    """
    Main VokroDL downloader class.
    
    This class provides the primary interface for downloading videos from
    various platforms with advanced features like progress tracking,
    retry mechanisms, and post-processing.
    """
    
    def __init__(
        self,
        config: Optional[DownloadConfig] = None,
        global_config: Optional[GlobalConfig] = None
    ):
        """
        Initialize VokroDL downloader.
        
        Args:
            config: Download configuration. If None, uses default.
            global_config: Global configuration. If None, loads from default location.
        """
        self.global_config = global_config or GlobalConfig.load_default()
        self.config = config or self.global_config.defaults
        
        # Initialize components
        self.extractor_registry = ExtractorRegistry()
        self.retry_manager = RetryManager(self.config.retry)
        self.network_manager = NetworkManager(self.config.network)
        self.progress_tracker = ProgressTracker()
        self.metadata_processor = MetadataProcessor()
        self.thumbnail_processor = ThumbnailProcessor()
        self.subtitle_processor = SubtitleProcessor(self.config.subtitles)
        self.post_processing_manager = get_global_manager()
        
        # Console for rich output
        self.console = Console(quiet=self.config.quiet)
        
        # Active downloads tracking
        self._active_downloads: Dict[str, asyncio.Task] = {}
        self._download_semaphore = asyncio.Semaphore(self.config.parallel_downloads)
    
    async def download(
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
        # Merge configurations
        effective_config = self.config
        if config_override:
            effective_config = merge_configs(self.config, config_override)
        
        try:
            # Extract video information
            video_info = await self.extract_info(url)
            
            # Measure bandwidth for intelligent quality selection
            bandwidth = await self.network_manager.measure_bandwidth()

            # Create quality selector
            quality_selector = QualitySelector(effective_config.quality, bandwidth)

            # Select best format using intelligent selection
            format_type = FormatType.VIDEO if not effective_config.post_processing.extract_audio else FormatType.AUDIO
            selected_format = quality_selector.select_best_format(video_info.formats, format_type)
            
            if not selected_format:
                raise DownloadError(f"No suitable format found for {url}")
            
            # Generate output filename
            output_path = self._generate_output_path(video_info, selected_format, effective_config)
            
            # Check if file already exists
            if output_path.exists() and not effective_config.output.overwrite:
                if effective_config.resume_downloads:
                    logger.info(f"Resuming download: {output_path}")
                else:
                    logger.info(f"File already exists: {output_path}")
                    return output_path
            
            # Perform download with retry logic
            async with self._download_semaphore:
                download_path = await self.retry_manager.execute(
                    self._download_file,
                    selected_format.url,
                    output_path,
                    video_info,
                    effective_config,
                    progress_callback
                )
            
            # Download subtitles if requested
            subtitle_paths = []
            if effective_config.subtitles.download_subtitles:
                subtitle_paths = await self.subtitle_processor.download_subtitles(
                    video_info.subtitles,
                    output_path.parent,
                    output_path.stem,
                    await self.network_manager.get_session()
                )

            # Download and process thumbnail
            thumbnail_path = None
            if effective_config.post_processing.embed_thumbnails and video_info.thumbnails:
                best_thumbnail = self.thumbnail_processor.get_best_thumbnail(video_info.thumbnails)
                if best_thumbnail:
                    thumbnail_path = output_path.parent / f"{output_path.stem}_thumb.jpg"
                    await self.thumbnail_processor.download_thumbnail(
                        best_thumbnail,
                        thumbnail_path,
                        await self.network_manager.get_session()
                    )

            # Create info JSON if requested
            if effective_config.output.create_dirs:  # Using this as a proxy for detailed output
                info_json_path = output_path.parent / f"{output_path.stem}.info.json"
                self.metadata_processor.create_info_json(video_info, info_json_path)

            # Post-processing
            download_path = await self.post_processing_manager.process_file(
                download_path, video_info, effective_config.post_processing
            )

            # Embed subtitles if requested
            if effective_config.subtitles.embed_subtitles and subtitle_paths:
                await self.subtitle_processor.embed_subtitles(download_path, subtitle_paths)
            
            return download_path
            
        except Exception as e:
            if isinstance(e, VokroDLError):
                raise
            else:
                raise DownloadError(f"Download failed: {str(e)}", url=url) from e
    
    async def download_batch(
        self,
        urls: List[str],
        config_override: Optional[DownloadConfig] = None,
        progress_callback: Optional[Callable[[str, DownloadProgress], None]] = None
    ) -> List[Path]:
        """
        Download multiple videos concurrently.
        
        Args:
            urls: List of video URLs to download
            config_override: Configuration overrides
            progress_callback: Optional callback for progress updates (url, progress)
            
        Returns:
            List of paths to downloaded files
        """
        tasks = []
        
        for url in urls:
            # Create individual progress callback
            individual_callback = None
            if progress_callback:
                individual_callback = lambda p, u=url: progress_callback(u, p)
            
            task = asyncio.create_task(
                self.download(url, config_override, individual_callback)
            )
            tasks.append(task)
        
        # Wait for all downloads to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_downloads = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to download {urls[i]}: {result}")
            else:
                successful_downloads.append(result)
        
        return successful_downloads
    
    async def extract_info(self, url: str) -> VideoInfo:
        """
        Extract video information without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo object with extracted information
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            # Find appropriate extractor
            extractor = self.extractor_registry.get_extractor(url)
            if not extractor:
                raise UnsupportedPlatformError(url)
            
            # Extract information with retry logic
            video_info = await self.retry_manager.execute(
                extractor.extract_info, url
            )
            
            return video_info
            
        except Exception as e:
            if isinstance(e, VokroDLError):
                raise
            else:
                raise ExtractionError(f"Failed to extract info: {str(e)}", url=url) from e
    
    async def _download_file(
        self,
        url: str,
        output_path: Path,
        video_info: VideoInfo,
        config: DownloadConfig,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> Path:
        """Download a file from URL to output path."""
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize progress tracking
        progress = DownloadProgress(filename=str(output_path))
        
        # Check for resume
        resume_pos = 0
        if config.resume_downloads and output_path.exists():
            resume_pos = output_path.stat().st_size
            progress.downloaded_bytes = resume_pos
        
        try:
            async with self.network_manager.get_session() as session:
                headers = {}
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Get total size
                    content_length = response.headers.get('content-length')
                    if content_length:
                        total_size = int(content_length)
                        if resume_pos > 0:
                            total_size += resume_pos
                        progress.total_bytes = total_size
                    
                    # Open file for writing
                    mode = 'ab' if resume_pos > 0 else 'wb'
                    async with aiofiles.open(output_path, mode) as f:
                        start_time = time.time()
                        last_update = start_time
                        
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            progress.downloaded_bytes += len(chunk)
                            
                            # Update progress
                            current_time = time.time()
                            if current_time - last_update >= 0.1:  # Update every 100ms
                                progress.elapsed = current_time - start_time
                                if progress.elapsed > 0:
                                    progress.speed = progress.downloaded_bytes / progress.elapsed
                                
                                if progress.total_bytes:
                                    progress.percent = (progress.downloaded_bytes / progress.total_bytes) * 100
                                    if progress.speed > 0:
                                        remaining_bytes = progress.total_bytes - progress.downloaded_bytes
                                        progress.eta = remaining_bytes / progress.speed
                                
                                if progress_callback:
                                    progress_callback(progress)
                                
                                last_update = current_time
            
            # Final progress update
            progress.status = "completed"
            progress.percent = 100.0
            if progress_callback:
                progress_callback(progress)
            
            return output_path
            
        except Exception as e:
            # Clean up partial file on error (unless resuming)
            if not config.resume_downloads and output_path.exists():
                output_path.unlink()
            raise NetworkError(f"Download failed: {str(e)}", url=url) from e
    
    def _generate_output_path(
        self, 
        video_info: VideoInfo, 
        format_info, 
        config: DownloadConfig
    ) -> Path:
        """Generate output file path based on template and video info."""
        # Template variables
        template_vars = {
            'title': self._sanitize_filename(video_info.title),
            'id': video_info.id,
            'ext': format_info.container.value,
            'uploader': self._sanitize_filename(video_info.uploader or 'unknown'),
            'platform': video_info.platform,
            'quality': format_info.quality_label or 'unknown',
        }
        
        # Apply template
        filename = config.output.filename_template % template_vars
        
        return config.output.output_dir / filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()
    
    async def download_playlist(
        self,
        url: str,
        config_override: Optional[DownloadConfig] = None,
        progress_callback: Optional[Callable[[str, DownloadProgress], None]] = None
    ) -> List[Path]:
        """
        Download all videos from a playlist.

        Args:
            url: Playlist URL
            config_override: Configuration overrides
            progress_callback: Optional callback for progress updates

        Returns:
            List of paths to downloaded files
        """
        # Merge configurations
        effective_config = self.config
        if config_override:
            effective_config = merge_configs(self.config, config_override)

        try:
            # Get extractor for playlist
            extractor = self.extractor_registry.get_extractor(url)
            if not extractor:
                raise UnsupportedPlatformError(url)

            # Check if extractor supports playlists
            if not hasattr(extractor, 'SUPPORTS_PLAYLISTS') or not extractor.SUPPORTS_PLAYLISTS:
                # Fallback: treat as single video
                single_result = await self.download(url, config_override,
                                                 lambda p: progress_callback(url, p) if progress_callback else None)
                return [single_result]

            # Extract playlist entries
            playlist_entries = await extractor.extract_playlist_entries(url)

            # Apply playlist filtering
            start_idx = effective_config.playlist_start - 1  # Convert to 0-based
            end_idx = effective_config.playlist_end if effective_config.playlist_end else len(playlist_entries)

            filtered_entries = playlist_entries[start_idx:end_idx]

            if effective_config.playlist_reverse:
                filtered_entries = list(reversed(filtered_entries))

            # Download all entries
            return await self.download_batch(filtered_entries, config_override, progress_callback)

        except Exception as e:
            if isinstance(e, VokroDLError):
                raise
            else:
                raise DownloadError(f"Playlist download failed: {str(e)}", url=url) from e
    
    async def close(self):
        """Clean up resources."""
        await self.network_manager.close()
        
        # Cancel any active downloads
        for task in self._active_downloads.values():
            if not task.done():
                task.cancel()
        
        if self._active_downloads:
            await asyncio.gather(*self._active_downloads.values(), return_exceptions=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
