/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0F14", // Primary Background
        secondary: "#121826", // Secondary Background
        surface: "#161B26",   // Card / Surface
        border: "#232A3A",    // Border Subtle

        // Text
        primary: "#E6EAF2",
        "text-secondary": "#9AA4B2",
        muted: "#6B7280",

        // Semantic Agent Colors
        security: "#E5484D",
        logic: "#22C55E",
        quality: "#F59E0B",
        quality: "#F59E0B",
        uncertainty: "#8B5CF6", // for Abstention

        // Requested Landing Page Accents
        "accent-cyan": "#22D3EE",
        confidence: "#10B981", // Specific emerald for landing page

        // Brand/Tech
        brand: "#3b82f6", // Keep brand blue for generic actions if needed, or replace with neutral
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        'card': '14px',
        'input': '10px',
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.2)',
        'glow-security': '0 0 20px rgba(229, 72, 77, 0.35)',
        'glow-logic': '0 0 20px rgba(34, 197, 94, 0.35)',
        'glow-quality': '0 0 20px rgba(245, 158, 11, 0.35)',
        'glow-uncertainty': '0 0 20px rgba(139, 92, 246, 0.35)',
      }
    },
  },
  plugins: [],
}
