import type { Machine } from "@/types/api";
import { formatTimestamp } from "@/lib/format";
import { SeverityBadge, StatusDot, toneForSeverity } from "@/components/ui";

export function MachineOverview({
  machine,
  assessmentTimestamp,
}: {
  machine: Machine;
  assessmentTimestamp: string | null;
}) {
  const tone = toneForSeverity(machine.severity);
  const risk = machine.risk_score ?? 0;
  return (
    <section className="grid gap-4 lg:grid-cols-[minmax(0,1.45fr)_minmax(310px,.85fr)]">
      <div className="grid-background relative overflow-hidden rounded-xl border border-line bg-panel p-5 sm:p-6">
        <div className="pointer-events-none absolute -right-12 -top-20 h-64 w-64 rounded-full border border-line/60" />
        <div className="pointer-events-none absolute -right-2 -top-10 h-44 w-44 rounded-full border border-line/50" />
        <div className="relative">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-muted">Machine overview</p>
              <h2 className="mono mt-2 text-2xl font-semibold tracking-tight text-text sm:text-3xl">{machine.machine_id}</h2>
            </div>
            <SeverityBadge severity={machine.severity} />
          </div>
          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-[10px] text-muted">
            <span className="flex items-center gap-2"><StatusDot tone={tone} />{machine.health_status?.replaceAll("_", " ") ?? "Health status unavailable"}</span>
            <span>Last telemetry <span className="mono text-[#c1cbd1]">{formatTimestamp(machine.last_seen)}</span></span>
          </div>
          <div className="mt-6 max-w-3xl border-l-2 border-lime/65 pl-3">
            <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-muted">Current condition summary</p>
            <p className="mt-2 text-sm leading-6 text-[#d4dde2]">{machine.summary ?? "Run an assessment to generate a condition summary."}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-line bg-panel p-4">
          <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-muted">Health severity</div>
          <div className="mt-3"><SeverityBadge severity={machine.severity} /></div>
          <div className="mt-3 text-[10px] text-muted">From Phase 4 sensor analysis</div>
        </div>
        <div className={`rounded-xl border p-4 ${risk >= 70 ? "border-danger/25 bg-danger/[0.045]" : risk >= 45 ? "border-amber/25 bg-amber/[0.04]" : "border-line bg-panel"}`}>
          <div className="flex items-center justify-between gap-2">
            <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-muted">Risk score</div>
            <span className="mono text-[9px] text-muted">/100</span>
          </div>
          <div className={`mono mt-2 text-3xl font-semibold tracking-tight ${risk >= 70 ? "text-danger" : risk >= 45 ? "text-amber" : "text-good"}`}>
            {machine.risk_score === null ? "—" : Math.round(machine.risk_score)}
          </div>
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-background">
            <div className={`h-full rounded-full ${risk >= 70 ? "bg-danger" : risk >= 45 ? "bg-amber" : "bg-good"}`} style={{ width: `${Math.min(100, Math.max(0, risk))}%` }} />
          </div>
        </div>
        <div className="col-span-2 rounded-xl border border-line bg-panel p-4">
          <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-muted">Latest assessment</div>
          <div className="mono mt-2 text-xs text-[#cbd5da]">
            {assessmentTimestamp ? formatTimestamp(assessmentTimestamp) : "Assessment timestamp unavailable"}
          </div>
          <div className="mt-1 text-[9px] text-muted">
            {assessmentTimestamp ? "Recorded by this dashboard after the API response" : "The assessment API does not include a generation timestamp."}
          </div>
        </div>
      </div>
    </section>
  );
}
