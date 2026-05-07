/* eslint-disable @typescript-eslint/no-explicit-any */
/** SOCsentinel — Threat Hunting feature — Proactive threat scenario generation. */

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Crosshair,
  Zap,
  Shield,
  AlertTriangle,
  ChevronRight,
  Loader2,
  Target,
  Terminal,
  Eye,
} from "lucide-react";
import { apiClient } from "../../../shared/lib/api";
import type { APIResponse } from "../../../shared/types";
import { cn } from "../../../shared/lib/utils";

/** Common MITRE ATT&CK techniques for quick selection. */
const COMMON_TECHNIQUES = [
  { id: "T1110", name: "Brute Force", tactic: "Credential Access" },
  { id: "T1059", name: "Command & Scripting Interpreter", tactic: "Execution" },
  { id: "T1021", name: "Remote Services", tactic: "Lateral Movement" },
  { id: "T1048", name: "Exfiltration Over Alternative Protocol", tactic: "Exfiltration" },
  { id: "T1486", name: "Data Encrypted for Impact", tactic: "Impact" },
  { id: "T1566", name: "Phishing", tactic: "Initial Access" },
  { id: "T1078", name: "Valid Accounts", tactic: "Defense Evasion" },
  { id: "T1053", name: "Scheduled Task/Job", tactic: "Persistence" },
];

/** Known APT groups for selection. */
const APT_GROUPS = [
  "generic",
  "APT28 (Fancy Bear)",
  "APT29 (Cozy Bear)",
  "APT41 (Winnti)",
  "Lazarus Group",
  "FIN7",
  "Conti",
  "LockBit",
];

