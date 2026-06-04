import { create } from "zustand";
import type { ParsedWSEvent } from "@/lib/wsSchema";
import { formatAgentError } from "@/lib/formatAgentError";
import type { BlindSpot, DecisionOutput, PipelineState, WsAuthStatus } from "@/types/nexus";

const PIPELINE_STATES: PipelineState[] = [
  "IDLE",
  "CONNECTING",
  "CONNECTED",
  "ANALYZING",
  "ATTACKING",
  "TRACING",
  "DECIDING",
  "EVOLVING",
  "COMPLETE",
  "ERROR",
];

function isPipelineState(value: string): value is PipelineState {
  return (PIPELINE_STATES as string[]).includes(value);
}

interface NexusStore {
  pipelineState: PipelineState;
  agentTokens: Record<string, string>;
  agentOutputs: Record<string, unknown>;
  blindSpots: BlindSpot[];
  decisions: DecisionOutput[];
  isConnected: boolean;
  wsAuthStatus: WsAuthStatus;
  lastError: string | null;
  startPipeline: () => void;
  handleWSEvent: (event: ParsedWSEvent) => void;
  resetPipeline: () => void;
  setConnected: (v: boolean) => void;
  setWsAuthStatus: (status: WsAuthStatus) => void;
  setLastError: (msg: string | null) => void;
  clearError: () => void;
}

export const useNexusStore = create<NexusStore>((set) => ({
  pipelineState: "IDLE",
  agentTokens: {},
  agentOutputs: {},
  blindSpots: [],
  decisions: [],
  isConnected: false,
  wsAuthStatus: "pending",
  lastError: null,
  startPipeline: () =>
    set({ pipelineState: "CONNECTING", agentTokens: {}, agentOutputs: {}, lastError: null }),
  setConnected: (v) =>
    set({
      isConnected: v,
      wsAuthStatus: v ? useNexusStore.getState().wsAuthStatus : "pending",
    }),
  setWsAuthStatus: (status) => set({ wsAuthStatus: status }),
  setLastError: (msg) => set({ lastError: msg }),
  clearError: () => set({ lastError: null }),
  resetPipeline: () =>
    set({
      pipelineState: "IDLE",
      agentTokens: {},
      agentOutputs: {},
      blindSpots: [],
      decisions: [],
      lastError: null,
    }),
  handleWSEvent: (event) => {
    if (event.type === "AGENT_ERROR") {
      if (event.agent_id === "system" && event.data === "invalid_token") {
        set({ wsAuthStatus: "failed", lastError: "WebSocket authentication failed" });
        return;
      }
      set({ lastError: formatAgentError(event.data) });
      return;
    }
    if (event.type === "PIPELINE_STATE" && typeof event.data === "object" && event.data !== null) {
      const state = (event.data as { state?: string }).state;
      if (!state) return;
      if (state === "AUTHENTICATED") {
        set({ wsAuthStatus: "authenticated" });
        return;
      }
      if (isPipelineState(state)) {
        set({ pipelineState: state });
        if (state === "ERROR") {
          set({ lastError: "Pipeline entered error state" });
        }
        if (state === "COMPLETE") {
          set({ lastError: null });
          const report = (event.data as { report?: { decisions?: DecisionOutput[] } }).report;
          if (report?.decisions?.length) {
            set({ decisions: report.decisions });
          }
        }
      }
    }
    if (event.type === "AGENT_TOKEN" && typeof event.data === "string") {
      const id = event.agent_id;
      set((s) => ({
        agentTokens: { ...s.agentTokens, [id]: (s.agentTokens[id] || "") + event.data },
      }));
    }
    if (event.type === "AGENT_COMPLETE") {
      const id = event.agent_id;
      set((s) => ({ agentOutputs: { ...s.agentOutputs, [id]: event.data } }));
      if (id === "silent_finder" && event.data && typeof event.data === "object") {
        const spots = (event.data as { blind_spots?: BlindSpot[] }).blind_spots || [];
        set({ blindSpots: spots });
      }
      if (id === "decision" && event.data && typeof event.data === "object") {
        const decs = (event.data as { decisions?: DecisionOutput[] }).decisions || [];
        set({ decisions: decs });
      }
    }
  },
}));
