/** SOCsentinel — API endpoint constants. */

import { env } from "../config/env";

const BASE = env.apiUrl;

export const API = {
  // Pipeline
  PIPELINE_INVESTIGATE: `${BASE}/pipeline/investigate`,
  PIPELINE_STATUS: (id: string) => `${BASE}/pipeline/status/${id}`,

  // Alerts
  ALERTS: `${BASE}/alerts`,
  ALERT_DETAIL: (id: string) => `${BASE}/alerts/${id}`,
  ALERTS_GENERATE: `${BASE}/alerts/generate`,

  // Orchestrator
  ORCHESTRATOR_ROUTE: `${BASE}/orchestrator/route`,

  // Triage
  TRIAGE_CLASSIFY: `${BASE}/triage/classify`,

  // Evidence
  EVIDENCE_COLLECT: `${BASE}/evidence/collect`,

  // MITRE Mapper
  MITRE_MAP: `${BASE}/mitre/map`,

  // Report
  REPORT_GENERATE: `${BASE}/report/generate`,
  REPORTS: `${BASE}/reports`,
  REPORT_DETAIL: (id: string) => `${BASE}/reports/${id}`,

  // Audit
  AUDIT_TRAIL: (id: string) => `${BASE}/audit/trail/${id}`,

  // System
  HEALTH: `${BASE.replace("/api/v1", "")}/health`,
} as const;
