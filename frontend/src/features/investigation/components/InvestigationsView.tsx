/** SOCsentinel — Investigation feature — Pipeline results view. */

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Brain,
  ChevronRight,
  FileText,
  Target,
  Eye,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import { cn, formatConfidence } from "../../../shared/lib/utils";
import type { APIResponse, Investigation, InvestigationSummary } from "../../../shared/types";

function AgentStepCard({
  step,
  data,
  isActive,
  onClick,
}: {
  step: string;
  data: Record<string, unknown> | null;
  isActive: boolean;
  onClick: () => void;
}) {
  const agentIcons: Record<string, typeof Brain> = {
    orchestrator: Shield,
    l1_triage: Eye,
    evidence_collector: Search,
    mitre_mapper: Target,
    report_writer: FileText,
  };
  const Icon = agentIcons[step] || Brain;
  const agentName = (data as Record<string, unknown>)?._agent as string || step;
  const confidence = (data as Record<string, unknown>)?.confidence as number;
  const timeMs = (data as Record<string, unknown>)?._processing_time_ms as number;

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-all",
        isActive
          ? "border-cyan-500/40 bg-cyan-500/10"
          : data
            ? "border-green-500/20 bg-green-500/5 hover:border-green-500/30"
            : "border-white/10 bg-white/5 opacity-50"
      )}
    >
      <div className={cn("rounded-lg p-2", data ? "bg-green-500/10" : "bg-white/5")}>
        <Icon size={16} className={data ? "text-green-400" : "text-gray-500"} />
      </div>
      <div className="flex-1">
        <p className="text-xs font-semibold text-white">{agentName}</p>
        <div className="flex gap-3 text-[10px] text-gray-500">
          {confidence != null && <span>Confidence: {formatConfidence(confidence)}</span>}
          {timeMs != null && <span>{timeMs.toFixed(1)}ms</span>}
        </div>
      </div>
      {data && <CheckCircle2 size={14} className="text-green-400" />}
      <ChevronRight size={14} className="text-gray-500" />
    </button>
  );
}

export function InvestigationsView() {
  const [selectedInv, setSelectedInv] = useState<Investigation | null>(null);
  const [activeStep, setActiveStep] = useState<string>("orchestrator");

  const { data: listData } = useQuery({
    queryKey: ["investigations"],
    queryFn: () => apiClient.get<APIResponse<InvestigationSummary[]>>("/pipeline/list"),
    refetchInterval: 5000,
  });

  const investigations = (listData?.data?.data as InvestigationSummary[]) || [];

  const demoMutation = useMutation({
    mutationFn: (scenario: string) =>
      apiClient.post<APIResponse<Investigation>>(`/pipeline/investigate-demo?scenario=${scenario}`),
    onSuccess: (res) => {
      if (res.data.data) setSelectedInv(res.data.data as Investigation);
    },
  });

  const steps = [
    { key: "orchestrator", dataKey: "orchestrator_result" },
    { key: "l1_triage", dataKey: "triage_result" },
    { key: "evidence_collector", dataKey: "evidence_result" },
    { key: "mitre_mapper", dataKey: "mitre_result" },
    { key: "report_writer", dataKey: "report_result" },
  ] as const;

  const activeData = selectedInv
    ? (selectedInv[steps.find((s) => s.key === activeStep)?.dataKey || "orchestrator_result"] as Record<string, unknown>)
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Investigations</h1>
          <p className="mt-1 text-sm text-gray-400">Multi-agent pipeline results and analysis</p>
        </div>
        <button
          onClick={() => demoMutation.mutate("brute_force")}
          disabled={demoMutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 text-sm font-medium text-white transition-all hover:shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50"
        >
          {demoMutation.isPending ? (
            <><Clock size={16} className="animate-spin" /> Running...</>
          ) : (
            <><Search size={16} /> Run Demo Investigation</>
          )}
        </button>
      </div>

      {selectedInv ? (
        <div className="grid grid-cols-12 gap-4">
          {/* Agent steps sidebar */}
          <div className="col-span-3 space-y-2">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Pipeline Steps</h3>
            {steps.map((step) => (
              <AgentStepCard
                key={step.key}
                step={step.key}
                data={selectedInv[step.dataKey] as Record<string, unknown> | null}
                isActive={activeStep === step.key}
                onClick={() => setActiveStep(step.key)}
              />
            ))}
            <div className="mt-4 rounded-lg border border-white/10 bg-white/5 p-3">
              <p className="text-[10px] uppercase tracking-wider text-gray-500">Total Time</p>
              <p className="text-lg font-bold text-cyan-400">{selectedInv.total_processing_time_ms.toFixed(0)}ms</p>
            </div>
          </div>

          {/* Agent output detail */}
          <div className="col-span-9">
            <div className="glass-card min-h-[400px]">
              <h3 className="mb-4 text-sm font-semibold text-white">
                {(activeData as Record<string, unknown>)?._agent as string || activeStep} Output
              </h3>
              <pre className="overflow-auto rounded-lg bg-navy-950 p-4 font-mono text-xs leading-relaxed text-gray-300">
                {activeData ? JSON.stringify(activeData, null, 2) : "No data available"}
              </pre>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card flex flex-col items-center py-16 text-center">
          <Search size={48} className="mb-4 text-gray-600" />
          <p className="text-sm text-gray-500">No investigation selected</p>
          <p className="mt-1 text-xs text-gray-600">Run a demo investigation or select one from the list</p>
        </div>
      )}
    </div>
  );
}
