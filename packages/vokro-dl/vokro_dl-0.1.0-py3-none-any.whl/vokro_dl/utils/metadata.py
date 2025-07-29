"""
Metadata handling utilities for VokroDL.

This module provides functionality for extracting, processing, and embedding
metadata in downloaded video files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

try:
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
    from mutagen.oggvorbis import OggVorbis
    from mutagen.flac import FLAC
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Mutagen not available - metadata embedding will be limited")

from ..core.models import VideoInfo, Thumbnail
from ..core.exceptions import PostProcessingError


class MetadataProcessor:
    """
    Processes and embeds metadata in media files.
    
    Supports various formats including MP4, MP3, FLAC, and OGG.
    """
    
    def __init__(self):
        """Initialize metadata processor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, video_info: VideoInfo) -> Dict[str, Any]:
        """
        Extract metadata from VideoInfo object.
        
        Args:
            video_info: Video information object
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {
            'title': video_info.title,
            'artist': video_info.uploader,
            'album': f"{video_info.platform.title()} Videos",
            'date': video_info.upload_date.isoformat() if video_info.upload_date else None,
            'genre': 'Video',
            'comment': video_info.description,
            'url': video_info.webpage_url,
            'duration': video_info.duration,
            'view_count': video_info.view_count,
            'like_count': video_info.like_count,
            'platform': video_info.platform,
            'video_id': video_info.id,
            'tags': video_info.tags,
            'categories': video_info.categories,
        }
        
        # Remove None values
        return {k: v for k, v in metadata.items() if v is not None}
    
    async def embed_metadata(
        self, 
        file_path: Path, 
        video_info: VideoInfo,
        thumbnail_path: Optional[Path] = None
    ) -> bool:
        """
        Embed metadata into media file.
        
        Args:
            file_path: Path to media file
            video_info: Video information
            thumbnail_path: Optional path to thumbnail image
            
        Returns:
            True if successful, False otherwise
        """
        if not MUTAGEN_AVAILABLE:
            self.logger.warning("Cannot embed metadata - mutagen not available")
            return False
        
        try:
            metadata = self.extract_metadata(video_info)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.mp4':
                return await self._embed_mp4_metadata(file_path, metadata, thumbnail_path)
            elif file_extension == '.mp3':
                return await self._embed_mp3_metadata(file_path, metadata, thumbnail_path)
            elif file_extension == '.flac':
                return await self._embed_flac_metadata(file_path, metadata, thumbnail_path)
            elif file_extension in ['.ogg', '.oga']:
                return await self._embed_ogg_metadata(file_path, metadata, thumbnail_path)
            else:
                self.logger.warning(f"Metadata embedding not supported for {file_extension}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to embed metadata: {e}")
            return False
    
    async def _embed_mp4_metadata(
        self, 
        file_path: Path, 
        metadata: Dict[str, Any],
        thumbnail_path: Optional[Path] = None
    ) -> bool:
        """Embed metadata in MP4 file."""
        try:
            mp4_file = MP4(str(file_path))
            
            # Basic metadata
            if metadata.get('title'):
                mp4_file['\xa9nam'] = [metadata['title']]
            if metadata.get('artist'):
                mp4_file['\xa9ART'] = [metadata['artist']]
            if metadata.get('album'):
                mp4_file['\xa9alb'] = [metadata['album']]
            if metadata.get('date'):
                mp4_file['\xa9day'] = [metadata['date'][:4]]  # Year only
            if metadata.get('genre'):
                mp4_file['\xa9gen'] = [metadata['genre']]
            if metadata.get('comment'):
                mp4_file['\xa9cmt'] = [metadata['comment'][:255]]  # Limit length
            
            # Custom metadata
            if metadata.get('url'):
                mp4_file['----:com.apple.iTunes:URL'] = [metadata['url'].encode('utf-8')]
            if metadata.get('platform'):
                mp4_file['----:com.apple.iTunes:PLATFORM'] = [metadata['platform'].encode('utf-8')]
            if metadata.get('video_id'):
                mp4_file['----:com.apple.iTunes:VIDEO_ID'] = [metadata['video_id'].encode('utf-8')]
            
            # Thumbnail
            if thumbnail_path and thumbnail_path.exists():
                with open(thumbnail_path, 'rb') as f:
                    thumbnail_data = f.read()
                
                # Determine format
                if thumbnail_path.suffix.lower() in ['.jpg', '.jpeg']:
                    format_type = MP4Cover.FORMAT_JPEG
                elif thumbnail_path.suffix.lower() == '.png':
                    format_type = MP4Cover.FORMAT_PNG
                else:
                    format_type = MP4Cover.FORMAT_JPEG
                
                mp4_file['covr'] = [MP4Cover(thumbnail_data, format_type)]
            
            mp4_file.save()
            self.logger.info(f"Embedded metadata in MP4 file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to embed MP4 metadata: {e}")
            return False
    
    async def _embed_mp3_metadata(
        self, 
        file_path: Path, 
        metadata: Dict[str, Any],
        thumbnail_path: Optional[Path] = None
    ) -> bool:
        """Embed metadata in MP3 file."""
        try:
            mp3_file = ID3(str(file_path))
            
            # Basic metadata
            if metadata.get('title'):
                mp3_file['TIT2'] = TIT2(encoding=3, text=metadata['title'])
            if metadata.get('artist'):
                mp3_file['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
            if metadata.get('album'):
                mp3_file['TALB'] = TALB(encoding=3, text=metadata['album'])
            if metadata.get('date'):
                mp3_file['TDRC'] = TDRC(encoding=3, text=metadata['date'][:4])
            if metadata.get('genre'):
                mp3_file['TCON'] = TCON(encoding=3, text=metadata['genre'])
            
            # Thumbnail
            if thumbnail_path and thumbnail_path.exists():
                with open(thumbnail_path, 'rb') as f:
                    thumbnail_data = f.read()
                
                # Determine MIME type
                if thumbnail_path.suffix.lower() in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif thumbnail_path.suffix.lower() == '.png':
                    mime_type = 'image/png'
                else:
                    mime_type = 'image/jpeg'
                
                mp3_file['APIC'] = APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=thumbnail_data
                )
            
            mp3_file.save()
            self.logger.info(f"Embedded metadata in MP3 file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to embed MP3 metadata: {e}")
            return False
    
    async def _embed_flac_metadata(
        self, 
        file_path: Path, 
        metadata: Dict[str, Any],
        thumbnail_path: Optional[Path] = None
    ) -> bool:
        """Embed metadata in FLAC file."""
        try:
            flac_file = FLAC(str(file_path))
            
            # Basic metadata
            if metadata.get('title'):
                flac_file['TITLE'] = metadata['title']
            if metadata.get('artist'):
                flac_file['ARTIST'] = metadata['artist']
            if metadata.get('album'):
                flac_file['ALBUM'] = metadata['album']
            if metadata.get('date'):
                flac_file['DATE'] = metadata['date'][:4]
            if metadata.get('genre'):
                flac_file['GENRE'] = metadata['genre']
            if metadata.get('comment'):
                flac_file['COMMENT'] = metadata['comment']
            
            # Custom metadata
            if metadata.get('url'):
                flac_file['URL'] = metadata['url']
            if metadata.get('platform'):
                flac_file['PLATFORM'] = metadata['platform']
            
            # Thumbnail (FLAC supports embedded images)
            if thumbnail_path and thumbnail_path.exists():
                from mutagen.flac import Picture
                
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.desc = 'Cover'
                
                with open(thumbnail_path, 'rb') as f:
                    picture.data = f.read()
                
                if thumbnail_path.suffix.lower() in ['.jpg', '.jpeg']:
                    picture.mime = 'image/jpeg'
                elif thumbnail_path.suffix.lower() == '.png':
                    picture.mime = 'image/png'
                
                flac_file.add_picture(picture)
            
            flac_file.save()
            self.logger.info(f"Embedded metadata in FLAC file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to embed FLAC metadata: {e}")
            return False
    
    async def _embed_ogg_metadata(
        self, 
        file_path: Path, 
        metadata: Dict[str, Any],
        thumbnail_path: Optional[Path] = None
    ) -> bool:
        """Embed metadata in OGG file."""
        try:
            ogg_file = OggVorbis(str(file_path))
            
            # Basic metadata
            if metadata.get('title'):
                ogg_file['TITLE'] = metadata['title']
            if metadata.get('artist'):
                ogg_file['ARTIST'] = metadata['artist']
            if metadata.get('album'):
                ogg_file['ALBUM'] = metadata['album']
            if metadata.get('date'):
                ogg_file['DATE'] = metadata['date'][:4]
            if metadata.get('genre'):
                ogg_file['GENRE'] = metadata['genre']
            if metadata.get('comment'):
                ogg_file['COMMENT'] = metadata['comment']
            
            # Custom metadata
            if metadata.get('url'):
                ogg_file['URL'] = metadata['url']
            if metadata.get('platform'):
                ogg_file['PLATFORM'] = metadata['platform']
            
            ogg_file.save()
            self.logger.info(f"Embedded metadata in OGG file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to embed OGG metadata: {e}")
            return False
    
    def create_info_json(self, video_info: VideoInfo, output_path: Path) -> bool:
        """
        Create JSON file with complete video information.
        
        Args:
            video_info: Video information
            output_path: Path for JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert VideoInfo to dictionary
            info_dict = video_info.dict()
            
            # Convert datetime objects to ISO format
            if info_dict.get('upload_date'):
                info_dict['upload_date'] = info_dict['upload_date'].isoformat()
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(info_dict, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Created info JSON: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create info JSON: {e}")
            return False


class ThumbnailProcessor:
    """Processes and downloads thumbnails."""
    
    def __init__(self):
        """Initialize thumbnail processor."""
        self.logger = logging.getLogger(__name__)
    
    async def download_thumbnail(
        self, 
        thumbnail: Thumbnail, 
        output_path: Path,
        session = None
    ) -> bool:
        """
        Download thumbnail image.
        
        Args:
            thumbnail: Thumbnail information
            output_path: Output file path
            session: Optional aiohttp session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import aiohttp
            import aiofiles
            
            # Create session if not provided
            if session is None:
                async with aiohttp.ClientSession() as session:
                    return await self._download_thumbnail_with_session(
                        thumbnail, output_path, session
                    )
            else:
                return await self._download_thumbnail_with_session(
                    thumbnail, output_path, session
                )
                
        except Exception as e:
            self.logger.error(f"Failed to download thumbnail: {e}")
            return False
    
    async def _download_thumbnail_with_session(
        self, 
        thumbnail: Thumbnail, 
        output_path: Path,
        session
    ) -> bool:
        """Download thumbnail with provided session."""
        try:
            import aiofiles
            
            async with session.get(thumbnail.url) as response:
                response.raise_for_status()
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save
                async with aiofiles.open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                self.logger.info(f"Downloaded thumbnail: {output_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to download thumbnail: {e}")
            return False
    
    def get_best_thumbnail(self, thumbnails: List[Thumbnail]) -> Optional[Thumbnail]:
        """
        Select the best thumbnail from available options.
        
        Args:
            thumbnails: List of available thumbnails
            
        Returns:
            Best thumbnail or None if no thumbnails available
        """
        if not thumbnails:
            return None
        
        # Prefer thumbnails with known dimensions
        thumbnails_with_size = [t for t in thumbnails if t.width and t.height]
        
        if thumbnails_with_size:
            # Select highest resolution thumbnail
            return max(thumbnails_with_size, key=lambda t: t.width * t.height)
        else:
            # Fallback to first thumbnail
            return thumbnails[0]
