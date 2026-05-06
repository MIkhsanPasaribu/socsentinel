/** SOCsentinel — Supported investigation scenarios. */

export const ALERT_SCENARIOS = [
  "brute_force",
  "lateral_movement",
  "data_exfiltration",
  "phishing",
  "ransomware",
] as const;

export type AlertScenario = (typeof ALERT_SCENARIOS)[number];
