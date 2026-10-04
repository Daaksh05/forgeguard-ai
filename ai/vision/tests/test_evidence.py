"""
ForgeGuard AI — Unit Tests for Computer Vision Evidence & Interface Layer
Covers:
- Valid evidence creation and serialization
- Confidence boundary validation
- Severity validation
- Defect type validation
- Bounding region validation
- Normal / no-defect evidence
- Multiple visual findings report aggregation
- Demo mode explicit "DEMO" mode indicator
- Inference interface contract
"""

import unittest
from pathlib import Path

from ai.vision.demo import (
    generate_demo_visual_evidence,
    get_demo_evidence_incipient,
    get_demo_evidence_normal,
    get_demo_evidence_severe,
)
from ai.vision.evidence import (
    ALLOWED_DEFECT_TYPES,
    ALLOWED_SEVERITIES,
    BoundingRegion,
    VisualEvidence,
    VisualInspectionReport,
)
from ai.vision.inference import BaseVisionDetector, VisionInferenceEngine, detect


class TestVisualEvidenceSchema(unittest.TestCase):

    def test_valid_evidence_creation(self):
        """Verify valid visual evidence constructs properly and serializes to dict."""
        evidence = VisualEvidence(
            machine_id="PUMP_001",
            image_id="IMG_001",
            timestamp="2026-10-04T12:00:00Z",
            defect_type="DEFECT_OIL_LEAK",
            confidence=0.92,
            severity="HIGH",
            region=BoundingRegion(x=0.42, y=0.55, width=0.18, height=0.22),
            visual_evidence="Dark fluid weeping from labyrinth seal.",
            possible_implication="Loss of lubricant in bearing cavity.",
            mode="DEMO"
        )

        data = evidence.to_dict()
        self.assertEqual(data["machine_id"], "PUMP_001")
        self.assertEqual(data["defect_type"], "DEFECT_OIL_LEAK")
        self.assertEqual(data["confidence"], 0.92)
        self.assertEqual(data["severity"], "HIGH")
        self.assertEqual(data["mode"], "DEMO")
        self.assertEqual(data["region"]["x"], 0.42)
        self.assertEqual(data["region"]["width"], 0.18)
        self.assertIn("Dark fluid weeping", data["visual_evidence"])
        self.assertIn("Loss of lubricant", data["possible_implication"])

    def test_invalid_confidence(self):
        """Verify confidence values outside [0.0, 1.0] raise ValueError."""
        # Greater than 1.0
        with self.assertRaises(ValueError):
            VisualEvidence(
                machine_id="PUMP_001",
                image_id="IMG_001",
                timestamp="2026-10-04T12:00:00Z",
                defect_type="DEFECT_OIL_LEAK",
                confidence=1.25,
                severity="HIGH",
                region=BoundingRegion(x=0.1, y=0.1, width=0.2, height=0.2),
                visual_evidence="Leak",
                possible_implication="Friction"
            )

        # Less than 0.0
        with self.assertRaises(ValueError):
            VisualEvidence(
                machine_id="PUMP_001",
                image_id="IMG_001",
                timestamp="2026-10-04T12:00:00Z",
                defect_type="DEFECT_OIL_LEAK",
                confidence=-0.1,
                severity="HIGH",
                region=BoundingRegion(x=0.1, y=0.1, width=0.2, height=0.2),
                visual_evidence="Leak",
                possible_implication="Friction"
            )

    def test_invalid_severity(self):
        """Verify unauthorized severity string raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            VisualEvidence(
                machine_id="PUMP_001",
                image_id="IMG_001",
                timestamp="2026-10-04T12:00:00Z",
                defect_type="DEFECT_OIL_LEAK",
                confidence=0.85,
                severity="SUPER_URGENT",  # Invalid
                region=BoundingRegion(x=0.1, y=0.1, width=0.2, height=0.2),
                visual_evidence="Leak",
                possible_implication="Friction"
            )
        self.assertIn("Invalid severity", str(ctx.exception))

    def test_invalid_defect_type(self):
        """Verify unauthorized defect type raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            VisualEvidence(
                machine_id="PUMP_001",
                image_id="IMG_001",
                timestamp="2026-10-04T12:00:00Z",
                defect_type="UNKNOWN_ALIEN_DAMAGE",  # Invalid
                confidence=0.85,
                severity="HIGH",
                region=BoundingRegion(x=0.1, y=0.1, width=0.2, height=0.2),
                visual_evidence="Leak",
                possible_implication="Friction"
            )
        self.assertIn("Invalid defect_type", str(ctx.exception))

    def test_invalid_bounding_region(self):
        """Verify negative coordinate in bounding box raises ValueError."""
        with self.assertRaises(ValueError):
            BoundingRegion(x=-0.5, y=0.2, width=0.3, height=0.3)

        with self.assertRaises(ValueError):
            BoundingRegion(x=0.2, y=-0.1, width=0.3, height=0.3)

        with self.assertRaises(ValueError):
            BoundingRegion(x=0.2, y=0.2, width=-0.3, height=0.3)

    def test_normal_no_defect_evidence(self):
        """Verify nominal/healthy machine visual evidence structure."""
        report = get_demo_evidence_normal()
        self.assertEqual(report.machine_id, "PUMP_001")
        self.assertEqual(report.overall_visual_status, "NORMAL")
        self.assertEqual(report.max_severity, "NORMAL")
        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].defect_type, "NORMAL_OPERATION")
        self.assertEqual(report.mode, "DEMO")

    def test_multiple_visual_findings_aggregation(self):
        """Verify multiple findings in a single report correctly escalate max_severity and status."""
        incipient_report = get_demo_evidence_incipient()
        self.assertEqual(len(incipient_report.findings), 2)
        self.assertEqual(incipient_report.overall_visual_status, "DEFECT_DETECTED")
        self.assertEqual(incipient_report.max_severity, "MEDIUM")

        severe_report = get_demo_evidence_severe()
        self.assertEqual(len(severe_report.findings), 2)
        self.assertEqual(severe_report.overall_visual_status, "CRITICAL_DEFECT")
        self.assertEqual(severe_report.max_severity, "CRITICAL")
        self.assertEqual(severe_report.mode, "DEMO")

    def test_demo_mode_explicit_indicator(self):
        """Verify every demo output strictly carries the 'DEMO' mode indicator."""
        demo_dict = generate_demo_visual_evidence("all")
        self.assertEqual(demo_dict["mode"], "DEMO")
        for stage_key, stage_val in demo_dict["scenarios"].items():
            self.assertEqual(stage_val["mode"], "DEMO")
            for finding in stage_val["findings"]:
                self.assertEqual(finding["mode"], "DEMO")

    def test_vision_inference_engine_interface(self):
        """Verify VisionInferenceEngine implements BaseVisionDetector and handles unready state."""
        engine = VisionInferenceEngine()
        self.assertIsInstance(engine, BaseVisionDetector)
        self.assertFalse(engine.is_ready())

        # Calling detect without loaded weights must raise RuntimeError
        fake_path = Path("non_existent_image.jpg")
        # Should raise FileNotFoundError for non-existent file
        with self.assertRaises(FileNotFoundError):
            engine.detect(fake_path)

        # Registering a mock backend should make engine ready
        def mock_backend(p):
            return [{
                "defect_type": "DEFECT_OIL_LEAK",
                "confidence": 0.95,
                "severity": "HIGH",
                "region": {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.2},
                "visual_evidence": "Mock leak detection",
                "possible_implication": "Mock implication"
            }]

        engine.register_backend(mock_backend)
        self.assertTrue(engine.is_ready())


if __name__ == "__main__":
    unittest.main()
