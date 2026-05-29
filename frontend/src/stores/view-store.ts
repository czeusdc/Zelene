/**
 * @fileoverview Global Zustand store for the strategic-intelligence View.
 * Holds signals, entities, relationships, chat messages, UI state
 * (connection status, deployment phase, thinking indicator, simulation
 * flags), and focus state for dynamic panel emphasis.
 * Part of the Zelene strategic intelligence platform.
 */

import { create } from "zustand";
import { Signal, Entity, RelationshipEdge, ChatMessage, Source } from "@/lib/types";

/**
 * ViewState — shape of the view store including data arrays and UI flags.
 */
interface ViewState {
  signals: Signal[]; addSignal: (s: Signal) => void;
  sources: Source[]; addSource: (s: Source) => void;
  entities: Entity[]; setEntities: (e: Entity[]) => void;
  relationships: RelationshipEdge[];
  messages: ChatMessage[]; addMessage: (m: ChatMessage) => void;
  isThinking: boolean; setIsThinking: (t: boolean) => void;
  /** True when the LLM is in simulation/demo mode (no AIMLAPI key used). */
  llmSimulation: boolean;
  /** True when Bright Data is in simulation/demo mode (no BD key used). */
  dataSimulation: boolean;
  deploymentId: string | null; setDeploymentId: (id: string | null) => void;
  companyId: string | null; setCompanyId: (id: string | null) => void;
  connectionStatus: "connecting" | "connected" | "simulation" | "error"; setConnectionStatus: (s: ViewState["connectionStatus"]) => void;
  phase: "deploying" | "gathering" | "analyzing" | "synthesizing" | "active"; setPhase: (p: ViewState["phase"]) => void;
  focusState: "signal" | "graph" | "chat" | "balanced"; setFocusState: (f: ViewState["focusState"]) => void;
  silence: boolean; setSilence: (v: boolean) => void;
}

export const useViewStore = create<ViewState>((set) => ({
  signals: [],
  addSignal: (signal) => set((s) => ({ signals: [...s.signals, signal] })),
  sources: [],
  addSource: (source) => set((s) => ({ sources: [...s.sources, source] })),
  entities: [],
  setEntities: (entities) => set({ entities }),
  relationships: [],
  messages: [],
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  isThinking: false, setIsThinking: (isThinking) => set({ isThinking }),
  llmSimulation: false, dataSimulation: false,
  deploymentId: null, setDeploymentId: (id) => set({ deploymentId: id }),
  companyId: null, setCompanyId: (id) => set({ companyId: id }),
  connectionStatus: "connecting", setConnectionStatus: (s) => set({ connectionStatus: s }),
  phase: "deploying", setPhase: (p) => set({ phase: p }),
  focusState: "balanced", setFocusState: (f) => set({ focusState: f }),
  silence: false, setSilence: (v) => set({ silence: v }),
}));
