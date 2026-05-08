/** SOCsentinel — Qwen3 Thinking Mode Panel.
 *
 * Shows chain-of-thought reasoning from the AI agents.
 * Displays as an expandable dark code block per agent step.
 */

import { useState } from "react";
import { Brain, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { cn } from "../../../shared/lib/utils";
import type { AgentStep } from "../hooks/useSSEInvestigation";

interface ThinkingPanelProps {
  /** All agent steps (may include thinking_content). */
  agents: AgentStep[];
}

function ThinkingEntry({ agent }: { agent: AgentStep }) {
  const [expanded, setExpanded] = useState(true);

  if (!agent.thinking_content) return null;

  return (
    <div className="overflow-hidden rounded-lg border border-purple-500/20 bg-black/40">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between border-b border-purple-500/20 bg-purple-500/10 px-3 py-2 text-left transition-colors hover:bg-purple-500/15"
      >
        <div className="flex items-center gap-2">
          <Brain size={14} className="text-purple-400" />
          <span className="text-xs font-medium text-purple-300">
            {agent.name}
          </span>
          <span className="rounded bg-purple-500/20 px-1.5 py-0.5 text-[9px] font-medium text-purple-400">
            CoT
          </span>
          {agent.processing_time_ms != null && (
            <span className="text-[10px] text-gray-500">
              {agent.processing_time_ms.toFixed(0)}ms
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp size={14} className="text-gray-500" />
        ) : (
          <ChevronDown size={14} className="text-gray-500" />
        )}
      </button>

      {/* Thinking content */}
      {expanded && (
        <pre className="max-h-48 overflow-auto whitespace-pre-wrap p-3 font-mono text-xs leading-relaxed text-purple-200/80">
          {agent.thinking_content}
        </pre>
      )}
    </div>
  );
}

export function ThinkingPanel({ agents }: ThinkingPanelProps) {
  const agentsWithThinking = agents.filter((a) => a.thinking_content);

  if (agentsWithThinking.length === 0) return null;

  return (
    <div className="rounded-xl border border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-indigo-600/5 p-4 sm:p-6">
      <div className="mb-4 flex items-center gap-2">
        <Sparkles size={18} className="text-purple-400" />
        <h3 className="text-sm font-semibold text-white">
          AI Reasoning (Chain-of-Thought)
        </h3>
        <span className="rounded-full bg-purple-500/10 px-2.5 py-0.5 text-xs font-medium text-purple-400">
          Qwen3 Thinking Mode
        </span>
      </div>

      <div className="space-y-2">
        {agentsWithThinking.map((agent) => (
          <ThinkingEntry key={agent.step} agent={agent} />
        ))}
      </div>
    </div>
  );
}

/** Toggle switch for enabling/disabling thinking mode. */
export function ThinkingModeToggle({
  enabled,
  onToggle,
  loading,
}: {
  enabled: boolean;
  onToggle: () => void;
  loading?: boolean;
}) {
  return (
    <button
      onClick={onToggle}
      disabled={loading}
      className={cn(
        "flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-all",
        enabled
          ? "border-purple-500/30 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20"
          : "border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-gray-300",
        loading && "opacity-50",
      )}
      title={enabled ? "Disable AI reasoning display" : "Enable AI reasoning display"}
    >
      <Brain size={14} />
      <span className="hidden sm:inline">Thinking</span>
      <div
        className={cn(
          "relative h-4 w-7 rounded-full transition-colors",
          enabled ? "bg-purple-500" : "bg-gray-600",
        )}
      >
        <div
          className={cn(
            "absolute top-0.5 h-3 w-3 rounded-full bg-white transition-transform",
            enabled ? "translate-x-3.5" : "translate-x-0.5",
          )}
        />
      </div>
    </button>
  );
}
