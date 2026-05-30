/**
 * @fileoverview Strategic-intelligence View — main dashboard with a
 * three-panel layout: signal feed (280px), intelligence map (flex),
 * and Zelene chat (320px). Initiates intelligence deployment and
 * connects the SSE stream on mount.
 *
 * Features a cinematic reveal transition on mount: header fades in,
 * center panel emerges with ambient glow, side panels slide in from
 * their respective edges.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ViewHeader } from "@/components/ui/view-header";
import { StatusBar } from "@/components/ui/status-bar";
import { SignalFeed } from "@/components/panels/signal-feed";
import { IntelligenceMap } from "@/components/panels/intelligence-map";
import { ZeleneChat } from "@/components/panels/zelene-chat";
import { SettingsDrawer } from "@/components/settings/settings-drawer";
import { useViewStore } from "@/stores/view-store";
import { useIntelligenceStream } from "@/hooks/useIntelligenceStream";
import { api } from "@/lib/api";

function ViewContent() {
  const searchParams = useSearchParams();
  const companyId = searchParams.get("company_id");
  const setCompanyId = useViewStore((s) => s.setCompanyId);
  const deploymentId = useViewStore((s) => s.deploymentId);
  const setDeploymentId = useViewStore((s) => s.setDeploymentId);
  const connectionStatus = useViewStore((s) => s.connectionStatus);
  const setConnectionStatus = useViewStore((s) => s.setConnectionStatus);
  const focusState = useViewStore((s) => s.focusState);
  const silence = useViewStore((s) => s.silence);
  const [settingsOpen, setSettingsOpen] = useState(false);
  // Derived: deploying until deployment ID arrives; error short-circuits
  const deploying = connectionStatus !== "error" && !deploymentId;

  const focusStyles = (panel: "signal" | "graph" | "chat") => {
    if (focusState === "balanced") return { opacity: 1, filter: "brightness(1)" };
    return focusState === panel
      ? { opacity: 1, filter: "brightness(1)" }
      : { opacity: 0.7, filter: "brightness(0.85)" };
  };

  useIntelligenceStream();

  useEffect(() => {
    if (!companyId) {
      setConnectionStatus("error");
      return;
    }
    setCompanyId(companyId);
    api.deployIntelligence(companyId)
      .then((res) => {
        setDeploymentId(res.deployment_id);
      })
      .catch(() => {
        setConnectionStatus("error");
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Zustand setters are stable
  }, [companyId]);

  // Missing company ID is a dead-end — show an error instead of empty panels
  if (!companyId) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "hsl(var(--surface-base))" }}>
        <p
          className="text-sm"
          style={{ color: "hsl(var(--signal-critical))" }}
        >
          Missing company ID. Please start from onboarding.
        </p>
      </div>
    );
  }

  if (deploying) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "hsl(var(--surface-base))" }}>
        <p
          className="text-sm animate-pulse-soft"
          style={{ color: "hsl(var(--text-secondary))" }}
        >
          Deploying intelligence...
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col h-screen overflow-hidden">
      {/* Ambient background motion behind panels */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(ellipse at 20% 30%, hsla(228, 56%, 52%, 0.025) 0%, transparent 50%), radial-gradient(ellipse at 80% 70%, hsla(180, 45%, 40%, 0.02) 0%, transparent 50%)",
          backgroundSize: "200% 200%",
          animation: "orbit-bg 30s ease-in-out infinite",
        }}
      />

      {/* Silence overlay — dims the UI during the synthesis beat */}
      {silence && (
        <motion.div
          className="pointer-events-none absolute inset-0 z-20 silence-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1 }}
        />
      )}

      {/* Header — fades in at T+400ms */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={deploymentId ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.2, delay: 0.3, ease: "easeOut" }}
      >
        <ViewHeader onSettingsClick={() => setSettingsOpen(true)} />
      </motion.div>

      <div className="relative z-10 flex flex-1 overflow-hidden">
        {/* Signal Feed — slides in from left at T+900ms */}
        <motion.div
          className="w-[280px] flex flex-col overflow-hidden"
          initial={{ opacity: 0, x: -40 }}
          animate={deploymentId ? { x: 0, ...focusStyles("signal") } : { opacity: 0, x: -40 }}
          transition={{ duration: 0.4, delay: 0.7, ease: "easeOut" }}
          style={{
            background: "hsl(var(--surface-base))",
            boxShadow: "4px 0 12px rgba(0,0,0,0.3)",
          }}
        >
          <SignalFeed />
        </motion.div>

        {/* Intelligence Map — fades in with ambient glow at T+600ms */}
        <motion.div
          className="flex-1 flex flex-col overflow-hidden"
          initial={{ opacity: 0 }}
          animate={!!deploymentId ? focusStyles("graph") : { opacity: 0 }}
          transition={{ duration: 0.5, delay: 0.5, ease: "easeOut" }}
          style={{
            background: "hsl(var(--surface-elevated))",
            position: "relative",
          }}
        >
          {/* Ambient glow behind the map — visible before nodes appear */}
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(ellipse at 50% 50%, hsla(228, 56%, 52%, 0.04) 0%, transparent 60%)",
            }}
          />
          <div className="relative z-10 h-full">
            <IntelligenceMap />
          </div>
        </motion.div>

        {/* Zelene Chat — slides in from right at T+1000ms */}
        <motion.div
          className="w-[320px] flex flex-col overflow-hidden"
          initial={{ opacity: 0, x: 40 }}
          animate={!!deploymentId ? { x: 0, ...focusStyles("chat") } : { opacity: 0, x: 40 }}
          transition={{ duration: 0.4, delay: 0.8, ease: "easeOut" }}
          style={{
            background: "hsl(var(--surface-overlay))",
            boxShadow: "-4px 0 12px rgba(0,0,0,0.3)",
          }}
        >
          <ZeleneChat />
        </motion.div>
      </div>

      {/* Status Bar — fades in at T+1400ms */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={!!deploymentId ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.2, delay: 1.1, ease: "easeOut" }}
      >
        <StatusBar />
      </motion.div>

      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

export default function ViewPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <p className="text-sm" style={{ color: "hsl(var(--text-secondary))" }}>
            Loading...
          </p>
        </div>
      }
    >
      <ViewContent />
    </Suspense>
  );
}
