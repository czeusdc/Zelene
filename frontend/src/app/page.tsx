/**
 * @fileoverview Landing page — a scrollable, multi-section narrative experience.
 * "The Threshold" (hero) is followed by 6 sections that tell Zelene's story:
 *   - The Problem, The Response, The View, How It Works, Trust Signals, Final CTA
 * Features:
 *   - Theme-aware breathing ambient background (radial gradients via CSS vars)
 *   - Drifting indigo particles in hero and final CTA
 *   - Animated title with teal-highlighted "E" letters
 *   - Dual ghost-style "Begin" / "Begin Simulated" call-to-action buttons
 *   - Scroll-triggered section reveals via Framer Motion whileInView
 *   - Fixed theme toggle that appears after scrolling past hero
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Brain, Globe, Lightbulb } from "lucide-react";
import { ZeleneAvatar } from "@/components/onboarding/zelene-avatar";
import { SectionReveal, revealItemVariants } from "@/components/landing/section-reveal";

/** Drifting particle positions and animation durations. */
const particles = [
  { left: "12%", top: "18%", size: 3, duration: 14, delay: 0 },
  { left: "78%", top: "22%", size: 2, duration: 18, delay: 2 },
  { left: "85%", top: "72%", size: 4, duration: 12, delay: 1 },
  { left: "22%", top: "80%", size: 2, duration: 16, delay: 3 },
  { left: "60%", top: "15%", size: 3, duration: 20, delay: 4 },
  { left: "45%", top: "85%", size: 2, duration: 15, delay: 1.5 },
  { left: "8%", top: "55%", size: 3, duration: 17, delay: 0.5 },
  { left: "92%", top: "45%", size: 2, duration: 13, delay: 2.5 },
];

