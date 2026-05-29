/**
 * @fileoverview Settings slide-out drawer — theme toggle only.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "@/hooks/useTheme";

/**
 * SettingsDrawer — slide-out drawer panel for theme selection.
 */
export function SettingsDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <AnimatePresence>
      {open && (<>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={onClose} className="fixed inset-0 z-40" style={{ background: "rgba(0,0,0,0.4)" }} />
        <motion.div
          initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="fixed right-0 top-0 bottom-0 z-50 w-80 p-6 overflow-y-auto"
          style={{ background: "hsl(var(--surface-base))", borderLeft: "1px solid hsl(var(--text-muted) / 0.1)" }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium">Settings</h3>
            <button onClick={onClose} className="text-lg" style={{ color: "hsl(var(--text-muted))" }}>
              {"\u2715"}
            </button>
          </div>

          <div className="mb-6">
            <h4 className="text-xs uppercase tracking-widest mb-3" style={{ color: "hsl(var(--text-muted))" }}>
              Theme
            </h4>
            <div className="flex gap-2">
              {["dark", "light"].map((t) => (
                <button key={t} onClick={() => theme !== t && toggleTheme()}
                  className="flex-1 rounded-lg py-2 text-xs capitalize"
                  style={{
                    background: theme === t ? "hsl(var(--accent-primary) / 0.15)" : "hsl(var(--surface-overlay))",
                    color: theme === t ? "hsl(var(--accent-primary))" : "hsl(var(--text-secondary))",
                  }}>
                  {t}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </>)}
    </AnimatePresence>
  );
}
