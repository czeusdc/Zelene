"use client";
import { motion } from "framer-motion";

export function ZeleneAvatar({ isThinking }: { isThinking?: boolean }) {
  return (
    <div className="flex flex-col items-center gap-3">
      <motion.div
        animate={isThinking ? { scale: [1, 1.04, 1] } : {}}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        className="relative flex h-14 w-14 items-center justify-center rounded-full"
        style={{ background: "hsla(228, 56%, 52%, 0.12)" }}>
        <div className="h-6 w-6 rounded-full" style={{ background: "hsl(var(--accent-primary))" }} />
        {isThinking && (
          <motion.div animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 rounded-full"
            style={{ boxShadow: "0 0 24px hsla(228, 56%, 52%, 0.3)" }} />
        )}
      </motion.div>
      <span className="text-xs font-medium tracking-widest uppercase" style={{ color: "hsl(var(--text-muted))" }}>Zelene</span>
    </div>
  );
}
