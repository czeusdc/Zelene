/**
 * @fileoverview Global Zustand store for the strategic-intelligence View.
 * Holds signals, entities, relationships, chat messages, and UI state
 * (connection status, deployment phase, thinking indicator).
 * Part of the Zelene strategic intelligence platform.
 */

import { create } from "zustand";
import { Signal, Entity, RelationshipEdge, ChatMessage } from "@/lib/types";

/**
 * ViewState — shape of the view store including data arrays and UI flags.
 */
interface ViewState {
  signals: Signal[]; addSignal: (s: Signal) => void;
  entities: Entity[]; setEntities: (e: Entity[]) => void;
  relationships: RelationshipEdge[];
  messages: ChatMessage[]; addMessage: (m: ChatMessage) => void;
  isThinking: boolean; setIsThinking: (t: boolean) => void;
  deploymentId: string | null; setDeploymentId: (id: string | null) => void;
  companyId: string | null; setCompanyId: (id: string | null) => void;
  connectionStatus: "connecting" | "connected" | "simulation" | "error"; setConnectionStatus: (s: ViewState["connectionStatus"]) => void;
  phase: "deploying" | "gathering" | "analyzing" | "active"; setPhase: (p: ViewState["phase"]) => void;
}

export const useViewStore = create<ViewState>((set) => ({
  signals: [],
  addSignal: (signal) => set((s) => ({ signals: [...s.signals, signal] })),
  entities: [],
  setEntities: (entities) => set({ entities }),
  relationships: [],
  messages: [],
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  isThinking: false, setIsThinking: (isThinking) => set({ isThinking }),
  deploymentId: null, setDeploymentId: (id) => set({ deploymentId: id }),
  companyId: null, setCompanyId: (id) => set({ companyId: id }),
  connectionStatus: "connecting", setConnectionStatus: (s) => set({ connectionStatus: s }),
  phase: "deploying", setPhase: (p) => set({ phase: p }),
}));
