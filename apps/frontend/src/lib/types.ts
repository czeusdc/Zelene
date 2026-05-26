/**
 * @fileoverview Shared TypeScript interfaces for the Zelene platform:
 * CompanyProfile, Signal, Entity, RelationshipEdge, Insight, ChatMessage,
 * and UserSettings.
 * Part of the Zelene strategic intelligence platform.
 */

export interface CompanyProfile {
  id: string; name: string; industry?: string; description?: string;
  competitors: string[]; market_focus: string[]; business_goals: string[]; operational_concerns: string[];
}

export interface UserSettings { gemini_api_key?: string; gemini_model: string; }

export interface Signal {
  id: string; deployment_id: string; type: string; title: string; content: string;
  source: string; source_url?: string; confidence: number;
  severity: "info" | "warning" | "critical"; entities: string[]; conflicts_with?: string[]; extracted_at: string;
}

export interface Entity {
  id: string; name: string; type: "competitor" | "vendor" | "market" | "regulatory" | "customer_segment";
  description?: string; activity_level: number; last_signal_at?: string;
}

export interface RelationshipEdge {
  id: string; entity_a: string; entity_b: string; relationship_type: string; strength: number; evidence: string[];
}

export interface Insight {
  id: string; type: "warning" | "opportunity" | "observation" | "recommendation";
  title: string; body: string; reasoning?: string; confidence: number; evidence_signals: string[]; actions: string[];
}

export interface ChatMessage { id: string; role: "zelene" | "user"; content: string; related_insight?: string; created_at: string; }
