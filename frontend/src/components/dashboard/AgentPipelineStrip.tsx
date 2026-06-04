"use client";

import { useNexusStore } from "@/store/nexusStore";
import { cn } from "@/lib/utils";

const AGENTS = [
  { id: "connector", label: "Connector", color: "var(--agent-connector)" },
  { id: "finder", label: "Blind spots", color: "var(--agent-finder)" },
  { id: "adversarial", label: "Red team", color: "var(--agent-adversarial)" },
  { id: "traceback", label: "Traceback", color: "var(--agent-traceback)" },
  { id: "decision", label: "Decision", color: "var(--agent-decision)" },
  { id: "evolution", label: "Evolution", color: "var(--agent-evolution)" },
] as const;

const STATE_ORDER = [
  "IDLE",
  "CONNECTING",
  "CONNECTED",
  "ANALYZING",
  "ATTACKING",
  "TRACING",
  "DECIDING",
  "EVOLVING",
  "COMPLETE",
] as const;

function activeAgentIndex(state: string): number {
  const map: Record<string, number> = {
    IDLE: -1,
    CONNECTING: 0,
    CONNECTED: 0,
    ANALYZING: 1,
    ATTACKING: 2,
    TRACING: 3,
    DECIDING: 4,
    EVOLVING: 5,
    COMPLETE: 6,
    ERROR: -1,
  };
  return map[state] ?? -1;
}

export function AgentPipelineStrip() {
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const active = activeAgentIndex(pipelineState);
  const complete = pipelineState === "COMPLETE";
  const running = active >= 0 && !complete && pipelineState !== "ERROR";

  return (
    <section className="pipeline-strip rounded-xl border border-border/80 bg-surface/60 p-4 md:p-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-sky-400">
            Six-agent pipeline
          </p>
          <p className="text-[11px] text-muted mt-0.5">
            Orchestrated review — not a single chat prompt
          </p>
        </div>
        <span className="text-[11px] font-mono text-slate-500">{pipelineState}</span>
      </div>

      <ol className="flex flex-wrap md:flex-nowrap items-stretch gap-1 md:gap-0">
        {AGENTS.map((agent, i) => {
          const isActive = running && active === i;
          const isDone = complete || active > i;
          return (
            <li
              key={agent.id}
              className={cn(
                "pipeline-node flex-1 min-w-[4.5rem] relative flex flex-col items-center text-center px-1 py-2 rounded-lg transition-all",
                isActive && "pipeline-node-active",
                isDone && !isActive && "opacity-100",
                !isDone && !isActive && "opacity-45"
              )}
            >
              {i > 0 && (
                <span
                  className="hidden md:block absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-2 h-px bg-slate-700"
                  aria-hidden
                />
              )}
              <span
                className={cn(
                  "h-2.5 w-2.5 rounded-full mb-2 transition-all",
                  isActive && "scale-125 animate-pulse ring-2 ring-sky-400/60 ring-offset-2 ring-offset-surface"
                )}
                style={{
                  backgroundColor: agent.color,
                  boxShadow: isActive ? `0 0 12px ${agent.color}` : undefined,
                }}
              />
              <span className="text-[10px] font-medium text-slate-300 leading-tight">
                {agent.label}
              </span>
            </li>
          );
        })}
      </ol>

      <p className="text-[10px] text-slate-600 mt-3 font-mono">
        {STATE_ORDER.join(" → ")}
      </p>
    </section>
  );
}
