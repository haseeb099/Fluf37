"use client";

import { AlertTriangle, Database } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useHealthStatus } from "@/hooks/useHealthStatus";
import { useNexusStore } from "@/store/nexusStore";

export function ReviewDataModeBanner() {
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const correlationId = useNexusStore((s) => s.correlationId);
  const health = useHealthStatus();

  if (pipelineState !== "COMPLETE" || blindSpots.length === 0) return null;

  const synthetic = health?.uses_demo_pipeline ?? true;
  const label = synthetic ? "Synthetic pilot data" : "Live connector data";

  return (
    <div
      className="flex flex-wrap items-center gap-2 rounded-lg border border-amber-500/25 bg-amber-950/20 px-4 py-3 text-sm"
      role="status"
    >
      <Database className="h-4 w-4 text-amber-400 shrink-0" />
      <span className="text-amber-100/90">
        This review used <strong>{label}</strong>
        {correlationId ? ` · correlation ${correlationId.slice(0, 12)}…` : ""}.
      </span>
      {synthetic && (
        <Badge variant="warning" className="ml-auto">
          <AlertTriangle className="h-3 w-3 mr-1 inline" />
          Not customer production data
        </Badge>
      )}
    </div>
  );
}
