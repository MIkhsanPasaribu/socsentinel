/** SOCsentinel — Pipeline Flow Visualization component.
 *
 * Shows a horizontal flow diagram of the 9-agent pipeline with
 * status indicators and processing times for each agent.
 */

import {
  Shield,
  Eye,
  Search,
  Target,
  Radar,
  ShieldCheck,
  FileText,
  Zap,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import { cn } from "../../../shared/lib/utils";

interface PipelineNode {
  id: string;
  name: string;
  icon: React.ReactNode;
  status: "completed" | "active" | "pending" | "skipped";
  timeMs?: number;
}

interface PipelineFlowDiagramProps {
  /** Current pipeline step (agent step ID). */
  currentStep?: string;
  /** Completed steps with timing data. */
  completedSteps?: Array<{ step: string; processing_time_ms?: number }>;
}

/** All pipeline agents in execution order. */
const PIPELINE_AGENTS = [
  { id: "orchestrator", name: "Orchestrator", icon: <Shield size={14} /> },
  { id: "l1_triage", name: "L1 Triage", icon: <Eye size={14} /> },
  { id: "evidence_collector", name: "Evidence", icon: <Search size={14} /> },
  { id: "mitre_mapper", name: "MITRE", icon: <Target size={14} /> },
  { id: "threat_generator", name: "Threat Gen", icon: <Radar size={14} /> },
  { id: "detection", name: "Detection", icon: <ShieldCheck size={14} /> },
  { id: "report_writer", name: "Report", icon: <FileText size={14} /> },
  { id: "response_planner", name: "Response", icon: <Zap size={14} /> },
  { id: "validator", name: "Validator", icon: <CheckCircle2 size={14} /> },
];

export function PipelineFlowDiagram({
  currentStep,
  completedSteps = [],
}: PipelineFlowDiagramProps) {
  const completedIds = new Set(completedSteps.map((s) => s.step));

  const nodes: PipelineNode[] = PIPELINE_AGENTS.map((agent) => {
    let status: PipelineNode["status"] = "pending";
    if (completedIds.has(agent.id)) {
      status = "completed";
    } else if (agent.id === currentStep) {
      status = "active";
    }

    const stepData = completedSteps.find((s) => s.step === agent.id);
    return {
      ...agent,
      status,
      timeMs: stepData?.processing_time_ms,
    };
  });

  return (
    <div className="glass-card overflow-x-auto">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
          Pipeline Flow
        </h4>
        <span className="text-[10px] text-gray-600 sm:hidden">&larr; scroll &rarr;</span>
      </div>
      <div className="flex items-center gap-1" style={{ minWidth: "max-content" }}>
        {nodes.map((node, i) => (
          <div key={node.id} className="flex items-center">
            {/* Node */}
            <div
              className={cn(
                "flex flex-col items-center gap-1 rounded-lg border px-3 py-2 transition-all",
                node.status === "completed" &&
                  "border-green-500/30 bg-green-500/10",
                node.status === "active" &&
                  "border-cyan-500/50 bg-cyan-500/10 ring-1 ring-cyan-500/30 animate-pulse",
                node.status === "pending" &&
                  "border-white/10 bg-white/[0.02]",
                node.status === "skipped" &&
                  "border-gray-700/30 bg-gray-800/20 opacity-50"
              )}
            >
              <div
                className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-full",
                  node.status === "completed" && "bg-green-500/20 text-green-400",
                  node.status === "active" && "bg-cyan-500/20 text-cyan-400",
                  node.status === "pending" && "bg-white/10 text-gray-500",
                  node.status === "skipped" && "bg-gray-700/20 text-gray-600"
                )}
              >
                {node.icon}
              </div>
              <span
                className={cn(
                  "text-[9px] font-medium whitespace-nowrap",
                  node.status === "completed" && "text-green-400",
                  node.status === "active" && "text-cyan-400",
                  node.status === "pending" && "text-gray-500",
                  node.status === "skipped" && "text-gray-600"
                )}
              >
                {node.name}
              </span>
              {node.timeMs !== undefined && (
                <span className="text-[8px] font-mono text-gray-500">
                  {node.timeMs.toFixed(0)}ms
                </span>
              )}
            </div>

            {/* Arrow connector */}
            {i < nodes.length - 1 && (
              <ChevronRight
                size={12}
                className={cn(
                  "mx-0.5 shrink-0",
                  node.status === "completed" ? "text-green-500/50" : "text-gray-700"
                )}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
