/**
 * @fileoverview SVG entity node for the intelligence map.
 * Renders a clickable circle with type-based colour, label, ambient
 * glow, slow drift, and dynamic opacity based on active state.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion } from "framer-motion";

const typeColors: Record<string, string> = {
  company: "hsl(var(--accent-primary))",
  competitor: "hsl(var(--signal-warning))",
  vendor: "hsl(var(--signal-positive))",
  market: "hsl(var(--signal-info))",
  regulatory: "hsl(var(--signal-critical))",
};

const typeLabels: Record<string, string> = {
  company: "You",
  competitor: "Comp",
  vendor: "Vendor",
  market: "Market",
  regulatory: "Reg",
};

/** EntityNode — SVG group representing an entity on the relationship map.
 *  Features entry animation, ambient drift, glow, and hover states. */
export function EntityNode({
  x,
  y,
  name,
  type,
  active,
  emphasized,
  pulse,
  onClick,
}: {
  x: number;
  y: number;
  name: string;
  type: string;
  active: boolean;
  emphasized?: boolean;
  pulse?: boolean;
  onClick: () => void;
}) {
  const color = typeColors[type] || typeColors.company;
  const size = type === "company" ? 52 : 36;
  const baseOpacity = active ? 1 : 0.4;
  const glowOpacity = emphasized ? 0.12 : active ? 0.08 : 0;

  // Random drift direction so each node feels independent
  // Guard against single-character names (charCodeAt(1) would be NaN)
  const driftX = (name.charCodeAt(0) || 0) % 3 - 1;
  const driftY = ((name.charCodeAt(1) ?? name.charCodeAt(0)) || 0) % 3 - 1;

  return (
    <g transform={`translate(${x}, ${y})`}>
      <motion.g
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{
          opacity: emphasized ? [1, 0.7] : baseOpacity,
          scale: 1,
          x: driftX * 4,
          y: driftY * 4,
        }}
        transition={{
          opacity: emphasized ? { duration: 1, ease: "easeOut" } : { duration: 0.4, ease: "easeOut" },
          scale: { duration: 0.4, ease: "easeOut" },
          x: { duration: 6, repeat: Infinity, ease: "easeInOut", repeatType: "mirror" },
          y: { duration: 5, repeat: Infinity, ease: "easeInOut", repeatType: "mirror" },
        }}
        style={{ cursor: "pointer" }}
        onClick={onClick}
      >
      {/* Ambient glow behind node */}
      <circle
        r={(size / 2) * 3}
        fill={color}
        opacity={glowOpacity}
        style={{ pointerEvents: "none" }}
      />

      {/* Active pulse ring */}
      {active && (
        <motion.circle
          animate={{
            r: [size / 2 + 4, size / 2 + 10, size / 2 + 4],
            opacity: [0.25, 0.08, 0.25],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          cx={0}
          cy={0}
          fill={color}
          style={{ pointerEvents: "none" }}
        />
      )}

      {/* Signal pulse ring */}
      {pulse && (
        <motion.circle
          animate={{
            r: [size / 2 + 4, size / 2 + 20, size / 2 + 4],
            opacity: [0.4, 0, 0.4],
          }}
          transition={{ duration: 1.5, repeat: 2, ease: "easeOut" }}
          cx={0}
          cy={0}
          fill="none"
          stroke={color}
          strokeWidth={2}
          style={{ pointerEvents: "none" }}
        />
      )}

      {/* Main node body */}
      <circle
        r={size / 2}
        fill={color}
        opacity={type === "company" ? 0.2 : 0.12}
        stroke={color}
        strokeWidth={type === "company" ? 2 : 1.5}
      />

      {/* Name label */}
      <text
        textAnchor="middle"
        dy="0.35em"
        fontSize={type === "company" ? 12 : 10}
        fontWeight={type === "company" ? 700 : 600}
        fill={color}
        style={{ pointerEvents: "none" }}
      >
        {name.length > 10 ? name.slice(0, 10) + "..." : name}
      </text>

      {/* Type label */}
      <text
        textAnchor="middle"
        dy={size / 2 + 14}
        fontSize={9}
        fill="hsl(var(--text-muted))"
        opacity={0.5}
        style={{ pointerEvents: "none" }}
      >
        {typeLabels[type] || type}
      </text>
      </motion.g>
    </g>
  );
}
