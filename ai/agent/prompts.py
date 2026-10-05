"""Prompt templates for the ForgeGuard multimodal reasoning agent."""

from __future__ import annotations

from typing import Any, Dict

from .schemas import AgentInput

DEFAULT_SYSTEM_PROMPT = (
    "You are the ForgeGuard AI reasoning engine. Correlate telemetry, visual evidence, "
    "and maintenance guidance; do not invent missing facts; explain uncertainty clearly; "
    "recommend safe maintenance actions and require human approval for high-risk intervention."
)


def build_reasoning_prompt(agent_input: AgentInput) -> str:
    """Construct a deterministic prompt for the reasoning engine."""
    machine = agent_input.machine
    sensor = agent_input.sensor_evidence
    visual = agent_input.visual_evidence
    maintenance = agent_input.maintenance_evidence

    lines = [
        DEFAULT_SYSTEM_PROMPT,
        "",
        f"Machine ID: {machine.machine_id}",
        f"Operating state: {machine.operating_state or 'unknown'}",
        f"Timestamp: {machine.timestamp or 'unknown'}",
    ]

    if sensor:
        lines.append(f"Sensor status: {sensor.status}")
        if sensor.summary:
            lines.append(f"Sensor summary: {sensor.summary}")
        if sensor.anomalies:
            lines.append("Sensor anomalies:")
            for anomaly in sensor.anomalies[:5]:
                lines.append(f"  - {anomaly}")

    if visual:
        lines.append(f"Visual mode: {visual.mode}")
        lines.append(f"Visual status: {visual.overall_visual_status}")
        if visual.summary:
            lines.append(f"Visual summary: {visual.summary}")
        if visual.findings:
            lines.append("Visual findings:")
            for item in visual.findings:
                lines.append(f"  - {item.observation} [{item.severity}]")

    if maintenance:
        lines.append("Maintenance guidance:")
        for item in maintenance.results[:3]:
            lines.append(f"  - {item.source_name}: {item.observation[:220]}")

    prompt = "\n".join(lines)
    return prompt


def build_action_prompt(agent_input: AgentInput) -> str:
    """Prompt focused on prioritizing recommended maintenance actions."""
    machine = agent_input.machine
    sensor = agent_input.sensor_evidence
    visual = agent_input.visual_evidence
    maintenance = agent_input.maintenance_evidence

    sections = [
        f"Machine {machine.machine_id}",
        "Determine the safest next maintenance actions based on available evidence.",
        "Do not invent missing facts or suggest actions that are unsupported by the evidence.",
    ]

    if sensor and sensor.summary:
        sections.append(f"Telemetry context: {sensor.summary}")
    if visual and visual.summary:
        sections.append(f"Visual context: {visual.summary}")
    if maintenance and maintenance.results:
        sections.append("Maintenance references are available; favor actions that align with retrieved guidance.")

    return "\n".join(sections)


__all__ = ["DEFAULT_SYSTEM_PROMPT", "build_reasoning_prompt", "build_action_prompt"]
