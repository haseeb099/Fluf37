"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useNexusWebSocket } from "@/hooks/useNexusWebSocket";

type NexusWsContextValue = ReturnType<typeof useNexusWebSocket>;

const NexusWsContext = createContext<NexusWsContextValue | null>(null);

export function NexusWebSocketProvider({ children }: { children: ReactNode }) {
  const value = useNexusWebSocket();
  return <NexusWsContext.Provider value={value}>{children}</NexusWsContext.Provider>;
}

export function useNexusWs() {
  const ctx = useContext(NexusWsContext);
  if (!ctx) {
    throw new Error("useNexusWs must be used within NexusWebSocketProvider");
  }
  return ctx;
}
