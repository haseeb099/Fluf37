"use client";

import { Eye, GitBranch, ShieldCheck, Swords } from "lucide-react";
import { PRODUCT_NAME } from "@/lib/brand";

const PILLARS = [
  {
    icon: Eye,
    title: "Find blind spots",
    desc: "Cross-source gaps CRM dashboards never surface alone.",
    accent: "text-amber-400",
    border: "border-amber-500/20",
    bg: "from-amber-500/10",
  },
  {
    icon: Swords,
    title: "Stress-test adversarially",
    desc: "Every finding attacked before a wire or credit decision.",
    accent: "text-red-400",
    border: "border-red-500/20",
    bg: "from-red-500/10",
  },
  {
    icon: GitBranch,
    title: "Trace to prior losses",
    desc: "Graph + vector memory links signals to named failures.",
    accent: "text-violet-400",
    border: "border-violet-500/20",
    bg: "from-violet-500/10",
  },
  {
    icon: ShieldCheck,
    title: "Prove it in audit",
    desc: "Hash-chained log, correlation ID, exportable review JSON.",
    accent: "text-emerald-400",
    border: "border-emerald-500/20",
    bg: "from-emerald-500/10",
  },
] as const;

export function ProductPitchStrip() {
  return (
    <section aria-label={`Why ${PRODUCT_NAME}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500 mb-3">
        Why judges and CFOs care
      </p>
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3">
        {PILLARS.map(({ icon: Icon, title, desc, accent, border, bg }) => (
          <div
            key={title}
            className={`pitch-card rounded-xl border ${border} bg-gradient-to-br ${bg} to-transparent p-4`}
          >
            <Icon className={`h-5 w-5 ${accent} mb-2`} />
            <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
