"use client";

import { AgentGrid } from "@/components/dashboard/AgentGrid";
import { useNexusStore } from "@/store/nexusStore";

export default function DashboardPage() {
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const pipelineState = useNexusStore((s) => s.pipelineState);

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-cyan-300">Dashboard</h2>
        <p className="text-slate-400 text-sm">Pipeline: {pipelineState}</p>
      </header>
      <AgentGrid />
      <section>
        <h3 className="text-lg mb-3">Blind Spots ({blindSpots.length})</h3>
        <div className="space-y-2">
          {blindSpots.map((bs) => (
            <div key={bs.id} className="glass-panel p-3">
              <span className="text-xs uppercase text-red-400">{bs.severity}</span>
              <h4 className="font-medium">{bs.title}</h4>
              <p className="text-sm text-slate-400">{bs.description}</p>
            </div>
          ))}
          {blindSpots.length === 0 && (
            <p className="text-slate-500 text-sm">Run pipeline to detect blind spots.</p>
          )}
        </div>
      </section>
    </div>
  );
}
