/**
 * @fileoverview Landing page — "The Threshold." The first thing a user sees.
 * A restrained, expensive entrance that feels like stepping into a quiet
 * intelligence facility. Features:
 *   - Theme-aware breathing ambient background (radial gradients via CSS vars)
 *   - Drifting indigo particles
 *   - Animated title with teal-highlighted "E" letters
 *   - Ghost-style "Begin" call-to-action
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

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
  /* Whether the current theme is dark (derived from <html> class on mount) */
  const [isDark, setIsDark] = useState(true);
  /* True while the "Begin" → onboarding navigation is in progress */
  const [isNavigating, setIsNavigating] = useState(false);
  /* Tracks hover on the CTA button to subtly adjust border opacity */
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
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
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden">
      {/* Theme toggle — upper right */}
      <button
        onClick={toggleTheme}
        className="absolute top-6 right-6 z-20 text-xs uppercase tracking-widest transition-all hover:opacity-100 hover:brightness-125"
        style={{ color: "hsl(var(--text-secondary))", opacity: 0.8 }}
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

        <motion.button
          whileHover={isNavigating ? {} : {
            boxShadow: "0 0 20px hsla(228, 56%, 52%, 0.2)",
          }}
          whileTap={isNavigating ? {} : { scale: 0.98 }}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
          onClick={() => {
            setIsNavigating(true);
            router.push("/onboarding");
          }}
          disabled={isNavigating}
          className="mt-12 rounded-lg px-10 py-3 text-sm tracking-wide transition-colors"
          style={{
            background: "transparent",
            border: `1px solid hsl(var(--accent-primary) / ${isHovering ? 0.7 : 0.4})`,
            color: "hsl(var(--text-primary))",
            opacity: isNavigating ? 0.6 : 1,
          }}
        >
          {isNavigating ? "Entering..." : "Begin"}
        </motion.button>
      </motion.div>

      {/* Footer */}
      <div
        className="absolute bottom-6 text-xs"
        style={{
          color: "hsl(var(--text-muted))",
          opacity: 0.7,
          letterSpacing: "0.05em",
        }}
      >
        Powered by Bright Data &nbsp;&middot;&nbsp; Gemini
      </div>
    </main>
  );
}
