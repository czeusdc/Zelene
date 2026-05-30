/**
 * @fileoverview Zelene chat panel — single evolving presence interface.
 * Shows ONE active Zelene thought at a time via InsightPresence, with
 * previous insights collapsed below. User chat messages appear beneath
 * the insight area. This replaces the old stacked-cards layout.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, FormEvent, useEffect } from "react";
import { useViewStore } from "@/stores/view-store";
import { TypingIndicator } from "@/components/conversation/typing-indicator";
import { InsightPresence } from "@/components/intelligence/insight-card";
import { api } from "@/lib/api";
import { motion } from "framer-motion";

/**
 * ZeleneChat — renders the single evolving presence right panel.
 * InsightPresence handles Zelene's strategic thoughts (active + collapsed).
 * Below it, user messages and the input form provide conversational follow-up.
 */
export function ZeleneChat() {
  const messages = useViewStore((s) => s.messages);
  const isThinking = useViewStore((s) => s.isThinking);
  const addMessage = useViewStore((s) => s.addMessage);
  const setIsThinking = useViewStore((s) => s.setIsThinking);
  const setActiveInsight = useViewStore((s) => s.setActiveInsight);
  const companyId = useViewStore((s) => s.companyId);
  const insights = useViewStore((s) => s.insights);
  const [input, setInput] = useState("");

  // Auto-select latest insight as active when new insight arrives
  useEffect(() => {
    if (insights.length > 0) {
      const latest = insights[insights.length - 1];
      setActiveInsight(latest.id!);
    }
  }, [insights.length, insights, setActiveInsight]);

  // User chat messages only
  const userMessages = messages.filter((m) => m.role === "user");

  const handleAsk = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || !companyId) return;
    setInput("");
    addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    });
    setIsThinking(true);
    try {
      const res = await api.askZelene(companyId, text);
      addMessage({
        id: crypto.randomUUID(),
        role: "zelene",
        content: res.reply,
        created_at: new Date().toISOString(),
      });
    } catch {
      addMessage({
        id: crypto.randomUUID(),
        role: "zelene",
        content: "I'm having trouble accessing that information right now.",
        created_at: new Date().toISOString(),
      });
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-4 pt-4 pb-2">
        <span
          className="text-xs uppercase"
          style={{
            color: "hsl(var(--accent-primary))",
            opacity: 0.6,
            letterSpacing: "0.2em",
          }}
        >
          Zelene
        </span>
      </div>

      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto px-4">
        {/* Zelene's evolving presence — one active thought at a time */}
        <InsightPresence insights={insights} />

        {/* User chat messages — below Zelene's thoughts */}
        {userMessages.length > 0 && (
          <div
            className="pt-3 mt-3"
            style={{ borderTop: "1px solid hsl(var(--text-muted) / 0.06)" }}
          >
            {userMessages.map((msg) => (
              <div key={msg.id} className="flex justify-end mb-3">
                <div
                  className="rounded-xl px-4 py-2.5 max-w-[80%] text-sm"
                  style={{
                    background: "hsl(var(--accent-primary) / 0.12)",
                    color: "hsl(var(--text-primary))",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
          </div>
        )}

        {isThinking && <TypingIndicator />}
      </div>

      {/* Input form */}
      <form
        onSubmit={handleAsk}
        className="p-3 border-t"
        style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}
      >
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Zelene about a competitor, signal, or risk..."
            autoComplete="off"
            className="flex-1 rounded-lg px-3 py-2 text-xs outline-none"
            style={{
              background: "hsl(var(--surface-overlay))",
              color: "hsl(var(--text-primary))",
              border: "1px solid hsl(var(--text-muted) / 0.15)",
            }}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={!input.trim() || isThinking}
            className="rounded-lg px-4 py-2 text-xs font-medium"
            style={{
              background: "hsl(var(--accent-primary))",
              color: "white",
              opacity: !input.trim() ? 0.4 : 1,
            }}
          >
            Ask
          </motion.button>
        </div>
      </form>
    </div>
  );
}
