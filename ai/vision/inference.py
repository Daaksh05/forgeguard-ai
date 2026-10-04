"""
ForgeGuard AI — Computer Vision Inference Interface
Provides a model-independent abstraction layer for image-based visual defect detection.
Designed for future plug-and-play integration with AMD ROCm / PyTorch / ONNX vision backends.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ai.vision.evidence import (
    BoundingRegion,
    VisualEvidence,
    VisualInspectionReport,
)


class BaseVisionDetector(ABC):
    """Abstract interface for computer vision defect detection backends."""

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if vision model weights and compute backend are loaded."""
        pass

    @abstractmethod
    def detect(
        self,
        image_path: Union[str, Path],
        machine_id: str = "PUMP_001",
        timestamp: Optional[str] = None
    ) -> VisualInspectionReport:
        """Process an image file and return structured visual inspection evidence."""
        pass


class VisionInferenceEngine(BaseVisionDetector):
    """
    Production Computer Vision Inference Pipeline for ForgeGuard AI.
    
    Accepts optical inspection imagery, invokes the configured neural vision backbone
    (e.g. YOLOv8 / ViT running on AMD Instinct / ROCm), and converts raw detections into
    standardized VisualEvidence objects.
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None, device: str = "cpu"):
        self.model_path = Path(model_path) if model_path else None
        self.device = device
        self._backend: Optional[Callable] = None
        self._is_loaded = False

        if self.model_path and self.model_path.exists():
            self._load_model()

    def _load_model(self):
        """Internal loader for neural network weights."""
        # Future Phase: Initialize ROCm PyTorch / ONNX model session
        self._is_loaded = True

    def register_backend(self, backend_fn: Callable[[Path], List[Dict[str, Any]]]):
        """Register an external vision inference function/pipeline (e.g. AMD ROCm runner)."""
        self._backend = backend_fn
        self._is_loaded = True

    def is_ready(self) -> bool:
        """Return True if an inference backend or model is active."""
        return self._is_loaded and (self._backend is not None or self.model_path is not None)

    def detect(
        self,
        image_path: Union[str, Path],
        machine_id: str = "PUMP_001",
        timestamp: Optional[str] = None
    ) -> VisualInspectionReport:
        """
        Execute visual defect detection on an input image.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Input image not found: {path}")

        ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        image_id = path.stem

        if not self.is_ready():
            raise RuntimeError(
                f"Vision model weights are not loaded in VisionInferenceEngine. "
                f"To inspect synthetic demonstration scenarios, use 'ai.vision.demo.generate_demo_visual_evidence()'. "
                f"To run real inference, configure model weights or register an AMD ROCm backend."
            )

        # Execute registered neural backend
        raw_detections = self._backend(path) if self._backend else []
        findings: List[VisualEvidence] = []

        for det in raw_detections:
            evidence = VisualEvidence(
                machine_id=machine_id,
                image_id=image_id,
                timestamp=ts,
                defect_type=det["defect_type"],
                confidence=det["confidence"],
                severity=det["severity"],
                region=BoundingRegion(**det["region"]),
                visual_evidence=det["visual_evidence"],
                possible_implication=det["possible_implication"],
                mode="REAL"
            )
            findings.append(evidence)

        report = VisualInspectionReport(
            machine_id=machine_id,
            image_id=image_id,
            timestamp=ts,
            findings=findings,
            mode="REAL"
        )
        return report


# Global default engine instance for convenience
_DEFAULT_ENGINE = VisionInferenceEngine()


def detect(
    image_path: Union[str, Path],
    machine_id: str = "PUMP_001",
    timestamp: Optional[str] = None,
    engine: Optional[VisionInferenceEngine] = None
) -> VisualInspectionReport:
    """
    Public convenience API for running visual defect inference on an image.
    """
    runner = engine or _DEFAULT_ENGINE
    return runner.detect(image_path=image_path, machine_id=machine_id, timestamp=timestamp)
