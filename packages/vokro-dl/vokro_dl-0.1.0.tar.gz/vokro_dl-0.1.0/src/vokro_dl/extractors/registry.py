"""
Extractor registry for VokroDL.

This module manages the registration and discovery of video extractors
for different platforms.
"""

import logging
from typing import Dict, List, Optional, Type, Any
from urllib.parse import urlparse

from .base import BaseExtractor
from ..core.exceptions import UnsupportedPlatformError


logger = logging.getLogger(__name__)


class ExtractorRegistry:
    """
    Registry for managing video extractors.
    
    This class handles the registration, discovery, and instantiation
    of extractors for different video platforms.
    """
    
    def __init__(self):
        """Initialize extractor registry."""
        self._extractors: Dict[str, Type[BaseExtractor]] = {}
        self._instances: Dict[str, BaseExtractor] = {}
        self._platform_configs: Dict[str, Dict[str, Any]] = {}
        
        # Register built-in extractors
        self._register_builtin_extractors()
    
    def register_extractor(
        self,
        extractor_class: Type[BaseExtractor],
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register an extractor class.
        
        Args:
            extractor_class: Extractor class to register
            config: Platform-specific configuration
        """
        platform_name = extractor_class.PLATFORM_NAME
        
        if not platform_name:
            raise ValueError(f"Extractor {extractor_class.__name__} must define PLATFORM_NAME")
        
        self._extractors[platform_name] = extractor_class
        
        if config:
            self._platform_configs[platform_name] = config
        
        logger.debug(f"Registered extractor for platform: {platform_name}")
    
    def unregister_extractor(self, platform_name: str) -> None:
        """
        Unregister an extractor.
        
        Args:
            platform_name: Platform name to unregister
        """
        if platform_name in self._extractors:
            del self._extractors[platform_name]
        
        if platform_name in self._instances:
            del self._instances[platform_name]
        
        if platform_name in self._platform_configs:
            del self._platform_configs[platform_name]
        
        logger.debug(f"Unregistered extractor for platform: {platform_name}")
    
    def get_extractor(self, url: str) -> Optional[BaseExtractor]:
        """
        Get appropriate extractor for URL.
        
        Args:
            url: Video URL
            
        Returns:
            Extractor instance or None if no suitable extractor found
        """
        # Try each registered extractor
        for platform_name, extractor_class in self._extractors.items():
            if extractor_class.can_handle(url):
                # Return cached instance or create new one
                if platform_name not in self._instances:
                    config = self._platform_configs.get(platform_name, {})
                    self._instances[platform_name] = extractor_class(config)
                
                return self._instances[platform_name]
        
        # No suitable extractor found
        return None
    
    def get_extractor_by_platform(self, platform_name: str) -> Optional[BaseExtractor]:
        """
        Get extractor by platform name.
        
        Args:
            platform_name: Platform name
            
        Returns:
            Extractor instance or None if not found
        """
        if platform_name not in self._extractors:
            return None
        
        if platform_name not in self._instances:
            extractor_class = self._extractors[platform_name]
            config = self._platform_configs.get(platform_name, {})
            self._instances[platform_name] = extractor_class(config)
        
        return self._instances[platform_name]
    
    def list_platforms(self) -> List[str]:
        """
        List all registered platforms.
        
        Returns:
            List of platform names
        """
        return list(self._extractors.keys())
    
    def list_extractors(self) -> Dict[str, Type[BaseExtractor]]:
        """
        List all registered extractors.
        
        Returns:
            Dictionary mapping platform names to extractor classes
        """
        return self._extractors.copy()
    
    def update_platform_config(self, platform_name: str, config: Dict[str, Any]) -> None:
        """
        Update configuration for a platform.
        
        Args:
            platform_name: Platform name
            config: New configuration
        """
        self._platform_configs[platform_name] = config
        
        # Update existing instance if it exists
        if platform_name in self._instances:
            self._instances[platform_name].config.update(config)
    
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """
        Get configuration for a platform.
        
        Args:
            platform_name: Platform name
            
        Returns:
            Platform configuration
        """
        return self._platform_configs.get(platform_name, {})
    
    def detect_platform(self, url: str) -> Optional[str]:
        """
        Detect platform from URL without creating extractor instance.
        
        Args:
            url: Video URL
            
        Returns:
            Platform name or None if not detected
        """
        for platform_name, extractor_class in self._extractors.items():
            if extractor_class.can_handle(url):
                return platform_name
        
        return None
    
    def is_supported(self, url: str) -> bool:
        """
        Check if URL is supported by any registered extractor.
        
        Args:
            url: Video URL
            
        Returns:
            True if supported, False otherwise
        """
        return self.detect_platform(url) is not None
    
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domains.
        
        Returns:
            List of domain names
        """
        domains = set()
        
        for extractor_class in self._extractors.values():
            for pattern in extractor_class.URL_PATTERNS:
                # Extract domain from pattern (simplified)
                pattern_str = pattern.pattern
                if 'youtube.com' in pattern_str or 'youtu.be' in pattern_str:
                    domains.update(['youtube.com', 'youtu.be'])
                elif 'vimeo.com' in pattern_str:
                    domains.add('vimeo.com')
                elif 'twitch.tv' in pattern_str:
                    domains.add('twitch.tv')
                elif 'tiktok.com' in pattern_str:
                    domains.add('tiktok.com')
                elif 'instagram.com' in pattern_str:
                    domains.add('instagram.com')
        
        return sorted(list(domains))
    
    async def close_all(self) -> None:
        """Close all extractor instances."""
        for instance in self._instances.values():
            await instance.close()
        
        self._instances.clear()
    
    def _register_builtin_extractors(self) -> None:
        """Register built-in extractors."""
        try:
            from .youtube import YouTubeExtractor
            self.register_extractor(YouTubeExtractor)
        except ImportError as e:
            logger.warning(f"Failed to register YouTube extractor: {e}")
        
        try:
            from .vimeo import VimeoExtractor
            self.register_extractor(VimeoExtractor)
        except ImportError as e:
            logger.warning(f"Failed to register Vimeo extractor: {e}")
        
        try:
            from .generic import GenericExtractor
            self.register_extractor(GenericExtractor)
        except ImportError as e:
            logger.warning(f"Failed to register Generic extractor: {e}")
        
        # Add more built-in extractors here as they are implemented
        logger.info(f"Registered {len(self._extractors)} built-in extractors")


# Global registry instance
_global_registry: Optional[ExtractorRegistry] = None


def get_global_registry() -> ExtractorRegistry:
    """
    Get the global extractor registry instance.
    
    Returns:
        Global ExtractorRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = ExtractorRegistry()
    
    return _global_registry


def register_extractor(
    extractor_class: Type[BaseExtractor],
    config: Optional[Dict[str, Any]] = None
) -> None:
    """
    Register an extractor in the global registry.
    
    Args:
        extractor_class: Extractor class to register
        config: Platform-specific configuration
    """
    registry = get_global_registry()
    registry.register_extractor(extractor_class, config)


def get_extractor_for_url(url: str) -> BaseExtractor:
    """
    Get extractor for URL from global registry.
    
    Args:
        url: Video URL
        
    Returns:
        Extractor instance
        
    Raises:
        UnsupportedPlatformError: If no suitable extractor found
    """
    registry = get_global_registry()
    extractor = registry.get_extractor(url)
    
    if extractor is None:
        raise UnsupportedPlatformError(url)
    
    return extractor


def is_url_supported(url: str) -> bool:
    """
    Check if URL is supported by any registered extractor.
    
    Args:
        url: Video URL
        
    Returns:
        True if supported, False otherwise
    """
    registry = get_global_registry()
    return registry.is_supported(url)
