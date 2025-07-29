"""
Custom exceptions for PyResolver.

This module defines specific exception types for different error conditions
that can occur during dependency resolution.
"""

from __future__ import annotations

from typing import List, Optional


class PyResolverError(Exception):
    """Base exception for all PyResolver errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class NetworkError(PyResolverError):
    """Raised when network operations fail."""

    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        details = {}
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code

        super().__init__(message, details)
        self.url = url
        self.status_code = status_code


class PackageNotFoundError(PyResolverError):
    """Raised when a package cannot be found."""

    def __init__(self, package_name: str, source: str = "PyPI"):
        message = f"Package '{package_name}' not found on {source}"
        details = {'package_name': package_name, 'source': source}
        super().__init__(message, details)
        self.package_name = package_name
        self.source = source


class VersionNotFoundError(PyResolverError):
    """Raised when a specific version of a package cannot be found."""

    def __init__(self, package_name: str, version: str, available_versions: Optional[List[str]] = None):
        message = f"Version '{version}' of package '{package_name}' not found"
        details = {
            'package_name': package_name,
            'requested_version': version,
            'available_versions': available_versions or []
        }
        super().__init__(message, details)
        self.package_name = package_name
        self.version = version
        self.available_versions = available_versions or []


class DependencyConflictError(PyResolverError):
    """Raised when dependency conflicts cannot be resolved."""

    def __init__(self, conflicting_packages: List[str], conflict_description: str):
        message = f"Dependency conflict: {conflict_description}"
        details = {
            'conflicting_packages': conflicting_packages,
            'conflict_description': conflict_description
        }
        super().__init__(message, details)
        self.conflicting_packages = conflicting_packages
        self.conflict_description = conflict_description


class CircularDependencyError(PyResolverError):
    """Raised when circular dependencies are detected."""

    def __init__(self, dependency_chain: List[str]):
        chain_str = " -> ".join(dependency_chain)
        message = f"Circular dependency detected: {chain_str}"
        details = {'dependency_chain': dependency_chain}
        super().__init__(message, details)
        self.dependency_chain = dependency_chain


class InvalidVersionSpecError(PyResolverError):
    """Raised when a version specification is invalid."""

    def __init__(self, version_spec: str, package_name: Optional[str] = None):
        message = f"Invalid version specification: '{version_spec}'"
        if package_name:
            message += f" for package '{package_name}'"

        details = {'version_spec': version_spec}
        if package_name:
            details['package_name'] = package_name

        super().__init__(message, details)
        self.version_spec = version_spec
        self.package_name = package_name


class InvalidRequirementError(PyResolverError):
    """Raised when a requirement string is invalid."""

    def __init__(self, requirement_string: str, parse_error: Optional[str] = None):
        message = f"Invalid requirement string: '{requirement_string}'"
        if parse_error:
            message += f" ({parse_error})"

        details = {
            'requirement_string': requirement_string,
            'parse_error': parse_error
        }
        super().__init__(message, details)
        self.requirement_string = requirement_string
        self.parse_error = parse_error


class ResolutionTimeoutError(PyResolverError):
    """Raised when dependency resolution times out."""

    def __init__(self, timeout_seconds: float, packages_processed: int):
        message = f"Resolution timed out after {timeout_seconds}s (processed {packages_processed} packages)"
        details = {
            'timeout_seconds': timeout_seconds,
            'packages_processed': packages_processed
        }
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds
        self.packages_processed = packages_processed


class IncompatiblePlatformError(PyResolverError):
    """Raised when packages are incompatible with the current platform."""

    def __init__(self, package_name: str, version: str, platform: str, supported_platforms: List[str]):
        message = f"Package '{package_name}=={version}' is not compatible with platform '{platform}'"
        details = {
            'package_name': package_name,
            'version': version,
            'platform': platform,
            'supported_platforms': supported_platforms
        }
        super().__init__(message, details)
        self.package_name = package_name
        self.version = version
        self.platform = platform
        self.supported_platforms = supported_platforms


class IncompatiblePythonVersionError(PyResolverError):
    """Raised when packages require a different Python version."""

    def __init__(self, package_name: str, version: str, current_python: str, required_python: str):
        message = f"Package '{package_name}=={version}' requires Python {required_python}, but current version is {current_python}"
        details = {
            'package_name': package_name,
            'version': version,
            'current_python': current_python,
            'required_python': required_python
        }
        super().__init__(message, details)
        self.package_name = package_name
        self.version = version
        self.current_python = current_python
        self.required_python = required_python


def handle_pypi_error(func):
    """
    Decorator to handle PyPI-related errors gracefully.

    This decorator catches common PyPI errors and converts them to
    appropriate PyResolver exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Convert common errors to PyResolver exceptions
            error_message = str(e).lower()

            if "404" in error_message or "not found" in error_message:
                # Extract package name if possible
                package_name = "unknown"
                if len(args) > 1 and isinstance(args[1], str):
                    package_name = args[1]
                raise PackageNotFoundError(package_name) from e

            elif "timeout" in error_message or "timed out" in error_message:
                raise NetworkError("Request timed out", details={'original_error': str(e)}) from e

            elif "connection" in error_message or "network" in error_message:
                raise NetworkError("Network connection failed", details={'original_error': str(e)}) from e

            else:
                # Re-raise as generic PyResolver error
                raise PyResolverError(f"Unexpected error: {e}") from e

    return wrapper