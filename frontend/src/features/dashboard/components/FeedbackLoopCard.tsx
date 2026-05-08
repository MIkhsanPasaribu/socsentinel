/** SOCsentinel — Feedback Loop Card — Shows self-improving triage metrics. */

import { useQuery } from "@tanstack/react-query";
import { Brain, TrendingUp, AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";

interface FeedbackStats {
  total_feedback: number;
  agreement_rate: number;
  corrections: number;
}

export function FeedbackLoopCard() {
  const { data: stats, isLoading } = useQuery<FeedbackStats>({
    queryKey: ["feedback-stats"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse>("/pipeline/feedback-stats");
      return res.data.data as FeedbackStats;
    },
    refetchInterval: 15_000,
  });

  if (isLoading) {
    return (
      <div className="glass-card flex items-center justify-center py-8">
        <Loader2 size={20} className="animate-spin text-cyan-400" />
      </div>
    );
  }

  const total = stats?.total_feedback ?? 0;
  const agreementRate = stats?.agreement_rate ?? 0;
  const corrections = stats?.corrections ?? 0;

  return (
    <div className="glass-card">
      <div className="mb-4 flex items-center gap-2">
        <div className="rounded-lg bg-purple-500/10 p-2">
          <Brain size={18} className="text-purple-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">Self-Improving Triage Loop</h3>
          <p className="text-[10px] text-gray-500">
            AI learns from analyst decisions to improve future classifications
          </p>
        </div>
      </div>

      {total === 0 ? (
        <div className="rounded-lg border border-white/5 bg-white/[0.02] px-4 py-6 text-center">
          <Brain size={32} className="mx-auto mb-2 text-gray-600" />
          <p className="text-xs text-gray-500">No feedback data yet</p>
          <p className="mt-1 text-[10px] text-gray-600">
            Make decisions on investigations to start the learning loop
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-lg bg-white/[0.03] p-3 text-center">
              <p className="text-2xl font-bold text-white">{total}</p>
              <p className="text-[10px] text-gray-500">Total Feedback</p>
            </div>
            <div className="rounded-lg bg-white/[0.03] p-3 text-center">
              <div className="flex items-center justify-center gap-1">
                <TrendingUp size={14} className="text-green-400" />
                <p className="text-2xl font-bold text-green-400">{agreementRate}%</p>
              </div>
              <p className="text-[10px] text-gray-500">AI-Human Agreement</p>
            </div>
            <div className="rounded-lg bg-white/[0.03] p-3 text-center">
              <p className="text-2xl font-bold text-orange-400">{corrections}</p>
              <p className="text-[10px] text-gray-500">Corrections Made</p>
            </div>
          </div>

          {/* Learning Progress Bar */}
          <div className="mt-3 rounded-lg bg-white/[0.02] p-3">
            <div className="mb-1.5 flex items-center justify-between text-[10px]">
              <span className="font-medium text-gray-400">Learning Progress</span>
              <span className="text-purple-400">{agreementRate}% accuracy</span>
            </div>
            <div className="h-2 rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 transition-all duration-500"
                style={{ width: `${Math.min(agreementRate, 100)}%` }}
              />
            </div>
            <div className="mt-2 flex items-start gap-1.5">
              {agreementRate >= 80 ? (
                <>
                  <CheckCircle2 size={12} className="mt-0.5 shrink-0 text-green-400" />
                  <p className="text-[10px] text-green-400">High agreement — AI triage is well-calibrated</p>
                </>
              ) : agreementRate >= 50 ? (
                <>
                  <TrendingUp size={12} className="mt-0.5 shrink-0 text-cyan-400" />
                  <p className="text-[10px] text-cyan-400">Learning in progress — accuracy improving with more feedback</p>
                </>
              ) : (
                <>
                  <AlertTriangle size={12} className="mt-0.5 shrink-0 text-orange-400" />
                  <p className="text-[10px] text-orange-400">More analyst feedback needed to improve AI calibration</p>
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
