"""
Subtitle handling utilities for VokroDL.

This module provides functionality for downloading, converting, and embedding
subtitles in various formats.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import timedelta

import aiohttp
import aiofiles

from ..core.models import Subtitle
from ..core.config import SubtitleConfig
from ..core.exceptions import SubtitleError


logger = logging.getLogger(__name__)


class SubtitleProcessor:
    """
    Processes subtitles including downloading, format conversion, and embedding.
    """
    
    def __init__(self, config: SubtitleConfig):
        """
        Initialize subtitle processor.
        
        Args:
            config: Subtitle configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def download_subtitles(
        self, 
        subtitles: List[Subtitle], 
        output_dir: Path,
        base_filename: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> List[Path]:
        """
        Download subtitles in preferred languages.
        
        Args:
            subtitles: Available subtitles
            output_dir: Output directory
            base_filename: Base filename (without extension)
            session: Optional aiohttp session
            
        Returns:
            List of downloaded subtitle file paths
        """
        if not self.config.download_subtitles:
            return []
        
        # Filter subtitles by language preference
        preferred_subtitles = self._filter_preferred_subtitles(subtitles)
        
        if not preferred_subtitles:
            self.logger.info("No subtitles found in preferred languages")
            return []
        
        downloaded_files = []
        
        # Create session if not provided
        if session is None:
            async with aiohttp.ClientSession() as session:
                for subtitle in preferred_subtitles:
                    file_path = await self._download_single_subtitle(
                        subtitle, output_dir, base_filename, session
                    )
                    if file_path:
                        downloaded_files.append(file_path)
        else:
            for subtitle in preferred_subtitles:
                file_path = await self._download_single_subtitle(
                    subtitle, output_dir, base_filename, session
                )
                if file_path:
                    downloaded_files.append(file_path)
        
        return downloaded_files
    
    def _filter_preferred_subtitles(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        """Filter subtitles by language preferences."""
        if not self.config.subtitle_languages:
            return subtitles
        
        preferred = []
        
        # First pass: exact language matches
        for lang in self.config.subtitle_languages:
            for subtitle in subtitles:
                if subtitle.language == lang:
                    # Skip auto-generated if not wanted
                    if subtitle.auto_generated and not self.config.auto_generated_subtitles:
                        continue
                    preferred.append(subtitle)
        
        # Second pass: language prefix matches (e.g., 'en' matches 'en-US')
        if not preferred:
            for lang in self.config.subtitle_languages:
                for subtitle in subtitles:
                    if subtitle.language.startswith(lang + '-'):
                        if subtitle.auto_generated and not self.config.auto_generated_subtitles:
                            continue
                        preferred.append(subtitle)
        
        return preferred
    
    async def _download_single_subtitle(
        self, 
        subtitle: Subtitle, 
        output_dir: Path, 
        base_filename: str,
        session: aiohttp.ClientSession
    ) -> Optional[Path]:
        """Download a single subtitle file."""
        try:
            # Generate filename
            lang_suffix = f".{subtitle.language}"
            if subtitle.auto_generated:
                lang_suffix += ".auto"
            
            filename = f"{base_filename}{lang_suffix}.{subtitle.format_type}"
            output_path = output_dir / filename
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download subtitle
            async with session.get(subtitle.url) as response:
                response.raise_for_status()
                content = await response.text()
            
            # Convert format if needed
            if subtitle.format_type.lower() != 'srt':
                content = await self._convert_subtitle_format(
                    content, subtitle.format_type, 'srt'
                )
                # Update filename extension
                output_path = output_path.with_suffix('.srt')
            
            # Save subtitle file
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self.logger.info(f"Downloaded subtitle: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to download subtitle {subtitle.language}: {e}")
            return None
    
    async def _convert_subtitle_format(
        self, 
        content: str, 
        from_format: str, 
        to_format: str
    ) -> str:
        """
        Convert subtitle between formats.
        
        Args:
            content: Subtitle content
            from_format: Source format (vtt, ass, etc.)
            to_format: Target format (srt, vtt, etc.)
            
        Returns:
            Converted subtitle content
        """
        from_format = from_format.lower()
        to_format = to_format.lower()
        
        if from_format == to_format:
            return content
        
        # Parse source format
        if from_format == 'vtt':
            entries = self._parse_vtt(content)
        elif from_format == 'ass' or from_format == 'ssa':
            entries = self._parse_ass(content)
        else:
            # Fallback: assume SRT-like format
            entries = self._parse_srt(content)
        
        # Convert to target format
        if to_format == 'srt':
            return self._generate_srt(entries)
        elif to_format == 'vtt':
            return self._generate_vtt(entries)
        else:
            raise SubtitleError(f"Conversion to {to_format} not supported")
    
    def _parse_vtt(self, content: str) -> List[Dict[str, Any]]:
        """Parse WebVTT subtitle format."""
        entries = []
        lines = content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip header and empty lines
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                i += 1
                continue
            
            # Check if this is a timestamp line
            if '-->' in line:
                # Parse timestamp
                start_time, end_time = self._parse_vtt_timestamp(line)
                
                # Collect subtitle text
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                
                if text_lines:
                    entries.append({
                        'start': start_time,
                        'end': end_time,
                        'text': '\n'.join(text_lines)
                    })
            else:
                i += 1
        
        return entries
    
    def _parse_srt(self, content: str) -> List[Dict[str, Any]]:
        """Parse SRT subtitle format."""
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Skip sequence number
            timestamp_line = lines[1]
            text_lines = lines[2:]
            
            if '-->' in timestamp_line:
                start_time, end_time = self._parse_srt_timestamp(timestamp_line)
                entries.append({
                    'start': start_time,
                    'end': end_time,
                    'text': '\n'.join(text_lines)
                })
        
        return entries
    
    def _parse_ass(self, content: str) -> List[Dict[str, Any]]:
        """Parse ASS/SSA subtitle format."""
        entries = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Dialogue:'):
                # Parse ASS dialogue line
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    start_time = self._parse_ass_timestamp(parts[1])
                    end_time = self._parse_ass_timestamp(parts[2])
                    text = parts[9]
                    
                    # Clean ASS formatting
                    text = re.sub(r'\{[^}]*\}', '', text)  # Remove formatting tags
                    text = text.replace('\\N', '\n')  # Convert line breaks
                    
                    entries.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
        
        return entries
    
    def _parse_vtt_timestamp(self, line: str) -> Tuple[timedelta, timedelta]:
        """Parse VTT timestamp line."""
        # Remove cue settings
        timestamp_part = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2]
        start_str, end_str = timestamp_part.split(' --> ')
        
        start_time = self._parse_time_string(start_str)
        end_time = self._parse_time_string(end_str)
        
        return start_time, end_time
    
    def _parse_srt_timestamp(self, line: str) -> Tuple[timedelta, timedelta]:
        """Parse SRT timestamp line."""
        start_str, end_str = line.split(' --> ')
        
        start_time = self._parse_time_string(start_str.replace(',', '.'))
        end_time = self._parse_time_string(end_str.replace(',', '.'))
        
        return start_time, end_time
    
    def _parse_ass_timestamp(self, time_str: str) -> timedelta:
        """Parse ASS timestamp."""
        # ASS format: H:MM:SS.cc
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        centiseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        
        return timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=centiseconds * 10
        )
    
    def _parse_time_string(self, time_str: str) -> timedelta:
        """Parse time string in various formats."""
        # Handle formats like HH:MM:SS.mmm or MM:SS.mmm
        time_str = time_str.strip()
        
        if time_str.count(':') == 2:
            # HH:MM:SS.mmm
            hours, minutes, seconds = time_str.split(':')
            hours = int(hours)
        else:
            # MM:SS.mmm
            hours = 0
            minutes, seconds = time_str.split(':')
        
        minutes = int(minutes)
        
        if '.' in seconds:
            seconds_part, milliseconds_part = seconds.split('.')
            seconds = int(seconds_part)
            # Pad or truncate to 3 digits
            milliseconds_part = milliseconds_part.ljust(3, '0')[:3]
            milliseconds = int(milliseconds_part)
        else:
            seconds = int(seconds)
            milliseconds = 0
        
        return timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds
        )
    
    def _generate_srt(self, entries: List[Dict[str, Any]]) -> str:
        """Generate SRT format from subtitle entries."""
        srt_content = []
        
        for i, entry in enumerate(entries, 1):
            start_time = self._format_srt_timestamp(entry['start'])
            end_time = self._format_srt_timestamp(entry['end'])
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(entry['text'])
            srt_content.append("")  # Empty line between entries
        
        return '\n'.join(srt_content)
    
    def _generate_vtt(self, entries: List[Dict[str, Any]]) -> str:
        """Generate VTT format from subtitle entries."""
        vtt_content = ["WEBVTT", ""]
        
        for entry in entries:
            start_time = self._format_vtt_timestamp(entry['start'])
            end_time = self._format_vtt_timestamp(entry['end'])
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(entry['text'])
            vtt_content.append("")  # Empty line between entries
        
        return '\n'.join(vtt_content)
    
    def _format_srt_timestamp(self, td: timedelta) -> str:
        """Format timedelta as SRT timestamp."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = td.microseconds // 1000
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _format_vtt_timestamp(self, td: timedelta) -> str:
        """Format timedelta as VTT timestamp."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = td.microseconds // 1000
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    async def embed_subtitles(
        self, 
        video_path: Path, 
        subtitle_paths: List[Path]
    ) -> bool:
        """
        Embed subtitles into video file using ffmpeg.
        
        Args:
            video_path: Path to video file
            subtitle_paths: List of subtitle file paths
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.embed_subtitles or not subtitle_paths:
            return True
        
        try:
            import subprocess
            
            # Build ffmpeg command
            cmd = ['ffmpeg', '-i', str(video_path)]
            
            # Add subtitle inputs
            for subtitle_path in subtitle_paths:
                cmd.extend(['-i', str(subtitle_path)])
            
            # Map video and audio streams
            cmd.extend(['-map', '0:v', '-map', '0:a'])
            
            # Map subtitle streams
            for i in range(len(subtitle_paths)):
                cmd.extend(['-map', f'{i+1}:s'])
            
            # Copy codecs (no re-encoding)
            cmd.extend(['-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text'])
            
            # Output file
            output_path = video_path.with_suffix('.embedded' + video_path.suffix)
            cmd.append(str(output_path))
            
            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Replace original file
                video_path.unlink()
                output_path.rename(video_path)
                
                self.logger.info(f"Embedded subtitles in: {video_path}")
                return True
            else:
                self.logger.error(f"ffmpeg failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to embed subtitles: {e}")
            return False
