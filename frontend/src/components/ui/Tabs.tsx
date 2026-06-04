"use client";

import { cn } from "@/lib/utils";

export function Tabs({
  tabs,
  active,
  onChange,
  className,
}: {
  tabs: { id: string; label: string; count?: number }[];
  active: string;
  onChange: (id: string) => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap gap-1 border-b border-border pb-px", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onChange(tab.id)}
          className={cn(
            "px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors -mb-px border-b-2",
            active === tab.id
              ? "text-sky-300 border-sky-400 bg-sky-500/5"
              : "text-muted border-transparent hover:text-slate-200 hover:bg-slate-800/40"
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className="ml-2 text-xs text-slate-500">({tab.count})</span>
          )}
        </button>
      ))}
    </div>
  );
}
