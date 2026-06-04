"use client";

import Link from "next/link";
import { CheckCircle2, Circle } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { useNexusStore } from "@/store/nexusStore";

const STEPS = [
  {
    id: "connect",
    label: "Connect or confirm data sources",
    href: "/integrations",
    done: (s: { integrationsReady: boolean }) => s.integrationsReady,
  },
  {
    id: "run",
    label: "Run a pre-release risk review",
    href: "/",
    done: (s: { reviewComplete: boolean }) => s.reviewComplete,
  },
  {
    id: "export",
    label: "Export the review report (JSON)",
    href: "/",
    done: (s: { exported: boolean }) => s.exported,
  },
  {
    id: "audit",
    label: "Replay audit trail in Traceback",
    href: "/traceback",
    done: (s: { reviewComplete: boolean }) => s.reviewComplete,
  },
] as const;

export function FirstRunChecklist({
  integrationsReady = false,
  exported = false,
}: {
  integrationsReady?: boolean;
  exported?: boolean;
}) {
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const reviewComplete = pipelineState === "COMPLETE";
  const state = { integrationsReady, reviewComplete, exported };
  const doneCount = STEPS.filter((step) => step.done(state)).length;

  if (doneCount === STEPS.length) return null;

  return (
    <Card className="border-sky-500/20 bg-sky-950/20 p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-sky-400 mb-3">
        First-run checklist · {doneCount}/{STEPS.length}
      </p>
      <ul className="space-y-2">
        {STEPS.map((step) => {
          const done = step.done(state);
          return (
            <li key={step.id}>
              <Link
                href={step.href}
                className="flex items-center gap-2 text-sm text-slate-300 hover:text-sky-200 transition-colors"
              >
                {done ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : (
                  <Circle className="h-4 w-4 text-slate-600 shrink-0" />
                )}
                {step.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
