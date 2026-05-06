/** SOCsentinel — Lightweight form validation hook. */

import { useState } from "react";
import type { ZodSchema, ZodError } from "zod";
import { formatZodErrors } from "../lib/validation";

export interface ValidationState {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Validate payloads with a Zod schema and return field errors.
 */
export function useFormValidation<T>(schema: ZodSchema<T>) {
  const [state, setState] = useState<ValidationState>({
    isValid: true,
    errors: {},
  });

  const validate = (payload: unknown): payload is T => {
    const result = schema.safeParse(payload);
    if (result.success) {
      setState({ isValid: true, errors: {} });
      return true;
    }

    const zodError = result.error as ZodError;
    setState({ isValid: false, errors: formatZodErrors(zodError) });
    return false;
  };

  const clearErrors = () => setState({ isValid: true, errors: {} });

  return { ...state, validate, clearErrors };
}
