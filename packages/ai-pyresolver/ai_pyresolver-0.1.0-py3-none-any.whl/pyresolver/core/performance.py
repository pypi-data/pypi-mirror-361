"""
Performance optimization utilities for PyResolver.

This module provides caching, parallel processing, and memory optimization
features to handle large dependency graphs efficiently.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PerformanceMetrics:
    """Track performance metrics for resolution operations."""

    total_packages_processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    network_requests: int = 0
    resolution_time: float = 0.0
    memory_peak_mb: float = 0.0
    parallel_tasks: int = 0

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as a percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            'total_packages_processed': self.total_packages_processed,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'network_requests': self.network_requests,
            'resolution_time': self.resolution_time,
            'memory_peak_mb': self.memory_peak_mb,
            'parallel_tasks': self.parallel_tasks,
            'cache_hit_rate': self.cache_hit_rate,
        }


class MemoryEfficientCache:
    """
    Memory-efficient cache with LRU eviction and size limits.

    This cache automatically manages memory usage by evicting least recently
    used items when memory limits are reached.
    """

    def __init__(self, max_size: int = 1000, max_memory_mb: float = 100.0):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of items to cache
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        with self._lock:
            if key in self._cache:
                self._access_times[key] = time.time()
                return self._cache[key]
            return None

    def put(self, key: str, value: Any) -> None:
        """Put an item in the cache."""
        with self._lock:
            # Check if we need to evict items
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            self._cache[key] = value
            self._access_times[key] = time.time()

    def _evict_lru(self) -> None:
        """Evict least recently used items."""
        if not self._access_times:
            return

        # Find the least recently used key
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])

        # Remove from cache
        del self._cache[lru_key]
        del self._access_times[lru_key]

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

    def size(self) -> int:
        """Get the number of cached items."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'max_memory_mb': self.max_memory_mb,
        }


class ParallelPackageFetcher:
    """
    Parallel package metadata fetcher for improved performance.

    This class fetches package information from multiple sources concurrently
    to reduce overall resolution time.
    """

    def __init__(self, max_workers: int = 10, timeout: float = 30.0):
        """
        Initialize the parallel fetcher.

        Args:
            max_workers: Maximum number of concurrent workers
            timeout: Timeout for individual fetch operations
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def fetch_packages_parallel(
        self,
        package_names: List[str],
        fetch_func: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """
        Fetch package information for multiple packages in parallel.

        Args:
            package_names: List of package names to fetch
            fetch_func: Function to fetch a single package

        Returns:
            Dictionary mapping package names to their information
        """
        results = {}

        # Submit all tasks
        future_to_package = {
            self._executor.submit(fetch_func, pkg_name): pkg_name
            for pkg_name in package_names
        }

        # Collect results as they complete
        for future in as_completed(future_to_package, timeout=self.timeout):
            package_name = future_to_package[future]
            try:
                result = future.result()
                if result is not None:
                    results[package_name] = result
            except Exception as e:
                logger.warning(f"Failed to fetch {package_name}: {e}")

        return results

    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self._executor.shutdown(wait=True)


def timed_operation(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure operation execution time.

    Args:
        func: Function to time

    Returns:
        Wrapped function that logs execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise

    return wrapper