"use client";

import { AppShell } from "@/components/layout/AppShell";
import { AgentGrid } from "@/components/dashboard/AgentGrid";
import { Badge } from "@/components/ui/Badge";
import { useNexusWs } from "@/providers/NexusWebSocketProvider";
import { useNexusStore } from "@/store/nexusStore";
import { Radio } from "lucide-react";

export default function AgentsPage() {
  const { isConnected } = useNexusWs();
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const running =
    pipelineState !== "IDLE" && pipelineState !== "COMPLETE" && pipelineState !== "ERROR";

  return (
    <AppShell
      title="Review transcript"
      subtitle="Detailed streaming output from the risk review pipeline — for audit and engineering review."
    >
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={isConnected ? "success" : "critical"}>
            <Radio className="h-3 w-3 mr-1 inline" />
            {isConnected ? "Stream connected" : "Stream disconnected"}
          </Badge>
          <Badge variant="outline">Pipeline: {pipelineState}</Badge>
          {running && <Badge variant="warning">Streaming</Badge>}
        </div>

        <p className="text-sm text-muted max-w-2xl">
          Run a risk review from the Risk review page to populate transcripts. Each card shows tokens
          streamed during the review (advanced — not required for sign-off).
        </p>

        <AgentGrid />
      </div>
    </AppShell>
  );
}
