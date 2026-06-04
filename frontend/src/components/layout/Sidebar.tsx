"use client";

import Link from "next/link";
import { useNexusWebSocket } from "@/hooks/useNexusWebSocket";
import { useNexusStore } from "@/store/nexusStore";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/connections", label: "Connections" },
  { href: "/agents", label: "Agents" },
  { href: "/traceback", label: "Traceback" },
  { href: "/decisions", label: "Decisions" },
  { href: "/evolution", label: "Evolution" },
];

export function Sidebar() {
  const { runPipeline, isConnected, lastError } = useNexusWebSocket();
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const wsAuthStatus = useNexusStore((s) => s.wsAuthStatus);
  const busy = pipelineState !== "IDLE" && pipelineState !== "COMPLETE" && pipelineState !== "ERROR";

  return (
    <aside
      className="w-56 border-r border-cyan-900/30 p-4 flex flex-col gap-4"
      style={{ background: "var(--bg-surface)" }}
    >
      <h1 className="text-lg font-bold text-cyan-400">Nexus AI</h1>
      <button
        type="button"
        onClick={runPipeline}
        disabled={!isConnected || busy}
        title={
          !isConnected
            ? "Waiting for WebSocket connection"
            : busy
              ? "Pipeline in progress"
              : "Run demo pipeline"
        }
        className="px-3 py-2 rounded bg-cyan-600/30 border border-cyan-500/50 text-sm hover:bg-cyan-600/50 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Run Pipeline (Demo)
      </button>
      <p className="text-xs text-slate-500">
        WS: {isConnected ? "connected" : "disconnected"}
        {wsAuthStatus === "authenticated" ? " · auth ok" : wsAuthStatus === "failed" ? " · auth failed" : ""} ·{" "}
        {pipelineState}
      </p>
      {lastError && (
        <p className="text-xs text-red-400 break-words" role="alert">
          {lastError}
        </p>
      )}
      <nav className="flex flex-col gap-1">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="text-sm text-slate-300 hover:text-cyan-400 px-2 py-1 rounded"
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
