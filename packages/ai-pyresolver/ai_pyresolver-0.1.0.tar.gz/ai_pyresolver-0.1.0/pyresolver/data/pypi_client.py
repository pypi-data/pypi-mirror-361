"""
PyPI client for fetching real package metadata and versions.

This module provides a robust client for interacting with the PyPI API
to fetch package information, versions, and dependencies.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from urllib.parse import urljoin, quote
import urllib.request
import urllib.error
import hashlib

from ..core.models import Package, Version, PackageVersion, Dependency

logger = logging.getLogger(__name__)


@dataclass
class PyPIConfig:
    """Configuration for PyPI client."""

    base_url: str = "https://pypi.org/pypi/"
    timeout: int = 30
    max_retries: int = 3
    cache_dir: Optional[Path] = None
    cache_ttl_hours: int = 24
    user_agent: str = "PyResolver/0.1.0"

    def __post_init__(self):
        if self.cache_dir is None:
            self.cache_dir = Path.home() / ".pyresolver" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class PackageInfo:
    """Raw package information from PyPI."""

    name: str
    summary: str
    description: str
    home_page: str
    author: str
    author_email: str
    license: str
    keywords: List[str]
    classifiers: List[str]
    requires_dist: List[str]
    requires_python: Optional[str]
    project_urls: Dict[str, str]

    @classmethod
    def from_pypi_json(cls, data: Dict[str, Any]) -> PackageInfo:
        """Create PackageInfo from PyPI JSON response."""
        info = data.get("info", {})

        return cls(
            name=info.get("name", ""),
            summary=info.get("summary", ""),
            description=info.get("description", ""),
            home_page=info.get("home_page", ""),
            author=info.get("author", ""),
            author_email=info.get("author_email", ""),
            license=info.get("license", ""),
            keywords=info.get("keywords", "").split() if info.get("keywords") else [],
            classifiers=info.get("classifiers", []),
            requires_dist=info.get("requires_dist") or [],
            requires_python=info.get("requires_python"),
            project_urls=info.get("project_urls") or {},
        )


class PyPIClient:
    """
    Client for fetching package information from PyPI.

    This client handles caching, rate limiting, and error recovery
    when fetching package metadata from the Python Package Index.
    """

    def __init__(self, config: Optional[PyPIConfig] = None):
        """Initialize the PyPI client."""
        self.config = config or PyPIConfig()
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._request_times: List[float] = []

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """
        Get package information from PyPI.

        Args:
            package_name: Name of the package to fetch

        Returns:
            PackageInfo object or None if package not found
        """
        # Check cache first
        cache_key = f"info:{package_name.lower()}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch from PyPI
        url = urljoin(self.config.base_url, f"{quote(package_name)}/json")

        try:
            data = self._make_request(url)
            if data:
                package_info = PackageInfo.from_pypi_json(data)
                self._store_in_cache(cache_key, package_info)
                return package_info
        except Exception as e:
            logger.error(f"Failed to fetch package info for {package_name}: {e}")

        return None

    def get_package_versions(self, package_name: str) -> List[PackageVersion]:
        """
        Get all available versions for a package.

        Args:
            package_name: Name of the package

        Returns:
            List of PackageVersion objects
        """
        # Check cache first
        cache_key = f"versions:{package_name.lower()}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch package info
        package_info = self.get_package_info(package_name)
        if not package_info:
            return []

        # Get detailed version information
        url = urljoin(self.config.base_url, f"{quote(package_name)}/json")

        try:
            data = self._make_request(url)
            if not data:
                return []

            package = Package(
                name=package_info.name,
                description=package_info.summary,
                homepage=package_info.home_page,
                license=package_info.license,
                keywords=package_info.keywords
            )

            versions = []
            releases = data.get("releases", {})

            for version_str, release_files in releases.items():
                if not release_files:  # Skip versions with no files
                    continue

                try:
                    version = Version(version_str)

                    # Parse dependencies from the first wheel or source dist
                    dependencies = self._parse_dependencies(
                        package_info.requires_dist,
                        package_info.requires_python
                    )

                    package_version = PackageVersion(
                        package=package,
                        version=version,
                        dependencies=dependencies,
                        requires_python=package_info.requires_python,
                        upload_time=release_files[0].get("upload_time") if release_files else None,
                        size=release_files[0].get("size") if release_files else None
                    )

                    versions.append(package_version)

                except Exception as e:
                    logger.warning(f"Skipping invalid version {version_str} for {package_name}: {e}")
                    continue

            # Sort versions (newest first)
            versions.sort(key=lambda pv: pv.version.version, reverse=True)

            self._store_in_cache(cache_key, versions)
            return versions

        except Exception as e:
            logger.error(f"Failed to fetch versions for {package_name}: {e}")
            return []

    def _parse_dependencies(self, requires_dist: List[str], requires_python: Optional[str]) -> List[Dependency]:
        """Parse dependency strings into Dependency objects."""
        dependencies = []

        for req_str in requires_dist or []:
            try:
                # Simple parsing for now - will enhance with proper PEP 508 parsing
                req_str = req_str.strip()
                if not req_str:
                    continue

                # Extract package name and version spec
                # Handle cases like: "requests>=2.25.0", "django>=3.2,<5.0"
                parts = req_str.split(";", 1)  # Split on environment markers
                main_part = parts[0].strip()
                markers = parts[1].strip() if len(parts) > 1 else None

                # Extract package name
                import re
                match = re.match(r"([a-zA-Z0-9_-]+)", main_part)
                if not match:
                    continue

                package_name = match.group(1)
                version_spec = main_part[len(package_name):].strip()

                if not version_spec:
                    version_spec = ""

                package = Package(name=package_name)
                dependency = Dependency(
                    package=package,
                    version_spec=version_spec,
                    markers=markers
                )

                dependencies.append(dependency)

            except Exception as e:
                logger.warning(f"Failed to parse dependency: {req_str}: {e}")
                continue

        return dependencies

    def _make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """Make HTTP request to PyPI with retries and rate limiting."""
        # Rate limiting: max 10 requests per second
        current_time = time.time()
        self._request_times = [t for t in self._request_times if current_time - t < 1.0]

        if len(self._request_times) >= 10:
            sleep_time = 1.0 - (current_time - self._request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self._request_times.append(current_time)

        # Make request with retries
        for attempt in range(self.config.max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': self.config.user_agent}
                )

                with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        return data
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    logger.info(f"Package not found: {url}")
                    return None
                logger.warning(f"HTTP error {e.code} for {url} (attempt {attempt + 1})")

            except Exception as e:
                logger.warning(f"Request failed for {url} (attempt {attempt + 1}): {e}")

            if attempt < self.config.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from memory cache."""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.config.cache_ttl_hours * 3600:
                return data
            else:
                del self._cache[key]

        # Try disk cache
        return self._get_from_disk_cache(key)

    def _store_in_cache(self, key: str, data: Any) -> None:
        """Store data in memory and disk cache."""
        timestamp = time.time()
        self._cache[key] = (timestamp, data)
        self._store_in_disk_cache(key, data, timestamp)

    def _get_from_disk_cache(self, key: str) -> Optional[Any]:
        """Get data from disk cache."""
        # Disable disk cache for now to avoid serialization issues
        # In a full implementation, this would properly serialize/deserialize objects
        return None

    def _store_in_disk_cache(self, key: str, data: Any, timestamp: float) -> None:
        """Store data in disk cache."""
        # Disable disk cache for now to avoid serialization issues
        # In a full implementation, this would properly serialize objects
        pass

    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif hasattr(data, '__dict__'):
            # Convert dataclass or object to dict
            return self._make_serializable(data.__dict__)
        else:
            # Fallback to string representation
            return str(data)

    def _deserialize_cache_data(self, data: Any) -> Any:
        """Convert cached data back to proper objects."""
        # For now, just return the data as-is
        # In a full implementation, this would reconstruct the proper objects
        return data

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

        # Clear disk cache
        try:
            for cache_file in self.config.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to clear disk cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        memory_entries = len(self._cache)
        disk_entries = len(list(self.config.cache_dir.glob("*.json")))

        return {
            'memory_entries': memory_entries,
            'disk_entries': disk_entries,
            'cache_dir': str(self.config.cache_dir),
            'ttl_hours': self.config.cache_ttl_hours
        }