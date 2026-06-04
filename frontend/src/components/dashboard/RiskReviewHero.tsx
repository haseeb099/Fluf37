"use client";

import { ArrowRight, Play, ShieldCheck, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { useNexusWs } from "@/providers/NexusWebSocketProvider";
import { useNexusStore } from "@/store/nexusStore";
import { PRODUCT_NAME, PRODUCT_WEDGE } from "@/lib/brand";
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
    <section className="hero-panel relative overflow-hidden rounded-2xl border border-sky-500/25 p-6 md:p-10">
      <div className="hero-glow pointer-events-none absolute inset-0" aria-hidden />
      <div className="hero-grid pointer-events-none absolute inset-0 opacity-40" aria-hidden />

      <div className="relative flex flex-col xl:flex-row xl:items-center xl:justify-between gap-8">
        <div className="max-w-2xl space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="border-sky-500/30 text-sky-200">
              {PRODUCT_NAME}
            </Badge>
            <Badge variant="outline">Pilot ready · demo data</Badge>
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

          <div>
            <p className="text-sm font-medium text-sky-300/90 mb-2">{PRODUCT_WEDGE}</p>
            <h1 className="text-3xl md:text-5xl font-bold text-white tracking-tight leading-[1.1]">
              Cross-source risk review
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-sky-300 via-sky-100 to-emerald-300">
                before you approve
              </span>
            </h1>
          </div>

          <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-xl">
            {PRODUCT_NAME} unifies CRM, ERP, banking, trading, and news through a six-agent pipeline —
            blind spots discovered, adversarially tested, traced through memory, and logged for audit replay.
          </p>

          {!complete && blindSpots.length === 0 && !busy && (
            <p className="text-xs text-sky-300/80">
              Click <strong>Run risk review</strong> — typical demo run surfaces 5–7 findings in under a minute.
            </p>
          )}
          {complete && (
            <p className="text-sm text-emerald-300 font-medium">
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

        <div className="flex flex-col items-stretch xl:items-end gap-4 shrink-0 xl:min-w-[240px]">
          <button
            type="button"
            onClick={runPipeline}
            disabled={!isConnected || busy}
            className={cn(
              "cta-button group inline-flex items-center justify-center gap-3 rounded-xl px-10 py-5 text-lg font-semibold",
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
                <Play className="h-6 w-6 fill-current" />
                Run risk review
                <ArrowRight className="h-5 w-5 opacity-70 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </button>

          <div className="rounded-lg border border-white/5 bg-black/20 px-4 py-3 text-center xl:text-right">
            <p className="text-[10px] uppercase tracking-wider text-slate-500">Pipeline state</p>
            <p className="text-sm font-mono text-sky-200 mt-0.5">{pipelineState}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
