/**
 * @fileoverview Scrollable chat area for the onboarding flow.
 * Renders Zelene prompts and user replies with fade-in animation,
 * typing text reveal for Zelene messages, and auto-scrolls to the
 * latest message.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TypingText } from "@/components/ui/typing-text";

interface Message { id: string; role: "zelene" | "user"; content: string; }

/**
 * ConversationArea — lists onboarding messages with staggered
 * entry animations, typing reveal for Zelene messages, and a
 * "thinking" indicator when Zelene is processing.
 */
const THINKING_PHRASES = [
  "Zelene is thinking",
  "Zelene is analyzing",
  "Zelene is observing",
  "Zelene is reflecting",
  "Zelene is watching",
  "Zelene is considering",
];

export function ConversationArea({ messages, isThinking }: { messages: Message[]; isThinking: boolean }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [phrase, setPhrase] = useState(THINKING_PHRASES[0]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isThinking]);
  useEffect(() => {
    if (!isThinking) return;
    const interval = setInterval(() => {
      setPhrase((p) => {
        const current = THINKING_PHRASES.indexOf(p);
        return THINKING_PHRASES[(current + 1) % THINKING_PHRASES.length];
      });
    }, 2500);
    return () => clearInterval(interval);
  }, [isThinking]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8" style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}>
      <AnimatePresence>
        {messages.map((msg, i) => (
          <motion.div key={msg.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * (messages.length - 1 - i), duration: 0.4 }} className="mb-6">
            {msg.role === "zelene" ? (
              <p className="text-sm leading-relaxed" style={{ color: "hsl(var(--text-primary))", whiteSpace: "pre-line" }}>
                <TypingText text={msg.content} messageId={msg.id} speed={20} />
              </p>
            ) : (
              <div className="flex justify-end">
                <div className="max-w-[80%] rounded-xl px-4 py-2.5 text-sm"
                  style={{ background: "hsl(var(--surface-overlay))" }}>{msg.content}</div>
              </div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
      {isThinking && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6">
          <p className="text-sm animate-pulse-soft" style={{ color: "hsl(var(--text-muted))" }}>{phrase}...</p>
        </motion.div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
