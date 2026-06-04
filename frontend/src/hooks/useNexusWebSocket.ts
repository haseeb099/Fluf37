"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useNexusStore } from "@/store/nexusStore";
import type { WSEvent } from "@/types/nexus";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/nexus/stream";

export function useNexusWebSocket() {
  const [reconnectCount, setReconnectCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const { handleWSEvent, setConnected, startPipeline } = useNexusStore();

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setReconnectCount((c) => c + 1);
      setTimeout(connect, Math.min(30000, 1000 * 2 ** reconnectCount));
    };
    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as WSEvent;
        handleWSEvent(event);
      } catch {
        /* ignore */
      }
    };
  }, [handleWSEvent, setConnected, reconnectCount]);

  useEffect(() => {
    connect();
    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "PING" }));
      }
    }, 30000);
    return () => {
      clearInterval(ping);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((payload: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  const runPipeline = useCallback(() => {
    startPipeline();
    send({ type: "RUN_PIPELINE", mode: "demo" });
  }, [send, startPipeline]);

  return {
    isConnected: useNexusStore((s) => s.isConnected),
    reconnectCount,
    send,
    runPipeline,
  };
}
