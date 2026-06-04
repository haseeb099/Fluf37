import { create } from "zustand";
import type { AgentId, BlindSpot, DecisionOutput, PipelineState, WSEvent } from "@/types/nexus";

interface NexusStore {
  pipelineState: PipelineState;
  agentTokens: Record<string, string>;
  agentOutputs: Record<string, unknown>;
  blindSpots: BlindSpot[];
  decisions: DecisionOutput[];
  isConnected: boolean;
  startPipeline: () => void;
  handleWSEvent: (event: WSEvent) => void;
  resetPipeline: () => void;
  setConnected: (v: boolean) => void;
}

export const useNexusStore = create<NexusStore>((set, get) => ({
  pipelineState: "IDLE",
  agentTokens: {},
  agentOutputs: {},
  blindSpots: [],
  decisions: [],
  isConnected: false,
  startPipeline: () => set({ pipelineState: "CONNECTING", agentTokens: {}, agentOutputs: {} }),
  setConnected: (v) => set({ isConnected: v }),
  resetPipeline: () =>
    set({
      pipelineState: "IDLE",
      agentTokens: {},
      agentOutputs: {},
      blindSpots: [],
      decisions: [],
    }),
  handleWSEvent: (event) => {
    if (event.type === "PIPELINE_STATE" && typeof event.data === "object" && event.data !== null) {
      const state = (event.data as { state?: PipelineState }).state;
      if (state) set({ pipelineState: state });
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
