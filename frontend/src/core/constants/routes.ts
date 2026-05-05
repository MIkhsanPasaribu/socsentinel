/** SOCsentinel — Route path constants. */

export const ROUTES = {
  DASHBOARD: "/",
  ALERTS: "/alerts",
  ALERT_DETAIL: "/alerts/:id",
  INVESTIGATION: "/investigation/:id",
  REPORTS: "/reports",
  REPORT_DETAIL: "/reports/:id",
  AUDIT: "/audit",
} as const;
