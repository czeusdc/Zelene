/**
 * @fileoverview Top bar of the strategic-intelligence View.
 * Shows the Zelene logo, memory status indicator, and a settings gear button.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useViewStore } from "@/stores/view-store";
import { motion, AnimatePresence } from "framer-motion";

/**
 * ViewHeader — renders the View's top bar with Zelene title,
 * memory status indicator, and a settings button.
 */
export function ViewHeader({ onSettingsClick }: { onSettingsClick: () => void }) {
  const memoryStatus = useViewStore((s) => s.memoryStatus);

  return (
    <header className="flex items-center justify-between px-6 py-2 border-b" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
      <div className="flex items-center gap-4">
        <h1 className="text-base font-normal uppercase tracking-widest" style={{ letterSpacing: "0.18em" }}>
          {"Z E L E N E".split(" ").map((char, i) =>
            i === 1 || i === 3 ? (
              <span key={i} style={{ color: "hsl(var(--accent-secondary))", animation: "letter-breath 3s ease-in-out infinite" }}>{char} </span>
            ) : (
              <span key={i}>{char} </span>
            )
          )}
        </h1>

        {/* Memory status indicator */}
        <AnimatePresence>
          {memoryStatus && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="flex items-center gap-2"
            >
              <motion.div
                className="h-1.5 w-1.5 rounded-full"
                style={{ background: memoryStatus.type === "cognee" ? "hsl(var(--accent-secondary))" : "hsl(var(--text-muted))" }}
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              />
              <span
                className="text-xs"
                style={{ color: "hsl(var(--text-muted))", letterSpacing: "0.05em" }}
              >
                {memoryStatus.type === "cognee" ? "Memory active" : "Session memory"}
                {" · "}
                {memoryStatus.entity_count} entities
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <button onClick={onSettingsClick} className="rounded-lg p-1.5 transition-all hover:brightness-125" style={{ color: "hsl(var(--text-muted))", fontSize: 24, lineHeight: 1 }}>{"\u2699"}</button>
    </header>
  );
}
