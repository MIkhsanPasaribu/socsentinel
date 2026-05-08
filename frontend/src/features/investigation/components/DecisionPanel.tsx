/** SOCsentinel — Human-in-the-Loop Analyst Workbench (UC-05). */

import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Shield,
  MessageSquare,
  Crosshair,
  History,
  SlidersHorizontal,
  Target,
  Loader2,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import { ConfidenceGauge } from "../../../shared/components/ConfidenceGauge";
import { useFormValidation } from "../../../shared/hooks/useFormValidation";
import { decisionSchema } from "../../../shared/lib/validation";
import { cn, getSeverityBadgeClass } from "../../../shared/lib/utils";
import type { APIResponse } from "../../../shared/types";

type Decision = "approve" | "escalate" | "reject";

interface RiskSummary {
  risk_level: string;
  risk_score: number;
  severity: string;
  classification: string;
  confidence: number;
  technique_count: number;
  top_techniques: string[];
  ioc_count: number;
  kill_chain_phase: string;
  escalation_level: string;
  recommended_action: string;
  decision_history: Array<{
    severity: string;
    rule_name: string;
    ai_classification: string;
    analyst_decision: string;
    confidence: number | null;
  }>;
  has_past_decisions: boolean;
}

interface DecisionPanelProps {
  investigationId: string;
  severity: string | null;
  avgConfidence: number | null;
  onDecisionMade?: (decision: Decision) => void;
}

function RiskBadge({ level }: { level: string }) {
  const styles: Record<string, string> = {
    critical: "bg-red-500/20 text-red-400 border-red-500/30",
    high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    low: "bg-green-500/20 text-green-400 border-green-500/30",
  };
  return (
    <span className={cn("rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase", styles[level] || styles.medium)}>
      {level} risk
    </span>
  );
}