export function ThreatHuntingView() {
  const [techniqueId, setTechniqueId] = useState("");
  const [aptGroup, setAptGroup] = useState("generic");
  const [targetSector, setTargetSector] = useState("general");

  const generateScenario = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<APIResponse>("/threat-generator/generate", {
        technique_id: techniqueId,
        apt_group: aptGroup,
        target_sector: targetSector,
        include_threat_intel: false,
        intel_keywords: [],
      });
      return res.data.data as any;
    },
  });

  const scenario = generateScenario.data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
          <Crosshair size={24} className="text-cyan-400" />
          Threat Hunting
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          Generate proactive attack scenarios based on MITRE ATT&CK techniques for purple team exercises
        </p>
      </div>

      {/* Input Panel */}
      <div className="glass-card space-y-4">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
          <Target size={16} className="text-cyan-400" />
          Scenario Configuration
        </h2>

        {/* Quick technique selection */}
        <div>
          <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-gray-500">
            MITRE ATT&CK Technique
          </label>
          <div className="mb-2 flex flex-wrap gap-2">
            {COMMON_TECHNIQUES.map((t) => (
              <button
                key={t.id}
                onClick={() => setTechniqueId(t.id)}
                className={cn(
                  "rounded-lg border px-3 py-1.5 text-xs font-medium transition-all",
                  techniqueId === t.id
                    ? "border-cyan-500/50 bg-cyan-500/10 text-cyan-400"
                    : "border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-gray-200"
                )}
              >
                <span className="font-mono text-[10px] text-gray-500">{t.id}</span>{" "}
                {t.name}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={techniqueId}
            onChange={(e) => setTechniqueId(e.target.value)}
            placeholder="Or type technique ID (e.g., T1110.001)"
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 font-mono text-sm text-white placeholder-gray-600 focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/30"
          />
        </div>

        {/* APT Group & Sector */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Threat Actor / APT Group
            </label>
            <select
              value={aptGroup}
              onChange={(e) => setAptGroup(e.target.value)}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/30"
            >
              {APT_GROUPS.map((g) => (
                <option key={g} value={g} className="bg-navy-900">
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Target Sector
            </label>
            <select
              value={targetSector}
              onChange={(e) => setTargetSector(e.target.value)}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/30"
            >
              <option value="general" className="bg-navy-900">General</option>
              <option value="finance" className="bg-navy-900">Finance</option>
              <option value="healthcare" className="bg-navy-900">Healthcare</option>
              <option value="energy" className="bg-navy-900">Energy / Utilities</option>
              <option value="government" className="bg-navy-900">Government</option>
              <option value="technology" className="bg-navy-900">Technology</option>
            </select>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={() => generateScenario.mutate()}
          disabled={!techniqueId || generateScenario.isPending}
          className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2.5 text-sm font-bold text-white transition-all hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] disabled:scale-100 disabled:opacity-50"
        >
          {generateScenario.isPending ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Generating Scenario...
            </>
          ) : (
            <>
              <Zap size={16} />
              Generate Attack Scenario
            </>
          )}
        </button>

        {generateScenario.isError && (
          <p className="text-xs text-red-400">
            Failed to generate scenario. Ensure the backend is running.
          </p>
        )}
      </div>

      {/* Scenario Results */}
      {scenario && (
        <div className="space-y-4 animate-slide-up">
          {/* Scenario Header */}
          <div className="glass-card border-l-4 border-l-cyan-500">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">{scenario.scenario_name}</h3>
                <p className="mt-1 text-sm text-gray-400">{scenario.intent}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-gray-300">
                  {scenario.threat_group}
                </span>
                <span className={cn(
                  "rounded-full px-3 py-1 text-xs font-medium",
                  scenario.detection_difficulty === "hard"
                    ? "bg-red-500/20 text-red-400"
                    : scenario.detection_difficulty === "medium"
                    ? "bg-orange-500/20 text-orange-400"
                    : "bg-green-500/20 text-green-400"
                )}>
                  {scenario.detection_difficulty} detection
                </span>
              </div>
            </div>
          </div>

          {/* Attack Chain */}
          <div className="glass-card">
            <h4 className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
              <Shield size={14} /> Attack Chain
            </h4>
            <div className="space-y-3">
              {scenario.attack_chain?.map((step: any, i: number) => (
                <div key={i} className="flex gap-3 rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-600/20 text-xs font-bold text-cyan-400">
                    {step.step || i + 1}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-red-500/20 px-1.5 py-0.5 font-mono text-[10px] text-red-400">
                        {step.technique_id}
                      </span>
                      <span className="text-sm font-medium text-white">{step.technique_name}</span>
                      <ChevronRight size={12} className="text-gray-600" />
                      <span className="text-[10px] uppercase text-gray-500">{step.phase}</span>
                    </div>
                    <p className="text-xs leading-relaxed text-gray-400">{step.description}</p>
                    {step.expected_telemetry && step.expected_telemetry.length > 0 && (
                      <div className="mt-1 flex items-start gap-1">
                        <Eye size={10} className="mt-0.5 shrink-0 text-yellow-500" />
                        <p className="text-[10px] text-yellow-400/80">
                          Telemetry: {step.expected_telemetry.join("; ")}
                        </p>
                      </div>
                    )}
                    {step.detection_opportunity && (
                      <div className="flex items-start gap-1">
                        <AlertTriangle size={10} className="mt-0.5 shrink-0 text-green-500" />
                        <p className="text-[10px] text-green-400/80">
                          Detection: {step.detection_opportunity}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* IOCs & Simulation Commands */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {/* IOCs */}
            {scenario.iocs && scenario.iocs.length > 0 && (
              <div className="glass-card">
                <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-orange-400">
                  <AlertTriangle size={14} /> Indicators of Compromise
                </h4>
                <div className="space-y-1.5">
                  {scenario.iocs.map((ioc: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <span className="rounded bg-orange-500/20 px-1.5 py-0.5 font-mono text-[10px] text-orange-400">
                        {ioc.type}
                      </span>
                      <span className="font-mono text-gray-300">{ioc.value}</span>
                      <span className="ml-auto text-[10px] text-gray-500">{ioc.role}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Simulation Commands */}
            {scenario.simulation_commands && scenario.simulation_commands.length > 0 && (
              <div className="glass-card">
                <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-purple-400">
                  <Terminal size={14} /> Simulation Commands
                </h4>
                <div className="space-y-1.5">
                  {scenario.simulation_commands.map((cmd: string, i: number) => (
                    <div key={i} className="rounded-md bg-black/40 px-3 py-2">
                      <code className="font-mono text-[11px] text-purple-300">{cmd}</code>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!scenario && !generateScenario.isPending && (
        <div className="glass-card flex flex-col items-center py-16 text-center">
          <Crosshair size={48} className="mb-4 text-gray-600" />
          <p className="text-sm text-gray-500">Select a technique and generate a scenario</p>
          <p className="mt-1 text-xs text-gray-600">
            Attack scenarios help validate detection coverage and train SOC analysts
          </p>
        </div>
      )}
    </div>
  );
}
