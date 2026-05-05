/** SOCsentinel — Dashboard main view. */

import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Zap,
  TrendingDown,
  Brain,
} from "lucide-react";

/** Stat card for the dashboard overview. */
function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  accentColor = "cyan",
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  trend?: { value: string; direction: "up" | "down" };
  accentColor?: "cyan" | "orange" | "green" | "red";
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
          <p className="mt-2 text-3xl font-bold text-white">{value}</p>
          <p className="mt-1 text-xs text-gray-500">{subtitle}</p>
        </div>
        <div className={`rounded-lg bg-white/5 p-2.5 ${iconColorMap[accentColor]}`}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1.5">
          <TrendingDown
            size={14}
            className={
              trend.direction === "down" ? "text-green-400" : "text-red-400"
            }
          />
          <span
            className={`text-xs font-medium ${
              trend.direction === "down" ? "text-green-400" : "text-red-400"
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
  status,
}: {
  name: string;
  role: string;
  model: string;
  status: "active" | "idle" | "processing";
}) {
  const statusStyles = {
    active: { dot: "agent-active", label: "Online", color: "text-green-400" },
    idle: { dot: "agent-idle", label: "Idle", color: "text-gray-400" },
    processing: {
      dot: "agent-active",
      label: "Processing",
      color: "text-cyan-400",
    },
  };

  const s = statusStyles[status];

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
        <div className="flex items-center gap-1.5">
          <span className={s.dot} />
          <span className={`text-xs font-medium ${s.color}`}>{s.label}</span>
        </div>
      </div>
    </div>
  );
}

export function DashboardView() {
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
          title="Total Alerts Today"
          value={127}
          subtitle="Across all sources"
          icon={<AlertTriangle size={22} />}
          accentColor="orange"
          trend={{ value: "12% from yesterday", direction: "down" }}
        />
        <StatCard
          title="Auto-Triaged"
          value={89}
          subtitle="70% triage rate"
          icon={<Zap size={22} />}
          accentColor="cyan"
        />
        <StatCard
          title="Resolved"
          value={73}
          subtitle="82% resolution rate"
          icon={<CheckCircle2 size={22} />}
          accentColor="green"
        />
        <StatCard
          title="Avg Response Time"
          value="< 45s"
          subtitle="Per investigation"
          icon={<Clock size={22} />}
          accentColor="cyan"
          trend={{ value: "30% faster than manual", direction: "down" }}
        />
      </div>

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
            status="active"
          />
          <AgentCard
            name="L1 Triage"
            role="L1 Analyst"
            model="Qwen3-4B"
            status="processing"
          />
          <AgentCard
            name="Evidence Collector"
            role="L2 Analyst"
            model="Qwen3-7B"
            status="active"
          />
          <AgentCard
            name="MITRE Mapper"
            role="L2/L3 Analyst"
            model="Qwen3-7B"
            status="idle"
          />
          <AgentCard
            name="Report Writer"
            role="Senior Analyst"
            model="Qwen3-14B"
            status="idle"
          />
        </div>
      </div>

      {/* Pipeline Activity (placeholder for real-time feed) */}
      <div>
        <div className="mb-4 flex items-center gap-2">
          <Shield size={18} className="text-cyan-400" />
          <h2 className="text-lg font-semibold text-white">
            Recent Investigations
          </h2>
        </div>
        <div className="glass-card">
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Shield size={48} className="mb-4 text-gray-600" />
            <p className="text-sm text-gray-500">
              No active investigations. Submit an alert to begin.
            </p>
            <button
              id="btn-generate-alert"
              className="mt-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 text-sm font-medium text-white transition-all hover:shadow-lg hover:shadow-cyan-500/25"
            >
              Generate Synthetic Alert
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
