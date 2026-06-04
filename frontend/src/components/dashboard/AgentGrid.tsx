"use client";

import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { useNexusStore } from "@/store/nexusStore";
import { getAgentColor } from "@/lib/utils";

const AGENTS = [
  { id: "connector", label: "Connector", desc: "Multi-source sync" },
  { id: "silent_finder", label: "Silent Forcing", desc: "Blind spot detection" },
  { id: "adversarial", label: "Red Team", desc: "Adversarial stress test" },
  { id: "traceback", label: "Traceback", desc: "Historical memory links" },
  { id: "decision", label: "Decision", desc: "CFO recommendations" },
  { id: "evolution", label: "Evolution", desc: "Rule & weight proposals" },
];

export function AgentGrid() {
  const tokens = useNexusStore((s) => s.agentTokens);
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const active = pipelineState !== "IDLE" && pipelineState !== "COMPLETE";

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {AGENTS.map(({ id, label, desc }) => {
        const color = getAgentColor(id);
        const text = tokens[id] || "";
        return (
          <Card
            key={id}
            className="p-5 glass-panel-hover flex flex-col min-h-[200px]"
            style={{ borderColor: `${color}33` }}
          >
            <CardHeader className="mb-3">
              <CardTitle className="text-sm flex items-center gap-2" style={{ color }}>
                <span
                  className="h-2.5 w-2.5 rounded-full shrink-0"
                  style={{
                    background: color,
                    boxShadow: text && active ? `0 0 10px ${color}` : undefined,
                  }}
                />
                {label}
              </CardTitle>
              <p className="text-[11px] text-muted mt-1">{desc}</p>
            </CardHeader>
            <div
              className={`flex-1 text-xs text-slate-300 font-mono leading-relaxed rounded-lg bg-slate-950/50 border border-border/60 p-3 overflow-auto max-h-48 ${
                text ? "stream-cursor" : ""
              }`}
            >
              {text || (
                <span className="text-slate-500 italic">Waiting for pipeline…</span>
              )}
            </div>
          </Card>
        );
      })}
    </div>
  );
}
