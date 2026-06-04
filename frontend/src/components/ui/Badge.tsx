import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "success" | "warning" | "critical" | "outline";

const styles: Record<BadgeVariant, string> = {
  default: "bg-slate-800 text-slate-300 border-slate-600/40",
  success: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  critical: "bg-red-500/15 text-red-300 border-red-500/30",
  outline: "bg-transparent text-slate-400 border-slate-600/50",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
        styles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
