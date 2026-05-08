/** SOCsentinel — Shared form validation schemas. */

import { z } from "zod";
import { ALERT_SCENARIOS } from "../../core/constants/scenarios";

export const scenarioSchema = z.enum(ALERT_SCENARIOS, {
  message: "Select a valid scenario.",
});

const decisionOptions = ["approve", "escalate", "reject"] as const;

export const decisionSchema = z
  .object({
    decision: z.enum(decisionOptions, {
      message: "Select a valid decision.",
    }),
    notes: z
      .string()
      .trim()
      .max(500, "Notes must be 500 characters or fewer.")
      .optional(),
    confidence_override: z
      .number()
      .min(0, "Confidence must be between 0 and 1.")
      .max(1, "Confidence must be between 0 and 1.")
      .nullable()
      .optional(),
    severity_override: z.string().nullable().optional(),
  })
  .superRefine((value, ctx) => {
    if (
      (value.decision === "reject" || value.decision === "escalate") &&
      !value.notes
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["notes"],
        message: "Notes are required for escalation or rejection.",
      });
    }
    if (value.confidence_override != null && !value.notes) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["notes"],
        message: "Notes are required when overriding confidence.",
      });
    }
  });

export type DecisionInput = z.infer<typeof decisionSchema>;
export type ScenarioInput = z.infer<typeof scenarioSchema>;

/** Convert Zod errors into a simple field->message map. */
export function formatZodErrors(error: z.ZodError): Record<string, string> {
  return error.issues.reduce<Record<string, string>>(
    (acc, issue: z.ZodIssue) => {
      const key = issue.path.join(".") || "_global";
      acc[key] = issue.message;
      return acc;
    },
    {},
  );
}
