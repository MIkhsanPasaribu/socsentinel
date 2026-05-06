/** SOCsentinel — Investigation feature — Real-time SSE pipeline viewer. */

import { useState } from "react";
import {
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Brain,
  Eye,
  FileText,
  Target,
  Zap,
  Loader2,
  Radar,
  ShieldCheck,
} from "lucide-react";
import { cn, getSeverityBadgeClass } from "../../../shared/lib/utils";
import { ConfidenceBar } from "../../../shared/components/ConfidenceGauge";
import { DecisionPanel } from "./DecisionPanel";
import {
  useSSEInvestigation,
  type AgentStep,
} from "../hooks/useSSEInvestigation";
import { env } from "../../../core/config/env";
import { ALERT_SCENARIOS } from "../../../core/constants/scenarios";
import { useFormValidation } from "../../../shared/hooks/useFormValidation";
import { scenarioSchema } from "../../../shared/lib/validation";
import { useInvestigationList } from "../../../shared/hooks/useInvestigations";

/** Agent step visualization for the SSE pipeline. */
function AgentStepRow({ agent }: { agent: AgentStep }) {
  const icons: Record<string, typeof Brain> = {
    orchestrator: Shield,
    l1_triage: Eye,
    evidence_collector: Search,
    mitre_mapper: Target,
    threat_generator: Radar,
    detection: ShieldCheck,
    report_writer: FileText,
    response_planner: Zap,
    validator: CheckCircle2,
  };
  const Icon = icons[agent.step] || Brain;

  const statusStyles = {
    pending: {
      border: "border-white/10",
      bg: "bg-white/[0.02]",
      iconBg: "bg-white/5",
      iconColor: "text-gray-600",
      label: "Pending",
      labelColor: "text-gray-600",
    },
    running: {
      border: "border-cyan-500/40 glow-cyan",
      bg: "bg-cyan-500/5",
      iconBg: "bg-cyan-500/10",
      iconColor: "text-cyan-400 animate-pulse",
      label: "Processing...",
      labelColor: "text-cyan-400",
    },
    completed: {
      border: "border-green-500/30",
      bg: "bg-green-500/5",
      iconBg: "bg-green-500/10",
      iconColor: "text-green-400",
      label: "Completed",
      labelColor: "text-green-400",
    },
  };

  const s = statusStyles[agent.status];

  return (
    <div
      className={cn(
        "flex items-center gap-4 rounded-xl border px-4 py-3 transition-all duration-500",
        s.border,
        s.bg,
      )}
    >
      {/* Icon */}
      <div className={cn("rounded-lg p-2.5", s.iconBg)}>
        <Icon size={18} className={s.iconColor} />
      </div>

      {/* Agent info */}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-semibold text-white">{agent.name}</p>
          <span className="rounded-md bg-white/5 px-1.5 py-0.5 font-mono text-[9px] text-gray-500">
            {agent.model}
          </span>
        </div>
        <p className="text-xs text-gray-500">{agent.role}</p>
      </div>

      {/* Status */}
      <div className="flex items-center gap-3">
        {agent.status === "running" && (
          <Loader2 size={14} className="animate-spin text-cyan-400" />
        )}
        {agent.status === "completed" && agent.confidence != null && (
          <ConfidenceBar score={agent.confidence} />
        )}
        {agent.status === "completed" && agent.processing_time_ms != null && (
          <span className="flex items-center gap-1 text-xs text-gray-400">
            <Clock size={12} />
            {agent.processing_time_ms.toFixed(0)}ms
          </span>
        )}
        <div className="flex items-center gap-1.5">
          {agent.status === "completed" ? (
            <CheckCircle2 size={14} className="text-green-400" />
          ) : agent.status === "running" ? (
            <span className="agent-active" />
          ) : (
            <span className="h-2 w-2 rounded-full bg-gray-700" />
          )}
          <span className={cn("text-xs font-medium", s.labelColor)}>
            {s.label}
          </span>
        </div>
      </div>
    </div>
  );
}

