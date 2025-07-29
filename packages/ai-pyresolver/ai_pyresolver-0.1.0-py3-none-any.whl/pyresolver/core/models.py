"""
Core data models for PyResolver.

This module defines the fundamental data structures used throughout the
dependency resolution process.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any

# Import proper packaging libraries for production use
try:
    from packaging.version import Version as PackagingVersion, InvalidVersion
    from packaging.specifiers import SpecifierSet, InvalidSpecifier
    from packaging.requirements import Requirement, InvalidRequirement
    from packaging.markers import Marker, InvalidMarker
    PACKAGING_AVAILABLE = True
except ImportError:
    # Fallback for environments without packaging library
    PACKAGING_AVAILABLE = False
    PackagingVersion = Any
    SpecifierSet = Any
    Requirement = Any
    Marker = Any


class ConflictType(Enum):
    """Types of dependency conflicts."""
    VERSION_CONFLICT = "version_conflict"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    PLATFORM_INCOMPATIBLE = "platform_incompatible"
    PYTHON_VERSION_INCOMPATIBLE = "python_version_incompatible"


class ResolutionStrategy(Enum):
    """Strategies for dependency resolution."""
    CONSERVATIVE = "conservative"  # Prefer older, stable versions
    AGGRESSIVE = "aggressive"      # Prefer newer versions
    AI_OPTIMIZED = "ai_optimized"  # Use AI predictions
    BALANCED = "balanced"          # Balance between stability and features


@dataclass(frozen=True)
class Version:
    """Represents a package version with PEP 440 compliance."""

    version: str
    _parsed: Optional[Any] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Validate and parse the version string."""
        if not self.version or not isinstance(self.version, str):
            raise ValueError(f"Invalid version format: {self.version}")

        if PACKAGING_AVAILABLE:
            try:
                parsed = PackagingVersion(self.version)
                object.__setattr__(self, '_parsed', parsed)
            except InvalidVersion as e:
                raise ValueError(f"Invalid version format: {self.version}") from e
        else:
            # Basic validation fallback
            if not re.match(r'^[0-9]+(\.[0-9]+)*', self.version):
                raise ValueError(f"Invalid version format: {self.version}")

    @property
    def parsed(self) -> Optional[Any]:
        """Get the parsed version object if packaging is available."""
        return self._parsed

    @property
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version."""
        if self._parsed:
            return self._parsed.is_prerelease
        # Fallback heuristic
        return any(marker in self.version.lower() for marker in ['a', 'b', 'rc', 'dev'])

    @property
    def major(self) -> int:
        """Get the major version number."""
        if self._parsed:
            return self._parsed.major
        # Fallback
        return int(self.version.split('.')[0])

    @property
    def minor(self) -> Optional[int]:
        """Get the minor version number."""
        if self._parsed:
            return self._parsed.minor
        # Fallback
        parts = self.version.split('.')
        return int(parts[1]) if len(parts) > 1 else None

    @property
    def micro(self) -> Optional[int]:
        """Get the micro version number."""
        if self._parsed:
            return self._parsed.micro
        # Fallback
        parts = self.version.split('.')
        return int(parts[2]) if len(parts) > 2 else None

    def __str__(self) -> str:
        return self.version

    def __lt__(self, other: Version) -> bool:
        if self._parsed and other._parsed:
            return self._parsed < other._parsed
        # Fallback string comparison
        return self.version < other.version

    def __le__(self, other: Version) -> bool:
        if self._parsed and other._parsed:
            return self._parsed <= other._parsed
        return self.version <= other.version

    def __gt__(self, other: Version) -> bool:
        if self._parsed and other._parsed:
            return self._parsed > other._parsed
        return self.version > other.version

    def __ge__(self, other: Version) -> bool:
        if self._parsed and other._parsed:
            return self._parsed >= other._parsed
        return self.version >= other.version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False
        if self._parsed and other._parsed:
            return self._parsed == other._parsed
        return self.version == other.version


@dataclass(frozen=True)
class Package:
    """Represents a Python package."""

    name: str
    description: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Normalize package name
        object.__setattr__(self, 'name', self.name.lower().replace('_', '-'))

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Dependency:
    """Represents a dependency relationship between packages with PEP 508 compliance."""

    package: Package
    version_spec: str
    extras: Set[str] = field(default_factory=set)
    markers: Optional[str] = None
    optional: bool = False
    _specifier: Optional[Any] = field(default=None, init=False, repr=False)
    _marker: Optional[Any] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Parse version specifier and markers."""
        if PACKAGING_AVAILABLE and self.version_spec:
            try:
                specifier = SpecifierSet(self.version_spec)
                object.__setattr__(self, '_specifier', specifier)
            except InvalidSpecifier:
                # Keep the original string for fallback
                pass

        if PACKAGING_AVAILABLE and self.markers:
            try:
                marker = Marker(self.markers)
                object.__setattr__(self, '_marker', marker)
            except InvalidMarker:
                # Keep the original string for fallback
                pass

    @classmethod
    def from_requirement_string(cls, req_string: str) -> Dependency:
        """
        Create a Dependency from a PEP 508 requirement string.

        Args:
            req_string: A requirement string like "django>=4.0; python_version>='3.8'"

        Returns:
            Dependency object
        """
        if PACKAGING_AVAILABLE:
            try:
                req = Requirement(req_string)
                package = Package(name=req.name)

                return cls(
                    package=package,
                    version_spec=str(req.specifier) if req.specifier else "",
                    extras=set(req.extras) if req.extras else set(),
                    markers=str(req.marker) if req.marker else None
                )
            except InvalidRequirement:
                # Fall back to simple parsing
                pass

        # Fallback parsing
        parts = req_string.split(";", 1)
        main_part = parts[0].strip()
        markers = parts[1].strip() if len(parts) > 1 else None

        # Extract package name and version spec
        import re
        match = re.match(r"([a-zA-Z0-9_-]+)(.*)$", main_part)
        if match:
            package_name = match.group(1)
            version_spec = match.group(2).strip()
        else:
            package_name = main_part
            version_spec = ""

        package = Package(name=package_name)
        return cls(
            package=package,
            version_spec=version_spec,
            markers=markers
        )

    @property
    def specifier(self) -> Optional[Any]:
        """Get the parsed version specifier if available."""
        return self._specifier

    @property
    def marker(self) -> Optional[Any]:
        """Get the parsed environment marker if available."""
        return self._marker

    def matches_version(self, version: Version) -> bool:
        """Check if a version satisfies this dependency."""
        if not self.version_spec:
            return True

        if self._specifier and version.parsed:
            return version.parsed in self._specifier

        # Fallback implementation for basic version specs
        if self.version_spec.startswith(">="):
            min_version = self.version_spec[2:].strip()
            return version.version >= min_version
        elif self.version_spec.startswith("=="):
            exact_version = self.version_spec[2:].strip()
            return version.version == exact_version
        elif self.version_spec.startswith(">"):
            min_version = self.version_spec[1:].strip()
            return version.version > min_version
        elif self.version_spec.startswith("<="):
            max_version = self.version_spec[2:].strip()
            return version.version <= max_version
        elif self.version_spec.startswith("<"):
            max_version = self.version_spec[1:].strip()
            return version.version < max_version

        return True  # Default to accepting all versions

    def matches_environment(self, environment: Optional[Dict[str, str]] = None) -> bool:
        """Check if this dependency matches the current environment."""
        if not self.markers:
            return True

        if self._marker and PACKAGING_AVAILABLE:
            try:
                return self._marker.evaluate(environment or {})
            except Exception:
                # If evaluation fails, assume it matches
                return True

        # Fallback: assume all dependencies match if we can't parse markers
        return True

    def __str__(self) -> str:
        extras_str = f"[{','.join(sorted(self.extras))}]" if self.extras else ""
        markers_str = f"; {self.markers}" if self.markers else ""
        return f"{self.package.name}{extras_str}{self.version_spec}{markers_str}"


