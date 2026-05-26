export const theme = {
  colors: {
    surface: {
      base: "hsl(220 20% 6%)",
      elevated: "hsl(220 20% 9%)",
      overlay: "hsl(220 18% 12%)",
    },
    accent: {
      primary: "hsl(228 56% 52%)",
      secondary: "hsl(180 45% 40%)",
    },
    text: {
      primary: "hsl(220 15% 92%)",
      secondary: "hsl(220 10% 64%)",
      muted: "hsl(220 8% 42%)",
    },
    signal: {
      positive: "hsl(160 60% 45%)",
      warning: "hsl(42 80% 55%)",
      critical: "hsl(0 72% 51%)",
      info: "hsl(220 40% 55%)",
    },
  },
  typography: {
    font: "'Inter', system-ui, sans-serif",
    mono: "'JetBrains Mono', monospace",
    scale: {
      xs: "0.75rem", sm: "0.875rem", base: "1rem", lg: "1.125rem",
      xl: "1.25rem", "2xl": "1.5rem", "3xl": "1.875rem", "4xl": "2.25rem",
    },
  },
  spacing: { panel: "1.5rem", section: "2rem", gutter: "1rem" },
} as const;
