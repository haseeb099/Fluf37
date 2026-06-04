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
      <header className="mb-6 pb-4 border-b border-border/60">
        <h2 className="text-lg font-semibold text-slate-200">{title}</h2>
        {subtitle && <p className="text-sm text-muted mt-1">{subtitle}</p>}
      </header>
      {children}
    </div>
  );
}
