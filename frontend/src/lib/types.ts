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

export interface UserSettings { llm_model: string; has_api_key: boolean; }

export interface Signal {
  id: string;
  type: string;
  title: string;
  content: string;
  source: string;
  confidence: number;
  severity: "info" | "warning" | "critical";
  source_url?: string;
  source_ids?: string[];
  entities?: string[];
  extracted_at?: string;
}

export interface Source {
  id: string;
  title: string;
  url: string;
  snippet: string;
  query: string;
}

export interface Entity {
  id: string; name: string; type: "company" | "competitor" | "market" | "regulatory";
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

export interface BriefingSection { heading: string; content: string; }

export interface Briefing {
  title: string;
  generated_at: string;
  sections: BriefingSection[];
  signal_count: number;
  entity_count: number;
  relationship_count: number;
  insight_count: number;
}

export interface MemoryStatus {
  stored: boolean;
  type: "cognee" | "session";
  entity_count: number;
  relationship_count: number;
  signal_count: number;
  company: string;
}
