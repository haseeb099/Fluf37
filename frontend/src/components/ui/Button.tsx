import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

const variants: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-sky-600 to-sky-500 text-white border border-sky-400/50 shadow-lg shadow-sky-900/40 hover:from-sky-500 hover:to-sky-400 hover:border-sky-300/60",
  secondary:
    "bg-slate-800/80 text-slate-200 border border-slate-600/40 hover:bg-slate-700/80 hover:border-slate-500/50",
  ghost: "text-slate-300 hover:bg-slate-800/60 border border-transparent",
  danger:
    "bg-red-500/10 text-red-200 border border-red-500/30 hover:bg-red-500/20",
};

const sizes: Record<Size, string> = {
  sm: "text-xs px-2.5 py-1.5 rounded-md",
  md: "text-sm px-3.5 py-2 rounded-lg",
  lg: "text-sm px-5 py-3 rounded-xl font-semibold",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "secondary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";
