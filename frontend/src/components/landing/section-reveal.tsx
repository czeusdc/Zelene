/**
 * @fileoverview Reusable scroll-triggered section reveal wrapper.
 * Uses Framer Motion whileInView to animate children with a stagger.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { motion, Variants } from "framer-motion";
import { ReactNode } from "react";

/** Default item variants for fade-in-up reveal. */
const itemVariants: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

/**
 * SectionReveal — wraps children in a motion container that staggers
 * their entrance when the section scrolls into view.
 */
export function SectionReveal({
  children,
  className,
  staggerDelay = 0.15,
}: {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
}) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.3 }}
      variants={{
        hidden: {},
        visible: {
          transition: { staggerChildren: staggerDelay },
        },
      }}
    >
      {children}
    </motion.div>
  );
}

/** Use this variant on direct children of SectionReveal. */
export const revealItemVariants = itemVariants;
