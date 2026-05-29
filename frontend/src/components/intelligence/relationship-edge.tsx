/**
 * @fileoverview SVG relationship edge for the intelligence map.
 * Draws a styled line between two entity nodes with an animated
 * opacity pulse, an indicator dot, and a brief brightness flash
 * when the relationship first appears.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

interface Point { x: number; y: number; }

/** RelationshipEdge — renders a connection line between two entity positions
 *  with ambient opacity pulse, moving indicator dot, and entry flash. */
export function RelationshipEdge({
  from,
  to,
  type,
  strength,
}: {
  from: Point;
  to: Point;
  type: string;
  strength: number;
}) {
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;
  const baseOpacity = 0.15 + strength * 0.25;

  return (
    <g>
      <motion.line
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        stroke="hsl(var(--text-muted))"
        strokeWidth={1 + strength * 1.5}
        strokeDasharray={type === "affected_by" ? "4 3" : undefined}
        initial={{ opacity: 0.6 }}
        animate={{ opacity: [baseOpacity, baseOpacity + 0.2, baseOpacity] }}
        transition={{ duration: 3 + strength, repeat: Infinity, ease: "easeInOut" }}
      />
      <circle r={2.5} fill="hsl(var(--accent-primary))" opacity={0.7}>
        <animateMotion
          dur={`${3 - strength * 2}s`}
          repeatCount="indefinite"
          path={`M${from.x},${from.y} L${to.x},${to.y}`}
        />
      </circle>
      <text
        x={midX}
        y={midY - 6}
        textAnchor="middle"
        fontSize={9}
        fill="hsl(var(--text-muted))"
        opacity={0.7}
      >
        {type.replace(/_/g, " ")}
      </text>
    </g>
  );
}
