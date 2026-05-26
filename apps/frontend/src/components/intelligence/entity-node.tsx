"use client";
import { motion } from "framer-motion";

const typeColors: Record<string, string> = { company: "hsl(var(--accent-primary))", competitor: "hsl(var(--signal-warning))", vendor: "hsl(var(--signal-positive))", market: "hsl(var(--signal-info))", regulatory: "hsl(var(--signal-critical))" };
const typeLabels: Record<string, string> = { company: "You", competitor: "Comp", vendor: "Vendor", market: "Market", regulatory: "Reg" };

export function EntityNode({ x, y, name, type, active, onClick }: { x: number; y: number; name: string; type: string; active: boolean; onClick: () => void }) {
  const color = typeColors[type] || typeColors.company;
  const size = type === "company" ? 48 : 36;
  return (
    <g transform={`translate(${x}, ${y})`} onClick={onClick} style={{ cursor: "pointer" }}>
      {active && <motion.circle animate={{ r: [size / 2 + 4, size / 2 + 8, size / 2 + 4], opacity: [0.3, 0.1, 0.3] }} transition={{ duration: 2, repeat: Infinity }} cx={0} cy={0} fill={color} />}
      <circle r={size / 2} fill={color} opacity={0.15} stroke={color} strokeWidth={1.5} />
      <text textAnchor="middle" dy="0.35em" fontSize={type === "company" ? 11 : 10} fontWeight={600} fill={color} style={{ pointerEvents: "none" }}>
        {name.length > 10 ? name.slice(0, 10) + "..." : name}
      </text>
      <text textAnchor="middle" dy={size / 2 + 14} fontSize={9} fill="hsl(var(--text-muted))" style={{ pointerEvents: "none" }}>{typeLabels[type] || type}</text>
    </g>
  );
}