export function DecisionPanel({
  investigationId,
  severity,
  avgConfidence,
  onDecisionMade,
}: DecisionPanelProps) {
  const [notes, setNotes] = useState("");
  const [decided, setDecided] = useState<Decision | null>(null);
  const [confidenceOverride, setConfidenceOverride] = useState<number | null>(null);
  const [showOverride, setShowOverride] = useState(false);
  const { errors, validate, clearErrors } = useFormValidation(decisionSchema);
  const queryClient = useQueryClient();

  const { data: riskSummary, isLoading: riskLoading } = useQuery<RiskSummary>({
    queryKey: ["risk-summary", investigationId],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse>(`/pipeline/risk-summary/${investigationId}`);
      return res.data.data as RiskSummary;
    },
    enabled: !!investigationId,
  });

  useEffect(() => {
    if (riskSummary?.confidence != null) {
      setConfidenceOverride(null);
    }
  }, [riskSummary]);

  const decisionMutation = useMutation({
    mutationFn: (decision: Decision) =>
      apiClient.post<APIResponse>(`/pipeline/decision/${investigationId}`, {
        decision,
        analyst_notes: notes,
        confidence_override: confidenceOverride,
        severity_override: null,
      }),
    onSuccess: (_, decision) => {
      setDecided(decision);
      clearErrors();
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-stats"] });
      onDecisionMade?.(decision);
    },
  });

  const handleDecision = (decision: Decision) => {
    const payload = {
      decision,
      notes: notes.trim() || undefined,
      confidence_override: confidenceOverride,
    };
    if (!validate(payload)) return;
    decisionMutation.mutate(decision);
  };

  if (decided) {
    const labels: Record<Decision, { text: string; color: string; icon: typeof CheckCircle2 }> = {
      approve: { text: "Response Approved", color: "text-green-400", icon: CheckCircle2 },
      escalate: { text: "Escalated to L3", color: "text-orange-400", icon: AlertTriangle },
      reject: { text: "Investigation Rejected", color: "text-red-400", icon: XCircle },
    };
    const d = labels[decided];
    const Icon = d.icon;

    return (
      <div className="animate-fade-in rounded-xl border border-white/10 bg-white/[0.03] p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-green-500/10 p-2">
            <Icon size={20} className={d.color} />
          </div>
          <div>
            <p className={`text-sm font-semibold ${d.color}`}>{d.text}</p>
            <p className="text-xs text-gray-500">Decision recorded for {investigationId}</p>
            {confidenceOverride !== null && (
              <p className="text-[10px] text-cyan-400">
                Confidence overridden: {Math.round(confidenceOverride * 100)}%
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-up space-y-3">
      {/* Header */}
      <div className="rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 p-4 sm:p-5">
        <div className="mb-4 flex items-center gap-3">
          <div className="rounded-lg bg-cyan-500/10 p-2">
            <Shield size={20} className="text-cyan-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-white">Analyst Workbench</h3>
            <p className="text-xs text-gray-400">Review risk assessment, override confidence, and make your decision</p>
          </div>
          {avgConfidence !== null && avgConfidence > 0 && (
            <ConfidenceGauge score={avgConfidence} size="sm" label="AI Score" />
          )}
        </div>

        {/* Risk Summary Card */}
        {riskLoading ? (
          <div className="flex items-center justify-center gap-2 rounded-lg border border-white/5 bg-white/[0.02] py-6">
            <Loader2 size={16} className="animate-spin text-cyan-400" />
            <span className="text-xs text-gray-500">Loading risk assessment...</span>
          </div>
        ) : riskSummary ? (
          <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
            <div className="mb-3 flex items-center gap-2">
              <Crosshair size={14} className="text-cyan-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Risk Assessment</span>
              <RiskBadge level={riskSummary.risk_level} />
              <span className={getSeverityBadgeClass(severity || "medium")}>{(severity || "medium").toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <div className="rounded-md bg-white/[0.03] px-2.5 py-2 text-center">
                <p className="text-lg font-bold text-white">{riskSummary.technique_count}</p>
                <p className="text-[10px] text-gray-500">MITRE Techniques</p>
              </div>
              <div className="rounded-md bg-white/[0.03] px-2.5 py-2 text-center">
                <p className="text-lg font-bold text-white">{riskSummary.ioc_count}</p>
                <p className="text-[10px] text-gray-500">IOCs Found</p>
              </div>
              <div className="rounded-md bg-white/[0.03] px-2.5 py-2 text-center">
                <p className="text-lg font-bold text-white">{riskSummary.escalation_level}</p>
                <p className="text-[10px] text-gray-500">Escalation Level</p>
              </div>
              <div className="rounded-md bg-white/[0.03] px-2.5 py-2 text-center">
                <p className="text-lg font-bold text-cyan-400">{Math.round((riskSummary.confidence || 0) * 100)}%</p>
                <p className="text-[10px] text-gray-500">AI Confidence</p>
              </div>
            </div>
            {riskSummary.top_techniques.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {riskSummary.top_techniques.map((t) => (
                  <span key={t} className="rounded bg-red-500/20 px-1.5 py-0.5 font-mono text-[10px] text-red-400">{t}</span>
                ))}
              </div>
            )}
            <div className="mt-2 flex items-start gap-1.5 rounded-md bg-cyan-500/5 p-2">
              <Target size={12} className="mt-0.5 shrink-0 text-cyan-400" />
              <p className="text-[11px] text-cyan-300">{riskSummary.recommended_action}</p>
            </div>
          </div>
        ) : null}

        {/* Decision History */}
        {riskSummary?.has_past_decisions && (
          <div className="mt-3 rounded-lg border border-white/10 bg-white/[0.03] p-3">
            <div className="mb-2 flex items-center gap-2">
              <History size={14} className="text-purple-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Decision History (Same Rule)</span>
            </div>
            <div className="space-y-1">
              {riskSummary.decision_history.map((h, i) => (
                <div key={i} className="flex items-center gap-2 rounded-md bg-white/[0.02] px-2 py-1.5 text-xs">
                  <span className={cn(
                    "rounded px-1.5 py-0.5 text-[10px] font-medium",
                    h.analyst_decision === "approve" ? "bg-green-500/20 text-green-400" :
                    h.analyst_decision === "escalate" ? "bg-orange-500/20 text-orange-400" :
                    "bg-red-500/20 text-red-400"
                  )}>
                    {h.analyst_decision}
                  </span>
                  <span className="text-gray-500">AI said: {h.ai_classification}</span>
                  {h.confidence && (
                    <span className="ml-auto text-gray-600">{Math.round(h.confidence * 100)}%</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Confidence Override */}
        <div className="mt-3">
          <button
            onClick={() => setShowOverride(!showOverride)}
            className="flex items-center gap-1.5 text-xs font-medium text-gray-400 transition-colors hover:text-cyan-400"
          >
            <SlidersHorizontal size={12} />
            {showOverride ? "Hide" : "Override"} AI Confidence
          </button>
          {showOverride && (
            <div className="mt-2 rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={confidenceOverride !== null ? Math.round(confidenceOverride * 100) : Math.round((riskSummary?.confidence || avgConfidence || 0) * 100)}
                  onChange={(e) => setConfidenceOverride(Number(e.target.value) / 100)}
                  className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-white/10 accent-cyan-400"
                />
                <span className="min-w-[3rem] text-right font-mono text-sm font-bold text-cyan-400">
                  {confidenceOverride !== null
                    ? `${Math.round(confidenceOverride * 100)}%`
                    : `${Math.round((riskSummary?.confidence || avgConfidence || 0) * 100)}%`}
                </span>
              </div>
              {confidenceOverride !== null && (
                <div className="mt-1 flex items-center justify-between">
                  <p className="text-[10px] text-yellow-400">Analyst override active — notes required</p>
                  <button
                    onClick={() => setConfidenceOverride(null)}
                    className="text-[10px] text-gray-500 underline hover:text-gray-300"
                  >
                    Reset
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Analyst Notes */}
        <div className="mt-3">
          <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-gray-400">
            <MessageSquare size={12} /> Analyst Notes {confidenceOverride !== null ? "(required)" : "(optional)"}
          </label>
          <textarea
            value={notes}
            onChange={(e) => {
              setNotes(e.target.value);
              if (Object.keys(errors).length) clearErrors();
            }}
            placeholder="Add investigation notes, observations, or reasoning..."
            rows={2}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-300 placeholder-gray-600 outline-none transition-colors focus:border-cyan-500/30 focus:bg-white/[0.07]"
          />
          {errors.notes && <p className="mt-1 text-xs text-orange-300">{errors.notes}</p>}
        </div>

        {/* Decision Buttons */}
        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:gap-3">
          <button
            onClick={() => handleDecision("approve")}
            disabled={decisionMutation.isPending}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-2.5 text-sm font-medium text-green-400 transition-all hover:bg-green-500/20 hover:shadow-lg hover:shadow-green-500/10 disabled:opacity-50"
          >
            <CheckCircle2 size={16} /> Approve Response
          </button>
          <button
            onClick={() => handleDecision("escalate")}
            disabled={decisionMutation.isPending}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-orange-500/30 bg-orange-500/10 px-4 py-2.5 text-sm font-medium text-orange-400 transition-all hover:bg-orange-500/20 hover:shadow-lg hover:shadow-orange-500/10 disabled:opacity-50"
          >
            <AlertTriangle size={16} /> Escalate to L3
          </button>
          <button
            onClick={() => handleDecision("reject")}
            disabled={decisionMutation.isPending}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm font-medium text-red-400 transition-all hover:bg-red-500/20 hover:shadow-lg hover:shadow-red-500/10 disabled:opacity-50"
          >
            <XCircle size={16} /> Reject
          </button>
        </div>
      </div>
    </div>
  );
}
