"""
Performance optimization utilities for VokroDL.

This module provides performance monitoring, memory optimization,
and benchmarking capabilities.
"""

import asyncio
import gc
import logging
import psutil
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    
    operation_name: str
    duration: float
    memory_used: int
    peak_memory: int
    cpu_percent: float
    network_bytes: int = 0
    disk_bytes: int = 0


class PerformanceMonitor:
    """Monitors performance metrics during operations."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process()
        
    @asynccontextmanager
    async def monitor_async(self, operation_name: str) -> AsyncGenerator[PerformanceMetrics, None]:
        """
        Monitor async operation performance.
        
        Args:
            operation_name: Name of the operation being monitored
            
        Yields:
            PerformanceMetrics object that gets updated during operation
        """
        # Initial measurements
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        start_cpu_time = self.process.cpu_times()
        
        # Create metrics object
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            duration=0.0,
            memory_used=0,
            peak_memory=start_memory,
            cpu_percent=0.0
        )
        
        try:
            yield metrics
        finally:
            # Final measurements
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            end_cpu_time = self.process.cpu_times()
            
            # Calculate metrics
            metrics.duration = end_time - start_time
            metrics.memory_used = end_memory - start_memory
            metrics.peak_memory = max(metrics.peak_memory, end_memory)
            
            # CPU percentage (approximate)
            cpu_time_used = (end_cpu_time.user + end_cpu_time.system) - \
                           (start_cpu_time.user + start_cpu_time.system)
            metrics.cpu_percent = (cpu_time_used / metrics.duration) * 100 if metrics.duration > 0 else 0
            
            # Store metrics
            self.metrics.append(metrics)
            
            logger.debug(f"Performance: {operation_name} took {metrics.duration:.2f}s, "
                        f"used {metrics.memory_used / 1024 / 1024:.1f}MB memory")
    
    @contextmanager
    def monitor_sync(self, operation_name: str):
        """
        Monitor synchronous operation performance.
        
        Args:
            operation_name: Name of the operation being monitored
        """
        # Similar to async version but for sync operations
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                duration=end_time - start_time,
                memory_used=end_memory - start_memory,
                peak_memory=end_memory,
                cpu_percent=0.0  # Simplified for sync
            )
            
            self.metrics.append(metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        total_duration = sum(m.duration for m in self.metrics)
        total_memory = sum(m.memory_used for m in self.metrics)
        avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
        
        return {
            'total_operations': len(self.metrics),
            'total_duration': total_duration,
            'total_memory_used': total_memory,
            'average_cpu_percent': avg_cpu,
            'operations': [
                {
                    'name': m.operation_name,
                    'duration': m.duration,
                    'memory_mb': m.memory_used / 1024 / 1024,
                    'cpu_percent': m.cpu_percent
                }
                for m in self.metrics
            ]
        }
    
    def clear(self):
        """Clear collected metrics."""
        self.metrics.clear()


class MemoryOptimizer:
    """Optimizes memory usage during downloads."""
    
    def __init__(self, max_memory_mb: int = 500):
        """
        Initialize memory optimizer.
        
        Args:
            max_memory_mb: Maximum memory usage in MB before optimization
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.process = psutil.Process()
        
    def check_memory_usage(self) -> bool:
        """
        Check if memory usage is within limits.
        
        Returns:
            True if memory usage is acceptable, False if optimization needed
        """
        current_memory = self.process.memory_info().rss
        return current_memory < self.max_memory_bytes
    
    def optimize_memory(self):
        """Perform memory optimization."""
        # Force garbage collection
        gc.collect()
        
        # Log memory usage
        memory_info = self.process.memory_info()
        logger.debug(f"Memory optimization: RSS={memory_info.rss / 1024 / 1024:.1f}MB, "
                    f"VMS={memory_info.vms / 1024 / 1024:.1f}MB")
    
    @contextmanager
    def memory_limit(self):
        """Context manager that enforces memory limits."""
        try:
            yield
        finally:
            if not self.check_memory_usage():
                logger.warning("Memory usage high, performing optimization")
                self.optimize_memory()


