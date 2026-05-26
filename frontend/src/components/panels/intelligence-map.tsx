/**
 * @fileoverview Intelligence map panel — renders an interactive SVG
 * force-layout graph of entities and their relationships. Highlights
 * nodes that are referenced in recent signals.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useMemo } from "react";
import { useViewStore } from "@/stores/view-store";
import { EntityNode } from "@/components/intelligence/entity-node";
import { RelationshipEdge } from "@/components/intelligence/relationship-edge";

/**
 * IntelligenceMap — computes static positions for up to 5 entities,
 * draws inter-entity relationship edges, and highlights nodes that
 * appear in the most recent signals.
 */
export function IntelligenceMap() {
  const entities = useViewStore((s) => s.entities);
  const relationships = useViewStore((s) => s.relationships);
  const signals = useViewStore((s) => s.signals);

  const positions: Record<number, { x: number; y: number }> = { 0: { x: 350, y: 250 }, 1: { x: 150, y: 120 }, 2: { x: 550, y: 380 }, 3: { x: 600, y: 120 }, 4: { x: 120, y: 380 } };

  const layoutNodes = useMemo(() =>
    entities.slice(0, 5).map((e, i) => ({ id: e.id, x: positions[i]?.x ?? 350, y: positions[i]?.y ?? 250, name: e.name, type: e.type })),
    [entities]
  );

  const nodeMap = useMemo(() => Object.fromEntries(layoutNodes.map((n) => [n.id, n])), [layoutNodes]);
  const activeNodes = useMemo(() => new Set(signals.slice(-5).flatMap((s) => s.entities || []).filter((e) => layoutNodes.some((n) => n.name === e)).map((e) => layoutNodes.find((n) => n.name === e)?.id).filter(Boolean)), [signals, layoutNodes]);

  if (layoutNodes.length === 0) {
    return <div className="flex items-center justify-center h-full"><p className="text-sm" style={{ color: "hsl(var(--text-muted))" }}>Intelligence map forming...</p></div>;
  }

  return (
    <div className="w-full h-full" style={{ minHeight: "400px" }}>
      <svg viewBox="0 0 700 500" className="w-full h-full">
        {relationships.slice(0, 6).map((rel) => {
          const a = nodeMap[rel.entity_a], b = nodeMap[rel.entity_b];
          if (!a || !b) return null;
          return <RelationshipEdge key={rel.id} from={{ x: a.x, y: a.y }} to={{ x: b.x, y: b.y }} type={rel.relationship_type} strength={rel.strength} />;
        })}
        {layoutNodes.map((node) => (
          <EntityNode key={node.id} x={node.x} y={node.y} name={node.name} type={node.type} active={activeNodes.has(node.id)} onClick={() => {}} />
        ))}
      </svg>
    </div>
  );
}
