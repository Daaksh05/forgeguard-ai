export type Severity = "NORMAL" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Machine {
  machine_id: string;
  last_seen: string;
  health_status: string | null;
  severity: Severity | null;
  risk_score: number | null;
  summary: string | null;
  latest_assessment: Assessment | null;
}

export interface TelemetryPoint {
  machine_id: string;
  timestamp: string;
  operating_state: string;
  values: Record<string, number>;
}

export interface TelemetryResponse {
  machine_id: string;
  total: number;
  limit: number;
  offset: number;
  items: TelemetryPoint[];
}

export interface SensorAnomaly {
  machine_id: string;
  timestamp: string;
  sensor: string;
  observed_value: number;
  baseline_value: number;
  threshold: number;
  anomaly_score: number;
  severity: Severity;
  evidence: string;
  possible_implication: string;
}

export interface CorrelatedEvidence {
  machine_id: string;
  timestamp: string;
  pattern_name: string;
  involved_sensors: string[];
  correlation_score: number;
  severity: Severity;
  description: string;
  root_cause_hypothesis: string;
}

export interface MachineHealthState {
  machine_id: string;
  timestamp: string;
  health_status: string;
  risk_score: number;
  severity: Severity;
  anomalous_sensors: string[];
  correlated_evidence: CorrelatedEvidence[];
  summary: string;
  sensor_anomalies: SensorAnomaly[];
}

export interface AnomalyResponse {
  machine_id: string;
  total_samples: number;
  analysis_period: { start: string; end: string };
  overall_health_progression: Array<Record<string, unknown>>;
  final_machine_state: MachineHealthState;
  total_anomalies_detected: number;
  key_findings: string[];
  timeline_evidence: MachineHealthState[];
}

export interface VisualFinding {
  machine_id: string;
  image_id: string;
  timestamp: string;
  defect_type: string;
  confidence: number;
  severity: Severity;
  region: { x: number; y: number; width: number; height: number };
  visual_evidence: string;
  possible_implication: string;
  mode: "DEMO" | "REAL" | "INFERENCE_SIMULATED";
}

export interface VisualEvidenceResponse {
  machine_id: string;
  image_id: string;
  timestamp: string;
  overall_visual_status: string;
  max_severity: Severity;
  findings_count: number;
  findings: VisualFinding[];
  summary: string;
  mode: "DEMO" | "REAL" | "INFERENCE_SIMULATED";
}

export interface MaintenanceResult {
  source_document: string;
  chunk_id: string;
  section: string;
  retrieved_content: string;
  relevance_score: number;
  retrieval_query: string;
  source_path: string;
}

export interface MaintenanceEvidenceResponse {
  query: string;
  total_chunks_searched: number;
  top_k: number;
  retrieval_method: string;
  results_count: number;
  results: MaintenanceResult[];
}

export interface Assessment {
  machine_id: string;
  severity: Severity;
  diagnosis: string;
  confidence: number;
  evidence: string[];
  reasoning: string;
  recommended_actions: string[];
  human_approval_required: boolean;
  metadata: {
    visual_mode?: string;
    mode?: string;
    sources?: { sensor?: boolean; visual?: boolean; maintenance?: boolean };
    source_details?: Record<string, unknown>;
  };
}

export interface ApprovalRequest {
  machine_id: string;
  approved: boolean;
  operator: string;
  comment?: string;
}

export interface ApprovalResponse {
  machine_id: string;
  approved: boolean;
  human_decision: boolean;
}

export interface HealthResponse {
  status: string;
  service: string;
}
