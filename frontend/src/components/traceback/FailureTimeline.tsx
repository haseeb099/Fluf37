"use client";

import type { GraphNodeData } from "@/types/graph";
import { cn, getSeverityColor } from "@/lib/utils";

interface FailureTimelineProps {
  nodes: GraphNodeData[];
  highlightId?: string | null;
  onHover?: (id: string | null) => void;
}

export function FailureTimeline({ nodes, highlightId, onHover }: FailureTimelineProps) {
  const failures = nodes.filter((n) => n.type === "failure" || (!n.type && n.description));

  if (failures.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-slate-300">Failure timeline</h3>
      <ul className="space-y-2">
        {failures.map((f) => (
          <li
            key={f.id}
            className={cn(
              "glass-panel p-3 text-sm cursor-default transition-colors",
              highlightId === f.id && "border-purple-500/60"
            )}
            onMouseEnter={() => onHover?.(f.id)}
            onMouseLeave={() => onHover?.(null)}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-xs text-purple-300">{f.id}</span>
              {f.severity && (
                <span
                  className="text-[10px] uppercase px-1.5 py-0.5 rounded"
                  style={{
                    color: getSeverityColor(f.severity),
                    border: `1px solid ${getSeverityColor(f.severity)}44`,
                  }}
                >
                  {f.severity}
                </span>
              )}
            </div>
            {f.description ? (
              <p className="text-slate-400 leading-relaxed">{f.description}</p>
            ) : (
              <p className="text-slate-500 italic">No description</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
