"""
Progress tracking utilities for VokroDL.

This module provides progress tracking and reporting functionality
with support for multiple concurrent downloads.
"""

import asyncio
import time
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta

from rich.console import Console
from rich.progress import (
    Progress, TaskID, BarColumn, TextColumn, 
    DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
)
from rich.table import Table
from rich.live import Live

from ..core.models import DownloadProgress


class ProgressTracker:
    """Tracks progress for multiple downloads."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self._downloads: Dict[str, DownloadProgress] = {}
        self._callbacks: Dict[str, Callable[[DownloadProgress], None]] = {}
        self._console = Console()
        self._progress_display: Optional[Progress] = None
        self._live_display: Optional[Live] = None
        self._task_ids: Dict[str, TaskID] = {}
    
    def add_download(
        self, 
        download_id: str, 
        filename: str,
        total_bytes: Optional[int] = None,
        callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> None:
        """
        Add a new download to track.
        
        Args:
            download_id: Unique identifier for the download
            filename: Name of the file being downloaded
            total_bytes: Total size in bytes (if known)
            callback: Optional callback for progress updates
        """
        progress = DownloadProgress(
            filename=filename,
            total_bytes=total_bytes,
            started_at=datetime.now()
        )
        
        self._downloads[download_id] = progress
        
        if callback:
            self._callbacks[download_id] = callback
        
        # Add to rich progress display if active
        if self._progress_display:
            task_id = self._progress_display.add_task(
                f"[cyan]{filename}[/cyan]",
                total=total_bytes
            )
            self._task_ids[download_id] = task_id
    
    def update_progress(
        self,
        download_id: str,
        downloaded_bytes: int,
        speed: Optional[float] = None,
        status: Optional[str] = None
    ) -> None:
        """
        Update progress for a download.
        
        Args:
            download_id: Download identifier
            downloaded_bytes: Bytes downloaded so far
            speed: Current download speed in bytes/second
            status: Current status string
        """
        if download_id not in self._downloads:
            return
        
        progress = self._downloads[download_id]
        progress.downloaded_bytes = downloaded_bytes
        
        if speed is not None:
            progress.speed = speed
        
        if status is not None:
            progress.status = status
        
        # Calculate percentage and ETA
        if progress.total_bytes:
            progress.percent = (downloaded_bytes / progress.total_bytes) * 100
            
            if progress.speed > 0:
                remaining_bytes = progress.total_bytes - downloaded_bytes
                eta_seconds = remaining_bytes / progress.speed
                progress.eta = timedelta(seconds=eta_seconds)
        
        # Update elapsed time
        progress.elapsed = datetime.now() - progress.started_at
        
        # Update rich progress display
        if download_id in self._task_ids and self._progress_display:
            self._progress_display.update(
                self._task_ids[download_id],
                completed=downloaded_bytes,
                description=f"[cyan]{progress.filename}[/cyan] - {progress.status}"
            )
        
        # Call callback if registered
        if download_id in self._callbacks:
            self._callbacks[download_id](progress)
    
    def complete_download(self, download_id: str) -> None:
        """
        Mark a download as completed.
        
        Args:
            download_id: Download identifier
        """
        if download_id in self._downloads:
            progress = self._downloads[download_id]
            progress.status = "completed"
            progress.percent = 100.0
            
            # Update rich progress display
            if download_id in self._task_ids and self._progress_display:
                self._progress_display.update(
                    self._task_ids[download_id],
                    completed=progress.total_bytes or progress.downloaded_bytes,
                    description=f"[green]{progress.filename}[/green] - completed"
                )
            
            # Call callback
            if download_id in self._callbacks:
                self._callbacks[download_id](progress)
    
    def fail_download(self, download_id: str, error: str) -> None:
        """
        Mark a download as failed.
        
        Args:
            download_id: Download identifier
            error: Error message
        """
        if download_id in self._downloads:
            progress = self._downloads[download_id]
            progress.status = f"failed: {error}"
            
            # Update rich progress display
            if download_id in self._task_ids and self._progress_display:
                self._progress_display.update(
                    self._task_ids[download_id],
                    description=f"[red]{progress.filename}[/red] - failed"
                )
            
            # Call callback
            if download_id in self._callbacks:
                self._callbacks[download_id](progress)
    
    def get_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """
        Get current progress for a download.
        
        Args:
            download_id: Download identifier
            
        Returns:
            DownloadProgress object or None if not found
        """
        return self._downloads.get(download_id)
    
    def get_all_progress(self) -> Dict[str, DownloadProgress]:
        """
        Get progress for all downloads.
        
        Returns:
            Dictionary mapping download IDs to progress objects
        """
        return self._downloads.copy()
    
    def start_rich_display(self) -> None:
        """Start rich progress display for console output."""
        if self._progress_display is None:
            self._progress_display = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
                console=self._console
            )
            
            self._live_display = Live(
                self._progress_display,
                console=self._console,
                refresh_per_second=10
            )
            self._live_display.start()
    
    def stop_rich_display(self) -> None:
        """Stop rich progress display."""
        if self._live_display:
            self._live_display.stop()
            self._live_display = None
        
        self._progress_display = None
        self._task_ids.clear()
    
    def print_summary(self) -> None:
        """Print a summary of all downloads."""
        if not self._downloads:
            return
        
        table = Table(title="Download Summary")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Size", justify="right")
        table.add_column("Speed", justify="right")
        table.add_column("Time", justify="right")
        
        for download_id, progress in self._downloads.items():
            status_style = "green" if progress.status == "completed" else "red"
            
            table.add_row(
                progress.filename or "Unknown",
                f"[{status_style}]{progress.status}[/{status_style}]",
                progress.size_human,
                progress.speed_human,
                str(progress.elapsed).split('.')[0]  # Remove microseconds
            )
        
        self._console.print(table)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_rich_display()
        self._downloads.clear()
        self._callbacks.clear()


class SimpleProgressCallback:
    """Simple progress callback that prints to console."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize simple progress callback.
        
        Args:
            console: Rich console instance
        """
        self.console = console or Console()
        self.last_update = 0
    
    def __call__(self, progress: DownloadProgress) -> None:
        """
        Handle progress update.
        
        Args:
            progress: Progress information
        """
        # Throttle updates to avoid spam
        current_time = time.time()
        if current_time - self.last_update < 0.5:  # Update every 0.5 seconds
            return
        
        self.last_update = current_time
        
        # Format progress message
        if progress.total_bytes:
            message = (
                f"[cyan]{progress.filename}[/cyan]: "
                f"{progress.percent:.1f}% "
                f"({progress.size_human}) "
                f"at {progress.speed_human}"
            )
            
            if progress.eta:
                eta_str = str(progress.eta).split('.')[0]  # Remove microseconds
                message += f" ETA: {eta_str}"
        else:
            message = (
                f"[cyan]{progress.filename}[/cyan]: "
                f"{progress.downloaded_bytes:,} bytes "
                f"at {progress.speed_human}"
            )
        
        self.console.print(message)


class BatchProgressTracker:
    """Tracks progress for batch downloads."""
    
    def __init__(self):
        """Initialize batch progress tracker."""
        self.total_downloads = 0
        self.completed_downloads = 0
        self.failed_downloads = 0
        self.active_downloads = 0
        self.start_time = time.time()
    
    def add_download(self) -> None:
        """Add a download to the batch."""
        self.total_downloads += 1
        self.active_downloads += 1
    
    def complete_download(self) -> None:
        """Mark a download as completed."""
        self.completed_downloads += 1
        self.active_downloads -= 1
    
    def fail_download(self) -> None:
        """Mark a download as failed."""
        self.failed_downloads += 1
        self.active_downloads -= 1
    
    @property
    def completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if self.total_downloads == 0:
            return 0.0
        
        return ((self.completed_downloads + self.failed_downloads) / self.total_downloads) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def estimated_time_remaining(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.completed_downloads == 0:
            return None
        
        avg_time_per_download = self.elapsed_time / self.completed_downloads
        remaining_downloads = self.total_downloads - self.completed_downloads - self.failed_downloads
        
        return avg_time_per_download * remaining_downloads
    
    def get_summary(self) -> Dict[str, Any]:
        """Get batch progress summary."""
        return {
            'total': self.total_downloads,
            'completed': self.completed_downloads,
            'failed': self.failed_downloads,
            'active': self.active_downloads,
            'completion_percentage': self.completion_percentage,
            'elapsed_time': self.elapsed_time,
            'estimated_time_remaining': self.estimated_time_remaining,
        }
