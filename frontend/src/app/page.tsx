"use client";

import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { FindingsPanel } from "@/components/dashboard/FindingsPanel";
import { KpiStrip } from "@/components/dashboard/KpiStrip";
import { PlatformStatusBanner } from "@/components/dashboard/PlatformStatusBanner";
import { RiskReviewHero } from "@/components/dashboard/RiskReviewHero";
import { RiskReviewWorkflow } from "@/components/dashboard/RiskReviewWorkflow";
import { useNexusStore } from "@/store/nexusStore";

export default function DashboardPage() {
  const blindSpots = useNexusStore((s) => s.blindSpots);

  return (
    <AppShell
      title="Overview"
      subtitle="Monitor risk signals and run pre-release reviews from one place."
    >
      <div className="space-y-6 animate-fade-in">
        <RiskReviewHero />

        <div className="flex flex-wrap gap-4 text-sm -mt-2">
          <Link href="/decisions" className="text-sky-400 hover:text-sky-300">
            View decisions →
          </Link>
          <Link href="/integrations" className="text-slate-400 hover:text-slate-300">
            Manage integrations
          </Link>
          <Link href="/agents" className="text-slate-400 hover:text-slate-300">
            Agent activity →
          </Link>
        </div>

        <KpiStrip />
        <PlatformStatusBanner />
        <RiskReviewWorkflow />
        <FindingsPanel blindSpots={blindSpots} />
      </div>
    </AppShell>
  );
}
