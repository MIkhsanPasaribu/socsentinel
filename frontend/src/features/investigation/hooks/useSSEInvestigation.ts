/** SOCsentinel — SSE investigation streaming hook. */

import { useState, useCallback, useRef } from "react";
import { useToast } from "../../../shared/components/Toast";

export interface SSEAgentEvent {
  investigation_id: string;
  agent_index: number;
  agent_name: string;
  agent_role?: string;
  agent_model?: string;
  step: string;
  processing_time_ms?: number;
  confidence?: number | null;
  classification?: string | null;
  status?: string;
  thinking_content?: string;
}

export interface SSEPipelineEvent {
  investigation_id: string;
  status: string;
  total_processing_time_ms?: number;
  agents_completed?: number;
  early_exit?: boolean;
  reason?: string;
  error?: string;
  alert_id?: string;
  severity?: string;
  rule_name?: string;
  total_agents?: number;
  thinking_mode?: boolean;
}

export type SSEPhase =
  | "idle"
  | "connecting"
  | "streaming"
  | "completed"
  | "failed";

export interface AgentStep {
  index: number;
  name: string;
  role: string;
  model: string;
  step: string;
  status: "pending" | "running" | "completed";
  processing_time_ms?: number;
  confidence?: number | null;
  classification?: string | null;
  thinking_content?: string;
}

export interface SSEState {
  phase: SSEPhase;
  investigationId: string | null;
  alertId: string | null;
  severity: string | null;
  ruleName: string | null;
  agents: AgentStep[];
  totalTimeMs: number | null;
  error: string | null;
  thinkingMode: boolean;
}

const INITIAL_AGENTS: AgentStep[] = [
  {
    index: 0,
    name: "Orchestrator",
    role: "SOC Manager",
    model: "Qwen3-7B",
    step: "orchestrator",
    status: "pending",
  },
  {
    index: 1,
    name: "L1 Triage",
    role: "L1 Analyst",
    model: "Qwen3-4B",
    step: "l1_triage",
    status: "pending",
  },
  {
    index: 2,
    name: "Evidence Collector",
    role: "L2 Analyst",
    model: "Qwen3-7B",
    step: "evidence_collector",
    status: "pending",
  },
  {
    index: 3,
    name: "MITRE Mapper",
    role: "L2/L3 Analyst",
    model: "Qwen3-7B",
    step: "mitre_mapper",
    status: "pending",
  },
  {
    index: 4,
    name: "Detection Agent",
    role: "Detection Engineer",
    model: "Qwen3-7B",
    step: "detection",
    status: "pending",
  },
  {
    index: 5,
    name: "Report Writer",
    role: "Senior Analyst",
    model: "Qwen3-14B",
    step: "report_writer",
    status: "pending",
  },
  {
    index: 6,
    name: "Response Planner",
    role: "L3 Incident Responder",
    model: "Qwen3-14B",
    step: "response_planner",
    status: "pending",
  },
  {
    index: 7,
    name: "Adversarial Validator",
    role: "Red Teamer / Critic",
    model: "Qwen3-7B",
    step: "validator",
    status: "pending",
  },
];

