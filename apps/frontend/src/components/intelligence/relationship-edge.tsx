/**
 * @fileoverview SVG relationship edge for the intelligence map.
 * Draws a styled line between two entity nodes with an animated
 * indicator dot and a relationship-type label.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";

interface Point { x: number; y: number; }

/**
 * RelationshipEdge — renders a connection line between two entity positions
 * with variable width/opacity based on relationship strength.
 */
export function RelationshipEdge({ from, to, type, strength }: { from: Point; to: Point; type: string; strength: number }) {
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;
  return (
    <g>
      <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="hsl(var(--text-muted))"
        strokeWidth={1 + strength * 1.5} opacity={0.15 + strength * 0.25} strokeDasharray={type === "affected_by" ? "4 3" : undefined} />
      <circle r={2.5} fill="hsl(var(--accent-primary))" opacity={0.7}>
        <animateMotion dur={`${3 - strength * 2}s`} repeatCount="indefinite" path={`M${from.x},${from.y} L${to.x},${to.y}`} />
      </circle>
      <text x={midX} y={midY - 6} textAnchor="middle" fontSize={9} fill="hsl(var(--text-muted))" opacity={0.7}>{type.replace(/_/g, " ")}</text>
    </g>
  );
}
