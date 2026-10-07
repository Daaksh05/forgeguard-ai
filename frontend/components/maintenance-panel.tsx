import type { MaintenanceEvidenceResponse } from "@/types/api";
import { PanelMessage, SectionCard } from "@/components/ui";

export function MaintenancePanel({
  report,
  loading,
  error,
}: {
  report: MaintenanceEvidenceResponse | null;
  loading: boolean;
  error: string | null;
}) {
  return (
    <SectionCard
      title="Maintenance knowledge"
      eyebrow="Phase 6A · local BM25 retrieval"
      icon="book"
      action={report ? <span className="mono text-[10px] text-muted">{report.results_count} matched sections</span> : null}
    >
      {error ? (
        <PanelMessage kind="error">{error}</PanelMessage>
      ) : loading ? (
        <PanelMessage kind="loading">Retrieving maintenance references…</PanelMessage>
      ) : !report ? (
        <PanelMessage kind="empty">No maintenance evidence is available.</PanelMessage>
      ) : report.results.length === 0 ? (
        <PanelMessage kind="empty">No matching maintenance sections were returned.</PanelMessage>
      ) : (
        <div className="space-y-3">
          <div className="rounded-lg border border-line bg-panel-raised/50 p-3">
            <div className="text-[9px] font-bold uppercase tracking-[0.15em] text-muted">Condition-driven retrieval query</div>
            <p className="mt-2 line-clamp-3 text-xs leading-5 text-[#bac4ca]">{report.query}</p>
          </div>
          {report.results.map((result) => (
            <article key={result.chunk_id} className="rounded-lg border border-line bg-[#0c1115] p-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <div className="mono text-[10px] font-bold text-lime">{result.source_document}</div>
                  <div className="mt-1 text-xs font-medium leading-5 text-text">{result.section}</div>
                </div>
                <span className="rounded border border-line px-2 py-1 text-[9px] text-muted">
                  Relevance {result.relevance_score.toFixed(2)}
                </span>
              </div>
              <div className="mono mt-2 text-[9px] text-muted">{result.chunk_id} · {result.source_path}</div>
              <div className="scrollbar-thin mt-3 max-h-52 overflow-auto whitespace-pre-wrap rounded-md border border-line/70 bg-background/70 p-3 text-[11px] leading-5 text-[#b9c3c9]">
                {result.retrieved_content}
              </div>
            </article>
          ))}
          <div className="text-[9px] text-muted">{report.retrieval_method} · {report.total_chunks_searched} source chunks searched</div>
        </div>
      )}
    </SectionCard>
  );
}
