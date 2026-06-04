"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { ExportRiskReviewButton } from "@/components/dashboard/ExportRiskReviewButton";
import { FindingsPanel } from "@/components/dashboard/FindingsPanel";
import { FirstRunChecklist } from "@/components/dashboard/FirstRunChecklist";
import { KpiStrip } from "@/components/dashboard/KpiStrip";
import { PlatformStatusBanner } from "@/components/dashboard/PlatformStatusBanner";
import { ReviewDataModeBanner } from "@/components/dashboard/ReviewDataModeBanner";
import { AgentPipelineStrip } from "@/components/dashboard/AgentPipelineStrip";
import { ProductPitchStrip } from "@/components/dashboard/ProductPitchStrip";
import { RiskReviewHero } from "@/components/dashboard/RiskReviewHero";
import { RiskReviewWorkflow } from "@/components/dashboard/RiskReviewWorkflow";
import { PRODUCT_NAME } from "@/lib/brand";
import { useNexusStore } from "@/store/nexusStore";

export default function DashboardPage() {
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const [exported, setExported] = useState(false);

  return (
    <AppShell
      title="Risk review"
      subtitle={`${PRODUCT_NAME} — pre-release review across CRM, ERP, and banking before wires, credit, or deal sign-off.`}
    >
      <div className="space-y-6 animate-fade-in">
        <RiskReviewHero />
        <ProductPitchStrip />
        <AgentPipelineStrip />
        <FirstRunChecklist exported={exported} />
        <ReviewDataModeBanner />

        <div className="flex flex-wrap items-center gap-4 text-sm -mt-2">
          <ExportRiskReviewButton onExported={() => setExported(true)} />
          <Link href="/decisions" className="text-sky-400 hover:text-sky-300">
            View decisions →
          </Link>
          <Link href="/integrations" className="text-slate-400 hover:text-slate-300">
            Manage integrations
          </Link>
          <Link href="/traceback" className="text-slate-400 hover:text-slate-300">
            Audit traceback →
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
