"use client";

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { useNexusStore } from "@/store/nexusStore";
import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const STEPS = [
  { key: "CONNECTED", label: "Ingest", desc: "Sync plugins & sources" },
  { key: "ANALYZING", label: "Blind spots", desc: "Cross-source gaps" },
  { key: "ATTACKING", label: "Stress test", desc: "Adversarial pass" },
  { key: "TRACING", label: "Memory", desc: "Historical traceback" },
  { key: "DECIDING", label: "Decisions", desc: "CFO recommendations" },
] as const;

function stepIndex(state: string): number {
  const order = [
    "IDLE", "CONNECTING", "CONNECTED", "ANALYZING", "ATTACKING",
    "TRACING", "DECIDING", "EVOLVING", "COMPLETE", "ERROR",
  ];
  return order.indexOf(state);
}

export function RiskReviewWorkflow() {
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const decisions = useNexusStore((s) => s.decisions);
  const current = stepIndex(pipelineState);
  const complete = pipelineState === "COMPLETE";
  const running = !complete && pipelineState !== "IDLE" && pipelineState !== "ERROR";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Review workflow</CardTitle>
        <CardDescription>
          Five-stage pipeline before approving wires, credit lines, or large deal terms.
        </CardDescription>
      </CardHeader>

      <ol className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {STEPS.map((step) => {
          const stepStateIdx = stepIndex(step.key);
          const active = current === stepStateIdx || (running && current === stepStateIdx - 1);
          const done = complete || current > stepStateIdx;
          return (
            <li
              key={step.key}
              className={cn(
                "rounded-lg border p-3 transition-all",
                active && "border-sky-500/50 bg-sky-500/10 shadow-glow",
                done && !active && "border-emerald-500/30 bg-emerald-500/5",
                !done && !active && "border-border bg-slate-900/30"
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                {done ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 text-sky-400 animate-spin shrink-0" />
                ) : (
                  <Circle className="h-4 w-4 text-slate-600 shrink-0" />
                )}
                <span className="text-xs font-semibold text-slate-200">{step.label}</span>
              </div>
              <p className="text-[10px] text-muted pl-6">{step.desc}</p>
            </li>
          );
        })}
      </ol>

      {complete && (
        <p className="text-sm text-emerald-400 mt-4 pt-4 border-t border-border">
          Review complete — {blindSpots.length} finding(s), {decisions.length} decision(s) ready for
          committee sign-off.
        </p>
      )}
    </Card>
  );
}
