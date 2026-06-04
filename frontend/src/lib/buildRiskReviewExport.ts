import type { BlindSpot, DecisionOutput } from "@/types/nexus";

export type RiskReviewDataMode = "synthetic" | "webhook" | "live" | "mixed";

export interface RiskReviewExport {
  workflow: "pre_release_risk_review";
  generated_at: string;
  data_mode: RiskReviewDataMode;
  correlation_id: string | null;
  summary: {
    blind_spots_count: number;
    decisions_count: number;
    critical_count: number;
    high_count: number;
    top_recommendation: string;
  };
  findings: Array<{
    id: string;
    title: string;
    severity: string;
    description: string;
    confidence: number;
  }>;
  decisions: DecisionOutput[];
}

export function resolveDataMode(usesDemoPipeline: boolean): RiskReviewDataMode {
  return usesDemoPipeline ? "synthetic" : "live";
}

export function buildRiskReviewExport(params: {
  blindSpots: BlindSpot[];
  decisions: DecisionOutput[];
  correlationId: string | null;
  usesDemoPipeline: boolean;
}): RiskReviewExport {
  const { blindSpots, decisions, correlationId, usesDemoPipeline } = params;
  const critical = blindSpots.filter((b) => b.severity === "critical").length;
  const high = blindSpots.filter((b) => b.severity === "high").length;
  const topRec =
    decisions[0]?.recommendation ??
    (blindSpots.length ? "Review findings before release." : "No material risks in this cycle.");

  return {
    workflow: "pre_release_risk_review",
    generated_at: new Date().toISOString(),
    data_mode: resolveDataMode(usesDemoPipeline),
    correlation_id: correlationId,
    summary: {
      blind_spots_count: blindSpots.length,
      decisions_count: decisions.length,
      critical_count: critical,
      high_count: high,
      top_recommendation: topRec,
    },
    findings: blindSpots.map((b) => ({
      id: b.id,
      title: b.title,
      severity: b.severity,
      description: b.description,
      confidence: b.confidence,
    })),
    decisions,
  };
}

export function downloadRiskReviewJson(exportData: RiskReviewExport): void {
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `risk-review-${exportData.correlation_id ?? exportData.generated_at.slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