export function InvestigationsView() {
  const {
    state: sseState,
    startInvestigation,
    reset,
  } = useSSEInvestigation(env.apiUrl);
  const [selectedScenario, setSelectedScenario] = useState("brute_force");
  const { errors, validate, clearErrors } = useFormValidation(scenarioSchema);

  const { data: investigations = [] } = useInvestigationList(5000);
  const completedCount = sseState.agents.filter(
    (a) => a.status === "completed",
  ).length;
  const avgConfidence =
    sseState.agents
      .filter((a) => a.confidence != null)
      .reduce((sum, a) => sum + (a.confidence || 0), 0) /
      (sseState.agents.filter((a) => a.confidence != null).length || 1) || null;

  const scenarios = ALERT_SCENARIOS;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Investigations</h1>
          <p className="mt-1 text-sm text-gray-400">
            Real-time multi-agent pipeline with SSE streaming
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedScenario}
            onChange={(e) => {
              setSelectedScenario(e.target.value);
              if (Object.keys(errors).length) {
                clearErrors();
              }
            }}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-300 outline-none focus:border-cyan-500/30"
          >
            {scenarios.map((s) => (
              <option key={s} value={s} className="bg-navy-900">
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </select>
          <button
            onClick={() => {
              if (!validate(selectedScenario)) {
                return;
              }
              reset();
              setTimeout(
                () => startInvestigation(selectedScenario, false),
                100,
              );
            }}
            disabled={
              sseState.phase === "streaming" || sseState.phase === "connecting"
            }
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 text-sm font-medium text-white transition-all hover:shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50"
          >
            {sseState.phase === "streaming" ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Streaming...
              </>
            ) : (
              <>
                <Zap size={16} /> Stream Investigation
              </>
            )}
          </button>
          {errors._global && (
            <p className="text-xs text-orange-300">{errors._global}</p>
          )}
        </div>
      </div>

      {/* SSE Pipeline Viewer */}
      {sseState.phase !== "idle" && (
        <div className="space-y-4">
          {/* Pipeline header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {sseState.severity && (
                <span className={getSeverityBadgeClass(sseState.severity)}>
                  {sseState.severity.toUpperCase()}
                </span>
              )}
              <span className="font-mono text-xs text-gray-500">
                {sseState.investigationId}
              </span>
              {sseState.ruleName && (
                <span className="text-xs text-gray-400">
                  {sseState.ruleName}
                </span>
              )}
            </div>

            {/* Progress */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                {sseState.agents.map((a, i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-2 w-8 rounded-full transition-all duration-500",
                      a.status === "completed"
                        ? "bg-green-500"
                        : a.status === "running"
                          ? "bg-cyan-400 animate-pulse"
                          : "bg-white/10",
                    )}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-400">
                {completedCount}/{sseState.agents.length} agents
              </span>
            </div>
          </div>

          {/* Agent steps */}
          <div className="space-y-2">
            {sseState.agents.map((agent) => (
              <AgentStepRow key={agent.index} agent={agent} />
            ))}
          </div>

          {/* Pipeline result */}
          {sseState.phase === "completed" && sseState.totalTimeMs && (
            <div className="flex items-center justify-between rounded-xl border border-green-500/20 bg-green-500/5 px-4 py-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={18} className="text-green-400" />
                <span className="text-sm font-medium text-green-400">
                  Investigation Complete
                </span>
              </div>
              <span className="text-sm font-bold text-green-400">
                {sseState.totalTimeMs.toFixed(0)}ms total
              </span>
            </div>
          )}

          {sseState.phase === "failed" && (
            <div className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3">
              <XCircle size={18} className="text-red-400" />
              <span className="text-sm font-medium text-red-400">
                Pipeline Failed: {sseState.error}
              </span>
            </div>
          )}

          {/* Human-in-the-Loop Decision Panel */}
          {sseState.phase === "completed" && sseState.investigationId && (
            <DecisionPanel
              investigationId={sseState.investigationId}
              severity={sseState.severity}
              avgConfidence={avgConfidence}
            />
          )}
        </div>
      )}

      {/* Past Investigations List */}
      {investigations.length > 0 && (
        <div>
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-400">
            <Clock size={14} /> Past Investigations ({investigations.length})
          </h2>
          <div className="space-y-2">
            {investigations.slice(0, 10).map((inv) => (
              <div
                key={inv.investigation_id}
                className="flex items-center gap-4 rounded-lg border border-white/5 bg-white/[0.02] px-4 py-2.5 text-xs"
              >
                <span className={getSeverityBadgeClass(inv.severity)}>
                  {inv.severity.toUpperCase()}
                </span>
                <span className="font-mono text-gray-400">
                  {inv.investigation_id}
                </span>
                <span className="flex items-center gap-1 text-gray-500">
                  <Clock size={12} />{" "}
                  {inv.processing_time_ms?.toFixed(0) || "?"}ms
                </span>
                <span className="ml-auto flex items-center gap-1 text-green-400">
                  <CheckCircle2 size={12} /> {inv.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {sseState.phase === "idle" && investigations.length === 0 && (
        <div className="glass-card flex flex-col items-center py-16 text-center">
          <Search size={48} className="mb-4 text-gray-600" />
          <p className="text-sm text-gray-500">No investigations yet</p>
          <p className="mt-1 text-xs text-gray-600">
            Select a scenario and click "Stream Investigation" to watch agents
            work in real-time
          </p>
        </div>
      )}
    </div>
  );
}
