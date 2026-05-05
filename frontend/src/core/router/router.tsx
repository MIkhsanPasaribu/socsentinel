/** SOCsentinel — Application router configuration. */

import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../../shared/components/layout";
import { DashboardView } from "../../features/dashboard";
import { AlertsView } from "../../features/alerts";
import { InvestigationsView } from "../../features/investigation";
import { ReportsView } from "../../features/reports";
import { AuditTrailView } from "../../features/audit";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardView /> },
      { path: "alerts", element: <AlertsView /> },
      { path: "investigation", element: <InvestigationsView /> },
      { path: "reports", element: <ReportsView /> },
      { path: "audit", element: <AuditTrailView /> },
    ],
  },
]);
