"""
Main CLI interface for VokroDL.

This module provides the command-line interface with comprehensive
options and user-friendly help documentation.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from ..core.downloader import VokroDL
from ..core.config import DownloadConfig, GlobalConfig, QualityConfig, OutputConfig
from ..core.models import Quality, Container
from ..core.exceptions import VokroDLError
from ..utils.progress import SimpleProgressCallback


# Install rich traceback handler
install(show_locals=True)

console = Console()


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Setup logging configuration."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, version):
    """VokroDL - Advanced Video Downloading Library"""
    if version:
        from .. import __version__
        click.echo(f"VokroDL {__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--quality', '-q', 
              type=click.Choice([q.value for q in Quality]), 
              default=Quality.BEST.value,
              help='Video quality to download')
@click.option('--format', '-f', 
              type=click.Choice([c.value for c in Container]),
              help='Preferred container format')
@click.option('--output-dir', '-o', 
              type=click.Path(path_type=Path),
              help='Output directory')
@click.option('--filename-template', 
              default='%(title)s.%(ext)s',
              help='Filename template')
@click.option('--audio-only', is_flag=True, 
              help='Extract audio only')
@click.option('--audio-format', 
              type=click.Choice(['mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a']),
              default='mp3',
              help='Audio format for extraction')
@click.option('--subtitles', is_flag=True, 
              help='Download subtitles')
@click.option('--embed-subtitles', is_flag=True, 
              help='Embed subtitles in video')
@click.option('--subtitle-languages', 
              default='en',
              help='Comma-separated list of subtitle languages')
@click.option('--parallel', '-p', 
              type=click.IntRange(1, 10), 
              default=1,
              help='Number of parallel downloads')
@click.option('--resume/--no-resume', 
              default=True,
              help='Resume interrupted downloads')
@click.option('--overwrite', is_flag=True, 
              help='Overwrite existing files')
@click.option('--batch-file', '-a', 
              type=click.File('r'),
              help='File containing URLs to download')
@click.option('--config', '-c', 
              type=click.Path(exists=True, path_type=Path),
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, 
              help='Verbose output')
@click.option('--quiet', is_flag=True, 
              help='Quiet mode')
@click.option('--max-filesize', 
              help='Maximum file size (e.g., 100MB, 1GB)')
@click.option('--min-duration', 
              type=float,
              help='Minimum video duration in seconds')
@click.option('--max-duration', 
              type=float,
              help='Maximum video duration in seconds')
@click.option('--playlist-start', 
              type=int, 
              default=1,
              help='Playlist start index')
@click.option('--playlist-end', 
              type=int,
              help='Playlist end index')
@click.option('--playlist-reverse', is_flag=True, 
              help='Download playlist in reverse order')
def download(urls, **kwargs):
    """Download videos from URLs."""
    asyncio.run(_download_async(urls, **kwargs))


async def _download_async(urls: tuple, **kwargs):
    """Async download function."""
    # Setup logging
    setup_logging(kwargs['verbose'], kwargs['quiet'])
    
    try:
        # Load configuration
        global_config = GlobalConfig.load_default()
        if kwargs['config']:
            global_config = GlobalConfig.load_from_file(kwargs['config'])
        
        # Build download config from CLI options
        download_config = _build_download_config(**kwargs)
        
        # Collect URLs
        all_urls = list(urls)
        if kwargs['batch_file']:
            batch_urls = [line.strip() for line in kwargs['batch_file'] 
                         if line.strip() and not line.startswith('#')]
            all_urls.extend(batch_urls)
        
        if not all_urls:
            console.print("[red]No URLs provided[/red]")
            return
        
        # Create downloader
        async with VokroDL(download_config, global_config) as downloader:
            # Setup progress callback
            progress_callback = SimpleProgressCallback(console)
            
            if len(all_urls) == 1:
                # Single download
                try:
                    output_path = await downloader.download(
                        all_urls[0], 
                        progress_callback=progress_callback
                    )
                    console.print(f"[green]Downloaded:[/green] {output_path}")
                except VokroDLError as e:
                    console.print(f"[red]Error:[/red] {e}")
                    if e.suggestion:
                        console.print(f"[yellow]Suggestion:[/yellow] {e.suggestion}")
                    sys.exit(1)
            else:
                # Batch download
                console.print(f"[cyan]Starting batch download of {len(all_urls)} URLs...[/cyan]")
                
                def batch_progress_callback(url, progress):
                    console.print(f"[dim]{url}:[/dim] {progress.percent:.1f}%")
                
                try:
                    output_paths = await downloader.download_batch(
                        all_urls,
                        progress_callback=batch_progress_callback
                    )
                    
                    console.print(f"[green]Completed {len(output_paths)} downloads[/green]")
                    for path in output_paths:
                        console.print(f"  {path}")
                        
                except VokroDLError as e:
                    console.print(f"[red]Batch download failed:[/red] {e}")
                    sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if kwargs['verbose']:
            console.print_exception()
        sys.exit(1)


def _build_download_config(**kwargs) -> DownloadConfig:
    """Build download configuration from CLI arguments."""
    # Quality config
    quality_config = QualityConfig(
        preferred_quality=Quality(kwargs['quality']),
        preferred_format=Container(kwargs['format']) if kwargs['format'] else None,
    )
    
    # Output config
    output_config = OutputConfig(
        output_dir=kwargs['output_dir'] or Path.cwd(),
        filename_template=kwargs['filename_template'],
        overwrite=kwargs['overwrite'],
    )
    
    # Parse max filesize
    max_filesize = None
    if kwargs['max_filesize']:
        max_filesize = _parse_filesize(kwargs['max_filesize'])
    
    quality_config.max_filesize = max_filesize
    
    # Build main config
    config = DownloadConfig(
        quality=quality_config,
        output=output_config,
        parallel_downloads=kwargs['parallel'],
        resume_downloads=kwargs['resume'],
        min_duration=kwargs['min_duration'],
        max_duration=kwargs['max_duration'],
        playlist_start=kwargs['playlist_start'],
        playlist_end=kwargs['playlist_end'],
        playlist_reverse=kwargs['playlist_reverse'],
        verbose=kwargs['verbose'],
        quiet=kwargs['quiet'],
    )
    
    # Subtitle config
    config.subtitles.download_subtitles = kwargs['subtitles']
    config.subtitles.embed_subtitles = kwargs['embed_subtitles']
    config.subtitles.subtitle_languages = kwargs['subtitle_languages'].split(',')
    
    # Post-processing config
    config.post_processing.extract_audio = kwargs['audio_only']
    config.post_processing.audio_format = Container(kwargs['audio_format'])
    
    return config


def _parse_filesize(size_str: str) -> int:
    """Parse filesize string to bytes."""
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number_part = size_str[:-len(suffix)].strip()
            try:
                return int(float(number_part) * multiplier)
            except ValueError:
                break
    
    # Try to parse as plain number
    try:
        return int(size_str)
    except ValueError:
        raise click.BadParameter(f"Invalid file size: {size_str}")


@cli.command()
@click.argument('url')
@click.option('--json', 'output_json', is_flag=True, 
              help='Output information as JSON')
def info(url, output_json):
    """Extract video information without downloading."""
    asyncio.run(_info_async(url, output_json))


async def _info_async(url: str, output_json: bool):
    """Async info extraction function."""
    try:
        global_config = GlobalConfig.load_default()
        
        async with VokroDL(global_config=global_config) as downloader:
            video_info = await downloader.extract_info(url)
            
            if output_json:
                import json
                console.print(json.dumps(video_info.dict(), indent=2, default=str))
            else:
                _print_video_info(video_info)
                
    except VokroDLError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _print_video_info(video_info):
    """Print video information in a readable format."""
    from rich.table import Table
    
    table = Table(title=f"Video Information: {video_info.title}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("ID", video_info.id)
    table.add_row("Title", video_info.title)
    table.add_row("Platform", video_info.platform)
    table.add_row("Uploader", video_info.uploader or "Unknown")
    table.add_row("Duration", f"{video_info.duration:.1f}s" if video_info.duration else "Unknown")
    table.add_row("View Count", f"{video_info.view_count:,}" if video_info.view_count else "Unknown")
    table.add_row("Upload Date", str(video_info.upload_date) if video_info.upload_date else "Unknown")
    table.add_row("Formats", str(len(video_info.formats)))
    table.add_row("Subtitles", str(len(video_info.subtitles)))
    
    console.print(table)
    
    if video_info.formats:
        formats_table = Table(title="Available Formats")
        formats_table.add_column("ID", style="cyan")
        formats_table.add_column("Container", style="green")
        formats_table.add_column("Quality", style="yellow")
        formats_table.add_column("Codec", style="blue")
        
        for fmt in video_info.formats[:10]:  # Show first 10 formats
            quality = f"{fmt.width}x{fmt.height}" if fmt.width and fmt.height else "Unknown"
            codec = f"{fmt.video_codec.value if fmt.video_codec else 'Unknown'}"
            
            formats_table.add_row(
                fmt.format_id,
                fmt.container.value,
                quality,
                codec
            )
        
        console.print(formats_table)


@cli.command()
def config():
    """Show current configuration."""
    try:
        global_config = GlobalConfig.load_default()
        config_path = GlobalConfig.get_default_config_path()
        
        console.print(f"[cyan]Configuration file:[/cyan] {config_path}")
        console.print(f"[cyan]Exists:[/cyan] {config_path.exists()}")
        
        if config_path.exists():
            console.print("\n[cyan]Current configuration:[/cyan]")
            import yaml
            console.print(yaml.dump(global_config.dict(), default_flow_style=False))
        else:
            console.print("\n[yellow]Using default configuration[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {e}")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
