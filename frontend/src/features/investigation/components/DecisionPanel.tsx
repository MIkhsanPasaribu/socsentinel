/** SOCsentinel — Human-in-the-Loop Decision Panel (UC-05). */

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Shield,
  MessageSquare,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import { ConfidenceGauge } from "../../../shared/components/ConfidenceGauge";
import { useFormValidation } from "../../../shared/hooks/useFormValidation";
import { decisionSchema } from "../../../shared/lib/validation";
import type { APIResponse } from "../../../shared/types";

type Decision = "approve" | "escalate" | "reject";

interface DecisionPanelProps {
  investigationId: string;
  severity: string | null;
  /** Average confidence across agents (0-1). */
  avgConfidence: number | null;
  onDecisionMade?: (decision: Decision) => void;
}

export function DecisionPanel({
  investigationId,
  avgConfidence,
  onDecisionMade,
}: DecisionPanelProps) {
  const [notes, setNotes] = useState("");
  const [decided, setDecided] = useState<Decision | null>(null);
  const { errors, validate, clearErrors } = useFormValidation(decisionSchema);
  const queryClient = useQueryClient();

  const decisionMutation = useMutation({
    mutationFn: (decision: Decision) =>
      apiClient.post<APIResponse>(`/pipeline/decision/${investigationId}`, {
        decision,
        analyst_notes: notes,
      }),
    onSuccess: (_, decision) => {
      setDecided(decision);
      clearErrors();
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-stats"] });
      onDecisionMade?.(decision);
    },
  });

  /** Validate and submit analyst decision. */
  const handleDecision = (decision: Decision) => {
    const payload = { decision, notes: notes.trim() || undefined };
    if (!validate(payload)) {
      return;
    }
    decisionMutation.mutate(decision);
  };

  if (decided) {
    const labels: Record<
      Decision,
      { text: string; color: string; icon: typeof CheckCircle2 }
    > = {
      approve: {
        text: "Response Approved",
        color: "text-green-400",
        icon: CheckCircle2,
      },
      escalate: {
        text: "Escalated to L3",
        color: "text-orange-400",
        icon: AlertTriangle,
      },
      reject: {
        text: "Investigation Rejected",
        color: "text-red-400",
        icon: XCircle,
      },
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
            <p className="text-xs text-gray-500">
              Decision recorded for {investigationId}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-up rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 p-4 sm:p-6">
      <div className="mb-4 flex items-center gap-3">
        <div className="rounded-lg bg-cyan-500/10 p-2">
          <Shield size={20} className="text-cyan-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">
            Human-in-the-Loop Decision Required
          </h3>
          <p className="text-xs text-gray-400">
            Review the investigation and make a response decision
          </p>
        </div>
        {avgConfidence !== null && avgConfidence > 0 && (
          <div className="ml-auto">
            <ConfidenceGauge score={avgConfidence} size="sm" label="Overall" />
          </div>
        )}
      </div>

      {/* Analyst Notes */}
      <div className="mb-4">
        <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-gray-400">
          <MessageSquare size={12} /> Analyst Notes (optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => {
            setNotes(e.target.value);
            if (Object.keys(errors).length) {
              clearErrors();
            }
          }}
          placeholder="Add investigation notes, observations, or reasoning..."
          rows={2}
          className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-300 placeholder-gray-600 outline-none transition-colors focus:border-cyan-500/30 focus:bg-white/[0.07]"
        />
        {errors.notes && (
          <p className="mt-1 text-xs text-orange-300">{errors.notes}</p>
        )}
      </div>

      {/* Decision Buttons */}
      <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
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
  );
}
