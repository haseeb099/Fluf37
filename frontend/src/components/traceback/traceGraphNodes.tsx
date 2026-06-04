"use client";

import { Handle, type NodeProps, Position } from "reactflow";
import { cn } from "@/lib/utils";
import type { GraphNodeData } from "@/types/graph";

export type TraceNodeData = {
  label: string;
  nodeType: string;
  detail?: GraphNodeData;
  highlighted?: boolean;
};

function FailureNode({ data, selected }: NodeProps<TraceNodeData>) {
  return (
    <div
      className={cn(
        "px-3 py-2 rounded border min-w-[160px] max-w-[220px]",
        selected || data.highlighted
          ? "border-purple-400 shadow-lg shadow-purple-900/40"
          : "border-purple-700/50"
      )}
      style={{ background: "rgba(153, 102, 255, 0.15)" }}
    >
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <p className="text-[10px] uppercase tracking-wide text-purple-300">failure</p>
      <p className="text-sm font-mono text-slate-100 mt-0.5">{data.label}</p>
    </div>
  );
}

function LossEventNode({ data, selected }: NodeProps<TraceNodeData>) {
  return (
    <div
      className={cn(
        "px-3 py-2 rounded border min-w-[160px]",
        selected || data.highlighted
          ? "border-red-400 shadow-lg shadow-red-900/40"
          : "border-red-700/50"
      )}
      style={{ background: "rgba(255, 23, 68, 0.12)" }}
    >
      <Handle type="target" position={Position.Left} id="in" />
      <p className="text-[10px] uppercase tracking-wide text-red-300">loss event</p>
      <p className="text-sm font-mono text-slate-100 mt-0.5">{data.label}</p>
      {typeof data.detail?.dollar_loss === "number" && (
        <p className="text-xs text-red-200 mt-1">${data.detail.dollar_loss.toLocaleString()} loss</p>
      )}
    </div>
  );
}

/** Stable reference for React Flow — do not recreate per render. */
export const traceGraphNodeTypes = {
  failure: FailureNode,
  loss_event: LossEventNode,
};
