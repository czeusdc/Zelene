/**
 * @fileoverview SSE-based intelligence stream hook — connects to the backend
 * SSE endpoint and dispatches signals, relationships, insights, and status
 * updates into the global view store.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useEffect } from "react";
import { useViewStore } from "@/stores/view-store";
import { api } from "@/lib/api";
import { Signal, RelationshipEdge, Insight } from "@/lib/types";

/**
 * useIntelligenceStream — opens a Server-Sent Events connection for the active
 * deployment and routes incoming events to the view store.
 */
export function useIntelligenceStream() {
  const deploymentId = useViewStore((s) => s.deploymentId);
  const addSignal = useViewStore((s) => s.addSignal);
  const addMessage = useViewStore((s) => s.addMessage);
  const setConnectionStatus = useViewStore((s) => s.setConnectionStatus);
  const setPhase = useViewStore((s) => s.setPhase);

  useEffect(() => {
    if (!deploymentId) return;
    setConnectionStatus("connecting");
    const url = api.intelligenceStreamUrl(deploymentId);
    const source = new EventSource(url);

    source.addEventListener("signal", (e) => {
      const data = JSON.parse(e.data) as Signal;
      if (data.type !== "status") addSignal(data);
    });

    source.addEventListener("relationship", (e) => {
      const data = JSON.parse(e.data) as RelationshipEdge;
      useViewStore.setState((s) => ({ relationships: [...s.relationships, data] }));
    });

    source.addEventListener("insight", (e) => {
      const data = JSON.parse(e.data) as Insight;
      addMessage({ id: data.id || crypto.randomUUID(), role: "zelene",
        content: `${data.title}\n\n${data.body}`, created_at: new Date().toISOString(), related_insight: data.id });
    });

    source.addEventListener("node_start", (e) => {
      const data = JSON.parse(e.data);
      if (data.node === "deploy" || data.node === "extract") setPhase("gathering");
      else if (data.node === "classify" || data.node === "verify") setPhase("analyzing");
    });

    source.addEventListener("complete", () => { setPhase("active"); setConnectionStatus("connected"); });
    source.onopen = () => setConnectionStatus("connected");
    source.onerror = () => setConnectionStatus("error");

    return () => source.close();
  }, [deploymentId]);
}
