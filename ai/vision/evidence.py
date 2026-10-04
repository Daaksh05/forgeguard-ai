"""
ForgeGuard AI — Structured Visual Evidence Schema
Defines dataclasses, validation rules, and serialization utilities for
optical camera inspection evidence and visual defect detection reports.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Union


# Standard allowed severity tiers across ForgeGuard AI
ALLOWED_SEVERITIES: Set[str] = {
    "NORMAL",
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
}

# Standard visual defect classifications per visual_dataset_spec.md
ALLOWED_DEFECT_TYPES: Set[str] = {
    "NORMAL_OPERATION",
    "DEFECT_OIL_LEAK",
    "DEFECT_THERMAL_DISCOLOR",
    "DEFECT_HOUSING_CRACK",
    "DEFECT_SEAL_CONTAMINATION",
    "DEFECT_COUPLING_WEAR"
}

# Allowed inference execution modes
ALLOWED_MODES: Set[str] = {
    "REAL",
    "DEMO",
    "INFERENCE_SIMULATED"
}


@dataclass
class BoundingRegion:
    """Bounding box region in image frame (normalized coordinates 0.0 - 1.0 or pixels)."""
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Validate bounding region coordinates."""
        for field_name, val in [("x", self.x), ("y", self.y), ("width", self.width), ("height", self.height)]:
            if not isinstance(val, (int, float)):
                raise TypeError(f"Bounding region '{field_name}' must be a number, got {type(val).__name__}")
            if val < 0.0:
                raise ValueError(f"Bounding region '{field_name}' must be non-negative, got {val}")

    def to_dict(self) -> Dict[str, float]:
        return {
            "x": round(float(self.x), 4),
            "y": round(float(self.y), 4),
            "width": round(float(self.width), 4),
            "height": round(float(self.height), 4)
        }


@dataclass
class VisualEvidence:
    """
    Structured visual inspection evidence for a single visual finding.
    
    Strictly separates:
    - OBSERVATION (visual_evidence): Pure optical facts seen by camera sensor.
    - INTERPRETATION (possible_implication): Domain inference of what the visual symptom implies.
    """
    machine_id: str
    image_id: str
    timestamp: str
    defect_type: str
    confidence: float
    severity: str
    region: Union[BoundingRegion, Dict[str, float]]
    visual_evidence: str        # OBSERVATION: What the camera actually observed
    possible_implication: str   # INTERPRETATION: What that observation may indicate
    mode: str = "DEMO"          # "REAL" or "DEMO"

    def __post_init__(self):
        # Convert dict region to BoundingRegion if needed
        if isinstance(self.region, dict):
            self.region = BoundingRegion(
                x=float(self.region.get("x", 0.0)),
                y=float(self.region.get("y", 0.0)),
                width=float(self.region.get("width", 0.0)),
                height=float(self.region.get("height", 0.0))
            )
        elif not isinstance(self.region, BoundingRegion):
            raise TypeError(f"Region must be a BoundingRegion or dict, got {type(self.region).__name__}")
        
        self.validate()

    def validate(self):
        """Validate all fields against strict schema constraints."""
        if not self.machine_id or not isinstance(self.machine_id, str):
            raise ValueError("machine_id must be a non-empty string")

        if not self.image_id or not isinstance(self.image_id, str):
            raise ValueError("image_id must be a non-empty string")

        if not self.timestamp or not isinstance(self.timestamp, str):
            raise ValueError("timestamp must be a non-empty string")

        # Confidence validation
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be a float between 0.0 and 1.0")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")

        # Severity validation
        if self.severity not in ALLOWED_SEVERITIES:
            raise ValueError(f"Invalid severity '{self.severity}'. Must be one of {sorted(ALLOWED_SEVERITIES)}")

        # Defect type validation
        if self.defect_type not in ALLOWED_DEFECT_TYPES:
            raise ValueError(f"Invalid defect_type '{self.defect_type}'. Must be one of {sorted(ALLOWED_DEFECT_TYPES)}")

        # Mode validation
        if self.mode not in ALLOWED_MODES:
            raise ValueError(f"Invalid mode '{self.mode}'. Must be one of {sorted(ALLOWED_MODES)}")

        # Observation vs Interpretation validation
        if not self.visual_evidence or not self.visual_evidence.strip():
            raise ValueError("visual_evidence (camera observation) cannot be empty")
        if not self.possible_implication or not self.possible_implication.strip():
            raise ValueError("possible_implication (domain interpretation) cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize visual evidence to standard dictionary format."""
        return {
            "machine_id": self.machine_id,
            "image_id": self.image_id,
            "timestamp": self.timestamp,
            "defect_type": self.defect_type,
            "confidence": round(float(self.confidence), 4),
            "severity": self.severity,
            "region": self.region.to_dict() if isinstance(self.region, BoundingRegion) else self.region,
            "visual_evidence": self.visual_evidence,
            "possible_implication": self.possible_implication,
            "mode": self.mode
        }


@dataclass
class VisualInspectionReport:
    """Consolidated visual inspection report for an image or inspection frame."""
    machine_id: str
    image_id: str
    timestamp: str
    findings: List[VisualEvidence] = field(default_factory=list)
    overall_visual_status: str = "NORMAL"
    max_severity: str = "NORMAL"
    summary: str = ""
    mode: str = "DEMO"

    def __post_init__(self):
        self.update_summary()

    def update_summary(self):
        """Derive overall status, max severity, and summary description from findings."""
        if not self.findings:
            self.overall_visual_status = "NORMAL"
            self.max_severity = "NORMAL"
            self.summary = f"No visual defects detected on {self.machine_id}; exterior components appear in nominal condition."
            return

        severity_rank = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        severities = [f.severity for f in self.findings]
        self.max_severity = max(severities, key=lambda s: severity_rank.get(s, 0))

        if self.max_severity == "CRITICAL":
            self.overall_visual_status = "CRITICAL_DEFECT"
        elif self.max_severity in ("HIGH", "MEDIUM"):
            self.overall_visual_status = "DEFECT_DETECTED"
        elif self.max_severity == "LOW":
            self.overall_visual_status = "SUSPICIOUS"
        else:
            self.overall_visual_status = "NORMAL"

        defect_names = [f.defect_type for f in self.findings if f.defect_type != "NORMAL_OPERATION"]
        if defect_names:
            self.summary = (
                f"Visual inspection of {self.machine_id} identified {len(self.findings)} finding(s): "
                f"{', '.join(defect_names)} with maximum severity {self.max_severity}."
            )
        else:
            self.summary = f"Visual inspection of {self.machine_id} confirms normal exterior condition."

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete visual inspection report."""
        return {
            "machine_id": self.machine_id,
            "image_id": self.image_id,
            "timestamp": self.timestamp,
            "overall_visual_status": self.overall_visual_status,
            "max_severity": self.max_severity,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "mode": self.mode
        }
