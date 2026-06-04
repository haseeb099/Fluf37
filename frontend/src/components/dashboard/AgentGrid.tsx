"use client";

import { useNexusStore } from "@/store/nexusStore";
import { getAgentColor } from "@/lib/utils";

const AGENTS = ["connector", "silent_finder", "adversarial", "traceback", "decision", "evolution"];

export function AgentGrid() {
  const tokens = useNexusStore((s) => s.agentTokens);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
      {AGENTS.map((id) => (
        <div
          key={id}
          className="glass-panel p-4"
          style={{ borderColor: `${getAgentColor(id)}33` }}
        >
          <h3 className="text-sm font-medium capitalize" style={{ color: getAgentColor(id) }}>
            {id.replace("_", " ")}
          </h3>
          <p className="text-xs text-slate-400 mt-2 font-mono line-clamp-4">
            {(tokens[id] || "Waiting...").slice(-200)}
          </p>
        </div>
      ))}
    </div>
  );
}
