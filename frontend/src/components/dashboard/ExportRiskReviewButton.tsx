"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { buildRiskReviewExport, downloadRiskReviewJson } from "@/lib/buildRiskReviewExport";
import { useHealthStatus } from "@/hooks/useHealthStatus";
import { useNexusStore } from "@/store/nexusStore";

export function ExportRiskReviewButton({ onExported }: { onExported?: () => void }) {
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const decisions = useNexusStore((s) => s.decisions);
  const correlationId = useNexusStore((s) => s.correlationId);
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const health = useHealthStatus();

  const ready = pipelineState === "COMPLETE" && blindSpots.length > 0;

  if (!ready) return null;

  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={() => {
        const payload = buildRiskReviewExport({
          blindSpots,
          decisions,
          correlationId,
          usesDemoPipeline: health?.uses_demo_pipeline ?? true,
        });
        downloadRiskReviewJson(payload);
        onExported?.();
      }}
    >
      <Download className="h-4 w-4" />
      Export review (JSON)
    </Button>
  );
}
