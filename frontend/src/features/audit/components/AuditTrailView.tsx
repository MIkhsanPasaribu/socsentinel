/** SOCsentinel — Audit Trail feature — Enhanced Timeline Audit Log view.
 *
 * Features: expandable reasoning, confidence gauges, severity + agent + search
 * filters, grouped by investigation, timeline connectors.
 */

import {
  ClipboardList,
  Clock,
  CheckCircle2,
  XCircle,
  Brain,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  Shield,
} from "lucide-react";
import { useState, useMemo } from "react";
import { cn, formatRelativeTime, getSeverityBadgeClass } from "../../../shared/lib/utils";
import { useInvestigationsFull } from "../../../shared/hooks/useInvestigations";

interface AuditEntry {
  timestamp: string;
  step: string;
  agent: string;
  processing_time_ms: number;
  confidence: number | null;
  status: string;
  investigation_id: string;
  severity: string;
  reason?: string;
  level?: string;
  auto_escalated?: boolean;
}

/** Agent color mapping for visual distinction. */
const agentColors: Record<string, string> = {
  Orchestrator: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  "L1 Triage": "text-green-400 bg-green-500/10 border-green-500/30",
  "Evidence Collector": "text-purple-400 bg-purple-500/10 border-purple-500/30",
  "MITRE Mapper": "text-red-400 bg-red-500/10 border-red-500/30",
  "Detection Agent": "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
  "Report Writer": "text-amber-400 bg-amber-500/10 border-amber-500/30",
  "Response Planner": "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  "Adversarial Validator": "text-pink-400 bg-pink-500/10 border-pink-500/30",
  "Threat Generator": "text-rose-400 bg-rose-500/10 border-rose-500/30",
  "Escalation Engine": "text-orange-400 bg-orange-500/10 border-orange-500/30",
  "Human Analyst": "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
};

function ConfidenceGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    score >= 0.7
      ? "text-green-400"
      : score >= 0.4
        ? "text-orange-400"
        : "text-red-400";
  const barColor =
    score >= 0.7
      ? "bg-green-500"
      : score >= 0.4
        ? "bg-orange-500"
        : "bg-red-500";

  return (
    <div className="flex items-center gap-1.5">
      <div className="h-2 w-20 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-500 ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-[10px] font-medium ${color}`}>{pct}%</span>
    </div>
  );
}

