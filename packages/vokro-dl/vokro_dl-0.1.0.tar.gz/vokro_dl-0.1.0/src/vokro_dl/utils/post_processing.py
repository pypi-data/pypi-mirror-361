"""
Post-processing utilities for VokroDL.

This module provides post-processing functionality including format conversion,
audio extraction, and custom processing hooks.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Union
from abc import ABC, abstractmethod

from ..core.models import VideoInfo, Container
from ..core.config import PostProcessingConfig
from ..core.exceptions import PostProcessingError


logger = logging.getLogger(__name__)


class PostProcessor(ABC):
    """Abstract base class for post-processors."""
    
    @abstractmethod
    async def process(
        self, 
        file_path: Path, 
        video_info: VideoInfo, 
        config: PostProcessingConfig
    ) -> Path:
        """
        Process the downloaded file.
        
        Args:
            file_path: Path to the downloaded file
            video_info: Video information
            config: Post-processing configuration
            
        Returns:
            Path to the processed file
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get processor name."""
        pass


class FFmpegProcessor(PostProcessor):
    """Post-processor using FFmpeg for format conversion and audio extraction."""
    
    def __init__(self):
        """Initialize FFmpeg processor."""
        self.logger = logging.getLogger(__name__)
    
    @property
    def name(self) -> str:
        return "ffmpeg"
    
    async def process(
        self, 
        file_path: Path, 
        video_info: VideoInfo, 
        config: PostProcessingConfig
    ) -> Path:
        """Process file using FFmpeg."""
        try:
            # Check if FFmpeg is available
            if not await self._check_ffmpeg():
                raise PostProcessingError("FFmpeg not found in PATH")
            
            processed_path = file_path
            
            # Extract audio if requested
            if config.extract_audio:
                processed_path = await self._extract_audio(
                    processed_path, config.audio_format
                )
            
            # Convert format if requested
            if config.convert_format and config.convert_format != Container(file_path.suffix[1:]):
                processed_path = await self._convert_format(
                    processed_path, config.convert_format
                )
            
            return processed_path
            
        except Exception as e:
            raise PostProcessingError(f"FFmpeg processing failed: {str(e)}") from e
    
    async def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            result = await asyncio.create_subprocess_exec(
                'ffmpeg', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    async def _extract_audio(self, input_path: Path, audio_format: Container) -> Path:
        """Extract audio from video file."""
        output_path = input_path.with_suffix(f'.{audio_format.value}')
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vn',  # No video
            '-acodec', self._get_audio_codec(audio_format),
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        # Add format-specific options
        if audio_format == Container.MP3:
            cmd.extend(['-ab', '192k'])  # 192 kbps bitrate
        elif audio_format == Container.AAC:
            cmd.extend(['-ab', '128k'])
        elif audio_format == Container.FLAC:
            cmd.extend(['-compression_level', '5'])
        
        self.logger.info(f"Extracting audio: {input_path} -> {output_path}")
        
        # Run FFmpeg
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
            raise PostProcessingError(f"Audio extraction failed: {error_msg}")
        
        # Remove original file
        input_path.unlink()
        
        self.logger.info(f"Audio extracted successfully: {output_path}")
        return output_path
    
    async def _convert_format(self, input_path: Path, target_format: Container) -> Path:
        """Convert file to different format."""
        output_path = input_path.with_suffix(f'.{target_format.value}')
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c', 'copy',  # Copy streams without re-encoding when possible
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        # Add format-specific options
        if target_format == Container.MP4:
            cmd.extend(['-movflags', '+faststart'])  # Optimize for streaming
        elif target_format == Container.WEBM:
            # For WebM, we might need to re-encode
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-c:v', 'libvpx-vp9',
                '-c:a', 'libopus',
                '-y',
                str(output_path)
            ]
        
        self.logger.info(f"Converting format: {input_path} -> {output_path}")
        
        # Run FFmpeg
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
            raise PostProcessingError(f"Format conversion failed: {error_msg}")
        
        # Remove original file
        input_path.unlink()
        
        self.logger.info(f"Format converted successfully: {output_path}")
        return output_path
    
    def _get_audio_codec(self, format_type: Container) -> str:
        """Get appropriate audio codec for format."""
        codec_map = {
            Container.MP3: 'libmp3lame',
            Container.AAC: 'aac',
            Container.OGG: 'libvorbis',
            Container.FLAC: 'flac',
            Container.WAV: 'pcm_s16le',
            Container.M4A: 'aac',
        }
        return codec_map.get(format_type, 'copy')


class MetadataProcessor(PostProcessor):
    """Post-processor for embedding metadata and thumbnails."""
    
    def __init__(self):
        """Initialize metadata processor."""
        self.logger = logging.getLogger(__name__)
    
    @property
    def name(self) -> str:
        return "metadata"
    
    async def process(
        self, 
        file_path: Path, 
        video_info: VideoInfo, 
        config: PostProcessingConfig
    ) -> Path:
        """Process file to embed metadata."""
        try:
            from .metadata import MetadataProcessor, ThumbnailProcessor
            
            metadata_proc = MetadataProcessor()
            thumbnail_proc = ThumbnailProcessor()
            
            # Download thumbnail if requested
            thumbnail_path = None
            if config.embed_thumbnails and video_info.thumbnails:
                best_thumbnail = thumbnail_proc.get_best_thumbnail(video_info.thumbnails)
                if best_thumbnail:
                    thumbnail_path = file_path.parent / f"{file_path.stem}_thumb.jpg"
                    await thumbnail_proc.download_thumbnail(best_thumbnail, thumbnail_path)
            
            # Embed metadata
            if config.embed_metadata:
                success = await metadata_proc.embed_metadata(
                    file_path, video_info, thumbnail_path
                )
                if not success:
                    self.logger.warning("Failed to embed metadata")
            
            # Clean up thumbnail file if it was temporary
            if thumbnail_path and thumbnail_path.exists() and not config.embed_thumbnails:
                thumbnail_path.unlink()
            
            return file_path
            
        except Exception as e:
            raise PostProcessingError(f"Metadata processing failed: {str(e)}") from e


class CustomProcessor(PostProcessor):
    """Post-processor for custom user-defined processing."""
    
    def __init__(self, name: str, processor_func: Callable):
        """
        Initialize custom processor.
        
        Args:
            name: Processor name
            processor_func: Processing function
        """
        self._name = name
        self.processor_func = processor_func
        self.logger = logging.getLogger(__name__)
    
    @property
    def name(self) -> str:
        return self._name
    
    async def process(
        self, 
        file_path: Path, 
        video_info: VideoInfo, 
        config: PostProcessingConfig
    ) -> Path:
        """Process file using custom function."""
        try:
            if asyncio.iscoroutinefunction(self.processor_func):
                return await self.processor_func(file_path, video_info, config)
            else:
                return self.processor_func(file_path, video_info, config)
        except Exception as e:
            raise PostProcessingError(f"Custom processing failed: {str(e)}") from e


class PostProcessingManager:
    """Manages post-processing pipeline."""
    
    def __init__(self):
        """Initialize post-processing manager."""
        self.processors: Dict[str, PostProcessor] = {}
        self.logger = logging.getLogger(__name__)
        
        # Register built-in processors
        self.register_processor(FFmpegProcessor())
        self.register_processor(MetadataProcessor())
    
    def register_processor(self, processor: PostProcessor):
        """Register a post-processor."""
        self.processors[processor.name] = processor
        self.logger.debug(f"Registered post-processor: {processor.name}")
    
    def register_custom_processor(
        self, 
        name: str, 
        processor_func: Callable
    ):
        """Register a custom post-processor function."""
        processor = CustomProcessor(name, processor_func)
        self.register_processor(processor)
    
    async def process_file(
        self, 
        file_path: Path, 
        video_info: VideoInfo, 
        config: PostProcessingConfig
    ) -> Path:
        """
        Process file through the post-processing pipeline.
        
        Args:
            file_path: Path to the downloaded file
            video_info: Video information
            config: Post-processing configuration
            
        Returns:
            Path to the final processed file
        """
        current_path = file_path
        
        # Always run metadata processor if metadata embedding is enabled
        if config.embed_metadata or config.embed_thumbnails:
            if 'metadata' in self.processors:
                current_path = await self.processors['metadata'].process(
                    current_path, video_info, config
                )
        
        # Run FFmpeg processor for format conversion/audio extraction
        if config.extract_audio or config.convert_format:
            if 'ffmpeg' in self.processors:
                current_path = await self.processors['ffmpeg'].process(
                    current_path, video_info, config
                )
        
        # Run custom processors
        for processor_name in config.post_processors:
            if processor_name in self.processors:
                self.logger.info(f"Running post-processor: {processor_name}")
                current_path = await self.processors[processor_name].process(
                    current_path, video_info, config
                )
            else:
                self.logger.warning(f"Post-processor not found: {processor_name}")
        
        return current_path
    
    def list_processors(self) -> List[str]:
        """Get list of available processors."""
        return list(self.processors.keys())


# Global post-processing manager instance
_global_manager: Optional[PostProcessingManager] = None


def get_global_manager() -> PostProcessingManager:
    """Get the global post-processing manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = PostProcessingManager()
    return _global_manager


def register_processor(processor: PostProcessor):
    """Register a processor in the global manager."""
    manager = get_global_manager()
    manager.register_processor(processor)


def register_custom_processor(name: str, processor_func: Callable):
    """Register a custom processor function in the global manager."""
    manager = get_global_manager()
    manager.register_custom_processor(name, processor_func)


# Example custom processors
async def example_file_organizer(
    file_path: Path, 
    video_info: VideoInfo, 
    config: PostProcessingConfig
) -> Path:
    """Example post-processor that organizes files by platform."""
    # Create platform directory
    platform_dir = file_path.parent / video_info.platform
    platform_dir.mkdir(exist_ok=True)
    
    # Move file to platform directory
    new_path = platform_dir / file_path.name
    file_path.rename(new_path)
    
    return new_path


def example_file_renamer(
    file_path: Path, 
    video_info: VideoInfo, 
    config: PostProcessingConfig
) -> Path:
    """Example post-processor that renames files with upload date."""
    if video_info.upload_date:
        date_str = video_info.upload_date.strftime("%Y-%m-%d")
        new_name = f"{date_str}_{file_path.name}"
        new_path = file_path.parent / new_name
        file_path.rename(new_path)
        return new_path
    
    return file_path
