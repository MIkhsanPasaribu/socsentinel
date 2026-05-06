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
