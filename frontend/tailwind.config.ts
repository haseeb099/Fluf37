import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "var(--bg-void)",
        surface: "var(--bg-surface)",
        elevated: "var(--bg-elevated)",
        accent: "var(--accent-primary)",
        muted: "var(--text-muted)",
        border: "var(--border-subtle)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 32px rgba(0,0,0,0.35)",
        glow: "0 0 24px rgba(56, 189, 248, 0.12)",
        "glow-lg": "0 0 40px rgba(56, 189, 248, 0.18)",
      },
    },
  },
  plugins: [],
};
export default config;
