"use client";

import { useEffect, useState } from "react";
import { getDecisions, submitOutcome } from "@/lib/api";
import type { DecisionOutput } from "@/types/nexus";
import { useNexusStore } from "@/store/nexusStore";

export default function DecisionsPage() {
  const storeDecisions = useNexusStore((s) => s.decisions);
  const [decisions, setDecisions] = useState<DecisionOutput[]>([]);

  useEffect(() => {
    getDecisions()
      .then((d) => setDecisions(d as DecisionOutput[]))
      .catch(() => setDecisions(storeDecisions));
  }, [storeDecisions]);

  const list = decisions.length ? decisions : storeDecisions;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-cyan-300">Decisions</h2>
      {list.map((d) => (
        <div key={d.id} className="glass-panel p-4">
          <span className="text-xs text-cyan-500 uppercase">{d.decision_type}</span>
          <h3 className="font-medium mt-1">{d.recommendation}</h3>
          <p className="text-sm text-slate-400">Confidence: {(d.confidence * 100).toFixed(0)}%</p>
          <p className="text-xs mt-1">
            Stress test: {d.adversarial_stress_passed ? "PASSED" : "FAILED"}
          </p>
          <div className="flex gap-2 mt-3">
            <button
              type="button"
              onClick={() => submitOutcome(d.id, "correct")}
              className="text-xs px-2 py-1 rounded bg-green-900/40 border border-green-600"
            >
              Correct
            </button>
            <button
              type="button"
              onClick={() => submitOutcome(d.id, "incorrect")}
              className="text-xs px-2 py-1 rounded bg-red-900/40 border border-red-600"
            >
              Incorrect
            </button>
          </div>
        </div>
      ))}
      {list.length === 0 && <p className="text-slate-500">Run pipeline to generate decisions.</p>}
    </div>
  );
}
