"""
PyResolver: AI-Powered Python Dependency Resolution

An intelligent dependency resolver that uses machine learning to automatically
resolve complex dependency conflicts in Python projects.
"""

__version__ = "0.1.0"
__author__ = "PyResolver Team"
__email__ = "team@pyresolver.dev"

from .core.resolver import PyResolver
from .core.models import Package, Version, Dependency, Resolution
from .ai.predictor import CompatibilityPredictor
from .ai.trainer import ModelTrainer

__all__ = [
    "PyResolver",
    "Package",
    "Version",
    "Dependency",
    "Resolution",
    "CompatibilityPredictor",
    "ModelTrainer",
]