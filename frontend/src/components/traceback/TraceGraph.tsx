"use client";

import { useCallback, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { FailureNode, LossEventNode, type TraceNodeData } from "@/components/traceback/traceGraphNodes";
import { graphNodeLabel, graphNodeSubtitle } from "@/lib/graphLabels";
import { cn, getSeverityColor } from "@/lib/utils";
import type { GraphEdgeData, GraphNodeData } from "@/types/graph";

/** Module-level stable nodeTypes (React Flow #002). */
const traceGraphNodeTypes = {
  failure: FailureNode,
  loss_event: LossEventNode,
} as const;

export type { GraphEdgeData, GraphNodeData };

interface TraceGraphProps {
  nodes: GraphNodeData[];
  edges: GraphEdgeData[];
  highlightId?: string | null;
  className?: string;
}

type NexusFlowNode = Node<TraceNodeData>;

function layoutNodes(rawNodes: GraphNodeData[], highlightId?: string | null): NexusFlowNode[] {
  const failures = rawNodes.filter((n) => (n.type || "failure") !== "loss_event");
  const lossEvents = rawNodes.filter((n) => n.type === "loss_event");
  const flowNodes: NexusFlowNode[] = [];

  failures.forEach((n, i) => {
    const nodeType = n.type === "loss_event" ? "loss_event" : "failure";
    flowNodes.push({
      id: n.id,
      type: nodeType,
      position: { x: 40, y: 40 + i * 110 },
      data: {
        label: graphNodeLabel(n),
        nodeType,
        detail: n,
        highlighted: n.id === highlightId,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    });
  });

  lossEvents.forEach((n, i) => {
    flowNodes.push({
      id: n.id,
      type: "loss_event",
      position: { x: 380, y: 40 + i * 120 + Math.max(0, (failures.length - 1) * 30) },
      data: {
        label: graphNodeLabel(n),
        nodeType: "loss_event",
        detail: n,
        highlighted: n.id === highlightId,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    });
  });

  return flowNodes;
}

function toFlowEdges(rawEdges: GraphEdgeData[]): Edge[] {
  return rawEdges.map((e, i) => ({
    id: `${e.source}-${e.target}-${i}`,
    source: e.source,
    target: e.target,
    sourceHandle: "out",
    targetHandle: "in",
    label: e.probability != null ? `${Math.round(e.probability * 100)}%` : e.type,
    animated: e.type === "leads_to",
    style: {
      stroke: e.type === "leads_to" ? "#9966ff" : "#64748b",
      strokeWidth: 2,
    },
    labelStyle: { fill: "#94a3b8", fontSize: 10 },
  }));
}

export function TraceGraph({ nodes, edges, highlightId, className }: TraceGraphProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const nodeTypes = useMemo(() => traceGraphNodeTypes, []);

  const flowNodes = useMemo(() => layoutNodes(nodes, highlightId), [nodes, highlightId]);
  const flowEdges = useMemo(() => toFlowEdges(edges), [edges]);

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedId),
    [nodes, selectedId]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedId(node.id);
  }, []);

  if (nodes.length === 0) {
    return (
      <p className="text-slate-500 text-sm p-4">
        No graph data. Start the backend with demo memory seeded.
      </p>
    );
  }

  return (
    <div className={cn("flex flex-col lg:flex-row gap-4", className)}>
      <div className="flex-1 h-[420px] rounded border border-purple-900/30 overflow-hidden bg-slate-950/50">
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          onNodeClick={onNodeClick}
          fitView
          fitViewOptions={{ padding: 0.25 }}
          proOptions={{ hideAttribution: true }}
          nodesDraggable={false}
          nodesConnectable={false}
        >
          <Background color="#1e293b" gap={16} />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(n) => (n.type === "loss_event" ? "#ff1744" : "#9966ff")}
            maskColor="rgba(2, 4, 8, 0.8)"
          />
        </ReactFlow>
      </div>
      {selectedNode && (
        <aside className="lg:w-72 glass-panel p-4 text-sm space-y-2 shrink-0">
          <p className="text-xs uppercase text-purple-400">{selectedNode.type || "node"}</p>
          <p className="font-medium text-cyan-100">{graphNodeLabel(selectedNode)}</p>
          <p className="font-mono text-[10px] text-slate-500">{selectedNode.id}</p>
          {graphNodeSubtitle(selectedNode) && (
            <p className="text-slate-400 text-xs">{graphNodeSubtitle(selectedNode)}</p>
          )}
          {selectedNode.severity && (
            <p>
              Severity:{" "}
              <span style={{ color: getSeverityColor(selectedNode.severity) }}>
                {selectedNode.severity}
              </span>
            </p>
          )}
          {selectedNode.description && (
            <p className="text-slate-300 leading-relaxed">{selectedNode.description}</p>
          )}
          {typeof selectedNode.dollar_loss === "number" && (
            <p className="text-red-300">Loss: ${selectedNode.dollar_loss.toLocaleString()}</p>
          )}
        </aside>
      )}
    </div>
  );
}
