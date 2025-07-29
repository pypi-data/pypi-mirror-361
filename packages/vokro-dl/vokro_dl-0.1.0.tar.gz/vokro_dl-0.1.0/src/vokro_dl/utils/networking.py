"""
Network utilities for VokroDL.

This module provides networking functionality including session management,
bandwidth detection, and connection pooling.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from ..core.config import NetworkConfig
from ..core.exceptions import NetworkError


logger = logging.getLogger(__name__)


class NetworkManager:
    """Manages network connections and sessions."""
    
    def __init__(self, config: NetworkConfig):
        """
        Initialize network manager.
        
        Args:
            config: Network configuration
        """
        self.config = config
        self._session: Optional[ClientSession] = None
        self._connector: Optional[TCPConnector] = None
        self._bandwidth_cache: Dict[str, float] = {}
    
    async def get_session(self) -> ClientSession:
        """
        Get or create aiohttp session.
        
        Returns:
            Configured aiohttp session
        """
        if self._session is None or self._session.closed:
            await self._create_session()
        
        return self._session
    
    async def _create_session(self):
        """Create new aiohttp session with configuration."""
        # Create connector with connection pooling
        self._connector = TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=min(self.config.max_connections, 10),
            ttl_dns_cache=300,  # 5 minutes DNS cache
            use_dns_cache=True,
            ssl=self.config.verify_ssl,
        )
        
        # Create timeout configuration
        timeout = ClientTimeout(
            total=self.config.timeout,
            connect=min(self.config.timeout, 10),
            sock_read=self.config.timeout
        )
        
        # Prepare headers
        headers = {
            'User-Agent': self.config.user_agent,
            **self.config.headers
        }
        
        # Create session
        self._session = ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers=headers,
            trust_env=True,  # Use environment proxy settings
        )
        
        logger.debug("Created new aiohttp session")
    
    async def close(self):
        """Close session and connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        
        if self._connector:
            await self._connector.close()
        
        logger.debug("Closed network manager")
    
    async def test_connection(self, url: str) -> bool:
        """
        Test if a URL is reachable.
        
        Args:
            url: URL to test
            
        Returns:
            True if reachable, False otherwise
        """
        try:
            session = await self.get_session()
            async with session.head(url) as response:
                return response.status < 400
        except Exception as e:
            logger.debug(f"Connection test failed for {url}: {e}")
            return False
    
    async def get_content_length(self, url: str) -> Optional[int]:
        """
        Get content length for a URL without downloading.
        
        Args:
            url: URL to check
            
        Returns:
            Content length in bytes, or None if unknown
        """
        try:
            session = await self.get_session()
            async with session.head(url) as response:
                content_length = response.headers.get('content-length')
                if content_length:
                    return int(content_length)
        except Exception as e:
            logger.debug(f"Failed to get content length for {url}: {e}")
        
        return None
    
    async def measure_bandwidth(self, test_url: Optional[str] = None) -> float:
        """
        Measure available bandwidth.
        
        Args:
            test_url: URL to use for bandwidth test. If None, uses default.
            
        Returns:
            Bandwidth in bytes per second
        """
        if not test_url:
            # Use a small file from a reliable CDN for testing
            test_url = "https://httpbin.org/bytes/1024"
        
        # Check cache first
        cache_key = urlparse(test_url).netloc
        if cache_key in self._bandwidth_cache:
            cached_time, cached_bandwidth = self._bandwidth_cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minutes cache
                return cached_bandwidth
        
        try:
            session = await self.get_session()
            start_time = time.time()
            
            async with session.get(test_url) as response:
                response.raise_for_status()
                
                total_bytes = 0
                async for chunk in response.content.iter_chunked(8192):
                    total_bytes += len(chunk)
                
                elapsed_time = time.time() - start_time
                
                if elapsed_time > 0:
                    bandwidth = total_bytes / elapsed_time
                    
                    # Cache result
                    self._bandwidth_cache[cache_key] = (time.time(), bandwidth)
                    
                    logger.debug(f"Measured bandwidth: {bandwidth / 1024 / 1024:.2f} MB/s")
                    return bandwidth
        
        except Exception as e:
            logger.warning(f"Bandwidth measurement failed: {e}")
        
        # Return default bandwidth estimate (1 MB/s)
        return 1024 * 1024
    
    async def get_optimal_chunk_size(self, url: str) -> int:
        """
        Determine optimal chunk size for downloading from URL.
        
        Args:
            url: URL to download from
            
        Returns:
            Optimal chunk size in bytes
        """
        # Measure bandwidth
        bandwidth = await self.measure_bandwidth()
        
        # Calculate chunk size based on bandwidth
        # Aim for chunks that take about 0.1 seconds to download
        target_time = 0.1
        chunk_size = int(bandwidth * target_time)
        
        # Clamp to reasonable range
        min_chunk = 8192  # 8KB
        max_chunk = 1024 * 1024  # 1MB
        
        chunk_size = max(min_chunk, min(chunk_size, max_chunk))
        
        logger.debug(f"Optimal chunk size for {url}: {chunk_size} bytes")
        return chunk_size
    
    def get_proxy_config(self) -> Optional[str]:
        """
        Get proxy configuration.
        
        Returns:
            Proxy URL or None
        """
        return self.config.proxy


class BandwidthLimiter:
    """Rate limiter for bandwidth control."""
    
    def __init__(self, max_bytes_per_second: float):
        """
        Initialize bandwidth limiter.
        
        Args:
            max_bytes_per_second: Maximum bytes per second
        """
        self.max_bytes_per_second = max_bytes_per_second
        self.last_update = time.time()
        self.allowance = max_bytes_per_second
    
    async def consume(self, bytes_count: int) -> None:
        """
        Consume bandwidth allowance, sleeping if necessary.
        
        Args:
            bytes_count: Number of bytes to consume
        """
        current_time = time.time()
        time_passed = current_time - self.last_update
        self.last_update = current_time
        
        # Add allowance based on time passed
        self.allowance += time_passed * self.max_bytes_per_second
        
        # Cap allowance to prevent burst
        self.allowance = min(self.allowance, self.max_bytes_per_second)
        
        # Check if we need to wait
        if bytes_count > self.allowance:
            sleep_time = (bytes_count - self.allowance) / self.max_bytes_per_second
            await asyncio.sleep(sleep_time)
            self.allowance = 0
        else:
            self.allowance -= bytes_count


class ConnectionPool:
    """Manages connection pooling for different hosts."""
    
    def __init__(self, max_connections_per_host: int = 10):
        """
        Initialize connection pool.
        
        Args:
            max_connections_per_host: Maximum connections per host
        """
        self.max_connections_per_host = max_connections_per_host
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
    
    def get_semaphore(self, host: str) -> asyncio.Semaphore:
        """
        Get semaphore for host to limit concurrent connections.
        
        Args:
            host: Hostname
            
        Returns:
            Semaphore for the host
        """
        if host not in self._semaphores:
            self._semaphores[host] = asyncio.Semaphore(self.max_connections_per_host)
        
        return self._semaphores[host]
    
    async def acquire(self, url: str):
        """
        Acquire connection for URL.
        
        Args:
            url: URL to connect to
            
        Returns:
            Async context manager for the connection
        """
        parsed = urlparse(url)
        host = parsed.netloc
        semaphore = self.get_semaphore(host)
        
        return semaphore
