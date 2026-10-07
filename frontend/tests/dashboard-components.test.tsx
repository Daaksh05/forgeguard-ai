import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AssessmentPanel } from "@/components/assessment-panel";
import { VisualPanel } from "@/components/visual-panel";
import type { Assessment, VisualEvidenceResponse } from "@/types/api";

const assessment: Assessment = {
  machine_id: "PUMP_001",
  severity: "HIGH",
  diagnosis: "Evidence indicates an abnormal machine condition.",
  confidence: 0.87,
  evidence: ["Observed vibration evidence."],
  reasoning: "Sensor and maintenance evidence support further inspection.",
  recommended_actions: ["Inspect the assembly."],
  human_approval_required: true,
  metadata: {
    visual_mode: "DEMO",
    sources: { sensor: true, visual: true, maintenance: true },
  },
};

const visualReport: VisualEvidenceResponse = {
  machine_id: "PUMP_001",
  image_id: "IMG_DEMO",
  timestamp: "2026-10-04T15:30:00Z",
  overall_visual_status: "DEFECT_DETECTED",
  max_severity: "HIGH",
  findings_count: 1,
  summary: "One synthetic visual finding.",
  mode: "DEMO",
  findings: [{
    machine_id: "PUMP_001",
    image_id: "IMG_DEMO",
    timestamp: "2026-10-04T15:30:00Z",
    defect_type: "DEFECT_OIL_LEAK",
    confidence: 0.91,
    severity: "HIGH",
    region: { x: 0, y: 0, width: 1, height: 1 },
    visual_evidence: "Synthetic demo observation.",
    possible_implication: "Demo implication from the existing evidence.",
    mode: "DEMO",
  }],
};

describe("operator decision and visual evidence", () => {
  it("clearly requires human approval and submits only the operator decision", () => {
    const onDecision = vi.fn();
    render(
      <AssessmentPanel
        assessment={assessment}
        assessmentTimestamp={null}
        loading={false}
        error={null}
        approval={null}
        approvalError={null}
        approvalLoading={false}
        onRunAssessment={vi.fn()}
        onDecision={onDecision}
      />,
    );

    expect(screen.getByText("HUMAN APPROVAL REQUIRED")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /approve action/i }));
    expect(onDecision).toHaveBeenCalledWith(true, "demo_operator");
    expect(screen.getByText(/no machinery action will be executed/i)).toBeInTheDocument();
  });

  it("labels Phase 5 demo output as demo evidence", () => {
    render(<VisualPanel report={visualReport} loading={false} error={null} />);
    expect(screen.getByText("DEMO EVIDENCE")).toBeInTheDocument();
    expect(screen.getByText(/not real camera input or neural vision inference/i)).toBeInTheDocument();
    expect(screen.getByText("Synthetic demo observation.")).toBeInTheDocument();
  });
});
