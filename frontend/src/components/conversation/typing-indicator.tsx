/**
 * @fileoverview Typing indicator — three animated dots with a
 * "Zelene is analyzing" label, shown while the backend is processing.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const THINKING_PHRASES = [
  "Zelene is analyzing",
  "Zelene is thinking",
  "Zelene is observing",
  "Zelene is reflecting",
  "Zelene is watching",
  "Zelene is considering",
];

/**
 * TypingIndicator — renders three pulsing dots and a cycling label to
 * indicate that Zelene is processing a request.
 */
export function TypingIndicator() {
  const [phrase, setPhrase] = useState(THINKING_PHRASES[0]);
  useEffect(() => {
    const interval = setInterval(() => {
      setPhrase((p) => {
        const current = THINKING_PHRASES.indexOf(p);
        return THINKING_PHRASES[(current + 1) % THINKING_PHRASES.length];
      });
    }, 2500);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="flex items-center gap-1.5 px-3 py-2">
      {[0, 1, 2].map((i) => (
        <motion.div key={i} animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
          className="h-1.5 w-1.5 rounded-full" style={{ background: "hsl(var(--accent-primary))" }} />
      ))}
      <span className="text-xs ml-1" style={{ color: "hsl(var(--text-muted))" }}>{phrase}...</span>
    </div>
  );
}
