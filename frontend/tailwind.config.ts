import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // SOCsentinel "Dark Ops" palette
        navy: {
          50: "#e6eaf0",
          100: "#c0c9d9",
          200: "#97a5bf",
          300: "#6d81a5",
          400: "#4e6591",
          500: "#2f4a7e",
          600: "#274076",
          700: "#1E3A5F", // Steel Blue
          800: "#152d4a",
          900: "#0A1628", // Deep Navy (primary bg)
          950: "#050d17",
        },
        cyan: {
          electric: "#00D4FF", // Accent primary
        },
        alert: {
          orange: "#FF6B35", // Warning / high severity
        },
        ice: {
          gray: "#F0F4F8", // Subtle backgrounds
        },
        severity: {
          critical: "#EF4444",
          high: "#F97316",
          medium: "#EAB308",
          low: "#22C55E",
          info: "#3B82F6",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
        mono: ['"JetBrains Mono"', '"Fira Code"', "monospace"],
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "fade-in": "fade-in 0.3s ease-out",
        "slide-up": "slide-up 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          "0%": { opacity: "0", transform: "translateX(10px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
