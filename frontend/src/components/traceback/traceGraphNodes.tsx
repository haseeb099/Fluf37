"use client";

import { Handle, type NodeProps, Position } from "reactflow";
import { graphNodeLabel, graphNodeSubtitle } from "@/lib/graphLabels";
import { cn } from "@/lib/utils";
import type { GraphNodeData } from "@/types/graph";

export type TraceNodeData = {
  label: string;
  nodeType: string;
  detail?: GraphNodeData;
  highlighted?: boolean;
};

function FailureNode({ data, selected }: NodeProps<TraceNodeData>) {
  const detail = data.detail;
  const subtitle = detail ? graphNodeSubtitle(detail) : null;
  return (
    <div
      className={cn(
        "px-3 py-2 rounded border min-w-[200px] max-w-[280px]",
        selected || data.highlighted
          ? "border-purple-400 shadow-lg shadow-purple-900/40"
          : "border-purple-700/50"
      )}
      style={{ background: "rgba(153, 102, 255, 0.15)" }}
    >
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <p className="text-[10px] uppercase tracking-wide text-purple-300">failure</p>
      <p className="text-sm font-medium text-slate-100 mt-0.5 leading-snug">{data.label}</p>
      {subtitle && <p className="text-[11px] text-slate-400 mt-1 leading-snug">{subtitle}</p>}
    </div>
  );
}

function LossEventNode({ data, selected }: NodeProps<TraceNodeData>) {
  const detail = data.detail;
  const subtitle = detail ? graphNodeSubtitle(detail) : null;
  return (
    <div
      className={cn(
        "px-3 py-2 rounded border min-w-[200px] max-w-[280px]",
        selected || data.highlighted
          ? "border-red-400 shadow-lg shadow-red-900/40"
          : "border-red-700/50"
      )}
      style={{ background: "rgba(255, 23, 68, 0.12)" }}
    >
      <Handle type="target" position={Position.Left} id="in" />
      <p className="text-[10px] uppercase tracking-wide text-red-300">loss event</p>
      <p className="text-sm font-medium text-slate-100 mt-0.5 leading-snug">{data.label}</p>
      {typeof data.detail?.dollar_loss === "number" && (
        <p className="text-xs text-red-200 mt-1">${data.detail.dollar_loss.toLocaleString()} realized</p>
      )}
      {subtitle && <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{subtitle}</p>}
    </div>
  );
}

export { FailureNode, LossEventNode };
