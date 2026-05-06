/* eslint-disable @typescript-eslint/no-explicit-any */
/** SOCsentinel — Shared TypeScript types for API responses. */

export interface APIResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T | null;
  error: { code: string; detail?: unknown } | null;
  meta: Record<string, unknown> | null;
}

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface Alert {
  alert_id: string;
  source: string;
  timestamp: string;
  rule_name: string;
  severity: Severity;
  description: string;
  source_ip: string;
  destination_ip: string;
  source_port: number | null;
  destination_port: number | null;
  protocol: string;
  username: string;
  hostname: string;
  raw_log: string;
  metadata: Record<string, string>;
}

export interface AuditEntry {
  timestamp: string;
  step: string;
  agent: string;
  processing_time_ms: number;
  confidence: number | null;
  status: string;
}

export interface Investigation {
  investigation_id: string;
  alert: Alert;
  status: string;
  started_at: string;
  completed_at: string | null;
  orchestrator_result: Record<string, unknown> | null;
  triage_result: Record<string, any> | null;
  evidence_result: Record<string, any> | null;
  mitre_result: Record<string, any> | null;
  report_result: Record<string, any> | null;
  response_result: Record<string, any> | null;
  validator_result: Record<string, any> | null;
  escalation_result: Record<string, any> | null;
  analyst_decision: Record<string, any> | null;
  audit_trail: AuditEntry[];
  total_processing_time_ms: number;
}

export interface InvestigationSummary {
  investigation_id: string;
  alert_id: string;
  status: string;
  severity: Severity;
  started_at: string;
  completed_at: string | null;
  processing_time_ms: number;
}
