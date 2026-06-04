"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { connectionBadge, dataModeBadge, pluginIcon } from "@/lib/integrations";
import { cn } from "@/lib/utils";
import { CATEGORY_LABELS, type PluginManifest } from "@/types/integrations";
import { CheckCircle2, ExternalLink } from "lucide-react";

interface PluginCardProps {
  plugin: PluginManifest;
  busy?: boolean;
  onConnect?: () => void;
  onSync?: () => void;
  onDisconnect?: () => void;
  onSelect?: () => void;
  selected?: boolean;
}

export function PluginCard({
  plugin,
  busy,
  onConnect,
  onSync,
  onDisconnect,
  onSelect,
  selected,
}: PluginCardProps) {
  const Icon = pluginIcon(plugin.icon);
  const canConnect = plugin.integration_type === "builtin" && plugin.source_type;

  return (
    <Card
      className={cn(
        "glass-panel-hover flex flex-col h-full cursor-pointer animate-fade-in",
        selected && "ring-1 ring-sky-500/40 border-sky-500/30"
      )}
      onClick={onSelect}
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500/10 border border-sky-500/20">
              <Icon className="h-5 w-5 text-sky-400" />
            </div>
            <div>
              <CardTitle>{plugin.name}</CardTitle>
              <p className="text-xs text-muted mt-0.5">{plugin.vendor}</p>
            </div>
          </div>
          <Badge variant={plugin.tier === "official" ? "default" : "outline"}>{plugin.tier}</Badge>
        </div>
        <CardDescription>{plugin.description}</CardDescription>
      </CardHeader>

      <div className="flex flex-wrap gap-1.5 mb-4">
        <Badge variant="outline">{CATEGORY_LABELS[plugin.category]}</Badge>
        {plugin.data_mode && <Badge variant={dataModeBadge(plugin.data_mode)}>{plugin.data_mode}</Badge>}
        {plugin.connection_state && (
          <Badge variant={connectionBadge(plugin.connection_state)}>{plugin.connection_state}</Badge>
        )}
        {plugin.installed && (
          <Badge variant="success">
            <CheckCircle2 className="h-3 w-3 mr-1 inline" />
            active
          </Badge>
        )}
      </div>

      <div className="mt-auto flex flex-wrap gap-2 pt-2 border-t border-border" onClick={(e) => e.stopPropagation()}>
        {canConnect && (
          <>
            <Button size="sm" variant="primary" disabled={busy} onClick={onConnect}>
              {busy ? "Working…" : "Connect"}
            </Button>
            <Button size="sm" disabled={busy} onClick={onSync}>
              Sync
            </Button>
            {plugin.connection_state === "connected" && onDisconnect && (
              <Button size="sm" variant="ghost" disabled={busy} onClick={onDisconnect}>
                Disconnect
              </Button>
            )}
          </>
        )}
        {plugin.integration_type === "webhook" && plugin.tier === "community" && (
          <span className="text-xs text-muted self-center">Webhook registered</span>
        )}
        {plugin.docs_url && (
          <a
            href={plugin.docs_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 ml-auto"
          >
            Docs <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </Card>
  );
}
