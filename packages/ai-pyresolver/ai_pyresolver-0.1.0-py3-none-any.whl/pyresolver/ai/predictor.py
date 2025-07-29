"""
AI-powered compatibility prediction for package versions.

This module implements machine learning models that predict the compatibility
of different package version combinations based on historical data.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# We'll implement these without external ML dependencies for now
# In a real implementation, these would use PyTorch/TensorFlow

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityScore:
    """Represents a compatibility score between package versions."""

    score: float  # 0.0 to 1.0, where 1.0 is highly compatible
    confidence: float  # 0.0 to 1.0, confidence in the prediction
    reasoning: List[str]  # Human-readable reasons for the score

    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class PredictionFeatures:
    """Features extracted for ML prediction."""

    package_name: str
    version: str
    dependency_count: int
    version_age_days: int
    download_count: int
    has_wheels: bool
    python_versions: List[str]
    semantic_version_parts: Tuple[int, int, int]  # major, minor, patch

    def to_vector(self) -> List[float]:
        """Convert features to a numerical vector for ML models."""
        return [
            float(self.dependency_count),
            float(self.version_age_days),
            float(self.download_count),
            1.0 if self.has_wheels else 0.0,
            float(len(self.python_versions)),
            float(self.semantic_version_parts[0]),
            float(self.semantic_version_parts[1]),
            float(self.semantic_version_parts[2]),
        ]


class CompatibilityPredictor:
    """
    AI-powered predictor for package version compatibility.

    This class uses machine learning models to predict how likely different
    package versions are to work together based on historical data.
    """

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the predictor with an optional pre-trained model."""
        self.model_path = model_path
        self._model = None
        self._feature_scaler = None
        self._is_trained = False

        # Load model if path provided
        if model_path and model_path.exists():
            self.load_model(model_path)

    def predict_compatibility(
        self,
        package_versions: List[Any],  # List of PackageVersion objects
        context: Optional[Dict[str, Any]] = None
    ) -> List[CompatibilityScore]:
        """
        Predict compatibility scores for a list of package versions.

        Args:
            package_versions: List of PackageVersion objects to score
            context: Additional context about the current resolution state

        Returns:
            List of CompatibilityScore objects, one for each input package version
        """
        if not self._is_trained:
            logger.warning("Model not trained, using heuristic predictions")
            return self._heuristic_predictions(package_versions)

        scores = []
        for pv in package_versions:
            features = self._extract_features(pv)
            score = self._predict_single(features, context)
            scores.append(score)

        return scores

    def select_best_version(
        self,
        candidate_versions: List[Any],  # List of PackageVersion objects
        current_resolution: Dict[str, Any]
    ) -> Any:  # Returns PackageVersion
        """
        Select the best version from candidates based on AI predictions.

        Args:
            candidate_versions: List of candidate PackageVersion objects
            current_resolution: Current state of dependency resolution

        Returns:
            The PackageVersion with the highest compatibility score
        """
        if not candidate_versions:
            return None

        # Get compatibility scores for all candidates
        scores = self.predict_compatibility(candidate_versions, current_resolution)

        # Find the version with the highest score
        best_idx = 0
        best_score = scores[0].score

        for i, score in enumerate(scores[1:], 1):
            if score.score > best_score:
                best_score = score.score
                best_idx = i

        logger.info(
            f"Selected {candidate_versions[best_idx]} with compatibility score "
            f"{scores[best_idx].score:.3f} (confidence: {scores[best_idx].confidence:.3f})"
        )

        return candidate_versions[best_idx]

    def _extract_features(self, package_version: Any) -> PredictionFeatures:
        """Extract ML features from a PackageVersion object."""
        # Mock feature extraction - in reality this would analyze the package
        return PredictionFeatures(
            package_name=package_version.package.name,
            version=package_version.version.version,
            dependency_count=len(package_version.dependencies),
            version_age_days=30,  # Mock value
            download_count=10000,  # Mock value
            has_wheels=True,  # Mock value
            python_versions=["3.9", "3.10", "3.11"],  # Mock value
            semantic_version_parts=(1, 0, 0),  # Mock value
        )

    def _predict_single(
        self,
        features: PredictionFeatures,
        context: Optional[Dict[str, Any]]
    ) -> CompatibilityScore:
        """Predict compatibility score for a single package version."""
        # Mock ML prediction - in reality this would use a trained model
        feature_vector = features.to_vector()

        # Simple heuristic based on features
        base_score = 0.7

        # Adjust based on dependency count (fewer dependencies = more stable)
        if features.dependency_count < 5:
            base_score += 0.1
        elif features.dependency_count > 20:
            base_score -= 0.1

        # Adjust based on version age (not too old, not too new)
        if 30 <= features.version_age_days <= 365:
            base_score += 0.1
        elif features.version_age_days > 1095:  # > 3 years
            base_score -= 0.2

        # Ensure score is in valid range
        score = max(0.0, min(1.0, base_score))

        return CompatibilityScore(
            score=score,
            confidence=0.8,  # Mock confidence
            reasoning=[
                f"Package has {features.dependency_count} dependencies",
                f"Version is {features.version_age_days} days old",
                "Based on historical compatibility patterns"
            ]
        )

    def _heuristic_predictions(self, package_versions: List[Any]) -> List[CompatibilityScore]:
        """Fallback heuristic predictions when no trained model is available."""
        scores = []

        for pv in package_versions:
            # Simple heuristic: prefer newer versions but not pre-releases
            version_str = pv.version.version

            if "a" in version_str or "b" in version_str or "rc" in version_str:
                # Pre-release version
                score = 0.4
                reasoning = ["Pre-release version, lower compatibility expected"]
            else:
                # Stable version
                score = 0.8
                reasoning = ["Stable version, good compatibility expected"]

            scores.append(CompatibilityScore(
                score=score,
                confidence=0.6,  # Lower confidence for heuristics
                reasoning=reasoning
            ))

        return scores

    def load_model(self, model_path: Path) -> None:
        """Load a pre-trained model from disk."""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            self._model = model_data.get('model')
            self._feature_scaler = model_data.get('scaler')
            self._is_trained = True

            logger.info(f"Loaded model from {model_path}")

        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            self._is_trained = False

    def save_model(self, model_path: Path) -> None:
        """Save the trained model to disk."""
        if not self._is_trained:
            raise ValueError("No trained model to save")

        model_data = {
            'model': self._model,
            'scaler': self._feature_scaler,
            'version': '0.1.0'
        }

        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Saved model to {model_path}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'is_trained': self._is_trained,
            'model_path': str(self.model_path) if self.model_path else None,
            'model_type': type(self._model).__name__ if self._model else None,
        }