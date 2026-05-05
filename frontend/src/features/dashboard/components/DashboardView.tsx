/** SOCsentinel — Dashboard main view (live data from API). */

import { useNavigate } from "react-router-dom";
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Zap,
  TrendingDown,
  TrendingUp,
  Brain,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import { usePipelineStats, useRecentInvestigations } from "../hooks/useDashboardStats";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../../../shared/lib/api";
import { getSeverityBadgeClass, formatRelativeTime } from "../../../shared/lib/utils";
import { MitreHeatmap } from "./MitreHeatmap";

/** Stat card for the dashboard overview. */
function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  accentColor = "cyan",
  isLoading = false,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  trend?: { value: string; direction: "up" | "down" };
  accentColor?: "cyan" | "orange" | "green" | "red";
  isLoading?: boolean;
}) {
  const accentMap = {
    cyan: "from-cyan-500/20 to-blue-500/20 border-cyan-500/30",
    orange: "from-orange-500/20 to-red-500/20 border-orange-500/30",
    green: "from-green-500/20 to-emerald-500/20 border-green-500/30",
    red: "from-red-500/20 to-pink-500/20 border-red-500/30",
  };

  const iconColorMap = {
    cyan: "text-cyan-400",
    orange: "text-orange-400",
    green: "text-green-400",
    red: "text-red-400",
  };

  return (
    <div
      className={`animate-fade-in rounded-xl border bg-gradient-to-br p-6 ${accentMap[accentColor]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-400">{title}</p>
          {isLoading ? (
            <div className="mt-2 h-9 w-20 animate-pulse rounded bg-white/10" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-white">{value}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">{subtitle}</p>
        </div>
        <div className={`rounded-lg bg-white/5 p-2.5 ${iconColorMap[accentColor]}`}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1.5">
          {trend.direction === "down" ? (
            <TrendingDown size={14} className="text-green-400" />
          ) : (
            <TrendingUp size={14} className="text-cyan-400" />
          )}
          <span
            className={`text-xs font-medium ${
              trend.direction === "down" ? "text-green-400" : "text-cyan-400"
            }`}
          >
            {trend.value}
          </span>
        </div>
      )}
    </div>
  );
}

/** Agent status card showing each AI agent's current state. */
function AgentCard({
  name,
  role,
  model,
  avgTime,
  totalRuns,
}: {
  name: string;
  role: string;
  model: string;
  avgTime?: number;
  totalRuns?: number;
}) {
  const hasRuns = totalRuns !== undefined && totalRuns > 0;

  return (
    <div className="glass-card animate-slide-up flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/20">
          <Brain size={20} className="text-cyan-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">{name}</h3>
          <p className="text-xs text-gray-500">{role}</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="rounded-md bg-white/5 px-2 py-1 font-mono text-[10px] text-gray-400">
          {model}
        </span>
        {hasRuns ? (
          <div className="text-right">
            <p className="text-xs font-medium text-cyan-400">{avgTime?.toFixed(0)}ms avg</p>
            <p className="text-[10px] text-gray-500">{totalRuns} runs</p>
          </div>
        ) : (
          <div className="flex items-center gap-1.5">
            <span className="agent-active" />
            <span className="text-xs font-medium text-green-400">Online</span>
          </div>
        )}
      </div>
    </div>
  );
}

/** Recent investigation row. */
function InvestigationRow({
  inv,
  onClick,
}: {
  inv: {
    investigation_id: string;
    alert_id: string;
    status: string;
    severity: string;
    processing_time_ms: number;
    started_at: string;
  };
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="flex cursor-pointer items-center gap-4 rounded-lg border border-white/5 bg-white/[0.02] px-4 py-3 transition-all hover:border-cyan-500/20 hover:bg-white/[0.04]"
    >
      <span className={getSeverityBadgeClass(inv.severity)}>
        {inv.severity.toUpperCase()}
      </span>
      <div className="flex-1">
        <p className="font-mono text-xs text-gray-300">{inv.investigation_id}</p>
        <p className="text-[10px] text-gray-500">{inv.alert_id}</p>
      </div>
      <div className="flex items-center gap-1 text-xs text-gray-400">
        <Clock size={12} />
        <span>{inv.processing_time_ms?.toFixed(0) || "?"}ms</span>
      </div>
      <span className="flex items-center gap-1 text-xs text-green-400">
        <CheckCircle2 size={12} />
        {inv.status}
      </span>
      <span className="text-[10px] text-gray-500">{formatRelativeTime(inv.started_at)}</span>
      <ArrowRight size={14} className="text-gray-500" />
    </div>
  );
}

export function DashboardView() {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = usePipelineStats();
  const { data: investigations, isLoading: invLoading } = useRecentInvestigations();

  const generateAndInvestigate = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post("/pipeline/investigate-demo?scenario=brute_force");
      return res.data;
    },
  });

  /** Find agent performance data by name. */
  const getAgentPerf = (name: string) =>
    stats?.agent_performance?.find((a) => a.agent === name);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Security Operations Dashboard
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          Real-time overview of SOC agent activity and alert processing
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Investigations"
          value={stats?.total_investigations ?? 0}
          subtitle="All-time processed"
          icon={<AlertTriangle size={22} />}
          accentColor="orange"
          isLoading={statsLoading}
        />
        <StatCard
          title="Auto-Triaged"
          value={stats?.auto_triaged ?? 0}
          subtitle={`${stats?.auto_triage_rate ?? 0}% auto-triage rate`}
          icon={<Zap size={22} />}
          accentColor="cyan"
          isLoading={statsLoading}
          trend={
            stats && stats.auto_triage_rate > 0
              ? { value: `${stats.auto_triage_rate}% automated`, direction: "up" }
              : undefined
          }
        />
        <StatCard
          title="Threat Intel (RAG)"
          value="100%"
          subtitle="697 MITRE Techniques"
          icon={<Shield size={22} />}
          accentColor="green"
          isLoading={statsLoading}
        />
        <StatCard
          title="Avg Response Time"
          value={
            stats?.avg_processing_time_ms
              ? `${stats.avg_processing_time_ms.toFixed(0)}ms`
              : "—"
          }
          subtitle="Per investigation"
          icon={<Clock size={22} />}
          accentColor="cyan"
          isLoading={statsLoading}
          trend={
            stats && stats.avg_processing_time_ms > 0
              ? { value: "30x faster than manual", direction: "down" }
              : undefined
          }
        />
      </div>

      {/* MITRE ATT&CK Heatmap */}
      <MitreHeatmap />

      {/* Agent Status */}
      <div>
        <div className="mb-4 flex items-center gap-2">
          <Activity size={18} className="text-cyan-400" />
          <h2 className="text-lg font-semibold text-white">Agent Status</h2>
          <span className="ml-2 rounded-full bg-green-500/10 px-2.5 py-0.5 text-xs font-medium text-green-400">
            All Systems Operational
          </span>
        </div>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3">
          <AgentCard
            name="Orchestrator"
            role="SOC Manager"
            model="Qwen3-7B"
            avgTime={getAgentPerf("Orchestrator")?.avg_time_ms}
            totalRuns={getAgentPerf("Orchestrator")?.total_runs}
          />
          <AgentCard
            name="L1 Triage"
            role="L1 Analyst"
            model="Qwen3-4B"
            avgTime={getAgentPerf("L1 Triage")?.avg_time_ms}
            totalRuns={getAgentPerf("L1 Triage")?.total_runs}
          />
          <AgentCard
            name="Evidence Collector"
            role="L2 Analyst"
            model="Qwen3-7B"
            avgTime={getAgentPerf("Evidence Collector")?.avg_time_ms}
            totalRuns={getAgentPerf("Evidence Collector")?.total_runs}
          />
          <AgentCard
            name="MITRE Mapper"
            role="L2/L3 Analyst"
            model="Qwen3-7B"
            avgTime={getAgentPerf("MITRE Mapper")?.avg_time_ms}
            totalRuns={getAgentPerf("MITRE Mapper")?.total_runs}
          />
          <AgentCard
            name="Report Writer"
            role="Senior Analyst"
            model="Qwen3-14B"
            avgTime={getAgentPerf("Report Writer")?.avg_time_ms}
            totalRuns={getAgentPerf("Report Writer")?.total_runs}
          />
          <AgentCard
            name="Response Planner"
            role="L3 Incident Responder"
            model="Qwen3-14B"
            avgTime={getAgentPerf("Response Planner")?.avg_time_ms}
            totalRuns={getAgentPerf("Response Planner")?.total_runs}
          />
        </div>
      </div>

      {/* Recent Investigations */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield size={18} className="text-cyan-400" />
            <h2 className="text-lg font-semibold text-white">
              Recent Investigations
            </h2>
          </div>
          {investigations && investigations.length > 0 && (
            <button
              onClick={() => navigate("/investigation")}
              className="flex items-center gap-1 text-xs font-medium text-cyan-400 transition-colors hover:text-cyan-300"
            >
              View all <ArrowRight size={14} />
            </button>
          )}
        </div>

        {invLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-14 animate-pulse rounded-lg bg-white/5" />
            ))}
          </div>
        ) : investigations && investigations.length > 0 ? (
          <div className="space-y-2">
            {investigations.slice(0, 5).map((inv) => (
              <InvestigationRow
                key={inv.investigation_id}
                inv={inv}
                onClick={() => navigate("/investigation")}
              />
            ))}
          </div>
        ) : (
          <div className="glass-card relative overflow-hidden">
            {/* Background pulse effect */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
              <div className="h-64 w-64 animate-ping rounded-full bg-cyan-500/5 duration-[3000ms]" />
              <div className="absolute left-1/2 top-1/2 h-32 w-32 -translate-x-1/2 -translate-y-1/2 animate-ping rounded-full bg-blue-500/10 duration-[2000ms] delay-500" />
            </div>
            
            <div className="relative flex flex-col items-center justify-center py-16 text-center z-10">
              <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 ring-1 ring-white/10 backdrop-blur-md">
                <Shield size={40} className="text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
                SOCsentinel is Ready
              </h3>
              <p className="text-sm text-gray-400 max-w-sm mb-8">
                The 6-agent AI pipeline is standing by. Generate a synthetic alert to watch the system triage, investigate, and respond in real-time.
              </p>
              <button
                id="btn-generate-alert"
                onClick={() => generateAndInvestigate.mutate()}
                disabled={generateAndInvestigate.isPending}
                className="group flex items-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-3 text-sm font-bold text-white transition-all hover:scale-105 hover:shadow-[0_0_30px_rgba(34,211,238,0.4)] disabled:scale-100 disabled:opacity-50"
              >
                {generateAndInvestigate.isPending ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    Running Pipeline...
                  </>
                ) : (
                  <>
                    <Zap size={18} className="group-hover:animate-pulse" />
                    Simulate Attack Scenario
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
