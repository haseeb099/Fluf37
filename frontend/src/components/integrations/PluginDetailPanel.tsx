"use client";

import { Badge } from "@/components/ui/Badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { pluginIcon } from "@/lib/integrations";
import type { PluginManifest } from "@/types/integrations";
import { ListOrdered } from "lucide-react";

export function PluginDetailPanel({ plugin }: { plugin: PluginManifest | null }) {
  if (!plugin) {
    return (
      <Card className="h-full min-h-[320px] flex items-center justify-center">
        <p className="text-sm text-muted text-center px-6">
          Select an integration to view setup steps, data mode, and connection status.
        </p>
      </Card>
    );
  }

  const Icon = pluginIcon(plugin.icon);

  return (
    <Card className="h-full animate-fade-in">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-500/10 border border-sky-500/20">
            <Icon className="h-6 w-6 text-sky-400" />
          </div>
          <div>
            <CardTitle className="text-lg">{plugin.name}</CardTitle>
            <CardDescription>{plugin.vendor} · v{plugin.version}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <p className="text-sm text-slate-300 leading-relaxed mb-4">{plugin.description}</p>

      <div className="flex flex-wrap gap-2 mb-6">
        <Badge variant="outline">{plugin.integration_type}</Badge>
        {plugin.live_vendor && <Badge variant="default">Live: {plugin.live_vendor}</Badge>}
        {plugin.supports_webhook && <Badge variant="success">Webhook</Badge>}
        {plugin.data_mode && <Badge variant="warning">{plugin.data_mode} data</Badge>}
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2 flex items-center gap-2">
            <ListOrdered className="h-3.5 w-3.5" /> Setup
          </h4>
          <ol className="space-y-2">
            {plugin.setup_steps.map((step, i) => (
              <li key={i} className="text-sm text-slate-400 flex gap-2">
                <span className="text-sky-500 font-mono text-xs shrink-0">{i + 1}.</span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        {plugin.required_env.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
              Environment
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {plugin.required_env.map((v) => (
                <code key={v} className="text-[11px] px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-sky-300">
                  {v}
                </code>
              ))}
            </div>
          </div>
        )}

        {plugin.source_type && plugin.integration_type === "builtin" && (
          <p className="text-xs text-muted border-t border-border pt-4">
            Source type: <code className="text-sky-400">{plugin.source_type}</code>
          </p>
        )}
      </div>
    </Card>
  );
}
