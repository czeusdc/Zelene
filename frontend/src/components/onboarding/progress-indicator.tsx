/**
 * @fileoverview Onboarding progress bar — thin horizontal line that
 * fills left-to-right based on the current stage.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

const stages = ["introduction", "company", "competitors", "goals", "confirm"];

/**
 * ProgressIndicator — displays a thin horizontal line that fills
 * proportionally to the current onboarding stage.
 */
export function ProgressIndicator({ stage }: { stage: string }) {
  const currentIdx = stages.indexOf(stage);
  const progress = Math.max(0, Math.min(1, (currentIdx + 1) / stages.length));

  return (
    <div className="w-32 h-0.5 rounded-full overflow-hidden" style={{ background: "hsl(var(--text-muted) / 0.15)" }}>
      <motion.div
        className="h-full rounded-full"
        style={{ background: "hsl(var(--accent-primary))" }}
        initial={{ width: 0 }}
        animate={{ width: `${progress * 100}%` }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      />
    </div>
  );
}
