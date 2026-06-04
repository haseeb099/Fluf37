"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchAuthToken, getCachedAuthToken } from "@/lib/api";
import { parseWSEvent } from "@/lib/wsSchema";
import { useNexusStore } from "@/store/nexusStore";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/nexus/stream";

function buildWsUrl(token: string | null): string {
  if (!token) return WS_URL;
  const sep = WS_URL.includes("?") ? "&" : "?";
  return `${WS_URL}${sep}token=${encodeURIComponent(token)}`;
}

/** Avoid closing a socket while CONNECTING — that spuriously warns in DevTools. */
function closeWebSocket(ws: WebSocket, reason = "unmount") {
  if (ws.readyState === WebSocket.CONNECTING) {
    ws.addEventListener("open", () => ws.close(1000, reason), { once: true });
    return;
  }
  if (ws.readyState === WebSocket.OPEN) {
    ws.close(1000, reason);
  }
}

export function useNexusWebSocket() {
  const reconnectCountRef = useRef(0);
  const [reconnectCount, setReconnectCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const storeRef = useRef({
    handleWSEvent: useNexusStore.getState().handleWSEvent,
    setConnected: useNexusStore.getState().setConnected,
    clearError: useNexusStore.getState().clearError,
    setLastError: useNexusStore.getState().setLastError,
  });

  storeRef.current = {
    handleWSEvent: useNexusStore.getState().handleWSEvent,
    setConnected: useNexusStore.getState().setConnected,
    clearError: useNexusStore.getState().clearError,
    setLastError: useNexusStore.getState().setLastError,
  };

  const { setLastError } = useNexusStore();

  useEffect(() => {
    let active = true;

    const clearReconnectTimer = () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    const connect = () => {
      if (!active) return;
      clearReconnectTimer();

      const token = getCachedAuthToken();
      const ws = new WebSocket(buildWsUrl(token));
      wsRef.current = ws;

      ws.onopen = () => {
        if (!active) {
          closeWebSocket(ws);
          return;
        }
        storeRef.current.setConnected(true);
        storeRef.current.clearError();
        if (token) {
          ws.send(JSON.stringify({ type: "AUTH", token }));
        }
      };

      ws.onclose = () => {
        if (!active) return;
        storeRef.current.setConnected(false);
        reconnectCountRef.current += 1;
        const attempt = reconnectCountRef.current;
        setReconnectCount(attempt);
        const delay = Math.min(30000, 1000 * 2 ** attempt);
        reconnectTimerRef.current = setTimeout(connect, delay);
      };

      ws.onmessage = (msg) => {
        try {
          const parsed = JSON.parse(msg.data) as unknown;
          const event = parseWSEvent(parsed);
          if (event) storeRef.current.handleWSEvent(event);
        } catch {
          /* ignore malformed */
        }
      };
    };

    fetchAuthToken().catch(() => {
      /* demo: API key on REST still works */
    });
    connect();

    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "PING" }));
      }
    }, 30000);

    return () => {
      active = false;
      clearReconnectTimer();
      clearInterval(ping);
      const ws = wsRef.current;
      if (!ws) return;
      ws.onclose = null;
      ws.onopen = null;
      ws.onmessage = null;
      wsRef.current = null;
      closeWebSocket(ws);
    };
  }, []);

  const send = useCallback((payload: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
      return true;
    }
    setLastError("WebSocket not connected");
    return false;
  }, [setLastError]);

  const runPipeline = useCallback(() => {
    if (!useNexusStore.getState().isConnected) {
      setLastError("Connect WebSocket before running pipeline");
      return;
    }
    useNexusStore.getState().startPipeline();
    const sent = send({ type: "RUN_PIPELINE", mode: "demo" });
    if (!sent) {
      setLastError("Could not send RUN_PIPELINE");
    }
  }, [send, setLastError]);

  return {
    isConnected: useNexusStore((s) => s.isConnected),
    reconnectCount,
    lastError: useNexusStore((s) => s.lastError),
    send,
    runPipeline,
  };
}
