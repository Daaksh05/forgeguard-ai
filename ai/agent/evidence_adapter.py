"""Adapters that normalize evidence from earlier ForgeGuard phases into Phase 6B AgentInput."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from .schemas import (
    AgentInput,
    EvidenceItem,
    MachineContext,
    MaintenanceEvidenceInput,
    SensorEvidenceInput,
    VisualEvidenceInput,
    VisualMode,
)


def _to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            converted = value.to_dict()
            if isinstance(converted, dict):
                return converted
        except TypeError:
            pass
    return {}


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _safe_mode(value: Any) -> Optional[VisualMode]:
    if value is None:
        return None
    normalized = str(value).upper()
    if normalized in {"REAL", "DEMO", "INFERENCE_SIMULATED"}:
        return VisualMode(normalized)
    return None


def _coerce_severity(value: Any) -> str:
    severity = str(value or "NORMAL").upper()
    return severity if severity in {"NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"} else "NORMAL"


def _coerce_confidence(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


def _build_evidence_item(
    source_type: str,
    source_name: str,
    *,
    observation: str,
    interpretation: str = "",
    severity: Any = "NORMAL",
    confidence: Any = 0.0,
    timestamp: Any = None,
    source_provenance: str = "",
    mode: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> EvidenceItem:
    return EvidenceItem(
        source_type=source_type,
        source_name=source_name,
        timestamp=str(timestamp) if timestamp is not None else None,
        observation=str(observation or ""),
        interpretation=str(interpretation or ""),
        severity=_coerce_severity(severity),
        confidence=_coerce_confidence(confidence),
        source_provenance=str(source_provenance or ""),
        mode=_safe_mode(mode),
        metadata=metadata or {},
    )


def normalize_sensor_evidence(sensor_report: Any, machine_id: Optional[str] = None) -> Optional[SensorEvidenceInput]:
    """Convert telemetry evidence into SensorEvidenceInput without inventing facts."""
    if sensor_report is None:
        return None

    payload = _to_dict(sensor_report)
    if not payload:
        return None

    resolved_machine_id = str(_first_non_empty(machine_id, payload.get("machine_id"), payload.get("asset_id"), "UNKNOWN"))
    timestamp = _first_non_empty(payload.get("timestamp"), payload.get("analysis_period", {}).get("end"), payload.get("analysis_period", {}).get("start"))

    final_state = payload.get("final_machine_state") if isinstance(payload.get("final_machine_state"), dict) else {}
    anomalies = (
        final_state.get("sensor_anomalies")
        or payload.get("sensor_anomalies")
        or payload.get("anomalies")
        or []
    )
    correlated = final_state.get("correlated_evidence") or payload.get("correlated_evidence") or []

    evidence_items: List[EvidenceItem] = []
    for anomaly in anomalies:
        if isinstance(anomaly, dict):
            anomaly_score = anomaly.get("anomaly_score")
            evidence_items.append(
                _build_evidence_item(
                    "sensor",
                    str(anomaly.get("sensor") or anomaly.get("name") or "sensor"),
                    observation=str(anomaly.get("evidence") or anomaly.get("description") or anomaly.get("summary") or ""),
                    interpretation=str(anomaly.get("possible_implication") or anomaly.get("root_cause_hypothesis") or ""),
                    severity=anomaly.get("severity", "NORMAL"),
                    confidence=(
                        float(anomaly_score) / 100.0
                        if anomaly_score is not None
                        else anomaly.get("confidence", 0.0)
                    ),
                    timestamp=anomaly.get("timestamp") or timestamp,
                    source_provenance=str(anomaly.get("sensor") or anomaly.get("name") or resolved_machine_id),
                    metadata=anomaly,
                )
            )

    for corr in correlated:
        if isinstance(corr, dict):
            correlation_score = corr.get("correlation_score")
            evidence_items.append(
                _build_evidence_item(
                    "sensor",
                    str(corr.get("pattern_name") or corr.get("name") or "correlated_evidence"),
                    observation=str(corr.get("description") or corr.get("summary") or ""),
                    interpretation=str(corr.get("root_cause_hypothesis") or corr.get("hypothesis") or ""),
                    severity=corr.get("severity", "NORMAL"),
                    confidence=(
                        float(correlation_score) / 100.0
                        if correlation_score is not None
                        else corr.get("confidence", 0.0)
                    ),
                    timestamp=corr.get("timestamp") or timestamp,
                    source_provenance=str(corr.get("pattern_name") or corr.get("name") or resolved_machine_id),
                    metadata=corr,
                )
            )

    status = str(final_state.get("health_status") or payload.get("status") or "UNKNOWN")
    summary = str(final_state.get("summary") or payload.get("summary") or " ".join(payload.get("key_findings", [])) or "")

    observed_values: Dict[str, float] = {}
    for sensor_name, value in (final_state.get("sensor_values") or {}).items():
        try:
            observed_values[str(sensor_name)] = float(value)
        except (TypeError, ValueError):
            pass
    for anomaly in anomalies:
        if not isinstance(anomaly, dict):
            continue
        sensor_name = anomaly.get("sensor")
        value = anomaly.get("observed_value")
        if sensor_name and isinstance(value, (int, float)):
            observed_values[str(sensor_name)] = float(value)

    return SensorEvidenceInput(
        machine_id=resolved_machine_id,
        timestamp=str(timestamp) if timestamp else None,
        status=status,
        observed_values=observed_values,
        anomalies=[anomaly for anomaly in anomalies if isinstance(anomaly, dict)],
        correlated_evidence=[corr for corr in correlated if isinstance(corr, dict)],
        summary=summary,
        source=str(payload.get("source") or "sensor_anomaly_detection"),
        evidence_items=evidence_items,
    )


def normalize_visual_evidence(visual_report: Any, machine_id: Optional[str] = None) -> Optional[VisualEvidenceInput]:
    """Convert visual defect evidence to normalized VisualEvidenceInput while preserving mode."""
    if visual_report is None:
        return None

    payload = _to_dict(visual_report)
    if not payload:
        return None

    resolved_machine_id = str(_first_non_empty(machine_id, payload.get("machine_id"), "UNKNOWN"))
    findings = payload.get("findings") or []
    evidence_items: List[EvidenceItem] = []
    mode = _safe_mode(_first_non_empty(payload.get("mode"), payload.get("visual_mode"), "DEMO")) or VisualMode.DEMO

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        evidence_items.append(
            _build_evidence_item(
                "visual",
                str(finding.get("defect_type") or finding.get("name") or "visual_finding"),
                observation=str(finding.get("visual_evidence") or finding.get("observation") or ""),
                interpretation=str(finding.get("possible_implication") or finding.get("interpretation") or ""),
                severity=finding.get("severity", "NORMAL"),
                confidence=finding.get("confidence", 0.0),
                timestamp=finding.get("timestamp") or payload.get("timestamp"),
                source_provenance=str(finding.get("image_id") or payload.get("image_id") or resolved_machine_id),
                mode=finding.get("mode") or mode,
                metadata=finding,
            )
        )

    return VisualEvidenceInput(
        machine_id=resolved_machine_id,
        image_id=str(_first_non_empty(payload.get("image_id"), "")),
        timestamp=str(_first_non_empty(payload.get("timestamp"), "")),
        findings=evidence_items,
        overall_visual_status=str(payload.get("overall_visual_status") or "NORMAL"),
        max_severity=str(payload.get("max_severity") or "NORMAL"),
        summary=str(payload.get("summary") or ""),
        mode=mode,
        source=str(payload.get("source") or "vision_pipeline"),
    )


def normalize_maintenance_evidence(maintenance_report: Any, machine_id: Optional[str] = None) -> Optional[MaintenanceEvidenceInput]:
    """Convert maintenance retrieval results into normalized knowledge evidence."""
    if maintenance_report is None:
        return None

    payload = _to_dict(maintenance_report)
    if not payload:
        return None

    results = payload.get("results") or []
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        results = []

    resolved_machine_id = str(_first_non_empty(machine_id, payload.get("machine_id"), "UNKNOWN"))
    evidence_items: List[EvidenceItem] = []
    document_ids: List[str] = []

    for result in results:
        if not isinstance(result, dict):
            continue
        document_ids.append(str(result.get("source_document") or result.get("document_id") or ""))
        evidence_items.append(
            _build_evidence_item(
                "maintenance",
                str(result.get("source_document") or result.get("document_id") or "maintenance_result"),
                observation=str(result.get("retrieved_content") or result.get("content") or result.get("summary") or ""),
                interpretation=str(result.get("section") or result.get("source_section") or "Maintenance guidance"),
                severity=result.get("severity", "NORMAL"),
                confidence=result.get("confidence", 0.0),
                timestamp=result.get("timestamp"),
                source_provenance=str(result.get("source_path") or result.get("section") or result.get("source_document") or ""),
                metadata=result,
            )
        )

    return MaintenanceEvidenceInput(
        machine_id=resolved_machine_id,
        query=str(payload.get("query") or ""),
        results=evidence_items,
        retrieval_method=str(payload.get("retrieval_method") or ""),
        source=str(payload.get("source") or "maintenance_retrieval"),
        document_ids=list(dict.fromkeys(doc_id for doc_id in document_ids if doc_id)),
    )


def normalize_agent_input(
    *,
    machine_context: Optional[Union[MachineContext, Dict[str, Any]]] = None,
    machine_id: Optional[str] = None,
    sensor_report: Any = None,
    visual_report: Any = None,
    maintenance_report: Any = None,
    notes: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> AgentInput:
    """Build a normalized AgentInput from any combination of modality reports."""
    if machine_context is None:
        sensor_payload = _to_dict(sensor_report)
        visual_payload = _to_dict(visual_report)
        maintenance_payload = _to_dict(maintenance_report)
        resolved_machine_id = _first_non_empty(
            machine_id,
            sensor_payload.get("machine_id"),
            visual_payload.get("machine_id"),
            maintenance_payload.get("machine_id"),
            "UNKNOWN",
        )
        machine_context = {"machine_id": str(resolved_machine_id)}

    if isinstance(machine_context, dict):
        resolved_context = MachineContext(
            machine_id=str(machine_context.get("machine_id") or machine_id or "UNKNOWN"),
            machine_name=machine_context.get("machine_name") or machine_context.get("name"),
            site=machine_context.get("site"),
            operating_state=machine_context.get("operating_state"),
            timestamp=machine_context.get("timestamp"),
            notes=machine_context.get("notes") or notes,
        )
    else:
        resolved_context = machine_context

    sensor_input = normalize_sensor_evidence(sensor_report, machine_id=resolved_context.machine_id)
    visual_input = normalize_visual_evidence(visual_report, machine_id=resolved_context.machine_id)
    maintenance_input = normalize_maintenance_evidence(maintenance_report, machine_id=resolved_context.machine_id)

    return AgentInput(
        machine=resolved_context,
        sensor_evidence=sensor_input,
        visual_evidence=visual_input,
        maintenance_evidence=maintenance_input,
        notes=notes or resolved_context.notes,
        workflow_id=workflow_id,
    )


def adapt_evidence(
    sensor_report: Any = None,
    visual_report: Any = None,
    maintenance_report: Any = None,
    machine_context: Optional[Union[MachineContext, Dict[str, Any]]] = None,
    machine_id: Optional[str] = None,
    notes: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> AgentInput:
    """Backward-compatible alias for building an AgentInput from raw evidence inputs."""
    return normalize_agent_input(
        machine_context=machine_context,
        machine_id=machine_id,
        sensor_report=sensor_report,
        visual_report=visual_report,
        maintenance_report=maintenance_report,
        notes=notes,
        workflow_id=workflow_id,
    )


__all__ = [
    "normalize_sensor_evidence",
    "normalize_visual_evidence",
    "normalize_maintenance_evidence",
    "normalize_agent_input",
    "adapt_evidence",
    "EvidenceAdapter",
]


class EvidenceAdapter:
    """Convenience adapter class for callers that prefer a class-based interface."""

    @staticmethod
    def normalize_sensor_evidence(sensor_report: Any, machine_id: Optional[str] = None) -> Optional[SensorEvidenceInput]:
        return normalize_sensor_evidence(sensor_report, machine_id=machine_id)

    @staticmethod
    def normalize_visual_evidence(visual_report: Any, machine_id: Optional[str] = None) -> Optional[VisualEvidenceInput]:
        return normalize_visual_evidence(visual_report, machine_id=machine_id)

    @staticmethod
    def normalize_maintenance_evidence(maintenance_report: Any, machine_id: Optional[str] = None) -> Optional[MaintenanceEvidenceInput]:
        return normalize_maintenance_evidence(maintenance_report, machine_id=machine_id)

    @staticmethod
    def normalize_agent_input(
        *,
        machine_context: Optional[Union[MachineContext, Dict[str, Any]]] = None,
        machine_id: Optional[str] = None,
        sensor_report: Any = None,
        visual_report: Any = None,
        maintenance_report: Any = None,
        notes: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> AgentInput:
        return normalize_agent_input(
            machine_context=machine_context,
            machine_id=machine_id,
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
            notes=notes,
            workflow_id=workflow_id,
        )
