"use client";

import { useCallback, useEffect, useState } from "react";
import { getDecisions, submitOutcome } from "@/lib/api";
import type { DecisionOutput } from "@/types/nexus";
import { useNexusStore } from "@/store/nexusStore";

function dedupeDecisions(items: DecisionOutput[]): DecisionOutput[] {
  const byKey = new Map<string, DecisionOutput>();
  for (const d of items) {
    const key = `${d.decision_type}::${d.recommendation}`;
    if (!byKey.has(key)) byKey.set(key, d);
  }
  return [...byKey.values()];
}

export default function DecisionsPage() {
  const storeDecisions = useNexusStore((s) => s.decisions);
  const [decisions, setDecisions] = useState<DecisionOutput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedbackId, setFeedbackId] = useState<string | null>(null);

  const loadDecisions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await getDecisions();
      setDecisions(d as DecisionOutput[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load decisions");
      const fromStore = useNexusStore.getState().decisions;
      if (fromStore.length) setDecisions(fromStore);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDecisions();
  }, [loadDecisions]);

  const list = dedupeDecisions(decisions.length ? decisions : storeDecisions);

  const handleOutcome = async (id: string, outcome: "correct" | "incorrect") => {
    setFeedbackId(id);
    setError(null);
    try {
      await submitOutcome(id, outcome);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit feedback");
    } finally {
      setFeedbackId(null);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-cyan-300">Decisions</h2>
      {loading && <p className="text-slate-500 text-sm">Loading decisions…</p>}
      {error && (
        <p className="text-red-400 text-sm" role="alert">
          {error}
        </p>
      )}
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
              disabled={feedbackId === d.id}
              onClick={() => handleOutcome(d.id, "correct")}
              className="text-xs px-2 py-1 rounded bg-green-900/40 border border-green-600 disabled:opacity-50"
            >
              {feedbackId === d.id ? "Saving…" : "Correct"}
            </button>
            <button
              type="button"
              disabled={feedbackId === d.id}
              onClick={() => handleOutcome(d.id, "incorrect")}
              className="text-xs px-2 py-1 rounded bg-red-900/40 border border-red-600 disabled:opacity-50"
            >
              Incorrect
            </button>
          </div>
        </div>
      ))}
      {!loading && list.length === 0 && (
        <p className="text-slate-500">Run pipeline to generate decisions.</p>
      )}
    </div>
  );
}
