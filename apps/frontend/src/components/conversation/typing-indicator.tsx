"use client";
import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-3 py-2">
      {[0, 1, 2].map((i) => (
        <motion.div key={i} animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
          className="h-1.5 w-1.5 rounded-full" style={{ background: "hsl(var(--accent-primary))" }} />
      ))}
      <span className="text-xs ml-1" style={{ color: "hsl(var(--text-muted))" }}>Zelene is analyzing</span>
    </div>
  );
}
