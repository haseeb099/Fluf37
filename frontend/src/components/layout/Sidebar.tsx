"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import {
  FileText,
  GitBranch,
  LayoutDashboard,
  Play,
  Plug,
  Scale,
  Sparkles,
  Zap,
} from "lucide-react";
import { PRODUCT_NAME, PRODUCT_WEDGE } from "@/lib/brand";
import { useNexusStore } from "@/store/nexusStore";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";
import { fetchAuthToken } from "@/lib/api";
import { useNexusWs } from "@/providers/NexusWebSocketProvider";

const NAV = [
  { href: "/", label: "Risk review", icon: LayoutDashboard },
  { href: "/integrations", label: "Integrations", icon: Plug },
  { href: "/traceback", label: "Traceback", icon: GitBranch },
  { href: "/decisions", label: "Decisions", icon: Scale },
];

const ADVANCED = [
  { href: "/agents", label: "Review transcript", icon: FileText },
  { href: "/evolution", label: "Evolution", icon: Sparkles },
];

const showAdvanced = process.env.NEXT_PUBLIC_SHOW_ADVANCED === "true";

export function Sidebar() {
  const pathname = usePathname();
  const { runPipeline, isConnected, lastError } = useNexusWs();
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const wsAuthStatus = useNexusStore((s) => s.wsAuthStatus);
  const busy = pipelineState !== "IDLE" && pipelineState !== "COMPLETE" && pipelineState !== "ERROR";
  const onRiskReview = pathname === "/";

  useEffect(() => {
    fetchAuthToken("viewer").catch(() => undefined);
  }, []);

  return (
    <aside
      className="w-64 shrink-0 border-r border-border flex flex-col min-h-screen"
      style={{ background: "var(--bg-surface)" }}
    >
      <div className="p-5 border-b border-border space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="brand-mark h-10 w-10 rounded-xl flex items-center justify-center shrink-0">
            <span className="text-xs font-bold tracking-tight bg-gradient-to-br from-sky-300 to-emerald-400 bg-clip-text text-transparent">
              F37
            </span>
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 tracking-tight">{PRODUCT_NAME}</h1>
            <p className="text-[10px] text-muted leading-tight flex items-center gap-1">
              <Zap className="h-2.5 w-2.5 text-sky-400" />
              {PRODUCT_WEDGE}
            </p>
          </div>
        </div>

        {!onRiskReview && (
          <Button
            variant="primary"
            size="lg"
            className="w-full shadow-glow"
            onClick={runPipeline}
            disabled={!isConnected || busy}
          >
            <Play className="h-4 w-4 fill-current" />
            {busy ? "Running…" : "Run risk review"}
          </Button>
        )}

        <Badge variant={isConnected ? "success" : "critical"}>
          {isConnected ? "Stream connected" : "Stream disconnected"}
        </Badge>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-sky-500/10 text-sky-200 border border-sky-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
        {showAdvanced && (
          <>
            <p className="text-[10px] uppercase tracking-wider text-slate-600 px-3 pt-4 pb-1">
              Advanced
            </p>
            {ADVANCED.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm text-slate-500 hover:text-slate-300"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </>
        )}
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <p className="text-[11px] text-muted">
          Pipeline: <span className="text-slate-300">{pipelineState}</span>
        </p>
        {wsAuthStatus === "authenticated" && (
          <p className="text-[11px] text-emerald-400/80">Authenticated</p>
        )}
        {lastError && (
          <p className="text-xs text-red-400 break-words" role="alert">
            {lastError}
          </p>
        )}
      </div>
    </aside>
  );
}
