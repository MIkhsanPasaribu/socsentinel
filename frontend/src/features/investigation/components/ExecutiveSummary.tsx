/** SOCsentinel — Executive Summary Banner — Post-investigation verdict at a glance. */

import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Clock,
  Crosshair,
} from "lucide-react";
import { cn } from "../../../shared/lib/utils";
import type { AgentStep } from "../hooks/useSSEInvestigation";

interface ExecutiveSummaryProps {
  agents: AgentStep[];
  totalTimeMs: number;
  severity: string | null;
  ruleName: string | null;
}

const KILL_CHAIN_PHASES = [
  "Reconnaissance",
  "Initial Access",
  "Execution",
  "Persistence",
  "Privilege Escalation",
  "Lateral Movement",
  "Collection",
  "Exfiltration",
  "Impact",
];

export function ExecutiveSummary({
  agents,
  totalTimeMs,
  severity,
  ruleName,
}: ExecutiveSummaryProps) {
  const triageAgent = agents.find((a) => a.name === "L1 Triage");
  const classification = triageAgent?.classification || "investigate";

  const isFalsePositive = classification === "close";
  const isEscalation = classification === "escalate";

  const verdictConfig = isFalsePositive
    ? {
        label: "False Positive",
        color: "text-green-400",
        border: "border-green-500/30",
        bg: "from-green-500/5 to-emerald-500/5",
        icon: ShieldCheck,
        description: "AI triage determined this alert is benign",
      }
    : isEscalation
    ? {
        label: "Escalation Required",
        color: "text-orange-400",
        border: "border-orange-500/30",
        bg: "from-orange-500/5 to-red-500/5",
        icon: ShieldAlert,
        description: "Alert requires L2/L3 analyst review",
      }
    : {
        label: "True Positive",
        color: "text-red-400",
        border: "border-red-500/30",
        bg: "from-red-500/5 to-pink-500/5",
        icon: ShieldX,
        description: "Confirmed threat — response actions recommended",
      };

  const VerdictIcon = verdictConfig.icon;

  const completedAgents = agents.filter((a) => a.status === "completed");
  const avgConfidence = completedAgents.length > 0
    ? completedAgents.reduce((sum, a) => sum + (a.confidence || 0), 0) / completedAgents.length
    : 0;

  const manualTimeMinutes = severity === "critical" || severity === "high" ? 45 : 25;
  const timeSavedMinutes = manualTimeMinutes - (totalTimeMs / 60000);

  const detectionAgent = agents.find((a) => a.name === "Detection");
  const responseAgent = agents.find((a) => a.name === "Response Planner");

  const killChainIndex = severity === "critical" ? 7 : severity === "high" ? 5 : severity === "medium" ? 3 : 1;

  return (
    <div className={cn(
      "animate-slide-up rounded-xl border bg-gradient-to-br p-4 sm:p-5",
      verdictConfig.border,
      verdictConfig.bg
    )}>
      {/* Verdict Header */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className={cn("rounded-lg p-2", isFalsePositive ? "bg-green-500/10" : isEscalation ? "bg-orange-500/10" : "bg-red-500/10")}>
            <VerdictIcon size={22} className={verdictConfig.color} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className={cn("text-base font-bold", verdictConfig.color)}>{verdictConfig.label}</h3>
              <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-medium text-gray-400">
                {Math.round(avgConfidence * 100)}% confidence
              </span>
            </div>
            <p className="text-xs text-gray-400">{verdictConfig.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-xs text-gray-500">Time Saved</p>
            <p className="text-lg font-bold text-cyan-400">{timeSavedMinutes.toFixed(0)} min</p>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="text-right">
            <p className="text-xs text-gray-500">AI Pipeline</p>
            <p className="text-lg font-bold text-white">{(totalTimeMs / 1000).toFixed(1)}s</p>
          </div>
        </div>
      </div>

      {/* Kill Chain Progress */}
      <div className="mb-4">
        <div className="mb-1.5 flex items-center gap-1.5">
          <Crosshair size={12} className="text-gray-500" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-500">Kill Chain Progress</span>
        </div>
        <div className="flex gap-1">
          {KILL_CHAIN_PHASES.map((phase, i) => (
            <div key={phase} className="flex-1 group relative">
              <div
                className={cn(
                  "h-2 rounded-full transition-all",
                  i <= killChainIndex
                    ? i <= 2 ? "bg-yellow-500" : i <= 5 ? "bg-orange-500" : "bg-red-500"
                    : "bg-white/10"
                )}
              />
              <div className="absolute left-1/2 top-4 hidden -translate-x-1/2 whitespace-nowrap rounded bg-navy-800 px-1.5 py-0.5 text-[8px] text-gray-400 group-hover:block">
                {phase}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-1 flex justify-between text-[8px] text-gray-600">
          <span>Recon</span>
          <span>Impact</span>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div className="rounded-lg bg-white/[0.03] px-3 py-2 text-center">
          <p className="text-[10px] text-gray-500">Agents Completed</p>
          <p className="text-sm font-bold text-white">{completedAgents.length}/{agents.length}</p>
        </div>
        <div className="rounded-lg bg-white/[0.03] px-3 py-2 text-center">
          <p className="text-[10px] text-gray-500">Rule</p>
          <p className="truncate text-sm font-bold text-white">{ruleName || "—"}</p>
        </div>
        <div className="rounded-lg bg-white/[0.03] px-3 py-2 text-center">
          <p className="text-[10px] text-gray-500">Detection</p>
          <p className="text-sm font-bold text-white">
            {detectionAgent?.status === "completed" ? "Sigma Rules Generated" : "—"}
          </p>
        </div>
        <div className="rounded-lg bg-white/[0.03] px-3 py-2 text-center">
          <p className="text-[10px] text-gray-500">Response Plan</p>
          <p className="text-sm font-bold text-white">
            {responseAgent?.status === "completed" ? "Playbook Ready" : "—"}
          </p>
        </div>
      </div>

      {/* Manual vs AI Comparison */}
      <div className="mt-3 flex items-center gap-2 rounded-lg bg-white/[0.02] px-3 py-2">
        <Clock size={14} className="shrink-0 text-gray-500" />
        <p className="text-[11px] text-gray-400">
          This investigation would take a human analyst <span className="font-bold text-white">~{manualTimeMinutes} minutes</span>
          {" → "}SOCsentinel completed it in <span className="font-bold text-cyan-400">{(totalTimeMs / 1000).toFixed(1)} seconds</span>
          {" ("}
          <span className="font-bold text-green-400">{Math.round(manualTimeMinutes * 60000 / totalTimeMs)}x faster</span>
          {")"}
        </p>
      </div>
    </div>
  );
}
