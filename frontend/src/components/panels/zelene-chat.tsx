/**
 * @fileoverview Zelene chat panel — provides a conversational interface
 * for asking strategic questions. Messages are routed through the backend
 * and displayed as ZeleneMessage cards.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, FormEvent } from "react";
import { useViewStore } from "@/stores/view-store";
import { ZeleneMessage } from "@/components/conversation/zelene-message";
import { TypingIndicator } from "@/components/conversation/typing-indicator";
import { api } from "@/lib/api";
import { motion } from "framer-motion";

/**
 * ZeleneChat — renders chat history from the store, an input form with
 * a submit handler that calls the askZelene API, and a typing indicator
 * while waiting for a response.
 */
export function ZeleneChat() {
  const messages = useViewStore((s) => s.messages);
  const isThinking = useViewStore((s) => s.isThinking);
  const addMessage = useViewStore((s) => s.addMessage);
  const setIsThinking = useViewStore((s) => s.setIsThinking);
  const companyId = useViewStore((s) => s.companyId);
  const [input, setInput] = useState("");

  const handleAsk = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || !companyId) return;
    setInput("");
    addMessage({ id: crypto.randomUUID(), role: "user", content: text, created_at: new Date().toISOString() });
    setIsThinking(true);
    try {
      const res = await api.askZelene(companyId, text);
      addMessage({ id: crypto.randomUUID(), role: "zelene", content: res.reply, created_at: new Date().toISOString() });
    } catch {
      addMessage({ id: crypto.randomUUID(), role: "zelene", content: "I'm having trouble accessing that information right now.", created_at: new Date().toISOString() });
    } finally { setIsThinking(false); }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-center" style={{ color: "hsl(var(--text-muted))" }}>Zelene will surface strategic insights here as intelligence is gathered.</p>
          </div>
        )}
        {messages.map((msg) => (
          <ZeleneMessage key={msg.id} insight={{ id: msg.id, type: "observation", title: msg.content.split("\n\n")[0] || msg.content.slice(0, 100), body: msg.content, confidence: 0.8, evidence_signals: [], actions: ["monitor", "generate_brief", "dismiss"] }} onAction={(a) => console.log("Action:", a)} />
        ))}
        {isThinking && <TypingIndicator />}
      </div>
      <form onSubmit={handleAsk} className="p-3 border-t" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
        <div className="flex gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask Zelene about a competitor, signal, or risk..."
            className="flex-1 rounded-lg px-3 py-2 text-xs outline-none" style={{ background: "hsl(var(--surface-overlay))", color: "hsl(var(--text-primary))", border: "1px solid hsl(var(--text-muted) / 0.15)" }} />
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit" disabled={!input.trim() || isThinking}
            className="rounded-lg px-4 py-2 text-xs font-medium" style={{ background: "hsl(var(--accent-primary))", color: "white", opacity: !input.trim() ? 0.4 : 1 }}>Ask</motion.button>
        </div>
      </form>
    </div>
  );
}
