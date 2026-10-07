"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnomalyPanel } from "@/components/anomaly-panel";
import { AssessmentPanel } from "@/components/assessment-panel";
import { DashboardHeader } from "@/components/dashboard-header";
import { EvidenceFlow } from "@/components/evidence-flow";
import { MachineOverview } from "@/components/machine-overview";
import { MaintenancePanel } from "@/components/maintenance-panel";
import { TelemetryPanel } from "@/components/telemetry-panel";
import { VisualPanel } from "@/components/visual-panel";
import { Icon, PanelMessage } from "@/components/ui";
import { forgeguardApi } from "@/lib/api";
import type {
  AnomalyResponse,
  ApprovalResponse,
  Assessment,
  Machine,
  MaintenanceEvidenceResponse,
  TelemetryResponse,
  VisualEvidenceResponse,
} from "@/types/api";

type ResourceKey = "machine" | "telemetry" | "anomalies" | "visual" | "maintenance" | "assessment";
type DashboardData = {
  machine: Machine | null;
  telemetry: TelemetryResponse | null;
  anomalies: AnomalyResponse | null;
  visual: VisualEvidenceResponse | null;
  maintenance: MaintenanceEvidenceResponse | null;
  assessment: Assessment | null;
};
type DashboardErrors = Record<ResourceKey, string | null>;

const emptyData: DashboardData = {
  machine: null,
  telemetry: null,
  anomalies: null,
  visual: null,
  maintenance: null,
  assessment: null,
};
const emptyErrors: DashboardErrors = {
  machine: null,
  telemetry: null,
  anomalies: null,
  visual: null,
  maintenance: null,
  assessment: null,
};

function failureMessage(result: PromiseSettledResult<unknown>): string | null {
  if (result.status === "fulfilled") return null;
  return result.reason instanceof Error ? result.reason.message : "The request could not be completed.";
}

function fulfilledValue<T>(result: PromiseSettledResult<T>): T | null {
  return result.status === "fulfilled" ? result.value : null;
}

