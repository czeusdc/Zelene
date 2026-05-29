/**
 * @fileoverview Onboarding confirmation screen — displays a card grid of
 * extracted company context and lets the user confirm or go back to adjust.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

interface Props { context: Record<string, unknown>; onConfirm: () => void; onAdjust: () => void; error?: boolean; isConfirming?: boolean; }

function Card({ label, value }: { label: string; value: string | string[] }) {
  const display = Array.isArray(value) ? value.join(", ") : value;
  if (!display) return null;
  return (
    <motion.div initial={{ opacity: 0, y: 16, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="rounded-xl p-5" style={{ background: "hsl(var(--surface-overlay))" }}>
      <p className="text-xs uppercase tracking-widest" style={{ color: "hsl(var(--text-muted))" }}>{label}</p>
      <p className="mt-1 text-sm font-medium">{display}</p>
    </motion.div>
  );
}

/**
 * ContextReveal — shows extracted company profile fields as cards
 * with Confirm / Adjust action buttons.
 */
export function ContextReveal({ context, onConfirm, onAdjust, error, isConfirming }: Props) {
  const items = [
    { label: "Company", value: context.company_name as string },
    { label: "Industry", value: context.industry as string },
    { label: "Competitors", value: context.competitors as string[] },
    { label: "Market Focus", value: context.market_focus as string[] },
    { label: "Goals", value: context.goals as string[] },
  ].filter((i) => i.value && (Array.isArray(i.value) ? i.value.length > 0 : true));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="px-6 py-4" style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}>
      <p className="text-sm mb-4" style={{ color: "hsl(var(--text-secondary))" }}>What I understand so far:</p>
      <div className="grid grid-cols-2 gap-3 mb-6">
        {items.map((item) => (<Card key={item.label} label={item.label} value={item.value} />))}
      </div>
      {error && <p className="text-xs text-red-400 mb-4">Unable to save your profile. Please try again.</p>}
      <div className="flex gap-3">
        <motion.button whileHover={isConfirming ? {} : { scale: 1.02 }} whileTap={isConfirming ? {} : { scale: 0.98 }}
          onClick={onConfirm} disabled={isConfirming} className="rounded-lg px-6 py-2.5 text-sm font-medium"
          style={{ background: "hsl(var(--accent-primary))", color: "white", opacity: isConfirming ? 0.6 : 1 }}>
          {isConfirming ? "Saving..." : "Yes, continue"}
        </motion.button>
        <motion.button whileHover={isConfirming ? {} : { scale: 1.02 }} whileTap={isConfirming ? {} : { scale: 0.98 }}
          onClick={onAdjust} disabled={isConfirming} className="rounded-lg px-6 py-2.5 text-sm"
          style={{ background: "hsl(var(--surface-overlay))", color: "hsl(var(--text-secondary))", opacity: isConfirming ? 0.4 : 1 }}>
          Let me adjust
        </motion.button>
      </div>
    </motion.div>
  );
}
