"use client";

import { PluginCard } from "@/components/integrations/PluginCard";
import { PluginDetailPanel } from "@/components/integrations/PluginDetailPanel";
import { RegisterPluginPanel } from "@/components/integrations/RegisterPluginPanel";
import { Badge } from "@/components/ui/Badge";
import { Tabs } from "@/components/ui/Tabs";
import {
  connectSource,
  disconnectSource,
  getPluginCatalog,
  syncSource,
} from "@/lib/api";
import { CATEGORY_LABELS, type PluginManifest } from "@/types/integrations";
import { Layers, Puzzle, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

export function IntegrationsHub() {
  const [tab, setTab] = useState("marketplace");
  const [category, setCategory] = useState<string>("all");
  const [plugins, setPlugins] = useState<PluginManifest[]>([]);
  const [summary, setSummary] = useState({ total: 0, installed: 0, official: 0, community: 0 });
  const [selected, setSelected] = useState<PluginManifest | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRegister, setShowRegister] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPluginCatalog({
        installed: tab === "installed",
        category: category !== "all" ? category : undefined,
      });
      setPlugins(data.plugins);
      setSummary(data.summary);
      setSelected((prev) =>
        prev ? data.plugins.find((p) => p.id === prev.id) ?? null : null
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load integrations");
    } finally {
      setLoading(false);
    }
  }, [tab, category]);

  useEffect(() => {
    load();
  }, [load]);

  const categories = useMemo(
    () => ["all", ...Object.keys(CATEGORY_LABELS)] as const,
    []
  );

  const runAction = async (
    plugin: PluginManifest,
    action: "connect" | "sync" | "disconnect"
  ) => {
    if (!plugin.source_type) return;
    setBusyId(plugin.id);
    setError(null);
    try {
      if (action === "connect") await connectSource(plugin.source_type);
      else if (action === "sync") await syncSource(plugin.source_type);
      else await disconnectSource(plugin.source_type);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : `${action} failed`);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-sky-500 mb-1">
            Integration hub
          </p>
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-50 tracking-tight">
            Plugins & data sources
          </h1>
          <p className="text-muted text-sm mt-2 max-w-2xl">
            Connect official Fluf37 connectors or register your own webhook integration. One catalog for
            your CFO risk-review pipeline.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="default">
            <Puzzle className="h-3 w-3 mr-1 inline" />
            {summary.total} plugins
          </Badge>
          <Badge variant="success">{summary.installed} active</Badge>
          <button
            type="button"
            onClick={load}
            className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-sky-300 px-2 py-1"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </header>

      <Tabs
        tabs={[
          { id: "marketplace", label: "Marketplace", count: summary.total },
          { id: "installed", label: "Installed", count: summary.installed },
          { id: "add", label: "Add integration" },
        ]}
        active={tab}
        onChange={(id) => {
          setTab(id);
          if (id === "add") setShowRegister(true);
        }}
      />

      {error && (
        <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3" role="alert">
          {error}
        </p>
      )}

      {tab === "add" || showRegister ? (
        <RegisterPluginPanel
          onRegistered={() => {
            setShowRegister(false);
            setTab("installed");
            load();
          }}
          onClose={() => {
            setShowRegister(false);
            setTab("marketplace");
          }}
        />
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategory(cat)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    category === cat
                      ? "bg-sky-500/15 border-sky-500/40 text-sky-200"
                      : "border-slate-700 text-muted hover:border-slate-500"
                  }`}
                >
                  {cat === "all" ? "All categories" : CATEGORY_LABELS[cat as keyof typeof CATEGORY_LABELS]}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="grid sm:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="glass-panel h-48 animate-pulse bg-slate-800/30" />
                ))}
              </div>
            ) : plugins.length === 0 ? (
              <div className="glass-panel p-12 text-center">
                <Layers className="h-10 w-10 text-slate-600 mx-auto mb-3" />
                <p className="text-muted">No integrations in this view.</p>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 gap-4">
                {plugins.map((plugin) => (
                  <PluginCard
                    key={plugin.id}
                    plugin={plugin}
                    selected={selected?.id === plugin.id}
                    busy={busyId === plugin.id}
                    onSelect={() => setSelected(plugin)}
                    onConnect={() => runAction(plugin, "connect")}
                    onSync={() => runAction(plugin, "sync")}
                    onDisconnect={() => runAction(plugin, "disconnect")}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <PluginDetailPanel plugin={selected} />
          </div>
        </div>
      )}
    </div>
  );
}
