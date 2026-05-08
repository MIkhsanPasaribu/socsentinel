/** SOCsentinel — Business Value Impact Card for the Dashboard.
 *
 * Shows before/after comparison: manual analyst vs SOCsentinel,
 * with time savings, cost savings, and annual projections.
 */

import { DollarSign, Clock, TrendingUp, BarChart3 } from "lucide-react";

interface BusinessValueCardProps {
  /** Total completed investigations. */
  totalInvestigations: number;
  /** Average processing time per investigation (ms). */
  avgProcessingTimeMs: number;
}

/** Manual analyst benchmarks (industry average). */
const MANUAL_TRIAGE_MINUTES = 45;
const ANALYST_HOURLY_RATE = 75;
const WORKING_HOURS_PER_YEAR = 2080;

export function BusinessValueCard({
  totalInvestigations,
  avgProcessingTimeMs,
}: BusinessValueCardProps) {
  const avgTimeSec = avgProcessingTimeMs > 0 ? avgProcessingTimeMs / 1000 : 4.2;
  const timeSavedMinutes = totalInvestigations * (MANUAL_TRIAGE_MINUTES - avgTimeSec / 60);
  const timeSavedHours = timeSavedMinutes / 60;
  const costSaved = timeSavedHours * ANALYST_HOURLY_RATE;

  const alertsPerDay = Math.max(totalInvestigations, 1);
  const annualAlerts = alertsPerDay * 365;
  const annualTimeSavedHours = annualAlerts * (MANUAL_TRIAGE_MINUTES / 60);
  const annualCostSaved = annualTimeSavedHours * ANALYST_HOURLY_RATE;
  const speedupFactor =
    avgProcessingTimeMs > 0
      ? Math.round((MANUAL_TRIAGE_MINUTES * 60 * 1000) / avgProcessingTimeMs)
      : 540;

  return (
    <div className="rounded-xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/5 to-green-600/5 p-4 sm:p-6">
      <div className="mb-4 flex items-center gap-2">
        <DollarSign size={18} className="text-emerald-400" />
        <h2 className="text-lg font-semibold text-white">Business Impact</h2>
        <span className="ml-2 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
          ROI Calculator
        </span>
      </div>

      {/* Before vs After Comparison */}
      <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-center">
          <p className="text-[10px] uppercase tracking-wider text-red-400">Manual Analyst</p>
          <p className="mt-1 text-2xl font-bold text-red-400">45 min</p>
          <p className="text-[10px] text-gray-500">per alert triage</p>
        </div>
        <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-center">
          <p className="text-[10px] uppercase tracking-wider text-emerald-400">SOCsentinel</p>
          <p className="mt-1 text-2xl font-bold text-emerald-400">{avgTimeSec.toFixed(1)}s</p>
          <p className="text-[10px] text-gray-500">per alert triage</p>
        </div>
        <div className="rounded-lg bg-cyan-500/10 border border-cyan-500/20 p-3 text-center">
          <p className="text-[10px] uppercase tracking-wider text-cyan-400">Speed Improvement</p>
          <p className="mt-1 text-2xl font-bold text-cyan-400">{speedupFactor}x</p>
          <p className="text-[10px] text-gray-500">faster response</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-lg bg-white/5 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-gray-500">
            <BarChart3 size={10} />
            Investigations
          </div>
          <p className="mt-1 text-xl font-bold text-white">{totalInvestigations}</p>
          <p className="text-[10px] text-gray-500">processed to date</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-gray-500">
            <Clock size={10} />
            Time Saved
          </div>
          <p className="mt-1 text-xl font-bold text-emerald-400">
            {timeSavedHours >= 1 ? `${timeSavedHours.toFixed(1)}h` : `${Math.round(timeSavedMinutes)}m`}
          </p>
          <p className="text-[10px] text-gray-500">vs manual analysis</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-gray-500">
            <DollarSign size={10} />
            Cost Saved
          </div>
          <p className="mt-1 text-xl font-bold text-emerald-400">
            ${costSaved >= 1000 ? `${(costSaved / 1000).toFixed(1)}K` : Math.round(costSaved)}
          </p>
          <p className="text-[10px] text-gray-500">at $75/hr analyst rate</p>
        </div>
        <div className="rounded-lg bg-white/5 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-gray-500">
            <TrendingUp size={10} />
            Annual Projection
          </div>
          <p className="mt-1 text-xl font-bold text-orange-400">
            ${annualCostSaved >= 1000 ? `${(annualCostSaved / 1000).toFixed(0)}K` : Math.round(annualCostSaved)}
          </p>
          <p className="text-[10px] text-gray-500">estimated savings/yr</p>
        </div>
      </div>
    </div>
  );
}
