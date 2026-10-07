"use client";

import { Icon, StatusDot } from "@/components/ui";
import type { Machine } from "@/types/api";

export function DashboardHeader({
  machines,
  selectedMachine,
  onSelectMachine,
  apiConnected,
  loading,
}: {
  machines: Machine[];
  selectedMachine: string;
  onSelectMachine: (machineId: string) => void;
  apiConnected: boolean;
  loading: boolean;
}) {
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-background/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:flex-nowrap lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-lime/25 bg-lime/[0.07] text-lime">
            <Icon name="mark" size={22} />
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <h1 className="text-[15px] font-bold tracking-tight text-text">ForgeGuard <span className="text-lime">AI</span></h1>
              <span className="hidden text-[9px] font-semibold uppercase tracking-[0.17em] text-muted sm:inline">Operator console</span>
            </div>
            <p className="mt-0.5 text-[9px] uppercase tracking-[0.12em] text-muted">Industrial decision support</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <div className="hidden items-center gap-2 rounded-lg border border-line bg-panel px-3 py-2 sm:flex">
            <StatusDot tone={apiConnected ? "green" : loading ? "amber" : "red"} />
            <span className="text-[10px] font-semibold tracking-wide text-[#c6d1d7]">
              {apiConnected ? "SYSTEM READY" : loading ? "SYSTEM STARTING" : "SYSTEM OFFLINE"}
            </span>
          </div>
          <div
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${
              apiConnected ? "border-good/20 bg-good/[0.06]" : "border-danger/25 bg-danger/[0.06]"
            }`}
            role="status"
            aria-live="polite"
          >
            <StatusDot tone={apiConnected ? "green" : loading ? "amber" : "red"} />
            <span className={`text-[10px] font-semibold ${apiConnected ? "text-good" : loading ? "text-amber" : "text-danger"}`}>
              API {apiConnected ? "CONNECTED" : loading ? "CONNECTING" : "DISCONNECTED"}
            </span>
          </div>
          <label className="relative flex items-center gap-2 rounded-lg border border-line bg-panel px-3 py-2">
            <span className="hidden text-[9px] font-bold uppercase tracking-[0.12em] text-muted sm:inline">Asset</span>
            <select
              aria-label="Current machine"
              value={selectedMachine}
              onChange={(event) => onSelectMachine(event.target.value)}
              disabled={machines.length === 0 || loading}
              className="max-w-36 cursor-pointer appearance-none bg-transparent pr-5 text-xs font-semibold text-text outline-none disabled:cursor-not-allowed disabled:opacity-50"
            >
              {machines.length === 0 ? <option value="">No machines</option> : machines.map((machine) => (
                <option key={machine.machine_id} value={machine.machine_id}>{machine.machine_id}</option>
              ))}
            </select>
            <Icon name="chevron" size={13} className="pointer-events-none absolute right-2 text-muted" />
          </label>
        </div>
      </div>
    </header>
  );
}
