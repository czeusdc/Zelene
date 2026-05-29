/**
 * @fileoverview Status bar — fixed bottom bar displaying live counts
 * of signals, entities, relationships, and overall confidence. Updates
 * in real time as the Zustand store changes.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useViewStore } from "@/stores/view-store";

/**
 * StatusBar — renders a 28px tall fixed bar at the bottom of The View
 * with real-time counts from the global store.
 */
export function StatusBar() {
  const signals = useViewStore((s) => s.signals);
  const entities = useViewStore((s) => s.entities);
  const relationships = useViewStore((s) => s.relationships);

  const confidence = signals.length > 0
    ? Math.round(signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length * 100)
    : 0;

  return (
    <div
      className="shrink-0 flex items-center justify-center text-xs"
      style={{
        height: 28,
        background: "hsl(var(--surface-base))",
        color: "hsl(var(--text-secondary))",
        opacity: 0.85,
        letterSpacing: "0.15em",
        borderTop: "1px solid hsl(var(--text-muted) / 0.06)",
      }}
    >
      <span>signals: {signals.length}</span>
      <span className="mx-2">&middot;</span>
      <span>entities: {entities.length}</span>
      <span className="mx-2">&middot;</span>
      <span>relationships: {relationships.length}</span>
      <span className="mx-2">&middot;</span>
      <span>confidence: {confidence}%</span>
    </div>
  );
}
