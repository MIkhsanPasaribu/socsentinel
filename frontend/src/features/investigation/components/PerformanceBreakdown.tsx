/** SOCsentinel — Per-agent performance breakdown after investigation completes.
 *
 * Shows a horizontal bar chart of per-agent inference timing,
 * total pipeline time, tokens/sec estimate, and GPU info.
 */

import { Cpu, Clock, Zap } from "lucide-react";
import { cn } from "../../../shared/lib/utils";
import type { AgentStep } from "../hooks/useSSEInvestigation";

interface PerformanceBreakdownProps {
  /** Completed agent steps with timing data. */
  agents: AgentStep[];
  /** Total pipeline time in ms. */
  totalTimeMs: number;
}

/** Agent color mapping for visual distinction in the bar chart. */
const agentBarColors: Record<string, string> = {
  orchestrator: "from-blue-500 to-blue-400",
  l1_triage: "from-green-500 to-green-400",
  evidence_collector: "from-purple-500 to-purple-400",
  mitre_mapper: "from-red-500 to-red-400",
  threat_generator: "from-pink-500 to-pink-400",
  detection: "from-yellow-500 to-yellow-400",
  report_writer: "from-amber-500 to-amber-400",
  response_planner: "from-emerald-500 to-emerald-400",
  validator: "from-cyan-500 to-cyan-400",
};

export function PerformanceBreakdown({
  agents,
  totalTimeMs,
}: PerformanceBreakdownProps) {
  const completedAgents = agents.filter(
    (a) => a.status === "completed" && a.processing_time_ms != null,
  );

  if (completedAgents.length === 0) return null;

  const maxTime = Math.max(
    ...completedAgents.map((a) => a.processing_time_ms || 0),
  );

  const totalTokensEstimate = completedAgents.length * 450;
  const totalTimeSec = totalTimeMs / 1000;
  const tokensPerSec =
    totalTimeSec > 0 ? Math.round(totalTokensEstimate / totalTimeSec) : 0;

  return (
    <div className="rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 to-blue-600/5 p-4 sm:p-6">
      <div className="mb-4 flex items-center gap-2">
        <Cpu size={18} className="text-cyan-400" />
        <h3 className="text-sm font-semibold text-white">
          Pipeline Performance (AMD MI300X)
        </h3>
      </div>

      {/* Agent Timing Bars */}
      <div className="space-y-2">
        {completedAgents.map((agent) => {
          const timeMs = agent.processing_time_ms || 0;
          const barWidth = maxTime > 0 ? (timeMs / maxTime) * 100 : 0;
          const gradient =
            agentBarColors[agent.step] || "from-gray-500 to-gray-400";

          return (
            <div key={agent.step} className="flex items-center gap-3">
              <span className="w-28 truncate text-right text-xs text-gray-400">
                {agent.name}
              </span>
              <div className="flex-1">
                <div className="h-4 overflow-hidden rounded-full bg-white/5">
                  <div
                    className={cn(
                      "h-full rounded-full bg-gradient-to-r transition-all duration-700",
                      gradient,
                    )}
                    style={{ width: `${Math.max(barWidth, 4)}%` }}
                  />
                </div>
              </div>
              <span className="w-16 text-right font-mono text-xs text-gray-400">
                {timeMs.toFixed(0)}ms
              </span>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-lg bg-white/5 p-2.5 text-center">
          <div className="flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-gray-500">
            <Clock size={10} />
            Total
          </div>
          <p className="mt-1 text-lg font-bold text-cyan-400">
            {totalTimeMs.toFixed(0)}ms
          </p>
        </div>
        <div className="rounded-lg bg-white/5 p-2.5 text-center">
          <div className="flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-gray-500">
            <Zap size={10} />
            Tokens/sec
          </div>
          <p className="mt-1 text-lg font-bold text-green-400">
            ~{tokensPerSec}
          </p>
        </div>
        <div className="rounded-lg bg-white/5 p-2.5 text-center">
          <p className="text-[10px] uppercase tracking-wider text-gray-500">
            Agents
          </p>
          <p className="mt-1 text-lg font-bold text-white">
            {completedAgents.length}
          </p>
        </div>
        <div className="rounded-lg bg-white/5 p-2.5 text-center">
          <p className="text-[10px] uppercase tracking-wider text-gray-500">
            GPU
          </p>
          <p className="mt-1 text-lg font-bold text-white">MI300X</p>
          <p className="text-[10px] text-gray-500">192GB HBM3</p>
        </div>
      </div>
    </div>
  );
}