export default function DashboardPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedMachine, setSelectedMachine] = useState("");
  const selectedMachineRef = useRef("");
  const requestId = useRef(0);
  const [data, setData] = useState<DashboardData>(emptyData);
  const [errors, setErrors] = useState<DashboardErrors>(emptyErrors);
  const [apiConnected, setApiConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [assessmentTimestamp, setAssessmentTimestamp] = useState<string | null>(null);
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalError, setApprovalError] = useState<string | null>(null);

  const loadDashboard = useCallback(async (requestedMachine?: string) => {
    const currentRequest = ++requestId.current;
    setLoading(true);
    setPageError(null);
    setApproval(null);
    setApprovalError(null);

    const [healthResult, machinesResult] = await Promise.allSettled([
      forgeguardApi.health(),
      forgeguardApi.machines(),
    ]);
    if (currentRequest !== requestId.current) return;
    setApiConnected(healthResult.status === "fulfilled");

    if (machinesResult.status === "rejected") {
      setPageError(failureMessage(machinesResult) ?? "Could not load the machine list.");
      setLoading(false);
      return;
    }

    const availableMachines = machinesResult.value;
    setMachines(availableMachines);
    const preferredMachine = requestedMachine ?? selectedMachineRef.current;
    const machineId = availableMachines.some((item) => item.machine_id === preferredMachine)
      ? preferredMachine
      : availableMachines[0]?.machine_id ?? "";
    selectedMachineRef.current = machineId;
    setSelectedMachine(machineId);

    if (!machineId) {
      setData(emptyData);
      setErrors(emptyErrors);
      setPageError("The API returned no available machines.");
      setLoading(false);
      return;
    }

    const results = await Promise.allSettled([
      forgeguardApi.machine(machineId),
      forgeguardApi.telemetry(machineId),
      forgeguardApi.anomalies(machineId),
      forgeguardApi.visualEvidence(machineId),
      forgeguardApi.maintenance(machineId),
      forgeguardApi.assessment(machineId),
    ]);
    if (currentRequest !== requestId.current) return;

    setData({
      machine: fulfilledValue(results[0]),
      telemetry: fulfilledValue(results[1]),
      anomalies: fulfilledValue(results[2]),
      visual: fulfilledValue(results[3]),
      maintenance: fulfilledValue(results[4]),
      assessment: fulfilledValue(results[5]),
    });
    setErrors({
      machine: failureMessage(results[0]),
      telemetry: failureMessage(results[1]),
      anomalies: failureMessage(results[2]),
      visual: failureMessage(results[3]),
      maintenance: failureMessage(results[4]),
      assessment: failureMessage(results[5]),
    });
    if (results[5].status === "fulfilled") {
      setAssessmentTimestamp(new Date().toISOString());
    } else {
      setAssessmentTimestamp(null);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const runAssessment = useCallback(async () => {
    const machineId = selectedMachineRef.current;
    if (!machineId) return;
    setAssessmentLoading(true);
    setErrors((current) => ({ ...current, assessment: null }));
    setApproval(null);
    setApprovalError(null);
    try {
      const assessment = await forgeguardApi.assessment(machineId);
      if (selectedMachineRef.current !== machineId) return;
      setData((current) => ({ ...current, assessment }));
      setAssessmentTimestamp(new Date().toISOString());
    } catch (error) {
      if (selectedMachineRef.current === machineId) {
        setErrors((current) => ({
          ...current,
          assessment: error instanceof Error ? error.message : "Assessment request failed.",
        }));
      }
    } finally {
      setAssessmentLoading(false);
    }
  }, []);

  const recordDecision = useCallback(async (approved: boolean, operator: string) => {
    const machineId = selectedMachineRef.current;
    if (!machineId) return;
    setApprovalLoading(true);
    setApprovalError(null);
    try {
      const result = await forgeguardApi.approve({
        machine_id: machineId,
        approved,
        operator: operator.trim(),
        comment: "Operator decision recorded in the ForgeGuard dashboard.",
      });
      if (selectedMachineRef.current === machineId) setApproval(result);
    } catch (error) {
      setApprovalError(error instanceof Error ? error.message : "Could not record the operator decision.");
    } finally {
      setApprovalLoading(false);
    }
  }, []);

  const selectMachine = (machineId: string) => {
    selectedMachineRef.current = machineId;
    setSelectedMachine(machineId);
    setData(emptyData);
    setErrors(emptyErrors);
    setAssessmentTimestamp(null);
    void loadDashboard(machineId);
  };

  return (
    <main className="min-h-screen">
      <DashboardHeader
        machines={machines}
        selectedMachine={selectedMachine}
        onSelectMachine={selectMachine}
        apiConnected={apiConnected}
        loading={loading}
      />

      <div className="mx-auto max-w-[1600px] px-4 pb-12 pt-6 sm:px-6 lg:px-8">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.2em] text-lime">
              <span className="h-px w-5 bg-lime" />
              Intelligent industry · operator view
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-text sm:text-[28px]">Maintenance command center</h1>
            <p className="mt-1.5 text-xs text-muted">Evidence-led equipment health assessment and operator review.</p>
          </div>
          <button
            type="button"
            onClick={() => void loadDashboard(selectedMachineRef.current)}
            disabled={loading || !selectedMachine}
            className="inline-flex items-center gap-2 rounded-lg border border-line bg-panel px-3.5 py-2.5 text-[10px] font-semibold text-[#cbd5da] transition-colors hover:border-lime/30 hover:text-lime disabled:cursor-wait disabled:opacity-50"
          >
            <Icon name="refresh" size={14} className={loading ? "animate-spin" : ""} />
            Refresh evidence
          </button>
        </div>

        {pageError && (
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-danger/30 bg-danger/[0.06] p-4">
            <div className="flex items-start gap-3">
              <Icon name="warning" className="mt-0.5 text-danger" size={17} />
              <div>
                <div className="text-xs font-semibold text-danger">Dashboard data unavailable</div>
                <p className="mt-1 text-[11px] text-[#c9a6a3]">{pageError}</p>
              </div>
            </div>
            <button type="button" onClick={() => void loadDashboard()} className="rounded-md border border-danger/30 px-3 py-2 text-[10px] font-semibold text-danger hover:bg-danger/10">Retry connection</button>
          </div>
        )}

        {!data.machine && !pageError && loading && (
          <div className="mb-5">
            <PanelMessage kind="loading">Connecting to ForgeGuard API and preparing the operator view…</PanelMessage>
          </div>
        )}

        {data.machine && (
          <div className="space-y-5">
            <MachineOverview machine={data.machine} assessmentTimestamp={assessmentTimestamp} />
            <EvidenceFlow />

            <TelemetryPanel
              telemetry={data.telemetry}
              anomalies={data.anomalies}
              loading={loading && !data.telemetry}
              error={errors.telemetry}
            />

            <div className="grid items-start gap-5 xl:grid-cols-2">
              <AnomalyPanel report={data.anomalies} loading={loading && !data.anomalies} error={errors.anomalies} />
              <VisualPanel report={data.visual} loading={loading && !data.visual} error={errors.visual} />
            </div>

            <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,.9fr)_minmax(0,1.1fr)]">
              <MaintenancePanel report={data.maintenance} loading={loading && !data.maintenance} error={errors.maintenance} />
              <AssessmentPanel
                assessment={data.assessment}
                assessmentTimestamp={assessmentTimestamp}
                loading={assessmentLoading || (loading && !data.assessment)}
                error={errors.assessment}
                approval={approval}
                approvalError={approvalError}
                approvalLoading={approvalLoading}
                onRunAssessment={() => void runAssessment()}
                onDecision={(approved, operator) => void recordDecision(approved, operator)}
              />
            </div>
          </div>
        )}

        <footer className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4 text-[9px] text-muted">
          <span>ForgeGuard AI · Human-in-the-loop maintenance decision support</span>
          <span className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-amber" /> Visual evidence is DEMO data · No machinery control</span>
        </footer>
      </div>
    </main>
  );
}
