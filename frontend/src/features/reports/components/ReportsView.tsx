/* eslint-disable @typescript-eslint/no-explicit-any */
/** SOCsentinel — Reports feature — Investigation Reports view. */

import {
  FileText,
  Shield,
  AlertTriangle,
  Target,
  ChevronDown,
  ChevronUp,
  Clock,
  CheckCircle2,
  Zap,
  Code,
  Download,
  Copy,
  Cpu,
} from "lucide-react";
import { useState } from "react";
import {
  getSeverityBadgeClass,
  formatRelativeTime,
  formatConfidence,
  cn,
} from "../../../shared/lib/utils";
import { useInvestigationsFull } from "../../../shared/hooks/useInvestigations";
import type { Investigation } from "../../../shared/types";
import { ExportButtons } from "./ExportButtons";
import { SoarExportButton } from "./SoarExportButton";

/** Download text content as a file. */
function downloadAsFile(content: string, filename: string) {
  const blob = new Blob([content], { type: "text/yaml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function ReportCard({ investigation }: { investigation: Investigation }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const report = investigation.report_result;
  const mitre = investigation.mitre_result;
  const triage = investigation.triage_result;
  const evidence = investigation.evidence_result;
  const detection = investigation.detection_result;
  const response = investigation.response_result;
  const validator = investigation.validator_result;

  return (
    <div className="glass-card animate-slide-up overflow-hidden transition-all">
      {/* Header */}
      <div
        className="flex cursor-pointer flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-4"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="min-w-0 flex-1 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className={getSeverityBadgeClass(investigation.alert?.severity || "info")}>
              {(investigation.alert?.severity || "info").toUpperCase()}
            </span>
            <span className="truncate font-mono text-xs text-gray-500">
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
        <div className="relative flex items-center gap-2 self-end sm:self-start">
          <ExportButtons investigationId={investigation.investigation_id} />
          <SoarExportButton investigationId={investigation.investigation_id} />
          <button className="rounded-lg bg-white/5 p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-white">
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
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
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
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

          {/* Detection Engineering — Sigma Rule (from Detection Agent) */}
          {detection?.sigma_rule && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-yellow-400">
                <Cpu size={14} /> Detection Engineering (Sigma Rule)
              </h4>
              <div className="rounded-lg border border-yellow-500/20 bg-black/40 overflow-hidden">
                <div className="flex items-center justify-between border-b border-yellow-500/20 bg-yellow-500/10 px-3 py-1.5">
                  <span className="font-mono text-[10px] text-yellow-500">
                    detection_rule.yml
                  </span>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(detection.sigma_rule);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      }}
                      className="flex items-center gap-1 rounded bg-white/10 px-2 py-0.5 text-[10px] text-gray-300 transition-colors hover:bg-white/20 hover:text-white"
                    >
                      <Copy size={10} />
                      {copied ? "Copied!" : "Copy"}
                    </button>
                    <button
                      onClick={() => downloadAsFile(detection.sigma_rule, `sigma_rule_${investigation.investigation_id}.yml`)}
                      className="flex items-center gap-1 rounded bg-yellow-500/20 px-2 py-0.5 text-[10px] text-yellow-400 transition-colors hover:bg-yellow-500/30 hover:text-yellow-300"
                    >
                      <Download size={10} />
                      .yml
                    </button>
                  </div>
                </div>
                <pre className="overflow-x-auto whitespace-pre-wrap p-3 font-mono text-xs text-yellow-100">
                  {detection.sigma_rule}
                </pre>
              </div>

              {/* Detection metadata grid */}
              <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
                {detection.mitre_techniques_mapped && detection.mitre_techniques_mapped.length > 0 && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Techniques</p>
                    <p className="text-xs font-semibold text-red-400">
                      {detection.mitre_techniques_mapped.join(", ")}
                    </p>
                  </div>
                )}
                {detection.false_positive_risk && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">FP Risk</p>
                    <p className={cn(
                      "text-xs font-semibold",
                      detection.false_positive_risk === "high" ? "text-red-400" :
                      detection.false_positive_risk === "medium" ? "text-orange-400" : "text-green-400"
                    )}>
                      {detection.false_positive_risk}
                    </p>
                  </div>
                )}
                {detection.confidence !== undefined && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Confidence</p>
                    <p className="text-xs font-semibold text-cyan-400">
                      {typeof detection.confidence === "number"
                        ? `${(detection.confidence * 100).toFixed(0)}%`
                        : detection.confidence}
                    </p>
                  </div>
                )}
                {detection.recommended_log_sources && detection.recommended_log_sources.length > 0 && (
                  <div className="rounded-lg bg-white/5 p-2.5">
                    <p className="text-[10px] uppercase text-gray-500">Log Sources</p>
                    <p className="text-xs font-semibold text-gray-300">
                      {detection.recommended_log_sources.join(", ")}
                    </p>
                  </div>
                )}
              </div>

              {/* Detection logic explanation */}
              {detection.detection_logic && (
                <p className="mt-2 rounded-lg bg-white/5 p-3 text-xs leading-relaxed text-gray-300">
                  <strong className="text-gray-200">Detection Logic:</strong>{" "}
                  {detection.detection_logic}
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

          {/* Response Playbook */}
          {response && response.steps && response.steps.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
                <Zap size={14} /> Containment Playbook
              </h4>
              <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-sm font-semibold text-emerald-400">
                    {response.playbook_name || "Response Playbook"}
                  </span>
                  <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-medium uppercase text-emerald-400">
                    {response.priority || "Standard"} Priority
                  </span>
                </div>
                
                <div className="space-y-2">
                  {response.steps.map((step: any, i: number) => (
                    <div key={i} className="flex gap-3 rounded-md bg-white/5 p-2">
                      <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-400">
                        {step.order || i + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{step.action}</p>
                        <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-gray-400">
                          <span className="font-mono bg-white/10 px-1 rounded">{step.tool}</span>
                          <span className={step.risk_level === "high" ? "text-red-400" : step.risk_level === "medium" ? "text-orange-400" : "text-green-400"}>
                            Risk: {step.risk_level}
                          </span>
                          {step.automated && <span className="text-cyan-400">Automated</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Validator (Critic) Audit & Sigma Rule */}
          {validator && (
            <div className="space-y-4">
              {/* Validation Status */}
              <div>
                <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-purple-400">
                  <Shield size={14} /> Adversarial Audit
                </h4>
                <div className={cn(
                  "rounded-lg border p-3",
                  validator.is_approved 
                    ? "border-green-500/20 bg-green-500/5" 
                    : "border-red-500/20 bg-red-500/5"
                )}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className={cn(
                      "text-sm font-semibold",
                      validator.is_approved ? "text-green-400" : "text-red-400"
                    )}>
                      {validator.is_approved ? "Playbook Approved" : "Playbook Rejected"}
                    </span>
                    <span className="rounded bg-white/10 px-2 py-0.5 text-[10px] font-medium text-gray-300">
                      Risk Score: {validator.risk_score}
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed text-gray-300">
                    {validator.critic_comments}
                  </p>
                  
                  {validator.safe_alternatives && validator.safe_alternatives.length > 0 && (
                    <div className="mt-3 border-t border-white/10 pt-2">
                      <p className="mb-1 text-[10px] uppercase text-gray-500">Safer Alternatives:</p>
                      <ul className="space-y-1">
                        {validator.safe_alternatives.map((alt: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-orange-400">
                            <span className="mt-0.5 text-orange-500">→</span> {alt}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Sigma Rule Generation */}
              {validator.sigma_rule && (
                <div>
                  <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-yellow-400">
                    <Code size={14} /> On-The-Fly Detection Engineering (Sigma)
                  </h4>
                  <div className="rounded-lg border border-yellow-500/20 bg-black/40 p-0 overflow-hidden">
                    <div className="bg-yellow-500/10 px-3 py-1.5 border-b border-yellow-500/20 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-yellow-500">sigma_rule.yml</span>
                    </div>
                    <pre className="p-3 text-xs text-yellow-100 overflow-x-auto font-mono whitespace-pre-wrap">
                      {validator.sigma_rule}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ReportsView() {
  const { data: investigations, isLoading } = useInvestigationsFull();

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
