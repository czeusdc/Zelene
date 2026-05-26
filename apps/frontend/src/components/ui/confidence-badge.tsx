"use client";
import { motion } from "framer-motion";

export function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 85 ? "hsl(var(--signal-positive))" : pct >= 70 ? "hsl(var(--signal-warning))" : "hsl(var(--signal-critical))";
  return (
    <motion.span animate={pct < 75 ? { opacity: [0.9, 0.5, 0.9] } : {}}
      transition={{ duration: 2, repeat: Infinity }}
      className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
      style={{ background: `${color}15`, color }}>
      <span className="inline-block h-1.5 w-1.5 rounded-full" style={{ background: color }} />{pct}%
    </motion.span>
  );
}
