/**
 * @fileoverview Global Zustand store for the strategic-intelligence View.
 * Holds signals, entities, relationships, chat messages, UI state
 * (connection status, deployment phase, thinking indicator, simulation
 * flags), focus state for dynamic panel emphasis, and active insight
 * tracking for the single evolving presence right panel.
 * Part of the Zelene strategic intelligence platform.
 */

import { create } from "zustand";
import { Signal, Entity, RelationshipEdge, ChatMessage, Source, Insight, Briefing, MemoryStatus } from "@/lib/types";

/** Insight tracking states for the single evolving presence right panel. */
type InsightState = "emerging" | "presenting" | "acknowledged" | "dismissed";

/** Visible intelligence process states for the discovery phase indicator. */
type DiscoveryPhase = "idle" | "discovering" | "reviewing" | "validating" | "connecting" | "understanding";

/**
 * ViewState — shape of the view store including data arrays and UI flags.
 */
interface ViewState {
  signals: Signal[]; addSignal: (s: Signal) => void;
  sources: Source[]; addSource: (s: Source) => void;
  entities: Entity[]; setEntities: (e: Entity[]) => void;
  relationships: RelationshipEdge[];
  messages: ChatMessage[]; addMessage: (m: ChatMessage) => void;
  /** Insights received via SSE — preserves full metadata (confidence, reasoning, evidence_signals). */
  insights: Insight[]; addInsight: (insight: Insight) => void;
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
  /** Single evolving presence — tracks which insight is currently active in the right panel. */
  activeInsightId: string | null; setActiveInsight: (id: string | null) => void;
  /** Map of insight IDs to their display state for presence transitions. */
  insightStates: Record<string, InsightState>; setInsightState: (id: string, state: InsightState) => void;
  /** Current intelligence discovery phase — drives the visible process indicator in the signal feed. */
  discoveryPhase: DiscoveryPhase; setDiscoveryPhase: (p: DiscoveryPhase) => void;
  /** Memory status — whether intelligence has been persisted to Cognee. */
  memoryStatus: MemoryStatus | null; setMemoryStatus: (m: MemoryStatus | null) => void;
  /** Strategic briefing generated from all intelligence. */
  briefing: Briefing | null; setBriefing: (b: Briefing | null) => void;
  /** Whether a briefing is currently being generated. */
  briefingLoading: boolean; setBriefingLoading: (v: boolean) => void;
  /** Whether the briefing panel is visible. */
  briefingOpen: boolean; setBriefingOpen: (v: boolean) => void;
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
  insights: [],
  addInsight: (insight) => set((s) => ({ insights: [...s.insights, insight] })),
  isThinking: false, setIsThinking: (isThinking) => set({ isThinking }),
  llmSimulation: false, dataSimulation: false,
  deploymentId: null, setDeploymentId: (id) => set({ deploymentId: id }),
  companyId: null, setCompanyId: (id) => set({ companyId: id }),
  connectionStatus: "connecting", setConnectionStatus: (s) => set({ connectionStatus: s }),
  phase: "deploying", setPhase: (p) => set({ phase: p }),
  focusState: "balanced", setFocusState: (f) => set({ focusState: f }),
  silence: false, setSilence: (v) => set({ silence: v }),
  activeInsightId: null, setActiveInsight: (id) => set({ activeInsightId: id }),
  insightStates: {}, setInsightState: (id, state) => set((s) => ({ insightStates: { ...s.insightStates, [id]: state } })),
  discoveryPhase: "idle", setDiscoveryPhase: (p) => set({ discoveryPhase: p }),
  memoryStatus: null, setMemoryStatus: (m) => set({ memoryStatus: m }),
  briefing: null, setBriefing: (b) => set({ briefing: b }),
  briefingLoading: false, setBriefingLoading: (v) => set({ briefingLoading: v }),
  briefingOpen: false, setBriefingOpen: (v) => set({ briefingOpen: v }),
}));
