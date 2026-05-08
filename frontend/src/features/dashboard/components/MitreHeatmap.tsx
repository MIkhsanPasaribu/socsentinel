/** SOCsentinel — Dashboard feature — MITRE ATT&CK Heatmap Visualization. */

import { useQuery } from "@tanstack/react-query";
import { Target, Loader2 } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import { cn } from "../../../shared/lib/utils";
import type { APIResponse } from "../../../shared/types";

interface HeatmapData {
  tactics: {
    tactic: string;
    techniques: { id: string; count: number }[];
    total_count: number;
  }[];
  total_techniques_mapped: number;
  total_investigations_analyzed: number;
}

/** Pre-defined exact order of MITRE Enterprise matrix tactics */
const TACTIC_ORDER = [
  "Initial Access",
  "Execution",
  "Persistence",
  "Privilege Escalation",
  "Defense Evasion",
  "Credential Access",
  "Discovery",
  "Lateral Movement",
  "Collection",
  "Command and Control",
  "Exfiltration",
  "Impact",
];

export function MitreHeatmap() {
  const { data, isLoading } = useQuery({
    queryKey: ["mitre-heatmap"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<HeatmapData>>("/pipeline/mitre-heatmap");
      return res.data.data;
    },
    refetchInterval: 10_000,
  });

  if (isLoading) {
    return (
      <div className="glass-card flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan-500" />
      </div>
    );
  }

  if (!data || data.total_techniques_mapped === 0) {
    return (
      <div className="glass-card flex h-64 flex-col items-center justify-center text-center">
        <Target size={32} className="mb-3 text-gray-600" />
        <h3 className="text-sm font-semibold text-gray-400">MITRE ATT&CK Matrix</h3>
        <p className="mt-1 text-xs text-gray-500">Run investigations to map techniques</p>
      </div>
    );
  }

  // Find max count to scale colors
  const maxCount = Math.max(
    ...data.tactics.flatMap((t) => t.techniques.map((tech) => tech.count)),
    1 // fallback
  );

  const getColorClass = (count: number) => {
    if (count === 0) return "bg-navy-900/50 border-white/5";
    const ratio = count / maxCount;
    if (ratio > 0.7) return "bg-red-500/80 border-red-400 text-white";
    if (ratio > 0.4) return "bg-orange-500/80 border-orange-400 text-white";
    if (ratio > 0.1) return "bg-cyan-500/60 border-cyan-400 text-white";
    return "bg-cyan-500/20 border-cyan-500/30 text-cyan-100";
  };

  // Reorder and pad tactics for full matrix view
  const orderedTactics = TACTIC_ORDER.map((tacticName) => {
    const found = data.tactics.find((t) => t.tactic === tacticName);
    return found || { tactic: tacticName, techniques: [], total_count: 0 };
  });

  return (
    <div className="glass-card flex flex-col overflow-hidden p-0">
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target size={16} className="text-red-400" />
            <h3 className="font-semibold text-white">MITRE ATT&CK Matrix</h3>
          </div>
          <span className="rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-400">
            {data.total_techniques_mapped} Techniques Mapped
          </span>
        </div>
        <div className="mt-1 flex items-center justify-between">
          <p className="text-xs text-gray-400">
            Technique density across {data.total_investigations_analyzed} investigations
          </p>
          <span className="text-[10px] text-gray-600 sm:hidden">&larr; scroll &rarr;</span>
        </div>
      </div>

      <div className="flex-1 overflow-x-auto p-3 sm:p-4 custom-scrollbar">
        <div className="flex gap-2" style={{ minWidth: "max-content" }}>
          {orderedTactics.map((tactic, i) => (
            <div key={i} className="flex w-32 flex-col gap-2">
              {/* Column Header */}
              <div className="flex h-12 flex-col justify-end border-b border-white/10 pb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 line-clamp-2 leading-tight">
                  {tactic.tactic}
                </span>
                <span className="text-[10px] text-gray-500">
                  ({tactic.total_count})
                </span>
              </div>

              {/* Technique Cells */}
              <div className="flex flex-col gap-1.5 pt-2">
                {tactic.techniques.length > 0 ? (
                  tactic.techniques
                    // Sort descending by count
                    .sort((a, b) => b.count - a.count)
                    .map((tech, j) => (
                      <div
                        key={j}
                        className={cn(
                          "relative group flex h-14 w-full cursor-help flex-col items-center justify-center rounded border transition-all hover:scale-105",
                          getColorClass(tech.count)
                        )}
                      >
                        <span className="font-mono text-[10px] font-bold tracking-tighter">
                          {tech.id}
                        </span>
                        <span className="text-[9px] opacity-75">{tech.count} hits</span>
                        
                        {/* Tooltip */}
                        <div className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-[10px] text-white opacity-0 shadow-xl transition-opacity group-hover:opacity-100 whitespace-nowrap">
                          {tech.id} detected {tech.count} time(s)
                        </div>
                      </div>
                    ))
                ) : (
                  // Empty state placeholder cell for aesthetics
                  <div className="flex h-14 w-full items-center justify-center rounded border border-white/5 bg-navy-900/20 border-dashed">
                    <span className="text-[10px] text-gray-600">—</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
