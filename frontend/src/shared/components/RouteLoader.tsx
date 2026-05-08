/** SOCsentinel — Route-level loading spinner for lazy-loaded pages. */

import { Loader2 } from "lucide-react";

export function RouteLoader() {
  return (
    <div className="flex h-64 items-center justify-center">
      <Loader2 size={28} className="animate-spin text-cyan-400" />
    </div>
  );
}
