/** SOCsentinel — Reports feature — Investigation Reports view. */

import { useQuery } from "@tanstack/react-query";
import {
  FileText,
  Shield,
  AlertTriangle,
  Target,
  ChevronDown,
  ChevronUp,
  Clock,
  CheckCircle2,
} from "lucide-react";
import { useState } from "react";
import { apiClient } from "../../../shared/lib/api";
import {
  getSeverityBadgeClass,
  formatRelativeTime,
  formatConfidence,
} from "../../../shared/lib/utils";
import type { APIResponse, Investigation } from "../../../shared/types";

function ReportCard({ investigation }: { investigation: Investigation }) {
  const [expanded, setExpanded] = useState(false);
  const report = investigation.report_result;
  const mitre = investigation.mitre_result;
  const triage = investigation.triage_result;
  const evidence = investigation.evidence_result;

  return (
    <div className="glass-card animate-slide-up overflow-hidden transition-all">
      {/* Header */}
      <div
        className="flex cursor-pointer items-start justify-between gap-4"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className={getSeverityBadgeClass(investigation.alert?.severity || "info")}>
              {(investigation.alert?.severity || "info").toUpperCase()}
            </span>
            <span className="font-mono text-xs text-gray-500">
              {investigation.investigation_id}
            </span>
            <span className="flex items-center gap-1 text-xs text-green-400">
              <CheckCircle2 size={12} /> {investigation.status}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-white">
            {report?.title || investigation.alert?.rule_name || "Investigation Report"}
          </h3>
          <p className="line-clamp-2 text-xs leading-relaxed text-gray-400">
            {report?.executive_summary || "Report pending..."}
          </p>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {investigation.total_processing_time_ms
                ? `${investigation.total_processing_time_ms.toFixed(0)}ms`
                : "N/A"}
            </span>
            {investigation.started_at && (
              <span>{formatRelativeTime(investigation.started_at)}</span>
            )}
          </div>
        </div>
        <button className="rounded-lg bg-white/5 p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-white">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Expanded Report Detail */}
      {expanded && (
        <div className="mt-4 space-y-4 border-t border-white/10 pt-4">
          {/* Executive Summary */}
          {report?.executive_summary && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <Shield size={14} /> Executive Summary
              </h4>
              <p className="rounded-lg bg-white/5 p-3 text-xs leading-relaxed text-gray-300">
                {report.executive_summary}
              </p>
            </div>
          )}

          {/* Triage Result */}
          {triage && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <AlertTriangle size={14} /> Triage Analysis
              </h4>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {triage.classification && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Classification</p>
                    <p className="text-sm font-semibold text-white">{triage.classification}</p>
                  </div>
                )}
                {triage.severity && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Severity</p>
                    <p className="text-sm font-semibold text-white">{triage.severity}</p>
                  </div>
                )}
                {triage.confidence !== undefined && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Confidence</p>
                    <p className="text-sm font-semibold text-cyan-400">
                      {formatConfidence(triage.confidence)}
                    </p>
                  </div>
                )}
                {triage.false_positive_probability !== undefined && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">FP Probability</p>
                    <p className="text-sm font-semibold text-orange-400">
                      {formatConfidence(triage.false_positive_probability)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* MITRE ATT&CK Techniques */}
          {mitre?.techniques && mitre.techniques.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <Target size={14} /> MITRE ATT&CK Mapping
              </h4>
              <div className="space-y-1.5">
                {mitre.techniques.map((t: Record<string, string>, i: number) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 rounded-lg bg-white/5 px-3 py-2"
                  >
                    <span className="rounded bg-red-500/20 px-1.5 py-0.5 font-mono text-[10px] text-red-400">
                      {t.technique_id || t.id || `T${1000 + i}`}
                    </span>
                    <span className="text-xs text-gray-300">{t.name || t.technique_name}</span>
                    {t.tactic && (
                      <span className="ml-auto text-[10px] text-gray-500">{t.tactic}</span>
                    )}
                  </div>
                ))}
              </div>
              {mitre.kill_chain_phase && (
                <p className="mt-2 text-xs text-gray-400">
                  <strong className="text-gray-300">Kill Chain Phase:</strong>{" "}
                  {mitre.kill_chain_phase}
                </p>
              )}
            </div>
          )}

          {/* IOCs */}
          {evidence?.iocs && evidence.iocs.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <AlertTriangle size={14} /> Indicators of Compromise
              </h4>
              <div className="space-y-1">
                {evidence.iocs.map((ioc: Record<string, string>, i: number) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="rounded bg-orange-500/20 px-1.5 py-0.5 font-mono text-[10px] text-orange-400">
                      {ioc.type || "IOC"}
                    </span>
                    <span className="font-mono text-gray-300">{ioc.value || JSON.stringify(ioc)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {report?.recommendations && report.recommendations.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                Recommendations
              </h4>
              <ul className="space-y-1">
                {report.recommendations.map((rec: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                    <span className="mt-0.5 text-cyan-400">→</span> {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ReportsView() {
  const { data: investigations, isLoading } = useQuery<Investigation[]>({
    queryKey: ["investigations-full"],
    queryFn: async () => {
      const res = await apiClient.get<APIResponse<Investigation[]>>("/pipeline/list");
      const summaries = (res.data.data as Investigation[]) || [];

      // Fetch full data for each completed investigation
      const full = await Promise.all(
        summaries
          .filter((s) => s.status === "completed")
          .map(async (s) => {
            try {
              const detail = await apiClient.get<APIResponse<Investigation>>(
                `/pipeline/status/${s.investigation_id}`
              );
              return detail.data.data as Investigation;
            } catch {
              return s;
            }
          })
      );
      return full;
    },
    refetchInterval: 15_000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Investigation Reports</h1>
        <p className="mt-1 text-sm text-gray-400">
          Completed investigations with full agent analysis and recommendations
        </p>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-card h-28 animate-pulse" />
            ))}
          </div>
        ) : !investigations || investigations.length === 0 ? (
          <div className="glass-card flex flex-col items-center py-16 text-center">
            <FileText size={48} className="mb-4 text-gray-600" />
            <p className="text-sm text-gray-500">No completed investigations yet</p>
            <p className="mt-1 text-xs text-gray-600">
              Run an investigation from the Alerts page to generate reports
            </p>
          </div>
        ) : (
          investigations.map((inv) => (
            <ReportCard key={inv.investigation_id} investigation={inv} />
          ))
        )}
      </div>
    </div>
  );
}
