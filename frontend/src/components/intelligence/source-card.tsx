"use client";

import { motion } from "framer-motion";
import { Source } from "@/lib/types";

export function SourceCard({ source }: { source: Source }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="p-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))]"
    >
      <div className="flex items-start gap-2">
        <div className="flex-1 min-w-0">
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-[hsl(var(--foreground))] hover:text-[hsl(var(--primary))] transition-colors line-clamp-2"
          >
            {source.title}
          </a>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 line-clamp-2">
            {source.snippet}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 truncate">
            {source.url}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
