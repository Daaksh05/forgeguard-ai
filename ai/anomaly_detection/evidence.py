"""
ForgeGuard AI — Structured Anomaly Evidence Objects
Defines dataclasses and serialization utilities for individual sensor anomalies,
multi-sensor correlated evidence, and machine-level health summaries.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorAnomalyEvidence:
    """Structured evidence for a single sensor channel anomaly."""
    machine_id: str
    timestamp: str
    sensor: str
    observed_value: float
    baseline_value: float
    threshold: float
    anomaly_score: float  # Normalized 0.0 - 100.0
    severity: str        # 'NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    evidence: str        # Explainable textual justification
    possible_implication: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to standard serializable dictionary."""
        return asdict(self)


@dataclass
class CorrelatedEvidence:
    """Structured evidence for multi-sensor pattern correlation."""
    machine_id: str
    timestamp: str
    pattern_name: str
    involved_sensors: List[str]
    correlation_score: float  # 0.0 - 100.0
    severity: str
    description: str
    root_cause_hypothesis: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert correlated evidence to dictionary."""
        return asdict(self)


@dataclass
class MachineHealthSummary:
    """Machine-level health, degradation progression, and risk assessment."""
    machine_id: str
    timestamp: str
    health_status: str     # 'HEALTHY', 'EARLY_DEGRADATION', 'SEVERE_DEGRADATION', 'CRITICAL_RISK'
    risk_score: float      # Overall risk index 0.0 - 100.0
    severity: str          # 'NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    anomalous_sensors: List[str]
    correlated_evidence: List[Dict[str, Any]]
    summary: str
    sensor_anomalies: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert machine summary to standard serializable dictionary."""
        return asdict(self)


@dataclass
class TelemetryAnalysisReport:
    """Complete time-series telemetry analysis report."""
    machine_id: str
    total_samples: int
    analysis_period: Dict[str, str]
    overall_health_progression: List[Dict[str, Any]]
    final_machine_state: Dict[str, Any]
    total_anomalies_detected: int
    key_findings: List[str]
    timeline_evidence: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert full report to dictionary."""
        return asdict(self)
