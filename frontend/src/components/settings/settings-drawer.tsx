/**
 * @fileoverview Settings slide-out drawer — theme toggle and model selector.
 * API keys are NEVER entered or stored here; they live in .env.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useViewStore } from "@/stores/view-store";
import { useTheme } from "@/hooks/useTheme";
import { api } from "@/lib/api";

const MODELS = [
  { value: "gemini-3.1-pro", label: "Gemini 3.1 Pro" },
  { value: "gemini-3.5-flash", label: "Gemini 3.5 Flash" },
  { value: "gemini-3.1-flash-lite", label: "Gemini 3.1 Flash-Lite" },
];

export function SettingsDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const companyId = useViewStore((s) => s.companyId);
  const { theme, toggleTheme } = useTheme();
  const [model, setModel] = useState("gemini-3.1-pro");
  const [hasApiKey, setHasApiKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(false);

  useEffect(() => {
    if (open && companyId) {
      api.getSettings(companyId).then((s) => {
        if (s.gemini_model) setModel(s.gemini_model);
        setHasApiKey(s.has_api_key);
      }).catch(() => {});
    }
  }, [open, companyId]);

  const handleSave = async () => {
    if (!companyId) return;
    setSaving(true);
    setSaveError(false);
    try {
      await api.saveSettings(companyId, { gemini_model: model });
      onClose();
    } catch {
      setSaveError(true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (<>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={onClose} className="fixed inset-0 z-40" style={{ background: "rgba(0,0,0,0.4)" }} />
        <motion.div
          initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="fixed right-0 top-0 bottom-0 z-50 w-80 p-6 overflow-y-auto"
          style={{ background: "hsl(var(--surface-base))", borderLeft: "1px solid hsl(var(--text-muted) / 0.1)" }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium">Settings</h3>
            <button onClick={onClose} className="text-lg" style={{ color: "hsl(var(--text-muted))" }}>
              {"\u2715"}
            </button>
          </div>

          <div className="mb-6">
            <h4 className="text-xs uppercase tracking-widest mb-3" style={{ color: "hsl(var(--text-muted))" }}>
              Theme
            </h4>
            <div className="flex gap-2">
              {["dark", "light"].map((t) => (
                <button key={t} onClick={() => theme !== t && toggleTheme()}
                  className="flex-1 rounded-lg py-2 text-xs capitalize"
                  style={{
                    background: theme === t ? "hsl(var(--accent-primary) / 0.15)" : "hsl(var(--surface-overlay))",
                    color: theme === t ? "hsl(var(--accent-primary))" : "hsl(var(--text-secondary))",
                  }}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-xs uppercase tracking-widest mb-3" style={{ color: "hsl(var(--text-muted))" }}>
              Intelligence
            </h4>
            <div className="rounded-lg p-3 mb-3 text-xs" style={{ background: "hsl(var(--surface-overlay))" }}>
              <span style={{ color: "hsl(var(--text-muted))" }}>Gemini API: </span>
              <span style={{ color: hasApiKey ? "hsl(var(--signal-positive))" : "hsl(var(--text-muted))" }}>
                {hasApiKey ? "Configured" : "Not configured"}
              </span>
              {!hasApiKey && (
                <p className="mt-2" style={{ color: "hsl(var(--text-muted))" }}>
                  Set GEMINI_API_KEY in your .env file.
                </p>
              )}
            </div>

            <label className="text-xs mb-1 block" style={{ color: "hsl(var(--text-secondary))" }}>
              Model
            </label>
            <select value={model} onChange={(e) => setModel(e.target.value)}
              className="w-full rounded-lg px-3 py-2 text-xs outline-none mb-4"
              style={{
                background: "hsl(var(--surface-overlay))",
                color: "hsl(var(--text-primary))",
                border: "1px solid hsl(var(--text-muted) / 0.15)",
              }}>
              {MODELS.map((m) => (<option key={m.value} value={m.value}>{m.label}</option>))}
            </select>
          </div>

          <button onClick={handleSave} disabled={saving}
            className="w-full rounded-lg py-2.5 text-xs font-medium"
            style={{ background: "hsl(var(--accent-primary))", color: "white", opacity: saving ? 0.5 : 1 }}>
            {saving ? "Saving..." : "Save"}
          </button>
          {saveError && (
            <p className="text-xs text-red-400 mt-2 text-center">
              Failed to save settings. Please try again.
            </p>
          )}
        </motion.div>
      </>)}
    </AnimatePresence>
  );
}
