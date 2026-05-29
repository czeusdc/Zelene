/**
 * @fileoverview Zelene avatar icon used during onboarding.
 * A breathing dot communicates presence and the "thinking" state.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

/**
 * ZeleneAvatar — renders a breathing dot avatar with the Zelene label.
 * The dot pulses opacity to create a sense of living presence.
 */
export function ZeleneAvatar({ isThinking }: { isThinking?: boolean }) {
  return (
    <div className="flex flex-col items-center gap-3">
      <motion.div
        className="h-3 w-3 rounded-full"
        style={{ background: "hsl(var(--accent-primary))" }}
        animate={isThinking ? { opacity: [0.6, 1, 0.6], scale: [1, 1.2, 1] } : { opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      />
      <span className="text-xs font-medium tracking-widest uppercase" style={{ color: "hsl(var(--text-muted))" }}>Zelene</span>
    </div>
  );
}