export default function Home() {
  const router = useRouter();
  /* Whether the current theme is dark (default dark, synced from DOM on mount). */
  const [isDark, setIsDark] = useState(true);
  /* True while the "Begin" -> onboarding navigation is in progress */
  const [isNavigating, setIsNavigating] = useState(false);
  /* Tracks hover on the CTA button to subtly adjust border opacity */
  const [isHovering, setIsHovering] = useState(false);
  /* Show fixed theme toggle after scrolling past the hero */
  const [showFixedToggle, setShowFixedToggle] = useState(false);

  // Sync theme state from the DOM class set by the FOUC script in layout.tsx.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  // Clear simulation mode when returning to the landing page.
  useEffect(() => {
    localStorage.removeItem("zelene_simulation_mode");
  }, []);

  // Track scroll position to show the fixed theme toggle once the hero is out of view.
  useEffect(() => {
    const onScroll = () => {
      setShowFixedToggle(window.scrollY > window.innerHeight * 0.8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* Toggles between dark and light theme, persisting choice to localStorage */
  const toggleTheme = () => {
    const html = document.documentElement;
    if (html.classList.contains("dark")) {
      html.classList.remove("dark");
      html.classList.add("light");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      html.classList.remove("light");
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <main className="relative overflow-x-hidden">
      {/* =====================================================================
          Section 0 — The Threshold (Hero)
          =================================================================== */}
      <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden">
        {/* Theme toggle — upper right */}
        {/* Theme toggle — upper right (absolute in hero) */}
        <button
          onClick={toggleTheme}
          className="absolute top-6 right-6 z-20 text-xs uppercase tracking-widest transition-all hover:opacity-100 hover:brightness-125"
          style={{ color: "hsl(var(--text-secondary))", opacity: 0.8 }}
        >
          {isDark ? "Light" : "Dark"}
        </button>

        {/* Fixed theme toggle — appears after scrolling past hero */}
        <button
          onClick={toggleTheme}
          className={`fixed top-6 right-6 z-30 text-xs uppercase tracking-widest transition-opacity duration-500 hover:opacity-100 hover:brightness-125 ${showFixedToggle ? "opacity-80" : "pointer-events-none opacity-0"}`}
          style={{ color: "hsl(var(--text-secondary))" }}
        >
          {isDark ? "Light" : "Dark"}
        </button>
        {/* Ambient breathing gradients */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage: "var(--breathe-glow-1), var(--breathe-glow-2), var(--breathe-glow-3)",
            backgroundSize: "200% 200%",
            animation: "breathe 8s ease-in-out infinite",
          }}
        />

        {/* Drifting particles */}
        {particles.map((p, i) => (
          <div
            key={i}
            className="pointer-events-none absolute rounded-full"
            style={{
              left: p.left,
              top: p.top,
              width: p.size,
              height: p.size,
              backgroundColor: "hsl(var(--accent-primary))",
              opacity: 0.15,
              animation: `drift ${p.duration}s ease-in-out infinite`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="relative z-10 text-center"
        >
          <h1
            className="text-[2.5rem] font-extralight uppercase"
            style={{ letterSpacing: "0.3em" }}
          >
            {/* Title: each letter rendered as a <span> so the two "E"s
                (indices 1 & 3 in the split array) can be styled in the
                secondary teal color with a phase-offset breathing pulse. */}
            {"Z E L E N E".split(" ").map((char, i) =>
              i === 1 || i === 3 ? (
                <span
                  key={i}
                  style={{
                    color: "hsl(var(--accent-secondary))",
                    animation: "letter-breath 3s ease-in-out infinite",
                    animationDelay: `${i === 1 ? 0 : 1.5}s`,
                  }}
                >
                  {char}{" "}
                </span>
              ) : (
                <span key={i}>
                  {char}{" "}
                </span>
              )
            )}
          </h1>

          <p
            className="mt-5 text-[0.85rem] uppercase"
            style={{
              color: "hsl(var(--text-secondary))",
              letterSpacing: "0.08em",
            }}
          >
            Strategic Intelligence Presence
          </p>

          <p
            className="mt-3 text-[0.8rem] italic"
            style={{ color: "hsl(var(--text-muted))" }}
          >
            See what matters before it becomes obvious.
          </p>

          <div className="mt-12 flex items-center gap-4">
            <motion.button
              whileHover={isNavigating ? {} : {
                boxShadow: "0 0 20px hsla(228, 56%, 52%, 0.2)",
              }}
              whileTap={isNavigating ? {} : { scale: 0.98 }}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              onClick={() => {
                setIsNavigating(true);
                localStorage.removeItem("zelene_simulation_mode");
                router.push("/onboarding");
              }}
              disabled={isNavigating}
              className="rounded-lg px-10 py-3 text-sm tracking-wide transition-colors"
              style={{
                background: "transparent",
                border: `1px solid hsl(var(--accent-primary) / ${isHovering ? 0.7 : 0.4})`,
                color: "hsl(var(--text-primary))",
                opacity: isNavigating ? 0.6 : 1,
              }}
            >
              {isNavigating ? "Entering..." : "Begin"}
            </motion.button>
            <motion.button
              whileHover={isNavigating ? {} : {
                boxShadow: "0 0 20px hsla(228, 56%, 52%, 0.15)",
              }}
              whileTap={isNavigating ? {} : { scale: 0.98 }}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              onClick={() => {
                setIsNavigating(true);
                localStorage.setItem("zelene_simulation_mode", "true");
                router.push("/onboarding");
              }}
              disabled={isNavigating}
              className="rounded-lg px-10 py-3 text-sm italic tracking-wide transition-colors"
              style={{
                background: "transparent",
                border: `1px solid hsl(var(--accent-primary) / ${isHovering ? 0.5 : 0.25})`,
                color: "hsl(var(--text-secondary))",
                opacity: isNavigating ? 0.6 : 1,
              }}
            >
              {isNavigating ? "Entering..." : "Begin Simulated"}
            </motion.button>
          </div>
        </motion.div>
      </section>

      {/* =====================================================================
          Section 1 — The Problem
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center px-6"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        <SectionReveal className="max-w-2xl text-center">
          <motion.p
            variants={revealItemVariants}
            className="text-lg font-light leading-relaxed"
            style={{ color: "hsl(var(--text-primary))" }}
          >
            Your competitors are making moves right now.
          </motion.p>
          <motion.p
            variants={revealItemVariants}
            className="mt-4 text-lg font-light leading-relaxed"
            style={{ color: "hsl(var(--text-muted))" }}
          >
            Pricing shifts, hiring surges, and market entries pass unseen.
          </motion.p>
          <motion.p
            variants={revealItemVariants}
            className="mt-4 text-lg font-light leading-relaxed"
            style={{ color: "hsl(var(--text-muted))" }}
          >
            By the time you see it in a report, it is already history.
          </motion.p>
        </SectionReveal>
      </section>

      {/* =====================================================================
          Section 2 — The Response
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center px-6"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        <SectionReveal className="flex max-w-2xl flex-col items-center text-center">
          <motion.div variants={revealItemVariants}>
            <ZeleneAvatar />
          </motion.div>
          <motion.p
            variants={revealItemVariants}
            className="mt-8 text-xl font-light leading-relaxed"
            style={{ color: "hsl(var(--text-primary))" }}
          >
            Zelene watches the web so you do not have to.
          </motion.p>
          <motion.p
            variants={revealItemVariants}
            className="mt-4 text-base font-light leading-relaxed"
            style={{ color: "hsl(var(--text-secondary))" }}
          >
            An AI Chief Intelligence Officer that learns your business, observes your competitive landscape in real time, and tells you what matters before it becomes obvious.
          </motion.p>
        </SectionReveal>
      </section>

      {/* =====================================================================
          Section 3 — The View (Product Reveal)
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center px-6"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        <div className="flex w-full max-w-5xl flex-col items-center gap-12">
          {/* Schematic panels */}
          <div className="relative flex w-full items-end gap-4">
            {/* Signal flow dot — animates across panels after they appear */}
            <div
              className="pointer-events-none absolute top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full"
              style={{
                backgroundColor: "hsl(var(--accent-primary))",
                animation: "signal-flow 4s ease-in-out 1.2s forwards",
                opacity: 0,
              }}
            />
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="flex flex-1 flex-col items-center justify-center rounded-lg border px-2 py-8 md:px-4"
              style={{
                backgroundColor: "hsl(var(--surface-base))",
                borderColor: "hsl(var(--accent-primary) / 0.15)",
                minHeight: "200px",
              }}
            >
              <span
                className="text-xs uppercase tracking-widest"
                style={{ color: "hsl(var(--text-secondary))" }}
              >
                Signal Feed
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.15 }}
              className="flex flex-[2] flex-col items-center justify-center rounded-lg border px-2 py-12 md:px-4"
              style={{
                backgroundColor: "hsl(var(--surface-elevated))",
                borderColor: "hsl(var(--accent-primary) / 0.2)",
                boxShadow: "inset 0 0 40px hsla(228, 56%, 52%, 0.04)",
                minHeight: "280px",
              }}
            >
              <span
                className="text-xs uppercase tracking-widest"
                style={{ color: "hsl(var(--text-primary))" }}
              >
                Intelligence Map
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.5, ease: "easeOut", delay: 0.3 }}
              className="flex flex-1 flex-col items-center justify-center rounded-lg border px-2 py-8 md:px-4"
              style={{
                backgroundColor: "hsl(var(--surface-overlay))",
                borderColor: "hsl(var(--accent-primary) / 0.15)",
                minHeight: "200px",
              }}
            >
              <span
                className="text-xs uppercase tracking-widest"
                style={{ color: "hsl(var(--text-secondary))" }}
              >
                Zelene Chat
              </span>
            </motion.div>
          </div>

          {/* Copy */}
          <SectionReveal className="max-w-xl text-center">
            <motion.p
              variants={revealItemVariants}
              className="text-xl font-light"
              style={{ color: "hsl(var(--text-primary))" }}
            >
              Intelligence, not dashboards.
            </motion.p>
            <motion.p
              variants={revealItemVariants}
              className="mt-3 text-base font-light"
              style={{ color: "hsl(var(--text-secondary))" }}
            >
              Three panels. One dominant at a time.
            </motion.p>
            <motion.p
              variants={revealItemVariants}
              className="mt-2 text-base font-light"
              style={{ color: "hsl(var(--text-muted))" }}
            >
              Signals emerge. Patterns connect. Insights crystallize.
            </motion.p>
          </SectionReveal>
        </div>
      </section>

      {/* =====================================================================
          Section 4 — How It Works (Pipeline)
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center px-6"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        <div className="flex w-full max-w-4xl flex-col items-center gap-12">
          <div className="flex w-full flex-col items-center gap-8 md:flex-row">
            {/* Card 1 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="flex flex-1 flex-col items-center rounded-lg border px-6 py-10 text-center"
              style={{
                backgroundColor: "hsl(var(--surface-elevated))",
                borderColor: "hsl(var(--accent-primary) / 0.15)",
              }}
            >
              <Brain
                className="mb-4 h-6 w-6"
                style={{ color: "hsl(var(--accent-primary))" }}
              />
              <h3
                className="text-sm font-medium uppercase tracking-widest"
                style={{ color: "hsl(var(--text-primary))" }}
              >
                Learn
              </h3>
              <p
                className="mt-3 text-sm font-light leading-relaxed"
                style={{ color: "hsl(var(--text-secondary))" }}
              >
                Zelene learns your business through conversation. Your market, your competitors, what you care about.
              </p>
            </motion.div>

            {/* Connector (hidden on mobile) */}
            <div
              className="hidden h-px w-12 md:block"
              style={{ backgroundColor: "hsl(var(--accent-primary) / 0.2)" }}
            />

            {/* Card 2 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.15 }}
              className="flex flex-1 flex-col items-center rounded-lg border px-6 py-10 text-center"
              style={{
                backgroundColor: "hsl(var(--surface-elevated))",
                borderColor: "hsl(var(--accent-primary) / 0.15)",
              }}
            >
              <Globe
                className="mb-4 h-6 w-6"
                style={{ color: "hsl(var(--accent-primary))" }}
              />
              <h3
                className="text-sm font-medium uppercase tracking-widest"
                style={{ color: "hsl(var(--text-primary))" }}
              >
                Observe
              </h3>
              <p
                className="mt-3 text-sm font-light leading-relaxed"
                style={{ color: "hsl(var(--text-secondary))" }}
              >
                Real-time web intelligence via Bright Data. SERP, Scraper, and Unlocker watching every corner.
              </p>
            </motion.div>

            {/* Connector (hidden on mobile) */}
            <div
              className="hidden h-px w-12 md:block"
              style={{ backgroundColor: "hsl(var(--accent-primary) / 0.2)" }}
            />

            {/* Card 3 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.3 }}
              className="flex flex-1 flex-col items-center rounded-lg border px-6 py-10 text-center"
              style={{
                backgroundColor: "hsl(var(--surface-elevated))",
                borderColor: "hsl(var(--accent-primary) / 0.15)",
              }}
            >
              <Lightbulb
                className="mb-4 h-6 w-6"
                style={{ color: "hsl(var(--accent-primary))" }}
              />
              <h3
                className="text-sm font-medium uppercase tracking-widest"
                style={{ color: "hsl(var(--text-primary))" }}
              >
                Surface
              </h3>
              <p
                className="mt-3 text-sm font-light leading-relaxed"
                style={{ color: "hsl(var(--text-secondary))" }}
              >
                Signals, patterns, and insights emerge as they form. Not buried in a report you read next quarter.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* =====================================================================
          Section 5 — Trust Signals
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center px-6"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        <SectionReveal className="grid max-w-4xl grid-cols-1 gap-10 md:grid-cols-2">
          <motion.div variants={revealItemVariants} className="text-center md:text-left">
            <h3
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: "hsl(var(--text-primary))" }}
            >
              Evidence, not fabrication
            </h3>
            <p
              className="mt-3 text-sm font-light leading-relaxed"
              style={{ color: "hsl(var(--text-secondary))" }}
            >
              Every signal links back to its source. Zelene never invents data.
            </p>
          </motion.div>
          <motion.div variants={revealItemVariants} className="text-center md:text-left">
            <h3
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: "hsl(var(--text-primary))" }}
            >
              Confidence, not certainty
            </h3>
            <p
              className="mt-3 text-sm font-light leading-relaxed"
              style={{ color: "hsl(var(--text-secondary))" }}
            >
              Scores are calibrated. An early signal that needs more data is a valid and honest answer.
            </p>
          </motion.div>
          <motion.div variants={revealItemVariants} className="text-center md:text-left">
            <h3
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: "hsl(var(--text-primary))" }}
            >
              Presence, not notification
            </h3>
            <p
              className="mt-3 text-sm font-light leading-relaxed"
              style={{ color: "hsl(var(--text-secondary))" }}
            >
              Intelligence unfolds in real time. No email digests, no alert fatigue.
            </p>
          </motion.div>
          <motion.div variants={revealItemVariants} className="text-center md:text-left">
            <h3
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: "hsl(var(--text-primary))" }}
            >
              Simulation included
            </h3>
            <p
              className="mt-3 text-sm font-light leading-relaxed"
              style={{ color: "hsl(var(--text-secondary))" }}
            >
              Full demo experience with zero API costs. See the product before connecting your keys.
            </p>
          </motion.div>
        </SectionReveal>
      </section>

      {/* =====================================================================
          Section 6 — Final CTA + Footer
          =================================================================== */}
      <section
        className="section-divider relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 pb-24"
        style={{ backgroundColor: "hsl(var(--surface-base))" }}
      >
        {/* Re-ambient gradients */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage: "var(--breathe-glow-1), var(--breathe-glow-2), var(--breathe-glow-3)",
            backgroundSize: "200% 200%",
            animation: "breathe 8s ease-in-out infinite",
            opacity: 0.6,
          }}
        />

        {/* Drifting particles (subset) */}
        {particles.slice(0, 4).map((p, i) => (
          <div
            key={`cta-p-${i}`}
            className="pointer-events-none absolute rounded-full"
            style={{
              left: p.left,
              top: p.top,
              width: p.size,
              height: p.size,
              backgroundColor: "hsl(var(--accent-primary))",
              opacity: 0.1,
              animation: `drift ${p.duration}s ease-in-out infinite`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative z-10 flex flex-col items-center text-center"
        >
          <p
            className="text-2xl font-extralight"
            style={{
              color: "hsl(var(--text-primary))",
              letterSpacing: "0.05em",
            }}
          >
            See what matters before it becomes obvious.
          </p>

          <div className="mt-12 flex items-center gap-4">
            <motion.button
              whileHover={isNavigating ? {} : {
                boxShadow: "0 0 20px hsla(228, 56%, 52%, 0.2)",
              }}
              whileTap={isNavigating ? {} : { scale: 0.98 }}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              onClick={() => {
                setIsNavigating(true);
                localStorage.removeItem("zelene_simulation_mode");
                router.push("/onboarding");
              }}
              disabled={isNavigating}
              className="rounded-lg px-10 py-3 text-sm tracking-wide transition-colors"
              style={{
                background: "transparent",
                border: `1px solid hsl(var(--accent-primary) / ${isHovering ? 0.7 : 0.4})`,
                color: "hsl(var(--text-primary))",
                opacity: isNavigating ? 0.6 : 1,
              }}
            >
              {isNavigating ? "Entering..." : "Begin"}
            </motion.button>
            <motion.button
              whileHover={isNavigating ? {} : {
                boxShadow: "0 0 20px hsla(228, 56%, 52%, 0.15)",
              }}
              whileTap={isNavigating ? {} : { scale: 0.98 }}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              onClick={() => {
                setIsNavigating(true);
                localStorage.setItem("zelene_simulation_mode", "true");
                router.push("/onboarding");
              }}
              disabled={isNavigating}
              className="rounded-lg px-10 py-3 text-sm italic tracking-wide transition-colors"
              style={{
                background: "transparent",
                border: `1px solid hsl(var(--accent-primary) / ${isHovering ? 0.5 : 0.25})`,
                color: "hsl(var(--text-secondary))",
                opacity: isNavigating ? 0.6 : 1,
              }}
            >
              {isNavigating ? "Entering..." : "Begin Simulated"}
            </motion.button>
          </div>

          <p
            className="mt-16 text-xs"
            style={{
              color: "hsl(var(--text-muted))",
              opacity: 0.7,
              letterSpacing: "0.05em",
            }}
          >
            Built with Bright Data · AIMLAPI · Cognee · LangGraph
          </p>
        </motion.div>

        <div
          className="absolute bottom-6 text-xs"
          style={{
            color: "hsl(var(--text-muted))",
            opacity: 0.7,
            letterSpacing: "0.05em",
          }}
        >
          Powered by Bright Data · AIMLAPI · Cognee
        </div>
      </section>
    </main>
  );
}
