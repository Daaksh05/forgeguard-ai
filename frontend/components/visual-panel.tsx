import type { VisualEvidenceResponse } from "@/types/api";
import { formatTimestamp, titleCase } from "@/lib/format";
import { Icon, PanelMessage, SectionCard, SeverityBadge } from "@/components/ui";

export function VisualPanel({
  report,
  loading,
  error,
}: {
  report: VisualEvidenceResponse | null;
  loading: boolean;
  error: string | null;
}) {
  const isDemo = report?.mode === "DEMO" || report?.findings.some((finding) => finding.mode === "DEMO");
  return (
    <SectionCard
      title="Visual evidence"
      eyebrow="Phase 5 · inspection evidence"
      icon="camera"
      action={isDemo ? (
        <span className="inline-flex items-center gap-1.5 rounded border border-amber/35 bg-amber/10 px-2 py-1 text-[9px] font-bold tracking-[0.12em] text-amber">
          <span className="h-1.5 w-1.5 rounded-full bg-amber" /> DEMO EVIDENCE
        </span>
      ) : report ? (
        <span className="rounded border border-line px-2 py-1 text-[9px] font-bold tracking-[0.12em] text-muted">{report.mode}</span>
      ) : null}
    >
      {error ? (
        <PanelMessage kind="error">{error}</PanelMessage>
      ) : loading ? (
        <PanelMessage kind="loading">Loading visual evidence…</PanelMessage>
      ) : !report ? (
        <PanelMessage kind="empty">No visual evidence is available.</PanelMessage>
      ) : (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="text-xs text-muted">{report.overall_visual_status.replaceAll("_", " ")}</div>
            <SeverityBadge severity={report.max_severity} />
          </div>
          {isDemo && (
            <div className="rounded-md border border-amber/25 bg-amber/[0.06] px-3 py-2 text-[10px] leading-4 text-amber">
              Synthetic Phase 5 demo output. This is not real camera input or neural vision inference.
            </div>
          )}
          {report.findings.length === 0 ? (
            <PanelMessage kind="empty">The report contains no visual findings.</PanelMessage>
          ) : (
            report.findings.map((finding, index) => (
              <article key={`${finding.image_id}-${finding.defect_type}-${index}`} className="rounded-lg border border-line bg-[#0c1115] p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <h3 className="text-xs font-semibold">{titleCase(finding.defect_type)}</h3>
                    <p className="mono mt-1 text-[9px] text-muted">{finding.image_id} · {formatTimestamp(finding.timestamp)}</p>
                  </div>
                  <SeverityBadge severity={finding.severity} />
                </div>
                <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-muted">
                  <span className="inline-flex items-center gap-1"><Icon name="spark" size={12} /> {Math.round(finding.confidence * 100)}% reported confidence</span>
                  <span className="rounded border border-line px-1.5 py-0.5">{finding.mode}</span>
                </div>
                <p className="mt-3 text-xs leading-5 text-[#bac4ca]">{finding.visual_evidence}</p>
                <p className="mt-2 border-l border-amber/50 pl-2 text-[11px] leading-5 text-muted">{finding.possible_implication}</p>
              </article>
            ))
          )}
          <p className="text-[10px] leading-4 text-muted">{report.summary}</p>
        </div>
      )}
    </SectionCard>
  );
}
