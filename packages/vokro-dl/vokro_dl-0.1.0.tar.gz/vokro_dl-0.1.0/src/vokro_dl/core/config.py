"""
Configuration management for VokroDL.

This module provides configuration classes and utilities for managing
download settings, global preferences, and user configurations.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
import yaml
import toml
from pydantic import BaseModel, Field, validator

from .models import Quality, Container, FormatType
from .exceptions import ConfigurationError


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    
    max_retries: int = Field(3, ge=0, description="Maximum number of retries")
    initial_delay: float = Field(1.0, gt=0, description="Initial delay in seconds")
    max_delay: float = Field(60.0, gt=0, description="Maximum delay in seconds")
    exponential_base: float = Field(2.0, gt=1, description="Exponential backoff base")
    jitter: bool = Field(True, description="Add random jitter to delays")


class NetworkConfig(BaseModel):
    """Network-related configuration."""
    
    timeout: float = Field(30.0, gt=0, description="Request timeout in seconds")
    max_connections: int = Field(10, ge=1, description="Maximum concurrent connections")
    user_agent: str = Field(
        "VokroDL/0.1.0 (+https://github.com/vokrob/vokro-dl)",
        description="User agent string"
    )
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers")
    proxy: Optional[str] = Field(None, description="Proxy URL")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")


class OutputConfig(BaseModel):
    """Output and file naming configuration."""
    
    output_dir: Path = Field(Path.cwd(), description="Output directory")
    filename_template: str = Field(
        "%(title)s.%(ext)s",
        description="Filename template"
    )
    overwrite: bool = Field(False, description="Overwrite existing files")
    create_dirs: bool = Field(True, description="Create output directories")
    
    @validator('output_dir')
    def validate_output_dir(cls, v):
        """Ensure output directory is a Path object."""
        if isinstance(v, str):
            return Path(v)
        return v


class QualityConfig(BaseModel):
    """Quality selection configuration."""
    
    preferred_quality: Quality = Field(Quality.BEST, description="Preferred video quality")
    preferred_format: Optional[Container] = Field(None, description="Preferred container format")
    audio_quality: str = Field("best", description="Audio quality preference")
    prefer_free_formats: bool = Field(True, description="Prefer open/free formats")
    max_filesize: Optional[int] = Field(None, description="Maximum file size in bytes")


class SubtitleConfig(BaseModel):
    """Subtitle configuration."""
    
    download_subtitles: bool = Field(False, description="Download subtitles")
    embed_subtitles: bool = Field(False, description="Embed subtitles in video")
    subtitle_languages: List[str] = Field(
        default_factory=lambda: ["en"],
        description="Preferred subtitle languages"
    )
    auto_generated_subtitles: bool = Field(False, description="Include auto-generated subtitles")


class PostProcessingConfig(BaseModel):
    """Post-processing configuration."""
    
    convert_format: Optional[Container] = Field(None, description="Convert to format")
    extract_audio: bool = Field(False, description="Extract audio only")
    audio_format: Container = Field(Container.MP3, description="Audio format for extraction")
    embed_metadata: bool = Field(True, description="Embed metadata in files")
    embed_thumbnails: bool = Field(False, description="Embed thumbnails")
    
    # Custom post-processing hooks
    post_processors: List[str] = Field(
        default_factory=list,
        description="List of post-processor names"
    )


class DownloadConfig(BaseModel):
    """Main download configuration."""
    
    # Core settings
    quality: QualityConfig = Field(default_factory=QualityConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    subtitles: SubtitleConfig = Field(default_factory=SubtitleConfig)
    post_processing: PostProcessingConfig = Field(default_factory=PostProcessingConfig)
    
    # Download behavior
    parallel_downloads: int = Field(1, ge=1, le=10, description="Number of parallel downloads")
    resume_downloads: bool = Field(True, description="Resume interrupted downloads")
    
    # Playlist settings
    playlist_start: int = Field(1, ge=1, description="Playlist start index")
    playlist_end: Optional[int] = Field(None, description="Playlist end index")
    playlist_reverse: bool = Field(False, description="Download playlist in reverse")
    
    # Filtering
    min_duration: Optional[float] = Field(None, description="Minimum video duration")
    max_duration: Optional[float] = Field(None, description="Maximum video duration")
    
    # Logging and progress
    verbose: bool = Field(False, description="Verbose output")
    quiet: bool = Field(False, description="Quiet mode")
    progress_template: str = Field(
        "%(percent)s %(speed)s ETA %(eta)s",
        description="Progress display template"
    )
    
    @validator('playlist_end')
    def validate_playlist_end(cls, v, values):
        """Validate playlist end is greater than start."""
        if v is not None and 'playlist_start' in values:
            if v < values['playlist_start']:
                raise ValueError("playlist_end must be greater than playlist_start")
        return v


class GlobalConfig(BaseModel):
    """Global application configuration."""
    
    # Default download config
    defaults: DownloadConfig = Field(default_factory=DownloadConfig)
    
    # Platform-specific settings
    platform_configs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Platform-specific configurations"
    )
    
    # Authentication
    auth_configs: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Authentication configurations"
    )
    
    # Plugin settings
    enabled_plugins: List[str] = Field(
        default_factory=list,
        description="List of enabled plugin names"
    )
    plugin_configs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Plugin-specific configurations"
    )
    
    # Cache settings
    cache_dir: Path = Field(
        Path.home() / ".cache" / "vokro-dl",
        description="Cache directory"
    )
    cache_enabled: bool = Field(True, description="Enable caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    
    @classmethod
    def load_from_file(cls, config_path: Union[str, Path]) -> "GlobalConfig":
        """Load configuration from file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.toml':
                    data = toml.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration format: {config_path.suffix}"
                    )
            
            return cls(**data)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.dict(exclude_none=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.toml':
                    toml.dump(data, f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration format: {config_path.suffix}"
                    )
                    
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        # Check environment variable first
        if env_path := os.getenv('VOKRO_DL_CONFIG'):
            return Path(env_path)
        
        # Check common locations
        config_dirs = [
            Path.home() / ".config" / "vokro-dl",
            Path.home() / ".vokro-dl",
            Path.cwd(),
        ]
        
        for config_dir in config_dirs:
            for filename in ["config.yaml", "config.yml", "config.toml"]:
                config_path = config_dir / filename
                if config_path.exists():
                    return config_path
        
        # Return default location
        return Path.home() / ".config" / "vokro-dl" / "config.yaml"
    
    @classmethod
    def load_default(cls) -> "GlobalConfig":
        """Load configuration from default location."""
        config_path = cls.get_default_config_path()
        
        if config_path.exists():
            return cls.load_from_file(config_path)
        else:
            # Return default configuration
            return cls()


def merge_configs(base: DownloadConfig, override: DownloadConfig) -> DownloadConfig:
    """Merge two download configurations, with override taking precedence."""
    base_dict = base.dict()
    override_dict = override.dict(exclude_unset=True)
    
    def deep_merge(base_dict: dict, override_dict: dict) -> dict:
        """Recursively merge dictionaries."""
        result = base_dict.copy()
        
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    merged_dict = deep_merge(base_dict, override_dict)
    return DownloadConfig(**merged_dict)
