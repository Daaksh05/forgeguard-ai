import type { ReactNode } from "react";
import type { Severity } from "@/types/api";

export function Icon({
  name,
  size = 18,
  className = "",
}: {
  name: "mark" | "activity" | "box" | "wave" | "warning" | "camera" | "book" | "spark" | "arrow" | "check" | "x" | "refresh" | "chevron";
  size?: number;
  className?: string;
}) {
  const paths: Record<typeof name, ReactNode> = {
    mark: <><path d="M12 2 21 7v10l-9 5-9-5V7l9-5Z" /><path d="m8 14 2-5 2 6 2-4 2 3" /></>,
    activity: <><path d="M3 12h4l3-8 4 16 3-8h4" /></>,
    box: <><path d="m12 3 9 5-9 5-9-5 9-5Z" /><path d="m3 8 9 5 9-5" /><path d="M12 13v9" /><path d="m3 8v9l9 5 9-5V8" /></>,
    wave: <><path d="M2 12h3l3-7 5 14 3-9 2 4h4" /></>,
    warning: <><path d="m12 3 10 18H2L12 3Z" /><path d="M12 9v5" /><path d="M12 18h.01" /></>,
    camera: <><path d="M4 7h3l2-3h6l2 3h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z" /><circle cx="12" cy="13" r="3" /></>,
    book: <><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22V4.5Z" /><path d="M4 18a2.5 2.5 0 0 1 2.5-2.5H20" /></>,
    spark: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" /><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    x: <><path d="m18 6-12 12" /><path d="m6 6 12 12" /></>,
    refresh: <><path d="M20 7v5h-5" /><path d="M4 17v-5h5" /><path d="M5.6 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 12.4-3" /></>,
    chevron: <path d="m7 10 5 5 5-5" />,
  };

  return (
    <svg
      aria-hidden="true"
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

export function StatusDot({ tone = "green" }: { tone?: "green" | "amber" | "red" }) {
  const colors = {
    green: "bg-good shadow-[0_0_8px_rgba(120,215,154,.65)]",
    amber: "bg-amber shadow-[0_0_8px_rgba(243,185,79,.55)]",
    red: "bg-danger shadow-[0_0_8px_rgba(255,104,94,.6)]",
  };
  return <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${colors[tone]}`} />;
}

export function SeverityBadge({ severity }: { severity: string | null | undefined }) {
  const normalized = severity?.toUpperCase() ?? "UNKNOWN";
  const style =
    normalized === "CRITICAL" || normalized === "HIGH"
      ? "border-danger/30 bg-danger/10 text-danger"
      : normalized === "MEDIUM"
        ? "border-amber/30 bg-amber/10 text-amber"
        : normalized === "NORMAL" || normalized === "LOW"
          ? "border-good/25 bg-good/10 text-good"
          : "border-line bg-panel-raised text-muted";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[10px] font-bold tracking-[0.13em] ${style}`}>
      {(normalized === "HIGH" || normalized === "CRITICAL") && <StatusDot tone="red" />}
      {normalized}
    </span>
  );
}

export function SectionCard({
  title,
  eyebrow,
  icon,
  action,
  children,
  className = "",
}: {
  title: string;
  eyebrow?: string;
  icon?: Parameters<typeof Icon>[0]["name"];
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-xl border border-line bg-panel shadow-[0_14px_45px_rgba(0,0,0,.14)] ${className}`}>
      <div className="flex min-h-[62px] items-center justify-between gap-4 border-b border-line px-5 py-3">
        <div className="flex min-w-0 items-center gap-3">
          {icon && (
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-line bg-panel-raised text-lime">
              <Icon name={icon} size={16} />
            </span>
          )}
          <div className="min-w-0">
            {eyebrow && <p className="mb-0.5 text-[9px] font-bold uppercase tracking-[0.18em] text-muted">{eyebrow}</p>}
            <h2 className="truncate text-sm font-semibold text-text">{title}</h2>
          </div>
        </div>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

export function PanelMessage({
  kind,
  children,
}: {
  kind: "loading" | "error" | "empty";
  children: ReactNode;
}) {
  const color = kind === "error" ? "text-danger" : "text-muted";
  return (
    <div className={`flex min-h-24 items-center justify-center rounded-lg border border-dashed border-line px-4 text-center text-xs ${color}`}>
      {kind === "loading" ? (
        <span className="flex items-center gap-2"><span className="h-3 w-3 animate-spin rounded-full border border-muted border-t-lime" />{children}</span>
      ) : children}
    </div>
  );
}

export function toneForSeverity(severity: Severity | string | null | undefined) {
  switch (severity?.toUpperCase()) {
    case "CRITICAL":
    case "HIGH":
      return "red" as const;
    case "MEDIUM":
      return "amber" as const;
    default:
      return "green" as const;
  }
}
