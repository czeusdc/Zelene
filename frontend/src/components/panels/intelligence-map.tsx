/**
 * @fileoverview Intelligence map panel — renders an interactive SVG
 * graph of entities and their relationships. Features staggered node
 * entry, ambient drift, glow, and node emphasis choreography driven
 * by incoming signals.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useMemo, useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useViewStore } from "@/stores/view-store";
import { EntityNode } from "@/components/intelligence/entity-node";
import { RelationshipEdge } from "@/components/intelligence/relationship-edge";

/**
 * Hard-coded positions for up to 6 entities — the 6th slot accommodates
 * a potential_competitor entity surfaced from new_entrant signals.
 */
const positions: Record<number, { x: number; y: number }> = {
  0: { x: 350, y: 250 },
  1: { x: 150, y: 120 },
  2: { x: 550, y: 380 },
  3: { x: 600, y: 120 },
  4: { x: 120, y: 380 },
  5: { x: 350, y: 90 },
};

/** Framer Motion variants for staggered node entry. */
const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.2 },
  },
};

const nodeVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
};

/**
 * IntelligenceMap — computes static positions for up to 6 entities,
 * draws inter-entity relationship edges, highlights nodes that appear
 * in the most recent signals, and orchestrates entry/emphasis motion.
 * The 6th slot supports potential_competitor entities from new_entrant signals.
 */
export function IntelligenceMap() {
  const entities = useViewStore((s) => s.entities);
  const relationships = useViewStore((s) => s.relationships);
  const signals = useViewStore((s) => s.signals);

  const [emphasizedNodeIds, setEmphasizedNodeIds] = useState<Set<string>>(new Set());
  const [pulsingNodeIds, setPulsingNodeIds] = useState<Set<string>>(new Set());

  // Trigger node emphasis and pulse when a new signal references entities
  useEffect(() => {
    if (signals.length === 0) return;
    const latest = signals[signals.length - 1];
    if (!latest.entities || latest.entities.length === 0) return;

    const matchedIds = new Set<string>();
    latest.entities.forEach((entityName) => {
      const node = layoutNodes.find((n) => n.name === entityName);
      if (node) matchedIds.add(node.id);
    });

    if (matchedIds.size > 0) {
      setEmphasizedNodeIds(matchedIds);
      setPulsingNodeIds(matchedIds);
      const emphasisTimer = setTimeout(() => setEmphasizedNodeIds(new Set()), 1200);
      const pulseTimer = setTimeout(() => setPulsingNodeIds(new Set()), 3000);
      return () => {
        clearTimeout(emphasisTimer);
        clearTimeout(pulseTimer);
      };
    }
  }, [signals]);

  const layoutNodes = useMemo(
    () =>
      entities.slice(0, 6).map((e, i) => ({
        id: e.id,
        x: positions[i]?.x ?? 350,
        y: positions[i]?.y ?? 250,
        name: e.name,
        type: e.type,
      })),
    [entities]
  );

  const nodeMap = useMemo(
    () => Object.fromEntries(layoutNodes.map((n) => [n.id, n])),
    [layoutNodes]
  );

  const activeNodes = useMemo(() => {
    const recent = signals.slice(-5);
    const names = new Set(recent.flatMap((s) => s.entities || []));
    return new Set(
      Array.from(names)
        .map((name) => layoutNodes.find((n) => n.name === name)?.id)
        .filter(Boolean) as string[]
    );
  }, [signals, layoutNodes]);

  if (layoutNodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm" style={{ color: "hsl(var(--text-muted))" }}>
          Intelligence map forming...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full h-full overflow-hidden">
      <div className="px-4 pt-4 pb-2">
        <span
          className="text-xs uppercase"
          style={{
            color: "hsl(var(--text-muted))",
            opacity: 0.5,
            letterSpacing: "0.2em",
          }}
        >
          Intelligence Map
        </span>
      </div>
      <div className="flex-1 w-full" style={{ minHeight: "400px" }}>
        <svg viewBox="0 0 700 500" className="w-full h-full">
        {relationships.slice(0, 6).map((rel) => {
          const a = nodeMap[rel.entity_a];
          const b = nodeMap[rel.entity_b];
          if (!a || !b) return null;
          return (
            <RelationshipEdge
              key={rel.id}
              from={{ x: a.x, y: a.y }}
              to={{ x: b.x, y: b.y }}
              type={rel.relationship_type}
              strength={rel.strength}
            />
          );
        })}
        <motion.g variants={containerVariants} initial="hidden" animate="visible">
          {layoutNodes.map((node) => (
            <motion.g key={node.id} variants={nodeVariants}>
              <EntityNode
                x={node.x}
                y={node.y}
                name={node.name}
                type={node.type}
                active={activeNodes.has(node.id)}
                emphasized={emphasizedNodeIds.has(node.id)}
                pulse={pulsingNodeIds.has(node.id)}
                onClick={() => {}}
              />
            </motion.g>
          ))}
        </motion.g>
      </svg>
      </div>
    </div>
  );
}
