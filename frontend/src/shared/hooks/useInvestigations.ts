/** SOCsentinel — Shared investigation data hooks.
 *
 * Eliminates duplicated pipeline/list + pipeline/status fetch patterns
 * across Dashboard, Reports, Audit, and Investigation views.
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/api";
import type { APIResponse, Investigation, InvestigationSummary } from "../types";

/** Fetch investigation summaries (lightweight list). */
export function useInvestigationList(refetchInterval = 5000) {
  return useQuery<InvestigationSummary[]>({
    queryKey: ["investigations"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<InvestigationSummary[]>>("/pipeline/list");
      return (res.data.data as InvestigationSummary[]) || [];
    },
    refetchInterval,
  });
}

/** Fetch full investigation details (with agent results + audit trail). */
export function useInvestigationsFull(refetchInterval = 15000) {
  return useQuery<Investigation[]>({
    queryKey: ["investigations-full"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<InvestigationSummary[]>>("/pipeline/list");
      const summaries = (res.data.data as InvestigationSummary[]) || [];

      const full = await Promise.all(
        summaries.map(async (s) => {
          try {
            const detail = await apiClient.get<APIResponse<Investigation>>(
              `/pipeline/status/${s.investigation_id}`
            );
            return detail.data.data as Investigation;
          } catch {
            return s as unknown as Investigation;
          }
        })
      );
      return full;
    },
    refetchInterval,
  });
}
