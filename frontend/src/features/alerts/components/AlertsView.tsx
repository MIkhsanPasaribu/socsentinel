/** SOCsentinel — Alerts feature — Alert Queue view. */

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Bell, RefreshCw, Clock, Server, ArrowRight } from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import {
  formatRelativeTime,
  getSeverityBadgeClass,
} from "../../../shared/lib/utils";
import { ALERT_SCENARIOS } from "../../../core/constants/scenarios";
import { useFormValidation } from "../../../shared/hooks/useFormValidation";
import { scenarioSchema } from "../../../shared/lib/validation";
import type { Alert, APIResponse } from "../../../shared/types";

function AlertCard({
  alert,
  onInvestigate,
}: {
  alert: Alert;
  onInvestigate: (a: Alert) => void;
}) {
  return (
    <div className="glass-card animate-slide-up flex flex-col gap-3 transition-all hover:border-cyan-500/30 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className={getSeverityBadgeClass(alert.severity)}>
            {alert.severity.toUpperCase()}
          </span>
          <span className="font-mono text-xs text-gray-500">
            {alert.alert_id}
          </span>
        </div>
        <h3 className="text-sm font-semibold text-white">{alert.rule_name}</h3>
        <p className="text-xs leading-relaxed text-gray-400">
          {alert.description}
        </p>
        <div className="flex flex-wrap gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Server size={12} /> {alert.source_ip} → {alert.destination_ip}
          </span>
          <span className="flex items-center gap-1">
            <Clock size={12} /> {formatRelativeTime(alert.timestamp)}
          </span>
          {alert.username && <span>👤 {alert.username}</span>}
          {alert.hostname && <span>🖥 {alert.hostname}</span>}
        </div>
      </div>
      <button
        onClick={() => onInvestigate(alert)}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-cyan-500/10 px-3 py-2 text-xs font-medium text-cyan-400 transition-all hover:bg-cyan-500/20 hover:shadow-lg hover:shadow-cyan-500/10 sm:w-auto sm:justify-start"
      >
        Investigate <ArrowRight size={14} />
      </button>
    </div>
  );
}

export function AlertsView() {
  const queryClient = useQueryClient();
  const [investigating, setInvestigating] = useState<string | null>(null);
  const { errors, validate, clearErrors } = useFormValidation(scenarioSchema);

  const generateMutation = useMutation({
    mutationFn: (scenario?: string) =>
      apiClient.post<APIResponse<Alert>>(
        `/alerts/generate${scenario ? `?scenario=${scenario}` : ""}`,
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const investigateMutation = useMutation({
    mutationFn: (alert: Alert) =>
      apiClient.post<APIResponse>("/pipeline/investigate", alert),
    onSuccess: () => {
      setInvestigating(null);
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });

  const [alerts, setAlerts] = useState<Alert[]>([]);

  const handleGenerate = async (scenario?: string) => {
    if (scenario && !validate(scenario)) {
      return;
    }
    const res = await generateMutation.mutateAsync(scenario);
    if (res.data.data) {
      setAlerts((prev) => [res.data.data as Alert, ...prev]);
    }
  };

  const handleInvestigate = async (alert: Alert) => {
    setInvestigating(alert.alert_id);
    await investigateMutation.mutateAsync(alert);
  };

  const scenarios = ALERT_SCENARIOS;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Alert Queue</h1>
          <p className="mt-1 text-sm text-gray-400">
            Incoming SIEM alerts awaiting triage and investigation
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {scenarios.map((s) => (
            <button
              key={s}
              onClick={() => {
                clearErrors();
                handleGenerate(s);
              }}
              disabled={generateMutation.isPending}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-gray-300 transition-all hover:border-cyan-500/30 hover:bg-cyan-500/10 hover:text-cyan-400 disabled:opacity-50"
            >
              {s.replace("_", " ")}
            </button>
          ))}
          {errors._global && (
            <p className="text-xs text-orange-300">{errors._global}</p>
          )}
        </div>
      </div>

      {/* Alert list */}
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="glass-card flex flex-col items-center py-16 text-center">
            <Bell size={48} className="mb-4 text-gray-600" />
            <p className="text-sm text-gray-500">No alerts in queue</p>
            <p className="mt-1 text-xs text-gray-600">
              Generate synthetic alerts using the buttons above
            </p>
          </div>
        ) : (
          alerts.map((alert) => (
            <AlertCard
              key={alert.alert_id}
              alert={alert}
              onInvestigate={handleInvestigate}
            />
          ))
        )}
      </div>

      {/* Investigation progress */}
      {investigating && (
        <div className="fixed bottom-6 right-3 left-3 z-50 max-w-[calc(100vw-1.5rem)] animate-slide-up rounded-xl border border-cyan-500/30 bg-navy-900/95 p-4 shadow-2xl backdrop-blur-xl glow-cyan sm:left-auto sm:right-6 sm:max-w-sm">
          <div className="flex items-center gap-3">
            <RefreshCw size={18} className="animate-spin text-cyan-400" />
            <div>
              <p className="text-sm font-medium text-white">
                Investigation in progress...
              </p>
              <p className="text-xs text-gray-400">
                Running multi-agent pipeline on {investigating}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
