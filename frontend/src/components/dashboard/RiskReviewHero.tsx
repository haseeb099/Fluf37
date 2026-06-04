"use client";

import { ArrowRight, Play, ShieldCheck, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useNexusWs } from "@/providers/NexusWebSocketProvider";
import { useNexusStore } from "@/store/nexusStore";
import { cn } from "@/lib/utils";

export function RiskReviewHero() {
  const { runPipeline, isConnected, lastError } = useNexusWs();
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const decisions = useNexusStore((s) => s.decisions);

  const busy =
    pipelineState !== "IDLE" && pipelineState !== "COMPLETE" && pipelineState !== "ERROR";
  const complete = pipelineState === "COMPLETE";
  const critical = blindSpots.filter((b) => b.severity === "critical").length;

  return (
    <section className="hero-panel relative overflow-hidden rounded-2xl border border-sky-500/20 p-6 md:p-8">
      <div className="hero-glow pointer-events-none absolute inset-0" aria-hidden />

      <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="max-w-xl space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">CFO command center</Badge>
            {isConnected ? (
              <Badge variant="success">
                <Wifi className="h-3 w-3 mr-1 inline" />
                Live stream
              </Badge>
            ) : (
              <Badge variant="critical">
                <WifiOff className="h-3 w-3 mr-1 inline" />
                Disconnected
              </Badge>
            )}
            {complete && (
              <Badge variant="success">
                <ShieldCheck className="h-3 w-3 mr-1 inline" />
                Review complete
              </Badge>
            )}
          </div>

          <h1 className="text-2xl md:text-4xl font-bold text-white tracking-tight leading-tight">
            Pre-release risk review
          </h1>
          <p className="text-slate-300 text-sm md:text-base leading-relaxed">
            Run a full six-agent scan across CRM, ERP, banking, and markets before you approve wires,
            credit lines, or major deal terms.
          </p>

          {!complete && blindSpots.length === 0 && !busy && (
            <p className="text-xs text-sky-300/80">
              No findings yet — start a review to surface cross-source blind spots.
            </p>
          )}
          {complete && (
            <p className="text-sm text-emerald-300">
              {blindSpots.length} finding(s) · {decisions.length} decision(s) ready for sign-off
              {critical > 0 && ` · ${critical} critical`}
            </p>
          )}
          {lastError && (
            <p className="text-sm text-red-400" role="alert">
              {lastError}
            </p>
          )}
        </div>

        <div className="flex flex-col sm:flex-row lg:flex-col items-stretch sm:items-center lg:items-end gap-3 shrink-0">
          <button
            type="button"
            onClick={runPipeline}
            disabled={!isConnected || busy}
            className={cn(
              "cta-button group inline-flex items-center justify-center gap-3 rounded-xl px-8 py-4 text-base font-semibold",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            )}
          >
            {busy ? (
              <>
                <span className="h-5 w-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                Review in progress…
              </>
            ) : (
              <>
                <Play className="h-5 w-5 fill-current" />
                Run risk review
                <ArrowRight className="h-4 w-4 opacity-70 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </button>

          <p className="text-[11px] text-slate-400 text-center lg:text-right">
            Pipeline: <span className="text-slate-200 font-medium">{pipelineState}</span>
          </p>
        </div>
      </div>
    </section>
  );
}
