"""
Quality and format selection utilities for VokroDL.

This module provides intelligent quality selection based on various criteria
including bandwidth, user preferences, and available formats.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..core.models import Format, Quality, Container, Codec, FormatType
from ..core.config import QualityConfig


logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality scoring information."""
    format_obj: Format
    score: float
    reasons: List[str]
    bandwidth_suitable: bool = True
    size_suitable: bool = True


class QualitySelector:
    """
    Intelligent quality and format selector.
    
    This class implements sophisticated logic for selecting the best
    video/audio format based on user preferences, bandwidth, and
    other criteria.
    """
    
    def __init__(self, config: QualityConfig, available_bandwidth: Optional[float] = None):
        """
        Initialize quality selector.
        
        Args:
            config: Quality configuration
            available_bandwidth: Available bandwidth in bytes/second
        """
        self.config = config
        self.available_bandwidth = available_bandwidth
        
        # Quality preference weights
        self.quality_weights = {
            'resolution': 0.4,
            'bitrate': 0.3,
            'codec': 0.2,
            'container': 0.1
        }
        
        # Codec preference scores (higher is better)
        self.codec_scores = {
            # Video codecs
            Codec.AV1: 100,
            Codec.H265: 90,
            Codec.VP9: 85,
            Codec.H264: 80,
            Codec.VP8: 70,
            
            # Audio codecs
            Codec.OPUS: 100,
            Codec.AAC_CODEC: 90,
            Codec.VORBIS: 80,
            Codec.MP3_CODEC: 70,
            Codec.FLAC_CODEC: 95,  # High quality but large
        }
        
        # Container preference scores
        self.container_scores = {
            Container.WEBM: 100 if config.prefer_free_formats else 80,
            Container.MP4: 95,
            Container.MKV: 90,
            Container.AVI: 60,
            Container.FLV: 40,
            Container.MOV: 85,
            
            # Audio containers
            Container.OGG: 100 if config.prefer_free_formats else 80,
            Container.FLAC: 95,
            Container.MP3: 85,
            Container.AAC: 90,
            Container.M4A: 88,
            Container.WAV: 70,  # Uncompressed, large
        }
    
    def select_best_format(
        self, 
        formats: List[Format], 
        format_type: FormatType = FormatType.VIDEO
    ) -> Optional[Format]:
        """
        Select the best format from available options.
        
        Args:
            formats: List of available formats
            format_type: Type of format to select
            
        Returns:
            Best format or None if no suitable format found
        """
        if not formats:
            return None
        
        # Filter by format type
        matching_formats = [f for f in formats if f.format_type == format_type]
        if not matching_formats:
            return None
        
        # Handle specific quality requests
        if self.config.preferred_quality != Quality.BEST and self.config.preferred_quality != Quality.WORST:
            specific_format = self._select_specific_quality(matching_formats)
            if specific_format:
                return specific_format
        
        # Score all formats
        scored_formats = []
        for fmt in matching_formats:
            score_info = self._calculate_format_score(fmt)
            scored_formats.append(score_info)
        
        # Filter by constraints
        suitable_formats = self._filter_by_constraints(scored_formats)
        
        if not suitable_formats:
            logger.warning("No formats meet the specified constraints")
            # Fallback to all formats if none meet constraints
            suitable_formats = scored_formats
        
        # Sort by score
        suitable_formats.sort(key=lambda x: x.score, reverse=True)
        
        # Handle best/worst selection
        if self.config.preferred_quality == Quality.WORST:
            return suitable_formats[-1].format_obj
        else:
            return suitable_formats[0].format_obj
    
    def _select_specific_quality(self, formats: List[Format]) -> Optional[Format]:
        """Select format matching specific quality requirement."""
        target_height = self._quality_to_height(self.config.preferred_quality)
        if not target_height:
            return None
        
        # Find exact matches first
        exact_matches = [f for f in formats if f.height == target_height]
        if exact_matches:
            # Return best quality among exact matches
            return max(exact_matches, key=lambda f: self._calculate_format_score(f).score)
        
        # Find closest match
        formats_with_height = [f for f in formats if f.height is not None]
        if not formats_with_height:
            return None
        
        closest_format = min(
            formats_with_height,
            key=lambda f: abs(f.height - target_height)
        )
        
        return closest_format
    
    def _quality_to_height(self, quality: Quality) -> Optional[int]:
        """Convert quality enum to height in pixels."""
        quality_map = {
            Quality.RESOLUTION_144P: 144,
            Quality.RESOLUTION_240P: 240,
            Quality.RESOLUTION_360P: 360,
            Quality.RESOLUTION_480P: 480,
            Quality.RESOLUTION_720P: 720,
            Quality.RESOLUTION_1080P: 1080,
            Quality.RESOLUTION_1440P: 1440,
            Quality.RESOLUTION_2160P: 2160,
            Quality.RESOLUTION_4320P: 4320,
        }
        return quality_map.get(quality)
    
    def _calculate_format_score(self, fmt: Format) -> QualityScore:
        """Calculate comprehensive quality score for a format."""
        score = 0.0
        reasons = []
        
        # Resolution score
        if fmt.height:
            resolution_score = min(fmt.height / 1080.0, 2.0) * 100  # Normalize to 1080p
            score += resolution_score * self.quality_weights['resolution']
            reasons.append(f"resolution: {fmt.height}p ({resolution_score:.1f})")
        
        # Bitrate score
        if fmt.bitrate:
            # Normalize bitrate (assume 5000 kbps as reference for 1080p)
            bitrate_score = min(fmt.bitrate / 5000.0, 2.0) * 100
            score += bitrate_score * self.quality_weights['bitrate']
            reasons.append(f"bitrate: {fmt.bitrate}kbps ({bitrate_score:.1f})")
        
        # Codec score
        codec_score = 0
        if fmt.video_codec:
            codec_score += self.codec_scores.get(fmt.video_codec, 50)
        if fmt.audio_codec:
            codec_score += self.codec_scores.get(fmt.audio_codec, 50)
        
        if codec_score > 0:
            score += codec_score * self.quality_weights['codec']
            reasons.append(f"codec: {codec_score:.1f}")
        
        # Container score
        container_score = self.container_scores.get(fmt.container, 50)
        score += container_score * self.quality_weights['container']
        reasons.append(f"container: {fmt.container.value} ({container_score:.1f})")
        
        # Preferred format bonus
        if self.config.preferred_format and fmt.container == self.config.preferred_format:
            score += 20
            reasons.append("preferred format bonus")
        
        # Free format bonus
        if self.config.prefer_free_formats:
            free_containers = {Container.WEBM, Container.OGG, Container.FLAC}
            free_codecs = {Codec.VP8, Codec.VP9, Codec.AV1, Codec.OPUS, Codec.VORBIS}
            
            if fmt.container in free_containers:
                score += 10
                reasons.append("free container bonus")
            
            if fmt.video_codec in free_codecs or fmt.audio_codec in free_codecs:
                score += 10
                reasons.append("free codec bonus")
        
        return QualityScore(
            format_obj=fmt,
            score=score,
            reasons=reasons
        )
    
    def _filter_by_constraints(self, scored_formats: List[QualityScore]) -> List[QualityScore]:
        """Filter formats by bandwidth and size constraints."""
        suitable_formats = []
        
        for score_info in scored_formats:
            fmt = score_info.format_obj
            
            # Check bandwidth constraint
            if self.available_bandwidth and fmt.bitrate:
                # Convert bitrate from kbps to bytes/second
                required_bandwidth = (fmt.bitrate * 1000) / 8
                if required_bandwidth > self.available_bandwidth * 0.8:  # 80% safety margin
                    score_info.bandwidth_suitable = False
                    logger.debug(f"Format {fmt.format_id} requires too much bandwidth")
                    continue
            
            # Check file size constraint
            if self.config.max_filesize and fmt.filesize:
                if fmt.filesize > self.config.max_filesize:
                    score_info.size_suitable = False
                    logger.debug(f"Format {fmt.format_id} exceeds max file size")
                    continue
            
            suitable_formats.append(score_info)
        
        return suitable_formats
    
    def get_format_recommendations(
        self, 
        formats: List[Format], 
        format_type: FormatType = FormatType.VIDEO,
        count: int = 3
    ) -> List[Tuple[Format, float, List[str]]]:
        """
        Get top format recommendations with scores and reasons.
        
        Args:
            formats: Available formats
            format_type: Type of format
            count: Number of recommendations to return
            
        Returns:
            List of (format, score, reasons) tuples
        """
        matching_formats = [f for f in formats if f.format_type == format_type]
        
        scored_formats = []
        for fmt in matching_formats:
            score_info = self._calculate_format_score(fmt)
            scored_formats.append(score_info)
        
        # Sort by score
        scored_formats.sort(key=lambda x: x.score, reverse=True)
        
        # Return top recommendations
        recommendations = []
        for score_info in scored_formats[:count]:
            recommendations.append((
                score_info.format_obj,
                score_info.score,
                score_info.reasons
            ))
        
        return recommendations
    
    def estimate_download_time(self, fmt: Format) -> Optional[float]:
        """
        Estimate download time for a format.
        
        Args:
            fmt: Format to estimate
            
        Returns:
            Estimated download time in seconds, or None if cannot estimate
        """
        if not self.available_bandwidth or not fmt.filesize:
            return None
        
        # Account for protocol overhead and other factors
        effective_bandwidth = self.available_bandwidth * 0.7
        
        return fmt.filesize / effective_bandwidth
    
    def get_bandwidth_recommendation(self, formats: List[Format]) -> Optional[str]:
        """
        Get bandwidth recommendation based on available formats.
        
        Args:
            formats: Available formats
            
        Returns:
            Bandwidth recommendation string
        """
        if not self.available_bandwidth:
            return None
        
        # Convert to Mbps for user-friendly display
        bandwidth_mbps = (self.available_bandwidth * 8) / (1000 * 1000)
        
        if bandwidth_mbps >= 25:
            return "Your bandwidth is excellent for 4K video"
        elif bandwidth_mbps >= 10:
            return "Your bandwidth is good for 1080p video"
        elif bandwidth_mbps >= 5:
            return "Your bandwidth is suitable for 720p video"
        elif bandwidth_mbps >= 2:
            return "Your bandwidth is suitable for 480p video"
        else:
            return "Consider audio-only or very low quality video"