function AuditEntryRow({
  entry,
  isLast,
}: {
  entry: AuditEntry;
  isLast: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const colorClass =
    agentColors[entry.agent] || "text-gray-400 bg-white/5 border-white/10";

  return (
    <div className="relative flex gap-3">
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div
          className={cn(
            "flex h-6 w-6 shrink-0 items-center justify-center rounded-full",
            entry.status === "completed"
              ? "bg-green-500/20"
              : entry.status === "skipped"
                ? "bg-gray-500/20"
                : "bg-red-500/20",
          )}
        >
          {entry.status === "completed" ? (
            <CheckCircle2 size={12} className="text-green-400" />
          ) : (
            <XCircle size={12} className="text-red-400" />
          )}
        </div>
        {!isLast && (
          <div className="w-px flex-1 bg-white/10" />
        )}
      </div>

      {/* Entry content */}
      <div className="mb-3 flex-1">
        <div
          onClick={() => setExpanded(!expanded)}
          className="cursor-pointer rounded-lg border border-white/5 bg-white/[0.02] px-4 py-3 transition-all hover:border-white/10 hover:bg-white/[0.04]"
        >
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            {/* Agent badge */}
            <div
              className={`rounded-md border px-2 py-0.5 text-[11px] font-medium ${colorClass}`}
            >
              <div className="flex items-center gap-1">
                <Brain size={10} />
                {entry.agent}
              </div>
            </div>

            {/* Severity */}
            <span className={getSeverityBadgeClass(entry.severity)}>
              {entry.severity.toUpperCase()}
            </span>

            {/* Timing */}
            {entry.processing_time_ms != null && (
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Clock size={10} />
                <span>{entry.processing_time_ms.toFixed(0)}ms</span>
              </div>
            )}

            {/* Confidence gauge */}
            {entry.confidence != null && (
              <ConfidenceGauge score={entry.confidence} />
            )}

            {/* Timestamp */}
            <span className="ml-auto text-[10px] text-gray-500">
              {formatRelativeTime(entry.timestamp)}
            </span>

            {/* Expand icon */}
            {expanded ? (
              <ChevronUp size={12} className="text-gray-500" />
            ) : (
              <ChevronDown size={12} className="text-gray-500" />
            )}
          </div>

          {/* Investigation ID */}
          <div className="mt-1.5 flex items-center gap-2">
            <span className="font-mono text-[10px] text-gray-600">
              {entry.investigation_id}
            </span>
            {entry.level && (
              <span className="rounded bg-orange-500/20 px-1.5 py-0.5 text-[9px] font-medium text-orange-400">
                {entry.level}
              </span>
            )}
          </div>
        </div>

        {/* Expanded detail */}
        {expanded && (
          <div className="mt-1 rounded-lg border border-white/5 bg-white/[0.01] px-4 py-3 text-xs text-gray-400">
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <div>
                <span className="text-[10px] uppercase text-gray-600">Step</span>
                <p className="font-mono text-gray-300">{entry.step}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase text-gray-600">Status</span>
                <p className={entry.status === "completed" ? "text-green-400" : "text-red-400"}>
                  {entry.status}
                </p>
              </div>
              {entry.confidence != null && (
                <div>
                  <span className="text-[10px] uppercase text-gray-600">Confidence</span>
                  <p className="text-gray-300">{(entry.confidence * 100).toFixed(1)}%</p>
                </div>
              )}
              {entry.processing_time_ms != null && (
                <div>
                  <span className="text-[10px] uppercase text-gray-600">Processing Time</span>
                  <p className="text-gray-300">{entry.processing_time_ms.toFixed(1)}ms</p>
                </div>
              )}
              {entry.reason && (
                <div className="sm:col-span-2">
                  <span className="text-[10px] uppercase text-gray-600">Reason</span>
                  <p className="text-gray-300">{entry.reason}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function AuditTrailView() {
  const [agentFilter, setAgentFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: investigations, isLoading } = useInvestigationsFull(10_000);

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
    entries.sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );
    return entries;
  }, [investigations]);

  /** Apply all filters. */
  const filteredEntries = useMemo(() => {
    let result = allEntries;

    if (agentFilter !== "all") {
      result = result.filter((e) => e.agent === agentFilter);
    }

    if (severityFilter !== "all") {
      result = result.filter((e) => e.severity === severityFilter);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (e) =>
          e.agent.toLowerCase().includes(q) ||
          e.investigation_id.toLowerCase().includes(q) ||
          e.step.toLowerCase().includes(q) ||
          (e.reason && e.reason.toLowerCase().includes(q)),
      );
    }

    return result;
  }, [allEntries, agentFilter, severityFilter, searchQuery]);

  const agents = [
    "all",
    "Orchestrator",
    "L1 Triage",
    "Evidence Collector",
    "MITRE Mapper",
    "Detection Agent",
    "Report Writer",
    "Response Planner",
    "Adversarial Validator",
    "Threat Generator",
    "Escalation Engine",
    "Human Analyst",
  ];

  const severities = ["all", "critical", "high", "medium", "low", "info"];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Trail</h1>
          <p className="mt-1 text-sm text-gray-400">
            Complete log of all agent actions across investigations
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <div className="flex items-center gap-1.5">
            <Shield size={14} />
            <span>{investigations?.length ?? 0} investigations</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ClipboardList size={14} />
            <span>{filteredEntries.length} entries</span>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search
          size={14}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
        />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by agent, investigation ID, or step..."
          className="w-full rounded-lg border border-white/10 bg-white/5 py-2 pl-9 pr-3 text-xs text-gray-300 placeholder-gray-600 outline-none transition-colors focus:border-cyan-500/30 focus:bg-white/[0.07]"
        />
      </div>

      {/* Filter Bars */}
      <div className="space-y-2">
        {/* Agent Filter */}
        <div className="flex flex-wrap items-center gap-1.5">
          <Filter size={12} className="text-gray-500" />
          <span className="text-[10px] uppercase tracking-wider text-gray-600 mr-1">Agent:</span>
          {agents.map((agent) => (
            <button
              key={agent}
              onClick={() => setAgentFilter(agent)}
              className={cn(
                "rounded-md border px-2 py-0.5 text-[11px] font-medium transition-all",
                agentFilter === agent
                  ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
                  : "border-white/10 bg-white/5 text-gray-500 hover:border-white/20 hover:text-gray-400",
              )}
            >
              {agent === "all" ? "All" : agent}
            </button>
          ))}
        </div>

        {/* Severity Filter */}
        <div className="flex flex-wrap items-center gap-1.5">
          <Filter size={12} className="text-gray-500" />
          <span className="text-[10px] uppercase tracking-wider text-gray-600 mr-1">Severity:</span>
          {severities.map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={cn(
                "rounded-md border px-2 py-0.5 text-[11px] font-medium transition-all",
                severityFilter === sev
                  ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
                  : "border-white/10 bg-white/5 text-gray-500 hover:border-white/20 hover:text-gray-400",
              )}
            >
              {sev === "all" ? "All" : sev.charAt(0).toUpperCase() + sev.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Audit entries with timeline */}
      <div>
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-white/5" />
            ))}
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="glass-card flex flex-col items-center py-16 text-center">
            <ClipboardList size={48} className="mb-4 text-gray-600" />
            <p className="text-sm text-gray-500">No audit entries found</p>
            <p className="mt-1 text-xs text-gray-600">
              {searchQuery || agentFilter !== "all" || severityFilter !== "all"
                ? "Try adjusting your filters"
                : "Run investigations to populate the audit trail"}
            </p>
          </div>
        ) : (
          filteredEntries.map((entry, i) => (
            <AuditEntryRow
              key={`${entry.investigation_id}-${entry.step}-${i}`}
              entry={entry}
              isLast={i === filteredEntries.length - 1}
            />
          ))
        )}
      </div>
    </div>
  );
}
