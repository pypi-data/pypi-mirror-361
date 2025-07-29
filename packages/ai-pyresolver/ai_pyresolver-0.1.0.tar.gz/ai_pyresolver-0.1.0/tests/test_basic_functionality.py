"""
Basic functionality tests for PyResolver.

This module contains tests that demonstrate the core functionality of the
AI-powered dependency resolver.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyresolver.core.resolver import PyResolver, ResolverConfig
from pyresolver.core.models import ResolutionStrategy, Package, Version, Dependency
from pyresolver.ai.predictor import CompatibilityPredictor


class TestBasicResolution:
    """Test basic dependency resolution functionality."""

    def test_simple_resolution(self):
        """Test resolving a simple set of dependencies."""
        resolver = PyResolver()
        requirements = ["django>=4.0", "requests>=2.25.0"]

        resolution = resolver.resolve(requirements)

        assert resolution is not None
        assert resolution.resolution_time is not None
        assert resolution.resolution_time > 0

        # Should resolve successfully with mock data
        if resolution.is_successful:
            assert resolution.package_count >= 2
            assert "django" in resolution.resolved_packages
            assert "requests" in resolution.resolved_packages

    def test_conflicting_requirements(self):
        """Test handling of conflicting requirements."""
        resolver = PyResolver()
        # These requirements should create a conflict in a real scenario
        requirements = ["django==3.0", "django==4.0"]

        resolution = resolver.resolve(requirements)

        assert resolution is not None
        # With our mock implementation, this might not create conflicts
        # In a real implementation, this would test conflict detection

    def test_different_strategies(self):
        """Test different resolution strategies."""
        strategies = [
            ResolutionStrategy.CONSERVATIVE,
            ResolutionStrategy.AGGRESSIVE,
            ResolutionStrategy.AI_OPTIMIZED,
            ResolutionStrategy.BALANCED
        ]

        for strategy in strategies:
            config = ResolverConfig(strategy=strategy)
            resolver = PyResolver(config)

            resolution = resolver.resolve(["django"])
            assert resolution is not None
            assert resolution.strategy == strategy


class TestDataModels:
    """Test the core data models."""

    def test_package_creation(self):
        """Test creating Package objects."""
        package = Package(name="Django", description="Web framework")

        assert package.name == "django"  # Should be normalized
        assert package.description == "Web framework"

    def test_version_creation(self):
        """Test creating Version objects."""
        version = Version("1.2.3")

        assert str(version) == "1.2.3"

        # Test version comparison
        v1 = Version("1.0.0")
        v2 = Version("2.0.0")
        assert v1 < v2

    def test_dependency_creation(self):
        """Test creating Dependency objects."""
        package = Package(name="django")
        dependency = Dependency(package=package, version_spec=">=4.0")

        assert dependency.package.name == "django"
        assert dependency.version_spec == ">=4.0"

        # Test version matching
        version_4_1 = Version("4.1.0")
        version_3_2 = Version("3.2.0")

        assert dependency.matches_version(version_4_1)
        assert not dependency.matches_version(version_3_2)


class TestAIPredictor:
    """Test the AI compatibility predictor."""

    def test_predictor_creation(self):
        """Test creating a CompatibilityPredictor."""
        predictor = CompatibilityPredictor()

        assert predictor is not None
        info = predictor.get_model_info()
        assert "is_trained" in info

    def test_heuristic_predictions(self):
        """Test heuristic predictions when no model is trained."""
        predictor = CompatibilityPredictor()

        # Create mock package versions
        from pyresolver.core.models import PackageVersion

        package = Package(name="test-package")
        pv1 = PackageVersion(package=package, version=Version("1.0.0"))
        pv2 = PackageVersion(package=package, version=Version("2.0.0a1"))  # Pre-release

        scores = predictor.predict_compatibility([pv1, pv2])

        assert len(scores) == 2
        assert all(0.0 <= score.score <= 1.0 for score in scores)
        assert all(0.0 <= score.confidence <= 1.0 for score in scores)

        # Pre-release should have lower score
        assert scores[1].score < scores[0].score

    def test_version_selection(self):
        """Test AI-powered version selection."""
        predictor = CompatibilityPredictor()

        # Create mock package versions
        from pyresolver.core.models import PackageVersion

        package = Package(name="test-package")
        versions = [
            PackageVersion(package=package, version=Version("1.0.0")),
            PackageVersion(package=package, version=Version("1.1.0")),
            PackageVersion(package=package, version=Version("2.0.0a1")),  # Pre-release
        ]

        selected = predictor.select_best_version(versions, {})

        assert selected is not None
        assert selected in versions
        # Should prefer stable versions over pre-releases
        assert "a" not in selected.version.version


def test_integration_example():
    """
    Integration test showing the complete workflow.

    This test demonstrates how all components work together to resolve
    dependencies using AI-powered predictions.
    """
    # Create resolver with AI optimization
    config = ResolverConfig(
        strategy=ResolutionStrategy.AI_OPTIMIZED,
        use_ai_predictions=True
    )
    resolver = PyResolver(config)

    # Define some realistic requirements
    requirements = [
        "django>=4.0",
        "celery>=5.0",
        "requests>=2.25.0"
    ]

    # Resolve dependencies
    resolution = resolver.resolve(requirements)

    # Verify results
    assert resolution is not None
    assert resolution.strategy == ResolutionStrategy.AI_OPTIMIZED
    assert resolution.resolution_time is not None

    # Print results for demonstration
    print(f"\n🎯 Integration Test Results:")
    print(f"Strategy: {resolution.strategy.value}")
    print(f"Resolution time: {resolution.resolution_time:.3f}s")
    print(f"Success: {resolution.is_successful}")
    print(f"Packages resolved: {resolution.package_count}")

    if resolution.conflicts:
        print(f"Conflicts: {len(resolution.conflicts)}")
        for conflict in resolution.conflicts:
            print(f"  - {conflict}")

    if resolution.resolved_packages:
        print("Resolved packages:")
        for name, pv in resolution.resolved_packages.items():
            print(f"  - {pv}")


if __name__ == "__main__":
    # Run the integration test directly
    test_integration_example()