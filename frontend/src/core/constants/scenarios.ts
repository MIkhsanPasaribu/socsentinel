/** SOCsentinel — Supported investigation scenarios. */

export const ALERT_SCENARIOS = [
  "brute_force",
  "lateral_movement",
  "data_exfiltration",
  "phishing",
  "ransomware",
  "privilege_escalation",
  "supply_chain",
  "insider_threat",
  "cryptomining",
] as const;

export type AlertScenario = (typeof ALERT_SCENARIOS)[number];
