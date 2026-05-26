/**
 * @fileoverview Signal feed panel — renders the live stream of intelligence
 * signals in a scrollable list, with a placeholder state while deploying.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useViewStore } from "@/stores/view-store";
import { SignalCard } from "@/components/intelligence/signal-card";

const statusMessages: Record<string, string> = {
  deploying: "Preparing intelligence deployment...",
  gathering: "Discovering signals across the web...",
  analyzing: "Analyzing extracted intelligence...",
  active: "Intelligence environment active.",
};

/**
 * SignalFeed — reads signals from the view store and renders them
 * as SignalCards, or shows a phase-dependent loading state.
 */
export function SignalFeed() {
  const signals = useViewStore((s) => s.signals);
  const phase = useViewStore((s) => s.phase);

  if (signals.length === 0 && phase !== "active") {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <div className="animate-pulse-soft mb-4">
          <div className="h-2 w-24 rounded mx-auto mb-3" style={{ background: "hsl(var(--accent-primary) / 0.3)" }} />
        </div>
        <p className="text-sm" style={{ color: "hsl(var(--text-secondary))" }}>{statusMessages[phase]}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-4 overflow-y-auto h-full">
      {signals.map((signal, i) => (<SignalCard key={signal.id || i} signal={signal} />))}
    </div>
  );
}
