/** SOCsentinel — Benchmark Dashboard — AMD MI300X performance proof. */

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Gauge,
  Play,
  Loader2,
  Cpu,
  Clock,
  Zap,
  TrendingDown,
  CheckCircle2,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";
import { cn } from "../../../shared/lib/utils";

interface ScenarioResult {
  scenario: string;
  investigation_id: string;
  status: string;
  total_time_ms: number;
  agent_times: Record<string, number>;
  severity: string;
  escalation_level: string;
}

interface BenchmarkResult {
  scenarios: ScenarioResult[];
  aggregate: {
    total_scenarios: number;
    total_time_ms: number;
    avg_per_scenario_ms: number;
    min_scenario_ms: number;
    max_scenario_ms: number;
  };
  agent_performance: Record<string, { avg_ms: number; min_ms: number; max_ms: number }>;
}

const COMPARISON_DATA = [
  { name: "SOCsentinel (AI)", time: 0, cost: 0, label: "~2-8s", costLabel: "$0 (open-source)" },
  { name: "Manual L1 Analyst", time: 600000, cost: 36000, label: "~10 min", costLabel: "$12.50/case" },
  { name: "Manual L2 Analyst", time: 2700000, cost: 75000, label: "~45 min", costLabel: "$56.25/case" },
  { name: "Dropzone AI", time: 120000, cost: 36000, label: "~2 min", costLabel: "$36,000/yr" },
];

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
  info: "#6b7280",
};

const AGENT_COLORS = [
  "#22d3ee", "#3b82f6", "#8b5cf6", "#ec4899",
  "#f97316", "#eab308", "#22c55e", "#14b8a6", "#6366f1",
];

