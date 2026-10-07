"""Pydantic API schemas for the ForgeGuard service."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class HealthResponse(BaseModel):
    status: str
    service: str


class TelemetryPoint(BaseModel):
    machine_id: str
    timestamp: str
    operating_state: str
    values: dict[str, float]


class TelemetryResponse(BaseModel):
    machine_id: str
    total: int
    limit: int
    offset: int
    items: list[TelemetryPoint]


class AnomalyResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    machine_id: str
    total_samples: int
    analysis_period: dict[str, str]
    overall_health_progression: list[dict[str, Any]]
    final_machine_state: dict[str, Any]
    total_anomalies_detected: int
    key_findings: list[str]
    timeline_evidence: list[dict[str, Any]]


class VisualEvidenceResponse(BaseModel):
    machine_id: str
    image_id: str
    timestamp: str
    overall_visual_status: str
    max_severity: str
    findings_count: int
    findings: list[dict[str, Any]]
    summary: str
    mode: Literal["DEMO", "REAL", "INFERENCE_SIMULATED"]


class MaintenanceEvidenceResponse(BaseModel):
    query: str
    total_chunks_searched: int
    top_k: int
    retrieval_method: str
    results_count: int
    results: list[dict[str, Any]]


class AssessmentRequest(BaseModel):
    machine_id: str = Field(min_length=1)
    notes: str | None = None

    @field_validator("machine_id")
    @classmethod
    def strip_machine_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("machine_id must not be blank")
        return value


class AssessmentResponse(BaseModel):
    """Phase 6B AgentOutput fields; intentionally kept schema-compatible."""

    machine_id: str
    severity: str
    diagnosis: str
    confidence: float
    evidence: list[str]
    reasoning: str
    recommended_actions: list[str]
    human_approval_required: bool
    metadata: dict[str, Any]


class Machine(BaseModel):
    machine_id: str
    last_seen: str
    health_status: str | None = None
    severity: str | None = None
    risk_score: float | None = None
    summary: str | None = None
    latest_assessment: AssessmentResponse | None = None


class ApprovalRequest(BaseModel):
    machine_id: str = Field(min_length=1)
    approved: StrictBool
    operator: str = Field(min_length=1)
    comment: str | None = None

    @field_validator("machine_id", "operator")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class ApprovalResponse(BaseModel):
    machine_id: str
    approved: bool
    human_decision: bool
