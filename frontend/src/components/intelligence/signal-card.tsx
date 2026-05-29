/**
 * @fileoverview Signal card component — displays an individual intelligence
 * signal with severity colour coding, type icon, confidence badge, source
 * attribution, and expandable evidence provenance linking back to web sources.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ConfidenceBadge } from "@/components/ui/confidence-badge";
import { RelativeTime } from "@/components/ui/relative-time";
import { Signal, Source } from "@/lib/types";

const severityColors = { info: "hsl(var(--signal-info))", warning: "hsl(var(--signal-warning))", critical: "hsl(var(--signal-critical))" };
const typeIcons: Record<string, string> = { price_change: "\u{1F4CA}", sentiment_shift: "\u{1F4AC}", hiring_surge: "\u{1F465}", regulatory: "\u2696\uFE0F", new_entrant: "\u{1F50D}" };

function resolveSourceTitles(sourceIds: string[] | undefined, sources: Source[]): string[] {
  if (!sourceIds || sourceIds.length === 0) return [];
  const set = new Set(sourceIds);
  return sources.filter((s) => set.has(s.id)).map((s) => s.title);
}

/**
 * SignalCard — renders a signal with coloured left border, type icon,
 * confidence badge, content body, and expandable evidence provenance.
 */
export function SignalCard({ signal, sources }: { signal: Signal; sources?: Source[] }) {
  const [expanded, setExpanded] = useState(false);
  const color = severityColors[signal.severity] || severityColors.info;
  const sourceTitles = resolveSourceTitles(signal.source_ids, sources || []);
  const evidenceCount = sourceTitles.length;

  return (
    <motion.div
      initial={{ opacity: 0, x: -16, boxShadow: `0 0 12px ${color}40` }}
      animate={{ opacity: 1, x: 0, boxShadow: `0 0 0px ${color}00` }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="rounded-xl p-4"
      style={{ background: "hsl(var(--surface-elevated))", borderLeft: `3px solid ${color}` }}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm">{typeIcons[signal.type] || "\u25CF"}</span>
          <h4 className="text-sm font-medium">
            {signal.type === "price_change" && `I'm seeing movement around ${signal.title}`}
            {signal.type === "sentiment_shift" && `Something interesting is emerging: ${signal.title}`}
            {signal.type === "hiring_surge" && `I noticed ${signal.title}`}
            {signal.type === "regulatory" && `This pattern deserves attention: ${signal.title}`}
            {signal.type === "new_entrant" && `I'm noticing something: ${signal.title}`}
            {!["price_change", "sentiment_shift", "hiring_surge", "regulatory", "new_entrant"].includes(signal.type) && signal.title}
          </h4>
        </div>
        <ConfidenceBadge value={signal.confidence} />
      </div>
      <p className="text-xs leading-relaxed mb-2" style={{ color: "hsl(var(--text-secondary))" }}>{signal.content}</p>
      <div className="flex items-center gap-2 text-xs" style={{ color: "hsl(var(--text-muted))" }}>
        <span>{signal.source}</span>
        {evidenceCount > 0 && (
          <>
            <span>&middot;</span>
            <button
              onClick={() => setExpanded(!expanded)}
              className="hover:opacity-80 transition-opacity"
              style={{ color: "hsl(var(--accent-primary))" }}
            >
              Evidence &middot; {evidenceCount} {evidenceCount === 1 ? "source" : "sources"}
            </button>
          </>
        )}
        <span>&middot;</span>
        {signal.extracted_at && <RelativeTime dateString={signal.extracted_at} />}
        {signal.confidence < 0.75 && <span style={{ color: "hsl(var(--signal-warning))" }}>&mdash; Early signal, I&rsquo;ll need more data to be sure</span>}
      </div>
      <AnimatePresence>
        {expanded && evidenceCount > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div
              className="mt-2 pt-2 space-y-1"
              style={{ borderTop: `1px solid hsl(var(--text-muted) / 0.15)` }}
            >
              {sourceTitles.map((title, i) => (
                <div key={i} className="flex items-start gap-1.5 text-xs" style={{ color: "hsl(var(--text-muted))" }}>
                  <span style={{ color: "hsl(var(--accent-primary))" }}>&#10003;</span>
                  <span>{title}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
