/**
 * @fileoverview Insight card component for the single evolving presence right panel.
 * Renders ONE active Zelene thought at a time with states: emerging (typing),
 * presenting (full display with actions), acknowledged (collapsed summary),
 * and dismissed (removed). Previous insights collapse to summaries below.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Insight } from "@/lib/types";
import { TypingText } from "@/components/ui/typing-text";
import { useViewStore } from "@/stores/view-store";
import { useEffect, useRef } from "react";

/**
 * InsightCard — displays a single Zelene insight with presence states.
 * When isActive is true, shows the full typed insight. When acknowledged,
 * collapses to a single summary line. Supports re-expansion.
 */
export function InsightCard({
  insight,
  isActive,
}: {
  insight: Insight;
  isActive: boolean;
}) {
  const insightStates = useViewStore((s) => s.insightStates);
  const setInsightState = useViewStore((s) => s.setInsightState);
  const setActiveInsight = useViewStore((s) => s.setActiveInsight);
  const state = insightStates[insight.id] || "presenting";
  const hasEmerged = useRef(false);

  // Mark as emerging on first active mount, then transition to presenting after typing
  useEffect(() => {
    if (isActive && !hasEmerged.current && !insightStates[insight.id]) {
      hasEmerged.current = true;
      setInsightState(insight.id, "emerging");
      const timer = setTimeout(() => {
        setInsightState(insight.id, "presenting");
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [insight.id, isActive, insightStates, setInsightState]);

  const handleDismiss = () => {
    setInsightState(insight.id, "dismissed");
    setActiveInsight(null);
  };

  const handleMonitor = () => {
    // Keep this insight tracked
    setInsightState(insight.id, "acknowledged");
  };

  // Dismissed insights are hidden entirely
  if (state === "dismissed") return null;

  // Acknowledged (collapsed) insight — tap to re-expand
  if (state === "acknowledged" && !isActive) {
    return (
      <motion.button
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full text-left rounded-lg px-3 py-2 mb-2 text-xs group"
        style={{
          background: "hsl(var(--surface-overlay))",
          border: "1px solid hsl(var(--text-muted) / 0.1)",
          color: "hsl(var(--text-secondary))",
        }}
        onClick={() => setActiveInsight(insight.id)}
      >
        <span className="text-xs font-medium" style={{ color: "hsl(var(--accent-primary))" }}>
          Zelene
        </span>
        {" · "}
        <span className="group-hover:opacity-80 transition-opacity">
          {insight.title.length > 80 ? insight.title.slice(0, 80) + "..." : insight.title}
        </span>
      </motion.button>
    );
  }

  // Active insight — full display with typing animation
  return (
    <AnimatePresence>
      <motion.div
        key={insight.id}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8, transition: { duration: 0.3 } }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="mb-4"
      >
        <div
          className="rounded-xl p-4"
          style={{
            background: "hsl(var(--surface-overlay))",
            border: "1px solid hsl(var(--text-muted) / 0.2)",
          }}
        >
          {/* Zelene identity header */}
          <div className="flex items-center gap-2 mb-3">
            <motion.div
              className="h-3 w-3 rounded-full"
              style={{ background: "hsl(var(--accent-primary))" }}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
            <span
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "hsl(var(--accent-primary))" }}
            >
              Zelene
            </span>
          </div>

          {/* Title */}
          <p className="text-sm leading-relaxed mb-2" style={{ color: "hsl(var(--text-primary))" }}>
            {insight.title}
          </p>

          {/* Body with typing reveal */}
          <p className="text-xs leading-relaxed mb-3" style={{ color: "hsl(var(--text-secondary))" }}>
            {state === "emerging" ? (
              <TypingText text={insight.body} messageId={insight.id} speed={25} />
            ) : (
              insight.body
            )}
          </p>

          {/* Reasoning */}
          {insight.reasoning && (
            <p className="text-xs italic mb-3" style={{ color: "hsl(var(--text-muted))" }}>
              {insight.reasoning}
            </p>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleMonitor}
              className="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors hover:opacity-80"
              style={{
                background: "hsl(var(--surface-elevated))",
                color: "hsl(var(--text-secondary))",
                border: "1px solid hsl(var(--text-muted) / 0.15)",
              }}
            >
              Monitor
            </button>
            <button
              onClick={handleDismiss}
              className="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors hover:opacity-80"
              style={{
                background: "hsl(var(--surface-elevated))",
                color: "hsl(var(--text-secondary))",
                border: "1px solid hsl(var(--text-muted) / 0.15)",
              }}
            >
              Dismiss
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * InsightPresence — renders the single evolving presence area.
 * Shows the active insight in full, and previous insights as collapsed summaries.
 * User chat messages remain below the insight area.
 */
export function InsightPresence({ insights }: { insights: Insight[] }) {
  const activeInsightId = useViewStore((s) => s.activeInsightId);
  const insightStates = useViewStore((s) => s.insightStates);

  if (insights.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <p className="text-xs text-center" style={{ color: "hsl(var(--text-muted))" }}>
          Zelene will surface strategic insights here as intelligence is gathered.
        </p>
      </div>
    );
  }

  // Active insight (one at a time) and acknowledged (collapsed) ones
  const active = insights.find((i) => i.id === activeInsightId) || insights[0];
  const rest = insights.filter((i) => i.id !== active.id);

  return (
    <div className="space-y-1">
      {/* Active insight — full display */}
      <InsightCard insight={active} isActive={true} />

      {/* Previous insights — collapsed summaries */}
      <div className="pt-2" style={{ borderTop: "1px solid hsl(var(--text-muted) / 0.06)" }}>
        {rest
          .filter((i) => insightStates[i.id] !== "dismissed")
          .map((insight) => (
            <InsightCard key={insight.id} insight={insight} isActive={false} />
          ))}
      </div>
    </div>
  );
}
