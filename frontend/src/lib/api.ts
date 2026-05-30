/**
 * @fileoverview Typed API client for the Zelene backend.
 * Wraps fetch with JSON helpers and exposes endpoint-level methods
 * for onboarding, intelligence deployment, signals, chat, and settings.
 * Part of the Zelene strategic intelligence platform.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),

  onboard: (message: string, sessionId?: string, simulation?: boolean) =>
    request<{ reply: string; session_id: string; context_so_far: Record<string, unknown> }>(
      "/api/company/onboard", { method: "POST", body: JSON.stringify({ message, session_id: sessionId, simulation: simulation ?? false }) }
    ),

  saveCompany: (companyId: string) =>
    request<{ status: string; company_id: string }>("/api/company/save", {
      method: "POST", body: JSON.stringify({ company_id: companyId }),
    }),

  getCompany: (id: string) => request<import("./types").CompanyProfile>(`/api/company/${id}`),

  deployIntelligence: (companyId: string) =>
    request<{ stream_url: string; deployment_id: string }>("/api/intelligence/deploy", {
      method: "POST", body: JSON.stringify({ company_id: companyId }),
    }),

  getSignals: (deploymentId: string) =>
    request<import("./types").Signal[]>(`/api/signals?deployment_id=${deploymentId}`),

  getRelationships: (deploymentId: string) =>
    request<{ entities: import("./types").Entity[]; relationships: import("./types").RelationshipEdge[] }>(
      `/api/relationships?deployment_id=${deploymentId}`
    ),

  askZelene: (companyId: string, message: string, entity?: string) =>
    request<{ reply: string }>("/api/conversation/ask", {
      method: "POST", body: JSON.stringify({ company_id: companyId, message, entity }),
    }),

  saveSettings: (companyId: string, settings: Partial<import("./types").UserSettings>) =>
    request<{ updated: boolean }>("/api/settings", {
      method: "POST", body: JSON.stringify({ company_id: companyId, ...settings }),
    }),

  getSettings: (companyId: string) =>
    request<import("./types").UserSettings>(`/api/settings?company_id=${companyId}`),

  intelligenceStreamUrl: (deploymentId: string) =>
    `${BASE_URL}/api/intelligence/stream?deployment_id=${deploymentId}`,

  generateBriefing: (companyId: string) =>
    request<import("./types").Briefing>("/api/briefing/generate", {
      method: "POST", body: JSON.stringify({ company_id: companyId }),
    }),
};