@dataclass
class PackageVersion:
    """Represents a specific version of a package with its metadata."""

    package: Package
    version: Version
    dependencies: List[Dependency] = field(default_factory=list)
    requires_python: Optional[str] = None
    platform_tags: List[str] = field(default_factory=list)
    upload_time: Optional[str] = None
    size: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.package.name}=={self.version}"

    def __hash__(self) -> int:
        return hash((self.package.name, self.version.version))


@dataclass
class Conflict:
    """Represents a dependency conflict."""

    type: ConflictType
    packages: List[PackageVersion]
    description: str
    root_cause: Optional[str] = None
    suggested_solutions: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        package_names = [pv.package.name for pv in self.packages]
        return f"{self.type.value}: {', '.join(package_names)} - {self.description}"


@dataclass
class Resolution:
    """Represents a complete dependency resolution."""

    resolved_packages: Dict[str, PackageVersion] = field(default_factory=dict)
    conflicts: List[Conflict] = field(default_factory=list)
    strategy: ResolutionStrategy = ResolutionStrategy.BALANCED
    resolution_time: Optional[float] = None
    ai_confidence: Optional[float] = None

    @property
    def is_successful(self) -> bool:
        """Check if the resolution was successful (no conflicts)."""
        return len(self.conflicts) == 0

    @property
    def package_count(self) -> int:
        """Get the number of resolved packages."""
        return len(self.resolved_packages)

    def get_package_version(self, package_name: str) -> Optional[PackageVersion]:
        """Get the resolved version for a package."""
        return self.resolved_packages.get(package_name.lower().replace('_', '-'))

    def add_package(self, package_version: PackageVersion) -> None:
        """Add a resolved package to the resolution."""
        self.resolved_packages[package_version.package.name] = package_version

    def __str__(self) -> str:
        status = "SUCCESS" if self.is_successful else f"FAILED ({len(self.conflicts)} conflicts)"
        return f"Resolution[{self.package_count} packages, {status}]"