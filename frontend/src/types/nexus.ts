export type AgentId =
  | "connector"
  | "silent_finder"
  | "adversarial"
  | "traceback"
  | "decision"
  | "evolution";

export type PipelineState =
  | "IDLE"
  | "CONNECTING"
  | "CONNECTED"
  | "ANALYZING"
  | "ATTACKING"
  | "TRACING"
  | "DECIDING"
  | "EVOLVING"
  | "COMPLETE"
  | "ERROR";

/** WebSocket AUTH handshake — not a pipeline phase. */
export type WsAuthStatus = "pending" | "authenticated" | "failed";

export type SourceType = "crm" | "erp" | "bank" | "trading" | "news" | "custom";

export interface ConnectionStatus {
  source_type: SourceType;
  state: string;
  last_sync?: string;
  freshness_seconds?: number;
  message?: string;
}

export interface BlindSpot {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  confidence: number;
}

export interface DecisionOutput {
  id: string;
  decision_type: string;
  recommendation: string;
  confidence: number;
  adversarial_stress_passed: boolean;
}

export interface WSEvent {
  type: string;
  agent_id: string;
  data: unknown;
  timestamp?: string;
}
