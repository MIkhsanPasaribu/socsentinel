/** SOCsentinel — Audit Trail feature — Timeline Audit Log view. */

import { useQuery } from "@tanstack/react-query";
import {
  ClipboardList,
  Clock,
  CheckCircle2,
  XCircle,
  Brain,
  Filter,
} from "lucide-react";
import { useState, useMemo } from "react";
import { apiClient } from "../../../shared/lib/api";
import { formatRelativeTime } from "../../../shared/lib/utils";
import type { APIResponse, Investigation } from "../../../shared/types";

interface AuditEntry {
  timestamp: string;
  step: string;
  agent: string;
  processing_time_ms: number;
  confidence: number | null;
  status: string;
  investigation_id: string;
  severity: string;
}

/** Agent color mapping for visual distinction. */
const agentColors: Record<string, string> = {
  Orchestrator: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  "L1 Triage": "text-green-400 bg-green-500/10 border-green-500/30",
  "Evidence Collector": "text-purple-400 bg-purple-500/10 border-purple-500/30",
  "MITRE Mapper": "text-red-400 bg-red-500/10 border-red-500/30",
  "Report Writer": "text-amber-400 bg-amber-500/10 border-amber-500/30",
};

function AuditEntryRow({ entry }: { entry: AuditEntry }) {
  const colorClass = agentColors[entry.agent] || "text-gray-400 bg-white/5 border-white/10";

  return (
    <div className="flex items-center gap-4 rounded-lg border border-white/5 bg-white/[0.02] px-4 py-3 transition-all hover:border-white/10 hover:bg-white/[0.04]">
      {/* Timeline dot */}
      <div className="flex flex-col items-center">
        {entry.status === "completed" ? (
          <CheckCircle2 size={16} className="text-green-400" />
        ) : (
          <XCircle size={16} className="text-red-400" />
        )}
      </div>

      {/* Agent badge */}
      <div className={`rounded-md border px-2 py-1 text-xs font-medium ${colorClass}`}>
        <div className="flex items-center gap-1.5">
          <Brain size={12} />
          {entry.agent}
        </div>
      </div>

      {/* Investigation ID */}
      <span className="font-mono text-[10px] text-gray-500">{entry.investigation_id}</span>

      {/* Timing */}
      <div className="flex items-center gap-1 text-xs text-gray-400">
        <Clock size={12} />
        <span>{entry.processing_time_ms.toFixed(1)}ms</span>
      </div>

      {/* Confidence */}
      {entry.confidence !== null && entry.confidence !== undefined && (
        <div className="flex items-center gap-1">
          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/10">
            <div
              className={`h-full rounded-full ${
                entry.confidence > 0.7
                  ? "bg-green-500"
                  : entry.confidence > 0.4
                    ? "bg-orange-500"
                    : "bg-red-500"
              }`}
              style={{ width: `${entry.confidence * 100}%` }}
            />
          </div>
          <span className="text-[10px] text-gray-500">
            {(entry.confidence * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {/* Timestamp */}
      <span className="ml-auto text-[10px] text-gray-500">
        {formatRelativeTime(entry.timestamp)}
      </span>
    </div>
  );
}

export function AuditTrailView() {
  const [agentFilter, setAgentFilter] = useState<string>("all");

  const { data: investigations, isLoading } = useQuery<Investigation[]>({
    queryKey: ["investigations-audit"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<Investigation[]>>("/pipeline/list");
      const summaries = (res.data.data as Investigation[]) || [];

      const full = await Promise.all(
        summaries.map(async (s) => {
          try {
            const detail = await apiClient.get<APIResponse<Investigation>>(
              `/pipeline/status/${s.investigation_id}`
            );
            return detail.data.data as Investigation;
          } catch {
            return s;
          }
        })
      );
      return full;
    },
    refetchInterval: 10_000,
  });

  /** Flatten all audit trail entries across investigations. */
  const allEntries = useMemo(() => {
    if (!investigations) return [];
    const entries: AuditEntry[] = [];
    for (const inv of investigations) {
      if (!inv.audit_trail) continue;
      for (const entry of inv.audit_trail) {
        entries.push({
          ...entry,
          investigation_id: inv.investigation_id,
          severity: inv.alert?.severity || "info",
        });
      }
    }
    // Sort by timestamp descending (most recent first)
    entries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    return entries;
  }, [investigations]);

  /** Filter by agent. */
  const filteredEntries = useMemo(() => {
    if (agentFilter === "all") return allEntries;
    return allEntries.filter((e) => e.agent === agentFilter);
  }, [allEntries, agentFilter]);

  const agents = ["all", "Orchestrator", "L1 Triage", "Evidence Collector", "MITRE Mapper", "Report Writer"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Trail</h1>
          <p className="mt-1 text-sm text-gray-400">
            Complete log of all agent actions across investigations
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          <ClipboardList size={14} />
          <span>{allEntries.length} entries</span>
        </div>
      </div>

      {/* Agent Filter */}
      <div className="flex items-center gap-2">
        <Filter size={14} className="text-gray-500" />
        {agents.map((agent) => (
          <button
            key={agent}
            onClick={() => setAgentFilter(agent)}
            className={`rounded-lg border px-2.5 py-1 text-xs font-medium transition-all ${
              agentFilter === agent
                ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
                : "border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-gray-300"
            }`}
          >
            {agent === "all" ? "All Agents" : agent}
          </button>
        ))}
      </div>

      {/* Audit entries */}
      <div className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-14 animate-pulse rounded-lg bg-white/5" />
            ))}
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="glass-card flex flex-col items-center py-16 text-center">
            <ClipboardList size={48} className="mb-4 text-gray-600" />
            <p className="text-sm text-gray-500">No audit entries yet</p>
            <p className="mt-1 text-xs text-gray-600">
              Run investigations to populate the audit trail
            </p>
          </div>
        ) : (
          filteredEntries.map((entry, i) => <AuditEntryRow key={i} entry={entry} />)
        )}
      </div>
    </div>
  );
}
