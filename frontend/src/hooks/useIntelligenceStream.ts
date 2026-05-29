/**
 * @fileoverview SSE-based intelligence stream hook — connects to the backend
 * SSE endpoint and dispatches signals, relationships, insights, and status
 * updates into the global view store. Also drives focus-state choreography
 * so the UI emphasizes the panel most relevant to incoming data, and
 * manages the silence moment after the intelligence run completes.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useEffect } from "react";
import { useViewStore } from "@/stores/view-store";
import { api } from "@/lib/api";
import { Signal, RelationshipEdge, Insight, Entity, Source } from "@/lib/types";

/** Module-level timer to debounce returning focus to balanced. */
let focusTimeout: ReturnType<typeof setTimeout> | null = null;

function setTemporaryFocus(focus: "signal" | "graph" | "chat", duration: number) {
  useViewStore.getState().setFocusState(focus);
  if (focusTimeout) clearTimeout(focusTimeout);
  focusTimeout = setTimeout(() => {
    useViewStore.getState().setFocusState("balanced");
  }, duration);
}

/**
 * useIntelligenceStream — opens a Server-Sent Events connection for the active
 * deployment and routes incoming events to the view store.
 */
export function useIntelligenceStream() {
  const deploymentId = useViewStore((s) => s.deploymentId);
  const addSignal = useViewStore((s) => s.addSignal);
  const addSource = useViewStore((s) => s.addSource);
  const addMessage = useViewStore((s) => s.addMessage);
  const setConnectionStatus = useViewStore((s) => s.setConnectionStatus);
  const setPhase = useViewStore((s) => s.setPhase);
  const setIsThinking = useViewStore((s) => s.setIsThinking);
  const setSilence = useViewStore((s) => s.setSilence);

  useEffect(() => {
    if (!deploymentId) return;
    setConnectionStatus("connecting");
    const url = api.intelligenceStreamUrl(deploymentId);
    const source = new EventSource(url);

    source.addEventListener("signal", (e) => {
      const data = JSON.parse(e.data) as Signal;
      if (data.type !== "status") addSignal(data);
      setTemporaryFocus("signal", 3000);
    });

    source.addEventListener("source", (e) => {
      const data = JSON.parse(e.data) as Source;
      addSource(data);
    });

    source.addEventListener("relationship", (e) => {
      const data = JSON.parse(e.data) as RelationshipEdge;
      useViewStore.setState((s) => ({ relationships: [...s.relationships, data] }));
      setTemporaryFocus("graph", 3000);
    });

    source.addEventListener("entity", (e) => {
      const data = JSON.parse(e.data) as Entity;
      useViewStore.setState((s) => ({ entities: [...s.entities, data] }));
      setTemporaryFocus("graph", 3000);
    });

    source.addEventListener("insight", (e) => {
      const data = JSON.parse(e.data) as Insight;
      addMessage({ id: data.id || crypto.randomUUID(), role: "zelene",
        content: `${data.title}\n\n${data.body}`, created_at: new Date().toISOString(), related_insight: data.id });
      setTemporaryFocus("chat", 4000);
    });

    source.addEventListener("node_start", (e) => {
      const data = JSON.parse(e.data);
      // Map each pipeline node to a user-facing phase label
      if (data.node === "deploy") {
        setPhase("gathering");
        // Capture simulation flags from the deploy node for future UI (force-sim toggle)
        if (data.llm_simulation || data.data_simulation) {
          useViewStore.setState({ llmSimulation: data.llm_simulation, dataSimulation: data.data_simulation });
        }
      } else if (data.node === "extract") {
        setPhase("gathering");
      } else if (data.node === "classify" || data.node === "verify") {
        setPhase("analyzing");
      } else if (data.node === "synthesize") {
        setPhase("synthesizing");
        setIsThinking(true);  // synthesis is the 120s LLM call — show thinking state
      }
    });

    source.addEventListener("complete", () => {
      setPhase("active");
      setIsThinking(false);
      setConnectionStatus("connected");
      setSilence(true);
      setTimeout(() => {
        setSilence(false);
        addMessage({
          id: crypto.randomUUID(),
          role: "zelene",
          content: "Synthesis complete. Your intelligence environment is now active.",
          created_at: new Date().toISOString(),
        });
      }, 2000);
    });

    source.onopen = () => setConnectionStatus("connected");
    source.onerror = () => setConnectionStatus("error");

    return () => {
      source.close();
      if (focusTimeout) {
        clearTimeout(focusTimeout);
        focusTimeout = null;
      }
    };
  }, [deploymentId]);
}
