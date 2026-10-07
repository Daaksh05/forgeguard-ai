"use client";

import { useState } from "react";
import type { ApprovalResponse, Assessment } from "@/types/api";
import { Icon, PanelMessage, SectionCard, SeverityBadge } from "@/components/ui";

export function AssessmentPanel({
  assessment,
  assessmentTimestamp,
  loading,
  error,
  approval,
  approvalError,
  approvalLoading,
  onRunAssessment,
  onDecision,
}: {
  assessment: Assessment | null;
  assessmentTimestamp: string | null;
  loading: boolean;
  error: string | null;
  approval: ApprovalResponse | null;
  approvalError: string | null;
  approvalLoading: boolean;
  onRunAssessment: () => void;
  onDecision: (approved: boolean, operator: string) => void;
}) {
  const [operator, setOperator] = useState("demo_operator");
  return (
    <SectionCard
      title="AI assessment"
      eyebrow="Phase 6B · multimodal reasoning"
      icon="spark"
      className="border-lime/20"
      action={
        <button
          type="button"
          onClick={onRunAssessment}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md border border-line bg-panel-raised px-3 py-2 text-[10px] font-semibold text-[#cbd5da] transition-colors hover:border-lime/30 hover:text-lime disabled:cursor-wait disabled:opacity-50"
        >
          <Icon name="refresh" size={13} className={loading ? "animate-spin" : ""} />
          {loading ? "Running…" : "Run assessment"}
        </button>
      }
    >
      {error ? (
        <div className="space-y-3">
          <PanelMessage kind="error">{error}</PanelMessage>
          <button type="button" onClick={onRunAssessment} disabled={loading} className="text-xs font-semibold text-lime hover:underline">Retry assessment</button>
        </div>
      ) : loading && !assessment ? (
        <PanelMessage kind="loading">Running sensor, visual, and maintenance evidence through the reasoning agent…</PanelMessage>
      ) : !assessment ? (
        <PanelMessage kind="empty">No assessment is available. Run the assessment pipeline to continue.</PanelMessage>
      ) : (
        <div className="space-y-5">
          <div className="rounded-lg border border-line bg-[#0b1014] p-4 sm:p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.17em] text-muted">
                <Icon name="spark" size={14} className="text-lime" /> Diagnosis
              </div>
              <div className="flex items-center gap-2">
                <span className="mono text-[10px] text-muted">{Math.round(assessment.confidence * 100)}% confidence</span>
                <SeverityBadge severity={assessment.severity} />
              </div>
            </div>
            <p className="mt-4 text-base font-semibold leading-7 text-text sm:text-lg">{assessment.diagnosis}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {Object.entries(assessment.metadata.sources ?? {}).filter(([, included]) => included).map(([source]) => (
                <span key={source} className="rounded border border-lime/20 bg-lime/[0.045] px-2 py-1 text-[9px] font-semibold uppercase tracking-[0.09em] text-lime">{source} evidence</span>
              ))}
              {assessment.metadata.visual_mode && (
                <span className="rounded border border-amber/30 bg-amber/[0.06] px-2 py-1 text-[9px] font-semibold uppercase tracking-[0.09em] text-amber">
                  Visual mode: {assessment.metadata.visual_mode}
                </span>
              )}
            </div>
          </div>

          <div>
            <h3 className="text-[9px] font-bold uppercase tracking-[0.17em] text-muted">Reasoning</h3>
            <p className="mt-2 whitespace-pre-wrap text-xs leading-6 text-[#c0cbd1]">{assessment.reasoning}</p>
          </div>

          {assessment.evidence.length > 0 && (
            <div>
              <h3 className="text-[9px] font-bold uppercase tracking-[0.17em] text-muted">Supporting evidence</h3>
              <ul className="mt-2 space-y-2">
                {assessment.evidence.map((item, index) => (
                  <li key={`${index}-${item.slice(0, 36)}`} className="flex gap-2 text-[11px] leading-5 text-[#bbc6cc]">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-lime/70" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {assessment.recommended_actions.length > 0 && (
            <div>
              <h3 className="text-[9px] font-bold uppercase tracking-[0.17em] text-muted">Recommended actions · for operator review</h3>
              <ol className="mt-2 space-y-2">
                {assessment.recommended_actions.map((action, index) => (
                  <li key={`${index}-${action.slice(0, 30)}`} className="flex gap-3 rounded-md border border-line bg-panel-raised/60 p-3 text-xs leading-5 text-[#d0d9de]">
                    <span className="mono text-[10px] text-lime">{String(index + 1).padStart(2, "0")}</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {assessment.human_approval_required && (
            <div className="rounded-xl border border-amber/45 bg-[linear-gradient(135deg,rgba(243,185,79,.10),rgba(243,185,79,.025))] p-4 sm:p-5">
              <div className="flex items-start gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-amber/35 bg-amber/10 text-amber">
                  <Icon name="warning" size={18} />
                </span>
                <div>
                  <h3 className="text-sm font-extrabold tracking-[0.08em] text-amber">HUMAN APPROVAL REQUIRED</h3>
                  <p className="mt-1 max-w-xl text-[11px] leading-5 text-[#d0c4a7]">
                    Recommendations are decision support only. Record your decision for this assessment; no machinery action will be executed.
                  </p>
                </div>
              </div>

              {approval ? (
                <div className={`mt-4 flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold ${approval.approved ? "border-good/25 bg-good/[0.07] text-good" : "border-danger/25 bg-danger/[0.07] text-danger"}`}>
                  <Icon name={approval.approved ? "check" : "x"} size={15} />
                  {approval.approved ? "Approval decision recorded" : "Rejection decision recorded"} for {approval.machine_id}
                </div>
              ) : (
                <>
                  <label className="mt-4 block max-w-xs">
                    <span className="mb-1.5 block text-[9px] font-bold uppercase tracking-[0.13em] text-muted">Operator</span>
                    <input
                      value={operator}
                      onChange={(event) => setOperator(event.target.value)}
                      maxLength={80}
                      className="w-full rounded-md border border-line bg-background px-3 py-2 text-xs text-text placeholder:text-muted"
                    />
                  </label>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => onDecision(true, operator)}
                      disabled={approvalLoading || !operator.trim()}
                      className="inline-flex items-center gap-2 rounded-md bg-good px-4 py-2.5 text-[10px] font-extrabold tracking-[0.09em] text-[#08110c] transition hover:bg-[#91e3ae] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <Icon name="check" size={14} /> APPROVE ACTION
                    </button>
                    <button
                      type="button"
                      onClick={() => onDecision(false, operator)}
                      disabled={approvalLoading || !operator.trim()}
                      className="inline-flex items-center gap-2 rounded-md border border-danger/40 bg-danger/[0.07] px-4 py-2.5 text-[10px] font-extrabold tracking-[0.09em] text-danger transition hover:bg-danger/[0.13] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <Icon name="x" size={14} /> REJECT ACTION
                    </button>
                  </div>
                  {approvalLoading && <p className="mt-3 text-[10px] text-muted">Recording the operator decision…</p>}
                </>
              )}
              {approvalError && <p role="alert" className="mt-3 text-[11px] text-danger">{approvalError}</p>}
              {assessmentTimestamp && <p className="mt-3 text-[9px] text-muted">Assessment was returned at {new Date(assessmentTimestamp).toLocaleString()} (dashboard-local time).</p>}
            </div>
          )}
        </div>
      )}
    </SectionCard>
  );
}
