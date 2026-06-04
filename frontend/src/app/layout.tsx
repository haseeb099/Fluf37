import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { NexusWebSocketProvider } from "@/providers/NexusWebSocketProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Fluf37 — Pre-release risk review",
  description:
    "Auditable multi-agent financial intelligence — blind spots, adversarial stress tests, traceback, and audit trail.",
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
    shortcut: ["/icon.svg"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable} flex min-h-screen font-sans`}>
        <NexusWebSocketProvider>
          <Sidebar />
          <main className="flex-1 p-6 md:p-8 overflow-auto bg-void main-canvas">{children}</main>
        </NexusWebSocketProvider>
      </body>
    </html>
  );
}
