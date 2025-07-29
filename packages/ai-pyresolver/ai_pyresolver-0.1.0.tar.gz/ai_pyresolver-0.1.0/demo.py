#!/usr/bin/env python3
"""
PyResolver Demo Script

This script demonstrates the capabilities of the AI-powered dependency resolver.
"""

import time
from pyresolver import PyResolver
from pyresolver.core.models import ResolutionStrategy, Package, Version, PackageVersion
from pyresolver.core.resolver import ResolverConfig
from pyresolver.ai.predictor import CompatibilityPredictor


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demo_basic_resolution():
    """Demonstrate basic dependency resolution."""
    print_header("Basic Dependency Resolution")

    resolver = PyResolver()
    requirements = ["django>=4.0", "celery>=5.0", "requests>=2.25.0", "numpy>=1.20.0"]

    print(f"📦 Resolving requirements: {requirements}")

    start_time = time.time()
    resolution = resolver.resolve(requirements)
    end_time = time.time()

    print(f"⏱️  Resolution time: {end_time - start_time:.3f} seconds")
    print(f"✅ Success: {resolution.is_successful}")
    print(f"📊 Packages resolved: {resolution.package_count}")

    if resolution.resolved_packages:
        print("\n📋 Resolved packages:")
        for name, pv in resolution.resolved_packages.items():
            print(f"   • {pv}")

    if resolution.conflicts:
        print(f"\n⚠️  Conflicts detected: {len(resolution.conflicts)}")
        for conflict in resolution.conflicts:
            print(f"   • {conflict}")


def demo_ai_predictions():
    """Demonstrate AI-powered compatibility predictions."""
    print_header("AI Compatibility Predictions")

    predictor = CompatibilityPredictor()

    # Create some mock package versions
    django_package = Package(name="django", description="Web framework")
    versions = [
        PackageVersion(package=django_package, version=Version("3.2.0")),
        PackageVersion(package=django_package, version=Version("4.0.0")),
        PackageVersion(package=django_package, version=Version("4.1.0")),
        PackageVersion(package=django_package, version=Version("4.2.0")),
        PackageVersion(package=django_package, version=Version("5.0.0a1")),  # Pre-release
    ]

    print("🧠 Predicting compatibility scores for Django versions:")
    scores = predictor.predict_compatibility(versions)

    for pv, score in zip(versions, scores):
        print(f"   • {pv}: Score={score.score:.2f}, Confidence={score.confidence:.2f}")
        for reason in score.reasoning:
            print(f"     - {reason}")

    print("\n🎯 AI-selected best version:")
    best_version = predictor.select_best_version(versions, {})
    print(f"   • Selected: {best_version}")


def demo_different_strategies():
    """Demonstrate different resolution strategies."""
    print_header("Resolution Strategy Comparison")

    requirements = ["django", "celery"]
    strategies = [
        ResolutionStrategy.CONSERVATIVE,
        ResolutionStrategy.AGGRESSIVE,
        ResolutionStrategy.AI_OPTIMIZED,
        ResolutionStrategy.BALANCED
    ]

    print(f"📦 Resolving {requirements} with different strategies:")

    for strategy in strategies:
        config = ResolverConfig(strategy=strategy)
        resolver = PyResolver(config)

        start_time = time.time()
        resolution = resolver.resolve(requirements)
        end_time = time.time()

        print(f"\n🔧 Strategy: {strategy.value}")
        print(f"   ⏱️  Time: {end_time - start_time:.3f}s")
        print(f"   ✅ Success: {resolution.is_successful}")
        print(f"   📊 Packages: {resolution.package_count}")

        if resolution.resolved_packages:
            for name, pv in resolution.resolved_packages.items():
                print(f"      • {pv}")


def demo_conflict_explanation():
    """Demonstrate conflict explanation capabilities."""
    print_header("Conflict Analysis and Explanation")

    resolver = PyResolver()

    # Create a scenario that might cause conflicts
    conflicting_requirements = ["django==3.0", "django==4.0"]

    print(f"📦 Attempting to resolve conflicting requirements: {conflicting_requirements}")

    resolution = resolver.resolve(conflicting_requirements)

    if resolution.conflicts:
        print(f"\n⚠️  Conflicts detected: {len(resolution.conflicts)}")

        for i, conflict in enumerate(resolution.conflicts, 1):
            print(f"\n🔍 Conflict {i}:")
            explanation = resolver.explain_conflict(conflict)
            print(explanation)
    else:
        print("✅ No conflicts detected (this is expected with our mock implementation)")


def demo_performance_metrics():
    """Demonstrate performance metrics and statistics."""
    print_header("Performance Metrics")

    # Test with different complexity levels
    test_cases = [
        (["django"], "Simple (1 package)"),
        (["django", "celery"], "Medium (2 packages)"),
        (["django", "celery", "requests", "numpy"], "Complex (4 packages)"),
    ]

    print("📊 Performance analysis across different complexity levels:")

    for requirements, description in test_cases:
        resolver = PyResolver()

        start_time = time.time()
        resolution = resolver.resolve(requirements)
        end_time = time.time()

        print(f"\n🧪 {description}")
        print(f"   📦 Requirements: {len(requirements)}")
        print(f"   ⏱️  Resolution time: {end_time - start_time:.3f}s")
        print(f"   📊 Packages resolved: {resolution.package_count}")
        print(f"   ✅ Success rate: {'100%' if resolution.is_successful else '0%'}")


def main():
    """Run all demonstrations."""
    print("🚀 PyResolver AI-Powered Dependency Resolution Demo")
    print("   Demonstrating intelligent dependency resolution capabilities")

    try:
        demo_basic_resolution()
        demo_ai_predictions()
        demo_different_strategies()
        demo_conflict_explanation()
        demo_performance_metrics()

        print_header("Demo Complete")
        print("🎉 All demonstrations completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • AI-powered version compatibility prediction")
        print("   • Multiple resolution strategies")
        print("   • Intelligent conflict detection and explanation")
        print("   • Performance optimization")
        print("   • Comprehensive package resolution")

        print("\n🔗 Next Steps:")
        print("   • Try the CLI: python -m pyresolver.cli resolve 'django>=4.0'")
        print("   • Run tests: python tests/test_basic_functionality.py")
        print("   • Explore the codebase in the pyresolver/ directory")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()