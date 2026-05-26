"use client";
import { useState, useCallback, useEffect, useRef, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { OnboardingLayout } from "@/components/onboarding/onboarding-layout";
import { ConversationArea } from "@/components/onboarding/conversation-area";
import { ContextReveal } from "@/components/onboarding/context-reveal";
import { api } from "@/lib/api";

interface Message { id: string; role: "zelene" | "user"; content: string; }
let msgCounter = 0;

export default function OnboardingPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [stage, setStage] = useState("introduction");
  const [context, setContext] = useState<Record<string, unknown>>({});
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [showContext, setShowContext] = useState(false);

  const addMessage = useCallback((role: "zelene" | "user", content: string) => {
    setMessages(prev => [...prev, { id: String(++msgCounter), role, content }]);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (text.trim()) addMessage("user", text.trim());
    setIsThinking(true);
    try {
      const res = await api.onboard(text.trim() || "", sessionId);
      if (!sessionId) setSessionId(res.session_id);
      setContext(res.context_so_far);
      addMessage("zelene", res.reply);

      const ctx = res.context_so_far;
      const hasCompetitors = ctx.competitors && (ctx.competitors as string[]).length > 0;
      const hasGoals = ctx.goals && (ctx.goals as string[]).length > 0;
      const hasName = !!ctx.company_name;

      if (hasCompetitors && hasGoals && hasName) {
        setStage("confirm");
        setTimeout(() => setShowContext(true), 800);
      } else if (hasName) {
        setStage(ctx.competitors ? "competitors" : "company");
      }
    } catch {
      addMessage("zelene", "I apologize — I'm having trouble. Could you try again?");
    } finally {
      setIsThinking(false);
    }
  }, [sessionId, addMessage]);

  const handleConfirm = async () => {
    if (!sessionId) return;
    try {
      await api.saveCompany(sessionId);
      router.push(`/view?company_id=${sessionId}`);
    } catch { /* handle */ }
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const input = (e.currentTarget.elements.namedItem("message") as HTMLInputElement);
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    sendMessage(text);
  };

  const startedRef = useRef(false);
  useEffect(() => {
    if (!startedRef.current) {
      startedRef.current = true;
      sendMessage("");
    }
  }, [sendMessage]);

  return (
    <OnboardingLayout stage={stage} isThinking={isThinking}>
      <ConversationArea messages={messages} isThinking={isThinking} />
      {showContext && (
        <ContextReveal context={context} onConfirm={handleConfirm}
          onAdjust={() => { setShowContext(false); addMessage("zelene", "Of course. What would you like to adjust?"); }} />
      )}
      {!showContext && (
        <form onSubmit={handleSubmit} className="px-6 pb-8"
          style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}>
          <div className="flex gap-3">
            <input name="message" type="text" autoFocus placeholder="Type your response..."
              disabled={isThinking}
              className="flex-1 rounded-xl px-4 py-3 text-sm outline-none"
              style={{ background: "hsl(var(--surface-overlay))", color: "hsl(var(--text-primary))",
                border: "1px solid hsl(var(--text-muted) / 0.2)" }} />
            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              type="submit" disabled={isThinking}
              className="rounded-xl px-5 py-3 text-sm font-medium"
              style={{ background: "hsl(var(--accent-primary))", color: "white", opacity: isThinking ? 0.5 : 1 }}>
              Send
            </motion.button>
          </div>
        </form>
      )}
    </OnboardingLayout>
  );
}
