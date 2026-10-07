import { Icon } from "@/components/ui";

const stages = [
  { label: "Sensors", detail: "Telemetry", icon: "wave" as const },
  { label: "Anomaly detection", detail: "Phase 4", icon: "warning" as const },
  { label: "Visual evidence", detail: "DEMO", icon: "camera" as const },
  { label: "Maintenance knowledge", detail: "Phase 6A", icon: "book" as const },
  { label: "AI reasoning", detail: "Phase 6B", icon: "spark" as const },
  { label: "Operator decision", detail: "Human approval", icon: "check" as const },
];

export function EvidenceFlow({ currentStep = 4 }: { currentStep?: number }) {
  return (
    <section aria-label="Evidence flow" className="rounded-xl border border-line bg-panel px-4 py-4 sm:px-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-muted">Decision pipeline</p>
          <h2 className="mt-1 text-xs font-semibold text-text">Evidence flow</h2>
        </div>
        <span className="mono text-[9px] text-muted">Human-in-the-loop</span>
      </div>
      <ol className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {stages.map((stage, index) => {
          const active = index <= currentStep;
          return (
            <li key={stage.label} className="relative flex min-w-0 items-center gap-2 rounded-lg border border-line bg-background/55 p-2.5">
              <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md border ${active ? "border-lime/25 bg-lime/[0.07] text-lime" : "border-line text-muted"}`}>
                <Icon name={stage.icon} size={15} />
              </span>
              <span className="min-w-0">
                <span className="block truncate text-[10px] font-semibold text-text">{stage.label}</span>
                <span className="mt-0.5 block truncate text-[9px] text-muted">{stage.detail}</span>
              </span>
              {index < stages.length - 1 && (
                <span className="absolute -right-[10px] top-1/2 z-10 hidden -translate-y-1/2 text-muted lg:block">
                  <Icon name="arrow" size={12} />
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
