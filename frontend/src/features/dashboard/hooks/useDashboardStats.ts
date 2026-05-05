/** SOCsentinel — Dashboard hooks — useDashboardStats. */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";

interface PipelineStats {
  total_investigations: number;
  completed: number;
  failed: number;
  avg_processing_time_ms: number;
  total_alerts_today: number;
  auto_triaged: number;
  auto_triage_rate: number;
  false_positive_rate: number;
  escalation_rate: number;
  investigations_by_severity: Record<string, number>;
  agent_performance: Array<{
    agent: string;
    avg_time_ms: number;
    total_runs: number;
    max_time_ms: number;
    min_time_ms: number;
  }>;
}

interface InvestigationSummary {
  investigation_id: string;
  alert_id: string;
  status: string;
  severity: string;
  started_at: string;
  completed_at: string | null;
  processing_time_ms: number;
}

/** Fetch aggregate pipeline stats for the dashboard. */
export function usePipelineStats() {
  return useQuery<PipelineStats>({
    queryKey: ["pipeline-stats"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<PipelineStats>>("/pipeline/stats");
      return res.data.data as PipelineStats;
    },
    refetchInterval: 10_000,
  });
}

/** Fetch recent investigations list. */
export function useRecentInvestigations() {
  return useQuery<InvestigationSummary[]>({
    queryKey: ["investigations"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<InvestigationSummary[]>>("/pipeline/list");
      return (res.data.data as InvestigationSummary[]) || [];
    },
    refetchInterval: 10_000,
  });
}
