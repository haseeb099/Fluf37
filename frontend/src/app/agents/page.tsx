"use client";

import { useNexusStore } from "@/store/nexusStore";

export default function AgentsPage() {
  const tokens = useNexusStore((s) => s.agentTokens);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-cyan-300">Agent Console</h2>
      {Object.entries(tokens).map(([id, text]) => (
        <div key={id} className="glass-panel p-4">
          <h3 className="text-cyan-400 capitalize mb-2">{id}</h3>
          <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap stream-cursor">{text || "—"}</pre>
        </div>
      ))}
      {Object.keys(tokens).length === 0 && (
        <p className="text-slate-500">No agent output yet. Run the pipeline from the sidebar.</p>
      )}
    </div>
  );
}