class ChunkSizeOptimizer:
    """Optimizes chunk sizes for downloads based on performance."""
    
    def __init__(self):
        """Initialize chunk size optimizer."""
        self.performance_history: Dict[int, List[float]] = {}
        self.current_chunk_size = 8192  # Start with 8KB
        self.min_chunk_size = 1024  # 1KB
        self.max_chunk_size = 1024 * 1024  # 1MB
        
    def get_optimal_chunk_size(self, bandwidth: Optional[float] = None) -> int:
        """
        Get optimal chunk size based on performance history and bandwidth.
        
        Args:
            bandwidth: Available bandwidth in bytes/second
            
        Returns:
            Optimal chunk size in bytes
        """
        if bandwidth:
            # Calculate chunk size based on bandwidth
            # Aim for chunks that take about 0.1 seconds to download
            target_time = 0.1
            calculated_size = int(bandwidth * target_time)
            
            # Clamp to reasonable range
            calculated_size = max(self.min_chunk_size, 
                                min(calculated_size, self.max_chunk_size))
            
            return calculated_size
        
        # Use performance history if available
        if self.performance_history:
            # Find chunk size with best average performance
            best_chunk_size = self.current_chunk_size
            best_speed = 0.0
            
            for chunk_size, speeds in self.performance_history.items():
                avg_speed = sum(speeds) / len(speeds)
                if avg_speed > best_speed:
                    best_speed = avg_speed
                    best_chunk_size = chunk_size
            
            return best_chunk_size
        
        return self.current_chunk_size
    
    def record_performance(self, chunk_size: int, speed: float):
        """
        Record performance for a chunk size.
        
        Args:
            chunk_size: Chunk size used
            speed: Download speed achieved
        """
        if chunk_size not in self.performance_history:
            self.performance_history[chunk_size] = []
        
        # Keep only recent measurements
        history = self.performance_history[chunk_size]
        history.append(speed)
        if len(history) > 10:
            history.pop(0)
    
    def adapt_chunk_size(self, current_speed: float) -> int:
        """
        Adapt chunk size based on current performance.
        
        Args:
            current_speed: Current download speed
            
        Returns:
            New chunk size to try
        """
        # Record current performance
        self.record_performance(self.current_chunk_size, current_speed)
        
        # Try different chunk sizes occasionally
        if len(self.performance_history.get(self.current_chunk_size, [])) >= 5:
            # Try larger chunk size if current is working well
            if current_speed > 1024 * 1024:  # > 1MB/s
                new_size = min(self.current_chunk_size * 2, self.max_chunk_size)
                if new_size != self.current_chunk_size:
                    self.current_chunk_size = new_size
                    return new_size
        
        return self.current_chunk_size


def performance_benchmark(func):
    """Decorator to benchmark function performance."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        async with monitor.monitor_async(func.__name__) as metrics:
            result = await func(*args, **kwargs)
        
        logger.info(f"Benchmark {func.__name__}: {metrics.duration:.2f}s, "
                   f"{metrics.memory_used / 1024 / 1024:.1f}MB")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        with monitor.monitor_sync(func.__name__):
            result = func(*args, **kwargs)
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class DownloadOptimizer:
    """Optimizes download performance."""
    
    def __init__(self):
        """Initialize download optimizer."""
        self.chunk_optimizer = ChunkSizeOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.performance_monitor = PerformanceMonitor()
        
    async def optimize_download_session(
        self, 
        session, 
        url: str, 
        file_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimize download session parameters.
        
        Args:
            session: aiohttp session
            url: Download URL
            file_size: File size if known
            
        Returns:
            Optimization parameters
        """
        # Test connection speed
        test_start = time.time()
        async with session.head(url) as response:
            response.raise_for_status()
        test_duration = time.time() - test_start
        
        # Estimate bandwidth
        if test_duration > 0:
            # This is a rough estimate based on connection time
            estimated_bandwidth = 1024 * 1024 / test_duration  # Very rough estimate
        else:
            estimated_bandwidth = 1024 * 1024  # 1MB/s default
        
        # Get optimal chunk size
        chunk_size = self.chunk_optimizer.get_optimal_chunk_size(estimated_bandwidth)
        
        # Calculate optimal number of connections
        if file_size and file_size > 10 * 1024 * 1024:  # > 10MB
            max_connections = min(4, max(1, file_size // (5 * 1024 * 1024)))
        else:
            max_connections = 1
        
        return {
            'chunk_size': chunk_size,
            'max_connections': max_connections,
            'estimated_bandwidth': estimated_bandwidth
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'performance_summary': self.performance_monitor.get_summary(),
            'memory_status': {
                'current_rss_mb': self.memory_optimizer.process.memory_info().rss / 1024 / 1024,
                'memory_limit_mb': self.memory_optimizer.max_memory_bytes / 1024 / 1024,
                'within_limits': self.memory_optimizer.check_memory_usage()
            },
            'chunk_optimization': {
                'current_chunk_size': self.chunk_optimizer.current_chunk_size,
                'performance_history': {
                    str(k): v for k, v in self.chunk_optimizer.performance_history.items()
                }
            }
        }


# Global optimizer instance
_global_optimizer: Optional[DownloadOptimizer] = None


def get_global_optimizer() -> DownloadOptimizer:
    """Get global download optimizer instance."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = DownloadOptimizer()
    return _global_optimizer
