"""Deterministic reasoning engine for the ForgeGuard multimodal reasoning layer."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence, Union

from .schemas import AgentInput, AgentOutput, Diagnosis, EvidenceItem

SEVERITY_ORDER = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


class ReasoningEngine:
    """Heuristic multimodal reasoner that synthesizes sensor, visual, and maintenance evidence."""

    def reason(self, agent_input: Union[AgentInput, Dict[str, Any]]) -> AgentOutput:
        if isinstance(agent_input, dict):
            from .evidence_adapter import adapt_evidence

            if "machine" in agent_input or "sensor_evidence" in agent_input or "visual_evidence" in agent_input:
                machine = agent_input.get("machine") or {"machine_id": "UNKNOWN"}
                sensor_report = agent_input.get("sensor_evidence")
                visual_report = agent_input.get("visual_evidence")
                maintenance_report = agent_input.get("maintenance_evidence")
                agent_input = adapt_evidence(
                    machine_context=machine,
                    sensor_report=sensor_report,
                    visual_report=visual_report,
                    maintenance_report=maintenance_report,
                    notes=agent_input.get("notes"),
                    workflow_id=agent_input.get("workflow_id"),
                )
            else:
                agent_input = adapt_evidence(
                    machine_context={"machine_id": agent_input.get("machine_id", "UNKNOWN")},
                    sensor_report=agent_input.get("sensor"),
                    visual_report=agent_input.get("visual"),
                    maintenance_report=agent_input.get("maintenance"),
                    notes=agent_input.get("notes"),
                    workflow_id=agent_input.get("workflow_id"),
                )

        if not isinstance(agent_input, AgentInput):
            raise TypeError("agent_input must be an AgentInput or a dict convertible to AgentInput")

        diagnosis = self.build_diagnosis(agent_input)
        reasoning = self.build_reasoning_text(agent_input, diagnosis)
        evidence = self._collect_evidence_strings(agent_input)
        actions = diagnosis.recommended_actions or self.build_recommendations(agent_input)

        output = AgentOutput(
            machine_id=agent_input.machine.machine_id,
            severity=diagnosis.severity,
            diagnosis=diagnosis.summary,
            confidence=max(0.0, min(1.0, diagnosis.confidence)),
            evidence=evidence,
            reasoning=reasoning,
            recommended_actions=actions,
            human_approval_required=True,
            metadata={
                "visual_mode": self._visual_mode(agent_input),
                "mode": self._visual_mode(agent_input),
                "sources": {
                    "sensor": bool(agent_input.sensor_evidence),
                    "visual": bool(agent_input.visual_evidence),
                    "maintenance": bool(agent_input.maintenance_evidence),
                },
                "source_details": {
                    "sensor": {
                        "finding_count": len(agent_input.sensor_evidence.evidence_items)
                        if agent_input.sensor_evidence else 0,
                        "status": agent_input.sensor_evidence.status
                        if agent_input.sensor_evidence else None,
                    },
                    "visual": {
                        "finding_count": len(agent_input.visual_evidence.findings)
                        if agent_input.visual_evidence else 0,
                        "image_id": agent_input.visual_evidence.image_id
                        if agent_input.visual_evidence else None,
                    },
                    "maintenance": {
                        "finding_count": len(agent_input.maintenance_evidence.results)
                        if agent_input.maintenance_evidence else 0,
                        "document_ids": agent_input.maintenance_evidence.document_ids
                        if agent_input.maintenance_evidence else [],
                        "retrieval_method": agent_input.maintenance_evidence.retrieval_method
                        if agent_input.maintenance_evidence else None,
                        "query": agent_input.maintenance_evidence.query
                        if agent_input.maintenance_evidence else None,
                    },
                },
            },
        )
        return output

    def build_diagnosis(self, agent_input: AgentInput) -> Diagnosis:
        condition_items = []
        if agent_input.sensor_evidence:
            condition_items.extend(agent_input.sensor_evidence.evidence_items)
        if agent_input.visual_evidence:
            condition_items.extend(agent_input.visual_evidence.findings)

        highest_severity = self._max_severity(condition_items)
        evidence_strings = self._collect_evidence_strings(agent_input)
        actions = self.build_recommendations(agent_input)

        if not condition_items:
            if agent_input.sensor_evidence and agent_input.sensor_evidence.status.upper() == "HEALTHY":
                summary = (
                    f"Diagnosis: No sensor or visual abnormalities were reported for "
                    f"{agent_input.machine.machine_id}; the sensor report indicates healthy operation."
                )
            else:
                summary = (
                    f"Diagnosis: No sensor or visual condition findings were provided for "
                    f"{agent_input.machine.machine_id}; maintenance references alone do not establish a fault."
                )
            title = "Normal operating condition"
            root_cause = "No abnormal condition evidence was available to identify a root cause."
            confidence = 0.25
            severity = "NORMAL"
        else:
            severity = highest_severity
            correlation = next(
                (
                    item for item in condition_items
                    if item.source_type == "sensor"
                    and item.source_name in {
                        "BEARING_LUBRICATION_DEGRADATION",
                        "THERMAL_DECOUPLING",
                        "MECHANICAL_VS_HYDRAULIC_ISOLATION",
                    }
                ),
                None,
            )
            if correlation:
                title = correlation.source_name.replace("_", " ").title()
            else:
                strongest_findings = [
                    item.source_name.replace("_", " ").title()
                    for item in condition_items
                    if item.severity == highest_severity and item.source_name
                ]
                title = " / ".join(dict.fromkeys(strongest_findings[:2]))

            root_cause_item = correlation or next(
                (item for item in condition_items if item.source_type == "sensor" and item.interpretation),
                next((item for item in condition_items if item.interpretation), None),
            )
            root_cause = (
                f"{root_cause_item.interpretation} (from {root_cause_item.source_name})"
                if root_cause_item
                else "The available findings establish an abnormal condition but do not provide a root-cause interpretation."
            )
            key_observations = [
                item.observation.strip()
                for item in condition_items
                if item.observation.strip()
            ][:3]
            summary = (
                f"Diagnosis: {severity} {title} indicated for {agent_input.machine.machine_id}. "
                f"Observed findings: {' '.join(key_observations)}"
            )
            confidence = self._score_confidence(agent_input, condition_items)

        return Diagnosis(
            title=title,
            summary=summary,
            root_cause=root_cause,
            severity=severity,
            confidence=confidence,
            evidence=evidence_strings[:5],
            recommended_actions=actions,
        )

    def build_reasoning_text(self, agent_input: AgentInput, diagnosis: Diagnosis) -> str:
        """Explanation combining the normalized evidence chain into a plain-language narrative."""
        sensor = agent_input.sensor_evidence
        visual = agent_input.visual_evidence
        maintenance = agent_input.maintenance_evidence

        parts = [
            f"For the machine {agent_input.machine.machine_id}, the assessment identifies {diagnosis.title.lower()}.",
            diagnosis.root_cause,
        ]

        if sensor and sensor.summary:
            parts.append(f"Sensor evidence summary: {sensor.summary}")
        if visual and visual.summary:
            parts.append(f"Visual evidence summary: {visual.summary}")
        if maintenance and maintenance.results:
            sources = [
                f"{item.source_name}, {item.interpretation}"
                for item in maintenance.results[:2]
            ]
            parts.append(f"Retrieved maintenance evidence: {'; '.join(sources)}.")

        if diagnosis.severity in {"HIGH", "CRITICAL"}:
            parts.append(
                "Human approval is required before operating or restarting equipment."
            )

        return " ".join(parts)

    def build_recommendations(self, agent_input: AgentInput) -> List[str]:
        """Return prioritized maintenance actions, including safe-work guidance."""
        actions: List[str] = []
        sensor = agent_input.sensor_evidence
        visual = agent_input.visual_evidence
        maintenance = agent_input.maintenance_evidence

        severity = self._max_severity(self._collect_condition_items(agent_input))
        if sensor and sensor.evidence_items:
            sensors = ", ".join(dict.fromkeys(item.source_name for item in sensor.evidence_items))
            actions.append(f"Verify the reported {sensors} findings against current telemetry.")
        if visual and visual.findings:
            finding = visual.findings[0]
            actions.append(
                f"Inspect the visual finding {finding.source_name} in image "
                f"{visual.image_id or finding.source_provenance} and document whether it has progressed."
            )
        if maintenance and maintenance.results:
            if severity in {"HIGH", "CRITICAL"}:
                for item in maintenance.results:
                    match = re.search(
                        r"(?:\*\*)?EMERGENCY STOP(?:\*\*)?\.\s*Lock out equipment immediately\.",
                        item.observation,
                        flags=re.IGNORECASE,
                    )
                    if match:
                        actions.append(
                            f"{item.source_name} ({item.interpretation}): "
                            f"{match.group(0).replace('**', '')}"
                        )
                        break
            if not actions:
                item = maintenance.results[0]
                actions.append(
                    f"Review the retrieved procedure in {item.source_name}, {item.interpretation}, "
                    "and follow its applicable inspection steps."
                )
        if severity in {"HIGH", "CRITICAL"}:
            actions.append(
                "Keep the machine out of service until responsible maintenance staff review the evidence and approve restart."
            )
        elif not actions:
            actions.append("Continue routine monitoring and log machine health checks.")

        deduped: List[str] = []
        seen = set()
        for action in actions:
            if action not in seen:
                deduped.append(action)
                seen.add(action)
        return deduped[:5]

    def _collect_evidence_items(self, agent_input: AgentInput) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        if agent_input.sensor_evidence:
            items.extend(agent_input.sensor_evidence.evidence_items)
        if agent_input.visual_evidence:
            items.extend(agent_input.visual_evidence.findings)
        if agent_input.maintenance_evidence:
            items.extend(agent_input.maintenance_evidence.results)
        return items

    def _collect_evidence_strings(self, agent_input: AgentInput) -> List[str]:
        evidence_text: List[str] = []
        for item in self._collect_evidence_items(agent_input):
            details = [f"[{item.source_type}:{item.source_name}]"]
            if item.source_provenance and item.source_provenance != item.source_name:
                details.append(f"source={item.source_provenance}")
            if item.mode:
                mode = item.mode.value if hasattr(item.mode, "value") else item.mode
                details.append(f"mode={mode}")
            if item.observation:
                details.append(item.observation)
            if item.interpretation:
                details.append(f"Interpretation: {item.interpretation}")
            if len(details) > 1:
                evidence_text.append(" | ".join(details))
        return evidence_text

    def _collect_condition_items(self, agent_input: AgentInput) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []
        if agent_input.sensor_evidence:
            items.extend(agent_input.sensor_evidence.evidence_items)
        if agent_input.visual_evidence:
            items.extend(agent_input.visual_evidence.findings)
        return items

    def _visual_mode(self, agent_input: AgentInput) -> Union[str, None]:
        if not agent_input.visual_evidence:
            return None
        mode = agent_input.visual_evidence.mode
        return mode.value if hasattr(mode, "value") else mode

    def _max_severity(self, items: Iterable[EvidenceItem]) -> str:
        highest = "NORMAL"
        for item in items:
            current = str(item.severity).upper()
            if SEVERITY_ORDER.get(current, 0) > SEVERITY_ORDER.get(highest, 0):
                highest = current
        return highest

    def _score_confidence(self, agent_input: AgentInput, items: Sequence[EvidenceItem]) -> float:
        if not items:
            return 0.25
        modality_count = sum(
            bool(modality)
            for modality in (
                agent_input.sensor_evidence and agent_input.sensor_evidence.evidence_items,
                agent_input.visual_evidence and agent_input.visual_evidence.findings,
            )
        )
        avg_confidence = sum(item.confidence for item in items) / len(items)
        base = 0.45 + (0.10 * modality_count) + (0.35 * avg_confidence)
        return max(0.25, min(0.99, base))


def build_reasoning_report(agent_input: Union[AgentInput, Dict[str, Any]]) -> AgentOutput:
    """Convenience wrapper for running the deterministic reasoning engine."""
    return ReasoningEngine().reason(agent_input)


__all__ = ["ReasoningEngine", "build_reasoning_report"]
