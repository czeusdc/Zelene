/**
 * @fileoverview Onboarding progress bar — five-dot indicator that
 * animates between introduction → confirm stages.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

const stages = ["introduction", "company", "competitors", "goals", "confirm"];

/**
 * ProgressIndicator — displays five animated dots representing the
 * current onboarding stage. Active and completed stages are filled.
 */
export function ProgressIndicator({ stage }: { stage: string }) {
  const currentIdx = stages.indexOf(stage);
  return (
    <div className="flex items-center gap-2">
      {stages.map((s, i) => (
        <motion.div key={s} animate={{ scale: i === currentIdx ? 1 : 0.6, opacity: i <= currentIdx ? 1 : 0.3 }}
          className="h-1.5 rounded-full"
          style={{
            width: i === currentIdx ? "1.5rem" : "0.375rem",
            background: i <= currentIdx ? "hsl(var(--accent-primary))" : "hsl(var(--text-muted))",
          }} />
      ))}
    </div>
  );
}
