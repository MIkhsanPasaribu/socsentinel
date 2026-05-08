/** SOCsentinel — Agent Collaboration Graph — Circular network visualization. */

import { useMemo } from "react";
import type { AgentStep } from "../hooks/useSSEInvestigation";

interface AgentCollaborationGraphProps {
  agents: AgentStep[];
}

const AGENT_COLORS: Record<string, string> = {
  Orchestrator: "#22d3ee",
  "L1 Triage": "#3b82f6",
  "Evidence Collector": "#8b5cf6",
  "MITRE Mapper": "#ec4899",
  "Report Writer": "#f97316",
  Detection: "#eab308",
  "Response Planner": "#22c55e",
  Validator: "#14b8a6",
  "Threat Generator": "#6366f1",
};

const SHORT_LABELS: Record<string, string> = {
  Orchestrator: "ORCH",
  "L1 Triage": "TRIAGE",
  "Evidence Collector": "EVID",
  "MITRE Mapper": "MITRE",
  "Report Writer": "REPORT",
  Detection: "DETECT",
  "Response Planner": "RESP",
  Validator: "VALID",
  "Threat Generator": "THREAT",
};

export function AgentCollaborationGraph({ agents }: AgentCollaborationGraphProps) {
  const centerX = 160;
  const centerY = 160;
  const radius = 120;

  const nodes = useMemo(() => {
    return agents.map((agent, i) => {
      const angle = (2 * Math.PI * i) / agents.length - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      return { ...agent, x, y, angle };
    });
  }, [agents]);

  const activeIndex = agents.findIndex((a) => a.status === "running");
  const completedCount = agents.filter((a) => a.status === "completed").length;

  return (
    <div className="glass-card">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          Agent Collaboration Network
        </h4>
        <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-gray-500">
          {completedCount}/{agents.length} complete
        </span>
      </div>

      <div className="flex justify-center">
        <svg width="320" height="320" viewBox="0 0 320 320" className="max-w-full">
          {/* Connection lines between sequential agents */}
          {nodes.map((node, i) => {
            if (i === nodes.length - 1) return null;
            const next = nodes[i + 1];
            const isActive = node.status === "completed" && next.status !== "pending";
            const isCompleted = node.status === "completed" && next.status === "completed";
            return (
              <line
                key={`line-${i}`}
                x1={node.x}
                y1={node.y}
                x2={next.x}
                y2={next.y}
                stroke={isCompleted ? "#22d3ee" : isActive ? "#22d3ee" : "#1e293b"}
                strokeWidth={isCompleted ? 2 : 1}
                strokeDasharray={isActive && !isCompleted ? "4 4" : "none"}
                strokeOpacity={isCompleted ? 0.6 : isActive ? 0.8 : 0.3}
              >
                {isActive && !isCompleted && (
                  <animate
                    attributeName="stroke-dashoffset"
                    from="0"
                    to="-8"
                    dur="0.6s"
                    repeatCount="indefinite"
                  />
                )}
              </line>
            );
          })}

          {/* Data flow arrows — animated particles on active connections */}
          {nodes.map((node, i) => {
            if (i >= nodes.length - 1) return null;
            const next = nodes[i + 1];
            if (node.status !== "completed" || next.status === "pending") return null;
            return (
              <circle key={`particle-${i}`} r="3" fill="#22d3ee" opacity={0.8}>
                <animateMotion
                  dur="1.5s"
                  repeatCount="indefinite"
                  path={`M${node.x},${node.y} L${next.x},${next.y}`}
                />
              </circle>
            );
          })}

          {/* Center hub */}
          <circle cx={centerX} cy={centerY} r={28} fill="rgba(34,211,238,0.05)" stroke="#22d3ee" strokeWidth={1} strokeOpacity={0.3} />
          <text x={centerX} y={centerY - 6} textAnchor="middle" className="fill-cyan-400 text-[9px] font-bold">SOC</text>
          <text x={centerX} y={centerY + 6} textAnchor="middle" className="fill-cyan-400 text-[9px] font-bold">sentinel</text>

          {/* Agent nodes */}
          {nodes.map((node) => {
            const color = AGENT_COLORS[node.name] || "#6b7280";
            const isRunning = node.status === "running";
            const isCompleted = node.status === "completed";
            const nodeRadius = isRunning ? 24 : 20;

            return (
              <g key={node.index}>
                {/* Pulse ring for active agent */}
                {isRunning && (
                  <circle cx={node.x} cy={node.y} r={nodeRadius + 4} fill="none" stroke={color} strokeWidth={2} opacity={0.5}>
                    <animate attributeName="r" from={String(nodeRadius + 2)} to={String(nodeRadius + 12)} dur="1.2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.6" to="0" dur="1.2s" repeatCount="indefinite" />
                  </circle>
                )}

                {/* Node circle */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={nodeRadius}
                  fill={isCompleted ? `${color}22` : isRunning ? `${color}33` : "#0f172a"}
                  stroke={isCompleted ? color : isRunning ? color : "#334155"}
                  strokeWidth={isRunning ? 2.5 : isCompleted ? 2 : 1}
                />

                {/* Agent label */}
                <text
                  x={node.x}
                  y={node.y - 3}
                  textAnchor="middle"
                  fill={isCompleted || isRunning ? color : "#6b7280"}
                  className="text-[8px] font-bold"
                >
                  {SHORT_LABELS[node.name] || node.name.slice(0, 4).toUpperCase()}
                </text>

                {/* Timing or status */}
                <text
                  x={node.x}
                  y={node.y + 8}
                  textAnchor="middle"
                  fill={isCompleted ? "#9ca3af" : isRunning ? color : "#475569"}
                  className="text-[7px]"
                >
                  {isCompleted && node.processing_time_ms
                    ? `${node.processing_time_ms}ms`
                    : isRunning
                    ? "..."
                    : "idle"}
                </text>

                {/* Confidence badge for completed */}
                {isCompleted && node.confidence != null && (
                  <g>
                    <rect
                      x={node.x + nodeRadius - 6}
                      y={node.y - nodeRadius - 2}
                      width={20}
                      height={12}
                      rx={6}
                      fill={color}
                      opacity={0.2}
                    />
                    <text
                      x={node.x + nodeRadius + 4}
                      y={node.y - nodeRadius + 7}
                      textAnchor="middle"
                      fill={color}
                      className="text-[7px] font-bold"
                    >
                      {Math.round(node.confidence * 100)}%
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Active agent label */}
      {activeIndex >= 0 && (
        <div className="mt-2 flex items-center justify-center gap-2">
          <span className="agent-active" />
          <span className="text-xs text-cyan-400">
            {agents[activeIndex].name} processing...
          </span>
        </div>
      )}
    </div>
  );
}
