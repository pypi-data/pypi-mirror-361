"""
Main PyResolver class for intelligent dependency resolution.

This module implements the core dependency resolution algorithm that combines
traditional constraint satisfaction with AI-powered decision making.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .models import (
    Package, Version, Dependency, PackageVersion, Resolution,
    Conflict, ConflictType, ResolutionStrategy
)
from ..data.pypi_client import PyPIClient, PyPIConfig


@dataclass
class ResolverConfig:
    """Configuration for the dependency resolver."""

    strategy: ResolutionStrategy = ResolutionStrategy.AI_OPTIMIZED
    max_backtrack_depth: int = 100
    timeout_seconds: int = 300
    use_ai_predictions: bool = True
    prefer_stable_versions: bool = True
    allow_prereleases: bool = False
    platform_tags: List[str] = None
    python_version: str = "3.9"
    use_real_pypi: bool = True
    pypi_config: Optional[PyPIConfig] = None

    def __post_init__(self):
        if self.platform_tags is None:
            self.platform_tags = ["any"]


class PyResolver:
    """
    AI-powered Python dependency resolver.

    This class implements an intelligent dependency resolution algorithm that
    combines traditional constraint satisfaction techniques with machine learning
    to resolve complex dependency conflicts.
    """

    def __init__(self, config: Optional[ResolverConfig] = None):
        """Initialize the resolver with configuration."""
        self.config = config or ResolverConfig()
        self._package_cache: Dict[str, List[PackageVersion]] = {}
        self._resolution_cache: Dict[str, Resolution] = {}
        self._ai_predictor = None  # Will be initialized when needed

        # Initialize PyPI client if using real PyPI
        if self.config.use_real_pypi:
            pypi_config = self.config.pypi_config or PyPIConfig()
            self._pypi_client = PyPIClient(pypi_config)
        else:
            self._pypi_client = None

    def resolve(self, requirements: List[str]) -> Resolution:
        """
        Resolve a list of package requirements.

        Args:
            requirements: List of requirement strings (e.g., ["django>=4.0", "celery"])

        Returns:
            Resolution object containing resolved packages or conflicts
        """
        start_time = time.time()

        try:
            # Parse requirements into Dependency objects
            dependencies = self._parse_requirements(requirements)

            # Create initial resolution state
            resolution = Resolution(strategy=self.config.strategy)

            # Perform the actual resolution
            self._resolve_dependencies(dependencies, resolution)

            # Calculate resolution time
            resolution.resolution_time = time.time() - start_time

            return resolution

        except Exception as e:
            # Create a failed resolution with error information
            resolution = Resolution(strategy=self.config.strategy)
            conflict = Conflict(
                type=ConflictType.MISSING_DEPENDENCY,
                packages=[],
                description=f"Resolution failed: {str(e)}",
                root_cause=str(e)
            )
            resolution.conflicts.append(conflict)
            resolution.resolution_time = time.time() - start_time
            return resolution

    def _parse_requirements(self, requirements: List[str]) -> List[Dependency]:
        """Parse requirement strings into Dependency objects using PEP 508."""
        dependencies = []

        for req_str in requirements:
            req_str = req_str.strip()
            if not req_str or req_str.startswith("#"):
                continue

            try:
                # Use the new PEP 508 parsing method
                dependency = Dependency.from_requirement_string(req_str)
                dependencies.append(dependency)
            except Exception as e:
                logger.warning(f"Failed to parse requirement '{req_str}': {e}")
                continue

        return dependencies

    def _resolve_dependencies(self, dependencies: List[Dependency], resolution: Resolution) -> None:
        """
        Core dependency resolution algorithm.

        This method implements a simplified version of the PubGrub algorithm
        with AI-enhanced decision making.
        """
        # Queue of dependencies to resolve
        dependency_queue = dependencies.copy()
        resolved_names: Set[str] = set()

        while dependency_queue:
            current_dep = dependency_queue.pop(0)
            package_name = current_dep.package.name

            # Skip if already resolved
            if package_name in resolved_names:
                continue

            # Find compatible version for this dependency
            compatible_version = self._find_compatible_version(current_dep, resolution)

            if compatible_version is None:
                # Create conflict
                conflict = Conflict(
                    type=ConflictType.VERSION_CONFLICT,
                    packages=[],
                    description=f"No compatible version found for {package_name}",
                    root_cause=f"Version constraint {current_dep.version_spec} cannot be satisfied"
                )
                resolution.conflicts.append(conflict)
                continue

            # Add to resolution
            resolution.add_package(compatible_version)
            resolved_names.add(package_name)

            # Add transitive dependencies to queue
            for dep in compatible_version.dependencies:
                if dep.package.name not in resolved_names:
                    dependency_queue.append(dep)

    def _find_compatible_version(self, dependency: Dependency, resolution: Resolution) -> Optional[PackageVersion]:
        """
        Find a compatible version for a dependency.

        This method uses AI predictions when available to choose the best version.
        """
        package_name = dependency.package.name

        # Get available versions (mock implementation)
        available_versions = self._get_available_versions(package_name)

        # Filter versions that match the dependency constraint
        compatible_versions = [
            pv for pv in available_versions
            if dependency.matches_version(pv.version)
        ]

        if not compatible_versions:
            return None

        # Use AI to rank versions if available
        if self.config.use_ai_predictions and self._ai_predictor:
            return self._ai_predictor.select_best_version(
                compatible_versions, resolution.resolved_packages
            )

        # Fallback to simple heuristics
        if self.config.strategy == ResolutionStrategy.CONSERVATIVE:
            return min(compatible_versions, key=lambda pv: pv.version.version)
        else:
            return max(compatible_versions, key=lambda pv: pv.version.version)

    def _get_available_versions(self, package_name: str) -> List[PackageVersion]:
        """
        Get available versions for a package from PyPI or cache.
        """
        if package_name in self._package_cache:
            return self._package_cache[package_name]

        package_versions = []

        if self._pypi_client:
            # Use real PyPI data
            try:
                package_versions = self._pypi_client.get_package_versions(package_name)
                logger.info(f"Fetched {len(package_versions)} versions for {package_name} from PyPI")
            except Exception as e:
                logger.error(f"Failed to fetch versions for {package_name} from PyPI: {e}")
                # Fall back to mock data
                package_versions = self._get_mock_versions(package_name)
        else:
            # Use mock data
            package_versions = self._get_mock_versions(package_name)

        # Filter versions based on configuration
        if not self.config.allow_prereleases:
            package_versions = [pv for pv in package_versions if not pv.version.is_prerelease]

        self._package_cache[package_name] = package_versions
        return package_versions

    def _get_mock_versions(self, package_name: str) -> List[PackageVersion]:
        """Get mock versions for testing when PyPI is not available."""
        mock_versions = {
            "django": ["3.2.0", "4.0.0", "4.1.0", "4.2.0", "5.0.0a1"],
            "celery": ["5.0.0", "5.1.0", "5.2.0", "5.3.0"],
            "requests": ["2.25.0", "2.26.0", "2.27.0", "2.28.0", "2.29.0"],
            "numpy": ["1.20.0", "1.21.0", "1.22.0", "1.23.0", "1.24.0"],
            "flask": ["2.0.0", "2.1.0", "2.2.0", "2.3.0"],
            "fastapi": ["0.95.0", "0.96.0", "0.97.0", "0.98.0"],
        }

        versions = mock_versions.get(package_name, ["1.0.0", "1.1.0", "1.2.0"])

        package = Package(name=package_name)
        package_versions = [
            PackageVersion(package=package, version=Version(v))
            for v in versions
        ]

        return package_versions

    def explain_conflict(self, conflict: Conflict) -> str:
        """
        Provide a detailed explanation of a dependency conflict.

        This method analyzes the conflict and provides human-readable
        explanations and potential solutions.
        """
        explanation = f"Conflict Type: {conflict.type.value}\n"
        explanation += f"Description: {conflict.description}\n"

        if conflict.root_cause:
            explanation += f"Root Cause: {conflict.root_cause}\n"

        if conflict.suggested_solutions:
            explanation += "Suggested Solutions:\n"
            for i, solution in enumerate(conflict.suggested_solutions, 1):
                explanation += f"  {i}. {solution}\n"

        return explanation