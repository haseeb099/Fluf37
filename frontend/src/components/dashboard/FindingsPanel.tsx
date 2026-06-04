"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { cn, getSeverityColor } from "@/lib/utils";
import type { BlindSpot } from "@/types/nexus";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

function FindingRow({ bs }: { bs: BlindSpot }) {
  const [open, setOpen] = useState(bs.severity === "critical");

  return (
    <Card
      className={cn(
        "p-0 overflow-hidden glass-panel-hover transition-all",
        open && "border-l-2",
      )}
      style={open ? { borderLeftColor: getSeverityColor(bs.severity) } : undefined}
    >
      <button
        type="button"
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-slate-800/30 transition-colors"
        onClick={() => setOpen(!open)}
      >
        {open ? (
          <ChevronDown className="h-4 w-4 text-muted shrink-0 mt-0.5" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted shrink-0 mt-0.5" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <Badge
              variant={
                bs.severity === "critical"
                  ? "critical"
                  : bs.severity === "high"
                    ? "warning"
                    : "outline"
              }
            >
              {bs.severity}
            </Badge>
            <span className="text-xs text-muted">{Math.round(bs.confidence * 100)}% confidence</span>
          </div>
          <h4 className="font-medium text-slate-100">{bs.title}</h4>
          {open && <p className="text-sm text-muted mt-2 leading-relaxed">{bs.description}</p>}
        </div>
      </button>
    </Card>
  );
}

export function FindingsPanel({ blindSpots }: { blindSpots: BlindSpot[] }) {
  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100">
          Risk findings
          <span className="text-muted font-normal ml-2">({blindSpots.length})</span>
        </h3>
      </div>
      <div className="space-y-2">
        {blindSpots.map((bs) => (
          <FindingRow key={bs.id} bs={bs} />
        ))}
        {blindSpots.length === 0 && (
          <Card className="p-8 text-center">
            <p className="text-muted text-sm">
              No findings yet. Run a pre-release risk review from the sidebar to analyze cross-source
              blind spots.
            </p>
          </Card>
        )}
      </div>
    </section>
  );
}
