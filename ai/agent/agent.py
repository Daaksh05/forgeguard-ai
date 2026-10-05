"""Public agent interface for the ForgeGuard reasoning layer."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from .evidence_adapter import adapt_evidence
from .reasoning import ReasoningEngine
from .schemas import AgentInput, AgentOutput, MachineContext


class Agent:
    """High-level entry point for the multimodal reasoning layer."""

    def __init__(self, reasoning_engine: Optional[ReasoningEngine] = None):
        self.reasoning_engine = reasoning_engine or ReasoningEngine()

    def analyze(self, agent_input: Union[AgentInput, Dict[str, Any]]) -> AgentOutput:
        return self.reasoning_engine.reason(agent_input)

    def from_evidence(
        self,
        *,
        machine_context: Optional[Union[MachineContext, Dict[str, Any]]] = None,
        machine_id: Optional[str] = None,
        sensor_report: Any = None,
        visual_report: Any = None,
        maintenance_report: Any = None,
        notes: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> AgentOutput:
        normalized_input = adapt_evidence(
            machine_context=machine_context,
            machine_id=machine_id,
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
            notes=notes,
            workflow_id=workflow_id,
        )
        return self.analyze(normalized_input)


def run_agent(
    *,
    machine_context: Optional[Union[MachineContext, Dict[str, Any]]] = None,
    machine_id: Optional[str] = None,
    sensor_report: Any = None,
    visual_report: Any = None,
    maintenance_report: Any = None,
    notes: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> AgentOutput:
    """Convenience function for single-call invocation from scripts, tests, or APIs."""
    return Agent().from_evidence(
        machine_context=machine_context,
        machine_id=machine_id,
        sensor_report=sensor_report,
        visual_report=visual_report,
        maintenance_report=maintenance_report,
        notes=notes,
        workflow_id=workflow_id,
    )


__all__ = ["Agent", "run_agent"]
