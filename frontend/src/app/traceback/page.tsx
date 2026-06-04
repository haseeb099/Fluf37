"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { ReactFlowProvider } from "reactflow";
import { FailureTimeline } from "@/components/traceback/FailureTimeline";
import type { GraphEdgeData, GraphNodeData } from "@/types/graph";
import { fetchAuthToken, getMemoryGraph } from "@/lib/api";

const TraceGraph = dynamic(
  () => import("@/components/traceback/TraceGraph").then((mod) => mod.TraceGraph),
  {
    ssr: false,
    loading: () => <p className="text-slate-500 text-sm p-4">Loading graph…</p>,
  }
);

export default function TracebackPage() {
  const [nodes, setNodes] = useState<GraphNodeData[]>([]);
  const [edges, setEdges] = useState<GraphEdgeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightId, setHighlightId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAuthToken("viewer")
      .catch(() => undefined)
      .then(() => getMemoryGraph())
      .then((g) => {
        setNodes((g.nodes || []) as GraphNodeData[]);
        setEdges((g.edges || []) as GraphEdgeData[]);
      })
      .catch((e) => {
        setNodes([]);
        setEdges([]);
        setError(e instanceof Error ? e.message : "Failed to load graph");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-cyan-300">Traceback Graph</h2>
        <p className="text-slate-400 text-sm mt-1">
          Historical failure paths and loss events from graph memory. Click a node for details.
        </p>
      </div>

      {loading && <p className="text-slate-500 text-sm">Loading graph…</p>}
      {error && (
        <p className="text-red-400 text-sm" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && (
        <ReactFlowProvider>
          <TraceGraph nodes={nodes} edges={edges} highlightId={highlightId} />
          <FailureTimeline nodes={nodes} highlightId={highlightId} onHover={setHighlightId} />
          <p className="text-xs text-slate-600">
            {nodes.length} nodes · {edges.length} edges
            {edges[0]?.probability != null &&
              ` · top path confidence ${Math.round((edges[0].probability ?? 0) * 100)}%`}
          </p>
        </ReactFlowProvider>
      )}
    </div>
  );
}
