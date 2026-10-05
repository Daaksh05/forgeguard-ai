"""Strongly typed schemas for the ForgeGuard multimodal reasoning agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class VisualMode(str, Enum):
    """Allowed visual inference execution modes."""

    REAL = "REAL"
    DEMO = "DEMO"
    INFERENCE_SIMULATED = "INFERENCE_SIMULATED"


@dataclass
class MachineContext:
    """Machine-level metadata used across multimodal evidence evaluation."""

    machine_id: str
    machine_name: Optional[str] = None
    site: Optional[str] = None
    operating_state: Optional[str] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "machine_name": self.machine_name,
            "site": self.site,
            "operating_state": self.operating_state,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }


@dataclass
class EvidenceItem:
    """Normalized evidence unit with clear observation vs interpretation separation."""

    source_type: str
    source_name: str
    timestamp: Optional[str] = None
    observation: str = ""
    interpretation: str = ""
    severity: str = "NORMAL"
    confidence: float = 0.0
    source_provenance: str = ""
    mode: Optional[Union[str, VisualMode]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_name": self.source_name,
            "timestamp": self.timestamp,
            "observation": self.observation,
            "interpretation": self.interpretation,
            "severity": self.severity,
            "confidence": self.confidence,
            "source_provenance": self.source_provenance,
            "mode": self.mode.value if isinstance(self.mode, VisualMode) else self.mode,
            "metadata": self.metadata,
        }


@dataclass
class SensorEvidenceInput:
    """Normalized sensor signal evidence (telemetry and anomaly summaries)."""

    machine_id: str
    timestamp: Optional[str] = None
    status: str = "UNKNOWN"
    observed_values: Dict[str, float] = field(default_factory=dict)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    correlated_evidence: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    source: str = "sensor_anomaly_detection"
    evidence_items: List[EvidenceItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "observed_values": self.observed_values,
            "anomalies": self.anomalies,
            "correlated_evidence": self.correlated_evidence,
            "summary": self.summary,
            "source": self.source,
            "evidence_items": [item.to_dict() for item in self.evidence_items],
        }


@dataclass
class VisualEvidenceInput:
    """Normalized visual inspection evidence and mode metadata."""

    machine_id: str
    image_id: Optional[str] = None
    timestamp: Optional[str] = None
    findings: List[EvidenceItem] = field(default_factory=list)
    overall_visual_status: str = "NORMAL"
    max_severity: str = "NORMAL"
    summary: str = ""
    mode: Optional[Union[str, VisualMode]] = VisualMode.DEMO
    source: str = "vision_pipeline"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "image_id": self.image_id,
            "timestamp": self.timestamp,
            "findings": [item.to_dict() for item in self.findings],
            "overall_visual_status": self.overall_visual_status,
            "max_severity": self.max_severity,
            "summary": self.summary,
            "mode": self.mode.value if isinstance(self.mode, VisualMode) else self.mode,
            "source": self.source,
        }


@dataclass
class MaintenanceEvidenceInput:
    """Normalized maintenance knowledge retrieval evidence with source provenance."""

    machine_id: str
    query: str = ""
    results: List[EvidenceItem] = field(default_factory=list)
    retrieval_method: str = ""
    source: str = "maintenance_retrieval"
    document_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "query": self.query,
            "results": [item.to_dict() for item in self.results],
            "retrieval_method": self.retrieval_method,
            "source": self.source,
            "document_ids": self.document_ids,
        }


@dataclass
class AgentInput:
    """The complete normalized input that the reasoning engine evaluates."""

    machine: MachineContext
    sensor_evidence: Optional[SensorEvidenceInput] = None
    visual_evidence: Optional[VisualEvidenceInput] = None
    maintenance_evidence: Optional[MaintenanceEvidenceInput] = None
    notes: Optional[str] = None
    workflow_id: Optional[str] = None

    def __init__(
        self,
        machine: Optional[Union[MachineContext, Dict[str, Any]]] = None,
        sensor_evidence: Optional[SensorEvidenceInput] = None,
        visual_evidence: Optional[VisualEvidenceInput] = None,
        maintenance_evidence: Optional[MaintenanceEvidenceInput] = None,
        notes: Optional[str] = None,
        workflow_id: Optional[str] = None,
        *,
        machine_info: Optional[Union[MachineContext, Dict[str, Any]]] = None,
    ):
        if machine is None:
            machine = machine_info
        if isinstance(machine, dict):
            machine = MachineContext(
                machine_id=str(machine.get("machine_id") or "UNKNOWN"),
                machine_name=machine.get("machine_name") or machine.get("name"),
                site=machine.get("site"),
                operating_state=machine.get("operating_state"),
                timestamp=machine.get("timestamp"),
                notes=machine.get("notes") or notes,
            )
        if machine is None:
            machine = MachineContext(machine_id="UNKNOWN")
        self.machine = machine
        self.sensor_evidence = sensor_evidence
        self.visual_evidence = visual_evidence
        self.maintenance_evidence = maintenance_evidence
        self.notes = notes or getattr(machine, "notes", None)
        self.workflow_id = workflow_id

    @property
    def machine_info(self) -> MachineContext:
        return self.machine

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine": self.machine.to_dict(),
            "sensor_evidence": self.sensor_evidence.to_dict() if self.sensor_evidence else None,
            "visual_evidence": self.visual_evidence.to_dict() if self.visual_evidence else None,
            "maintenance_evidence": self.maintenance_evidence.to_dict() if self.maintenance_evidence else None,
            "notes": self.notes,
            "workflow_id": self.workflow_id,
        }


@dataclass
class Diagnosis:
    """Structured diagnostic output before final agent report formatting."""

    title: str
    summary: str
    root_cause: str = ""
    severity: str = "MEDIUM"
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "root_cause": self.root_cause,
            "severity": self.severity,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "recommended_actions": self.recommended_actions,
        }


@dataclass
class AgentOutput:
    """Final structured response returned by the reasoning layer."""

    machine_id: str
    severity: str
    diagnosis: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    reasoning: str = ""
    recommended_actions: List[str] = field(default_factory=list)
    human_approval_required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "severity": self.severity,
            "diagnosis": self.diagnosis,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
            "recommended_actions": self.recommended_actions,
            "human_approval_required": self.human_approval_required,
            "metadata": self.metadata,
        }


__all__ = [
    "VisualMode",
    "MachineContext",
    "EvidenceItem",
    "SensorEvidenceInput",
    "VisualEvidenceInput",
    "MaintenanceEvidenceInput",
    "AgentInput",
    "Diagnosis",
    "AgentOutput",
]
