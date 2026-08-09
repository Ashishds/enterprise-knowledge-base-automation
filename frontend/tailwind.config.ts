import type { Config } from "tailwindcss";

// Tokens copied verbatim from docs/DESIGN-SYSTEM.md §2. Every colour a
// component uses must resolve through one of these — no raw hex/rgb/hsl in
// component code (frontend.md §1a).
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      fontFamily: {
        sans: ["Geist Variable", "Inter Variable", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Geist Mono Variable", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        card: "hsl(var(--card) / <alpha-value>)",
        "card-foreground": "hsl(var(--card-foreground) / <alpha-value>)",
        popover: "hsl(var(--popover) / <alpha-value>)",
        "popover-foreground": "hsl(var(--popover-foreground) / <alpha-value>)",
        secondary: "hsl(var(--secondary) / <alpha-value>)",
        "secondary-foreground": "hsl(var(--secondary-foreground) / <alpha-value>)",
        muted: "hsl(var(--muted) / <alpha-value>)",
        "muted-foreground": "hsl(var(--muted-foreground) / <alpha-value>)",
        accent: "hsl(var(--accent) / <alpha-value>)",
        "accent-foreground": "hsl(var(--accent-foreground) / <alpha-value>)",
        destructive: "hsl(var(--destructive) / <alpha-value>)",
        "destructive-foreground": "hsl(var(--destructive-foreground) / <alpha-value>)",
        border: "hsl(var(--border) / <alpha-value>)",
        input: "hsl(var(--input) / <alpha-value>)",

        brand: "rgb(var(--brand) / <alpha-value>)",
        "brand-foreground": "rgb(var(--brand-foreground) / <alpha-value>)",
        success: "rgb(var(--success) / <alpha-value>)",
        warning: "rgb(var(--warning) / <alpha-value>)",
        info: "rgb(var(--info) / <alpha-value>)",
        danger: "rgb(var(--danger) / <alpha-value>)",
        neutral: "rgb(var(--neutral) / <alpha-value>)",
      },
      borderRadius: {
        DEFAULT: "var(--radius)",
        sm: "calc(var(--radius) - 2px)",
        xs: "calc(var(--radius) - 4px)",
        lg: "0.75rem",
        xl: "1rem",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        DEFAULT: "var(--shadow)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
      },
      keyframes: {
        "fade-up": { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        "pulse-soft": { "0%,100%": { opacity: "0.5" }, "50%": { opacity: "1" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out both",
        "pulse-soft": "pulse-soft 1.6s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
