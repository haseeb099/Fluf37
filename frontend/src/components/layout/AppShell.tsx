"use client";

import { type ReactNode } from "react";

interface AppShellProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function AppShell({ title, subtitle, children }: AppShellProps) {
  return (
    <div className="max-w-7xl mx-auto w-full">
      <header className="mb-8 pb-5 border-b border-border/60">
        <h2 className="text-xl font-semibold text-slate-100 tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-muted mt-1.5 max-w-3xl leading-relaxed">{subtitle}</p>}
      </header>
      {children}
    </div>
  );
}
