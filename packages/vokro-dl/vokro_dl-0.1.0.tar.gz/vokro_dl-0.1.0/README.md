# VokroDL - Advanced Video Downloading Library

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/vokrob/vokro-dl/workflows/tests/badge.svg)](https://github.com/vokrob/vokro-dl/actions)
[![Coverage](https://codecov.io/gh/vokrob/vokro-dl/branch/main/graph/badge.svg)](https://codecov.io/gh/vokrob/vokro-dl)

A comprehensive video downloading library that surpasses yt-dlp in terms of usability and functionality. VokroDL provides a modern Python API with async support, better error handling, and enhanced features for downloading videos from major platforms.

## 🚀 Features

### Core Capabilities
- **Multi-Platform Support**: YouTube, Vimeo, Twitch, TikTok, Instagram, and more
- **Modern Python API**: Type hints, async/await support, and clean interfaces
- **Superior Error Handling**: User-friendly error messages and automatic recovery
- **Progress Tracking**: Detailed download statistics and real-time progress
- **Quality Selection**: Intelligent format and quality selection
- **Metadata Extraction**: Comprehensive video information and embedding

### Enhanced Usability
- **Intuitive CLI**: Better help documentation and user experience
- **Simple API**: Easy integration into other Python projects
- **Configuration Support**: YAML/TOML config files for default settings
- **Batch Downloads**: Playlist and bulk downloading capabilities
- **Resume Downloads**: Automatic resume of interrupted downloads
- **Smart Retry**: Exponential backoff and automatic retry mechanisms

### Advanced Features
- **Parallel Downloads**: Multi-threaded downloading for improved speed
- **Bandwidth Awareness**: Smart quality selection based on connection speed
- **Subtitle Support**: Download and embed subtitles in multiple languages
- **Audio Extraction**: High-quality audio-only downloads
- **Post-Processing**: Custom hooks and built-in format conversion
- **Plugin System**: Extensible architecture for new platforms
- **Memory Efficient**: Optimized for large files and batch operations

## 📦 Installation

```bash
# Install from PyPI (recommended)
pip install vokro-dl

# Install with development dependencies
pip install vokro-dl[dev]

# Install from source
git clone https://github.com/vokrob/vokro-dl.git
cd vokro-dl
pip install -e .
```

## 🔧 Quick Start

### Command Line Interface

```bash
# Basic download
vokro-dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download with specific quality
vokro-dl --quality 720p "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download playlist
vokro-dl --playlist "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8VGOmm"

# Audio only
vokro-dl --audio-only --format mp3 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Batch download from file
vokro-dl --batch-file urls.txt --output-dir ./downloads
```

### Python API

```python
import asyncio
from vokro_dl import VokroDL, DownloadConfig

async def main():
    # Simple download
    downloader = VokroDL()
    await downloader.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    # Advanced configuration
    config = DownloadConfig(
        quality="best",
        output_dir="./downloads",
        audio_only=False,
        subtitles=True,
        parallel_downloads=3
    )
    
    downloader = VokroDL(config)
    
    # Download with progress callback
    async def progress_callback(progress):
        print(f"Downloaded: {progress.percent:.1f}% - {progress.speed}")
    
    await downloader.download(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        progress_callback=progress_callback
    )

# Synchronous API also available
from vokro_dl.sync import VokroDLSync

downloader = VokroDLSync()
downloader.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

asyncio.run(main())
```

## 📖 Documentation

- [User Guide](https://vokro-dl.readthedocs.io/en/latest/user-guide/)
- [API Reference](https://vokro-dl.readthedocs.io/en/latest/api/)
- [Configuration](https://vokro-dl.readthedocs.io/en/latest/configuration/)
- [Plugin Development](https://vokro-dl.readthedocs.io/en/latest/plugins/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the excellent work of yt-dlp and youtube-dl projects
- Built with modern Python best practices and async/await support
- Thanks to all contributors and the open-source community
