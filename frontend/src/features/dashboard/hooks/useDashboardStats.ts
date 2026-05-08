/** SOCsentinel — Dashboard hooks — useDashboardStats. */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse, PipelineStats, InvestigationSummary } from "../../../shared/types";

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
