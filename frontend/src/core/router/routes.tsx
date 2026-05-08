/** SOCsentinel — AppRoutes component (lazy-loaded pages). */

import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import { AppLayout } from "../../shared/components/layout";
import { RouteLoader } from "../../shared/components/RouteLoader";

const DashboardView = lazy(() =>
  import("../../features/dashboard").then((m) => ({ default: m.DashboardView }))
);
const AlertsView = lazy(() =>
  import("../../features/alerts").then((m) => ({ default: m.AlertsView }))
);
const InvestigationsView = lazy(() =>
  import("../../features/investigation").then((m) => ({ default: m.InvestigationsView }))
);
const ReportsView = lazy(() =>
  import("../../features/reports").then((m) => ({ default: m.ReportsView }))
);
const AuditTrailView = lazy(() =>
  import("../../features/audit").then((m) => ({ default: m.AuditTrailView }))
);
const ThreatHuntingView = lazy(() =>
  import("../../features/threat-hunting").then((m) => ({ default: m.ThreatHuntingView }))
);
const BenchmarkView = lazy(() =>
  import("../../features/benchmark").then((m) => ({ default: m.BenchmarkView }))
);

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Suspense fallback={<RouteLoader />}><DashboardView /></Suspense>} />
        <Route path="alerts" element={<Suspense fallback={<RouteLoader />}><AlertsView /></Suspense>} />
        <Route path="investigation" element={<Suspense fallback={<RouteLoader />}><InvestigationsView /></Suspense>} />
        <Route path="reports" element={<Suspense fallback={<RouteLoader />}><ReportsView /></Suspense>} />
        <Route path="threat-hunting" element={<Suspense fallback={<RouteLoader />}><ThreatHuntingView /></Suspense>} />
        <Route path="audit" element={<Suspense fallback={<RouteLoader />}><AuditTrailView /></Suspense>} />
        <Route path="benchmark" element={<Suspense fallback={<RouteLoader />}><BenchmarkView /></Suspense>} />
      </Route>
    </Routes>
  );
}