class AdaptiveQualitySelector(QualitySelector):
    """
    Adaptive quality selector that learns from user preferences and network conditions.
    """
    
    def __init__(self, config: QualityConfig, available_bandwidth: Optional[float] = None):
        super().__init__(config, available_bandwidth)
        self.download_history: List[Dict[str, Any]] = []
        self.preference_weights = self.quality_weights.copy()
    
    def record_download(
        self, 
        selected_format: Format, 
        download_time: float, 
        user_satisfaction: Optional[float] = None
    ):
        """
        Record download for learning purposes.
        
        Args:
            selected_format: Format that was downloaded
            download_time: Actual download time
            user_satisfaction: User satisfaction score (0-1)
        """
        record = {
            'format': selected_format,
            'download_time': download_time,
            'satisfaction': user_satisfaction,
            'timestamp': __import__('time').time()
        }
        
        self.download_history.append(record)
        
        # Keep only recent history
        if len(self.download_history) > 100:
            self.download_history = self.download_history[-100:]
        
        # Update preferences based on history
        self._update_preferences()
    
    def _update_preferences(self):
        """Update preference weights based on download history."""
        if len(self.download_history) < 5:
            return
        
        # Analyze successful downloads
        successful_downloads = [
            record for record in self.download_history
            if record.get('satisfaction', 0.5) > 0.7
        ]
        
        if not successful_downloads:
            return
        
        # Adjust weights based on successful patterns
        # This is a simplified implementation - could be much more sophisticated
        avg_resolution = sum(
            record['format'].height or 720 
            for record in successful_downloads
        ) / len(successful_downloads)
        
        if avg_resolution > 1080:
            self.preference_weights['resolution'] += 0.05
        elif avg_resolution < 480:
            self.preference_weights['bitrate'] += 0.05
        
        # Normalize weights
        total_weight = sum(self.preference_weights.values())
        for key in self.preference_weights:
            self.preference_weights[key] /= total_weight
