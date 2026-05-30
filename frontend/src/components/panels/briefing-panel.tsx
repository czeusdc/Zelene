/**
 * @fileoverview Strategic briefing panel — renders an executive summary
 * of all intelligence data. Shows sections for strategic assessment,
 * key findings, competitive landscape, and recommended actions.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useViewStore } from "@/stores/view-store";

/**
 * BriefingPanel — displays the strategic briefing in a slide-out panel.
 * Accessible from the "Generate Briefing" action on insight cards.
 */
export function BriefingPanel() {
  const briefing = useViewStore((s) => s.briefing);
  const briefingOpen = useViewStore((s) => s.briefingOpen);
  const setBriefingOpen = useViewStore((s) => s.setBriefingOpen);
  const briefingLoading = useViewStore((s) => s.briefingLoading);

  return (
    <AnimatePresence>
      {briefingOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40"
            style={{ background: "rgba(0,0,0,0.5)" }}
            onClick={() => setBriefingOpen(false)}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="fixed right-0 top-0 bottom-0 z-50 w-[420px] flex flex-col overflow-hidden"
            style={{
              background: "hsl(var(--surface-elevated))",
              boxShadow: "-8px 0 32px rgba(0,0,0,0.4)",
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
              <div>
                <span
                  className="text-xs uppercase block"
                  style={{ color: "hsl(var(--accent-primary))", opacity: 0.6, letterSpacing: "0.2em" }}
                >
                  Strategic Briefing
                </span>
                {briefing && (
                  <span className="text-xs" style={{ color: "hsl(var(--text-muted))" }}>
                    {briefing.signal_count} signals · {briefing.entity_count} entities · {briefing.insight_count} insights
                  </span>
                )}
              </div>
              <button
                onClick={() => setBriefingOpen(false)}
                className="rounded-lg p-1.5 transition-all hover:brightness-125"
                style={{ color: "hsl(var(--text-muted))", fontSize: 18 }}
              >
                {"\u2715"}
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {briefingLoading && (
                <div className="flex items-center justify-center h-32">
                  <p className="text-xs animate-pulse-soft" style={{ color: "hsl(var(--text-secondary))" }}>
                    Generating your strategic briefing...
                  </p>
                </div>
              )}

              {briefing && !briefingLoading && (
                <div className="space-y-6">
                  {/* Title */}
                  <h2 className="text-sm font-medium" style={{ color: "hsl(var(--text-primary))" }}>
                    {briefing.title}
                  </h2>

                  {/* Sections */}
                  {briefing.sections.map((section, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: i * 0.1, ease: "easeOut" }}
                    >
                      <h3
                        className="text-xs uppercase mb-2"
                        style={{ color: "hsl(var(--accent-primary))", letterSpacing: "0.1em" }}
                      >
                        {section.heading}
                      </h3>
                      <p
                        className="text-xs leading-relaxed whitespace-pre-line"
                        style={{ color: "hsl(var(--text-secondary))" }}
                      >
                        {section.content}
                      </p>
                    </motion.div>
                  ))}

                  {/* Metadata */}
                  <div
                    className="pt-4 mt-4 text-xs"
                    style={{ borderTop: "1px solid hsl(var(--text-muted) / 0.1)", color: "hsl(var(--text-muted))" }}
                  >
                    Generated {new Date(briefing.generated_at).toLocaleString()}
                  </div>
                </div>
              )}

              {!briefing && !briefingLoading && (
                <div className="flex items-center justify-center h-32">
                  <p className="text-xs text-center" style={{ color: "hsl(var(--text-muted))" }}>
                    Generate a briefing from an insight card to see the executive summary here.
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
