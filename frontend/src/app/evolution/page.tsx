"use client";

import { useEffect, useState } from "react";
import { getEvolutionReport } from "@/lib/api";

export default function EvolutionPage() {
  const [report, setReport] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    getEvolutionReport()
      .then((r) => setReport(r as Record<string, unknown>))
      .catch(() => setReport(null));
  }, []);

  const score = (report?.self_improvement_score as number) ?? 0.123;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-cyan-300">Evolution</h2>
      <div className="glass-panel p-6 text-center">
        <p className="text-4xl font-bold text-yellow-300">+{(score * 100).toFixed(1)}%</p>
        <p className="text-slate-400 text-sm">Self-improvement week-over-week</p>
      </div>
      {report && (
        <div className="glass-panel p-4 text-sm space-y-2">
          <p>Weight changes: {JSON.stringify(report.weight_changes)}</p>
          <ul className="list-disc pl-5 text-slate-400">
            {((report.new_rules as string[]) || []).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
