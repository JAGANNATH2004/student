/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12172B",       // near-black navy, primary text/background anchor
        slate: {
          850: "#1B2138",
        },
        parchment: "#F6F3EC", // warm paper background for content areas
        amber: {
          DEFAULT: "#C98A3E", // signature accent — "highlighter" amber, not terracotta
          light: "#E5B876",
        },
        moss: "#3F6C51",      // secondary accent for success/mastery states
      },
      fontFamily: {
        display: ["'Source Serif 4'", "Georgia", "serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
}
