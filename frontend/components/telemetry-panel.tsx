"use client";

import { useMemo, useState } from "react";
import type { AnomalyResponse, TelemetryResponse } from "@/types/api";
import { displaySensorValue, formatTimestamp, sensorLabel, sensorUnit } from "@/lib/format";
import { Icon, PanelMessage, SectionCard, SeverityBadge } from "@/components/ui";

const sensorOrder = [
  "temperature",
  "vibration",
  "pressure",
  "rpm",
  "current",
  "acoustic_emission",
  "ambient_temp",
];

export function TelemetryPanel({
  telemetry,
  anomalies,
  loading,
  error,
}: {
  telemetry: TelemetryResponse | null;
  anomalies: AnomalyResponse | null;
  loading: boolean;
  error: string | null;
}) {
  const [selectedSensor, setSelectedSensor] = useState("temperature");
  const lastPoint = telemetry?.items.at(-1);
  const sensorAnomalies = anomalies?.final_machine_state.sensor_anomalies ?? [];
  const anomalousSensors = new Set(sensorAnomalies.map((item) => item.sensor));
  const chartPoints = useMemo(() => {
    const readings = telemetry?.items ?? [];
    const values = readings
      .map((point) => point.values[selectedSensor])
      .filter((value): value is number => typeof value === "number" && Number.isFinite(value));
    if (values.length < 2) return "";
    const min = Math.min(...values);
    const max = Math.max(...values);
    const spread = max - min || 1;
    return values
      .map((value, index) => {
        const x = 8 + (index / (values.length - 1)) * 784;
        const y = 158 - ((value - min) / spread) * 126;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }, [telemetry, selectedSensor]);

  const values = lastPoint?.values ?? {};
  const availableSensors = sensorOrder.filter((sensor) => typeof values[sensor] === "number");

  return (
    <SectionCard
      title="Sensor telemetry"
      eyebrow="Source dataset · PUMP_001"
      icon="wave"
      action={telemetry ? (
        <span className="mono text-[10px] text-muted">
          {telemetry.total} samples <span className="px-1 text-line">/</span> latest {formatTimestamp(lastPoint?.timestamp)}
        </span>
      ) : null}
    >
      {error ? (
        <PanelMessage kind="error">{error}</PanelMessage>
      ) : loading ? (
        <PanelMessage kind="loading">Loading source telemetry…</PanelMessage>
      ) : !telemetry || telemetry.items.length === 0 ? (
        <PanelMessage kind="empty">No telemetry readings are available for this machine.</PanelMessage>
      ) : (
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 xl:grid-cols-7">
            {availableSensors.map((sensor) => {
              const abnormal = anomalousSensors.has(sensor);
              const active = selectedSensor === sensor;
              return (
                <button
                  key={sensor}
                  type="button"
                  onClick={() => setSelectedSensor(sensor)}
                  className={`group min-w-0 rounded-lg border p-3 text-left transition-colors ${
                    abnormal
                      ? "border-danger/35 bg-danger/[0.07] hover:bg-danger/[0.11]"
                      : active
                        ? "border-lime/35 bg-lime/[0.06]"
                        : "border-line bg-panel-raised/70 hover:border-line/90 hover:bg-panel-raised"
                  }`}
                  aria-pressed={active}
                >
                  <div className="flex min-h-8 items-start justify-between gap-1">
                    <span className="text-[10px] leading-4 text-muted">{sensorLabel(sensor)}</span>
                    {abnormal && <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-danger" title="Flagged by anomaly analysis" />}
                  </div>
                  <div className={`mono mt-2 text-lg font-semibold tracking-tight ${abnormal ? "text-danger" : "text-text"}`}>
                    {displaySensorValue(sensor, values[sensor])}
                  </div>
                  <div className="mt-0.5 flex items-center justify-between gap-1">
                    <span className="text-[9px] text-muted">{sensorUnit(sensor)}</span>
                    {abnormal && <SeverityBadge severity={sensorAnomalies.find((item) => item.sensor === sensor)?.severity} />}
                  </div>
                </button>
              );
            })}
          </div>

          <div className="rounded-lg border border-line bg-[#0b1014] p-3 sm:p-4">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="text-xs font-semibold text-text">{sensorLabel(selectedSensor)} trend</div>
                <div className="mt-1 text-[10px] text-muted">Last {telemetry.items.length} recorded samples · source CSV</div>
              </div>
              <span className="mono rounded border border-line px-2 py-1 text-[10px] text-muted">
                {sensorUnit(selectedSensor)}
              </span>
            </div>
            <div className="grid-background overflow-hidden rounded-md">
              <svg viewBox="0 0 800 180" className="h-40 w-full overflow-visible" role="img" aria-label={`${sensorLabel(selectedSensor)} readings over source telemetry samples`}>
                {[32, 74, 116, 158].map((y) => (
                  <line key={y} x1="0" x2="800" y1={y} y2={y} stroke="#29323a" strokeDasharray="3 6" />
                ))}
                {chartPoints && (
                  <>
                    <polyline points={`8,158 ${chartPoints} 792,158`} fill="rgba(199,243,107,.045)" stroke="none" />
                    <polyline points={chartPoints} fill="none" stroke="#c7f36b" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
                    {chartPoints.split(" ").filter((_, index, all) => index === all.length - 1).map((point) => {
                      const [cx, cy] = point.split(",");
                      return <circle key={point} cx={cx} cy={cy} r="4" fill="#c7f36b" stroke="#10151a" strokeWidth="2" />;
                    })}
                  </>
                )}
              </svg>
            </div>
            <div className="mt-2 flex justify-between text-[9px] text-muted">
              <span>{formatTimestamp(telemetry.items[0]?.timestamp)}</span>
              <span>{formatTimestamp(lastPoint?.timestamp)}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line pt-3 text-[10px] text-muted">
            <span className="flex items-center gap-2"><Icon name="box" size={13} /> Operating state</span>
            <span className="mono rounded bg-panel-raised px-2 py-1 text-text">{lastPoint?.operating_state ?? "Unavailable"}</span>
          </div>
        </div>
      )}
    </SectionCard>
  );
}
