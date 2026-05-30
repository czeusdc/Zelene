/**
 * @fileoverview Onboarding page — interactive conversational flow that
 * gathers company context (name, industry, competitors, goals) from the
 * user, then saves the profile and routes to the strategic-intelligence View.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useCallback, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { OnboardingLayout } from "@/components/onboarding/onboarding-layout";
import { ConversationArea } from "@/components/onboarding/conversation-area";
import { ContextReveal } from "@/components/onboarding/context-reveal";
import { api } from "@/lib/api";

/** Stage-specific pre-filled text for simulated mode. */
const SIMULATION_PREFILLS: Record<string, string> = {
  introduction: "Acme Corp — enterprise software for logistics",
  company: "We focus on real-time data integration and speed",
  competitors: "Salesforce, HubSpot, Monday.com",
  goals: "Market expansion, product launch, competitive positioning",
  confirm: "",
};

interface Message { id: string; role: "zelene" | "user"; content: string; }
let msgCounter = 0;

/** Zelene's full greeting — shown immediately without an API call. */
const GREETING =
  "Welcome. I'm Zelene, your strategic intelligence presence.\n\n" +
  "Think of me as an analyst who continuously observes your market on your behalf. Competitors, risks, opportunities, sentiment shifts.\n\n" +
  "To begin, I'd like to understand your business. Tell me about your company. What do you do, and in what industry?";

export default function OnboardingPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>(() => [
    { id: String(++msgCounter), role: "zelene" as const, content: GREETING },
  ]);
  const [stage, setStage] = useState("introduction");
  const [context, setContext] = useState<Record<string, unknown>>({});
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const [confirmError, setConfirmError] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isSimulation, setIsSimulation] = useState(false);
  const [inputValue, setInputValue] = useState("");

  // Read simulation flag from localStorage on mount.
  useEffect(() => {
    const sim = localStorage.getItem("zelene_simulation_mode");
    if (sim === "true") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setIsSimulation(true);
      setInputValue(SIMULATION_PREFILLS["introduction"]);
    }
  }, []);

  // Update pre-filled input when stage changes in simulation mode.
  useEffect(() => {
    if (isSimulation) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInputValue(SIMULATION_PREFILLS[stage] || "");
    }
  }, [stage, isSimulation]);

  const addMessage = useCallback((role: "zelene" | "user", content: string) => {
    setMessages((prev) => [...prev, { id: String(++msgCounter), role, content }]);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    addMessage("user", text);
    setIsThinking(true);
    try {
      const res = await api.onboard(text, sessionId ?? undefined, isSimulation);
      if (!sessionId) setSessionId(res.session_id);
      setContext(res.context_so_far);

      // Multiple replies separated by newlines → separate messages
      const replies = res.reply.split("\n\n").filter(Boolean);
      for (const r of replies) {
        addMessage("zelene", r);
      }

      // Stage is derived from data presence, not hard-coded transitions
      const ctx = res.context_so_far;
      const hasCompetitors = ctx.competitors && (ctx.competitors as string[]).length > 0;
      const hasGoals = ctx.goals && (ctx.goals as string[]).length > 0;
      const hasName = !!ctx.company_name;

      if (hasCompetitors && hasGoals && hasName) {
        setStage("confirm");
        setTimeout(() => setShowContext(true), 2500);
      } else if (hasCompetitors) {
        setStage("goals");
      } else if (hasName) {
        setStage("competitors");
      } else {
        setStage("company");
      }
    } catch {
      addMessage("zelene", "I apologize — I'm having trouble. Could you try again?");
    } finally {
      setIsThinking(false);
    }
  }, [sessionId, addMessage, isSimulation]);

  const handleConfirm = async () => {
    if (!sessionId || isConfirming) return;
    setIsConfirming(true);
    setConfirmError(false);
    try {
      const res = await api.saveCompany(sessionId);
      router.push(`/view?company_id=${res.company_id}`);
    } catch {
      setConfirmError(true);
      setIsConfirming(false);
    }
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const text = inputValue.trim();
    if (!text) return;
    setInputValue("");
    sendMessage(text);
  };

  return (
    <OnboardingLayout stage={stage} isThinking={isThinking}>
      <ConversationArea messages={messages} isThinking={isThinking} />
      {showContext && (
        <ContextReveal
          context={context}
          onConfirm={handleConfirm}
          onAdjust={() => {
            setShowContext(false);
            setConfirmError(false);
            addMessage("zelene", "Of course. What would you like to adjust?");
          }}
          error={confirmError}
          isConfirming={isConfirming}
        />
      )}
      {!showContext && (
        <form
          method="post"
          onSubmit={handleSubmit}
          className="px-6 pb-8"
          style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}
        >
          <div className="flex gap-3">
            <input
              name="message"
              type="text"
              autoFocus
              autoComplete="off"
              placeholder="Type your response..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isThinking}
              className="flex-1 rounded-xl px-4 py-3 text-sm outline-none"
              style={{
                background: "hsl(var(--surface-overlay))",
                color: "hsl(var(--text-primary))",
                border: "1px solid hsl(var(--text-muted) / 0.2)",
              }}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={isThinking}
              className="rounded-xl px-5 py-3 text-sm font-medium"
              style={{
                background: "hsl(var(--accent-primary))",
                color: "white",
                opacity: isThinking ? 0.5 : 1,
              }}
            >
              Send
            </motion.button>
          </div>
        </form>
      )}
    </OnboardingLayout>
  );
}
