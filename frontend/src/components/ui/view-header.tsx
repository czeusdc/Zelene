/**
 * @fileoverview Top bar of the strategic-intelligence View.
 * Shows the Zelene logo, connection-status indicator, current phase label,
 * and a settings gear button.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useViewStore } from "@/stores/view-store";

const phaseLabels: Record<string, string> = { deploying: "Deploying", gathering: "Gathering Intelligence", analyzing: "Analyzing", active: "Active" };

/**
 * ViewHeader — renders the View's top bar with phase badge, connection dot,
 * and a settings button that invokes the parent callback.
 */
export function ViewHeader({ onSettingsClick }: { onSettingsClick: () => void }) {
  const phase = useViewStore((s) => s.phase);
  const connectionStatus = useViewStore((s) => s.connectionStatus);
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-medium tracking-tight">Zelene</h1>
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full" style={{ background: connectionStatus === "connected" ? "hsl(var(--signal-positive))" : connectionStatus === "error" ? "hsl(var(--signal-critical))" : "hsl(var(--signal-warning))" }} />
          <span className="text-xs" style={{ color: "hsl(var(--text-muted))" }}>{phaseLabels[phase]}</span>
        </div>
      </div>
      <button onClick={onSettingsClick} className="rounded-lg p-2 text-xs hover:opacity-70" style={{ color: "hsl(var(--text-muted))" }}>{"\u2699"}</button>
    </header>
  );
}
