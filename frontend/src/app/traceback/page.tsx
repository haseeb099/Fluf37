"use client";

import { useEffect, useState } from "react";
import { getMemoryGraph } from "@/lib/api";

export default function TracebackPage() {
  const [graph, setGraph] = useState<{ nodes: { id: string; type?: string }[]; edges: unknown[] }>({
    nodes: [],
    edges: [],
  });

  useEffect(() => {
    getMemoryGraph()
      .then((g) =>
        setGraph({
          nodes: (g.nodes || []) as { id: string; type?: string }[],
          edges: g.edges || [],
        })
      )
      .catch(() => setGraph({ nodes: [], edges: [] }));
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-cyan-300">Traceback Graph</h2>
      <div className="glass-panel p-4 min-h-[400px]">
        <div className="grid gap-2">
          {graph.nodes.map((n) => (
            <div key={n.id} className="flex items-center gap-2 text-sm border-l-2 border-purple-500 pl-3">
              <span className="text-purple-400">{n.type || "node"}</span>
              <span>{n.id}</span>
            </div>
          ))}
        </div>
        {graph.nodes.length === 0 && <p className="text-slate-500">No graph data. Start backend with demo memory seeded.</p>}
        <p className="text-xs text-slate-600 mt-4">{graph.edges.length} edges · React Flow layout in production build</p>
      </div>
    </div>
  );
}
