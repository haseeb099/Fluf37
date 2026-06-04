"use client";

import { useEffect, useState } from "react";
import { connectSource, getSourcesStatus, syncSource } from "@/lib/api";
import type { ConnectionStatus, SourceType } from "@/types/nexus";

const SOURCES: SourceType[] = ["crm", "erp", "bank", "trading", "news"];

export default function ConnectionsPage() {
  const [sources, setSources] = useState<ConnectionStatus[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    getSourcesStatus()
      .then((d) => setSources((d.sources || []) as ConnectionStatus[]))
      .catch(() => setSources(SOURCES.map((s) => ({ source_type: s, state: "disconnected" }))))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-cyan-300">Data Connections</h2>
      <p className="text-slate-400 text-sm">CRM · ERP · Banking · Trading · News</p>
      {loading ? (
        <p className="text-slate-500">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SOURCES.map((st) => {
            const status = sources.find((s) => s.source_type === st) || { source_type: st, state: "disconnected" };
            const connected = status.state === "connected";
            return (
              <div key={st} className="glass-panel p-4">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-slate-600"}`} />
                  <h3 className="uppercase font-medium">{st}</h3>
                </div>
                <p className="text-xs text-slate-500 mt-1">State: {status.state}</p>
                <div className="flex gap-2 mt-4">
                  <button
                    type="button"
                    onClick={() => connectSource(st).then(refresh)}
                    className="text-xs px-2 py-1 rounded border border-cyan-600/50 hover:bg-cyan-900/30"
                  >
                    Connect
                  </button>
                  <button
                    type="button"
                    onClick={() => syncSource(st).then(refresh)}
                    className="text-xs px-2 py-1 rounded border border-slate-600 hover:bg-slate-800"
                  >
                    Sync
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <p className="text-xs text-slate-600">
        Webhook ingest: POST /ingest/&#123;source&#125; with X-Nexus-Signature header
      </p>
    </div>
  );
}
