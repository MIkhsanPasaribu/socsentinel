/** SOCsentinel — Utility functions. */

import { clsx, type ClassValue } from "clsx";

/** Merge CSS class names conditionally. */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

/** Format a timestamp to human-readable relative time. */
export function formatRelativeTime(date: Date | string): string {
  const now = new Date();
  const target = new Date(date);
  if (isNaN(target.getTime())) return "N/A";
  const diffMs = now.getTime() - target.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${diffDay}d ago`;
}

/** Format confidence score as percentage. */
export function formatConfidence(score: number): string {
  return `${(score * 100).toFixed(0)}%`;
}

/** Get severity badge class name. */
export function getSeverityBadgeClass(severity: string): string {
  const map: Record<string, string> = {
    critical: "badge-critical",
    high: "badge-high",
    medium: "badge-medium",
    low: "badge-low",
    info: "badge-info",
  };
  return map[severity.toLowerCase()] || "badge-info";
}