export function BenchmarkView() {
  const [result, setResult] = useState<BenchmarkResult | null>(null);

  const benchmarkMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<APIResponse>("/pipeline/benchmark", undefined, { timeout: 300000 });
      return res.data.data as BenchmarkResult;
    },
    onSuccess: (data) => setResult(data),
  });

  const agentChartData = result
    ? Object.entries(result.agent_performance).map(([agent, perf], i) => ({
        agent: agent.replace(" Agent", "").replace(" Writer", ""),
        avg_ms: perf.avg_ms,
        min_ms: perf.min_ms,
        max_ms: perf.max_ms,
        color: AGENT_COLORS[i % AGENT_COLORS.length],
      }))
    : [];

  const scenarioChartData = result
    ? result.scenarios.map((s) => ({
        scenario: s.scenario.replace("_", " "),
        total_time_ms: s.total_time_ms,
        severity: s.severity,
        color: SEVERITY_COLORS[s.severity] || "#6b7280",
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
            <Gauge size={24} className="text-cyan-400" />
            Benchmark Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-400">
            AMD MI300X performance proof — run all 5 attack scenarios and measure latency
          </p>
        </div>
        <button
          onClick={() => benchmarkMutation.mutate()}
          disabled={benchmarkMutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-2.5 text-sm font-bold text-white transition-all hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] disabled:scale-100 disabled:opacity-50"
        >
          {benchmarkMutation.isPending ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Running Benchmark...
            </>
          ) : (
            <>
              <Play size={16} />
              Run Full Benchmark
            </>
          )}
        </button>
      </div>

      {/* Aggregate Stats */}
      {result && (
        <div className="animate-slide-up grid grid-cols-2 gap-3 sm:grid-cols-5">
          <div className="glass-card text-center">
            <p className="text-[10px] uppercase tracking-wider text-gray-500">Scenarios</p>
            <p className="mt-1 text-2xl font-bold text-white">{result.aggregate.total_scenarios}</p>
          </div>
          <div className="glass-card text-center">
            <p className="text-[10px] uppercase tracking-wider text-gray-500">Total Time</p>
            <p className="mt-1 text-2xl font-bold text-cyan-400">{(result.aggregate.total_time_ms / 1000).toFixed(1)}s</p>
          </div>
          <div className="glass-card text-center">
            <p className="text-[10px] uppercase tracking-wider text-gray-500">Avg / Scenario</p>
            <p className="mt-1 text-2xl font-bold text-white">{(result.aggregate.avg_per_scenario_ms / 1000).toFixed(1)}s</p>
          </div>
          <div className="glass-card text-center">
            <p className="text-[10px] uppercase tracking-wider text-gray-500">Fastest</p>
            <p className="mt-1 text-2xl font-bold text-green-400">{(result.aggregate.min_scenario_ms / 1000).toFixed(1)}s</p>
          </div>
          <div className="glass-card text-center">
            <p className="text-[10px] uppercase tracking-wider text-gray-500">Slowest</p>
            <p className="mt-1 text-2xl font-bold text-orange-400">{(result.aggregate.max_scenario_ms / 1000).toFixed(1)}s</p>
          </div>
        </div>
      )}

      {/* Charts */}
      {result && (
        <div className="animate-slide-up grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Per-Scenario Latency */}
          <div className="glass-card min-w-0 overflow-hidden">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
              <Clock size={14} className="text-cyan-400" />
              Per-Scenario Latency
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={scenarioChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="scenario" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} label={{ value: "ms", fill: "#6b7280", fontSize: 10, position: "insideTopLeft" }} />
                <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: 12 }} />
                <Bar dataKey="total_time_ms" radius={[4, 4, 0, 0]}>
                  {scenarioChartData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Per-Agent Performance */}
          <div className="glass-card min-w-0 overflow-hidden">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
              <Zap size={14} className="text-cyan-400" />
              Per-Agent Avg Latency
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={agentChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" tick={{ fill: "#9ca3af", fontSize: 11 }} label={{ value: "ms", fill: "#6b7280", fontSize: 10, position: "insideBottomRight" }} />
                <YAxis dataKey="agent" type="category" tick={{ fill: "#9ca3af", fontSize: 10 }} width={90} />
                <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: 12 }} />
                <Bar dataKey="avg_ms" radius={[0, 4, 4, 0]}>
                  {agentChartData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Comparison Table */}
      <div className="glass-card">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
          <TrendingDown size={14} className="text-cyan-400" />
          SOCsentinel vs Industry Comparison
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-gray-500">
                <th className="py-3 pr-4">Solution</th>
                <th className="py-3 pr-4">Investigation Time</th>
                <th className="py-3 pr-4">Annual Cost</th>
                <th className="py-3">Advantage</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON_DATA.map((row, i) => (
                <tr key={i} className={cn("border-b border-white/5", i === 0 && "bg-cyan-500/5")}>
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-2">
                      {i === 0 && <CheckCircle2 size={14} className="text-cyan-400" />}
                      <span className={cn("font-medium", i === 0 ? "text-cyan-400" : "text-gray-300")}>
                        {row.name}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 pr-4">
                    <span className={cn("font-mono text-xs", i === 0 ? "text-green-400" : "text-gray-400")}>
                      {i === 0 && result ? `~${(result.aggregate.avg_per_scenario_ms / 1000).toFixed(1)}s` : row.label}
                    </span>
                  </td>
                  <td className="py-3 pr-4">
                    <span className={cn("text-xs", i === 0 ? "text-green-400 font-medium" : "text-gray-400")}>
                      {row.costLabel}
                    </span>
                  </td>
                  <td className="py-3">
                    {i === 0 ? (
                      <span className="rounded-full bg-cyan-500/20 px-2 py-0.5 text-[10px] font-bold text-cyan-400">
                        FASTEST + FREE
                      </span>
                    ) : (
                      <span className="text-[10px] text-gray-600">
                        {result ? `${Math.round(row.time / result.aggregate.avg_per_scenario_ms)}x slower` : "—"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* GPU Specs */}
      <div className="glass-card">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
          <Cpu size={14} className="text-cyan-400" />
          AMD Instinct MI300X Specifications
        </h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: "HBM3 Memory", value: "192 GB" },
            { label: "Memory Bandwidth", value: "5.3 TB/s" },
            { label: "Compute Units", value: "304 CUs" },
            { label: "Peak FP16", value: "1.3 PFLOPS" },
            { label: "ROCm Version", value: "6.x" },
            { label: "vLLM Serving", value: "PagedAttention" },
            { label: "Models Loaded", value: "Qwen3 4B/7B/14B" },
            { label: "Concurrent Agents", value: "9 Specialized" },
          ].map((spec) => (
            <div key={spec.label} className="rounded-lg bg-white/[0.03] p-3">
              <p className="text-[10px] uppercase tracking-wider text-gray-500">{spec.label}</p>
              <p className="mt-1 text-sm font-bold text-white">{spec.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {!result && !benchmarkMutation.isPending && (
        <div className="glass-card flex flex-col items-center py-16 text-center">
          <Gauge size={48} className="mb-4 text-gray-600" />
          <p className="text-sm text-gray-500">Click "Run Full Benchmark" to test all 5 attack scenarios</p>
          <p className="mt-1 text-xs text-gray-600">
            Results will show per-agent latency, per-scenario timing, and industry comparison
          </p>
        </div>
      )}

      {/* Running state */}
      {benchmarkMutation.isPending && (
        <div className="glass-card flex flex-col items-center py-16 text-center">
          <Loader2 size={48} className="mb-4 animate-spin text-cyan-400" />
          <p className="text-sm text-white">Running benchmark across 5 attack scenarios...</p>
          <p className="mt-1 text-xs text-gray-400">
            Testing: Brute Force, Lateral Movement, Data Exfiltration, Phishing, Ransomware
          </p>
        </div>
      )}

      {benchmarkMutation.isError && (
        <div className="glass-card border-l-4 border-l-red-500 py-4 text-center">
          <p className="text-sm text-red-400">Benchmark failed. Ensure the backend is running.</p>
        </div>
      )}
    </div>
  );
}
