/**
 * @fileoverview Signal card component — displays an individual intelligence
 * signal with severity colour coding, type icon, confidence badge, and source.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";
import { ConfidenceBadge } from "@/components/ui/confidence-badge";
import { Signal } from "@/lib/types";

const severityColors = { info: "hsl(var(--signal-info))", warning: "hsl(var(--signal-warning))", critical: "hsl(var(--signal-critical))" };
const typeIcons: Record<string, string> = { price_change: "\u{1F4CA}", sentiment_shift: "\u{1F4AC}", hiring_surge: "\u{1F465}", regulatory: "\u2696\uFE0F", vendor_change: "\u{1F3ED}" };

/**
 * SignalCard — renders a signal with a coloured left border, type icon,
 * confidence badge, content body, and source attribution.
 */
export function SignalCard({ signal }: { signal: Signal }) {
  const color = severityColors[signal.severity] || severityColors.info;
  return (
    <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="rounded-xl p-4" style={{ background: "hsl(var(--surface-elevated))", borderLeft: `3px solid ${color}` }}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm">{typeIcons[signal.type] || "\u25CF"}</span>
          <h4 className="text-sm font-medium">{signal.title}</h4>
        </div>
        <ConfidenceBadge value={signal.confidence} />
      </div>
      <p className="text-xs leading-relaxed mb-2" style={{ color: "hsl(var(--text-secondary))" }}>{signal.content}</p>
      <div className="flex items-center gap-2 text-xs" style={{ color: "hsl(var(--text-muted))" }}>
        <span>{signal.source}</span>
        {signal.confidence < 0.75 && <span style={{ color: "hsl(var(--signal-warning))" }}>— Low confidence</span>}
      </div>
    </motion.div>
  );
}
