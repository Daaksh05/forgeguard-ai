import type { AnomalyResponse } from "@/types/api";
import { formatTimestamp, sensorLabel } from "@/lib/format";
import { PanelMessage, SectionCard, SeverityBadge } from "@/components/ui";

export function AnomalyPanel({
  report,
  loading,
  error,
}: {
  report: AnomalyResponse | null;
  loading: boolean;
  error: string | null;
}) {
  const state = report?.final_machine_state;
  return (
    <SectionCard
      title="Anomaly evidence"
      eyebrow="Phase 4 · sensor analysis"
      icon="warning"
      action={report ? <span className="mono text-[10px] text-muted">{report.total_anomalies_detected} events</span> : null}
    >
      {error ? (
        <PanelMessage kind="error">{error}</PanelMessage>
      ) : loading ? (
        <PanelMessage kind="loading">Evaluating sensor evidence…</PanelMessage>
      ) : !report || !state ? (
        <PanelMessage kind="empty">No anomaly report is available.</PanelMessage>
      ) : (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line bg-panel-raised/60 p-3">
            <div>
              <div className="text-[10px] uppercase tracking-[0.15em] text-muted">Machine health state</div>
              <div className="mt-1 text-sm font-semibold">{state.health_status.replaceAll("_", " ")}</div>
            </div>
            <SeverityBadge severity={state.severity} />
          </div>

          {state.sensor_anomalies.length === 0 ? (
            <PanelMessage kind="empty">No sensor anomalies were reported in the latest state.</PanelMessage>
          ) : (
            <div className="space-y-2">
              {state.sensor_anomalies.map((anomaly, index) => (
                <article key={`${anomaly.sensor}-${anomaly.timestamp}-${index}`} className="rounded-lg border border-line bg-[#0c1115] p-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <div className="text-xs font-semibold text-text">{sensorLabel(anomaly.sensor)}</div>
                      <div className="mt-1 text-[10px] text-muted">{anomaly.sensor.replaceAll("_", " ")} · {formatTimestamp(anomaly.timestamp)}</div>
                    </div>
                    <SeverityBadge severity={anomaly.severity} />
                  </div>
                  <div className="mono mt-3 flex flex-wrap gap-x-5 gap-y-1 text-[10px]">
                    <span className="text-muted">Observed <b className="text-text">{anomaly.observed_value.toFixed(2)}</b></span>
                    <span className="text-muted">Threshold <b className="text-amber">{anomaly.threshold}</b></span>
                    <span className="text-muted">Baseline <b className="text-text">{anomaly.baseline_value.toFixed(2)}</b></span>
                  </div>
                  <p className="mt-3 text-xs leading-5 text-[#bac4ca]">{anomaly.evidence}</p>
                  {anomaly.possible_implication && (
                    <p className="mt-2 border-l border-amber/50 pl-2 text-[11px] leading-5 text-muted">{anomaly.possible_implication}</p>
                  )}
                </article>
              ))}
            </div>
          )}

          {state.correlated_evidence.length > 0 && (
            <div>
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-[10px] font-bold uppercase tracking-[0.15em] text-muted">Correlated evidence</h3>
                <span className="mono text-[10px] text-muted">{state.correlated_evidence.length} patterns</span>
              </div>
              <div className="space-y-2">
                {state.correlated_evidence.map((item) => (
                  <article key={`${item.pattern_name}-${item.timestamp}`} className="rounded-lg border border-amber/20 bg-amber/[0.04] p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="mono text-[10px] font-bold text-amber">{item.pattern_name}</span>
                      <SeverityBadge severity={item.severity} />
                    </div>
                    <p className="mt-2 text-xs leading-5 text-[#c3cbd0]">{item.description}</p>
                    <p className="mt-2 text-[10px] leading-4 text-muted">Hypothesis from detector: {item.root_cause_hypothesis}</p>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {item.involved_sensors.map((sensor) => (
                        <span key={sensor} className="rounded border border-line bg-panel px-2 py-1 text-[9px] text-muted">{sensorLabel(sensor)}</span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </SectionCard>
  );
}
