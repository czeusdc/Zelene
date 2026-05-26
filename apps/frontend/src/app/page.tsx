/**
 * @fileoverview Landing page — hero screen with the Zelene brand mark,
 * tagline, and a "Begin" button that routes to onboarding.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function Home() {
  const router = useRouter();
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }} className="text-center">
        <h1 className="text-4xl font-light tracking-tight">Zelene</h1>
        <p className="mt-3 text-lg" style={{ color: "hsl(var(--text-secondary))" }}>
          Strategic Intelligence Presence
        </p>
        <p className="mt-8 text-sm" style={{ color: "hsl(var(--text-muted))" }}>
          See what matters before it becomes obvious.
        </p>
        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
          onClick={() => router.push("/onboarding")}
          className="mt-12 rounded-lg px-8 py-3 text-sm font-medium transition-colors"
          style={{ background: "hsl(var(--accent-primary))", color: "hsl(var(--text-primary))" }}>
          Begin
        </motion.button>
      </motion.div>
    </main>
  );
}
