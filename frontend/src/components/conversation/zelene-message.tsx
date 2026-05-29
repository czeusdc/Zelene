/**
 * @fileoverview Zelene insight message card — displays an AI-generated
 * insight with title, body, optional reasoning, and contextual action buttons
 * (monitor, generate brief, dismiss, etc.). Body text uses typing reveal
 * to create a sense of presence.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";
import { Insight } from "@/lib/types";
import { TypingText } from "@/components/ui/typing-text";

const actionLabels: Record<string, string> = {
  monitor: "Monitor", generate_brief: "Generate Brief", dismiss: "Dismiss",
  export_salesforce: "Export to Salesforce", push_slack: "Push to Slack", enrich_crm: "Enrich CRM",
  escalate_alert: "Escalate Alert", push_siem: "Push to SIEM",
};

/**
 * ZeleneMessage — renders an insight card with the Zelene brand header,
 * title, body text with typing reveal, optional reasoning, and contextual
 * action buttons.
 */
export function ZeleneMessage({ insight, onAction }: { insight: Insight; onAction: (action: string) => void }) {
  return (
    <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="mb-4">
      <div className="rounded-xl p-4" style={{ background: "hsl(var(--surface-overlay))", border: "1px solid hsl(var(--text-muted) / 0.2)" }}>
        <div className="flex items-center gap-2 mb-2">
          <motion.div
            className="h-3 w-3 rounded-full"
            style={{ background: "hsl(var(--accent-primary))" }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          />
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "hsl(var(--accent-primary))" }}>Zelene</span>
        </div>
        <p className="text-sm leading-relaxed mb-1">{insight.title}</p>
        <p className="text-xs leading-relaxed mb-3" style={{ color: "hsl(var(--text-secondary))" }}>
          <TypingText text={insight.body} messageId={insight.id} speed={25} />
        </p>
        {insight.reasoning && <p className="text-xs italic mb-3" style={{ color: "hsl(var(--text-muted))" }}>— {insight.reasoning}</p>}
        <div className="flex flex-wrap gap-2">
          {(insight.actions || ["monitor", "dismiss"]).slice(0, 4).map((action) => (
            <button key={action} onClick={() => onAction(action)}
              className="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors hover:opacity-80"
              style={{ background: "hsl(var(--surface-elevated))", color: "hsl(var(--text-secondary))", border: "1px solid hsl(var(--text-muted) / 0.15)" }}>
              {actionLabels[action] || action}
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