/** Hook to stream an investigation via Server-Sent Events. */
export function useSSEInvestigation(apiUrl: string) {
  const { addToast } = useToast();
  const [state, setState] = useState<SSEState>({
    phase: "idle",
    investigationId: null,
    alertId: null,
    severity: null,
    ruleName: null,
    agents: INITIAL_AGENTS.map((a) => ({ ...a })),
    totalTimeMs: null,
    error: null,
    thinkingMode: false,
  });

  const eventSourceRef = useRef<EventSource | null>(null);

  const startInvestigation = useCallback(
    (
      scenario: string = "brute_force",
      includeThreatScenario: boolean = false,
    ) => {
      // Close any existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Reset state
      setState({
        phase: "connecting",
        investigationId: null,
        alertId: null,
        severity: null,
        ruleName: null,
        agents: INITIAL_AGENTS.map((a) => ({ ...a })),
        totalTimeMs: null,
        error: null,
        thinkingMode: false,
      });

      const es = new EventSource(
        `${apiUrl}/pipeline/stream-investigate?scenario=${scenario}&include_threat_scenario=${includeThreatScenario}`,
      );
      eventSourceRef.current = es;

      es.addEventListener("pipeline_started", (e) => {
        const data: SSEPipelineEvent = JSON.parse(e.data);
        const totalAgents = data.total_agents || INITIAL_AGENTS.length;
        const agents =
          totalAgents === INITIAL_AGENTS.length
            ? INITIAL_AGENTS
            : [
                ...INITIAL_AGENTS.slice(0, 4),
                {
                  index: 4,
                  name: "Threat Generator",
                  role: "Threat Intelligence Analyst",
                  model: "Qwen3-7B",
                  step: "threat_generator",
                  status: "pending" as const,
                },
                ...INITIAL_AGENTS.slice(4).map((agent, idx) => ({
                  ...agent,
                  index: idx + 5,
                })),
              ];

        setState((prev) => ({
          ...prev,
          phase: "streaming",
          investigationId: data.investigation_id,
          alertId: data.alert_id || null,
          severity: data.severity || null,
          ruleName: data.rule_name || null,
          agents: agents.map((agent) => ({ ...agent })),
          thinkingMode: !!data.thinking_mode,
        }));
      });

      es.addEventListener("agent_started", (e) => {
        const data: SSEAgentEvent = JSON.parse(e.data);
        setState((prev) => ({
          ...prev,
          agents: prev.agents.map((a) =>
            a.index === data.agent_index
              ? { ...a, status: "running" as const }
              : a,
          ),
        }));
      });

      es.addEventListener("agent_completed", (e) => {
        const data: SSEAgentEvent = JSON.parse(e.data);

        addToast({
          type: "success",
          title: `${data.agent_name} Completed`,
          message: `Processed in ${data.processing_time_ms?.toFixed(0)}ms. ${
            data.classification
              ? `Result: ${data.classification.toUpperCase()}`
              : ""
          }`,
        });

        setState((prev) => ({
          ...prev,
          agents: prev.agents.map((a) =>
            a.index === data.agent_index
              ? {
                  ...a,
                  status: "completed" as const,
                  processing_time_ms: data.processing_time_ms,
                  confidence: data.confidence,
                  classification: data.classification,
                  thinking_content: data.thinking_content,
                }
              : a,
          ),
        }));
      });

      es.addEventListener("pipeline_completed", (e) => {
        const data: SSEPipelineEvent = JSON.parse(e.data);

        addToast({
          type: data.early_exit ? "info" : "success",
          title: "Investigation Complete",
          message: data.early_exit
            ? `Early exit: ${data.reason}. Total time: ${data.total_processing_time_ms?.toFixed(0)}ms`
            : `All agents finished successfully in ${data.total_processing_time_ms?.toFixed(0)}ms`,
        });

        setState((prev) => ({
          ...prev,
          phase: "completed",
          totalTimeMs: data.total_processing_time_ms || null,
        }));
        es.close();
      });

      es.addEventListener("pipeline_failed", (e) => {
        const data: SSEPipelineEvent = JSON.parse(e.data);
        setState((prev) => ({
          ...prev,
          phase: "failed",
          error: data.error || "Unknown error",
          totalTimeMs: data.total_processing_time_ms || null,
        }));
        es.close();
      });

      es.onerror = () => {
        setState((prev) => ({
          ...prev,
          phase: prev.phase === "streaming" ? "completed" : "failed",
          error: prev.phase === "streaming" ? null : "Connection failed",
        }));
        es.close();
      };
    },
    [apiUrl, addToast],
  );

  const reset = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setState({
      phase: "idle",
      investigationId: null,
      alertId: null,
      severity: null,
      ruleName: null,
      agents: INITIAL_AGENTS.map((a) => ({ ...a })),
      totalTimeMs: null,
      error: null,
      thinkingMode: false,
    });
  }, []);

  return { state, startInvestigation, reset };
}
