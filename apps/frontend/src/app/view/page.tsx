"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ViewHeader } from "@/components/ui/view-header";
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
  const setDeploymentId = useViewStore((s) => s.setDeploymentId);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [deploying, setDeploying] = useState(true);

  useIntelligenceStream();

  useEffect(() => {
    if (!companyId) return;
    setCompanyId(companyId);
    api.deployIntelligence(companyId).then((res) => {
      setDeploymentId(res.deployment_id);
      setDeploying(false);
    }).catch(() => setDeploying(false));
  }, [companyId]);

  if (deploying) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm animate-pulse-soft" style={{ color: "hsl(var(--text-secondary))" }}>Deploying intelligence...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <ViewHeader onSettingsClick={() => setSettingsOpen(true)} />
      <div className="flex-1 grid grid-cols-3 divide-x" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
        <SignalFeed />
        <IntelligenceMap />
        <ZeleneChat />
      </div>
      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

export default function ViewPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center"><p className="text-sm" style={{ color: "hsl(var(--text-secondary))" }}>Loading...</p></div>}>
      <ViewContent />
    </Suspense>
  );
}
